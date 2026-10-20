#!/usr/bin/env python3
"""
parse_export.py - Parse and correlate Kibana Discover log exports (CSV/JSON).

Capabilities:
1. Formats Supported: CSV exports from Kibana Discover, JSON arrays, and
   line-delimited JSON.
2. Chronological Correlation: reconstructs a timeline across services.
3. Code Mapping: translates container stack-trace paths into local repository
   paths using the config's `stackTracePathRewrites` (falls back to a generic
   `/app/<service>/(dist/)?...` -> `apps/<service>/...` convention when no
   config is available offline).
4. Sanitization: redacts secrets, tokens, emails, phone numbers, and precise
   coordinates.
5. Output: human-readable markdown timeline, or structured JSON.

There is no Trash/backup recovery: an empty or near-empty export is always
reported as a clear user-facing error.
"""
import sys
import csv
import json
import re
import argparse
from datetime import datetime
from pathlib import Path

# Importing common is mandatory: it verifies the skill's Harness baseline
# integrity before this tool reads anything. Config itself stays optional.
from common import load_config, find_repo_root, redact_sensitive as _common_redact, ConfigError


def load_optional_rewrite_rules(repo_root_arg):
    """Best-effort: load stackTracePathRewrites/redactionFields from config if
    present; never fail the tool over missing/invalid config."""
    if load_config is None or find_repo_root is None:
        return [], []
    try:
        root = find_repo_root(repo_root_arg)
        config = load_config(root)
        return config.get("stackTracePathRewrites") or [], config.get("redactionFields") or []
    except Exception:
        return [], []


def redact_sensitive(text, extra_fields=None):
    if _common_redact is not None:
        return _common_redact(text, extra_fields)
    if not isinstance(text, str):
        return text
    text = re.sub(r'("(?:password|pushToken|token|refreshToken|accessToken)":\s*)"[^"]+"', r'\1"[REDACTED]"', text)
    text = re.sub(r'((?:password|token|secret)=\s*)[^\s&]+', r'\1[REDACTED]', text, flags=re.IGNORECASE)
    return text


def parse_ts(val):
    if not val or val == "-":
        return 0.0
    val = str(val).strip()
    if val.replace(",", "").isdigit():
        num = int(val.replace(",", ""))
        if num > 1e11:
            return num / 1000.0
        return float(num)
    try:
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        return dt.timestamp()
    except Exception:
        pass
    for fmt in ("%b %d, %Y %H:%M:%S.%f", "%b %d, %Y %H:%M:%S"):
        try:
            cleaned = val.replace(" @ ", " ")
            return datetime.strptime(cleaned, fmt).timestamp()
        except Exception:
            pass
    return 0.0


def map_stack_frame(line, repo_root=".", rewrite_rules=None):
    m = re.search(r'at (?:async )?([^\s]+) \((.+?):(\d+):(\d+)\)', line)
    if not m:
        m = re.search(r'at (.+?):(\d+):(\d+)', line)
        if not m:
            return None
        fn = ""
        raw_path, line_no, col_no = m.group(1), m.group(2), m.group(3)
    else:
        fn, raw_path, line_no, col_no = m.group(1), m.group(2), m.group(3), m.group(4)

    local_path = None
    root = Path(repo_root)

    for rule in (rewrite_rules or []):
        prefix = rule.get("containerPrefix")
        repo_prefix = rule.get("repoPrefix")
        if prefix and raw_path.startswith(prefix):
            rest = raw_path[len(prefix):]
            rest_ts = re.sub(r'\.js$', '.ts', rest)
            candidate = root / repo_prefix / rest_ts
            local_path = str(candidate) if candidate.exists() else f"{repo_prefix}{rest_ts}"
            break

    if local_path is None:
        # Generic fallback convention when no config rewrite rule matched.
        app_m = re.match(r'/app/([^/]+)/(?:dist/)?(.*)', raw_path)
        if app_m:
            service, rest = app_m.group(1), app_m.group(2)
            rest_ts = re.sub(r'\.js$', '.ts', rest)
            candidate1 = root / "apps" / service / rest_ts
            candidate2 = root / "apps" / service / rest
            candidate3 = root / "packages" / service / rest_ts
            if candidate1.exists():
                local_path = str(candidate1)
            elif candidate2.exists():
                local_path = str(candidate2)
            elif candidate3.exists():
                local_path = str(candidate3)
            else:
                local_path = f"apps/{service}/{rest_ts}"

    return {
        "function": fn,
        "raw_path": raw_path,
        "local_path": local_path,
        "line": int(line_no),
        "col": int(col_no),
    }


