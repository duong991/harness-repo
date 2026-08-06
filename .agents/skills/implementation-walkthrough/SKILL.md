---
name: implementation-walkthrough
description: Explain large implemented code changes as behavior-based review units, runtime flows, review order, contract changes, evidence boundaries, and unresolved questions before formal review. Use when a developer asks to understand, navigate, or get an overview of a large diff, commit, branch, or PR. Do not use when the primary request is to find defects, assign severity, judge compliance, or approve the implementation; use code-review instead.
---

# Implementation Walkthrough

Create a developer-oriented guide to an observed implementation.

Explain what changed, how the implementation is organized, how the main
runtime paths appear to work, and how a reviewer should read the change.

Do not:

- claim that the implementation is correct;
- approve product, API, security, or permission behavior;
- replace executable validation;
- turn potential concerns into formal code-review findings;
- treat a plan, PR description, test name, or existing code as authority.

Formal correctness, authority compliance, severity assignment, and actionable
findings belong to `code-review`.

## Resolve the target

Determine the review target from the user's request.

- No target:
  - inspect `git status --short`;
  - inspect staged changes;
  - inspect unstaged changes;
  - inspect relevant untracked files;
  - exclude ignored and generated files unless they affect the implementation.
- Commit: inspect `git show <commit>` and relevant parent context.
- Revision range: inspect `git diff <from>..<to>`.
- Branch: inspect `git diff <branch>...HEAD`.
- PR: retrieve its description, commits, and diff using available repository
  tools.

Record additions, modifications, deletions, renames, tests, generated or
mechanical files, dependency and configuration changes, migrations, and
schemas.

Inspect complete consequential files rather than relying only on diff hunks.

For deleted files, inspect the deleted diff or the previous revision when
needed to explain removed behavior and compatibility impact.

Do not silently expand a bounded diff walkthrough into a repository-wide
architecture audit.

## Establish the evidence boundary

Before explaining the implementation, distinguish the kinds of information
being used.

Use these evidence categories where the distinction matters:

- **Authority**: accepted product, API, security, permission, protocol, or
  architecture requirements.
- **Observed**: behavior or structure directly visible in the inspected code,
  diff, schema, configuration, or tests.
- **Claimed**: statements made by a plan, PR description, commit message, or
  previous validation record.
- **Inference**: a likely runtime consequence derived from observed code but not
  independently executed.
- **Verified now**: evidence established by a command or scenario executed
  during the current walkthrough.
- **Unverified**: behavior that depends on runtime configuration, deployment,
  external systems, database topology, framework wiring, or commands not run
  during the walkthrough.

Do not present an inference or a claim as verified behavior.

Use cautious wording:

- “The implementation appears to route…”
- “The code configures…”
- “The related tests cover…”
- “The plan claims…”
- “This walkthrough did not independently verify…”
- “Runtime behavior still depends on…”

Avoid unsupported conclusions such as:

- “This is transactional.”
- “The files are private.”
- “The permission is enforced.”
- “The migration is safe.”
- “The implementation satisfies the requirement.”

Instead, identify the mechanism observed in code and state what remains
unverified.

## Resolve plans and authority references

A plan is optional navigation context.

If the user supplies a plan, use it when it relates to the selected target.

Otherwise, inspect `docs/plans/active/` only when a plan would materially help
explain a large or multi-stage implementation. Ignore
`docs/plans/active/README.md`.

Rank candidate plans by:

- branch name;
- commit messages;
- changed paths;
- referenced symbols;
- milestones;
- stated scope.

If exactly one plan clearly matches, use it as navigation context and state
which plan was used. Do not stop to request confirmation.

If multiple plans are plausible, mention the ambiguity and continue without
assuming that any one plan governs the implementation.

If no relevant plan exists, continue with a planless walkthrough. Do not ask
the user to provide a plan unless the user explicitly requested
plan-to-implementation traceability.

Do not silently use completed or unrelated plans.

Plans describe intended execution. They do not automatically establish product,
API, security, permission, or architecture authority.

Read repository instructions and accepted authority needed to explain
externally observable contracts.

Do not perform a formal authority-compliance review. When observed behavior
appears inconsistent with accepted authority, record it as a **potential
mismatch** and hand it off to `code-review`.

If accepted authority sources appear to conflict, do not choose a winner during
the walkthrough. Record an unresolved authority conflict, name both sources,
and hand the decision to `code-review` or the responsible authority owner.

