---
name: minimal-implementation
description: Choose the smallest sufficient implementation for authorized coding work after tracing the affected flow. Use when accepted authority leaves the solution shape open; reuse repository, standard-library, platform, and installed capabilities before writing custom code without weakening required safeguards or validation.
---

# Minimal Implementation

`minimal-implementation` is a supporting discipline. It does not own routing,
does not create a new work type, and does not authorize implementation.
`work-router` selects the workflow; accepted product, design, repository, and
technical authority still decide the required behavior.

Comprehension precedes minimization. First read the accepted authority and
trace the affected flow, callers, data and error paths, trust boundaries, and
existing tests. This discipline does not replace comprehension of the affected
flow or `diagnosing-bugs` root-cause analysis.

## Choose the first sufficient option

For authorized implementation whose solution shape is open, stop at the first
option that satisfies the accepted behavior:

1. **YAGNI:** If the behavior is not required, skip it.
2. **Reuse:** Reuse existing repository behavior before writing new behavior.
3. **Standard library:** Prefer standard-library capability.
4. **Native platform:** Prefer native runtime or platform capability.
5. **Installed dependency:** Prefer already-installed dependencies.
6. **Direct implementation:** Prefer a direct, clear implementation over a
   speculative abstraction.
7. **Minimum custom implementation:** Only then write the minimum custom
   implementation necessary.

Do not add a dependency, abstraction, helper layer, configuration surface, or
new behavior unless the selected workflow and accepted authority require it.
Keep the change local to the understood flow; do not turn simplification into
an unrequested refactor.

## Preserve authority and safeguards

This discipline must not override accepted product, design, repository, API,
security, or compatibility authority. When accepted authority fixes an
implementation choice, follow it rather than substituting a smaller-looking
alternative.

Never trade away correctness, trust-boundary validation, authorization,
security, accessibility, data-loss handling, required error handling,
compatibility, or meaningful validation for a smaller patch. The smallest
implementation in the wrong layer, or one that omits a required safeguard, is
not sufficient.

`tdd` remains the TDD owner when a valuable automated seam exists, and
`codebase-design` remains the module, interface, and seam design discipline.
Do not use this discipline to route code review: formal findings and adequacy
belong only to `code-review`. It does not own completion;
`verification-before-completion` remains mandatory for every positive
completion claim.

This discipline does not create plans, stories, findings, or orchestration and
cannot independently spawn sub-agents. It defines no modes, lifecycle hooks,
slash commands, or second control plane.
