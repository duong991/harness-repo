# Execution Plan: Claude–Gemini Delegation V1

Date: 2026-09-05

## Status

Completed (V1 implementation; roadmap benchmark gaps recorded below)

## Outcome

Create a runnable, self-contained implementation in `newfolder/` of the user's
pasted Claude–Gemini Delegation Harness V1: compact TASK/RESULT packets, OMP
SCOUT/WORK, fresh OpenCode CRITIC, isolated execution and Git-verified changes.

## Context

Authority: the current user request and its attached design, especially sections
10–12, 18–24, 36–42. Repository workflow: `docs/WORKFLOW.md`. Existing unrelated
Harness maintenance and teach-skill edits are outside this change.

## Scope

V1 gateway, schemas, Claude skill, examples, local dependencies, automated
integration tests and live smoke checks where authentication is available.
Persistent OMP sessions and ULTRA/OMO are deferred per the design's V1 conclusion.
Provide benchmark recording and comparison; never manufacture Claude-only
baselines or claim measured token/quality gains without actual paired runs.

## Approach

1. Verify installed CLI contracts and install required local dependencies.
2. Build and test packet/result validation and the compact output boundary.
3. Add isolated Git workspaces, independent change verification, provider
   adapters, timeout handling and enforceable read-only worker permissions.
4. Add progressive-disclosure Claude guidance, examples and measurement tools.
5. Review against the accepted V1 design and run fresh automated/live proof.

## Risks And Recovery

- Never merge/apply worker edits automatically. Preserve patches and workspaces
  for lead acceptance. Source checkout and existing user changes remain intact.
- Keep runtime logs/authentication out of version control. Never print secrets.
- Child CLI drift requires tests and doctor diagnostics, not silent fallback.
- Recovery: remove only newly created `newfolder/` artifacts and this plan if
  abandoning; provider installation is separately removable. Failed worker runs
  remain inspectable and cannot be reported as accepted work.

## Progress

- [x] Read accepted design, repository workflow and current CLI availability.
- [x] Install dependencies and verify provider interfaces.
- [x] Implement and test the gateway and isolation.
- [x] Write Claude guidance, examples and benchmark tooling.
- [x] Review and validate final implementation; record limitations.

## Decisions

- 2026-09-05: Use literal `newfolder/` as the requested new directory.
- 2026-09-05: Target V1 as explicitly recommended by the supplied design. Keep
  DIRECT lead-owned and fail clearly on deferred ULTRA rather than rerouting it.
- 2026-09-05: Prefer standard-library process/Git orchestration and published
  JSON Schema validation over building another agent orchestrator.
- 2026-09-06: macOS native sandbox denies worker writes outside per-run runtime
  and (for WORK) its private worktree. No unsandboxed fallback. Snapshot the
  current dirty checkout into a separate Git repo to avoid shared source metadata.
- 2026-09-06: Pin local OMP 18.1.11 + Bun 1.4.2. Live responses showed retired
  Gemini 2.5 and zero Pro quota; use tested Flash selectors in runtime config.
  Allow one bounded transient retry without changing model/account.
- 2026-09-06: Live benchmark probes are validation gaps, not manufactured proof.
  The implementation can ship without asserting the full-roadmap token goals.

## Validation

- Focused proof: packet rejection, compact output, evidence checks.
- Integration proof: real temporary Git repos + fake executable workers for
  modifications, scope escapes, ignored/untracked files, failures and timeouts.
- Live proof: provider catalog/doctor and bounded SCOUT/WORK/CRITIC smoke runs.
- Repository proof: relevant Harness validator and diff whitespace check.

## Result

Implemented `newfolder/`: schemas, compact gateway, OS-enforced write boundary,
isolated Git snapshots/worktrees, OMP SCOUT/WORK, fresh OpenCode CRITIC, declared
check execution, evidence/scope verification, telemetry, benchmark recorder,
Claude skill/reference docs, reproducible setup and demo commands.

Fresh final proof on 2026-09-06: 41 tests pass (8.30 seconds, exit 0), Ruff passes,
all three example packets validate, doctor detects both runtimes/credential,
parent Harness validator passes, and diff whitespace check passes. Four real
Gemini runs prove SCOUT, WORK, CRITIC rejection on original source and CRITIC
confirmation on the candidate. Their artifacts were revalidated with current
contracts. See `newfolder/docs/validation.md` for exact runs and review evidence.

Limitations: actual paired token benchmark and natural auto-routing accuracy
remain unmeasured; Claude classification probes hit login/timeout failures.
Account quota can block new Gemini runs. Persistent OMP and ULTRA/OMO are
intentionally deferred as requested by the supplied design's V1 conclusion.
No edits to pre-existing unrelated Harness maintenance/teach-skill work.
