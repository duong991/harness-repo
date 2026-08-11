# Logic Prototype Branch

Use this branch for a business-rule, state-transition, lifecycle, authorization,
data-shape, or API-semantics question that is easier to evaluate by exercising a
small model. It works for backend-only scope and does not assume a frontend
exists.

1. State one domain-language question and the decision it can change.
2. Build the cheapest isolated, executable artifact: for example a state
   machine, pure functions, a reducer, a transformation, or a small interactive
   demo with explicit scenarios. Keep persistence and production infrastructure
   out unless the question itself requires a disposable local substitute.
3. Exercise the happy path, awkward transitions, prohibited actions, and failure
   behavior that are hard to judge from prose. Surface relevant state after each
   action so a non-developer can evaluate it.
4. Validate the model with the appropriate user or repository evidence. Do not
   turn the prototype into a tested production subsystem.

If the exploration exposes product-policy ambiguity, return to `grill-me`. If
it exposes durable vocabulary or relationship choices, use `domain-modeling`.
If it establishes a capability needing an implementation seam, use
`codebase-design`. Promote the validated decision or remove the artifact.
