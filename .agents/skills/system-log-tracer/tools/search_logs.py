#!/usr/bin/env python3
"""search_logs.py - Filtered read-only Elasticsearch log search by URL, body
fragment, request id, and/or time window."""
import argparse
from common import add_common_args, cfg, es, dump, index_path, source_summary

p = argparse.ArgumentParser(description="Read-only log search using Elasticsearch Query DSL")
add_common_args(p)
p.add_argument("--url", action="append", default=[])
p.add_argument("--source")
p.add_argument("--body-contains", action="append", default=[])
p.add_argument("--request-id")
p.add_argument("--request-field", default="requestId")
p.add_argument("--from", dest="from_")
p.add_argument("--to")
p.add_argument("--size", type=int)
p.add_argument("--raw", action="store_true", help="print full Elasticsearch response")
a = p.parse_args()
c = cfg()

filters = []
must = []
if a.url:
    should = []
    for v in a.url:
        should += [{"term": {"url.keyword": v}}, {"term": {"url": v}}, {"match_phrase": {"url": v}}]
    must.append({"bool": {"should": should, "minimum_should_match": 1}})
if a.source or c["source"]:
    v = a.source or c["source"]
    must.append({"bool": {"should": [{"term": {"source.keyword": v}}, {"term": {"source": v}}, {"match_phrase": {"source": v}}], "minimum_should_match": 1}})
for text in a.body_contains:
    must.append({"wildcard": {"body.keyword": {"value": f"*{text}*", "case_insensitive": True}}})
if a.request_id:
    must.append({"bool": {"should": [{"term": {f"{a.request_field}.keyword": a.request_id}}, {"term": {a.request_field: a.request_id}}, {"match_phrase": {a.request_field: a.request_id}}], "minimum_should_match": 1}})
if a.from_ or a.to:
    r = {}
    if a.from_:
        r["gte"] = a.from_
    if a.to:
        r["lte"] = a.to
    filters.append({"range": {c["time_field"]: r}})

query = {"bool": {"must": must or [{"match_all": {}}], "filter": filters}}
size = min(a.size or c["size"], c["size"])
body = {"size": size, "query": query, "sort": [{c["time_field"]: {"order": "asc", "unmapped_type": "date"}}]}
try:
    res = es("POST", index_path("/_search", c), body, c=c)
except Exception as e:
    # fallback for body mapped as text without a keyword subfield
    changed = False
    for clause in must:
        if "wildcard" in clause and "body.keyword" in clause["wildcard"]:
            val = clause["wildcard"]["body.keyword"]["value"].strip("*")
            clause.clear()
            clause.update({"match_phrase": {"body": val}})
            changed = True
    if not changed:
        raise
    res = es("POST", index_path("/_search", c), body, c=c)

if a.raw:
    dump(res, c["redaction_fields"])
else:
    hits = ((res.get("hits") or {}).get("hits") or [])
    dump({"count": len(hits), "total": (res.get("hits") or {}).get("total"), "hits": [source_summary(h) for h in hits]}, c["redaction_fields"])
