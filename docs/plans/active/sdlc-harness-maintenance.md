# Execution Plan: SDLC Harness Maintenance

Date: 2026-08-11

## Status

Blocked

## Outcome

The Harness core updater owns the complete workflow-skill suite, routing policy
has one canonical owner, and clean checkouts can execute checks that protect
the resulting SDLC contract.

## Context

- `AGENTS.md` is the repository entry gate.
- `docs/WORKFLOW.md` owns general workflow principles.
- `.agents/skills/work-router/SKILL.md` owns work-type taxonomy and routing.
- `.harness-core/manifest.json` and `.harness-core/base/` define the updater's
  three-way-update baseline.

## Scope

In scope:

- Register and snapshot all eight workflow skills in Harness core state.
- Remove duplicated routing taxonomy from `AGENTS.md` and keep only invariants
  and pointers there.
- Add executable harness-contract validation.
- Move walkthrough branch-specific material into references and clarify its
  critical-path exception.

Out of scope:

- Redesigning the workflow-skill architecture.
- Changing external skill provenance or upstream pins.
- Replacing or redistributing the local Harness binaries.

## Approach

1. Make the updater baseline exhaustive and synchronize its manifest hashes.
2. Align entry-point and explanatory documentation with single-source ownership.
3. Add fixture-driven validation for routing, boundaries, and managed-state
   integrity.
4. Run focused checks, inspect the resulting diff, and record evidence.

## Risks And Recovery

- A stale manifest hash would make the updater reject its own base. Mitigate by
  validating every managed path and hash; recovery is to restore the prior
  manifest/base pair together.
- Over-pruning the walkthrough could remove needed instructions. Keep its core
  phases and move only branch-specific detail into an explicitly linked
  reference.

## Progress

- [x] Snapshot the full workflow-skill suite in local updater state.
- [x] Consolidate routing ownership and documentation.
- [x] Add reproducible contract checks.
- [ ] Publish and verify an updater artifact that owns the same skill suite.

## Decisions

- 2026-08-11: Keep one `.harness-core/manifest.json` rather than introducing a
  second state tree, because the current updater already supports a generic
  file baseline and this keeps one atomic update unit.
- 2026-08-11: Keep the local core at release identity `0.1.7`; publishing this
  baseline as `0.1.8` requires a matching updater binary, which is outside this
  repository-only SDLC change.

## Validation

- Focused proof: `python3 scripts/validate-harness-sdlc.py`.
- Integration or end-to-end proof: `scripts/bin/harness doctor`.
- Repository-required checks: `git diff --check`.

## Result

Local SDLC contract work is complete: all eight workflow skills have complete
base snapshots and manifest hashes, routing ownership is consolidated, and
`scripts/test-harness-skills` validates routing, boundaries, ownership, and a
non-conflicting three-way merge.

The durable updater outcome is blocked externally. `scripts/bin/harness update
--dry-run` targets core `0.1.8`, whose artifact does not contain the eight-skill
suite and therefore previews their deletion. Before distributing this work or
moving this plan to `completed/`, publish a matching immutable core artifact
with this manifest/base pair, then rerun the dry-run and confirm no
Harness-managed skill is deleted.
