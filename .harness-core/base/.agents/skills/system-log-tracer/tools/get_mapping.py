#!/usr/bin/env python3
"""get_mapping.py - Inspect the field mapping of the configured index pattern."""
import argparse
from common import add_common_args, cfg, es, dump, index_path

p = argparse.ArgumentParser(description="Elasticsearch index field mapping inspector")
add_common_args(p)
p.add_argument("--field", action="append", default=[])
a = p.parse_args()

c = cfg()
res = es("GET", index_path("/_mapping", c), c=c)
if not a.field:
    dump(res, c["redaction_fields"])
    raise SystemExit


def walk(props, prefix=""):
    out = {}
    for k, v in (props or {}).items():
        name = f"{prefix}.{k}" if prefix else k
        out[name] = {"type": v.get("type"), "fields": list((v.get("fields") or {}).keys())}
        if "properties" in v:
            out.update(walk(v["properties"], name))
    return out


found = {}
for idx, m in res.items():
    flat = walk((((m or {}).get("mappings") or {}).get("properties") or {}))
    found[idx] = {f: flat.get(f) for f in a.field}
dump(found, c["redaction_fields"])
