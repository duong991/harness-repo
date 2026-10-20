#!/usr/bin/env python3
"""
common.py - Shared configuration, credential, redaction, read-only-guard, and
request utilities for the system-log-tracer tools.

Design constraints (see SKILL.md and the skill's config.schema.json):
  - Python standard library only. No third-party dependencies.
  - Non-secret config lives at <repo-root>/.agents/config/system-log-tracer.json
    and is validated against config.schema.json with a small built-in validator
    (no jsonschema package).
  - Credentials live at ~/.config/system-log-tracer/<env>.env (overridable with
    SLT_CREDENTIALS_DIR for tests) or plain process environment variables. They
    are never read from a repository-tracked file.
  - The tool REFUSES to run if a `.env` file exists in the skill directory, or
    if a `.env` / `system-log-tracer*.env` file exists under
    `<repo-root>/.agents/config/`. Those are the two places a stray secret file
    could sit inside the consumer repository for this skill.
  - Selecting a production environment requires `--env <name> --confirm-prod`
    AND a matching `~/.config/system-log-tracer/<env>.env` credential file.
  - Importing this module verifies that every file of the skill still matches
    the Harness baseline hash in `.harness-core/manifest.json`; any drift
    (including a hand- or agent-edited guard) stops the tool before it runs.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------

class ConfigError(Exception):
    """Config file missing, unparsable, or schema-invalid."""


class EnvFileRefused(Exception):
    """A .env file sits somewhere this skill refuses to operate near."""


class ProdGateError(Exception):
    """Production environment selected without satisfying the gate."""


class IntegrityError(Exception):
    """A skill file no longer matches its Harness baseline hash."""


EXIT_CONFIG_ERROR = 2
EXIT_ENV_FILE_REFUSED = 4
EXIT_PROD_GATE = 3
EXIT_INTEGRITY = 5


def fail(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


# --------------------------------------------------------------------------
# Repo root / skill dir
# --------------------------------------------------------------------------

def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def find_repo_root(start: "str | Path | None" = None) -> Path:
    """Nearest ancestor of `start` (default: cwd) containing `.git`."""
    root_override = os.environ.get("SLT_ROOT")
    if root_override:
        return Path(root_override).resolve()
    cur = Path(start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / ".git").exists():
            return candidate
    return cur


# --------------------------------------------------------------------------
# Skill integrity (Harness baseline hashes)
# --------------------------------------------------------------------------

def find_harness_root(start: Path) -> "Path | None":
    """Nearest ancestor of `start` holding `.harness-core/manifest.json`.
    Derived from the skill's own location, never from SLT_ROOT or --root."""
    for candidate in [start, *start.parents]:
        if (candidate / ".harness-core" / "manifest.json").is_file():
            return candidate
    return None


def verify_skill_integrity(skill: "Path | None" = None, harness_root: "Path | None" = None) -> None:
    """Raise IntegrityError unless every file under the skill directory
    (ignoring __pycache__) is listed in the Harness manifest with a matching
    sha256, and every manifest entry for the skill still exists."""
    skill = (skill or skill_dir()).resolve()
    harness_root = Path(harness_root).resolve() if harness_root else find_harness_root(skill)
    if harness_root is None:
        raise IntegrityError(
            f"No .harness-core/manifest.json found above {skill}; this skill only runs "
            "as a Harness-managed install."
        )
    manifest = json.loads((harness_root / ".harness-core" / "manifest.json").read_text(encoding="utf-8"))
    prefix = skill.relative_to(harness_root).as_posix() + "/"
    expected = {
        e["path"]: e["upstream_sha256"]
        for e in manifest.get("files", [])
        if isinstance(e, dict) and str(e.get("path", "")).startswith(prefix)
    }
    problems = []
    seen = set()
    for f in sorted(skill.rglob("*")):
        if not f.is_file() or "__pycache__" in f.parts:
            continue
        rel = f.relative_to(harness_root).as_posix()
        seen.add(rel)
        digest = hashlib.sha256(f.read_bytes()).hexdigest()
        if rel not in expected:
            problems.append(f"unmanaged file {rel}")
        elif expected[rel] != digest:
            problems.append(f"modified {rel}")
    problems += [f"missing {rel}" for rel in sorted(set(expected) - seen)]
    if problems:
        raise IntegrityError(
            "Refusing to run: system-log-tracer files differ from the Harness baseline ("
            + "; ".join(problems)
            + "). Do not edit skill files to get past a guard; report the blocked "
            "operation to the user. Legitimate changes go through the Harness update "
            "workflow (base snapshot + manifest hash)."
        )


