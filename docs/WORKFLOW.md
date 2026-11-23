# Repository Workflow

Canonical default workflow. Repository product behavior,
architecture, plans, decisions, code, tests, and runtime signals are the system
of record. Optimize for reliable agent execution with minimal human attention
and process overhead.

`work-router` owns the work-type taxonomy and selection rules. This document
owns the enduring workflow principles; skill-local behavior belongs to the
relevant skill, not a duplicate routing table.

## Repository Map

- `AGENTS.md`: small entry map and authority boundary.
- `README.md` and `docs/product/`: current product behavior.
- `docs/ARCHITECTURE.md` and `docs/decisions/`: structural constraints and
  lasting decisions.
- `docs/plans/active/`: complex work currently in progress.
- `docs/plans/completed/`: completed execution history worth retaining.
- Project code, tests, CI, and runtime signals: executable and observable truth.
- `scripts/README.md`: upstream Harness development and compatibility commands.

Use `docs/README.md` for the map; prefer targeted search.

## Select The Work Shape

Answer three questions independently; do not let one risk label decide them.

### Does The Work Need Durable Memory?

Use an ephemeral plan for bounded, single-session work.

Create or update one execution plan in `docs/plans/active/` when work:

- is likely to span sessions;
- coordinates multiple agents or contributors;
- has meaningful dependencies or an important sequence;
- requires an explicit recovery procedure; or
- would be unsafe or expensive to resume from the final diff alone.

Use `docs/templates/exec-plan.md`. Keep progress and task-local decisions in the
same file. Do not create parallel story, design, validation, and trace documents
for the same work unless one has independent long-term value.

### Does The Work Need Human Judgment?

Before editing, identify repository authority for each new externally
observable policy. If materially different choices remain open, stop before
edits and request the smallest necessary decision. Configurable defaults are
not authority.

For example, `Add rate limiting` without a quota, trusted key, enforcement
topology, or response contract must stop. `Enforce the documented 20 requests
per minute per authenticated tenant` may proceed.

Also pause when:

- product intent remains ambiguous;
- the action is irreversible or difficult to recover;
- validation, security, or compatibility requirements would be weakened; or
- the requested work does not authorize the necessary action.

### What Proves The Behavior?

Choose proof from the affected behavior:

- focused tests for local rules;
- integration tests for persistence and service boundaries;
- end-to-end interaction for user-visible behavior;
- recovery rehearsal for migrations and destructive operations; and
- runtime measurements for reliability or performance claims.

Harness rows, proof flags, trace tiers, context scores, and entropy scores do not
prove product behavior by themselves.

### Does The Work Encode An Invariant?

For architecture, reliability, security, or quality boundaries:

1. Find an accepted repository authority that states the required boundary.
   Conventions, code patterns, tests, defaults, and undocumented preferences do
   not establish policy. Stop when authority is absent or materially ambiguous.
2. Reuse the repository's native validation owner and command. Add the smallest
   mechanical check that covers the accepted scope and emits a diagnostic naming
   the violation, rule, and next action.
3. Require positive proof that allowed behavior passes and negative proof that
   the targeted forbidden behavior fails for the intended reason.
4. Report enforcement precisely: a local command is available or passed; a hook
   is optional developer convenience; CI either invokes the check or does not;
   branch protection is externally configured or unverified. Source or CI
   presence alone does not prove merge blocking.

Do not install hooks or change CI, merge, or branch-protection settings unless
separately authorized. Use the [invariant encoding pattern](patterns/encoding-invariants.md)
for the complete method.

## Task Flows

### Read-Only Request

For an answer, explanation, review, diagnosis, plan, or status report:

1. Read `AGENTS.md` and only the material needed for the response.
2. Use read-only inspection commands when useful.
3. Do not edit files or mutate Harness state.
4. Stop when concrete repository evidence supports the answer.

For test comprehension specifically:

1. Inspect the relevant production behavior and symbols.
2. Inspect test setup, action, assertions, negative assertions, and dependency
   behavior.
3. Produce a compact per-file test digest and one conclusion.
4. Stop without formal findings, adequacy judgment, severity, or approval.

Use `code-review` when the user asks whether tests are sufficient, correct,
safe, complete, or approvable. `code-review` may create the digest as context
before its formal adequacy review.

For large-change comprehension specifically:

1. Run `implementation-walkthrough` through `BASELINE → MAP → TRACE → PROBE →
   HANDOFF`.
2. Account for every consequential file in a behavior-based Review Unit or an
   explicit generated/mechanical/proof/skim classification.
3. Hand off formal questions to `code-review`; do not create findings or mutate
   git state in the walkthrough. Do not create a parallel review-planning or
   review-decomposition skill.

Discovery never grants authority to fix what it finds.

### Bounded Change

1. Restate the observable outcome.
2. Read the relevant product or design material, affected code, adjacent
   patterns, and existing tests.
3. Make the smallest coherent change that satisfies the outcome.
4. Run focused proof plus repository-required checks.
5. Report the outcome, important changed surfaces, proof, and known limitations.

No bootstrap, intake, story, matrix, trace, scoring, audit, or proposal command
is required.

### Durable Planned Change

1. Create or resume one plan in `docs/plans/active/`.
2. Record outcome, context, approach, risks, recovery, progress, decisions, and
   validation in that file.
3. Implement in coherent, independently verifiable groups.
4. Update progress and decisions as reality changes.
5. Run the plan's focused and repository-wide proof.
6. Promote lasting product or architecture decisions into `docs/decisions/`.
7. Record the final result and move the plan to `docs/plans/completed/`.

The plan is working memory, not a prediction frozen at intake. Update it when
evidence changes the approach.

### Operate The Application

When a task requires the real application:

1. Find the consumer-owned runbook and verify prerequisites and ownership.
2. Start only an isolated instance, prove readiness, and create known state.
3. Reproduce through the real interface and inspect correlated runtime evidence.
4. Validate through that interface, then stop only resources this run owns.

If no verified runbook exists, inspect current repository authority and report
or propose the missing guidance. Do not invent commands, credentials, product
policy, or cleanup obligations. The application-runbook template supplies
proposal structure, not proof that the application is operable.

### Improve The Harness

During ordinary work, report reusable agent friction without changing the
Harness for that new purpose. When the user explicitly invokes
`$improve-harness`, use `docs/templates/harness-improvement.md` to:

1. preserve the observed baseline and human intervention;
2. locate the earliest missing context, capability, owner, authority, proof, or
   environment boundary;
3. make the smallest authorized change at that owner;
4. run native proof and require a materially equivalent fresh-agent rerun; and
5. decide to keep, revise, or remove the intervention.

Do not claim improvement when the rerun did not retrieve or exercise the
intervention. Keep the record active while fresh-rerun evidence is pending.

## Completion Standard

A change is complete only when:

- the requested outcome exists or the blocker is explicit;
- relevant product and design truth remains current;
- behavior-appropriate proof has passed, or missing proof is disclosed without
  overstating completion;
- durable plan progress and result are current when a plan was required; and
- the final report separates verified facts, limitations, and unattempted work.

Git history, pull-request discussion, test artifacts, screenshots, videos,
logs, metrics, and plan progress are preferred evidence because they arise from
the work. Manual descriptions may add context but do not replace observed proof.
