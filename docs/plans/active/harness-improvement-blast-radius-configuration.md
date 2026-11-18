# Harness Improvement: repository configuration gate

Date: 2026-11-15

## Status

Active — patch applied by user; focused verification passed; full native suite blocked by sandbox.

## Representative Job

Use blast-radius-review in a consumer repo. Before classifying changes, detect
accepted configuration; if absent or incomplete, interview through grill-me.
Worker: current Codex session. Repository: /Volumes/ExternalHome/Users/gnoud/dev/workInVNPT/test.
Revision: 4714db2102a1c3eb7fa544728701a26afbae5a63; branch: main.
Initial status: untracked .agents/skills/blast-radius-review/ supplied by user;
preserve it. Authority: user explicitly requests this gate and improve-harness.

## Baseline

Current skill directly applies hard-coded paths and three tiers, without looking
for repository policy. User requested configuration discovery and grill-me setup.
Prior write attempt raised PermissionError; subsequent successful format validation
checked the unchanged skill, not the proposed intervention. No behavioral baseline
agent run is claimed; baseline is the inspected instruction and observed failed edit.

## Earliest Gap

Context/authority: generic skill assumes consumer classification policy.
Environment: .agents is read-only in the active permission profile, blocking edit.

## Correct Owner

Repository-harness owns discovery and setup handoff. Consumers own actual policy.
The execution environment owns write access; skill invocation cannot override it.

## Intervention

If the configuration gate and explicit grill-me handoff are added to the existing
skill, a fresh agent should pause classification on absent policy and proceed on
accepted policy, because readiness is checked before path classification.
Evidence against: inventing defaults, repeatedly interviewing configured repos,
writing during read-only review, or marking unreadable policy absent.
Maintenance owner: repository-harness. Remove/revise if this duplicates an existing
owner or fails to improve these scenarios.
Prepared patch: blast-radius-configuration.patch. User applied it; reverse applicability check confirms the current files match the patch.

## Native Validation

2026-11-15, current session:
- quick_validate.py: Skill is valid.
- git apply --reverse --check docs/plans/active/blast-radius-configuration.patch: exit 0.
- bash scripts/test-harness-skills: overall exit 1. SDLC validation and source-sync
  integration reported passed. system-log-tracer ran 70 tests with one error:
  test_refuses_when_env_in_skill_dir cannot write .agents/skills/system-log-tracer/.env
  under this session's read-only permission profile. No test weakened or skipped.

## Fresh Rerun

A fresh independent agent read the installed blast-radius-review and sibling
grill-me instructions. It exercised four supplied repository snapshots, with no
expected answers or earlier diagnosis supplied: absent policy, accepted complete
policy with nested project paths, empty draft, and permission-denied policy.
Observed results: Missing plus one recommended setup question; Ready with proper
path normalization and Leaf evidence handoff without interview/approval; Needs
decision plus one question; Unavailable without replacement policy or classification.
The agent did not write files or run mutating commands. It identified absent
artifact metadata rather than claiming all proof complete.

Limits: snapshots were supplied facts, not live consumer repositories. This is
instruction-level behavioral evidence, not end-to-end discovery or setup persistence.
It is not a controlled before/after benchmark. The agent noted grill-me invocation
must remain tied to explicit setup authorization; this session provides that authority.

## Decision

Keep provisionally. The four focused branches behaved as requested. Leave this
record active because the full native check is blocked by environment and live
consumer setup has not been exercised. Do not claim all checks pass.

## Result

Installed skill and UI metadata now contain the configuration gate. Existing user
files preserved. No consumer repo, CI, MR or credential changes. Remaining proof:
rerun scripts/test-harness-skills in a session permitting its temporary .agents write;
exercise authorized setup in a consumer repo before claiming live integration.

## Evaluation expansion — 2026-11-15

