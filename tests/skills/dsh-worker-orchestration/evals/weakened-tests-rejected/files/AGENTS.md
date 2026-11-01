# Agent Instructions

Classify each task with `work-router` before changing files: read-only-analysis,
tiny-fix, bounded-change, ambiguous-product-change, multi-session-initiative, or
orchestrated-multi-agent-work. Downstream skills cannot widen scope or introduce
orchestration. Run `python3 -m unittest discover -s tests` before claiming completion.
