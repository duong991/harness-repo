# Execution Plan: Harness-managed `system-log-tracer`

Date: 2026-10-20

## Status

Active

## Outcome

`system-log-tracer` is a Harness-managed, model-invoked supporting skill that
collects read-only runtime evidence for NestJS backends in a Turborepo + pnpm
monorepo and hands hypotheses to `diagnosing-bugs`. Read-only behavior, the
production gate, config/credential separation, and redaction are proven by
offline tests run from `scripts/test-harness-skills`.

## Context

- Confirmed brief: `grill-me` session of 2026-10-19/20 (decisions below).
- Origin: `safekid-microservice/safekid-backend/.agents/skills/system-log-tracer`
  (self-written, untracked there because `.agents/` is gitignored). The origin
  repository is read-only for this work.
- Reference only (ideas, no copied text; docs are CC BY 4.0):
  `sickn33/agentic-awesome-skills` at `c808e6e480696d243e0668ebbc3499bb8e7e10a4`
  — `debugging-and-error-recovery`, `debugging-toolkit-smart-debug`,
  `logic-locate`, `audit-agent-run-evidence`, `error-detective`,
  `bug-hunt-swarm`.
- Authority: `AGENTS.md`, `docs/WORKFLOW.md`, `docs/skills/skill-manifest.md`,
  `.agents/skills/work-router/SKILL.md`, `.agents/skills/diagnosing-bugs/SKILL.md`.

## Scope

In scope:

- Import the CLI tools and `SKILL.md` into `.agents/skills/system-log-tracer/`.
- Evidence-only role; root cause and fixes belong to `diagnosing-bugs`.
- Code-enforced read-only for every tool, default non-prod, prod gate
  (`--env prod` + per-session chat confirmation + `prod.env` present).
- Non-secret consumer config `.agents/config/system-log-tracer.json` (skill ships
  `config.example.json` + JSON schema); credentials in
  `~/.config/system-log-tracer/<env>.env` (mode 600) or environment variables;
  refuse when a `.env` exists in the skill directory or repository.
- Node tools resolve `kafkajs`/`mongodb` via `createRequire` from config field
  `nodeResolveFrom`.
- Remove `~/.Trash` recovery from `parse_export.py`; remove SafeKid hardcoding.
- 7-section chat evidence report; AAS additions 1–7 and 9 from the brief.
- Harness integration: `SOURCE.md` (with Influences), base snapshot, manifest
  hash, validator lists, `.claude/skills` link, skill-manifest row, router and
  `diagnosing-bugs` triggers, routing and boundary fixtures, offline tests.

Out of scope:

