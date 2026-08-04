---
name: grill-me
description: Run an explicit, one-question-at-a-time interview to resolve materially important product, UX, scope, permission, or acceptance decisions that repository authority cannot answer. Use only when the user invokes /grill-me, names $grill-me, asks for a grill session, or accepts work-router's recommendation to grill an ambiguous product change; finish with a confirmed Change Brief or Product Brief and do not implement code.
---

# Grill Me

Resolve decisions without inventing them.

## Establish context

1. Read `AGENTS.md`, `docs/WORKFLOW.md`, and the smallest relevant product,
   design, architecture, decision, and plan material.
2. Inspect the repository for facts before asking. Do not ask the user to repeat
   information already recorded in authority or observable evidence.
3. Build a decision tree. Ask only questions whose prerequisites are settled,
   starting with the decision that most changes downstream scope or behavior.

## Interview

- Ask exactly one question at a time and wait for the answer.
- Give a recommended answer and a concise rationale for every question.
- Keep facts and decisions separate: retrieve facts; put decisions to the user.
- Resolve users, problem, primary job, MVP, out of scope, user flow, loading,
  empty, error, disabled and permission states, data sources, integrations,
  security/operations, and testable acceptance criteria when relevant.
- Walk dependent branches only after their parent decision is confirmed.
- Do not design architecture unless architecture is the explicit subject of the
  grill. Do not write source code, create an active plan, create a Harness CLI
  story, or spawn a sub-agent.

## Close the session

When the decision tree is resolved, present a concise brief containing:

- objective and user;
- problem and primary job;
- confirmed scope and out of scope;
- main flow and exceptional states;
- functional and non-functional constraints;
- permissions, security, data, and integrations;
- testable acceptance criteria;
- assumptions, open decisions, and explicit unknowns.

Ask the user to confirm shared understanding. After confirmation, update the
existing repository document that owns the decision. For product intent, use
the relevant file under `docs/product/`; create `docs/product/product-brief.md`
only when no narrower product document exists and the user authorized a new
brief. If no destination has authority, return the exact brief and request the
smallest destination decision before writing.

End by asking `work-router` to reclassify the confirmed work. Do not continue
into implementation from this skill.
