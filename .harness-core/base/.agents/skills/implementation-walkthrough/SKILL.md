---
name: implementation-walkthrough
description: Explain a large implementation by organizing it into behavior-based Review Units, tracing consequential runtime paths, probing risks and invariants, classifying evidence freshness, and handing off a bounded review order before formal code review. Use for large diffs, commits, branches, PRs, worktrees, or prompts such as “how should these files be reviewed?” or “split this change into reviewable parts”; do not use it to find bugs, assign severity, approve changes, or mutate git state.
---

# Implementation Walkthrough

Explain how a developer should read a large change. Use five phases:

```text
BASELINE → MAP → TRACE → PROBE → HANDOFF
```

This skill is read-only and explanatory. Correctness, security, adequacy,
severity, compliance, and approval belong to `code-review`; fresh command proof
belongs to `verification-before-completion`.

## Boundary

Use for large-change comprehension, review organization, or a requested reading
order. Keep a 2–3-file change lightweight. Do not manufacture Review Units from
folders or file count.

For a large request to find bugs or formal findings, run this walkthrough first,
then hand off a materially large test surface to `test-walkthrough` and formal
judgment to `code-review`. A request only to understand tests routes directly
to `test-walkthrough`. A requested split/commit receives a proposed
decomposition only; this skill never changes Git state.

Do not create or suggest a `review-planner`, `review-decomposition`,
`security-review`, or `large-change-review` skill.

## Evidence boundary

Classify important statements as **Authority**, **Observed**, **Claimed**,
**Inference**, **Verified now**, **Existing evidence**, or **Unverified**.
Never treat a plan, test name, old output, graph result, or code appearance as
fresh verification. If the target changes during the walkthrough, invalidate
the map and rerun BASELINE.

An active plan or PR describes navigation context, not policy. Apply accepted
authority from the user request, product/design material, decisions, and
contracts. Record conflicts for `code-review` rather than choosing a winner.

When a current CodeGraph capability and index exist, use them only to narrow
candidate symbols and consumers after the target is fixed. Read consequential
source directly; graph output is neither authority nor complete impact or
runtime proof.

## BASELINE — fix the review target

Identify the exact worktree, staged/unstaged diff, branch, commit, range, or
PR. Record the fixed revision, file count, additions/deletions/renames,
consequential versus mechanical files, and available validation evidence with
freshness (`fresh`, `stale`, `failed`, `unavailable`, or `unknown`).

Inspect complete consequential files, not only hunks. Preserve unrelated
staged, unstaged, and untracked work. Do not reset, checkout, stage, commit,
split, or rewrite the target. Use
[`references/target-resolution.md`](references/target-resolution.md) for
target-specific commands and edge cases.

Complete when the exact target and freshness of available evidence are known.

## MAP — group Review Units

Use this definition:

```text
Review Unit = one independently reviewable behavior, contract, runtime
responsibility, or trust boundary.
```

Group files by the behavior they jointly implement, never merely by directory,
extension, layer, or count. Account for every consequential changed file: place
it in a Review Unit or classify it as `generated/mechanical`, `proof/test`,
`supporting`, `skim`, or `ignored` with a reason.

For every unit, name its cross-unit dependencies and keep these dimensions
separate:

```text
Reading priority: Must-read | Supporting | Proof | Skim
Risk: Critical | High | Medium | Low
```

Complete when every consequential file is accounted for, every unit has one
reviewable responsibility, and dependencies are identified.

## TRACE — follow consequential runtime paths

Use this definition:

```text
Critical Path = the highest-consequence end-to-end runtime path affected by the
change.
```

Risk-rank Review Units, then trace one primary Critical Path first, including
its highest-risk negative or exceptional paths. When independently
consequential runtime domains cannot be represented by one path, trace the
primary path plus the minimum secondary paths needed to cover them—for example,
runtime authorization, migration/backfill, and cache invalidation.

For each path, identify entry point, transformations, trust boundaries,
side-effects, outputs, failure states, and crossed units. Load a domain
reference only when it materially applies; authorization guidance is in
[`references/authorization.md`](references/authorization.md).

Complete when the selected paths, crossed units, and high-risk negative or
exceptional paths are explicit.

## PROBE — risks and invariants

Use these definitions:

```text
Risk Probe = targeted search or inspection for potentially dangerous sites.
Invariant = observable property expected to remain true throughout the change.
```

Adapt probes to the domain: authorization and tenant scope, transaction
boundaries, retry/idempotency, ordering, destructive operations, external
calls, or cache invalidation. A probe hit is discovery evidence, not a finding;
trace it or mark it unresolved for `code-review`.

For each high-risk unit, state the invariant it should preserve and distinguish
existing/supplied evidence from verification run now. Complete when high-risk
probes, their hits, invariants, and evidence boundaries are recorded.

## HANDOFF — prepare a bounded review

For each Review Unit, record its purpose, risk, failure modes, must-read,
supporting, and proof files, dependencies, observed path, architecture
questions, probes, evidence freshness, unverified items, and invariant. Use the
compact template in
[`references/review-unit-handoff.md`](references/review-unit-handoff.md).

End with:

1. review order by Critical Path and risk;
2. a progress matrix with `Review Unit`, `Risk`, `Source traced`, `Critical
   path`, `Test evidence`, `Invariant`, and `Formal review`;
3. tests to hand to `test-walkthrough` when there are more than three
   consequential test files or a large generated test set; and
4. unresolved questions and required validation.

Commit decomposition may be suggested but is never executed by this skill.

## Default output order

1. Evidence boundary and BASELINE target.
2. Review Unit map and file accounting.
3. Critical Path(s) and dependencies.
4. Risk Probes, invariants, and freshness.
5. Handoff and reading order.
6. Test handoff, validation gaps, and unresolved questions.

Use Mermaid only when it makes a consequential path clearer. Do not produce a
test matrix, formal finding, severity, approval statement, or line-by-line test
inventory. `code-review` remains the sole formal review entry point.
