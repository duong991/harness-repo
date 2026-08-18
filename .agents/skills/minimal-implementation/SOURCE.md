# Source

- Origin: Native Repository Harness discipline informed by external concepts
- Upstream repository: https://github.com/dietrichgebert/ponytail
- Source consulted: `AGENTS.md`
- Commit: `2ed6c52c9d7e5e56942508591085fd45dea277d3`
- License: MIT (conceptual reference only; no upstream files are vendored)
- Reviewed: 2026-08-18
- Owner: gnoud
- Activation: Model-invoked; `allow_implicit_invocation: true`
- Local implementation: translates only the YAGNI and capability-preference
  ladder into a supporting Harness discipline; retains Harness authority,
  routing, root-cause, TDD, design, review, verification, and non-orchestration
  ownership. It does not import Ponytail plugins, modes, hooks, commands, or
  control-plane features.
- Update method: compare an immutable upstream commit only for conceptual
  changes, retain the Harness boundaries, snapshot the revised tree atomically,
  and run the Harness skill validator.
