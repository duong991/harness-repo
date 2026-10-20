#!/usr/bin/env python3
"""raw_search.py - Execute a raw read-only Elasticsearch Query DSL search body
against the configured index pattern. Only the `_search` endpoint is used;
the file content can never choose a different (write) API path."""
import argparse
import json
from pathlib import Path
from common import add_common_args, cfg, es, dump, index_path

p = argparse.ArgumentParser(description="Execute a raw read-only Query DSL search")
add_common_args(p)
p.add_argument("--file", required=True, help="Path to a JSON file containing a Query DSL search body")
a = p.parse_args()

body = json.loads(Path(a.file).read_text(encoding="utf-8"))
c = cfg()
res = es("POST", index_path("/_search", c), body, c=c)
dump(res, c["redaction_fields"])
