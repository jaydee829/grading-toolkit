# Skill Evals

Automated eval suite for the grading-toolkit skills. Provisions isolated scenario directories, invokes `claude -p`, and checks the resulting files for structural compliance.

## Scenarios

### `grade-question` (collaborative mode)

The base scenario. Tests the full `grade-question` skill workflow with a collaborative `comment_strategy`. Includes students that trigger instructor-pause interactions:

| SID | Response | Expected grade | Interaction triggered |
|---|---|---|---|
| 111111 | Correct hypotheses | Correct | None |
| 222222 | Sample mean notation error | Minor communication error | Comment reuse |
| 333333 | Correct + extra rejection rule | Ambiguous | **Ask-up** |
| 444444 | Reversed hypotheses | Minor justification error | Comment reuse |
| 555555 | Verbal description only | Major errors | **Collaborative draft** |

**13 structural assertions.** Three (`decisions_updated`, `decisions_entry_format`, `new_comment_in_comments_md`) are marked `interaction_required_assertions` in `scenario.yml` and return `pass: null` in unattended (automated) runs.

**Regression signal:** `with_skill` should pass 10/13 structural assertions (3 are null/skipped). A drop below 10/13 flags a regression.

### `grade-question-strict` (strict mode)

Strict-mode scenario designed for fully automated regression testing. No instructor-pause interactions are triggered:

| SID | Response | Expected grade | Interaction triggered |
|---|---|---|---|
| 111111 | Correct hypotheses | Correct | None |
| 222222 | Sample mean notation error | Minor communication error | Comment reuse |
| 333333 | Correct hypotheses (clean) | Correct | None |
| 444444 | Reversed hypotheses | Minor justification error | Comment reuse |
| 555555 | Verbal description only | Major errors | None (strict — writes directly) |

**11 structural assertions actively checked** (2 interaction-required: `decisions_updated`, `decisions_entry_format` — skipped because no ask-up case exists in this scenario). `new_comment_in_comments_md` runs and should pass since strict mode writes the new comment directly without pausing.

**Regression signal:** `with_skill` should pass 11/13 structural assertions (2 null/skipped). A drop below 11/13 flags a regression.

## Running the Evals

```bash
cd C:\Users\Justin.Merrick\grading-toolkit

# Run the collaborative scenario
conda run -n Math378 python tests/evals/runner.py --scenario grade-question

# Run the strict scenario
conda run -n Math378 python tests/evals/runner.py --scenario grade-question-strict

# Compare all past results
conda run -n Math378 python tests/evals/runner.py --compare
```

## Interpreting Results

Results are written to `tests/evals/results/<timestamp>-results.json`.

### Structural assertions

Each assertion has `pass: true`, `pass: false`, or `pass: null`.

- `true` — assertion passed
- `false` — assertion failed (regression)
- `null` — assertion skipped (interaction required in unattended mode)

Skipped assertions are not failures — they reflect interactions the skill correctly triggers that `claude -p` cannot resolve non-interactively.

### Behavioral observations

The `behavioral` section in the results JSON is always `pass: null` after an automated run. To fill it in:

1. Open the `stdout_log` file listed in the results JSON.
2. Read through the log and verify each observation in `scenario.yml`'s `behavioral_observations`.
3. Edit the results JSON to set `pass: true` or `pass: false` and add a `note`.

### Regression tracking

```
conda run -n Math378 python tests/evals/runner.py --compare
```

Prints a table like:

```
scenario: grade-question-basic-workflow

                              2026-04-23  2026-04-28
with_skill / structural          10/13       10/13   ✓
with_skill / behavioral           0/7         3/7
without_skill / structural        7/13        7/13

scenario: grade-question-strict-workflow

                              2026-04-28
with_skill / structural          11/13
```

A drop in `with_skill / structural` between runs flags a regression. `without_skill` serves as a discriminability check — if its score improves over time, the scenario may no longer distinguish skill vs. no-skill.

## Running Unit Tests

```bash
conda run -n Math378 python -m pytest tests/evals/ -v
```

All 48 tests should pass:
- `test_checker.py` — 37 unit tests for all 13 checker assertions (including unattended mode)
- `test_checker_strict.py` — 3 tests for the strict scenario
- `test_runner.py` — 8 tests for the runner (provisioning, skill injection, pre-population)
