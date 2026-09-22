---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. Use when seeking architecture improvements; does not authorize refactoring without an accepted plan.
---

# Improve Codebase Architecture

Surface architectural friction and propose deepening opportunities: refactoring proposals that turn shallow modules into deep ones.

This skill is informed by the project's domain model and built on the shared design vocabulary from `codebase-design`:

- Use the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real").
- Domain language in `docs/GLOSSARY.md` gives names to good seams; accepted decisions under `docs/decisions/` record decisions this skill should not re-litigate.
- This skill does not authorize refactoring, implementation, or Git mutation.

## Process

### 1. Explore

Scope before scanning (YAGNI). Deepening a module pays off by making future changes easier, so focus on parts of the codebase that have recently changed:

- If the user named a direction, investigate that area directly.
- Otherwise, inspect recent commit history (`git log --oneline`) to identify hot spots.
- Read existing domain vocabulary in `docs/GLOSSARY.md` and relevant decisions in `docs/decisions/` first.
- Note where you experience friction:
  - Where understanding one concept requires bouncing between many small modules?
  - Where are modules **shallow**, with an interface nearly as complex as the implementation?
  - Where have pure functions been extracted just for testability without **locality**?
  - Where do tightly-coupled modules leak across their seams?
  - Which parts are untested or hard to test through their current interface?
- Apply the deletion test: would deleting it concentrate complexity, or just move it?

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing untracked lands in the repo. Resolve the temp directory from `$TMPDIR` (defaulting to `/tmp`), and write to `<tmpdir>/architecture-review-<timestamp>.html`. Open it for the user (`xdg-open` / `open` / `start`) and state the absolute path.

The report uses Tailwind via CDN and Mermaid via CDN. For each candidate, render:
- **Files**: affected files or modules
- **Problem**: why current architecture causes friction
- **Solution**: plain description of the proposed deepening
- **Benefits**: locality, leverage, and how tests improve
- **Before / After diagram**: visual side-by-side comparison
- **Recommendation strength**: `Strong`, `Worth exploring`, or `Speculative`

See [HTML-REPORT.md](HTML-REPORT.md) for layout and diagram templates.
Do NOT modify source files or propose interfaces yet. Ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, conduct an interview to explore the decision tree: constraints, dependencies, the shape of the deepened module, what sits behind the seam, and what tests survive.

Record decisions and terminology as they crystallize:
- Clarify or add domain terms in `docs/GLOSSARY.md` using `domain-modeling`.
- Record load-bearing architectural decisions in `docs/decisions/` using `docs/templates/decision.md`.
- When the user authorizes proceeding with refactoring, create an execution plan under `docs/plans/active/`; do not modify production code directly from this skill.
