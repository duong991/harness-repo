---
name: review-against-authority
description: Review a patch, branch, pull request, or implementation against the repository's actual authority and fresh evidence. Use after work-router classifies a read-only review or a medium or large change, and whenever the user explicitly requests review; prioritize the current user request and accepted product/design/architecture contracts over existing code, and return evidence-backed findings without editing files.
---

# Review Against Authority

Review the implementation, not the implementer's narrative. Keep the review
read-only and reconstruct the expected behavior from repository authority.

## Establish the review boundary

1. Read `AGENTS.md` and `docs/WORKFLOW.md`.
2. Resolve the patch boundary the user supplied. For uncommitted work, inspect
   staged and unstaged changes; for a branch or revision, verify the fixed point
   before reviewing its diff.
3. Record pre-existing worktree changes and do not modify, stage, fix, format,
   or generate files.

## Resolve authority

Apply this precedence when sources conflict:

1. current direct user request;
2. accepted product documentation;
3. accepted design documentation;
4. architecture and accepted decision records;
5. accepted API, security, and permission contracts;
6. active execution plan as execution guidance;
7. behavioral tests;
8. current code as observed behavior only.

Configuration defaults, code conventions, implementer comments, and existing
behavior do not create missing product policy. Mark unresolved normative choices
as `Decision required` instead of selecting one.

A document is accepted authority only when at least one is true:

- the current user explicitly approved it;
- repository workflow designates it as authoritative;
- an accepted decision record adopts it.

A draft, proposal, mockup, generated document, or stale plan is not accepted
authority merely because it exists in the repository.

An active plan may reference accepted authority, but it cannot confer authority
on a draft, proposal, generated document, or mockup. A plan reference counts
only when it records an explicit approval made by the user or another
recognized authority source.

## CodeGraph evidence

When a live, current CodeGraph capability is available, use it to discover
candidate callers, callees, routes, and impact surfaces that deserve review.
Read each consequential current file directly and account for static-analysis
blind spots such as dynamic dispatch, dependency injection, reflection,
generated code, templates, events, and external integrations.

CodeGraph results are derived navigation evidence. They cannot establish
authority, prove a runtime path, prove that the impact set is complete, or
replace executable validation.

## Review rubric

Inspect the changed behavior and relevant proof for:

1. requirement correctness;
2. scope discipline;
3. user-visible flow;
4. architecture and dependency fit;
5. security and permission behavior;
6. loading, empty, error, disabled, and stale states when applicable;
7. API contracts and data mapping;
8. appropriate behavioral test coverage;
9. fresh runtime or executable evidence;
10. documentation drift;
11. regression risk;
12. maintainability.

Trace each possible problem through the changed code and its consumers. Do not
report style issues already enforced mechanically unless the enforcement is
missing or the check fails. Do not invent requirements to make a finding.

## Severity

- **Critical** — security breach, data loss, destructive behavior, or direct
  violation of a non-negotiable product policy.
- **High** — incorrect user-visible behavior, broken permission boundary,
  incompatible contract, or release-blocking regression.
- **Medium** — incomplete edge state, meaningful maintainability risk, or
  likely localized regression.
- **Low** — limited issue with low impact that should not block the change.

## Findings

For every actionable finding, include:

```text
Severity:
Claim:
Authority and evidence:
File and location:
Impact:
Required correction:
Validation to rerun:
```

Order findings by severity. Keep summaries brief and list `Decision required`
items separately. If no actionable findings remain, say so and identify the
authority and validation surfaces actually checked; do not imply that untested
behavior passed.

Do not trust self-scores, agent consensus, old validation, or confident tone.
Do not spawn sub-agents, edit code, create plans, or create Harness CLI stories.
A tiny fix may skip a full review when its patch and fresh validation are
already narrow and clear, unless the user explicitly requests review.
