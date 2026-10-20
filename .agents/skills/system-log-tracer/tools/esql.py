#!/usr/bin/env python3
"""esql.py - Execute a read-only ES|QL statement (FROM/ROW/SHOW/META only)."""
import argparse
from common import add_common_args, cfg, es, dump, validate_esql_query

p = argparse.ArgumentParser(description="Read-only ES|QL executor")
add_common_args(p)
p.add_argument("--query", required=True)
p.add_argument("--format", choices=["json", "csv"], default="json")
a = p.parse_args()

try:
    validate_esql_query(a.query)
except PermissionError as exc:
    raise SystemExit(f"ERROR: {exc}")

c = cfg()
res = es("POST", "/_query", {"query": a.query.strip()}, c=c)
dump(res, c["redaction_fields"])
