# Iteration 1 grading audit

Audited the six eval criteria per configuration against `evals.json`, the saved outputs and grading, the installed `blast-radius-review` and `grill-me` skills, and the existing summary. No cases were executed and no criteria were changed.

## Correction

For eval 4 with skill, expectation 3 is now **pass**. The output first says it cannot classify `src/payment.ts` from the draft, then asks whether Core or Leaf should apply and explicitly labels Core as its recommendation. The `grill-me` skill requires a recommended answer for each question. In this context the recommendation is a proposal awaiting the user's decision, not an adopted policy or classification. Treating that recommendation as a policy default conflated proposal with authority.

Expectation 2 remains **fail**: the output does not say the draft lacks an accepted authority, nor identify its other material omissions. The distinction above does not cure that omission.

No other grading decision was demonstrably wrong. In particular, eval 3 without skill remains failed for omitting `code-review` as the formal findings owner. Eval 4 with skill remains failed for omitting accepted policy authority. These are explicit required concepts; semantic grading cannot credit absent owners or authority merely from context. The eval 6 without-skill output remains failed because it asks for several materials and does not ask the key Core/Leaf policy question.

## Revised totals

| Variant | Passed | Failed | Total | Pass rate |
| --- | ---: | ---: | ---: | ---: |
| With skill | 25 | 1 | 26 | 96.2% |
| Without skill | 24 | 2 | 26 | 92.3% |
| **All outputs** | **49** | **3** | **52** | **94.2%** |

## Suite weaknesses

- One saved response per case/configuration cannot establish repeatability or statistical significance.
- The cases provide repository facts directly; they assess response handling of supplied facts, not live discovery or actual skill/tool execution. Outputs and grading alone cannot verify claimed file reads or withheld commands.
- Equal-weight criterion counts conceal differences in consequence, and criteria that group several requirements can make it hard to see which sub-requirement was missed.
- The suite has little direct coverage of proposal versus adopted policy; this audit distinction was recoverable from eval 4's wording and `grill-me`'s explicit recommendation rule, but deserves careful human grading when interpreting similar responses.
