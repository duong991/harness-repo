# CodeGraph Policy

This is consumer-owned, task-specific guidance. It applies only when the root
`AGENTS.md` directs the agent here for a CodeGraph-relevant task. In a conflict,
`AGENTS.md`, `docs/WORKFLOW.md`, accepted decisions, and accepted product,
design, API, security, and permission contracts take precedence.

## Role

CodeGraph is optional code-intelligence infrastructure. It may help map symbols,
call paths, routes, dependencies, and candidate impact surfaces. It is not a
workflow, plan system, authority source, or completion gate.

## Use it only when ready

Use CodeGraph only when a live MCP or CLI capability is available to the agent
and its index is usable for the current worktree. Prefer its supported MCP or
CLI interface; never read or write a private index or database format directly.

If it is unavailable, stale, or incomplete, use targeted repository inspection.
Do not install, initialize, reconfigure, or block the task solely to obtain
CodeGraph. Keep `.codegraph/` out of version control.

## Evidence boundary

CodeGraph results are derived navigation evidence. They can identify candidates
to inspect, but cannot:

- classify a task or widen its scope;
- create plans or stories, or mutate Harness state;
- establish product, design, architecture, API, security, permission, or scope
  authority;
- prove root cause, a complete runtime call path, or a complete impact set; or
- replace tests, builds, runtime checks, or other executable validation.

Read consequential source files directly. Account for dependency injection,
dynamic dispatch, reflection, generated code, templates, event-driven flows,
and external integrations that static analysis may not observe.

## Skill use

- `work-router`: use graph output only to narrow the code surface after task
  classification remains unchanged.
- `diagnosing-bugs`: use it to form and eliminate hypotheses; reproduce and
  direct evidence still establish root cause.
- `code-review`: use it to find candidate callers, callees, routes, and
  consumers; inspect them directly. Graph output cannot replace its mandatory
  authority-compliance stage.
- `verification-before-completion`: graph health, sync, impact output, or an
  absence of visible callers is never completion evidence.

## Runtime integration status

This Harness scaffold defines policy only. It deliberately does not install,
configure, or index CodeGraph. A consumer application may add a pinned
CodeGraph CLI/MCP setup, telemetry policy, and local index after separately
reviewing that repository's security and operational requirements.
