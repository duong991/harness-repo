# Execution Plan: SDLC Harness Maintenance and Skill Expansion

Date: 2026-08-11

## Status

Blocked — the managed `prototype` discipline and local-source consumer
migration are complete; only the matching immutable-artifact release gate
remains.

## Outcome

The Repository Harness owns and safely distributes its core workflow suite plus
reusable supporting disciplines adapted from `mattpocock/skills`, without
introducing a second router, documentation hierarchy, or Git authority.

## Context

- `AGENTS.md` is the repository entry gate.
- `docs/WORKFLOW.md` owns general workflow principles.
- `.agents/skills/work-router/SKILL.md` owns work-type taxonomy and routing.
- `.harness-core/manifest.json` and `.harness-core/base/` define the updater's
  three-way-update baseline.

## Scope

In scope:

- Add `writing-for-agents`, `handoff`, `codebase-design`, `domain-modeling`,
  and `resolving-merge-conflicts` with immutable upstream provenance.
- Preserve `work-router` as the sole six-work-type router and add only
  downstream-discipline triggers.
- Snapshot the complete managed skill trees, validator, and fixtures in the
  updater baseline with manifest hashes.
- Expand contract and updater-safety regression coverage.
- Provide a guarded local-source migration path for legacy consumer repositories
  until the matching immutable artifact is published.
- Add `prototype` as a generic UI/logic exploration discipline with optional
  backend-implication extraction, without making UI an API authority.

Out of scope:

- Creating a second routing, planning, ADR, or orchestration hierarchy.
- Changing the pinned source commit `84fdeffd12f2ee307994d1eb6feb48173b6e0502`.
- Publishing an immutable updater artifact from this consumer checkout.

## Approach

1. Establish the clean baseline and inspect the pinned local upstream source.
2. Adapt the five skills to Harness authority, invocation, and Git-safety
   conventions.
3. Add routing triggers, provenance inventory, managed updater assets, and
   fixture-driven contracts.
4. Snapshot all changed managed paths atomically and run focused validation.
5. Add and prove a source-to-consumer migration script, then apply it to the
   authorized legacy consumer after a reviewed dry-run.
6. Import and adapt `prototype`, add its constrained router trigger and
   contract fixtures, then snapshot its complete tree into the updater base.

## Risks And Recovery

- A stale manifest hash would make the updater reject its own base. Mitigate by
  validating every managed path and hash; recovery is to restore the prior
  manifest/base pair together.
- Imported upstream behavior could widen routing, orchestration, documentation,
  or Git authority. Mitigate with explicit local contracts and boundary cases.
- A legacy consumer can have managed skills outside its old manifest. Mitigate
  with conflict reporting by default and recoverable backups before explicit
  adoption/overwrite.
- A prototype could be mistaken for production code or infer backend API shape
  from a UI. Mitigate with explicit promote/remove, capability-scope, and
  backend-implication boundaries plus negative contract cases.

## Progress

- [x] Confirm clean baseline and pinned source commit.
- [x] Add and adapt the five supporting disciplines.
- [x] Update router, documentation, validator, fixtures, and updater baseline.
- [x] Run local validation and inspect all consequential diffs.
- [x] Separate consumer customization validation from pristine release-baseline validation.
- [x] Add and prove a guarded local-source migration path for legacy consumers.
- [x] Migrate the authorized `safekid-backend` consumer and record verification.
- [x] Add, integrate, and validate the generic `prototype` supporting discipline.
- [ ] Publish a matching immutable updater artifact and prove an isolated upgrade.

## Decisions

- 2026-08-11: The five imported skills are supporting disciplines, not work
  types; `work-router` remains the sole workflow selector.
- 2026-08-11: `handoff` remains explicit-only and its output is continuation
  context, not durable project authority.
- 2026-08-11: An immutable release requires a matching artifact; this checkout
  must not claim an unpublished manifest version as distributable.
- 2026-08-11: Consumer validation permits local managed-file customizations;
  release qualification alone requires `LIVE == BASE`.
