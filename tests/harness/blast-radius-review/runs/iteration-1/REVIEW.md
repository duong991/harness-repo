# Iteration 1 grading review

Graded 12 saved outputs against the six expectation sets in `evals.json` (six with-skill and six without-skill outputs). Each criterion is counted equally; semantic equivalents are accepted. The scores describe only the saved final text. They do not prove that listed files were actually read, that a command was run or withheld, or that other tool actions did or did not occur.

| Variant | Criteria passed | Criteria failed | Total | Pass rate |
|---|---:|---:|---:|---:|
| With skill | 25 | 1 | 26 | 96.2% |
| Without skill | 24 | 2 | 26 | 92.3% |
| **All outputs** | **49** | **3** | **52** | **94.2%** |

## Notable results

- The with-skill eval 4 output fails one criterion: it omits the draft’s absent accepted authority and broader material policy gaps. Its Core recommendation is explicitly a proposal awaiting confirmation, not an adopted classification; see `GRADING_AUDIT.md`.
- The without-skill outputs fail eval 3 on the explicit code-review ownership handoff and eval 6 on the required focused setup question; they ask for several inputs and do not ask whether `src/ui/**` is Core or Leaf.
- Eval 4 without-skill appropriately declines classification and identifies absent authority plus missing path-matching rules, though it does not enumerate every missing policy dimension.
- Eval 6 with-skill meets the stated criterion with a conditional, provisional Leaf suggestion; that suggestion is still potentially leading given the authority gap.
- Eval 1 without-skill is safe but less targeted than the expected setup interview question.

## Rubric and evidence limitations

- Criterion pass rates are simple counts of the supplied expectations, not a measure of overall quality. Feedback also notes omissions and ambiguity beyond those assertions.
- The supplied prompt text includes many target facts and requested distinctions (for example, whether policy is absent, accepted, draft, or inaccessible). This is scenario scaffolding, not independent evidence that a model would discover those facts from a real repository.
- Outputs contain “Files read” assertions, but no execution traces accompany them. This review does not validate those claims or infer tool behavior from output phrasing. Likewise, “did not run” statements are judged as response behavior, not verified command history.
- No run metadata or generation method was used to adjust scores.
