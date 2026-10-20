# system-log-tracer tool reference

All tools live in `tools/` and accept the shared flags `--env <name>`,
`--root <path>`, and `--confirm-prod` (see `SKILL.md`'s "Environment
selection and the production gate"). Python tools require `python3` only
(stdlib); Node tools require `node` and resolve `kafkajs`/`mongodb` from the
workspace named by config `nodeResolveFrom`.

## `tools/common.py` / `tools/config.js`

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

## `tools/inspect_mongo.js`

```
node tools/inspect_mongo.js --list-dbs
node tools/inspect_mongo.js --db <db> --list-collections
node tools/inspect_mongo.js --db <db> --collection <c> --filter '<json>' [--limit N] [--count]
node tools/inspect_mongo.js --db <db> --collection <c> --distinct <field> [--filter '<json>']
node tools/inspect_mongo.js --db <db> --collection <c> --pipeline '<json array>'
node tools/inspect_mongo.js --db <db> --collection <c> --filter '{"userId": {"$oid": "<24 hex>"}}'
```

Only `find`/`countDocuments`/`distinct`/`aggregate` ever reach the driver
(enforced by `tools/mongo_guard.js`). Aggregate pipelines are scanned
recursively for `$out`/`$merge` (including nested `$facet`/`$unionWith`
sub-pipelines) and rejected if found. Default `--db` is the first entry in
the selected environment's `mongo.dbs`.

## `tools/trace_kafka.js`

```
node tools/trace_kafka.js --list-topics
node tools/trace_kafka.js --topic <name> --offsets
node tools/trace_kafka.js --topic <name> [--limit N] [--from-beginning]
```

Ephemeral, per-run consumer group; `autoCommit: false` is enforced by
`tools/kafka_guard.js`'s `buildReadOnlyRunConfig()`. No code path calls
`commitOffsets` or `produce`/`send`.

## `tools/mongo_guard.js` / `tools/kafka_guard.js` / `tools/redact.js`

Pure guard/redaction logic, importable without `mongodb`/`kafkajs` so tests
exercise the read-only contract offline. Not invoked directly.

## `tools/healthcheck.py`

`python3 tools/healthcheck.py` — reachability summary across Elasticsearch,
Kibana, Redis, MongoDB, and Kafka for the selected environment, without
exposing credentials. Exit code `1` only if every subsystem failed.
