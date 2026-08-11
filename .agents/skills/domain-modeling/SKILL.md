---
name: domain-modeling
description: Propose or apply changes to a project's domain vocabulary, relationships, and durable terminology. Use when domain concepts need active modeling rather than read-only explanation; use existing repository documentation and decision authority instead of imposing a new hierarchy.
---

# Domain Modeling

Use this discipline when actively changing domain language or relationships,
not merely reading terminology. Before writing, inspect `docs/README.md`,
existing product and domain vocabulary, relevant product docs, necessary code,
and accepted decisions under `docs/decisions/`.

If the consumer repository already accepts a `CONTEXT.md`, domain glossary, or
ubiquitous-language document, use it. Otherwise, when durable terminology is
explicitly needed, prefer the narrowest suitable document under `docs/product/`.
Create a dedicated domain document only when authorized and no existing
authority fits. Do not require `CONTEXT.md`, `CONTEXT-MAP.md`, or `docs/adr/`.

## During modeling

- Challenge terminology that conflicts with the established vocabulary.
- Separate overloaded terms with precise canonical names.
- Use concrete scenarios to test relationships and edge cases.
- Cross-check claimed behavior against code and surface contradictions.
- Keep domain concepts distinct from implementation detail.

For concise glossary structure, read
[references/domain-glossary-format.md](references/domain-glossary-format.md).

## Lasting decisions

Record a decision only when it is hard to reverse, surprising without context,
and the result of a real trade-off. Use `docs/decisions/` and
`docs/templates/decision.md`; do not create an alternate ADR hierarchy.

This discipline follows the selected Harness workflow. It cannot create a new
work type, plan, decision authority, or implementation scope.