- 2026-08-11: The developer-local bridge requires explicit `--adopt-legacy` for
  unmanaged legacy paths and explicit `--replace-conflict PATH` for a tracked
  three-way conflict; each applied migration retains a timestamped backup.
- 2026-08-11: `prototype` is a supporting exploration discipline. Task scope
  outranks repository classification; UI evidence produces only backend
  implications, with domain and interface design delegated downstream.

## Validation

- Focused proof: `./scripts/test-harness-skills` and
  `python3 scripts/validate-harness-sdlc.py`.
- Integration or end-to-end proof: `scripts/bin/harness doctor` and a future
  isolated `harness update` from the published artifact.
- Repository-required checks: `git diff --check`, manifest/base hash integrity,
  and `--release-baseline` live/base equality before packaging.

## Result

The original local implementation is complete: the five supporting disciplines are installed
with the pinned upstream provenance and Harness adaptations; `work-router`
retains its six work types and only adds downstream triggers; the validator,
fixtures, base snapshots, and manifest now cover all 13 managed skills plus the
five managed validation assets.

Consumer validation permits a managed-file customization while preserving the
base snapshot as the updater's three-way reference. Pristine equality is now a
separate release-only check; fixture proof is explicitly a three-way merge
contract model, not updater end-to-end proof.

Fresh local proof passed on 2026-08-11:

- `./scripts/test-harness-skills` (exit 0)
- `./scripts/test-harness-skills --release-baseline` (exit 0)
- `python3 scripts/validate-harness-sdlc.py` (exit 0)
- `scripts/bin/harness doctor` (exit 0)
- `git diff --check` (exit 0)

Focused regression probes confirmed that a temporary managed-file consumer
customization passes default validation and fails strict release validation,
and that a non-executable managed `scripts/test-harness-skills` is rejected.

The local-source bridge is implemented in `scripts/sync-harness-source.py` and
has an integration contract at `tests/harness/test-sync-harness-source.py`.
It validates the source against the pristine release baseline, dry-runs before
writing by default, three-way-merges manifest-tracked files, blocks legacy or
overlapping paths unless explicitly authorized, and writes recoverable backups
without staging or committing.

On 2026-08-11 it migrated the authorized
`/Volumes/ExternalHome/Users/gnoud/dev/workInVNPT/safekid-microservice/safekid-backend`
consumer from 19 to 75 managed files. Its current-tree contract test and
`scripts/bin/harness doctor` both exited 0; backups are under its
`.harness-core/source-sync-backups/`. The old installed `harness 0.1.7`
artifact still reports the consumer's local `docs/README.md` overlap during its
own `update --dry-run`; that artifact does not contain this unpublished
75-file source baseline, so this is the remaining artifact-release limitation,
not a bridge conflict.

The final release and isolated-consumer update gate remains blocked: this
checkout contains an installed `harness 0.1.7` updater but no release-artifact
source, publishing workflow, remote, or immutable next-version artifact. Do
not change the manifest version alone. Publish a matching artifact externally,
then run the dry-run and real isolated upgrade before moving this plan to
`docs/plans/completed/`.

On 2026-08-11, `prototype` was added as the 14th managed runtime/supporting
skill. Its UI, logic, backend-implications, provenance, and invocation-policy
files are manifest/base owned; the router adds only a constrained supporting
trigger. Routing fixtures cover UI exploration, backend-only logic exploration,
full-stack implication extraction, and settled design/API non-triggers. Boundary
fixtures prohibit new work types, language-only FE/BE inference, UI-to-API
authority, default findings documents, production promotion, and variant quotas.

Fresh proof for this addition passed:

- `./scripts/test-harness-skills --release-baseline` (exit 0)
- `python3 scripts/validate-harness-sdlc.py --require-pristine-baseline` (exit 0)
- `git diff --check` (exit 0)
- Safekid consumer `./scripts/test-harness-skills` and `scripts/bin/harness doctor` (exit 0)
- Safekid local-source bridge dry-run from 81 managed paths (exit 0)

The authorized Safekid consumer was migrated from 75 to 81 managed paths with
the six `prototype` files and matching baseline snapshots. Its recovery backup
is `.harness-core/source-sync-backups/20260811T061723Z`.
