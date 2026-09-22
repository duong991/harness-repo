---
name: grill-with-docs
description: Run an explicit interview to sharpen a plan or design while building and updating repository domain documents and decisions. Use when product, domain, or architectural clarity is needed before implementation; do not implement code or create parallel authority.
---

# Grill With Docs

Resolve product, domain, and architectural decisions through an explicit interview while recording decisions directly into the repository's system of record.

## Invocation and discipline

- Invoke explicitly via `/grill-with-docs` or when an ambiguous initiative requires durable documentation.
- Combine the interview discipline of `grill-me` with the domain modeling and decision capture of `domain-modeling`.
- Run an explicit, one-question-at-a-time interview, waiting for human answers before branching.
- Separate facts from decisions: inspect the repository first; put genuine trade-offs to the human.

## Documentation capture

- Update established domain vocabulary in `docs/GLOSSARY.md` or the narrowest relevant file under `docs/product/`.
- Record durable, consequential architectural or technical decisions in `docs/decisions/` following `docs/templates/decision.md`.
- Do not require `CONTEXT.md`, `CONTEXT-MAP.md`, or `docs/adr/` unless already accepted by the consumer repository.
- Keep domain concepts distinct from implementation details.

## Authority and boundaries

- This skill does not authorize implementation, code edits, or test execution.
- It cannot create a new work type or task database.
- When implementation is needed after decisions are recorded, hand off to `work-router` or create an execution plan under `docs/plans/active/` only when authorized.
