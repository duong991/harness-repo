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
- Also pause when product intent remains ambiguous, an action is difficult to
  recover, validation would be weakened, or the request does not authorize the
  needed action.
- Claim completion only with relevant executable or observable evidence. Report
  the outcome, important changed surfaces, validation, and unresolved risks.

SQLite intake, story, trace, scoring, audit, and proposal commands are optional
compatibility features. Use them only when explicitly requested or required by
an external orchestrator.

## Optional code intelligence

When a CodeGraph capability is actually available to the agent and its index is
current, use it to map symbols, call paths, routes, dependencies, and candidate
impact surfaces before broad code discovery.

- Use the supported MCP or CLI interface. Do not read or write a private graph
  database or index format directly.
- Treat graph results as derived navigation evidence, never as product, design,
  architecture, API, security, permission, or scope authority.
- Treat impact results as candidates for inspection, not a complete proof of the
  runtime dependency set. Read the current source directly when the index is
  stale or when dynamic dispatch, dependency injection, reflection, generated
  code, templates, events, or external integrations may be involved.
- CodeGraph is optional. If it is unavailable or not current, fall back to
  targeted repository inspection. Do not install, initialize, reconfigure, or
  block the task solely to obtain CodeGraph.
- CodeGraph does not classify the task, widen scope, create plans or stories,
  mutate Harness state, or replace executable and runtime validation.
<!-- HARNESS:END -->
