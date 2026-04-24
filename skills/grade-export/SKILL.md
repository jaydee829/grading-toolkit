---
name: grade-export
description: Use when one or more questions are fully graded and you need a CSV or JSON output file. Safe to run mid-grading for a progress snapshot — incomplete questions produce empty cells with a warning.
---

# Grade Export

Generate the configured output from all student grade files.

## Step 1: Check Completion

Run:
```
<run_prefix> scripts/check_progress.py
```

Report: how many students have at least one null grade. Ask:
"Proceed with export? (Ungraded questions will appear as empty cells in the output.)"

## Step 2: Run Export

```
<run_prefix> scripts/export_grades.py
```

This reads `workflow.yml` for format config and generates:
- CSV at `workflow.yml:output.csv_path` — one row per student, columns for `<Q>_grade` and `<Q>_comment`
- Question-indexed JSON at `workflow.yml:output.json_dir/grades_by_question.json`
- (or both, if format is `"both"`)

## Step 3: Verify Output

For CSV output: read the first 5 rows and verify:
- Headers match expected questions
- Student names and IDs look correct
- No encoding issues

Report the file path and row count. If any cells are empty (null grades), list the affected student/question pairs.
