# dsh headless adapter

Runtime: `@deepseek-ai/dsh` with the `headless` profile —
`dsh --profile headless "<task>"`. One fresh session per call, no follow-up
turn, no listening port. The worker's working directory (and sandbox workspace)
is the directory dsh is launched from, which is why `run-worker.sh` `cd`s into
the worktree.

## Verified on the author's machine (dsh 0.1.5-rc.1, 2026-10-31)

- `dsh --profile headless --help` prints usage and exits 0.
- **Node ≥ 21 is required.** Launched under Node 20, `dsh` exits **0 with no
  output at all** — indistinguishable from success unless you check stdout.
  `run-worker.sh` resolves the `node` next to the `dsh` binary and refuses to run
  below 21; it also maps empty stdout to `no_answer`.
- Missing model key: exit 1, stderr
  `dsh: MISSING_CREDENTIAL: llm-deepseek: no API key ...`. The fix is the user's:
  store the key via the dsh web Models page, or export `DEEPSEEK_API_KEY` in the
  launching environment. Never enter it yourself.

## Documented, not yet verified here

- Exit 0 when the final turn completed; exit 1 when aborted/errored, with
  `dsh: <code>: <message>` on stderr.
- stdout carries only the final assistant message; stderr carries streamed
  reasoning under `dsh: reasoning:`. Tool output is not printed — inspect the
  worktree for what actually happened.
- Default permission preset for new sessions is `workspace-write` with
  `approval: ask`. Headless has no approver and no CLI flag to change the
  preset. **What happens when a tool call needs approval is unverified** — it
  may be denied or the run may stall. The `--timeout` deadline is what bounds a
  stall; a timeout is `UNKNOWN`, not failure or success.
- `workspace-write` sandboxes writes to the workspace; it is not a path
  allowlist inside it, which is why `check-scope.py` exists.
- No read-only mode is reachable from headless, so Phase B never uses a worker
  for read-only routes.

## First-use smoke test (Phase A)

Before relying on the skill on a new machine, run once in an empty scratch git
repo and confirm each line:

```bash
mkdir -p /tmp/dsh-smoke && cd /tmp/dsh-smoke && git init -q && git commit -q --allow-empty -m init
<skill-dir>/scripts/run-worker.sh --worktree . --allow-main-worktree \
  --prompt-file <(echo 'Create b.txt containing PONG, then answer exactly: DONE') \
  --run-dir /tmp/dsh-smoke.run --timeout 300
cat b.txt     # PONG
```

Expected: `outcome: finished`, stdout `DONE`. Then try a prompt that needs a
command requiring approval (e.g. writing outside the workspace) to learn how
headless handles `approval: ask` on this install, and record the result here.

## Alternative controller (not used in Phase B)

`dshctl` (github.com/Qidianyan/dshctl) drives a running `dsh web` host over its
loopback HTTP API and exposes `/permission read-only|workspace-write|danger-full-access`,
`approvals`, `watch`, and `cancel`. It would enable read-only workers and
supervised approvals, but needs the web host running and is a separate
community tool. Consider it for a later phase, after verifying it on this
machine.
