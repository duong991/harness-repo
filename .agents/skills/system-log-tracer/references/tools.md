# system-log-tracer tool reference

All tools live in `tools/` and accept the shared flags `--env <name>`,
`--root <path>`, and `--confirm-prod` (see `SKILL.md`'s "Environment
selection and the production gate"). Every tool is Python. Most require only
`python3` (stdlib, no `pip install`); `tools/inspect_mongo.py` and
`tools/trace_kafka.py` pin their driver (`pymongo`, `confluent-kafka`) in a
PEP 723 inline script header and run via `uv run --script` instead.

## `tools/common.py`

Shared config loader, schema validator, credential loader, env/prod gate, and
redaction used by every other tool. Not invoked directly.

## `tools/router.py`

`python3 tools/router.py "<symptom text>"` — maps free-text symptom
description to the recommended tool and an example command. Blocks and
explains when the text looks like a mutation request (contains "fix",
"migrate", "delete", etc.).

## `tools/parse_export.py`

`python3 tools/parse_export.py --path <export.csv|json> [--request-id <id>] [--json]`

Parses a Kibana Discover CSV/JSON export offline (no credentials needed). An
empty or <=1 byte file fails with a message to widen the Kibana time window
and re-export; there is no automatic recovery of any kind. Stack-trace frames
are mapped to repository paths using config `stackTracePathRewrites` when a
config is available, else a generic `/app/<service>/(dist/)?...` convention.

## `tools/trace_request.py`

`python3 tools/trace_request.py --request-id <id> [--field requestId] [--size N] [--json]`

Live Elasticsearch search by request/trace ID field, ascending by the
configured `timeField`.

## `tools/search_logs.py`

`python3 tools/search_logs.py [--url <path>]... [--body-contains <text>]... [--request-id <id>] [--from <iso>] [--to <iso>] [--size N] [--raw]`

Filtered Query DSL search over the configured index pattern.

## `tools/find_around.py`

`python3 tools/find_around.py --timestamp <iso> [--minutes N] [--body-contains <text>]... [--url <path>]...`

Delegates to `search_logs.py` with a `[-minutes, +minutes]` window around the
given timestamp.

## `tools/get_mapping.py`

`python3 tools/get_mapping.py [--field <name>]...` — index field mapping
inspector; with no `--field`, dumps the full mapping.

## `tools/raw_search.py`

`python3 tools/raw_search.py --file <query.json>` — executes an arbitrary
read-only Query DSL body from a file against `_search` only; the file cannot
select a different (write) endpoint.

## `tools/esql.py`

`python3 tools/esql.py --query "FROM <index> | ..."` — read-only ES|QL;
rejects anything not starting with `FROM`/`ROW`/`SHOW`/`META`.

## `tools/inspect_redis.py`

`python3 tools/inspect_redis.py --cmd <GET|HGETALL|TTL|TYPE|SCAN|INFO|PING|...> [--key <k>] [--field <f>] [--pattern <glob>] [--count N]`

Pure-stdlib RESP client. Allow-listed read commands only (see
`ALLOWED_READ_COMMANDS` in the module); anything else raises
`PermissionError` before any socket write.

## `tools/inspect_mongo.py`

```
uv run --script tools/inspect_mongo.py --list-dbs
uv run --script tools/inspect_mongo.py --db <db> --list-collections
uv run --script tools/inspect_mongo.py --db <db> --collection <c> --filter '<json>' [--limit N] [--count]
uv run --script tools/inspect_mongo.py --db <db> --collection <c> --distinct <field> [--filter '<json>']
uv run --script tools/inspect_mongo.py --db <db> --collection <c> --pipeline '<json array>'
uv run --script tools/inspect_mongo.py --db <db> --collection <c> --filter '{"userId": {"$oid": "<24 hex>"}}'
```

Pinned dependency: `pymongo==4.10.1` (PEP 723 header; `uv` resolves it).
Only `find`/`countDocuments`/`distinct`/`aggregate` ever reach the driver
(enforced by `tools/mongo_guard.py`). Aggregate pipelines are scanned
recursively for `$out`/`$merge` (including nested `$facet`/`$unionWith`
sub-pipelines) and rejected if found. Default `--db` is the first entry in
the selected environment's `mongo.dbs`. If `pymongo` is not resolvable (e.g.
run with plain `python3` instead of `uv run --script`), the tool exits 2
with a message pointing at the correct `uv run --script` invocation.

## `tools/trace_kafka.py`

```
uv run --script tools/trace_kafka.py --list-topics
uv run --script tools/trace_kafka.py --topic <name> --offsets
uv run --script tools/trace_kafka.py --topic <name> [--limit N] [--from-beginning]
```

Pinned dependency: `confluent-kafka==2.6.1` (PEP 723 header; `uv` resolves
it). Ephemeral, per-run consumer group; `enable.auto.commit: False` and
`enable.auto.offset.store: False` are enforced by
`tools/kafka_guard.py`'s `build_read_only_consumer_config()`. The consumer
uses `assign()` with explicit offsets from `get_watermark_offsets()` instead
of `subscribe()`, and no code path calls `.commit(`, `.store_offsets(`, or
creates a `Producer`. Same `pymongo`-style exit-2 message if
`confluent-kafka` is not resolvable.

## `tools/mongo_guard.py` / `tools/kafka_guard.py`

Pure guard/evidence logic, importable without `pymongo`/`confluent-kafka` so
tests exercise the read-only contract and MongoDB Extended JSON
(`{"$oid"}`/`{"$date"}`) handling offline. Not invoked directly. Redaction
lives in `tools/common.py`'s `redact_sensitive()`, shared by every tool.

## `tools/healthcheck.py`

`python3 tools/healthcheck.py` — reachability summary across Elasticsearch,
Kibana, Redis, MongoDB, and Kafka for the selected environment, without
exposing credentials. Exit code `1` only if every subsystem failed.
MongoDB/Kafka checks shell out to `uv run --script tools/inspect_mongo.py
--list-collections` / `uv run --script tools/trace_kafka.py --list-topics`
with a short timeout; `healthcheck.py` itself never imports `pymongo` or
`confluent-kafka`. If `uv` is not on PATH, those two checks report
`"ok": null` with the exact command to run manually instead of failing.
