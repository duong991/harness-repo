# Execution Plan: gnoud-bootstrap-product skill

Date: 2026-08-04

## Status

Completed

## Outcome

Create and validate a local, reusable Codex skill named `gnoud-bootstrap-product`
that routes work from a blank repository through product clarification,
authority artifacts, scaffold, first vertical slice, review, and validation
using guarded execution.

## Context

- User-provided workflow: `/Volumes/ExternalHome/Users/gnoud/.codex/attachments/47a5f947-66b8-4963-b51a-f2f9d17510b7/pasted-text.txt`
- Repository workflow: `AGENTS.md` and `docs/WORKFLOW.md`
- Skill creation authority: `/Volumes/ExternalHome/Users/gnoud/.codex/skills/.system/skill-creator/SKILL.md`
- Target local skill directory: `.agents/skills/gnoud-bootstrap-product/`

## Scope

In scope:

- Initialize the skill with the standard skill-creator script.
- Write a concise router and guarded-execution contract in `SKILL.md`.
- Add a directly linked reference catalog for the phase prompts and output contracts.
- Generate UI metadata and run the standard validator.
- Forward-test the skill's routing behavior on a representative blank-repository request if feasible.

Out of scope:

- Installing the skill into the global Codex skill directory.
- Adding Harness CLI or other tool dependencies.
- Changing application code or repository product behavior.
- Creating separate skills for individual workflow phases.

## Approach

1. Initialize the local skill with `references/` only and deterministic UI metadata.
2. Replace the generated template with a concise router, safety boundary, and execution protocol.
3. Preserve the detailed user workflow as a progressive-disclosure reference.
4. Validate frontmatter, naming, metadata, and reference links.
5. Forward-test or manually inspect routing examples, then record limitations.

## Risks And Recovery

- Risk: the skill becomes a long prompt dump and is not reusable. Mitigation: keep routing rules in `SKILL.md` and move phase-specific prompts to one reference.
- Risk: the skill accidentally treats Harness CLI as mandatory. Mitigation: make CLI conditional and explicitly preserve repository workflow authority.
- Recovery: remove the new skill directory and leave the plan active if validation exposes a design defect; do not touch unrelated worktree changes.

## Progress

- [x] Initialize skill skeleton.
- [x] Write `SKILL.md` and reference catalog.
- [x] Validate skill structure and metadata.
- [x] Forward-test routing behavior.
- [x] Record result and move plan to completed.

## Decisions

- 2026-08-04: Use one router skill rather than a collection of phase-specific skills, because the supplied workflow has one lifecycle and a central routing decision.
- 2026-08-04: Use guarded execution: inspect and route automatically, but stop for materially different product or architecture decisions before edits.
- 2026-08-04: Create the skill locally under `.agents/skills/` before any global installation.

## Validation

- Focused proof: `quick_validate.py` was attempted but could not import `yaml`; equivalent checks passed for frontmatter fields, naming rules, description limits, reference links, and UI metadata YAML.
- Integration or end-to-end proof: isolated read-only Codex forward-test correctly selected bootstrap survey → product grill, avoided a new plan and CLI, and emitted exactly one recommended next question.
- Repository-required checks: `git diff --check` passed; final status contains only the new skill and this plan.

## Result

Created `.agents/skills/gnoud-bootstrap-product/` with a 133-line router and a
392-line progressive-disclosure workflow catalog. The skill is local-only,
explicitly invoked, guarded against premature edits and Harness CLI use, and
validated by manual structural checks plus a clean forward-test. The standard
validator should be rerun in an environment with PyYAML available.
