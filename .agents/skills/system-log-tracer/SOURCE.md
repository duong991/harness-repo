# Source

- Origin: self-written skill in `safekid-microservice/safekid-backend/.agents/skills/system-log-tracer`
  (untracked there because `.agents/` is gitignored in that repository; the
  origin repository is treated as read-only for this import).
- License: internal, no upstream license.
- Imported: 2026-10-20
- Owner: gnoud
- Activation: Model-invoked; `allow_implicit_invocation: true`.
- Role: read-only runtime evidence collection for NestJS services in a
  Turborepo/pnpm monorepo across Elasticsearch/Kibana, Redis, MongoDB, and
  Kafka; hands hypotheses to `diagnosing-bugs` and never concludes root
  cause.

## Local modifications

- Replaced the origin's single `.env` file and hardcoded SafeKid connection
  defaults with a split config/credential model: non-secret
  `<repo-root>/.agents/config/system-log-tracer.json` (validated against
  `config.schema.json` by a stdlib-only validator) plus
  `~/.config/system-log-tracer/<env>.env` credentials outside the repository.
- Added an environment selector and production gate: `--env` defaults to the
  first non-production environment; a production environment additionally
  requires `--confirm-prod` and a matching credential file, and the skill
  asks the user for explicit chat confirmation before ever using the flag.
- Added a refusal check: the skill will not run if a `.env` file exists in
  its own directory or under `<repo-root>/.agents/config/`.
- Closed read-only gaps the origin left as prose-only conventions: Mongo now
  code-enforces an allow-list of `find`/`countDocuments`/`distinct`/`aggregate`
  and recursively rejects `$out`/`$merge` in aggregation pipelines
  (`tools/mongo_guard.js`); Elasticsearch/Kibana calls are validated against
  an allow-list of read endpoints before the HTTP request is sent
  (`tools/common.py`); Kafka's ephemeral consumer now enforces `autoCommit:
  false` through a guard function (`tools/kafka_guard.js`) instead of only a
  code comment.
- Removed the origin's `~/.Trash` "smart recovery" from `parse_export.py`
  entirely; an empty/near-empty export now always fails with a message to
  widen the Kibana time window and re-export.
- Removed every SafeKid-specific hardcoded string (service names, Kong
  references, index/topic names, default Mongo URIs/DB names) from the
  tools; equivalent values now live only as illustrative examples in
  `config.example.json`.
- Switched Node driver resolution from a bundled `node_modules/.pnpm`
  heuristic to `module.createRequire` against a configurable
  `nodeResolveFrom` workspace, with a clear error when the workspace does not
  depend on the driver. Split the pure guard/validation logic
  (`tools/mongo_guard.js`, `tools/kafka_guard.js`) into driver-independent
  modules so it is testable without `kafkajs`/`mongodb` installed.
- Extended redaction to also mask emails, phone numbers, and precise
  coordinate pairs, plus any field name listed in config `redactionFields`.
- Rewrote `SKILL.md` around a fixed 7-section evidence report, an explicit
  untrusted-data rule for logs/stack traces/Kafka payloads, and an explicit
  hand-off to `diagnosing-bugs` instead of a 4-section root-cause report.
- Removed the MCP server integration (`tools/mcp_server.py`,
  `references/mcp.md`) from this import; out of scope for this round.

## Influences

Ideas only — no text copied; the referenced repository's documentation is
licensed CC BY 4.0, attributed here.

- Upstream repository: https://github.com/sickn33/agentic-awesome-skills
- Commit: `c808e6e480696d243e0668ebbc3499bb8e7e10a4`
- Skills consulted for ideas (not text): `debugging-and-error-recovery`,
  `debugging-toolkit-smart-debug`, `logic-locate`,
  `audit-agent-run-evidence`, `error-detective`, `bug-hunt-swarm`.
- What was adopted (restated in this skill's own words, not copied): a fixed
  intake packet before tooling; separating a causal timeline from raw
  timestamps; code-mapping from the failure cone outward instead of
  browsing broadly; qualitative (not invented-probability) confidence levels
  on hypotheses with explicit falsification conditions; treating missing
  telemetry as "not proven" rather than "no defect"; stating a re-run
  command set with no secrets as the final report section.
- Deliberately deferred: failing-vs-successful request diffing (that
  repository's idea #8) is out of scope for this round per the approved
  plan.

## Update method

This is an internal, self-written skill with no upstream release to track.
Future updates come from direct edits in this repository (or a fresh import
from the origin skill if it changes materially); update the
`.harness-core/base/` snapshot and manifest hash atomically with any change,
and re-run `scripts/test-harness-skills`.
