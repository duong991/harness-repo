---
name: codebase-design
description: Design or improve a module's interface, seam, depth, testability, or dependency shape. Use when architecture or implementation work needs a clearer module boundary; preserve the route, authority, and scope selected by the Repository Harness.
---

# Codebase Design

Use this supporting discipline to design **deep modules**: substantial behavior
behind a small interface at a clean seam. It supplies vocabulary and analysis;
it does not authorize refactoring, implementation, review, plans, or
orchestration.

## Vocabulary

- **Module**: a unit with one interface and an implementation.
- **Interface**: every fact a caller needs, including invariants, errors,
  ordering, configuration, and performance—not only type signatures.
- **Implementation**: the behavior behind the interface.
- **Depth**: caller leverage per unit of interface learned.
- **Seam**: the location where behavior can change without editing callers.
- **Adapter**: a concrete implementation at a seam.
- **Leverage**: capability a caller gains from depth.
- **Locality**: concentration of change, knowledge, bugs, and verification.

## Design principles

- Prefer a small interface that hides consequential implementation complexity.
- Apply the deletion test: if deletion spreads complexity back into callers, the
  module was earning its depth.
- Treat the interface as the primary test surface; tests should observe outcomes
  through it and survive implementation refactors.
- Add a seam when variation justifies adapters, not as speculative indirection.
- Accept dependencies and return results where that makes behavior testable.

For dependency categories, seam discipline, and replace-don't-layer testing,
read [references/deepening.md](references/deepening.md). For materially
different interfaces, read [references/design-it-twice.md](references/design-it-twice.md).

## Authority and scope

Use this vocabulary within the selected Harness workflow. It cannot independently
spawn sub-agents, widen scope into refactoring, or become an architecture-review
workflow. Sub-agents may be used only when `work-router` selected
`orchestrated-multi-agent-work` or the user already gave explicit authorization.
