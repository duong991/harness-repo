#!/usr/bin/env python3
"""
trace_request.py - Query the configured Elasticsearch environment by
Request ID / Trace ID. Correlates all matching log events in ascending
chronological order. Output goes to stdout only; this tool never writes files.
"""
import argparse
from datetime import datetime
from pathlib import Path

from common import add_common_args, cfg, es, dump, index_path, source_summary, redact_sensitive


def format_live_report(request_id, hits, redaction_fields=None):
    lines = []
    lines.append(f"# Live Request Trace Report: `{request_id}`")
    lines.append("")

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"- **Captured At**: {date_str}")
    lines.append(f"- **Total Events Found**: {len(hits)}")

    services = set()
    errors = []
    for h in hits:
        src = h.get("_source", {}) or {}
        svc = src.get("service") or src.get("@log_name") or "unknown"
        services.add(svc)
        status = src.get("statusCode") or src.get("status")
        level = src.get("level") or "info"
        if (status and str(status).startswith(("4", "5"))) or level in ("error", "warn"):
            errors.append(src)

    lines.append(f"- **Services Involved**: {', '.join(sorted(services)) if services else 'None'}")
    lines.append("")

    lines.append("## 1. Chronological Timeline")
    lines.append("| # | Timestamp | Service | Level | Method | URL / Action | Status | Detail / Message |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, h in enumerate(hits):
        src = h.get("_source", {}) or {}
        ts = src.get("timestamp") or src.get("@timestamp") or "-"
        svc = src.get("service") or src.get("@log_name") or "-"
        lvl = src.get("level") or "info"
        method = src.get("method") or "-"
        url = src.get("url") or src.get("path") or "-"
        status = src.get("statusCode") or src.get("status") or "-"
        msg = redact_sensitive(src.get("message") or src.get("error") or "-", redaction_fields)
        msg = str(msg).replace("\n", " ")
        msg_brief = msg[:80] + "..." if len(msg) > 80 else msg
        lines.append(f"| {i+1:02d} | {ts} | `{svc}` | {lvl} | {method} | `{url}` | **{status}** | {msg_brief} |")
    lines.append("")

    lines.append("## 2. Error Analysis & Exceptions")
    if not errors:
        lines.append("No 4xx/5xx errors or warning events recorded for this request.")
    else:
        for err in errors:
            svc = err.get("service") or err.get("@log_name") or "unknown"
            lvl = err.get("level") or "error"
            lines.append(f"### Service: `{svc}` ({lvl.upper()})")
            if err.get("url"):
                lines.append(f"- **Endpoint**: `{err.get('method', '')} {err.get('url')}` (Status: **{err.get('statusCode') or err.get('status')}**)")
            if err.get("errorMessage") or err.get("error"):
                lines.append(f"- **Error Message**: `{redact_sensitive(err.get('errorMessage') or err.get('error'), redaction_fields)}`")
            if err.get("message"):
                lines.append(f"- **Log Message**: `{redact_sensitive(err.get('message'), redaction_fields)}`")
            if err.get("errorStack") or err.get("stack"):
                lines.append("- **Stack Trace Summary**:")
                st = redact_sensitive(err.get("errorStack") or err.get("stack"), redaction_fields)
                st_brief = "\n".join(str(st).splitlines()[:10])
                lines.append(f"```\n{st_brief}\n```")
            lines.append("")

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Query Elasticsearch by Request ID (stdout only)")
    add_common_args(p)
    p.add_argument("--request-id", required=True, help="Target Request ID / Trace ID")
    p.add_argument("--field", default="requestId", help="Field name for Request ID")
    p.add_argument("--size", type=int, default=500, help="Maximum events to return")
    p.add_argument("--json", action="store_true", help="Output raw JSON timeline instead of text")
    a = p.parse_args()
    c = cfg()
    size = min(a.size, c["size"])

    q = {
        "bool": {
            "should": [
                {"term": {f"{a.field}.keyword": a.request_id}},
                {"term": {a.field: a.request_id}},
                {"match_phrase": {a.field: a.request_id}},
            ],
            "minimum_should_match": 1,
        }
    }
    body = {"size": size, "query": q, "sort": [{c["time_field"]: {"order": "asc", "unmapped_type": "date"}}]}

    res = es("POST", index_path("/_search", c), body, c=c)
    hits = ((res.get("hits") or {}).get("hits") or [])

    if a.json:
        dump({"request_id": a.request_id, "field": a.field, "count": len(hits), "timeline": [source_summary(h) for h in hits]}, c["redaction_fields"])
    else:
        report = format_live_report(a.request_id, hits, c["redaction_fields"])
        print(report)



if __name__ == "__main__":
    main()
