---
name: gnoud-bootstrap-product
description: Route and execute product work from a blank or early-stage repository through clarified requirements, product/design/architecture authority, minimal scaffold, first vertical slice, independent review, and behavior-appropriate validation. Use when Codex must choose between repository discovery, product grilling, brief creation, scaffold work, a first feature, a tiny fix, a bounded change, an active plan, or conditional Harness CLI orchestration; stop before edits when materially different product or architecture decisions lack authority.
---

# Bootstrap Product

Use this skill as a guarded lifecycle router. Start from the repository's
instructions and evidence, choose the smallest workflow that can safely satisfy
the request, and only widen the workflow when the task's risk or duration
requires it.

## Operating contract

1. Read `AGENTS.md` and `docs/WORKFLOW.md` before deeper inspection. Read only
   product, design, architecture, decision, code, and validation material that
   is relevant to the requested behavior.
2. Treat the repository as the system of record. Label important claims as
   `Observed`, `Derived`, `Authoritative`, `Decision required`, or `Unknown`.
   Do not turn a convention, implementation detail, or configurable default
   into product policy.
3. Preserve unrelated worktree changes. Discovery and review are read-only.
   Do not install tools, start services, create stories, or mutate Harness
   state unless the selected workflow explicitly authorizes that action.
4. Choose the smallest route below. Do not run `grill-me`, create an active
   plan, or use Harness CLI merely because a task has multiple steps.
5. If a question can be answered from the repository, inspect it instead of
   asking. If a materially different product or architecture choice remains,
   ask one question at a time and include a recommended answer with its
   rationale.
6. Before any mutation, state the observable outcome, authority, scope,
   affected surfaces, acceptance criteria, and validation. Stop if the needed
   authority or user authorization is missing.
7. Claim completion only from executable or observable evidence. Report changed
   surfaces, validation results, limitations, and unresolved decisions.

## Route the task

Classify the request before acting:

- **Read-only analysis, review, diagnosis, or status:** inspect the minimum
  evidence, return findings, and do not edit.
- **Tiny fix:** reproduce or isolate the cause, make the smallest patch, and
  run focused proof. Do not grill, create an active plan, or use CLI.
- **Bounded change:** use an ephemeral plan in the current session; inspect
  affected authority, implement the smallest coherent patch, and validate it.
- **Ambiguous product change:** run the one-question-at-a-time product grill;
  do not design architecture or write code until the product change brief is
  clear.
- **Blank or early-stage repository:** use the bootstrap sequence below and
  load the matching templates from `references/workflow-catalog.md`.
- **Multi-session initiative:** create exactly one plan under
  `docs/plans/active/` using `docs/templates/exec-plan.md`; record progress,
  decisions, risks, recovery, and validation there.
- **Orchestrated multi-agent work:** first evaluate whether machine-readable
  state, real dependencies, retries, locking, or worker coordination justify
  Harness CLI. Keep CLI conditional.

## Bootstrap sequence

For a repository with no application code, progress in this order and stop at
the first unresolved authority:

1. Survey the repository read-only and report observed state, missing authority,
   open decisions, and the lightest next step.
2. Grill the product intent. Resolve users, problem, primary job, MVP,
   out-of-scope behavior, states, data, security, operations, and measurable
   success criteria. End with a concise Product Change Brief.
3. Create `docs/product/product-brief.md` only after the answers are confirmed.
   Keep assumptions and `Decision required` items separate.
4. For UI work, create `docs/design/design-brief.md` before components. Cover
   navigation, hierarchy, all important states, responsive behavior,
   accessibility, density, tokens, and prohibited patterns.
5. Create `docs/ARCHITECTURE.md` after the product brief and, for UI work, the
   design brief. Prefer the simplest architecture that meets the authority.
6. Record technology choices as decisions when they have lasting impact; do
   not add framework or dependency choices without a concrete need.
7. Scaffold only the application shell, routes, build/lint/test setup, and
   README commands that the authority requires. Avoid fake features.
8. Implement the smallest valuable vertical slice across route, page, state,
   service/data adapter, loading/empty/error behavior, and tests.
9. Run an independent review and reconcile findings against authority and
   evidence. Finish with a completion audit; do not use story state or scores
   as a substitute for tests or runtime proof.

Do not introduce Harness CLI during the first eight stages. Consider it only
when several independent workers, real dependency scheduling, retry/locking,
long-lived lifecycle, machine-readable status, or audit tracing is required.

## Guarded execution boundaries

- **Discovery boundary:** read-only. Do not create briefs, code, stories, plans,
  caches, or runtime state.
- **Authority boundary:** create or update product/design/architecture artifacts
  only when the user asks for that stage or confirms the clarified decision.
- **Implementation boundary:** require the relevant authority, explicit scope,
  acceptance criteria, and a validation command before changing source code.
- **Orchestration boundary:** propose CLI stories before registering them;
  workers must not invent stories, alter dependencies, or broaden scope.
- **Recovery boundary:** for migrations, destructive operations, or other hard-
  to-recover work, stop until rollback/recovery is explicit.

## Handoff format

Before edits, report:

```text
Task class:
Observable outcome:
Authority:
Scope / out of scope:
Affected surfaces:
Acceptance criteria:
Validation:
Open decisions:
Selected route:
```

After work, report:

```text
Outcome:
Changed surfaces:
Validation evidence:
Limitations / unknowns:
Remaining decisions:
```

## Reference catalog

Read `references/workflow-catalog.md` when a phase-specific prompt, artifact
shape, SOC example, review rubric, or CLI decision checklist is needed. Use the
smallest relevant section; do not load or execute the entire catalog by habit.
