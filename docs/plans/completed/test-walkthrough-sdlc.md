# Execution Plan: Test Walkthrough SDLC Update

Date: 2026-08-06

## Status

Completed

## Outcome

Add a repository-local `test-walkthrough` skill and integrate it into the
default SDLC so users can understand what consequential test files exercise,
which production symbols they call, what behavior is protected, and what
remains unproven—without turning comprehension into a formal review or
approval gate.

## Context

- User-provided plan: `Plan cập nhật SDLC: Test Walkthrough`.
- Workflow authority: `AGENTS.md` and `docs/WORKFLOW.md`.
- Existing skill boundaries: `.agents/skills/work-router/`,
  `.agents/skills/code-review/`,
  `.agents/skills/implementation-walkthrough/`, and
  `.agents/skills/verification-before-completion/`.
- Documentation surfaces: `docs/HARNESS_WORKFLOW_GUIDE.md` and
  `docs/skills/skill-manifest.md`.
- `docs/TEST_MATRIX.md` and Harness/SQLite compatibility surfaces are out of
  scope.

## Scope

In scope:

- Create `.agents/skills/test-walkthrough/{SKILL.md,SOURCE.md,agents/openai.yaml}`.
- Add read-only test-comprehension routing while keeping `code-review` as the
  only formal review entry point.
- Add the compact handoffs in `code-review` and
  `implementation-walkthrough`.
- Update `AGENTS.md`, `docs/WORKFLOW.md`,
  `docs/HARNESS_WORKFLOW_GUIDE.md`, and `docs/skills/skill-manifest.md`.
- Validate skill metadata, routing boundaries, output format, and the stated
  acceptance scenarios.

Out of scope:

- Changing `docs/TEST_MATRIX.md`.
- Changing Harness CLI, SQLite schema, TDD workflow, verification gate, or
  product authority hierarchy.
- Editing or replacing unrelated existing worktree changes.
- Creating default Mermaid diagrams, test matrices, formal findings, or new
  repository documentation beyond the named surfaces.

## Approach

1. Record the clean baseline and inspect existing skill/documentation contracts.
2. Initialize and write the new skill with a concise, behavior-first workflow
   and exact per-file/final output contract.
3. Update routing and the two skill handoffs.
4. Update the root workflow guidance and manifest.
5. Run structural validators and scenario-oriented content checks.
6. Perform a read-only authority-first review of the diff, resolve issues, run
   fresh verification, and move this plan to `docs/plans/completed/`.

## Risks And Recovery

- Risk: routing the new skill as an approval or adequacy gate. Mitigation:
  preserve the explicit `code-review` boundary in every integration point.
- Risk: output inferred only from test names or mocks. Mitigation: require
  source inspection plus arrange/action/assertion/dependency evidence.
- Risk: overwriting existing changes. Mitigation: baseline is clean; recheck
  `git status` and inspect diffs before every broad edit.
- Recovery: revert only the files introduced or changed by this plan after
  confirming their paths with `git diff`; do not reset or checkout the worktree.

## Progress

- [x] Inspect authority, plan, target files, and current worktree baseline.
- [x] Create and validate `test-walkthrough`.
- [x] Update routing and skill handoffs.
- [x] Update SDLC guide and manifest.
- [x] Run scenario/content validation and review the complete diff.
- [x] Record result and promote the plan to `docs/plans/completed/`.

## Decisions

- 2026-08-06: Use one new explanatory skill rather than expanding
  `implementation-walkthrough`; this preserves the existing role boundaries.
- 2026-08-06: Keep the output per consequential test file and aggregate
  equivalent cases; do not list every test case by default.
- 2026-08-06: Define a canonical group block for helper, fixture, and generated
  files so aggregation does not weaken the six-section output contract.
- 2026-08-06: Keep the guide's CodeGraph wording capability-based rather than
  tied to the number of workflow skills.

## Validation

- Focused proof: `quick_validate.py` exited 0; UI metadata parsed as YAML; the
  static scenario/content assertion script exited 0 for required sections,
  routing boundaries, generated-group format, and unchanged out-of-scope files.
- Integration or end-to-end proof: an independent read-only Codex forward-test
  exited 0 and covered all eight scenarios in-memory. No application test,
  build, or runtime suite exists in this documentation-only repository.
- Repository-required checks: authority-first diff review and fresh
  `git diff --check` exited 0 after the final edits; no staged or pre-existing
  user changes were present.

## Result

Implemented the repository-local `test-walkthrough` skill and integrated its
read-only comprehension route with the router, formal review handoffs, root
instructions, workflow guide, and skill manifest. The output is now
per-consequential-file (or canonical grouped set) with the six required
sections plus one conclusion, while adequacy, severity, approval, and command
pass claims remain with their existing skills.

Fresh proof passed for metadata, YAML, routing/output contract, generated-group
format, out-of-scope protection, and diff hygiene. The repository has no
application test/build/runtime surface for this documentation-only change, so
the forward-test is static/in-memory and does not prove a live skill invocation.
