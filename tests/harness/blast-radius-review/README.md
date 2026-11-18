# Blast Radius Review evals

These compact evals exercise the observable review-configuration and triage
workflow with supplied repository snapshots. They are intended to run against a
fresh worker using `gpt-6-luna`. Give the worker only the prompt and, optionally,
the target skill; keep expected outputs and expectations hidden until the run
ends. Then give the grader the expectations to judge the response. Each case is
one sample, so results are useful for finding regressions but are not statistical
estimates of reliability.

The eval files live under `tests/harness/blast-radius-review/` because the
repository's `.agents/` material is read-only in this task. The artifacts
therefore do not change the skill or its source location.

The method follows Anthropic's skill testing guidance: first run realistic tasks
with a fresh agent, then grade observable results and use separate trigger
queries to check when the skill applies. Sources:

- [Skill authoring schema guidance](https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/references/schemas.md)
- [The Complete Guide to Building Skills for Claude: Testing and Iteration](https://claude.com/resources/guides/the-complete-guide-to-building-skills-for-claude/testing-and-iteration)

All task prompts state that their repository facts are snapshots and must not be
read as live filesystem state. `files` is empty because cases are self-contained.

## Validate artifacts

Run the standard-library validator:

```sh
python3 tests/harness/blast-radius-review/validate.py
```

For run summaries, provide a JSON array with one record per eval. Each record
contains `id`, an `output` string, and `expectation_results` (one boolean per
expectation, in order, filled in by a grader who has seen the criteria):

```json
[
  {"id":1,"output":"...","expectation_results":[true,true,true,true]}
]
```

Then run:

```sh
python3 tests/harness/blast-radius-review/validate.py --runs run-results.json
```

The summary reports case and expectation pass counts; it does not infer quality
from keywords or replace human grading.

## Repeat the evaluation

1. Run validate.py. Extract only each eval's prompt into a worker input; never
   give workers evals.json, expected_output, expectations, previous outputs or grades.
2. For each case launch two fresh gpt-6-luna agents, one with the installed skill
   and one without it. Use identical task facts and permissions. Do not inherit
   parent conversation. Stop interviews at the first question; do not synthesize
   user approval. Save each final response as
   runs/iteration-N/eval-ID/{with_skill,without_skill}/output.md.
3. Have an independent grader read the frozen criteria and outputs after execution.
   Save grading.json per run with expectations [{text,passed,evidence}] and summary
   {passed,failed,total,pass_rate}. Include eval_feedback for rubric weaknesses.
4. Run a separate selection probe using inputs/trigger-queries.json (no labels)
   and skill descriptions only. Save [{id,selected,reason}] as trigger-output.json.
5. Record executor model, skill hash and limitations in metadata.json. Do not
   estimate missing tokens/timing. Run:

```sh
python3 tests/harness/blast-radius-review/aggregate.py tests/harness/blast-radius-review/runs/iteration-1
```

This writes benchmark.json and validator-compatible with_skill-results.json and
without_skill-results.json. Aggregation exit 0 means records are internally valid,
not that every behavioral expectation passed. Inspect the reported failures.

Iteration 1 uses the supplied snapshot method. It does not measure real Claude
auto-triggering, disk discovery, permission handling or actual command side effects.
Final responses were saved from agent results; full tool transcripts were not
exported. Execution constraints prohibited repository writes in both conditions,
so non-mutation cannot be causally attributed to the skill. No CI wiring changed.

## Check the grading infrastructure

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/harness/blast-radius-review/test_artifacts.py
```

These three deterministic tests accept complete records and reject unsupported
grades and inconsistent totals. They test evaluation bookkeeping, not skill
behavior. Existing staged files are left untouched; avoid committing Python
bytecode caches with the suite.

## Interpretation limits and next iteration

- Frozen iteration-1 criteria are deliberately retained, including trigger query 4
  (policy-only summary), whose positive label is debatable. Do not change that
  label after observing the prediction to manufacture a pass.
- Eval 1 describes a review-only request although its expected-output prose
  mentions an explicitly requested setup interview. Treat this as a rubric
  ambiguity; a future iteration should split explicit setup and review-only
  authority into separate cases.
- The rubric does not strongly measure quality of recommendations: making every
  visible UI change Core would undermine the intended allocation of review effort.
- Add a dedicated UI-evidence assertion for mixed Core/UI changes in a future
  frozen suite; missing visual proof can be hidden by the broad Core criterion.
- Add live isolated-repository discovery and multi-turn setup persistence cases
  before claiming backend/Flutter integration. Snapshot cases do not cover those.

## Version scope

Iteration-1 benchmark predates conditional workflow integration. Its stored hash
is authoritative for that result; do not reuse its scores for the current skill.
The installed flow has a separate seven-scenario routing check in
`runs/flow-installed/luna-routing.md`, without a new behavioral benchmark claim.
