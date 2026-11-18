**Review configuration: Missing.** The supplied project facts say `AGENTS.md` points to `docs/review-policy.yaml`, which is absent. No accepted Core/Leaf boundaries are documented, so I can’t determine whether the change is ready. The available CI checks are `flutter analyze` and `npm test`; no review integration is documented.

**Setup question 1 — Core/Leaf boundaries:** Should `apps/mobile/lib/ui/` be classified as **Core** (recommended, because UI changes can affect user-visible behavior), or **Leaf**? This determines the review evidence required for changes there.

Files read: `tests/harness/blast-radius-review/inputs/missing-policy-setup/prompt.txt`, `.agents/skills/blast-radius-review/SKILL.md`, `.agents/skills/grill-me/SKILL.md`.
