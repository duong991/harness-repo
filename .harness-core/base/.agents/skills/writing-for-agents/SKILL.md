---
name: writing-for-agents
description: Write or improve agent-consumed documents, including SKILL.md files, AGENTS.md, and referenced agent guidance. Use when a document must reliably trigger the right action, point to authoritative context, or express a workflow without duplicating repository authority.
---

# Writing for Agents

Use this discipline when writing an `AGENTS.md`, skill document, or document
reached by one of those files. The target is predictable process, not identical
output.

## Start with authority

Find the repository source that owns each policy before writing it. Point to
that source instead of copying its rules. A new document does not create a
parallel router, plan, decision log, product specification, or completion
authority.

## Context pointers

A context pointer names out-of-context material and the condition for loading
it. A skill description and a line in `AGENTS.md` are both pointers. State what
the material is and each genuinely distinct trigger branch. Front-load the
leading trigger words, collapse synonym-only branches, and remove identity the
target already carries.

## Keep the information hierarchy legible

Put ordered actions in the main file. Keep rules needed by every branch nearby.
Move branch-specific detail behind an explicit relative pointer. This
progressive disclosure protects attention as well as context budget. Co-locate
a concept's definition, rules, and caveats; keep each policy in one source of
truth.

## Make instructions executable

Give every step a checkable, suitably demanding completion criterion. Use
concise established terms consistently when they sharpen a repeated idea.
Prune stale caches of information available from commands, configuration, or
the referenced authority. Delete no-op instructions rather than polishing them.

## Skill documents

For invocation mechanics, read [SKILL-MECHANICS.md](SKILL-MECHANICS.md).
When editing a skill, preserve the repository's routing, authority, scope, and
verification gates; this discipline improves expression, not policy.
