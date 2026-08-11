---
name: prototype
description: Make a cheap, throwaway UI or logic artifact to answer one unresolved design or behavior question when it is materially easier to evaluate through interaction or execution than prose. Use for structural UI-flow, state-model, lifecycle, business-rule, or data-shape exploration; do not use for settled requirements or production implementation.
---

# Prototype

`prototype` is a supporting exploration discipline. It does not own routing,
does not create a new work type, and does not authorize implementation, product
policy, durable documentation, or multi-agent work. `work-router` selects the
workflow; accepted repository authority still decides durable behavior.

Use it only when there is one specific unresolved question whose answer could
change a decision and a cheap interactive or executable artifact is materially
more useful than prose. Do not prototype settled requirements.

```text
QUESTION → SELECT BRANCH → PROTOTYPE → VALIDATE → EXTRACT → PROMOTE / REMOVE
```

## 1. State the question and scope

Write the exact question, the decision it can affect, and the smallest evidence
needed to answer it. “Prototype this app” is not enough.

Task scope outranks repository classification. Infer relevant capabilities from
the task, framework/runtime evidence, and repository structure—not from a
language name. `Node.js` alone is neither a frontend nor a backend indicator.
React, Vue, and Angular are frontend evidence; NestJS, Express, Fastify,
Django, FastAPI, Spring Boot, ASP.NET, Go services, Rails, and Laravel are
backend evidence. Inspect an ambiguous framework such as Next.js or a monorepo
instead of guessing. If capability remains unclear, follow the question scope.

## 2. Select the smallest branch

- Interaction, information hierarchy, visible states, or user flow → [UI.md](UI.md).
- Business rules, state transitions, lifecycle, authorization behavior, or data
  shape → [LOGIC.md](LOGIC.md).
- Use both only when the same bounded question genuinely needs both views.

The UI branch does not assume a backend exists. The logic branch does not
assume a frontend exists. A full-stack exploration may use a validated UI to
identify backend implications; use [BACKEND-IMPLICATIONS.md](BACKEND-IMPLICATIONS.md)
only when backend behavior is in scope.

## 3. Make and validate the artifact

Build the minimum useful, clearly marked throwaway artifact. Default to a temp
or scratch location. Use an isolated, conspicuously named repository area only
when app fidelity needs real components, theme, routing, auth context, fixtures,
or existing data shapes. A prototype is not production implementation.

Generate the minimum number of materially different variants needed to expose
the trade-off. Two or three UI variants are a useful default for an open
question, not a quota; differences must concern structure, flow, information
hierarchy, or primary interaction rather than color or copy.

Ground a concept before asking a user to judge it when that concept affects the
choice. Validate through user feedback or relevant observable evidence; record
what was selected, rejected, and still unknown.

## 4. Extract and end deliberately

For a backend-relevant validated behavior, extract capabilities, data/query
needs, commands, authorization, transitions, failure behavior, and open
questions. UI evidence is not backend API authority: do not derive endpoint,
DTO, controller, service, or repository design directly from a mockup.

- `domain-modeling` owns durable domain meaning and terminology.
- `codebase-design` owns module, interface, and seam design.
- `grill-me` resolves product-policy ambiguity that an artifact exposes but
  cannot decide.

Short exploration findings stay in the conversation or scratch artifact. When
they drive implementation or span sessions, promote the decision into an
existing accepted plan, specification, or product document; this skill does
not create a default findings document or a new documentation hierarchy.

Finish explicitly: promote the validated decision into normal implementation,
or remove/discard the prototype. Do not leave prototype sediment in production
areas, and do not claim implementation is complete from prototype evidence.
