# Installed flow rerun — 2026-11-15

Fresh executor: gpt-6-luna. Read installed AGENTS.md, docs/WORKFLOW.md,
work-router, blast-radius-review and grill-me. No prior eval or patch supplied.
Parent summary of the observed agent response (not a full tool transcript).

| Request | Observed behavior |
| --- | --- |
| Explain function | read-only-analysis; no blast/setup/write/plan |
| Core/Leaf with accepted policy | read-only-analysis + blast; check policy/scope and classify; no interview for Ready |
| Correctness only, missing policy, no setup authority | code-review continues; missing policy limits dependent claims; offer but do not start grill |
| Authorized setup | one-question interview; confirmed brief returns to router; authorized save is bounded-change |
| Core one-line auth fix | tiny-fix preserved; policy evidence required, no automatic durable plan |
| Leaf diff gains migration | reassess all paths and evidence; do not infer new work type or unaccepted tier |
| Policy summary only | read-only-analysis; no blast or setup |

All seven responses preserved intended boundaries. Case 4 described phases rather
than assigning a primary type to the initial interview; no implementation before
confirmation was authorized. Agent reported no direct contradiction in loaded
instructions. These are hypothetical routing probes over installed text, not live
consumer setup, actual code review or evidence of universal routing reliability.

Fresh checks: reverse patch check, quick_validate, Harness SDLC and source-sync
integration passed. Three grading-infrastructure tests passed. Full native suite
failed one of 70 system-log-tracer tests due to PermissionError writing its .env
fixture under protected .agents; no validation weakened or skipped.
