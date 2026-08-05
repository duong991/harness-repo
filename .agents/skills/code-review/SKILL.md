---
name: code-review
description: Reviews a PR, commit, branch, diff, revision range, or codebase change against accepted product and technical authority, then evaluates correctness, security, maintainability, compatibility, regression risk, and validation evidence. Use when the user asks for code review, change review, PR review, implementation compliance, review against requirements, review against a specification or design, or review against authority.
---

# Code Review

Review in two ordered layers:

```text
Authority compliance
        ↓
Technical correctness
```

Keep reviews read-only. Do not edit, stage, format, create plans, create Harness
state, or spawn sub-agents unless the router selected an authorized workflow
that explicitly requires those actions. Review only the requested target; do
not turn a bounded patch review into a repository audit.

## Resolve the review target

Choose the narrowest target that matches the request:

1. For no argument, inspect both `git diff` and `git diff --cached`.
2. For a commit, inspect `git show <commit>`.
3. For a branch, inspect `git diff <branch>...HEAD`.
4. For a revision range, inspect `git diff <from>..<to>`.
5. For a pull request, use `gh pr view <pr>` for its description and commits,
   and `gh pr diff <pr>` for its diff; inspect changed files, declared tests,
   and validation evidence as well.

Verify the fixed points before reviewing a branch or range. Record unrelated
pre-existing worktree changes and leave them untouched.

## Gather sufficient context

Treat the diff as a starting point. Read consequential changed files in full,
plus the smallest relevant set of callers, consumers, interfaces, schemas,
types, tests, error paths, permission boundaries, configuration, migrations,
and deployment or rollback behavior.

Create findings only for problems the change causes, exposes, or makes worse.
Read outside the diff when needed to prove impact.

When a live and current CodeGraph capability exists, use it only to locate
candidate callers, callees, routes, and consumers. Read consequential source
directly and account for dynamic dispatch, dependency injection, reflection,
generated code, templates, events, and external integrations. Treat graph
output as navigation evidence, never as authority, runtime proof, or proof of
complete impact coverage.

## Resolve accepted authority

Establish which source may decide the reviewed behavior. Apply this precedence
when sources conflict:

1. Current direct user request and accepted product or business decision.
2. Accepted design or specification.
3. Public API, schema, protocol, security, or permission contract.
4. Repository policy, architecture, and accepted decision record.
5. Accepted task brief.
6. Implementation plan as execution guidance only.
7. Existing tests and code as evidence of observed behavior only.
8. Reviewer inference.

Treat a document as accepted authority only when the user approved it, the
repository workflow designates it as authoritative, or an accepted decision
record adopts it. Do not promote drafts, proposals, mockups, generated text,
comments, README statements, defaults, conventions, plans, or existing code
into missing product policy.

When authority is insufficient, record a separate `Decision required` item.
State the unresolved policy choice and the behavior the implementation
currently selects. Do not choose a policy or claim compliance. Continue the
technical review where possible.

## Review authority compliance first

Compare observable behavior and contracts to accepted authority before judging
implementation quality. Check for:

- missing requirements or extra unapproved behavior;
- changed defaults, fallbacks, or error policy;
- broken accepted contracts;
- shifted responsibility between client and server;
- weakened validation, authorization, or permission boundaries; and
- implementation-plan choices that contradict higher authority.

Well-written code that implements the wrong policy is incorrect.

## Review technical correctness

After the compliance pass, inspect:

- **Correctness:** conditions, mapping, nullability, boundaries, stale state,
  retries, duplicate processing, idempotency, partial updates, swallowed errors,
  races, and resource release.
- **Maintainability:** duplication, misplaced abstraction, unnecessary coupling,
  misleading names, mixed responsibilities, hidden side effects, and hard-coded
  configuration. Report style only when an accepted convention is violated and
  mechanical enforcement does not already cover it.
- **API and compatibility:** request and response contracts, optionality, enums,
  serialization, consumer compatibility, version negotiation, migrations,
  deployment order, and rollback.
- **Test quality:** observable behavior, regression coverage, failure paths,
  mocks that hide real behavior, assertion strength, and whether tests prove the
  pull request's claims.
- **Performance:** report only concrete risks such as unbounded quadratic work,
  N+1 access, or blocking I/O on a demonstrated hot path.

Investigate before asserting a bug. Describe the realistic input, state,
environment, or sequence needed to reproduce it.

## Trace security and trust boundaries

For changed flows involving external input, authentication, authorization,
tenant data, storage, files, commands, queries, networking, secrets, or
destructive operations, trace:

```text
Untrusted input
→ parsing
→ validation
→ authorization
→ sensitive operation
→ storage or output
```

Verify enforcement at the real backend or operation boundary, not only in the
UI or caller. Check tenant isolation, injection, path traversal, unsafe file
access, token or personal-data leakage, fail-closed behavior, race-driven
permission bypass, and direct-API bypasses. For a security finding, identify
the attacker-controlled input, missing control, and concrete impact.

## Review regression and impact

Follow producer changes to consumers and interface changes to implementations
and callers. Check APIs, databases, caches, queues, events, feature flags,
existing tests, backward compatibility, deployment order, and rollback.

## Gate the adversarial pass by risk

Run an explicit counterexample pass when the change involves authentication,
authorization, tenant isolation, external input, file transfer, secrets,
migrations or schemas, concurrency, retries or idempotency, destructive
operations, public API compatibility, multiple services, or a material
assumption discovered during review.

Probe bypasses, duplicate events, failure paths, old state, old consumers, and
unsafe deployment order. Skip this pass for low-risk changes such as a tiny CSS
diff unless another risk signal is present.

## Evaluate validation evidence

Separate:

```text
Evidence available
Evidence missing
Validation to rerun
```

Do not infer working behavior from code appearance, historical test results,
pull-request claims, plan checkboxes, or static analysis alone. If running
validation directly, apply `verification-before-completion`: run it fresh,
read the exit code and relevant output, and keep claims within the evidence.

When no code finding exists but runtime proof is missing, report both
`No actionable code findings found.` and the remaining validation gap. Do not
imply that untested behavior works.

## Classify and report findings

Use one technical severity per actionable finding:

- **Critical:** likely severe data loss, authentication or authorization
  bypass, broad data exposure, remote code execution, or inability to deploy or
  roll back safely.
- **High:** important requirement violation, primary production failure,
  broken API or permission contract, main-flow data corruption, or definite
  consumer regression.
- **Medium:** realistic edge-case failure, incomplete error handling or
  validation, missing proof for important behavior, or maintainability likely
  to produce a defect.
- **Low:** limited clarity, naming, duplication, or test-readability issue with
  no material current behavior impact.

Keep `Decision required` separate; it is an unresolved-authority state, not a
technical severity.

For every finding, use:

```text
[Severity] Short title

Claim:
Authority and evidence:
Location:
Impact:
Required correction:
Validation to rerun:
```

Order findings by severity and evidence strength. Specify the required outcome
without forcing one implementation when alternatives satisfy authority.

Structure the final report as:

```text
Review target
Authority used
Summary
Findings
Decision required
Validation gaps
Files inspected
```

If no actionable finding exists, say `No actionable findings found.` and still
identify authority, inspected scope, available validation, missing validation,
and review limitations. Never return only `LGTM`.
