# Repository Skill Manifest

This manifest covers the core workflow skills and supporting disciplines
installed for this consumer repository. They are Harness-managed: their complete file trees have a base
snapshot and hash entry in `.harness-core/manifest.json`, so the updater can
perform a deterministic three-way update. Harness-managed
`onboard-repository` and `audit-onboarding-proposal` remain separate onboarding
skills outside the workflow/supporting-discipline suite.

| Skill                            | Source                                                            | Commit                                     | Activation                                        | Local changes                                                                                                                                   | Owner | Last reviewed |
| -------------------------------- | ----------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------------- |
| **Core workflow skills**         |                                                                   |                                            |                                                   |                                                                                                                                                 |       |               |
| `work-router`                    | Internal Repository Harness implementation                        | `internal`                                 | Auto, mandatory `AGENTS.md` gate                  | Sole workflow router; downstream skills cannot widen scope, plans, stories, or orchestration                                                    | gnoud | 2026-08-04    |
| `grill-me`                       | `mattpocock/skills` — `skills/productivity/grill-me` + `grilling` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Explicit-only                                     | Repository discovery, one-question interview, confirmed brief, permission-gated writes, no code/plan/story                                      | gnoud | 2026-08-04    |
| `diagnosing-bugs`                | `mattpocock/skills` — `skills/engineering/diagnosing-bugs`        | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto after routing                                | Evidence-first root-cause loop, read-only mode, compressed obvious-defect path, fresh regression validation                                     | gnoud | 2026-08-04    |
| `tdd`                            | `mattpocock/skills` — `skills/engineering/tdd`                    | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto after routing when appropriate               | Conditional red-green-refactor; observable behavior; practical boundary mocking                                                                 | gnoud | 2026-08-04    |
| `code-review`                    | Merged local + `mattpocock/skills` engineering code review        | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto for reviews and medium/large changes         | Single review entry point; mandatory authority-first compliance, technical/security/regression review, risk-gated adversarial pass, unified findings | gnoud | 2026-08-05    |
| `implementation-walkthrough`     | Internal                                                          | `internal`                                 | Auto after routing for large-change comprehension | Five-phase BASELINE/MAP/TRACE/PROBE/HANDOFF workflow; behavior-based Review Units, Critical Path, Risk Probes, Invariants, evidence freshness, conditional references, and formal-review handoff | gnoud | 2026-08-11    |
| `verification-before-completion` | `obra/superpowers` — `skills/verification-before-completion`      | `44c9b2d6e889982ac18c27d05a19fefe335194e1` | Auto and mandatory                                | Fresh claim-specific proof, exit-code record, explicit untested surfaces                                                                        | gnoud | 2026-08-04    |
| **Supporting disciplines**       |                                                                   |                                            |                                                   |                                                                                                                                                 |       |               |
| `writing-for-agents`             | `mattpocock/skills` — `skills/productivity/writing-for-agents`    | `84fdeffd12f2ee307994d1eb6feb48173b6e0502` | Model-invoked                                      | Harness invocation mechanics, authority pointers, no competing router                                                                            | gnoud | 2026-08-11    |
| `handoff`                        | `mattpocock/skills` — `skills/productivity/handoff`               | `84fdeffd12f2ee307994d1eb6feb48173b6e0502` | Explicit-only                                      | Temporary compact context, redaction, links instead of duplicate authority                                                                       | gnoud | 2026-08-11    |
| `codebase-design`                | `mattpocock/skills` — `skills/engineering/codebase-design`        | `84fdeffd12f2ee307994d1eb6feb48173b6e0502` | Model-invoked                                      | Deep-module vocabulary, sequential alternatives, no self-orchestration                                                                           | gnoud | 2026-08-11    |
| `domain-modeling`                | `mattpocock/skills` — `skills/engineering/domain-modeling`        | `84fdeffd12f2ee307994d1eb6feb48173b6e0502` | Model-invoked                                      | Existing `docs/product/` and `docs/decisions/` authority; no required CONTEXT or ADR hierarchy                                                   | gnoud | 2026-08-11    |
| `resolving-merge-conflicts`      | `mattpocock/skills` — `skills/engineering/resolving-merge-conflicts` | `84fdeffd12f2ee307994d1eb6feb48173b6e0502` | Model-invoked                                   | Intent-first, no invented behavior, only intended staging and authorized continuation                                                            | gnoud | 2026-08-11    |
| `teach`                          | `mattpocock/skills` — `skills/productivity/teach`                  | `5b15a47f2d7150f545fbcacbfe381787fc0230dc` | Explicit-only                                      | Approved teaching workspace, no repository-root writes, module-learning guidance, no code/test/Git mutation                                       | gnoud | 2026-08-24    |
| `encode-invariant`               | `hoangnb24/repository-harness` — `.agents/skills/encode-invariant` | `e765792b635b4d5e3e5fc0578f82f9ca5dea2681` | Model-invoked                                      | Smallest mechanical check, positive/negative proof, 4-level enforcement reporting | gnoud | 2026-09-22    |
| `improve-harness`                | `hoangnb24/repository-harness` — `.agents/skills/improve-harness`  | `e765792b635b4d5e3e5fc0578f82f9ca5dea2681` | Explicit-only                                      | Baseline preservation, earliest gap analysis, smallest intervention, required fresh rerun | gnoud | 2026-09-22    |
| `grill-with-docs`                | `mattpocock/skills` — `skills/engineering/grill-with-docs`        | `c55ee46073ed923f86ce59a5eb3b6d895095d1b7` | Explicit-only                                      | Combines `grill-me` with `domain-modeling`; records decisions in `docs/decisions/` and `docs/GLOSSARY.md`; no direct code edits | gnoud | 2026-09-22    |
| `improve-codebase-architecture`  | `mattpocock/skills` — `skills/engineering/improve-codebase-architecture` | `c55ee46073ed923f86ce59a5eb3b6d895095d1b7` | Explicit-only                                      | Scans hotspots for shallow modules; renders visual HTML report to `$TMPDIR`; grills deepening decisions; gates execution through `docs/plans/active/` | gnoud | 2026-09-22    |
| `system-log-tracer`              | Internal (origin safekid-backend), influenced by sickn33/agentic-awesome-skills | `internal` | Model-invoked | Read-only runtime evidence across Elasticsearch/Kibana, Redis, MongoDB, Kafka for NestJS/Turborepo services; Python-only tools (one policy implementation in `tools/common.py`), MongoDB/Kafka via `uv run --script` with pinned `pymongo`/`confluent-kafka`, code-enforced read-only guards, config/credential split, production gate, 7-section evidence report; hands off to `diagnosing-bugs` | gnoud | 2026-10-20 |
| `dsh-worker-orchestration`       | Internal                                                          | `internal`                                 | Explicit-only                                      | Delegate bounded code changes to a single DSH headless worker in an isolated git worktree with supervision and scope checks | gnoud | 2026-11-01    |
| `sync-repo-skills`               | Internal                                                          | `internal`                                 | Explicit-only / Model-invoked                      | Scan and synchronize skills from canonical repository to consumer repositories with prompt-driven confirmation | gnoud | 2026-11-01    |
| `codex-first` | `steipete/agent-scripts` — `skills/codex-first` | `2f82700ba9f3e7e93d3583e1990992584561eadc` | Explicit-only | Claude Code / OpenClaw-on-Claude work routing: delegate hands-on work to Codex under native-Claude model gate; bundled references and codex-resume watchdog script | gnoud | 2026-11-23 |
| `in-your-own-words` | `cursor/plugins` — `pstack/skills/in-your-own-words` | `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9` | Explicit-only | Restate in agent's own words what the user's goals and core problems are (/in-your-own-words) | gnoud | 2026-11-23 |
| `no-comments` | `cursor/plugins` — `pstack/skills/no-comments` | `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9` | Explicit-only | Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints (/no-comments) | gnoud | 2026-11-23 |
| `typescript-best-practices` | `cursor/plugins` — `pstack/skills/typescript-best-practices` | `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9` | Model-invoked / Explicit-only | TypeScript best practices when reading or editing .ts or .tsx files; covers discriminated unions, branded types, constructive modeling, schema validation, and patterns | gnoud | 2026-11-23 |

## Installation contract

Copying the eight core workflow skill directories alone is incomplete. Every consumer
repository must install an equivalent `## Task routing` gate in its root
`AGENTS.md` so `work-router` selects the workflow before downstream skills act.

CodeGraph is not an additional workflow skill. When available, it is an
optional discovery capability used by the router, debugging, review, and
verification guidance; its output is derived evidence and never authority or
completion proof. Consumer repositories may omit it without weakening the
Harness core workflow.

## Update policy

Update external skills only from an immutable commit or release. Read each
skill's `SOURCE.md`, compare upstream changes, preserve local Harness authority
and activation rules, update the corresponding `.harness-core/base/` snapshot
and manifest hash atomically, then run:

```bash
scripts/test-harness-skills
```

`SOURCE.md` remains provenance only; it is not an alternative update mechanism.
