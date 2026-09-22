# Learning Record Format

Learning records live in `./learning-records/` and use sequential numbering:
`0001-slug.md`, `0002-slug.md`, and so on. Create the directory lazily.

They record non-obvious understanding, prior knowledge, corrected
misconceptions, or mission changes that should affect future lessons. They are
not session logs and are not repository ADRs.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned and why it changes future teaching.}
```

Optional sections are appropriate only when useful:

- **Status**: `active` or `superseded by LR-NNNN`.
- **Evidence**: how the learner demonstrated the understanding.
- **Implications**: what this unlocks or rules out next.

Write a record only when the learner demonstrates genuine understanding,
discloses prior knowledge, corrects a misconception, or confirms a mission
shift. Material merely covered does not qualify.

When a later record contradicts an earlier one, mark the earlier record as
superseded rather than deleting it.
