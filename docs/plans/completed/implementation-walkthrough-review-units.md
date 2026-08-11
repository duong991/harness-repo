# Execution Plan: Implementation Walkthrough Review Units

Date: 2026-08-11

## Status

Completed

## Outcome

Upgrade the existing `implementation-walkthrough` skill into a five-phase,
read-only system for organizing large changes into behavior-based Review Units,
tracing a Critical Path, probing risks and invariants, and handing off to
`test-walkthrough` and `code-review` without creating a new review-planning
skill or making findings itself.

## Context

- User-provided decision: `Chốt cuối: không tạo thêm skill mới kiểu
  review-planner / review-decomposition`.
- Workflow authority: `AGENTS.md` and `docs/WORKFLOW.md`.
- Existing staged baseline: the prior `test-walkthrough` SDLC update is staged;
  this plan must preserve it and add only the new walkthrough evolution.
- Existing skill boundaries: `.agents/skills/implementation-walkthrough/`,
  `.agents/skills/test-walkthrough/`, `.agents/skills/code-review/`,
  `.agents/skills/work-router/`, and
  `.agents/skills/verification-before-completion/`.
- No `.codegraph/` directory is present; use targeted inspection.

## Scope

In scope:

- Rewrite `implementation-walkthrough/SKILL.md` around BASELINE, MAP, TRACE,
  PROBE, and HANDOFF.
- Add the authorization domain reference needed to exercise conditional
  reference loading.
- Update `test-walkthrough` evidence terminology and remove its overall
  confidence/adequacy conclusion.
- Update router, formal review handoff, source metadata, root/workflow guide,
  and skill manifest to describe the final four-skill mental model.
- Add scenario-oriented contract checks for small/large changes, authz,
  generated files, commit decomposition, stale evidence, risk probes, large
  test surfaces, and target resynchronization.

Out of scope:

- Creating `review-planner`, `review-decomposition`, `security-review`, or
  `large-change-review` skills.
- Any git reset, checkout, staging, commit, or branch mutation.
- Changing product behavior, Harness CLI/SQLite compatibility, or
  `docs/TEST_MATRIX.md`.
- Adding domain references not required by the current acceptance scenarios.

## Approach

1. Preserve the staged/unstaged baseline and create this plan.
2. Rewrite the implementation walkthrough as a concise five-phase workflow
   with canonical Review Unit, Critical Path, Risk Probe, and Invariant
   contracts.
3. Add the conditional authorization reference and update the test/review
   handoffs.
4. Synchronize routing and explanatory SDLC documentation without adding a
   primary work type or new skill.
5. Run structural, content, scenario, and diff checks; perform authority-first
   review; resolve findings; and move this plan to `completed/`.

## Risks And Recovery

- Risk: Review Units become folder buckets or implementation findings.
  Mitigation: require one independently reviewable behavior/contract per unit
  and explicit handoff to `code-review`.
- Risk: stale staged/unstaged scope invalidates the map. Mitigation: BASELINE
  records target and evidence, and HANDOFF requires resync when scope changes.
- Risk: old test terminology becomes an adequacy judgment. Mitigation: use
  Direct/Partial/Superficial evidence and keep formal review in `code-review`.
- Recovery: preserve the existing staged baseline; if this change must be
  abandoned, revert only the new unstaged hunks/files after inspecting
  `git diff`, without resetting or checking out the worktree.

## Progress

- [x] Read authority, decision attachment, affected skills, and staged baseline.
- [x] Rewrite `implementation-walkthrough` into five phases.
- [x] Add the authorization reference and update evidence/review handoffs.
- [x] Synchronize routing and SDLC documentation.
- [x] Run scenario/content validation and review the complete change.
- [x] Record result and move this plan to `docs/plans/completed/`.

## Decisions

- 2026-08-11: Extend `implementation-walkthrough`; do not create a parallel
  review-planning or decomposition skill.
- 2026-08-11: Use exactly five phases and four primitives: Review Unit,
  Critical Path, Risk Probe, and Invariant.
- 2026-08-11: Add only `references/authorization.md`; load it conditionally
  when an authorization/trust-boundary risk is materially present.

## Validation

- Focused proof: `skill-creator/scripts/quick_validate.py` passed for both
  walkthrough skill folders; both `agents/openai.yaml` files parsed as YAML.
- Integration proof: fresh scenario assertions passed for the five phases,
  four primitives, canonical Review Unit, separate reading-priority/risk
  labels, conditional authorization reference, Direct/Partial/Superficial
  evidence, routing, handoff, generated/commit/stale-evidence boundaries,
  `docs/TEST_MATRIX.md` scope, and forbidden parallel-skill absence.
- Repository-required checks: authority and boundary review, `git diff --check`
  passed, and the original staged baseline remained unchanged in the index.
- Independent subagent verification was attempted but unavailable because the
  selected model was at capacity; direct current-session validation is the
  completion evidence.

## Result

Completed on 2026-08-11. The existing implementation walkthrough now owns the
five-phase Review Unit workflow, the only new reference is conditional
authorization guidance, and test comprehension/formal review remain separate.
No parallel review-planning skill was created and no git mutation was performed.