def _enforce_integrity_on_import() -> None:
    try:
        verify_skill_integrity()
    except IntegrityError as exc:
        fail(str(exc), EXIT_INTEGRITY)


# --------------------------------------------------------------------------
# .env placement refusal
# --------------------------------------------------------------------------

def _env_like_files(directory: Path):
    if not directory.is_dir():
        return []
    found = []
    for p in directory.iterdir():
        if not p.is_file():
            continue
        if p.name == ".env" or (p.name.startswith("system-log-tracer") and p.name.endswith(".env")):
            found.append(p)
    return found


def refuse_if_env_files_present(repo_root: Path) -> None:
    """Refuse to run if a `.env` sits in the skill directory or in
    `<repo-root>/.agents/config/`. These are the only two locations this
    skill treats as in-repository credential leakage risk for itself; other
    application `.env` files elsewhere in the consumer repo are out of scope.
    """
    violations = list(_env_like_files(skill_dir()))
    violations += _env_like_files(repo_root / ".agents" / "config")
    if violations:
        names = ", ".join(str(p) for p in violations)
        raise EnvFileRefused(
            "Refusing to run: found .env file(s) in a location this skill treats as "
            f"in-repository secret leakage risk: {names}. Store credentials at "
            "~/.config/system-log-tracer/<env>.env (mode 600) instead, or set "
            "SLT_CREDENTIALS_DIR for tests."
        )


# --------------------------------------------------------------------------
# Minimal stdlib JSON-Schema-subset validator
# --------------------------------------------------------------------------

