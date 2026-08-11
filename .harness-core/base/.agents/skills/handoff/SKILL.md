---
name: handoff
description: Create compact continuation context for a later session when explicitly requested.
---

# Handoff

Write a concise handoff document in the user's operating-system temporary
directory, never in the workspace unless the user explicitly asks for it. Tailor
it to the next-session objective supplied by the user.

Include the current goal and state, work completed, current evidence, relevant
paths or URLs, remaining work and blockers, sensitive-data redaction, and
suggested next skills. Refer to existing plans, specifications, decisions,
commits, and diffs rather than duplicating them.

A handoff is not durable project authority. If an active plan exists, link to
`docs/plans/active/<plan>` rather than copying its contents. Do not claim a
milestone is complete without existing fresh verification evidence.
