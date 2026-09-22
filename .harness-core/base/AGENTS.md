# Agent Instructions

<!-- HARNESS:BEGIN -->
## Harness

Start with the requested outcome, then use the repository as the system of
record. Read `docs/WORKFLOW.md` and only the product, design, plan,
code, and validation material relevant to the task.

- Answers, explanations, reviews, diagnoses, plans, and status reports are
  read-only. Inspect only what is needed and do not mutate repository or Harness
  state.
- For a bounded change, use an ephemeral plan: inspect the affected behavior and
  existing proof, implement the change, and run behavior-appropriate validation.
  No control-plane operation is required.
- Create or update one file under `docs/plans/active/` when work spans sessions,
  needs coordination or an ordered sequence, has meaningful dependencies, or
  requires explicit recovery steps. Move it to `docs/plans/completed/` only
  after validation.
- Before editing, identify repository authority for each new externally
  observable policy. If materially different choices remain open, stop before
  edits; configurable defaults are not authority.
- For architecture, reliability, security, or quality invariant work, read
  `docs/patterns/encoding-invariants.md` and enforce only accepted rules.
- Report reusable agent friction. Change guidance, tools, runbooks, or validation
  for that purpose only when explicitly asked to use `$improve-harness`.
- Also pause when product intent remains ambiguous, an action is difficult to
  recover, validation would be weakened, or the request does not authorize the
  needed action.
- Claim completion only with relevant executable or observable evidence. Report
  the outcome, important changed surfaces, validation, and unresolved risks.

Harness has no task database or orchestration lifecycle. Use repository plans
and behavior-level proof; do not create parallel control-plane state.
<!-- HARNESS:END -->

## Task routing

Use `work-router` before changing repository state. It owns the work-type
taxonomy and downstream routing table; see
[`.agents/skills/work-router/SKILL.md`](.agents/skills/work-router/SKILL.md).

Hard invariants:

- A read-only request remains read-only even when a defect is discovered.
- Downstream skills cannot widen scope, create plans or stories, or introduce
  orchestration.
- Formal findings and adequacy judgments belong only to `code-review`.
- Large-change comprehension belongs to `implementation-walkthrough`; test
  comprehension belongs to `test-walkthrough`.
- Do not create parallel review-planning or review-decomposition skills.
- Any positive completion claim requires fresh evidence through
  `verification-before-completion`.

## Optional code intelligence

When a task concerns symbols, call paths, routes, dependencies, or code impact
and CodeGraph is available, read [`docs/tools/codegraph.md`](docs/tools/codegraph.md)
before using it. CodeGraph remains optional and cannot change task routing,
authority, scope, Harness state, or the completion evidence required.