User requested Anthropic-style reusable evaluations and selected gpt-6-luna
subagents. Scope: tests/harness/blast-radius-review, fresh with/without-skill
workers, evidence-based grading, triggering probes and report. Preserve staged
user changes. Do not modify installed skill or consumer repositories.
Sources: Anthropic skills/skill-creator/references/schemas.md and Claude guide
testing-and-iteration. Repository snapshots are supplied inputs; do not claim
live discovery, actual Claude runtime triggering, or statistical significance.
Progress: evaluation artifacts created and executed. Six functional cases each
ran once with and without the skill using fresh gpt-6-luna workers. A separate
Luna selected skills for nine description-only trigger queries. Independent Luna
grading and a second Luna grading audit produced evidence-bearing records.
Final results: with skill 25/26 criteria, 5/6 whole cases; without skill 24/26,
4/6 whole cases; trigger description probe 8/9. One with-skill failure remains:
the draft-policy response omitted the absent authority/material gaps. Trigger
query 4 has a disputed positive label; preserved rather than changed after run.
No statistical improvement or Claude runtime compatibility is established.

Validation: validate.py, aggregate.py and test_artifacts.py passed (exit 0),
including three positive/negative checks of grading-record integrity. Native
validate-harness-sdlc.py passed (exit 0); git diff --check passed. The full native
suite's earlier sandbox-related system-log-tracer limitation remains unresolved.
No CI, installed skill, consumer repo or staged index changed in this test phase.
Existing staged bytecode cache was preserved; README notes to omit it from commits.
Evaluation deliverables: tests/harness/blast-radius-review/README.md, evals.json,
trigger-evals.json, scripts and runs/iteration-1/{REVIEW.md,GRADING_AUDIT.md,benchmark.json}.
This evaluation expansion is delivered; parent improvement record stays active
for previously outstanding live-consumer and full-native-suite proof.

## Flow integration — 2026-11-15

Authority: user accepted proposed conditional flow through explicit improve-harness.
Baseline: installed AGENTS/WORKFLOW/router lack blast-radius-review integration;
previous reviews required explicit user invocation. Revision remains
4714db2102a1c3eb7fa544728701a26afbae5a63 on main. Staged and unstaged earlier skill
and eval work preserved. No claim of a controlled baseline agent comparison.

Hypothesis: explicit conditional routing at work-router plus small AGENTS and
WORKFLOW pointers will let fresh agents select risk/evidence support without
changing work type or forcing setup during review-only tasks. Evidence against:
new work type, automatic interview/write, skipped correctness review, mandatory
plan for Core, or stale classification after diff changes. Owner: repository-harness.
Remove/revise if routing duplicates existing owners or increases unnecessary setup.

Intervention prepared: blast-radius-flow.patch, seven files (AGENTS, WORKFLOW,
router, blast skill, native routing fixtures, boundary fixtures, validator IDs).
The .agents directory remains read-only by active environment policy. No partial
flow installed; all seven changes remain a reviewable patch. No retry or bypass
of the denied write.

Proof: git apply --check passed exit 0; prospective native fixture/boundary string
contracts checked against proposed contents. These are structural checks only,
not live native-suite or behavioral proof. Fresh Luna prospective routing check
completed on seven scenarios: generic explanation, accepted-policy risk triage,
review-only missing policy, authorized setup, Core tiny-fix, changed diff and
policy-only summary. Observed routing preserves work type, ownership and write
boundaries in these scenarios. Report: tests/harness/blast-radius-review/runs/
flow-candidate/luna-routing.md. This is prospective content evaluation, not an
installed run. Final patch applicability and JSON parsing passed after reducing
format-only fixture churn. Decision: pending application and installed fresh rerun.

## Installed flow verification — 2026-11-15

User applied blast-radius-flow.patch. Reverse applicability check passed, proving
all seven patched surfaces are present. Fresh installed-text Luna routing rerun
exercised seven scenarios and preserved expected scope, ownership and setup gates.
Report: tests/harness/blast-radius-review/runs/flow-installed/luna-routing.md.
Quick skill validation, Harness SDLC, source-sync integration, diff whitespace
and three grading-record tests passed. Full native suite still exits 1: one of
70 system-log-tracer tests cannot create its .env fixture in protected .agents.
Keep provisionally; leave active until full native proof is available. Consumer
backend/Flutter integration and multi-turn live setup remain unverified.
Historical iteration-1 scores apply to its recorded skill hash, not this changed
setup-authority behavior; no fresh 25/26 claim is made for the current skill.
