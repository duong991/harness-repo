---
name: resolving-merge-conflicts
description: Resolve an authorized in-progress Git merge or rebase conflict by reconstructing source intent, preserving compatible behavior, and verifying the result. Use only when conflict resolution is within the selected Harness workflow.
---

# Resolving Merge Conflicts

Use this discipline only for an authorized, in-progress merge or rebase. Follow:

```text
STATE → INTENT → RESOLVE → VERIFY → CONTINUE
```

1. **STATE:** inspect Git operation state, history, status, and every
   conflicting file.
2. **INTENT:** locate the primary sources for both changes—commits, accepted
   specs, decisions, code, tests, and requested merge goal—and understand why
   each side changed.
3. **RESOLVE:** preserve both intents where compatible. Never invent behavior.
   Stage only intended resolution paths; preserve unrelated local work.
4. **VERIFY:** run the repository checks appropriate to the resolved behavior
   and read their outcomes.
5. **CONTINUE:** continue or commit only when the requested merge/rebase
   operation authorizes it.

Resolve when intent can be established safely. If competing intents cannot be
reconciled without inventing behavior, stop with an explicit blocker. Do not
abort an in-progress operation unless the user requests it or aborting is
required for recovery.

This discipline cannot stage the entire repository, commit unrelated work,
create a plan, or widen Git authority. Read-only conflict analysis remains
read-only analysis.