def parse_file(path_str, repo_root=".", rewrite_rules=None, redaction_fields=None):
    p = Path(path_str)

    if not p.exists():
        raise FileNotFoundError(f"File not found: {path_str}")

    if p.stat().st_size <= 1:
        raise ValueError(
            f"File '{path_str}' is empty or contains only a single newline (1 byte). "
            "In Kibana Discover this usually means the search returned 0 hits "
            "(e.g. the time range was too narrow, such as 'now-15m'). Widen the "
            "time window in Kibana Discover, re-run the export, and pass the "
            "correct path to this tool; there is no automatic recovery."
        )

    events = []
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        content_peek = f.read(1024).strip()
        f.seek(0)
        if content_peek.startswith("[") or content_peek.startswith("{"):
            try:
                data = json.load(f)
                rows = data if isinstance(data, list) else [data]
            except Exception:
                f.seek(0)
                rows = [json.loads(line) for line in f if line.strip()]
        else:
            reader = csv.DictReader(f)
            rows = list(reader)

    for row in rows:
        started_at = row.get("started_at")
        ts_str = row.get("timestamp") or row.get("@timestamp") or ""
        epoch = parse_ts(started_at) if (started_at and started_at != "-") else parse_ts(ts_str)

        svc = row.get("service") or row.get("@log_name") or row.get("container_name") or "unknown"
        svc = svc.replace(".logs", "").replace("/", "")

        method = row.get("method") or ""
        url = row.get("url") or row.get("path") or row.get("upstream_uri") or ""
        status = row.get("statusCode") or row.get("status") or row.get("upstream_status") or ""
        req_id = row.get("requestId") or row.get("x-request-id") or ""
        level = row.get("level") or "info"
        msg = row.get("message") or ""
        err = row.get("errorMessage") or row.get("error") or ""
        stack = row.get("errorStack") or row.get("stack") or ""

        code_frames = []
        if stack and stack != "-":
            for sline in stack.splitlines():
                frame = map_stack_frame(sline, repo_root, rewrite_rules)
                if frame and frame.get("local_path"):
                    code_frames.append(frame)

        events.append({
            "epoch": epoch,
            "timestamp_str": ts_str,
            "service": svc,
            "level": level,
            "method": method,
            "url": url,
            "status": status,
            "requestId": req_id,
            "message": redact_sensitive(msg, redaction_fields),
            "error": redact_sensitive(err, redaction_fields),
            "code_frames": code_frames,
            "raw_stack": redact_sensitive(stack, redaction_fields) if stack != "-" else "",
        })

    events.sort(key=lambda e: e["epoch"])
    return events


def format_report(events, repo_root="."):
    lines = []
    lines.append("# Log Trace Analysis Report")
    lines.append("")

    req_ids = list({e['requestId'] for e in events if e.get('requestId') and e['requestId'] != "-"})
    services = list({e['service'] for e in events if e.get('service')})
    errors = [e for e in events if str(e.get('status')).startswith(('4', '5')) or e.get('level') in ('error', 'warn')]

    lines.append("## 1. Trace Overview")
    lines.append(f"- **Total Events**: {len(events)}")
    lines.append(f"- **Services Involved**: {', '.join(services)}")
    lines.append(f"- **Correlation IDs (requestId)**: {', '.join(req_ids) if req_ids else 'None found'}")
    if events:
        lines.append(f"- **Timeline Span**: {events[0]['timestamp_str']} -> {events[-1]['timestamp_str']}")
    lines.append("")

    lines.append("## 2. Chronological Timeline")
    lines.append("| # | Timestamp | Service | Level | Method | URL / Path | Status | Detail / Message |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, e in enumerate(events):
        msg_brief = e['message'].replace("\n", " ") if e['message'] and e['message'] != "-" else (e['error'] if e['error'] != "-" else "")
        msg_brief = msg_brief[:90] + "..." if len(msg_brief) > 90 else msg_brief
        status_disp = e['status'] if e['status'] and e['status'] != "-" else "-"
        method_disp = e['method'] if e['method'] and e['method'] != "-" else "-"
        url_disp = e['url'] if e['url'] and e['url'] != "-" else "-"
        lines.append(f"| {i+1:02d} | {e['timestamp_str']} | `{e['service']}` | {e['level']} | {method_disp} | `{url_disp}` | **{status_disp}** | {msg_brief} |")
    lines.append("")

    lines.append("## 3. Error Analysis & Code Mapping")
    if not errors:
        lines.append("No error-level events or 4xx/5xx status codes detected.")
    else:
        for err in errors:
            lines.append(f"### Service: `{err['service']}` ({err['level'].upper()})")
            if err['url'] and err['url'] != "-":
                lines.append(f"- **Endpoint**: `{err['method']} {err['url']}` (Status: **{err['status']}**)")
            if err['error'] and err['error'] != "-":
                lines.append(f"- **Error Message**: `{err['error']}`")
            if err['message'] and err['message'] != "-":
                lines.append(f"- **Log Message**: `{err['message']}`")

            if err['code_frames']:
                lines.append("- **Repository Code References**:")
                seen_paths = set()
                for cf in err['code_frames']:
                    key = f"{cf['local_path']}:{cf['line']}"
                    if key not in seen_paths:
                        seen_paths.add(key)
                        fn_str = f" in `{cf['function']}`" if cf['function'] else ""
                        lines.append(f"  - `{cf['local_path']}:{cf['line']}`{fn_str}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Parse and analyze Kibana Discover log exports (CSV/JSON)")
    parser.add_argument("--path", required=True, help="Path to exported CSV/JSON log file")
    parser.add_argument("--request-id", help="Filter by specific requestId")
    parser.add_argument("--json", action="store_true", help="Output raw JSON array instead of markdown report")
    parser.add_argument("--repo-root", default=".", help="Root of the consumer repository for code mapping")
    parser.add_argument("--root", help="Repository root override used to locate optional config for rewrite rules")
    args = parser.parse_args()

    rewrite_rules, redaction_fields = load_optional_rewrite_rules(args.root)

    try:
        events = parse_file(
            args.path,
            repo_root=args.repo_root,
            rewrite_rules=rewrite_rules,
            redaction_fields=redaction_fields,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.request_id:
        events = [e for e in events if e.get("requestId") == args.request_id]

    if args.json:
        payload = {"count": len(events), "events": events}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        report = format_report(events, repo_root=args.repo_root)
        print(report)



if __name__ == "__main__":
    main()
