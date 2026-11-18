**Review gate: Ready.** The accepted policy is Mobile Architecture Council policy at `mobile/docs/review-policy.yaml`, with paths matched relative to `mobile/`.

The working-tree diff contains only `mobile/lib/ui/settings/theme.dart`. Under the policy, `lib/ui/**` is Leaf, so this change is **Leaf**. Because it changes UI, the required evidence is:
- A passing `flutter analyze` run for the current revision, executed from `mobile/`.
- Visual proof of the changed UI, tied to the reviewed revision.

The supplied snapshot contains no results or artifacts for either requirement, so both are **missing**. The reviewed revision identifier is also not provided, so evidence freshness cannot yet be established. Core-only safety answers and feature-flag evidence are not required for this Leaf classification.

Review ownership belongs to `code-review`. No local or server MR enforcement is documented. No formal review findings or approval are made here.

Files read: `.agents/skills/blast-radius-review/SKILL.md`; `tests/harness/blast-radius-review/inputs/accepted-policy-nested-flutter-leaf/prompt.txt`.
