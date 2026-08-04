---
name: diagnosing-bugs
description: Diagnose bugs, failing tests, build failures, runtime failures, and performance regressions with an evidence-driven root-cause workflow before applying a minimal fix. Use after work-router classifies a concrete failure as read-only analysis, a bug-related tiny fix, or a bounded change; preserve read-only scope when the user has not authorized changes.
---

# Diagnosing Bugs

Separate the observed symptom from the causal defect. Read `AGENTS.md`,
`docs/WORKFLOW.md`, relevant authority, affected code, and existing tests before
changing behavior.

For an obvious deterministic defect, compress phases without silently skipping
the evidence chain. Still show a fresh reproduction, direct evidence proving
the causal line, the minimal authorized fix, and fresh regression validation.
Combine minimisation and hypothesis testing only when the direct evidence rules
out competing causes.

## Workflow

### 1. Reproduce

Create the smallest fresh command or runtime interaction that exercises the
reported symptom. Confirm it fails in the way the user described. For flaky or
performance failures, establish a measurable reproduction rate or baseline.

If the environment cannot reproduce the issue, record what was attempted and
request the smallest missing artifact or access: exact input, logs, HAR, dump,
screen recording with timestamps, or permission for targeted instrumentation.
Do not guess a root cause from an unverified symptom.

### 2. Collect evidence

Capture the exact error, output, state transition, timing, request, or log
boundary. Trace the relevant path from input to failure. Distinguish:

- **symptom:** what the caller or user observes;
- **trigger:** the condition that exposes it;
- **root cause:** the earliest incorrect assumption, state, or operation that
  makes the symptom inevitable.

For code-structure failures, an available and current CodeGraph index may help
locate entry points, callers, callees, and candidate affected paths. Verify
those relationships against current source and runtime evidence. A graph result
is a hypothesis aid, not proof of the root cause or a complete dependency set;
static analysis may miss dynamic dispatch, dependency injection, reflection,
generated code, templates, events, and external integrations.

### 3. Minimise

Remove inputs, callers, configuration, data, and steps one at a time, rerunning
the reproduction after each change. Keep only elements required for the
failure. Use the minimal case as the candidate regression scenario.

### 4. Form hypotheses

Create a short ranked list of falsifiable hypotheses. For each, state the
prediction that would be observed if it were true. Prefer hypotheses supported
by the collected evidence; do not patch the first plausible explanation.

### 5. Test hypotheses

Test one variable at a time with the narrowest probe. Prefer debugger or direct
inspection, then targeted uniquely tagged instrumentation. For performance,
measure or profile instead of adding broad logs. Reject hypotheses whose
predictions do not hold.

### 6. Identify root cause

State the complete causal chain from trigger to symptom and cite the evidence
that distinguishes it from rejected hypotheses. Do not confuse the final throw,
bad render, fallback, or timeout with the earlier cause.

### 7. Implement the minimal fix

Only when changes are authorized, correct the root cause at the narrowest
responsible boundary. Do not broaden scope, rewrite adjacent code, weaken an
assertion, swallow an error, or add a fallback merely to hide the symptom.

### 8. Add regression validation

When a valuable automated seam exists, use `tdd` to turn the minimal
reproduction into a failing behavioral test, apply the fix, and make it pass.
Then rerun the original reproduction and relevant broader checks. Remove all
temporary instrumentation and report any missing test seam as a limitation.

Use `verification-before-completion` before claiming the bug is fixed. Report
the reproduction command, root cause, changed files, regression proof, fresh
validation commands and exit codes, and untested surfaces.

## Constraints

- Keep diagnosis-only requests read-only.
- Do not create an active plan for a tiny fix.
- Do not create Harness CLI stories or sub-agents.
- Do not treat story state, old logs, prior test output, or implementer
  confidence as proof.
