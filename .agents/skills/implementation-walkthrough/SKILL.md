---
name: implementation-walkthrough
description: Explain a large implementation by organizing it into behavior-based Review Units, tracing the highest-consequence Critical Path, probing risks and invariants, classifying evidence freshness, and handing off a bounded review order before formal code review. Use for large diffs, commits, branches, PRs, worktrees, or prompts such as “how should these files be reviewed?” or “split this change into reviewable parts”; do not use it to find bugs, assign severity, approve changes, or mutate git state.
---

# Implementation Walkthrough

Explain how a developer should read a change. Use exactly five phases:

```text
BASELINE → MAP → TRACE → PROBE → HANDOFF
```

This skill is read-only and explanatory. It does not judge correctness,
security, adequacy, severity, compliance, or approval. Those conclusions belong
to `code-review`; command execution proof belongs to
`verification-before-completion`.

## Routing boundary

Use this skill for large-change comprehension and review organization:

- “107 files này nên review thế nào?”
- “chia change này thành từng phần để review”
- “giải thích implementation trước khi review”
- “show me what to read first”
- a large diff, commit, branch, PR, or worktree needing a bounded review order.

Keep a small 2–3 file change lightweight. Do not manufacture eight Review
Units when the change is one independently reviewable behavior.

When the user asks to find bugs or produce formal findings, run this walkthrough
first when the target is large, then hand off to `test-walkthrough` when the
test surface is materially large, and finally to `code-review`. When the user
asks only what tests prove, route directly to `test-walkthrough`. When the user
asks to split and commit, propose a decomposition only; git mutation is a
separate authorized workflow.

Do not create or suggest a `review-planner`, `review-decomposition`,
`security-review`, or `large-change-review` skill.

## Evidence boundary

Classify every important statement as one of:

- **Authority**: accepted product, API, security, permission, protocol, or
  architecture requirement.
- **Observed**: structure or behavior visible in the inspected source, diff,
  configuration, schema, or test.
- **Claimed**: a plan, PR description, commit message, or previous report.
- **Inference**: a likely consequence derived from observed material but not
  independently executed.
- **Verified now**: evidence established by a command or scenario in this
  walkthrough.
- **Existing evidence**: supplied or previous output inspected but not rerun.
- **Unverified**: behavior dependent on commands, runtime, environment,
  deployment, external systems, or topology not checked now.

Never turn a plan, test name, old output, graph result, or code appearance into
fresh verification. If `HEAD`, staged files, untracked files, or the requested
target changes during the walkthrough, invalidate the map and rerun BASELINE.

Use a supplied or matching active plan as navigation context only. Apply
accepted authority from the user request, product/design material, decisions,
and contracts; a plan or PR claim cannot create missing policy. If authority
sources conflict, record the conflict for `code-review` rather than choosing a
winner here.

If `.codegraph/` exists and a live, current CodeGraph capability is available,
use it only to narrow candidate symbols, callers, and consumers after the
target is fixed. Read consequential source directly; graph output is not
authority, a complete impact set, or runtime proof.

## Phase 1 — BASELINE

Identify the exact review target before explaining it:

- worktree, staged diff, unstaged diff, untracked files, branch, commit, range,
  or PR;
- fixed commit/range or current `HEAD`;
- file count, additions/deletions/renames, commits already separated, generated
  or mechanical surfaces, and consequential files;
- validation evidence available, with each item marked fresh, stale, failed,
  unavailable, or unknown.

For a worktree, use read-only inspection such as:

```bash
git status --short
git diff --cached --stat
git diff --cached --name-status
git diff --cached --numstat
git diff --stat
git diff --name-status
```

Inspect complete consequential files, not only hunks. Preserve unrelated
staged, unstaged, and untracked work. Do not reset, checkout, stage, commit,
split, or rewrite the target.

BASELINE is complete only when the exact target is known and all available
validation evidence has a freshness classification.

## Phase 2 — MAP into Review Units

Use this canonical definition:

```text
Review Unit
= one independently reviewable behavior, contract, runtime responsibility,
  or trust boundary.
```

Group consequential files by the behavior they jointly implement, not by
folder, extension, layer, or file count. For example, do not use `src/auth/*`
and `src/user/*` as units merely because they share directories. An
authorization change may instead contain units such as primitives, ability
construction, route enforcement, resource scope, cache invalidation, policy
integration, user context, and storage boundaries.

Account for every consequential changed file. Each file must belong to a
Review Unit or be explicitly classified as:

- `generated/mechanical`;
- `proof/test`;
- `supporting`;
- `skim`;
- `ignored` with a reason.

