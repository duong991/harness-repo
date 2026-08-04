# Repository Skill Manifest

This manifest covers the six supplemental workflow skills installed for this
consumer repository. Harness-managed `onboard-repository` and
`audit-onboarding-proposal` remain part of Harness core and are not members of
this six-skill suite.

| Skill | Source | Commit | Activation | Local changes | Owner | Last reviewed |
| --- | --- | --- | --- | --- | --- | --- |
| `work-router` | Internal Repository Harness implementation | `internal` | Auto | Sole workflow router; six work types; lightest-safe-flow and no-parallel-authority rules | gnoud | 2026-08-04 |
| `grill-me` | `mattpocock/skills` — `skills/productivity/grill-me` + `grilling` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Explicit-only | Repository discovery, one-question interview, confirmed Harness brief, no code/plan/story | gnoud | 2026-08-04 |
| `diagnosing-bugs` | `mattpocock/skills` — `skills/engineering/diagnosing-bugs` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto on bug/failure | Evidence-first root-cause loop, minimal fix, fresh regression validation | gnoud | 2026-08-04 |
| `tdd` | `mattpocock/skills` — `skills/engineering/tdd` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto when appropriate | Conditional red-green-refactor; behavioral seams; skips unsuitable visual-only work | gnoud | 2026-08-04 |
| `review-against-authority` | `mattpocock/skills` — `skills/engineering/code-review` | `2ab958093e83e0ec752e6c1c5932da465bf23e0c` | Auto for medium/large changes | Single-agent read-only review, Harness authority precedence, evidence-backed findings | gnoud | 2026-08-04 |
| `verification-before-completion` | `obra/superpowers` — `skills/verification-before-completion` | `44c9b2d6e889982ac18c27d05a19fefe335194e1` | Auto and mandatory | Fresh claim-specific proof, exit-code record, explicit untested surfaces | gnoud | 2026-08-04 |

## Update policy

Update external skills only from an immutable commit or release. Read each
skill's `SOURCE.md`, compare upstream changes, preserve local Harness authority
and activation rules, and rerun all six validation scenarios before replacing
the pinned revision.
