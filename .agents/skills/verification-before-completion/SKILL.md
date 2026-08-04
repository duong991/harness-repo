---
name: verification-before-completion
description: Enforce fresh evidence before any claim that work is complete, fixed, passing, built successfully, or compliant with requirements. Use automatically and mandatorily before completion statements, commits, pull requests, handoffs, or moving a plan to completed; require current-session commands or runtime checks, exit codes, important results, and explicit untested surfaces.
---

# Verification Before Completion

Apply one rule: make no positive completion claim without fresh evidence that
proves that exact claim.

## Gate

Before saying work is fixed, complete, passing, successful, or requirements-
compliant:

1. **Identify the claim.** State precisely what must be true.
2. **Choose proof.** Select the command, runtime interaction, artifact check, or
   requirements checklist that observes that behavior.
3. **Run it fresh.** Execute the complete validation in the current session
   against the current worktree and environment.
4. **Read the result.** Check the full relevant output, exit code, failure count,
   and whether the command actually exercised the claimed behavior.
5. **Compare claim to evidence.** If evidence is weaker, narrow the claim. If
   validation fails or cannot run, report the actual partial or blocked state.
6. **Report the record.** Include the command/check, exit code, important result,
   and everything not tested.

## Match proof to the claim

| Claim | Required fresh evidence |
| --- | --- |
| Tests pass | The relevant test command exits 0 with no reported failures |
| Build succeeds | The production or requested build command exits 0 |
| Lint/typecheck clean | Each named lint/typecheck command exits 0 |
| Bug fixed | The original symptom no longer reproduces and regression proof passes |
| Requirement met | Each acceptance criterion maps to executable or observable evidence |
| Migration safe | Migration proof and the authorized recovery/rollback check succeed |
| Plan complete | Milestones, acceptance criteria, must-fix findings, and required checks all have evidence |

One proof does not silently prove another: lint is not a build, a unit test is
not an end-to-end flow, and a successful happy path does not prove error or
permission behavior.

## Evidence that is not sufficient

- story status, trace score, task database state, or a checked plan box;
- implementer self-assessment or another agent's success report;
- output from an earlier session or before the latest edit;
- a diff that merely looks correct;
- partial validation extrapolated to an untested surface;
- an assumption that a small patch cannot regress.

If validation is unavailable, do not workaround the gate with confident
language. State the exact blocker, what remains unproven, and the command or
environment needed to prove it.

## Verification record

Use this compact shape in the handoff:

```text
Claim:
Check or command:
Exit code:
Important result:
Untested or unresolved:
Verdict: proven | partially proven | not proven
```

Do not create plans, stories, sub-agents, or alternate proof scores from this
skill. Verification evidence supplements repository authority; it does not
replace missing product or architecture decisions.
