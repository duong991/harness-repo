#!/usr/bin/env python3
"""
healthcheck.py - Unified read-only reachability check across Elasticsearch,
Kibana, Redis, MongoDB, and Kafka for the selected environment.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import add_common_args, cfg, es, kb, dump
from inspect_redis import ReadOnlyRedisClient


def check_es(c):
    if not c["es_url"]:
        return {"ok": False, "error": "elasticsearch.url not set for this environment"}
    try:
        info = es("GET", "/", c=c)
        return {"ok": True, "url": c["es_url"], "cluster_name": info.get("cluster_name"), "version": (info.get("version") or {}).get("number")}
    except Exception as exc:
        return {"ok": False, "url": c["es_url"], "error": str(exc)}


def check_kibana(c):
    if not c["kb_url"]:
        return {"ok": None, "note": "kibana.url not set for this environment"}
    try:
        st = kb("GET", "/api/status", c=c)
        ver = st.get("version", {}) if isinstance(st, dict) else {}
        return {"ok": True, "url": c["kb_url"], "version": ver.get("number") if isinstance(ver, dict) else ver}
    except Exception as exc:
        return {"ok": False, "url": c["kb_url"], "error": str(exc)}


def check_redis(c):
    host, port, password = c["redis_host"], c["redis_port"], c["redis_pass"]
    try:
        client = ReadOnlyRedisClient(host=host, port=port, password=password, timeout=3.0)
        res = client.execute("PING")
        return {"ok": True, "host": f"{host}:{port}", "response": res}
    except Exception as exc:
        return {"ok": False, "host": f"{host}:{port}", "error": str(exc)}


def check_mongo(c):
    tool_path = Path(__file__).resolve().with_name("inspect_mongo.js")
    try:
        proc = subprocess.run(["node", str(tool_path), "--list-collections"], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            parsed = json.loads(proc.stdout)
            return {"ok": True, "database": parsed.get("database"), "collections_count": len(parsed.get("collections", []))}
        return {"ok": False, "error": proc.stderr.strip()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_kafka(c):
    tool_path = Path(__file__).resolve().with_name("trace_kafka.js")
    try:
        proc = subprocess.run(["node", str(tool_path), "--list-topics"], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            parsed = json.loads(proc.stdout)
            return {"ok": True, "brokers": parsed.get("brokers"), "topics_count": parsed.get("count", 0)}
        return {"ok": False, "error": proc.stderr.strip()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main():
    p = argparse.ArgumentParser(description="Unified read-only health check across all five subsystems")
    add_common_args(p)
    p.parse_args()

    c = cfg()
    results = {
        "environment": c["env_name"],
        "elasticsearch": check_es(c),
        "kibana": check_kibana(c),
        "redis": check_redis(c),
        "mongodb": check_mongo(c),
        "kafka": check_kafka(c),
    }
    dump(results, c["redaction_fields"])

    all_failed = all(v.get("ok") is False for v in results.values() if isinstance(v, dict) and v.get("ok") is not None)
    sys.exit(1 if all_failed else 0)


if __name__ == "__main__":
    main()
