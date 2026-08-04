# Repository Skill Manifest

This manifest covers the six supplemental workflow skills installed for this
consumer repository. Harness-managed `onboard-repository` and
`audit-onboarding-proposal` remain part of Harness core and are not members of
this six-skill suite.

| Skill | Source | Commit | Activation | Local changes | Owner | Last reviewed |
| --- | --- | --- | --- | --- | --- | --- |
| `work-router` | Internal Repository Harness implementation | `internal` | Auto, mandatory `AGENTS.md` gate | Sole workflow router; downstream skills cannot widen scope, plans, stories, or orchestration | gnoud | 2026-08-04 |
| `grill-me` | `mattpocock/skills` — `skills/productivity/grill-me` + `grilling` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Explicit-only | Repository discovery, one-question interview, confirmed brief, permission-gated writes, no code/plan/story | gnoud | 2026-08-04 |
| `diagnosing-bugs` | `mattpocock/skills` — `skills/engineering/diagnosing-bugs` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto after routing | Evidence-first root-cause loop, read-only mode, compressed obvious-defect path, fresh regression validation | gnoud | 2026-08-04 |
| `tdd` | `mattpocock/skills` — `skills/engineering/tdd` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto after routing when appropriate | Conditional red-green-refactor; observable behavior; practical boundary mocking | gnoud | 2026-08-04 |
| `review-against-authority` | `mattpocock/skills` — `skills/engineering/code-review` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto after routing for medium/large changes | Accepted contracts outrank plans; plans cannot confer authority; severity definitions | gnoud | 2026-08-04 |
| `verification-before-completion` | `obra/superpowers` — `skills/verification-before-completion` | `44c9b2d6e889982ac18c27d05a19fefe335194e1` | Auto and mandatory | Fresh claim-specific proof, exit-code record, explicit untested surfaces | gnoud | 2026-08-04 |

## Installation contract

Copying the six skill directories alone is incomplete. Every consumer
repository must install an equivalent `## Task routing` gate in its root
`AGENTS.md` so `work-router` selects the workflow before downstream skills act.

## Update policy

Update external skills only from an immutable commit or release. Read each
skill's `SOURCE.md`, compare upstream changes, preserve local Harness authority
and activation rules, and rerun all six validation scenarios before replacing
the pinned revision.