- MCP server, `qa-investigation`, `kibana-log-investigator`, other self-written
  skills, installing AAS skills, failing-vs-successful request diff (AAS #8),
  USE/TSA host analysis, any change in `safekid-backend`.

## Approach

1. Copy origin tree minus `.env`, `*.zip`, `__pycache__`, `mcp_server.py`,
   `references/mcp.md`; never read or print credential values.
2. Add shared config/env loader with schema validation, env gate, and `.env`
   placement refusal; route every tool through it.
3. Close read-only gaps (`inspect_mongo.js`, `raw_search.py`), remove Trash
   recovery and hardcoding, switch Node resolution to `nodeResolveFrom`.
4. Rewrite `SKILL.md` to the confirmed contract.
5. Add offline tests (fakes/stubs only) and wire them into
   `scripts/test-harness-skills`.
6. Register in Harness (validator, manifest, base, router, fixtures, manifest
   doc, links) and run both validation modes.

## Risks And Recovery

- Credential leakage while copying: copy with explicit excludes; verify no
  `.env`, zip, or secret-looking values in the new tree before snapshotting.
- Router regression: routing/boundary fixtures must keep passing.
- Recovery: all changes are uncommitted files in this repository; revert with
  `git restore`/`git clean` on the listed paths.

## Progress

- [x] Import and sanitize tool tree.
- [x] Config/env loader, prod gate, `.env` refusal.
- [x] Read-only gaps, Trash removal, de-hardcoding, Node resolution.
- [x] `SKILL.md` contract.
- [x] Offline tests.
- [x] Harness registration and validation.

## Decisions

- 2026-10-19: Harness-managed supporting skill in this repo only (brief Q6).
- 2026-10-19: Evidence-only; no root-cause conclusion (Q7).
- 2026-10-19: Non-prod default; prod requires flag, chat confirmation, and
  `prod.env` (Q9).
- 2026-10-19: No MCP this round (Q10); remove Trash recovery (Q11).
- 2026-10-19: Config in consumer repo, credentials outside repo (Q12).
- 2026-10-19: Node drivers via consumer workspace `nodeResolveFrom` (Q13).
- 2026-10-19: Model-invoked with router trigger (Q14); chat-only 7-section
  report (Q15); offline proof only (Q16).
- 2026-10-20: Adopt AAS ideas 1–7 and 9; defer 8 (Q17).
- 2026-10-20: `.env` refusal is scoped to the skill directory and
  `.agents/config/`; unrelated application `.env` files are ignored.
- 2026-10-20: Review hardening — ES/Kibana guard matches path segments instead
  of substrings and allows Kibana `GET /api/status`; Redis `KEYS` removed from
  the allow-list (blocking on large keyspaces; `SCAN` covers the need).
- 2026-10-20: No self-modification — `SKILL.md` forbids editing skill,
  `.agents/config/`, or `.harness-core/` files during an investigation
  (boundary-fixture checked); every Python and Node tool verifies all skill
  files against `.harness-core/manifest.json` on start and exits 5 on any
  modified, missing, or unmanaged file. No bypass flag. `parse_export.py` and
  `router.py` import `common` unconditionally so the check cannot be skipped.
- 2026-10-20: Removed the `--save-doc` / `docs/traces/` archive the import had
  kept; it contradicted the chat-only report decision (Q15).
- 2026-10-20: MongoDB typing — explicit Extended JSON `{"$oid"}`/`{"$date"}`
  anywhere in filters and pipelines; implicit coercion only for 24-hex strings
  under `_id` (incl. `$in`/`$nin`/`$eq`/`$ne`, nested, `$match`); other fields
  are never guessed and a zero-result query prints a `$oid` hint. Output keeps
  types (`{"$oid"}`, `{"$date"}`) instead of the previous byte-array `_id` and
  empty `{}` dates. Phone redaction no longer matches inside ObjectIds or UUID
  segments (Python and Node). `SKILL.md` states that type mismatches are
  evidence and forbids changing tools, application code, schemas, or data to
  make a query match.

## Validation

- Focused proof: offline tool tests (allowed and blocked operations, env gate,
  config schema, `.env` refusal, redaction, empty export, Node resolution).
- Integration or end-to-end proof: deferred — non-prod smoke in the consumer
  after sync (owner: user).
- Repository-required checks: `scripts/test-harness-skills` and
  `scripts/test-harness-skills --release-baseline`.

## Result

2026-10-20: Implemented and validated offline; plan stays active until the
consumer smoke test.

- `scripts/test-harness-skills` and `--release-baseline`: both exit 0;
  57 offline `system-log-tracer` tests pass (including tamper tests on a
  copied install and ObjectId/Date handling with a stand-in ObjectId class).
- Not proven: behavior against real Elasticsearch/Kibana/Redis/MongoDB/Kafka,
  real `kafkajs`/`mongodb` driver resolution in a pnpm consumer, and MongoDB
  `find` field projection defaults (only limits are enforced).
- Not proven: ObjectId handling against the real `bson` ObjectId class (tests
  use a stand-in exposing `_bsontype` and `toHexString`, which real `bson`
  provides); phone numbers glued to a word by `-` (e.g. `tel-0912345678`) are
  no longer masked by the free-text pattern — key-based redaction of `phone`
  fields still applies.
- Residual risk: the integrity check is tamper-evident, not tamper-proof — an
  agent that rewrites both a tool and the manifest/base, or strips the check
  itself, is only caught by Git diff review and `--release-baseline`.
- Follow-up: sync to `safekid-backend` with `scripts/sync-harness-source.py`,
  create its `.agents/config/system-log-tracer.json` and
  `~/.config/system-log-tracer/<env>.env`, run a non-prod smoke, then move this
  plan to `docs/plans/completed/`.
