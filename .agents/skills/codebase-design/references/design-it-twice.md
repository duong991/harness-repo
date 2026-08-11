# Design It Twice

When alternative interfaces would materially affect the outcome, generate at
least two genuinely different designs before choosing. Start by recording the
constraints, dependency categories, and an illustrative non-proposal sketch.

Default execution is sequential in the current session:

```text
current agent → design A → reset assumptions → design B → optionally design C → compare
```

For each design, define the interface, caller example, hidden implementation,
dependency/adapters, invariants and errors, and trade-offs. Compare depth,
locality, seam placement, and compatibility with accepted authority. Recommend
one design only when the selected workflow authorizes that decision.

This technique does not self-orchestrate. Parallel sub-agents are available only
when `work-router` selected `orchestrated-multi-agent-work` or explicit user
authorization already exists.
