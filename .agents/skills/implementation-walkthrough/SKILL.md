---
name: implementation-walkthrough
description: Explain large implemented code changes as behavior-based review units, runtime flows, review order, contract changes, risks, and validation evidence. Use when a developer asks to understand, navigate, or get an overview of a large diff, commit, branch, or PR before detailed code review.
---

# Implementation Walkthrough

Create a developer-oriented guide to an observed implementation. Explain what
the change does and how to read it; do not claim that it is correct. Hand off
bug finding and correctness assessment to `code-review`, and do not replace
tests, executable validation, or repository authority.

## Resolve the target

- No target: inspect all uncommitted changes, including staged and unstaged.
- Commit: inspect `git show <commit>` and relevant parent context.
- Branch: inspect `git diff <branch>...HEAD`.
- PR: retrieve its description and diff with the available repository tools.

Record additions, modifications, deletions, renames, tests, generated files,
and dependency/configuration changes. Inspect complete consequential files, not
only diff hunks.

## Resolve plan and authority

Use a plan explicitly supplied by the user after confirming it relates to the
target. Otherwise inspect `docs/plans/active/` and rank candidates by branch
name, commit messages, changed paths, symbols, and stated scope. If one plan
clearly matches, ask for confirmation before using it; if several match, show
the candidates. Ignore `docs/plans/active/README.md`. If no relevant active
plan remains, ask the user whether to provide a plan path or continue with a
planless walkthrough. Do not silently use a completed or unrelated plan.

Treat plans as execution guidance, never as product, API, security, or
permission authority. Read the repository's governing instructions and the
accepted authority relevant to each externally observable contract.

## Build the implementation map

Use CodeGraph when the repository has it and the tool is available, after
reading the repository's CodeGraph instructions. Use it to discover candidate
entry points, callers, callees, consumers, and affected tests. Read important
source directly. Treat CodeGraph as navigation evidence only—not runtime
proof, complete impact analysis, or authority. Check framework wiring that may
not appear as ordinary calls, including dependency injection, decorators,
dynamic modules, events, queues, templates, and config-based registration.

Group changes by behavior or runtime responsibility, in this order of
preference:

1. Plan milestone or acceptance criterion.
2. User-visible or use-case behavior.
3. Runtime call path.
4. Domain responsibility.
5. File location.

Do not make primary groups such as “controllers”, “services”, and “tests” when
those files implement one behavior together.

Classify each file as deep review, normal review, skim, or generated/mechanical.
Do not automatically omit migrations, security configuration, dependency-lock
changes, or generated contracts with meaningful content changes.

## Produce the walkthrough

Default to a response in chat. Write a file under `docs/reviews/` only when the
user asks for an artifact. Include the disclaimer that the document is
explanatory review guidance and does not become product, API, security, or
design authority.

Start with a three-minute overview. Default to no more than seven logical
groups, 15 must-read files, three primary diagrams, and ten risks or unknowns.
Put remaining files in a compact appendix. Offer a deeper symbol- or file-level
walkthrough only on request.

The overview includes:

1. Executive summary: what changed, why, scope, and the main before/after.
2. A compact change map, before/after map, or runtime sequence when one makes
   dependencies, runtime flow, or review effort clearer.
3. Recommended review order, separated into must-read, supporting, proof-read,
   skim, and generated/mechanical files.
4. Top risk hotspots, deleted/replaced behavior, affected consumers, and
   unknowns.

For the guided review, include:

1. Logical change groups with purpose, files, runtime flow, and key contracts.
2. API, schema, persistence, configuration, and compatibility changes.
3. Tests and validation evidence, distinguishing observed evidence from claims
   that still need verification.
4. A plan/criterion → implementation → test → status matrix when a plan exists.

Use Mermaid only when it materially clarifies a change map, before/after
architecture, or runtime sequence; never add a decorative diagram. Use these
plan-coverage statuses: `Satisfied`, `Partially satisfied`, `Missing`,
`Contradicted`, `Unverifiable`, and `Not applicable`. Check requirements that
do not appear in the diff as well as those that do.

For every group answer: what it enables, how it runs, which contract matters,
which tests cover it, and what the developer should verify manually. Prefer
file paths with symbols or line references where available.

Use cautious language such as “the implementation routes…” and “the related
tests are…”. Never write “this is correct” unless a separate authoritative
validation actually establishes that claim.

## Handoff

End with a concise next step: invite the developer to read the proposed order,
then run `code-review` for correctness findings and the relevant executable
validation. Do not modify code while producing the walkthrough unless the user
separately requests implementation work.