## Build the implementation map

Use CodeGraph when the repository has it and the tool is available, after
reading the repository's CodeGraph instructions.

Use it to discover candidate entry points, callers, callees, consumers,
interfaces, schemas, handlers, and affected tests.

Read consequential source files directly.

Treat CodeGraph as navigation evidence only, not runtime or permission proof,
complete impact analysis, deployment proof, or product authority.

Inspect framework wiring that may not appear as ordinary calls, including:

- dependency injection;
- decorators;
- guards and interceptors;
- dynamic modules;
- events;
- queues;
- templates;
- configuration-based registration;
- generated clients;
- schema registration.

Group changes in this order of preference:

1. User-visible behavior or use case.
2. Runtime call path.
3. Externally observable contract.
4. Domain responsibility.
5. Plan milestone or acceptance criterion.
6. File location.

Do not use primary groups such as “controllers”, “services”, “repositories”,
and “tests” when those files jointly implement one behavior.

Classify files as:

- must-read;
- supporting;
- proof-read;
- skim;
- generated or mechanical.

Do not automatically omit:

- migrations;
- security configuration;
- dependency-lock changes;
- generated contracts with meaningful changes;
- deleted behavior;
- compatibility adapters.

## Investigation budget

Default to no more than seven primary behavior groups, fifteen consequential
source files read deeply, ten supporting or proof files inspected selectively,
and one primary runtime path before secondary paths.

If the change exceeds this budget, provide a phased walkthrough:

1. Primary behavior and contracts.
2. Persistence and integration.
3. Compatibility, deployment, and proof.

State what was not inspected. Do not imply complete coverage.

## Produce the walkthrough

Default to a response in chat.

Write an artifact under `docs/reviews/` only when the user explicitly asks for
a saved document.

Begin with this boundary or an equivalent statement:

> This walkthrough explains the observed implementation and proposes a review
> order. It does not establish correctness and does not replace accepted
> product, API, security, permission, or architecture authority.

Use repository-relative paths by default.

Include symbols or line references where available.

Avoid absolute workstation paths unless the active environment requires them
to create clickable editor links.

## Default output structure

1. Evidence boundary.
2. Three-minute overview.
3. Recommended review order.
4. Guided behavior groups.
5. Reference-to-implementation trace.
6. Potential mismatches and unknowns.
7. Validation evidence.
8. Review handoff.

## Three-minute overview

Keep the three-minute overview genuinely compact.

Default limits:

- one short executive summary;
- one primary diagram;
- five must-read files;
- five major behavior groups;
- five top risks, potential mismatches, or unknowns.

The overview should answer:

1. What changed?
2. What previous behavior was replaced or retained?
3. What is the main runtime flow?
4. Which files should be read first?
5. Which contracts or deployment assumptions deserve the most attention?
6. What has not been independently verified?

Place detailed inventories and secondary files in later sections.

## Recommended review order

Separate files into:

### Must-read

Files that establish the primary behavior, externally observable contract,
or orchestration.

### Supporting

Repositories, adapters, helpers, module wiring, configuration, and secondary
runtime paths needed to understand the main behavior.

### Proof-read

Tests, fixtures, migration verification, and executable evidence related to
important claims.

The presence of a test file is not proof that the test passes or covers the
claimed behavior.

### Skim

Mechanical DTOs, straightforward mappings, lockfiles, or deleted diff that
should be checked for scope and compatibility but does not require deep reading.

### Generated or mechanical

Files that are mostly generated or mechanically changed. Call out meaningful
contract changes even when they occur in generated output.

## Guided behavior groups

For each logical group, explain:

1. **Purpose**
   What capability or runtime responsibility the group introduces, replaces,
   or removes.
2. **Observed entry point**
   The route, handler, command, event, scheduler, or public method that starts
   the flow.
3. **Observed flow**
   The main calls, transformations, persistence operations, and outputs visible
   in the implementation.
4. **Relevant contract**
   Product, API, schema, security, permission, compatibility, or deployment
   behavior affected by the group.
5. **Evidence**
   Source files and tests related to the behavior.
6. **Unverified assumptions**
   Runtime, environment, framework, topology, or deployment behavior not
   established during the walkthrough.
7. **Manual review focus**
   What the developer or formal reviewer should inspect carefully.

Do not assign severity or prescribe a required correction. Those belong to
`code-review`.

## Runtime and deployment claims

