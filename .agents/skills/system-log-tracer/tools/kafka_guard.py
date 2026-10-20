#!/usr/bin/env python3
"""
kafka_guard.py - Pure, stdlib-only read-only guard for Kafka consumer
configuration. Importable WITHOUT the `confluent_kafka` driver.
trace_kafka.py must build its consumer configuration through
`build_read_only_consumer_config()` so the ephemeral group never auto-commits
and the tool never calls commit/store_offsets or creates a Producer/AdminClient
write path.
"""
from __future__ import annotations

import re
import time


class KafkaWriteRejected(Exception):
    """Raised when a Kafka consumer configuration is not explicitly read-only."""


def build_read_only_consumer_config(consumer_config):
    """Validate (and return, unmodified) a confluent_kafka Consumer config
    dict, refusing anything that is not explicitly read-only: both
    `enable.auto.commit` and `enable.auto.offset.store` must be False.
    """
    consumer_config = dict(consumer_config or {})
    if consumer_config.get("enable.auto.commit") is not False:
        raise KafkaWriteRejected(
            "Kafka consumer config must set 'enable.auto.commit': False explicitly; "
            "this read-only skill never commits offsets."
        )
    if consumer_config.get("enable.auto.offset.store") is not False:
        raise KafkaWriteRejected(
            "Kafka consumer config must set 'enable.auto.offset.store': False explicitly; "
            "this read-only skill never stores offsets."
        )
    return consumer_config


def ephemeral_group_id(client_id):
    """Ephemeral, per-run consumer group id so no durable group state is
    created. Uses epoch milliseconds, like the former Node tool's
    Date.now()."""
    return f"{client_id}-trace-probe-{int(time.time() * 1000)}"


# Patterns that must never appear as a call in this tool's source: proof (by
# string scan, not a live connection) that no write path exists.
FORBIDDEN_CALL_PATTERNS = (
    re.compile(r"\.commit\s*\("),
    re.compile(r"\.store_offsets\s*\("),
    re.compile(r"Producer\s*\("),
    re.compile(r"\.produce\s*\("),
    re.compile(r"\.create_topics\s*\("),
    re.compile(r"\.delete_topics\s*\("),
)


def assert_source_has_no_write_calls(source_text):
    for pattern in FORBIDDEN_CALL_PATTERNS:
        if pattern.search(source_text):
            raise KafkaWriteRejected(f"Forbidden write-capable call pattern found: {pattern.pattern}")
    return True
