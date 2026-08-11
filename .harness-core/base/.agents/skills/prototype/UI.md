# UI Prototype Branch

Use this branch for an unresolved interaction, information-hierarchy, or visual
flow question. It works for frontend-only scope and does not require a backend.

1. State the user-facing question and the decision it can change.
2. Show the minimum materially different structural variants needed to make the
   trade-off visible. Two or three is a default heuristic, not a quota.
3. Make hierarchy, primary actions, routing/interaction, loading, empty, error,
   and visible permission states legible. Do not spend effort on polish unless
   polish is the actual question.
4. Prefer scratch. If realistic context is necessary, use an isolated,
   clearly-named prototype area that reuses existing app conventions without
   becoming production code or silently shipping.
5. Ground unfamiliar concepts before asking for a choice; gather user feedback
   or observable evidence, then record the selected behavior and open questions.

For full-stack scope, translate validated observable behavior into optional
backend implications, not an API design. For example, bulk assignment implies
a bulk-assignment capability; it does not decide an endpoint or DTO. Delegate
domain meaning to `domain-modeling` and backend interfaces to `codebase-design`.

Remove losing variants and the prototype shell, or promote only the validated
decision through the selected Harness workflow.
