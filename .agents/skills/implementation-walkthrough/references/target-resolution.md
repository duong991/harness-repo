# Target Resolution Reference

Use this reference when BASELINE needs target-specific Git inspection. It is
navigation help only and never authorizes mutation.

## Worktree target

```bash
git status --short
git diff --cached --stat
git diff --cached --name-status
git diff --cached --numstat
git diff --stat
git diff --name-status
```

Read the full consequential files. Record unrelated staged, unstaged, and
untracked work; leave it untouched.

## Fixed target

- Commit: identify the commit ID and inspect its name-status, stat, and full
  consequential files.
- Branch or range: record both endpoints before deriving the diff.
- Pull request: record the PR revision/commit set and distinguish declared
  validation from validation rerun now.

If `HEAD`, staged files, untracked files, or the target revision changes during
the walkthrough, the earlier map is stale. Repeat BASELINE before relying on
file accounting or path tracing.
