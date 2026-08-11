---
name: work-router
description: Classify every Repository Harness task into one primary work type and select the lightest safe workflow without creating a parallel authority. Use automatically at the start of repository tasks to distinguish read-only analysis, tiny fixes, bounded changes, ambiguous product changes, multi-session initiatives, and orchestrated multi-agent work, then route to the relevant local skills and repository validation.
---

# Work Router

Route work; do not replace repository authority. Read `AGENTS.md` and
`docs/WORKFLOW.md` first, then inspect only the product, design, architecture,
decision, plan, code, and validation evidence relevant to the request.

## Optional code intelligence

When the task concerns code structure, call paths, routes, dependencies, or
impact and a live CodeGraph capability with a usable index is available, use it
to locate the smallest candidate code surface before broad discovery. Confirm
staleness/status first and read the current files directly before relying on the
result.

If the capability is unavailable or stale, use targeted repository inspection
without installing or initializing CodeGraph. Graph output is derived
navigation evidence: it cannot classify the task, widen scope, establish
authority, or replace tests and runtime validation.

## Select exactly one primary type

Choose the first type that accurately captures the requested outcome:

1. **read-only-analysis** — explanation, review, impact analysis, status, or
   diagnosis without authorized changes. Use `inspect → collect evidence →
   report`. When the request concerns a concrete failure, use
   `diagnosing-bugs` in read-only mode to reproduce, identify the root cause,
   and report without implementing a fix. For a request to understand a large
   completed implementation, such as “explain these changes”, “organize this
   diff for review”, or “show me what to read first”, use
   `implementation-walkthrough`. When correctness findings are also requested,
   run `implementation-walkthrough` first and then `code-review`. Do not edit,
   create a plan, create a story, or mutate Harness state.
   When the user only wants to understand what one or more test files exercise,
   which production symbols they call, or what remains unproven, use
   `test-walkthrough`. It produces a compact per-file digest and stops without
   formal findings. When the user asks whether tests are sufficient, correct,
   safe, complete, or approvable, use `code-review` as the review entry point;
   `code-review` may create a test digest before judging adequacy.
   For a request asking for findings, implementation compliance, review against
   requirements, or review against authority, use `code-review`; its mandatory
   authority-compliance stage runs before its technical review.
2. **tiny-fix** — a localized bug with narrow behavior and a small affected
   surface. Use `diagnosing-bugs → minimal patch → tdd when a valuable
   regression seam exists → validation → verification-before-completion`.
   Do not grill, create an active plan, or use Harness CLI.
3. **bounded-change** — a concrete, limited feature or flow, such as adding an
   existing-domain filter, that can be completed coherently in one session.
   Discover minor details from repository authority and adjacent behavior; do
   not promote missing implementation detail into product ambiguity. Use an
   ephemeral plan, conditional TDD, implementation, `code-review` when the
   change is medium-sized, and
   `verification-before-completion`. Do not create an active plan merely
   because the work has several steps.
4. **ambiguous-product-change** — materially different user outcomes, UX flows,
   permission policies, scope boundaries, or acceptance contracts remain open.
   Use this type only when selecting one option would reject another plausible
   product direction; ordinary implementation choices remain bounded. Propose
   the explicit `$grill-me` skill,
   produce a confirmed Change Brief or Product Brief, then reclassify. Do not
   change code before the decision has authority.
5. **multi-session-initiative** — work spans sessions, has meaningful
   milestones/dependencies, affects several areas, or needs recovery/rollback.
   Create or resume exactly one file under `docs/plans/active/`, implement by
   milestone, use `code-review`, then apply
   `verification-before-completion` against every milestone and acceptance
   criterion before moving the plan to `docs/plans/completed/`.
6. **orchestrated-multi-agent-work** — independent workers need machine-readable
   dependencies, runnable-task selection, locking, retry, or explicit lifecycle
   state. Use one active plan and Harness CLI only when it is installed and an
   identified orchestrator consumes its state. Never select this type merely
   because a task has many steps.

## Routing rules

- Let an explicit user constraint override inferred routing. A read-only
  request remains read-only even if a defect is discovered.
- Inspect the repository instead of asking for facts already recorded there.
- Keep a concrete local feature as `bounded-change` when repository evidence can
  supply its domain values, defaults, and interaction pattern. Reclassify it as
  ambiguous only when a materially different observable policy still requires
  human judgment.
- Stop before edits when product intent, security policy, compatibility, or a
  hard-to-recover action lacks authority.
- Use `diagnosing-bugs` as the only debugging workflow, `tdd` as the only TDD
  workflow, `code-review` as the primary review workflow, and
  `verification-before-completion` as the sole completion gate.
- Do not create sub-agents, Harness CLI stories, task databases, alternate plan
  locations, or alternate decision locations from this skill.
- Do not require grilling, TDD, a durable plan, or a full review when the
  selected work type does not justify it.

## Brief routing notice

Before acting, tell the user only:

```text
Task type: <one primary type>
Workflow: <short route>
Validation: <expected proof>
```

Keep the internal routing analysis private. If evidence changes the work type,
state the reclassification and why before widening the workflow.
