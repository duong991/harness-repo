#!/usr/bin/env python3
"""
router.py - Symptom -> tool routing helper for system-log-tracer. Uses the
consumer's config (services, kafkaTopics) when available; never hardcodes a
specific repository's service or topic names.
"""
import re
import json
import argparse

# Mandatory: importing common verifies the skill's Harness baseline integrity.
from common import load_config, find_repo_root


ROUTING_RULES = [
    {
        "id": "file_export",
        "target": "Kibana Discover / Exported File",
        "tool": "tools/parse_export.py",
        "pattern": r'\.(csv|json)\b|discover search|export|file',
        "template": 'python3 .agents/skills/system-log-tracer/tools/parse_export.py --path "{path}"',
        "rationale": "User provided a log export file (CSV/JSON) or mentions a downloaded Discover search.",
    },
    {
        "id": "uuid_request",
        "target": "Elasticsearch Live Trace",
        "tool": "tools/trace_request.py",
        "pattern": r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b|requestid|traceid',
        "template": 'python3 .agents/skills/system-log-tracer/tools/trace_request.py --request-id "{request_id}"',
        "rationale": "Explicit Request ID / Trace ID detected. Traces the request lifecycle across the configured index pattern.",
    },
    {
        "id": "redis_state",
        "target": "Redis Session & Cache",
        "tool": "tools/inspect_redis.py",
        "pattern": r'\bredis\b|session|refresh.?token|auth_context|ttl|rate_limit|hget|cache',
        "template": 'python3 .agents/skills/system-log-tracer/tools/inspect_redis.py --cmd GET --key "{key}"',
        "rationale": "Incident involves session tokens, refresh grants, cache state, or rate-limiting.",
    },
    {
        "id": "mongo_state",
        "target": "MongoDB Document State",
        "tool": "tools/inspect_mongo.py",
        "pattern": r'\bmongo\b|mongodb|collection|document|quota|subscription|entitlement|record|isdeleted',
        "template": "uv run --script .agents/skills/system-log-tracer/tools/inspect_mongo.py --collection {collection} --filter '{filter}'",
        "rationale": "Root cause requires verifying persistent database state.",
    },
    {
        "id": "kafka_stream",
        "target": "Kafka Event Stream",
        "tool": "tools/trace_kafka.py",
        "pattern": r'\bkafka\b|topic|event.?stream|message.?queue|producer|consumer|worker',
        "template": "uv run --script .agents/skills/system-log-tracer/tools/trace_kafka.py --topic {topic} --limit 10",
        "rationale": "Incident involves asynchronous messaging, event publishing/consumption, or background workers.",
    },
    {
        "id": "healthcheck",
        "target": "System Health & Connectivity",
        "tool": "tools/healthcheck.py",
        "pattern": r'\bhealth\b|status|ping|connectivity|cluster',
        "template": 'python3 .agents/skills/system-log-tracer/tools/healthcheck.py',
        "rationale": "User requests cluster reachability or subsystem connectivity diagnostics.",
    },
    {
        "id": "es_search",
        "target": "Elasticsearch Filtered Search",
        "tool": "tools/search_logs.py",
        "pattern": r'.*',
        "template": 'python3 .agents/skills/system-log-tracer/tools/search_logs.py --url "{url}" --body-contains "{text}"',
        "rationale": "General log search across recent index entries by endpoint, status code, or body fragment.",
    },
]

MUTATION_PATTERNS = re.compile(
    r'\b(fix|sửa|update|cập nhật|patch|modify|mutate|migrate|migration|restore|khôi phục|'
    r'delete|xóa|drop|truncate|alter|insert|write|chạy script sửa)\b',
    re.IGNORECASE,
)


def load_hints(root_arg=None):
    """Best-effort config read for example collection/topic names in output
    hints. Never required; routing works without config."""
    if load_config is None or find_repo_root is None:
        return [], []
    try:
        root = find_repo_root(root_arg)
        config = load_config(root)
        services = list((config.get("services") or {}).keys())
        topics = config.get("kafkaTopics") or []
        return services, topics
    except Exception:
        return [], []


def route(query, root_arg=None):
    q_lower = query.lower()

    if MUTATION_PATTERNS.search(q_lower):
        return {
            "status": "BLOCKED",
            "rule_id": "mutation_blocked",
            "target_system": "NONE - Mutation Attempt Blocked",
            "recommended_tool": "NONE",
            "suggested_command": "DO NOT RUN. The system-log-tracer skill is strictly read-only.",
            "rationale": "Running modification scripts, applying code fixes, or writing to databases is STRICTLY PROHIBITED in this skill.",
            "safety_note": "INVARIANT ENFORCED: evidence collection is 100% read-only. Hand off any fix to diagnosing-bugs after analysis.",
        }

    uuid_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', query, re.I)
    req_id = uuid_match.group(1) if uuid_match else "<request_id>"

    path_match = re.search(r'([^\s\'"]+\.(?:csv|json))', query, re.I)
    file_path = path_match.group(1) if path_match else "<path_to_file>"

    _services, topics = load_hints(root_arg)
    example_topic = topics[0] if topics else "<topic_name>"

    for rule in ROUTING_RULES:
        if re.search(rule["pattern"], q_lower):
            cmd = rule["template"].format(
                path=file_path, request_id=req_id, key="<key_pattern>",
                collection="<collection_name>", filter='{"_id": "..."}',
                topic=example_topic, url="/api/...", text="<error_or_text>",
            )
            return {
                "rule_id": rule["id"],
                "target_system": rule["target"],
                "recommended_tool": rule["tool"],
                "suggested_command": cmd,
                "rationale": rule["rationale"],
                "safety_note": "STRICT READ-ONLY. All sensitive fields (passwords, tokens, emails, phones, coordinates) are automatically masked.",
            }

    rule = ROUTING_RULES[-1]
    return {
        "rule_id": rule["id"],
        "target_system": rule["target"],
        "recommended_tool": rule["tool"],
        "suggested_command": rule["template"].format(url="/api/...", text="<search_term>"),
        "rationale": rule["rationale"],
        "safety_note": "STRICT READ-ONLY. All sensitive fields are masked.",
    }


def main():
    p = argparse.ArgumentParser(description="Tool routing helper for system log investigation")
    p.add_argument("query", nargs="*", help="Incident description, error message, or log prompt")
    p.add_argument("--root", help="Repository root override for optional config hints")
    p.add_argument("--json", action="store_true", help="Output JSON format")
    args = p.parse_args()

    query_str = " ".join(args.query).strip()
    if not query_str:
        p.print_help()
        raise SystemExit(0)

    decision = route(query_str, args.root)
    if args.json:
        print(json.dumps(decision, ensure_ascii=False, indent=2))
    else:
        print("=== ROUTING DECISION ===")
        print(f"Target System   : {decision['target_system']}")
        print(f"Recommended Tool: {decision['recommended_tool']}")
        print(f"Suggested Action: {decision['suggested_command']}")
        print(f"Rationale       : {decision['rationale']}")
        print(f"Safety Note     : {decision['safety_note']}")


if __name__ == "__main__":
    main()