For every unit, record cross-unit dependencies and keep two dimensions separate:

```text
Reading priority: Must-read | Supporting | Proof | Skim
Risk: Critical | High | Medium | Low
```

A small change may have one Review Unit. A large change may have as many units
as independently reviewable responsibilities require, without arbitrary
rounding or folder-based inflation.

MAP is complete only when every consequential file is accounted for, every unit
has one reviewable responsibility, and cross-unit dependencies are identified.

## Phase 3 — TRACE the Critical Path

Use this canonical definition:

```text
Critical Path
= the highest-consequence end-to-end runtime path affected by the change.
```

Risk-rank Review Units, then choose the highest-consequence path to trace first.
Trace the primary path plus the highest-risk negative or exceptional paths for
the domain. Do not hard-code authorization cases into the core workflow.

Examples of domain-shaped paths include:

```text
Request → authentication → user context → ability construction
→ route authorization → resource authorization → scoped query → response
```

or:

```text
Input → validation → persistence → event/queue → retry/recovery → consumer
```

For each path, identify entry point, transformations, trust boundaries,
side-effects, outputs, failure states, and units crossed. Load a domain
reference only when that risk boundary is materially present; available
references are linked from this skill's `references/` directory.

TRACE is complete only when the critical path, its crossed units, and the
highest-risk negative or exceptional paths are explicitly recorded.

## Phase 4 — PROBE risks and invariants

Use these canonical definitions:

```text
Risk Probe
= targeted search or inspection used to locate potentially dangerous
  implementation sites.

Invariant
= an observable property expected to remain true throughout the change.
```

Risk Probes may use targeted searches such as:

```bash
rg "authorize|ability|permission|policy" <scope>
rg "return true|allow|bypass|skip|super_admin" <scope>
```

Adapt probes to the domain: transaction boundaries, retry/idempotency,
ordering, destructive operations, external calls, cache invalidation, or
tenant scope. A Risk Probe hit is discovery evidence, not a finding. Trace the
hit and send it to `code-review` before anyone judges it.

For each unit, state the invariant it should preserve and the evidence that
currently supports it. Distinguish supplied/pre-existing evidence from fresh
verification:

```text
Known evidence:
344 operation IDs — supplied/pre-existing

Fresh verification:
Not run
```

Never write “route coverage passes 344/344” unless the command was run in the
current turn and its result was read.

PROBE is complete only when each high-risk unit has targeted probes, observed
hits are traced or explicitly unresolved, and important invariants are named
with their evidence boundary.

## Phase 5 — HANDOFF

Create a compact review handoff. Do not repeat entire source files or produce
formal findings. Use this contract for each Review Unit:

```text
## RU-03 — Route authorization

Purpose
What behavior or contract this unit owns.

Risk
Critical | High | Medium | Low

Failure modes
What could go wrong if this implementation is incorrect.

Files
Must-read:
- ...

Supporting:
- ...

Proof/test:
- ...

Dependencies
RU-01 → RU-02 → RU-03

Observed path
Request
→ ...

Architecture questions
Questions that must be resolved from the codebase.

Risk Probes
Targeted searches or inspections performed or recommended.

Test evidence
What is currently demonstrated, with freshness classified.

Unverified
What evidence is missing or unavailable.

Invariant
What observable property should remain stable.

Formal review
Pending code-review
```

End with:

1. a proposed review order by Critical Path and risk;
2. a compact progress matrix with `Review Unit`, `Risk`, `Source traced`,
   `Critical path`, `Test evidence`, `Invariant`, and `Formal review` columns;
3. the tests that should be handed to `test-walkthrough` when there are more
   than three consequential test files or a large generated test set;
4. unresolved questions and validation still required.

Suggested commit decomposition may be included:

```text
Suggested commit decomposition:
1. feat(authz): add authorization primitives
2. feat(authz): build abilities
3. feat(authz): enforce route authorization
```

This is a proposal only. Never run `git reset`, `git add`, `git commit`, or
other repository mutation from this skill.

## Default output order

Keep the response compact and behavior-oriented:

1. Evidence boundary and exact BASELINE target.
2. Review Unit map and file accounting.
3. Critical Path and crossed dependencies.
4. Risk Probes, invariants, and evidence freshness.
5. Review Unit handoff and recommended reading order.
6. Test handoff, validation gaps, and unresolved questions.

Use Mermaid only when it materially clarifies a critical runtime path. Do not
create a test matrix, formal severity finding, approval statement, or line-by-
line test inventory by default. `code-review` remains the only formal review
entry point.
