---
name: blast-radius-review
description: Check repository review configuration, prepare Core/Leaf risk classification and evidence, and hand formal review to code-review. When configuration is missing or incomplete, use grill-me to settle setup before classification.
---

# Blast Radius Review

Support the workflow selected by `work-router`. Keep review requests read-only.
Formal findings and approval belong to `code-review`; do not dispatch agents,
create orchestration, approve, merge, push, or alter CI from this skill.

## Check configuration before classification

1. Resolve the requested project directory and Git root separately. Use
   `git rev-parse --show-toplevel` and retain the project-relative prefix.
2. Read the target's `AGENTS.md` and `docs/WORKFLOW.md`. Follow their designated
   review-policy location; otherwise look for project-local
   `docs/review-policy.yaml`. Reuse an accepted equivalent in another format.
   Do not create a second source of policy or embed consumer paths in this skill.
3. Read the policy and its authority. Existence alone does not mean readiness.
   Check that it specifies:
   - accepted authority, project scope and the base for matching paths;
   - Core/Leaf rules, matching semantics, precedence, mixed changes, unknown
     paths, renames and semantic risk escalation;
   - required evidence/checks by affected area, execution directories and
     side effects, UI/runtime requirements and revision freshness;
   - Core safety answers, feature-flag applicability and recovery expectations;
   - review ownership and any existing PR/MR integration.
4. Report `Ready`, `Missing`, `Needs decision`, or `Unavailable` with the source
   and reason. Draft, conflicting or incomplete policy needs a decision. Name the absent
   authority and material missing rules; do not report only the draft label.
   An unreadable policy is Unavailable, not Missing; report the access blocker.
5. Ready proceeds without another interview; it means configuration readiness,
   not approval or readiness to merge. Missing or Needs decision follows the
   setup authorization gate below. Unavailable stops only policy-dependent
   claims. Independent technical inspection through code-review may continue.

## Setup through grill-me

For a review-only request without setup authorization, report the missing
policy/decisions and offer the interview; do not start it automatically. Continue
independent technical inspection if requested. When setup is explicitly requested
or the user accepts the handoff, resolve and read the target's `grill-me` skill, normally
`.agents/skills/grill-me/SKILL.md`. Explicit setup authorization
applies only to this interview and authorized setup scope; do not change grill-me's own
invocation policy. If the skill is unavailable, report the missing dependency
and ask the most important unresolved decision without claiming invocation.

Inspect repository facts before asking: structure, contracts, checks and MR
scripts. Never execute push/deployment/MR scripts just to discover capabilities.
Pass discovered facts and missing decisions to grill-me. Ask one question at a
time, recommend an answer with rationale, and wait. Settle only unknown policy:
Core/Leaf boundaries first, then mixed/unknown scope, evidence, review ownership,
and recovery exceptions. Examples and inferred defaults are proposals, not
accepted policy. Do not ask again for decisions already established by authority.

Finish with a user-confirmed setup brief and return control to work-router.
Grill-me itself does not implement setup. When the request authorizes setup,
the normal bounded-change workflow may save only the confirmed policy in the
repo-owned location and validate it. A review-only request remains read-only:
present the brief and obtain authorization before saving. Do not mark an unsaved
proposal Ready. If saving is blocked, report the blocker and stop dependent work.

Validate an authorized save by re-reading references and exercising known Core,
known Leaf, mixed, unknown, rename and nested-project/out-of-project examples
against the accepted rules. Re-run the configuration gate before continuing.
Installing hooks, changing CI and publishing PRs/MRs require separate scope.

## Classify and collect evidence

Resolve the requested base/head or explicit working-tree scope. Apply accepted
rules to all changed paths, including both sides of renames and deleted files.
Normalize Git-root paths to the policy's path base. Report out-of-project files;
do not discard them. Unknown scope returns to the relevant setup question,
never silently to Leaf. Apply the setup authorization gate before interviewing.
Inspect relevant contracts and consumers for impact. Reassess classification and
proof freshness whenever the reviewed diff changes; reuse existing walkthrough
context rather than generating another review decomposition.

Propose these requirements during setup; apply them only as accepted by the repo:

| Tier | Evidence |
| --- | --- |
| Leaf | Required CI checks; visual proof when UI changes |
| Core | Required CI checks; relevant runtime logs or integration tests; three safety answers; feature-flag declaration; visual proof when UI changes |

Core safety answers: what must remain unchanged; worst credible affected
users/data/services; how impact can be stopped and what cannot be rolled back.
Declare flag name, default and disable procedure, or an accepted not-applicable
reason and recovery approach. Disabling a flag does not undo changed data.

Bind evidence to the reviewed revision, command/scenario, environment, expected
and observed result, and artifact location. Separate available, missing and stale
proof. Inspect commands for mutations such as lint --fix before running them.
Local checks or another branch's pipeline do not prove current-revision CI pass.
Missing evidence allows source inspection but not a satisfied-gate claim.
Apply `verification-before-completion` to execution and completion claims.

## Hand off

Report configuration state/source, scope/base/head, risk and reasons,
available/missing/stale evidence, safety answers and unresolved decisions.
Hand context to `code-review`; no confidence-score approval. When a PR/MR draft
is requested, use the repository template and leave unobserved evidence explicit.
Drafting does not authorize publishing. Do not claim server merge enforcement
from local checks or workflow text alone.
