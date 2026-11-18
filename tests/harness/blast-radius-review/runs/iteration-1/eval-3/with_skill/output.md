**Triage:** The accepted policy is Ready. The rename touches a Core path (`services/api/**`) and a Leaf path (`apps/web/ui/**`), and the workflow change is also Core. The mixed change therefore receives Core treatment; both rename endpoints count.

**Evidence:** The shown CI result is from an earlier revision, so it does not establish a pass for this diff. The supplied facts identify `scripts/lint.sh` as mutating (`eslint --fix`), so I did not run it. No safe, non-mutating check command or current-revision integration/runtime evidence was supplied.

Before the Core evidence gate can be assessed, please provide the three safety answers: what must remain unchanged; the worst credible impact to users, data, or services; and how to stop the impact, including what cannot be rolled back. Also provide the feature-flag name, default, and disable procedure, or an accepted not-applicable rationale and recovery approach.

**Handoff:** `code-review` owns formal findings. No MR enforcement is configured.

**Files read:** `.agents/skills/blast-radius-review/SKILL.md`; `tests/harness/blast-radius-review/inputs/accepted-policy-core-rename-mixed-mutating-lint/prompt.txt`.
