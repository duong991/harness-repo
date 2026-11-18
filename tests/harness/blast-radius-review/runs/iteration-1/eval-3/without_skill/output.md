This is a Core-tier review: the change is mixed, it edits a Core workflow, and the rename crosses Core and Leaf paths. The CI result is from an earlier revision, so it does not verify the reviewed change.

I did not run `scripts/lint.sh` because it runs `eslint --fix` and mutates files. The supplied snapshot does not specify safe read-only checks or provide executable evidence, so I can’t report checks run. To complete the review, provide current-revision CI and the required integration/runtime evidence, safety answers, feature-flag or accepted N/A rationale, recovery approach, and visual proof for the UI change.

Files read: `tests/harness/blast-radius-review/inputs/accepted-policy-core-rename-mixed-mutating-lint/prompt.txt`
