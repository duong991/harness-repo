#!/usr/bin/env python3
"""
healthcheck.py - Unified read-only reachability check across Elasticsearch,
Kibana, Redis, MongoDB, and Kafka for the selected environment.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from common import add_common_args, cfg, es, kb, dump
from inspect_redis import ReadOnlyRedisClient

UV = shutil.which("uv")


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


def _run_uv_script(tool_name, extra_args, timeout=20):
    """Invoke a `uv run --script` Mongo/Kafka tool with a short timeout. This
    deliberately does not import pymongo/confluent-kafka itself: uv resolves
    the pinned dependency (from each tool's PEP 723 header) in its own
    isolated environment, so healthcheck.py stays importable without either
    driver installed."""
    tool_path = Path(__file__).resolve().with_name(tool_name)
    command = f"uv run --script {tool_path} {' '.join(extra_args)}".strip()
    if not UV:
        return {
            "ok": None,
            "note": f"`uv` is not on PATH; run manually to check this subsystem: {command}",
        }
    try:
        proc = subprocess.run(["uv", "run", "--script", str(tool_path), *extra_args], capture_output=True, text=True, timeout=timeout)
        if proc.returncode == 0:
            return {"ok": True, "output": json.loads(proc.stdout)}
        return {"ok": False, "error": proc.stderr.strip() or proc.stdout.strip(), "command": command}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timed out after {timeout}s", "command": command}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "command": command}


def check_mongo(c):
    result = _run_uv_script("inspect_mongo.py", ["--list-collections"])
    if result.get("ok") is True:
        parsed = result.pop("output")
        result.update({"database": parsed.get("database"), "collections_count": len(parsed.get("collections", []))})
    return result


def check_kafka(c):
    result = _run_uv_script("trace_kafka.py", ["--list-topics"])
    if result.get("ok") is True:
        parsed = result.pop("output")
        result.update({"brokers": parsed.get("brokers"), "topics_count": parsed.get("count", 0)})
    return result


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