def validate_schema(instance, schema, path="$"):
    """Validate `instance` against the subset of JSON Schema this project
    uses: type, required, properties, additionalProperties, items, enum,
    minItems. Returns a list of human-readable error strings (empty = valid).
    """
    errors = []
    t = schema.get("type")
    if t:
        ok = {
            "object": isinstance(instance, dict),
            "array": isinstance(instance, list),
            "string": isinstance(instance, str),
            "boolean": isinstance(instance, bool),
            "number": isinstance(instance, (int, float)) and not isinstance(instance, bool),
        }.get(t, True)
        if not ok:
            errors.append(f"{path}: expected type '{t}', got '{type(instance).__name__}'")
            return errors

    if t == "object" and isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property '{req}'")
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in props:
                errors.extend(validate_schema(value, props[key], f"{path}.{key}"))
            elif isinstance(additional, dict):
                errors.extend(validate_schema(value, additional, f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}: unexpected property '{key}'")

    if t == "array" and isinstance(instance, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} item(s)")
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(instance):
                errors.extend(validate_schema(item, items_schema, f"{path}[{i}]"))

    enum = schema.get("enum")
    if enum is not None and instance not in enum:
        errors.append(f"{path}: value {instance!r} is not one of {enum}")

    return errors


def config_path(repo_root: Path) -> Path:
    return repo_root / ".agents" / "config" / "system-log-tracer.json"


def load_schema() -> dict:
    return json.loads((skill_dir() / "config.schema.json").read_text(encoding="utf-8"))


def load_config(repo_root: Path) -> dict:
    path = config_path(repo_root)
    if not path.is_file():
        raise ConfigError(
            f"Config not found at {path}. Copy "
            f"{skill_dir() / 'config.example.json'} there and edit it for your "
            "environments and services."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config at {path} is not valid JSON: {exc}") from exc

    schema = load_schema()
    errors = validate_schema(data, schema)
    envs = data.get("environments") if isinstance(data, dict) else None
    if isinstance(envs, dict) and envs:
        if not any(isinstance(v, dict) and not v.get("isProduction", False) for v in envs.values()):
            errors.append("$.environments: at least one environment must have isProduction=false")
    if errors:
        bullet_list = "\n  - ".join(errors)
        raise ConfigError(f"Config at {path} failed validation:\n  - {bullet_list}")
    return data


# --------------------------------------------------------------------------
# Credentials
# --------------------------------------------------------------------------

def credentials_dir() -> Path:
    override = os.environ.get("SLT_CREDENTIALS_DIR")
    if override:
        return Path(override)
    return Path.home() / ".config" / "system-log-tracer"


def credentials_path(env_name: str) -> Path:
    return credentials_dir() / f"{env_name}.env"


def _parse_env_text(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip("'\"")
    return out


def check_credential_file_mode(path: Path):
    """Return the offending mode (int) if broader than 600, else None."""
    try:
        mode = path.stat().st_mode & 0o777
    except FileNotFoundError:
        return None
    if mode & 0o077:
        return mode
    return None


def load_credentials(env_name: str) -> dict:
    """Credentials for `env_name`: file (if present) merged under process env
    overrides are NOT applied here (process env is read directly by cfg() as a
    fallback when a key is missing from the file).
    """
    path = credentials_path(env_name)
    if not path.is_file():
        return {}
    bad_mode = check_credential_file_mode(path)
    if bad_mode is not None:
        print(
            f"WARNING: credential file {path} has mode {oct(bad_mode)[-3:]}; "
            "expected 600 or stricter. Tighten it with `chmod 600`.",
            file=sys.stderr,
        )
    return _parse_env_text(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Environment selection / prod gate
# --------------------------------------------------------------------------

def select_environment(config: dict, requested_env, confirm_prod: bool):
    envs = config.get("environments") or {}
    if not envs:
        raise ConfigError("Config has no environments defined.")

    if requested_env is None:
        for name, spec in envs.items():
            if not spec.get("isProduction", False):
                requested_env = name
                break
        else:
            raise ConfigError(
                "Config defines only production environments; pass --env explicitly."
            )

    if requested_env not in envs:
        raise ConfigError(f"Unknown environment '{requested_env}'. Known: {', '.join(envs)}")

    spec = envs[requested_env]
    is_prod = bool(spec.get("isProduction", False))
    if is_prod:
        if not confirm_prod:
            raise ProdGateError(
                f"Environment '{requested_env}' is production. Refusing without "
                "--confirm-prod. Ask the user for explicit chat confirmation before "
                f"re-running with --env {requested_env} --confirm-prod."
            )
        cred_path = credentials_path(requested_env)
        if not cred_path.is_file():
            raise ProdGateError(
                f"Environment '{requested_env}' is production and also requires the "
                f"credential file {cred_path} to exist, in addition to --confirm-prod. "
                "Refusing."
            )
    creds = load_credentials(requested_env)
    return requested_env, spec, creds, is_prod


def _parse_common_flags():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--env")
    parser.add_argument("--root")
    parser.add_argument("--confirm-prod", action="store_true")
    args, _ = parser.parse_known_args()
    return args


def env_bool(name, default=True):
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() not in {"0", "false", "no", "off"}


def cfg(env: "str | None" = None, root: "str | Path | None" = None, confirm_prod: "bool | None" = None) -> dict:
    """Build the flattened runtime config used by every tool. Reads --env /
    --root / --confirm-prod from argv when not passed explicitly (so existing
    tool scripts don't each need their own argparse wiring for these flags).
    """
    flags = _parse_common_flags()
    env = env if env is not None else flags.env
    root = root if root is not None else flags.root
    confirm_prod = confirm_prod if confirm_prod is not None else flags.confirm_prod

    repo_root = find_repo_root(root)
    try:
        refuse_if_env_files_present(repo_root)
        config = load_config(repo_root)
        env_name, spec, creds, is_prod = select_environment(config, env, confirm_prod)
    except EnvFileRefused as exc:
        fail(str(exc), EXIT_ENV_FILE_REFUSED)
    except ConfigError as exc:
        fail(str(exc), EXIT_CONFIG_ERROR)
    except ProdGateError as exc:
        fail(str(exc), EXIT_PROD_GATE)

    def pick(key, default=""):
        return creds.get(key, os.environ.get(key, default))

    es = spec.get("elasticsearch") or {}
    kb = spec.get("kibana") or {}
    redis = spec.get("redis") or {}
    mongo = spec.get("mongo") or {}
    kafka = spec.get("kafka") or {}
    limits = config.get("limits") or {}

    return {
        "repo_root": repo_root,
        "env_name": env_name,
        "is_production": is_prod,
        "services": config.get("services") or {},
        "kafka_topics": config.get("kafkaTopics") or [],
        "stack_trace_rewrites": config.get("stackTracePathRewrites") or [],
        "redaction_fields": config.get("redactionFields") or [],
        # Elasticsearch / Kibana
        "es_url": (es.get("url") or "").rstrip("/"),
        "es_api_key": pick("ELASTICSEARCH_API_KEY"),
        "es_user": pick("ELASTICSEARCH_USERNAME"),
        "es_pass": pick("ELASTICSEARCH_PASSWORD"),
        "kb_url": (kb.get("url") or "").rstrip("/"),
        "kb_api_key": pick("KIBANA_API_KEY"),
        "kb_user": pick("KIBANA_USERNAME"),
        "kb_pass": pick("KIBANA_PASSWORD"),
        "index": spec.get("indexPattern", "*"),
        "time_field": spec.get("timeField", "@timestamp"),
        "source": os.getenv("DEFAULT_SOURCE", ""),
        "size": int(limits.get("maxHits", 100)),
        "max_documents": int(limits.get("maxDocuments", 50)),
        "default_fields": limits.get("defaultFields", []),
        # Redis
        "redis_host": redis.get("host", "127.0.0.1"),
        "redis_port": int(redis.get("port", 6379)),
        "redis_pass": pick("REDIS_PASSWORD"),
        # MongoDB (connection string is a secret; non-secret db name list from config)
        "mongo_uri": pick("MONGO_URI", "mongodb://127.0.0.1:27017"),
        "mongo_user": pick("MONGO_USER"),
        "mongo_pass": pick("MONGO_PASSWORD"),
        "mongo_dbs": mongo.get("dbs") or [],
        # Kafka
        "kafka_brokers": pick("KAFKA_BROKERS", ",".join(kafka.get("brokers") or []) or "localhost:9092"),
        "kafka_client_id": pick("KAFKA_CLIENT_ID", "system-log-tracer"),
        # TLS & timeouts
        "verify": env_bool("VERIFY_SSL", True),
        "timeout": float(os.getenv("REQUEST_TIMEOUT", "30")),
    }


# --------------------------------------------------------------------------
# Redaction
# --------------------------------------------------------------------------

DEFAULT_SENSITIVE_FIELDS = (
    "password", "pushtoken", "token", "refreshtoken", "accesstoken", "secret",
    "salt", "authorization", "sessionid", "session_id", "apikey", "api_key",
    "email", "phone", "phonenumber", "mobile", "latitude", "longitude", "lat",
    "lng", "lon", "coordinates", "coords",
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Bounded by characters that cannot continue an identifier (alphanumerics or
# '-') so hex IDs such as ObjectIds and UUID segments are not mistaken for
# phone numbers.
PHONE_RE = re.compile(r"(?<![0-9A-Za-z\-])\+?\d[\d\-.\s]{7,14}\d(?![0-9A-Za-z\-])")
COORD_PAIR_RE = re.compile(r"-?\d{1,3}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,}")
JSON_SECRET_VALUE_RE = re.compile(
    r'("(?:password|pushToken|token|refreshToken|accessToken|secret|salt|authorization|'
    r'sessionId|apiKey)"\s*:\s*)"[^"]*"',
    re.IGNORECASE,
)
KV_SECRET_VALUE_RE = re.compile(
    r"((?:password|token|secret|pushToken|apikey)=\s*)[^\s&]+", re.IGNORECASE
)


def _sensitive_key_pattern(extra_fields=None):
    names = set(DEFAULT_SENSITIVE_FIELDS) | {f.lower() for f in (extra_fields or [])}
    alternation = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(rf"^({alternation})$", re.IGNORECASE)


def redact_sensitive(data, extra_fields=None):
    """Recursively mask credentials, tokens, emails, phone numbers, and
    precise coordinates. Safe to call on arbitrary JSON-shaped data or plain
    strings (e.g. raw log lines, stack traces, Kafka message values).
    """
    pattern = _sensitive_key_pattern(extra_fields)
    return _redact_value(data, pattern)


def _redact_value(data, pattern):
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            # Type-preserving Extended JSON wrappers ({"$oid"}, {"$date"})
            # carry identifiers and timestamps, never personal data: keep
            # them intact even though "oid"/"date" are not sensitive key
            # names themselves, so the string value is never mangled by the
            # phone/email/coordinate patterns below.
            if k in ("$oid", "$date") and isinstance(v, str):
                out[k] = v
            elif isinstance(k, str) and pattern.search(k):
                out[k] = "[REDACTED]"
            else:
                out[k] = _redact_value(v, pattern)
        return out
    if isinstance(data, list):
        return [_redact_value(x, pattern) for x in data]
    if isinstance(data, str):
        text = JSON_SECRET_VALUE_RE.sub(r'\1"[REDACTED]"', data)
        text = KV_SECRET_VALUE_RE.sub(r"\1[REDACTED]", text)
        text = COORD_PAIR_RE.sub("[REDACTED_COORDINATES]", text)
        text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
        # Phone-number masking only runs on strings that are not plain small
        # integers/ids, to avoid destroying unrelated numeric content; it
        # still intentionally over-redacts digit runs that look phone-shaped.
        text = PHONE_RE.sub("[REDACTED_PHONE]", text)
        return text
    return data


def dump(obj, extra_redaction_fields=None):
    sanitized = redact_sensitive(obj, extra_redaction_fields)
    print(json.dumps(sanitized, ensure_ascii=False, indent=2, default=str))


# --------------------------------------------------------------------------
# Elasticsearch / Kibana read-only guard + HTTP
# --------------------------------------------------------------------------

_ES_READ_LAST_SEGMENTS = ("_search", "_count", "_mapping")
_ES_READ_EXACT_PATHS = ("/_query", "/_search/scroll")
_KIBANA_READ_GET_PATHS = ("/api/status",)
_ES_FORBIDDEN_SUBSTRINGS = (
    "_bulk", "_update", "_delete_by_query", "_update_by_query", "_doc", "_create",
    "_close", "_open", "_reindex", "_settings",
)


def validate_es_request(method: str, path: str) -> None:
    """Raise PermissionError if this is not a recognized read-only ES/Kibana
    call. Matching is by path segment, not substring: the last segment must be
    a read API (`_search`, `_count`, `_mapping`), or the path must be ES|QL
    `/_query`, scroll, the root info endpoint, or Kibana `GET /api/status`.
    """
    method_u = method.upper()
    path_l = path.lower().split("?", 1)[0].rstrip("/") or "/"
    if method_u not in ("GET", "POST"):
        raise PermissionError(f"HTTP method '{method}' is not permitted in this read-only skill")
    if any(bad in path_l for bad in _ES_FORBIDDEN_SUBSTRINGS):
        raise PermissionError(f"Path '{path}' looks like a write/administrative endpoint and is blocked")
    if path_l == "/":
        return
    if method_u == "GET" and path_l in _KIBANA_READ_GET_PATHS:
        return
    if path_l in _ES_READ_EXACT_PATHS:
        return
    if path_l.rsplit("/", 1)[-1] in _ES_READ_LAST_SEGMENTS:
        return
    raise PermissionError(f"Path '{path}' is not an allow-listed read-only endpoint")


def validate_esql_query(query: str) -> None:
    q = query.strip().upper()
    if not q.startswith(("FROM ", "ROW ", "SHOW ", "META ")):
        raise PermissionError("ES|QL query must start with FROM, ROW, SHOW, or META in this read-only skill")


def do_request(base, method, path, *, api_key="", user="", password="", body=None, extra_headers=None, timeout=30.0, verify=True):
    validate_es_request(method, path)
    if not base:
        raise RuntimeError("Base URL is not configured")
    url = base.rstrip("/") + "/" + path.lstrip("/")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"ApiKey {api_key}"
    elif user and password:
        b64 = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {b64}"
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl._create_unverified_context() if not verify else None

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            if not content.strip():
                return {}
            try:
                return json.loads(content)
            except Exception:
                return {"text": content}
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {text}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection failed to {base}: {e.reason}") from e


def es(method, path, body=None, c=None):
    c = c or cfg()
    return do_request(
        c["es_url"], method, path, api_key=c["es_api_key"], user=c["es_user"],
        password=c["es_pass"], body=body, timeout=c["timeout"], verify=c["verify"],
    )


def kb(method, path, body=None, c=None):
    c = c or cfg()
    return do_request(
        c["kb_url"], method, path, api_key=c["kb_api_key"], user=c["kb_user"],
        password=c["kb_pass"], body=body, extra_headers={"kbn-xsrf": "true"},
        timeout=c["timeout"], verify=c["verify"],
    )


def index_path(suffix, c=None):
    c = c or cfg()
    return "/" + quote(c["index"], safe="*,-_:.") + suffix


def source_summary(hit):
    src = hit.get("_source", {}) or {}
    return {
        "@timestamp": src.get("@timestamp") or src.get("timestamp"),
        "requestId": src.get("requestId") or src.get("request_id") or src.get("traceId") or src.get("correlationId"),
        "source": src.get("source"),
        "service": src.get("service") or src.get("@log_name"),
        "method": src.get("method"),
        "url": src.get("url"),
        "statusCode": src.get("statusCode") or src.get("status"),
        "error": src.get("error") or src.get("errorMessage"),
        "body": redact_sensitive(src.get("body")),
    }


def add_common_args(parser):
    """Attach the shared --env/--root/--confirm-prod flags to a tool's own
    argparse.ArgumentParser so --help documents them and parse_args() does not
    reject them as unknown. cfg() reads the same flags independently from
    sys.argv, so the parsed namespace values are not otherwise consumed here.
    """
    parser.add_argument("--env", help="Environment name from config (default: first non-production)")
    parser.add_argument("--root", help="Repository root override (default: nearest ancestor with .git)")
    parser.add_argument("--confirm-prod", action="store_true", help="Required with --env <production env> to use a production environment")
    return parser


_enforce_integrity_on_import()
