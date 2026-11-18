This change is **Leaf** under the accepted Mobile Architecture Council policy: `mobile/lib/ui/settings/theme.dart` is under `lib/ui/**`. The policy requires current-revision CI evidence for `flutter analyze` and visual proof for UI changes. The supplied snapshot does not include either proof, so the gate is not yet evidenced.

Collect:
- A passing `flutter analyze` result tied to the current revision, run from `mobile/`.
- Visual proof of the UI change, also tied to the current revision.

The snapshot says there are no changes outside `mobile/`. It documents code review as the review owner and no local or server MR enforcement; it does not establish that either required check has run.

**Files read:** `tests/harness/blast-radius-review/inputs/accepted-policy-nested-flutter-leaf/prompt.txt` only.
