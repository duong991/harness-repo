#!/usr/bin/env python3
"""
mongo_guard.py - Pure, stdlib-only read-only guard and Extended JSON handling
for MongoDB operations. Importable WITHOUT the `pymongo` driver so tests can
exercise it even when the driver is not installed anywhere resolvable.

Covers two responsibilities that used to live in two separate Node modules:
  - mongo_guard.js: allow-list of read-only operations; recursive $out/$merge
    rejection in aggregation pipelines (including nested $facet/$unionWith).
  - mongo_ejson.js: MongoDB Extended JSON handling for filters/pipelines
    ({"$oid"}/{"$date"} anywhere; 24-hex string coercion only under `_id`
    keys) and type-preserving evidence output for driver results.

The `ObjectId` class used for coercion/detection is passed in by the caller
(typically `bson.ObjectId` from pymongo) so this module never needs the
driver to be importable. Any class named `ObjectId` whose instances expose a
`binary` attribute and a `__str__` returning the 24-hex id duck-types the
same way.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

HEX24_RE = re.compile(r"^[0-9a-fA-F]{24}$")
ID_OPERATORS = {"$eq", "$ne", "$in", "$nin"}

ALLOWED_OPERATIONS = {"find", "countDocuments", "distinct", "aggregate"}
FORBIDDEN_STAGES = {"$out", "$merge"}


class MongoWriteRejected(Exception):
    """Raised when a requested Mongo operation is outside the read-only allow-list."""


class EjsonError(Exception):
    """Raised for malformed MongoDB Extended JSON input ($oid/$date)."""


# ---------------------------------------------------------------------------
# Operation / pipeline allow-list
# ---------------------------------------------------------------------------

def find_forbidden_stage(node):
    """Recursively scan a pipeline (or any nested structure) for a forbidden
    write stage name, including inside $facet/$unionWith/$lookup
    sub-pipelines. Returns the stage name if found, else None."""
    if isinstance(node, list):
        for item in node:
            hit = find_forbidden_stage(item)
            if hit:
                return hit
        return None
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FORBIDDEN_STAGES:
                return key
            hit = find_forbidden_stage(value)
            if hit:
                return hit
    return None


def validate_mongo_operation(operation_name, options=None):
    """Validate a requested Mongo operation before it is ever sent to the
    driver. Raises MongoWriteRejected for anything outside the read-only
    allow-list, or an aggregate pipeline containing $out/$merge at any depth.
    """
    options = options or {}
    if operation_name not in ALLOWED_OPERATIONS:
        raise MongoWriteRejected(
            f"MongoDB operation '{operation_name}' is BLOCKED. This tool is strictly "
            f"read-only. Permitted operations: {', '.join(sorted(ALLOWED_OPERATIONS))}"
        )
    if operation_name == "aggregate":
        pipeline = options.get("pipeline") or []
        stage = find_forbidden_stage(pipeline)
        if stage:
            raise MongoWriteRejected(
                f"Aggregation stage '{stage}' is a write operation and is BLOCKED in "
                "this read-only skill."
            )
    return True


# ---------------------------------------------------------------------------
# Extended JSON input: {"$oid"} / {"$date"} anywhere; 24-hex coercion under _id
# ---------------------------------------------------------------------------

def _is_plain_dict(v):
    return isinstance(v, dict)


def make_object_id(object_id_cls, hex_str):
    if not isinstance(hex_str, str) or not HEX24_RE.match(hex_str):
        raise EjsonError(f"Invalid ObjectId '{hex_str}': expected 24 hexadecimal characters")
    return object_id_cls(hex_str)


def _parse_date(value):
    if not isinstance(value, str):
        raise EjsonError(f"Invalid $date '{value}'")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise EjsonError(f"Invalid $date '{value}'") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def from_extended_json(value, object_id_cls):
    """Convert explicit {"$oid"} / {"$date"} wrappers anywhere in a parsed
    JSON value (dict/list/scalar) into ObjectId / datetime instances."""
    if isinstance(value, list):
        return [from_extended_json(v, object_id_cls) for v in value]
    if not _is_plain_dict(value):
        return value
    keys = list(value.keys())
    if keys == ["$oid"]:
        if not isinstance(value["$oid"], str):
            raise EjsonError("$oid must be a string")
        return make_object_id(object_id_cls, value["$oid"])
    if keys == ["$date"]:
        return _parse_date(value["$date"])
    return {k: from_extended_json(v, object_id_cls) for k, v in value.items()}


def coerce_id_value(value, object_id_cls):
    if isinstance(value, str) and HEX24_RE.match(value):
        return make_object_id(object_id_cls, value)
    if isinstance(value, list):
        return [coerce_id_value(v, object_id_cls) for v in value]
    if _is_plain_dict(value):
        return {
            k: (coerce_id_value(v, object_id_cls) if k in ID_OPERATORS else v)
            for k, v in value.items()
        }
    return value


def coerce_id_fields(value, object_id_cls):
    """Coerce 24-hex strings under `_id` keys at any depth (e.g. inside
    $or/$match/$and), including inside $eq/$ne/$in/$nin under _id."""
    if isinstance(value, list):
        return [coerce_id_fields(v, object_id_cls) for v in value]
    if not _is_plain_dict(value):
        return value
    out = {}
    for k, v in value.items():
        out[k] = coerce_id_value(v, object_id_cls) if k == "_id" else coerce_id_fields(v, object_id_cls)
    return out


def prepare_query(parsed, object_id_cls):
    """Full input preparation for a --filter or --pipeline value."""
    return coerce_id_fields(from_extended_json(parsed, object_id_cls), object_id_cls)


def id_like_string_fields(value, prefix=""):
    """Non-_id field paths whose value is a plain 24-hex string (hint
    candidates for a zero-result query that may need {"$oid": ...})."""
    found = []

    def walk(v, path):
        if isinstance(v, str) and HEX24_RE.match(v) and not re.search(r"(^|\.)_id$", path):
            if path:
                found.append(path)
        elif isinstance(v, list):
            for item in v:
                walk(item, path)
        elif _is_plain_dict(v):
            for k, child in v.items():
                walk(child, path if k.startswith("$") else (f"{path}.{k}" if path else k))

    walk(value, prefix or "")
    seen = []
    for f in found:
        if f and f not in seen:
            seen.append(f)
    return seen


# ---------------------------------------------------------------------------
# Output: type-preserving, JSON-safe evidence
# ---------------------------------------------------------------------------

def _bson_type_name(value, object_id_cls=None):
    """Best-effort BSON type name detection: prefer the caller-supplied
    ObjectId class; else duck-type a class literally named 'ObjectId' with a
    'binary' attribute (so tests can pass a stand-in without importing
    bson); else detect any value whose class lives in a module starting
    with 'bson' (the real pymongo/bson package layout)."""
    if object_id_cls is not None and isinstance(value, object_id_cls):
        return "ObjectId"
    cls = type(value)
    if cls.__name__ == "ObjectId" and hasattr(value, "binary"):
        return "ObjectId"
    module = cls.__module__ or ""
    if module.startswith("bson"):
        return cls.__name__
    return None


def to_evidence(value, object_id_cls=None):
    """Convert driver results into type-preserving, JSON-safe evidence:
    ObjectId -> {"$oid": hex}, datetime -> {"$date": ISO8601 UTC with Z},
    other bson-module types -> {"$<lowerCamel type name>": str(v)},
    bytes -> {"$binary": "<n bytes>"}; recurse into dict/list.
    """
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
        iso = dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"
        return {"$date": iso}

    # Containers first: bson.son.SON and similar are dict subclasses living in
    # a `bson` module and must be recursed into, never stringified.
    if isinstance(value, dict):
        return {k: to_evidence(v, object_id_cls) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_evidence(v, object_id_cls) for v in value]

    type_name = _bson_type_name(value, object_id_cls)
    if type_name == "ObjectId":
        return {"$oid": str(value)}
    if type_name:
        lower_camel = type_name[0].lower() + type_name[1:]
        return {f"${lower_camel}": str(value)}

    if isinstance(value, (bytes, bytearray)):
        return {"$binary": f"<{len(value)} bytes>"}
    return value


def bounded_pipeline(pipeline, limit):
    """Append a server-side `$limit` so an aggregation never streams more than
    `limit` documents back (minimal reads)."""
    return list(pipeline) + [{"$limit": int(limit)}]


MAX_DISTINCT_VALUES = 100


def bounded_values(values, cap=MAX_DISTINCT_VALUES):
    """Cap a distinct() result for output; report the full count separately."""
    values = list(values)
    return values[:cap], len(values)
