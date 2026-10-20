#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["confluent-kafka==2.6.1"]
# ///
"""
trace_kafka.py - Strict read-only Kafka topic/offset/message inspector.

Run with `uv run --script tools/trace_kafka.py ...` so the pinned
`confluent-kafka` dependency resolves automatically.

Strictly read-only: the consumer configuration is built through
tools/kafka_guard.py, which refuses to run unless both
`enable.auto.commit` and `enable.auto.offset.store` are False. The consumer
uses an ephemeral, per-run group id and `assign()` with explicit offsets
computed from `get_watermark_offsets()` instead of `subscribe()`, so no
durable consumer-group state is created. This tool never commits or stores
offsets, and never creates a Producer or a write-capable AdminClient call;
see `kafka_guard.assert_source_has_no_write_calls()` for the mechanical
proof.
"""
from __future__ import annotations

import argparse
import json
import sys

from common import add_common_args, cfg, redact_sensitive
from kafka_guard import build_read_only_consumer_config, ephemeral_group_id

POLL_TIMEOUT_SECONDS = 1.0
TOTAL_RUN_TIMEOUT_SECONDS = 5.0


def _decode(raw):
    if raw is None:
        return None
    return raw.decode("utf-8", errors="replace") if isinstance(raw, (bytes, bytearray)) else raw


def message_evidence(msg, redaction_fields):
    """Turn a confluent_kafka Message into redacted evidence. Value, key, and
    headers are all redacted: headers commonly carry authorization or tokens."""
    text_value = _decode(msg.value())
    try:
        value = json.loads(text_value) if text_value is not None else None
    except (json.JSONDecodeError, TypeError):
        value = text_value
    headers = {k: _decode(v) for k, v in (msg.headers() or [])}
    ts = msg.timestamp()[1] if msg.timestamp() else None
    ts_iso = None
    if ts is not None and ts >= 0:
        from datetime import datetime, timezone
        ts_iso = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return {
        "partition": msg.partition(),
        "offset": msg.offset(),
        "timestamp": ts,
        "timestampIso": ts_iso,
        "key": redact_sensitive(_decode(msg.key()), redaction_fields),
        "value": redact_sensitive(value, redaction_fields),
        "headers": redact_sensitive(headers, redaction_fields),
    }


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Strict read-only Kafka topic/offset/message inspector")
    add_common_args(parser)
    parser.add_argument("--brokers", help="Comma-separated Kafka brokers (default: environment config/credentials)")
    parser.add_argument("--client-id", help="Explicit client ID (default: kafkaClientId from credentials/config)")
    parser.add_argument("--topic", "-t", default="", help="Topic to inspect")
    parser.add_argument("--limit", type=int, default=10, help="Maximum messages to peek (default: 10, max: 50)")
    parser.add_argument("--list-topics", action="store_true", help="List all topics on cluster")
    parser.add_argument("--offsets", action="store_true", help="Fetch partitions and latest offsets for topic")
    parser.add_argument("--from-beginning", action="store_true", help="Read messages from the beginning instead of latest")
    return parser


def main(argv=None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    limit = max(1, min(50, args.limit))

    c = cfg(env=args.env, root=args.root, confirm_prod=args.confirm_prod)

    try:
        from confluent_kafka import Consumer, TopicPartition
    except ImportError:
        print(
            "ERROR: confluent-kafka is not installed in this Python environment. Run it as "
            "`uv run --script tools/trace_kafka.py ...` so the pinned dependency "
            "(confluent-kafka==2.6.1) resolves automatically.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    brokers_str = args.brokers or c["kafka_brokers"]
    client_id = args.client_id or c["kafka_client_id"]
    brokers = [b.strip() for b in brokers_str.split(",") if b.strip()]

    probe_group_id = ephemeral_group_id(client_id)
    consumer_config = build_read_only_consumer_config({
        "bootstrap.servers": ",".join(brokers),
        "client.id": client_id,
        "group.id": probe_group_id,
        "enable.auto.commit": False,
        "enable.auto.offset.store": False,
        "session.timeout.ms": 10000,
        "socket.timeout.ms": 10000,
    })

    consumer = Consumer(consumer_config)
    try:
        if args.list_topics:
            metadata = consumer.list_topics(timeout=10.0)
            topics = sorted(metadata.topics.keys())
            print(json.dumps({"brokers": brokers, "clientId": client_id, "count": len(topics), "topics": topics}, indent=2))
            return

        if not args.topic:
            print("ERROR: --topic <name> is required (or use --list-topics)", file=sys.stderr)
            raise SystemExit(1)

        metadata = consumer.list_topics(topic=args.topic, timeout=10.0)
        topic_metadata = metadata.topics.get(args.topic)
        if topic_metadata is None or topic_metadata.error is not None:
            print(f"ERROR: topic '{args.topic}' not found", file=sys.stderr)
            raise SystemExit(2)
        partition_ids = sorted(topic_metadata.partitions.keys())

        if args.offsets:
            partitions = {}
            for pid in partition_ids:
                low, high = consumer.get_watermark_offsets(TopicPartition(args.topic, pid), timeout=10.0, cached=False)
                partitions[str(pid)] = {"low": low, "high": high}
            print(json.dumps({"brokers": brokers, "clientId": client_id, "topic": args.topic, "partitions": partitions}, indent=2))
            return

        # Explicit offsets via assign(), never subscribe(): no consumer-group
        # membership/rebalance state and no auto-commit/offset-store path.
        assignments = []
        for pid in partition_ids:
            low, high = consumer.get_watermark_offsets(TopicPartition(args.topic, pid), timeout=10.0, cached=False)
            if args.from_beginning:
                start = low
            else:
                start = max(low, high - limit)
            assignments.append(TopicPartition(args.topic, pid, start))
        consumer.assign(assignments)

        messages = []
        deadline = TOTAL_RUN_TIMEOUT_SECONDS
        import time as _time
        started = _time.monotonic()
        while len(messages) < limit and (_time.monotonic() - started) < deadline:
            msg = consumer.poll(POLL_TIMEOUT_SECONDS)
            if msg is None:
                continue
            if msg.error():
                continue
            messages.append(message_evidence(msg, c["redaction_fields"]))

        # Partitions interleave arbitrarily; order the evidence by broker time.
        messages.sort(key=lambda m: (m["timestamp"] is None, m["timestamp"] or 0, m["partition"], m["offset"]))

        print(json.dumps({
            "topic": args.topic,
            "clientId": client_id,
            "probeGroupId": probe_group_id,
            "messagesReturned": len(messages),
            "messages": messages,
        }, indent=2, default=str))
    except SystemExit:
        raise
    except Exception as exc:
        print(f"ERROR connecting to Kafka brokers ({brokers_str}) with clientId '{client_id}': {exc}", file=sys.stderr)
        raise SystemExit(2)
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
