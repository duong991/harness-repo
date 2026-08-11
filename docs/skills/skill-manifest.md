# Repository Skill Manifest

This manifest covers the eight supplemental workflow skills installed for this
consumer repository. Harness-managed `onboard-repository` and
`audit-onboarding-proposal` remain part of Harness core and are not members of
this eight-skill suite.

| Skill                            | Source                                                            | Commit                                     | Activation                                        | Local changes                                                                                                                                   | Owner | Last reviewed |
| -------------------------------- | ----------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------------- |
| `work-router`                    | Internal Repository Harness implementation                        | `internal`                                 | Auto, mandatory `AGENTS.md` gate                  | Sole workflow router; downstream skills cannot widen scope, plans, stories, or orchestration                                                    | gnoud | 2026-08-04    |
| `grill-me`                       | `mattpocock/skills` — `skills/productivity/grill-me` + `grilling` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Explicit-only                                     | Repository discovery, one-question interview, confirmed brief, permission-gated writes, no code/plan/story                                      | gnoud | 2026-08-04    |
| `diagnosing-bugs`                | `mattpocock/skills` — `skills/engineering/diagnosing-bugs`        | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto after routing                                | Evidence-first root-cause loop, read-only mode, compressed obvious-defect path, fresh regression validation                                     | gnoud | 2026-08-04    |
| `tdd`                            | `mattpocock/skills` — `skills/engineering/tdd`                    | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto after routing when appropriate               | Conditional red-green-refactor; observable behavior; practical boundary mocking                                                                 | gnoud | 2026-08-04    |
| `code-review`                    | Merged local + `mattpocock/skills` engineering code review        | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto for reviews and medium/large changes         | Single review entry point; mandatory authority-first compliance, technical/security/regression review, risk-gated adversarial pass, unified findings | gnoud | 2026-08-05    |
| `implementation-walkthrough`     | Internal                                                          | `internal`                                 | Auto after routing for large-change comprehension | Explains diffs by behavior within an investigation budget, uses matching active plans without confirmation as typed reference context, separates observed evidence from unresolved questions, and proposes a review order before formal review | gnoud | 2026-08-05    |
| `test-walkthrough`               | Internal                                                          | `internal`                                 | Auto after routing for test comprehension       | Per-file digest of actual production symbols, protected behavior, unproven behavior, Strong/Partial/Weak assessment, and reading priority; explanatory only, never an adequacy or approval gate | gnoud | 2026-08-06    |
| `verification-before-completion` | `obra/superpowers` — `skills/verification-before-completion`      | `44c9b2d6e889982ac18c27d05a19fefe335194e1` | Auto and mandatory                                | Fresh claim-specific proof, exit-code record, explicit untested surfaces                                                                        | gnoud | 2026-08-04    |

## Installation contract

Copying the eight skill directories alone is incomplete. Every consumer
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
and activation rules, and rerun the workflow validation suite before replacing
the pinned revision.