Be especially cautious with claims involving:

- transactions;
- authentication and authorization enforcement;
- tenant isolation;
- private or public storage;
- event delivery;
- retries;
- concurrency;
- rollback;
- filesystem containment;
- database indexes;
- production configuration;
- deployment order;
- compatibility with existing clients.

For example, prefer:
> The service opens a Mongo session and passes it to repository writes.
over:
> Publish is transactional.

Prefer:
> Blob paths are derived from SHA-256 under the configured blob root.
over:
> Blobs cannot be served publicly.

Then state what environment or integration evidence would be needed to verify
the stronger claim.

## Reference-to-implementation trace

When a relevant plan, claim, existing test, or accepted authority is available,
include a compact matrix.

Use this shape:

| Reference type | Criterion or claim | Observed implementation | Evidence located | Walkthrough status |
| -------------- | ------------------ | ----------------------- | ---------------- | ------------------ |

Label every row as `Authority`, `Plan`, `PR claim`, `Existing test`, or
`Other reference`. Never present a plan or PR claim as accepted authority.

Use only these walkthrough statuses:

- `Observed`
- `Partially observed`
- `Potential mismatch`
- `Not located`
- `Not independently verified`
- `Not applicable`

### Status definitions

- **Observed**: the mechanism is visible; correctness is not established.
- **Partially observed**: only part of the mechanism or runtime path is visible.
- **Potential mismatch**: observed behavior appears inconsistent with accepted
  authority; send it to `code-review` for formal assessment.
- **Not located**: no corresponding mechanism was found in the inspected scope;
  do not extrapolate this to the whole repository.
- **Not independently verified**: code or existing evidence suggests the
  behavior, but required validation was not executed.
- **Not applicable**: the reference does not apply to the selected change.

Do not use compliance conclusions such as:

- `Satisfied`
- `Contradicted`
- `Pass`
- `Fail`
- `Correct`
- `Approved`

Those belong to formal review and validation.

## Potential mismatches and unknowns

Include this section whenever any externally observable behavior, compatibility
choice, or runtime assumption remains unclear.

Examples include:

- implementation fallback differs from an accepted product policy;
- publish and revoke notify clients differently;
- an old client or endpoint is removed without visible migration handling;
- a transaction is configured but production topology has not been verified;
- a private storage assumption depends on deployment configuration;
- permission metadata exists but enforcement wiring has not been traced;
- event delivery is best-effort and clients require a recovery path;
- a schema or API change may require ordered deployment;
- an implementation defaults to behavior not explicitly authorized.

Write each item using this structure:

```text
Observed:
What the inspected implementation appears to do.

Authority or expectation:
The relevant accepted requirement, when available.

Why it needs review:
The ambiguity, potential mismatch, or external dependency.

Required next check:
The file, authority source, test, runtime scenario, or deployment evidence
needed to resolve it.
```

Do not assign severity in this section.

Do not state that the implementation violates authority unless `code-review`
has performed the authority-compliance assessment.

## Validation evidence

Distinguish clearly between:

### Verified now
Record each command or scenario executed during the current walkthrough with
its exact command, exit code, scope, and relevant result. Explicitly identify
important validation that the command did not exercise.

### Existing evidence observed
Test files, previous command output, plan records, CI references, or PR claims
that were inspected but not reproduced.

### Validation still required
Commands or scenarios needed to establish important behavior.

Never treat the following as current proof:

- a test file existing;
- a test name matching the requirement;
- a plan checkbox;
- a previous session claiming success;
- code that appears correct;
- static graph navigation alone.

If only `git diff --check` was run, state exactly that. Do not imply that build,
type-check, unit tests, integration tests, or runtime behavior were verified.

## Diagrams

Use Mermaid only when it materially clarifies:

- the primary runtime flow;
- before-and-after architecture;
- important deployment or compatibility sequencing.

Do not add diagrams merely to decorate the response.

Default to no more than:

- one diagram in the three-minute overview;
- two additional diagrams in the detailed walkthrough.

Diagram labels should describe runtime responsibilities rather than only class
names.

## Review handoff

End with a concise handoff appropriate to the observed evidence.

Typical handoff:

1. Read the implementation in the proposed order.
2. Send potential mismatches and high-risk paths to `code-review`.
3. Run fresh executable validation for the affected service or application.

Do not claim that the implementation is complete or correct.

Do not modify code while producing the walkthrough unless the user separately
requests implementation work.
