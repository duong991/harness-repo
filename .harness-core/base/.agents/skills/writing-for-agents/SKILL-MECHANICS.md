# Skill Mechanics

This reference applies the writing discipline to skills. Harness represents
invocation through the `SKILL.md` description plus `agents/openai.yaml` policy.
Do not depend on upstream-specific frontmatter such as `argument-hint` or
`disable-model-invocation`.

## Invocation

A model-invoked skill has a description with concrete trigger branches and an
`allow_implicit_invocation: true` policy. Use it when the agent or another
skill must reach the discipline without a user naming it.

An explicit-only skill has `allow_implicit_invocation: false`. Its display
prompt explains its purpose for a user who invokes it deliberately. Use this
when autonomous reach would add unnecessary context load or authority.

## Router relationship

Only `work-router` selects Harness work types and workflows. A supporting
discipline may document when it is useful, but cannot create a work type,
override the selected route, or use its invocation policy to widen authority.
