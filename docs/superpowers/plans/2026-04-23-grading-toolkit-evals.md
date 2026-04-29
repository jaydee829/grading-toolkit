# Grading-Toolkit Skill Evals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible eval suite that runs `grade-question` with and without the skill, auto-checks structural compliance via 13 assertions, captures behavioral compliance in stdout logs, and accumulates timestamped results for regression tracking.

**Architecture:** A `runner.py` provisions two identical scenario directories (with/without skill injected via CLAUDE.md), invokes `claude -p` in each, then calls `checker.py` which runs 13 structural assertions against the resulting files. Results are written as timestamped JSON; a `--compare` flag prints a regression table across all runs.

**Tech Stack:** Python 3.9+, PyYAML, pytest, subprocess (claude CLI), os.path.getmtime for iterative-write detection.

---

## File Map

**Create:**
- `tests/evals/__init__.py` — empty package marker
- `tests/evals/conftest.py` — `scenario` fixture (loads scenario.yml) + `result_dir` fixture (pre-populated passing state)
- `tests/evals/checker.py` — 13 assertion functions + `load_scenario` + `run_all_assertions` + `_parse_comments_md`
- `tests/evals/runner.py` — `provision_directory`, `run_claude`, `write_results`, `compare_results`, CLI entry point
- `tests/evals/test_checker.py` — unit tests for all checker functions
- `tests/evals/test_runner.py` — unit tests for `provision_directory`
- `tests/evals/results/.gitkeep` — keeps results/ tracked
- `tests/evals/scenarios/grade-question/scenario.yml` — scenario config
- `tests/evals/scenarios/grade-question/fixtures/workflow.yml`
- `tests/evals/scenarios/grade-question/fixtures/rubric.md`
- `tests/evals/scenarios/grade-question/fixtures/answer_key.md`
- `tests/evals/scenarios/grade-question/fixtures/comments.md` — 2 pre-existing Q1 comments
- `tests/evals/scenarios/grade-question/fixtures/decisions.md` — empty baseline
- `tests/evals/scenarios/grade-question/fixtures/instructor_profile.md` — minimal
- `tests/evals/scenarios/grade-question/fixtures/submissions/metadata.yml`
- `tests/evals/scenarios/grade-question/fixtures/transcriptions/111111.md`
- `tests/evals/scenarios/grade-question/fixtures/transcriptions/222222.md`
- `tests/evals/scenarios/grade-question/fixtures/transcriptions/333333.md`
- `tests/evals/scenarios/grade-question/fixtures/transcriptions/444444.md`
- `tests/evals/scenarios/grade-question/fixtures/transcriptions/555555.md`

**Modify:**
- `.gitignore` — add `tests/evals/results/*.json` and `tests/evals/results/*.txt`

---

## Task 1: Scaffold

**Files:**
- Create: `tests/evals/__init__.py`
- Create: `tests/evals/results/.gitkeep`
- Modify: `.gitignore`

- [ ] **Step 1: Create package marker and results placeholder**

```bash
mkdir -p tests/evals/results
touch tests/evals/__init__.py tests/evals/results/.gitkeep
```

- [ ] **Step 2: Update .gitignore**

Append to `.gitignore`:
```
tests/evals/results/*.json
tests/evals/results/*.txt
```

- [ ] **Step 3: Commit**

```bash
git add tests/evals/__init__.py tests/evals/results/.gitkeep .gitignore
git commit -m "chore: scaffold eval directory and update gitignore"
```

---

## Task 2: Fixture Files

**Files:**
- Create: all files under `tests/evals/scenarios/grade-question/fixtures/`

No tests needed — these are static content files.

- [ ] **Step 1: Create fixture directories**

```bash
mkdir -p tests/evals/scenarios/grade-question/fixtures/submissions
mkdir -p tests/evals/scenarios/grade-question/fixtures/transcriptions
```

- [ ] **Step 2: Create `fixtures/workflow.yml`**

```yaml
project:
  name: Grade-Question Eval
  course: Eval 101
  instructor: Test Instructor
  created_at: "2026-04-23"
  profile: instructor_profile.md
submissions:
  directory: submissions/
  metadata: submissions/metadata.yml
  pdf_type: image_layer
  pdf_renderer:
    tool: pdftoppm
    path: pdftoppm
    dpi: 150
    max_pages: 20
python:
  run_prefix: "python"
questions:
  - id: Q1
    description: State null and alternative hypotheses for a two-sample t-test
  - id: Q2
    description: Identify the correct test statistic formula
comment_strategy: collaborative
output:
  format: csv
  csv_path: grades.csv
  json_dir: workspace/grades/
paths:
  rubric: rubric.md
  answer_key: answer_key.md
  comments: comments.md
  decisions: decisions.md
  transcriptions: workspace/transcriptions/
  grades: workspace/grades/
  pages: workspace/pages/
  scripts: scripts/
```

- [ ] **Step 3: Create `fixtures/rubric.md`**

```markdown
# Grading Rubric

- Correct
- Minor communication error
- Multiple minor communication errors
- Minor justification error
- Multiple minor justification errors
- Major errors or misconceptions
- Incoherent/incomplete evidence of understanding
- Blank
```

- [ ] **Step 4: Create `fixtures/answer_key.md`**

```markdown
## Q1

State the null and alternative hypotheses for a two-sample t-test comparing
the means of two independent populations.

**Correct answer:** H₀: μ₁ = μ₂, H₁: μ₁ ≠ μ₂

The null hypothesis asserts no difference between population means.
The alternative asserts a difference (two-tailed).
Population parameters (μ) must be used, not sample statistics (x̄).

## Q2

Identify the correct test statistic formula for a two-sample t-test.

**Correct answer:** t = (x̄₁ - x̄₂) / SE
```

- [ ] **Step 5: Create `fixtures/comments.md`**

```markdown
## Q1

### Minor communication error
- "Are you using the right symbol to represent a population mean here?"

### Minor justification error
- "Does this hypothesis reflect what would be true if there were no difference between groups?"
```

- [ ] **Step 6: Create `fixtures/decisions.md`**

```markdown
```

(Empty file — baseline for new-entry detection.)

- [ ] **Step 7: Create `fixtures/instructor_profile.md`**

```markdown
# Instructor Profile

## Grading Style
- Comments are phrased as questions, never as corrections.
- One sentence per comment.
- Do not reveal the answer directly.

## Edge-Case Philosophy
When uncertain between two categories, prefer the less severe category
unless the error demonstrates a fundamental misunderstanding.
```

- [ ] **Step 8: Create `fixtures/submissions/metadata.yml`**

```yaml
students:
  - submission_id: "111111"
    student_name: Alice Correct
    pdf: 111111.pdf
  - submission_id: "222222"
    student_name: Bob Notation
    pdf: 222222.pdf
  - submission_id: "333333"
    student_name: Carol Ambiguous
    pdf: 333333.pdf
  - submission_id: "444444"
    student_name: Dave Reversed
    pdf: 444444.pdf
  - submission_id: "555555"
    student_name: Eve Verbal
    pdf: 555555.pdf
```

- [ ] **Step 9: Create 5 transcription files**

`fixtures/transcriptions/111111.md` — Correct (uses population parameter symbols):
```markdown
## Q1
H₀: μ₁ = μ₂
H₁: μ₁ ≠ μ₂

## Q2
t = (x̄₁ - x̄₂) / SE
```

`fixtures/transcriptions/222222.md` — Minor communication error (sample mean instead of population mean):
```markdown
## Q1
H₀: x̄₁ = x̄₂
H₁: x̄₁ ≠ x̄₂

## Q2
t = (x̄₁ - x̄₂) / SE
```

`fixtures/transcriptions/333333.md` — Ambiguous (correct hypotheses plus a rejection rule):
```markdown
## Q1
H₀: μ₁ = μ₂
H₁: μ₁ ≠ μ₂
We reject H₀ when p < 0.05.

## Q2
t = (x̄₁ - x̄₂) / SE
```

`fixtures/transcriptions/444444.md` — Minor justification error (null and alternative reversed):
```markdown
## Q1
H₀: μ₁ ≠ μ₂
H₁: μ₁ = μ₂

## Q2
t = (x̄₁ - x̄₂) / SE
```

`fixtures/transcriptions/555555.md` — Major errors (verbal description, no notation):
```markdown
## Q1
The null says no difference. The other says there is.

## Q2
t = (x̄₁ - x̄₂) / SE
```

- [ ] **Step 10: Commit**

```bash
git add tests/evals/scenarios/
git commit -m "feat(evals): add grade-question scenario fixtures"
```

---

## Task 3: scenario.yml

**Files:**
- Create: `tests/evals/scenarios/grade-question/scenario.yml`

- [ ] **Step 1: Create `scenario.yml`**

```yaml
name: grade-question-basic-workflow
skill: grade-question
query: |
  Grade all 5 students for Q1. Use the grading workflow.
question_id: Q1
students:
  - "111111"
  - "222222"
  - "333333"
  - "444444"
  - "555555"
correct_students:
  - "111111"
reuse_cases:
  "222222": "Minor communication error"
  "444444": "Minor justification error"
prepopulate:
  Q2:
    grades: "Correct"
    comments: ""
    explanations: "Correct."
iterative_write_threshold_seconds: 5
structural_assertions:
  - grade_files_exist
  - no_null_grades
  - iterative_writes
  - valid_rubric_categories
  - correct_response_empty_comment
  - comment_single_sentence
  - comment_ends_with_question
  - comment_reuse_verbatim
  - grade_schema_valid
  - decisions_updated
  - decisions_entry_format
  - new_comment_in_comments_md
  - merge_preserves_other_questions
behavioral_observations:
  - "Claude should read workflow.yml, rubric.md, comments.md, decisions.md, instructor_profile.md, and answer_key.md before grading the first student (Step 1)"
  - "Claude should run check_progress.py and display the null count for Q1 before starting the loop (Step 1)"
  - "Claude should display the current comment strategy and ask for an override before starting the loop (Step 2)"
  - "Claude should pause on 333333 and ask the instructor a question before assigning a grade (Step 3f)"
  - "Claude should propose a draft comment for 555555 and wait for approval before writing (Step 3c)"
  - "During the QC pass, Claude should re-scan students graded before the ask-up ruling and report any inconsistencies (Step 4)"
  - "Claude should run check_progress.py at the end of the QC pass and confirm zero nulls remain for Q1 (Step 4)"
```

- [ ] **Step 2: Commit**

```bash
git add tests/evals/scenarios/grade-question/scenario.yml
git commit -m "feat(evals): add grade-question scenario.yml"
```

---

## Task 4: checker.py Foundation — `load_scenario` + `_parse_comments_md`

**Files:**
- Create: `tests/evals/checker.py`
- Create: `tests/evals/test_checker.py`
- Create: `tests/evals/conftest.py`

- [ ] **Step 1: Write the failing test**

`tests/evals/test_checker.py`:
```python
import json
import os
import sys
import time
import pytest

sys.path.insert(0, os.path.dirname(__file__))

from checker import load_scenario, _parse_comments_md

SCENARIO_PATH = os.path.join(
    os.path.dirname(__file__),
    "scenarios", "grade-question", "scenario.yml"
)


def test_load_scenario_returns_required_keys():
    scenario = load_scenario(SCENARIO_PATH)
    for key in ("name", "question_id", "students", "correct_students",
                "reuse_cases", "prepopulate", "iterative_write_threshold_seconds"):
        assert key in scenario, f"missing key: {key}"


def test_load_scenario_injects_fixture_dir():
    scenario = load_scenario(SCENARIO_PATH)
    assert "_fixture_dir" in scenario
    assert os.path.isdir(scenario["_fixture_dir"])


def test_load_scenario_students_are_strings():
    scenario = load_scenario(SCENARIO_PATH)
    for sid in scenario["students"]:
        assert isinstance(sid, str)


def test_parse_comments_md_extracts_comments():
    fixture_dir = os.path.join(
        os.path.dirname(__file__), "scenarios", "grade-question", "fixtures"
    )
    result = _parse_comments_md(os.path.join(fixture_dir, "comments.md"))
    assert "Q1" in result
    assert "Minor communication error" in result["Q1"]
    assert "Minor justification error" in result["Q1"]
    assert len(result["Q1"]["Minor communication error"]) == 1
    assert result["Q1"]["Minor communication error"][0] == (
        "Are you using the right symbol to represent a population mean here?"
    )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd C:\Users\Justin.Merrick\grading-toolkit
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_load_scenario_returns_required_keys -v
```

Expected: `ERROR` — `ModuleNotFoundError: No module named 'checker'`

- [ ] **Step 3: Implement `checker.py`**

`tests/evals/checker.py`:
```python
import json
import os
import re
import time
import yaml


def load_scenario(scenario_path: str) -> dict:
    with open(scenario_path) as f:
        scenario = yaml.safe_load(f)
    scenario["_fixture_dir"] = os.path.join(os.path.dirname(scenario_path), "fixtures")
    scenario["students"] = [str(s) for s in scenario["students"]]
    scenario["correct_students"] = [str(s) for s in scenario.get("correct_students", [])]
    scenario["reuse_cases"] = {str(k): v for k, v in scenario.get("reuse_cases", {}).items()}
    return scenario


def _parse_comments_md(comments_md_path: str) -> dict:
    """Return {question_id: {category: [comment_text, ...]}}."""
    with open(comments_md_path) as f:
        text = f.read()
    result = {}
    current_q = None
    current_cat = None
    for line in text.splitlines():
        if line.startswith("## "):
            current_q = line[3:].strip()
            result[current_q] = {}
            current_cat = None
        elif line.startswith("### ") and current_q is not None:
            current_cat = line[4:].strip()
            result[current_q][current_cat] = []
        elif line.startswith('- "') and current_q and current_cat:
            comment = line[3:].rstrip('"')
            result[current_q][current_cat].append(comment)
    return result
```

- [ ] **Step 4: Create `tests/evals/conftest.py`**

```python
import json
import os
import shutil
import sys
import pytest

sys.path.insert(0, os.path.dirname(__file__))

SCENARIO_PATH = os.path.join(
    os.path.dirname(__file__),
    "scenarios", "grade-question", "scenario.yml"
)

# Verbatim comments matching fixtures/comments.md
_REUSE_COMMENTS = {
    "Minor communication error": "Are you using the right symbol to represent a population mean here?",
    "Minor justification error": "Does this hypothesis reflect what would be true if there were no difference between groups?",
}

_PASSING_GRADES = {
    "111111": ("Correct",                      "",                                  "Correct answer."),
    "222222": ("Minor communication error",    _REUSE_COMMENTS["Minor communication error"],  "Used sample mean notation instead of population mean."),
    "333333": ("Minor justification error",    _REUSE_COMMENTS["Minor justification error"],  "Included a rejection rule in the hypothesis statement."),
    "444444": ("Minor justification error",    _REUSE_COMMENTS["Minor justification error"],  "Reversed null and alternative hypotheses."),
    "555555": ("Major errors or misconceptions", "Have you considered what symbols statisticians use to represent population parameters here?", "Used verbal description with no mathematical notation."),
}


@pytest.fixture
def scenario():
    from checker import load_scenario
    return load_scenario(SCENARIO_PATH)


@pytest.fixture
def result_dir(tmp_path, scenario):
    """Pre-populated passing result directory."""
    grades_dir = tmp_path / "workspace" / "grades"
    grades_dir.mkdir(parents=True)

    qid = scenario["question_id"]
    prepopulate = scenario.get("prepopulate", {})

    for sid in scenario["students"]:
        grade, comment, explanation = _PASSING_GRADES[sid]
        data = {
            "submission_id": sid,
            "grades": {qid: grade},
            "comments": {qid: comment},
            "explanations": {qid: explanation},
            "flags": [],
        }
        for other_qid, vals in prepopulate.items():
            for field in ("grades", "comments", "explanations"):
                data[field][other_qid] = vals[field]
        (grades_dir / f"{sid}_grades.json").write_text(json.dumps(data, indent=2))

    fixture_dir = scenario["_fixture_dir"]
    shutil.copy(os.path.join(fixture_dir, "decisions.md"), tmp_path / "decisions.md")
    shutil.copy(os.path.join(fixture_dir, "comments.md"), tmp_path / "comments.md")

    # Add a new decisions entry (so decisions_updated passes by default)
    with open(tmp_path / "decisions.md", "a") as f:
        f.write(
            "\n## Q1 — 2026-04-23\n"
            "**Case:** Student wrote correct hypotheses but included a p-value rejection rule.\n"
            "**Ruling:** Minor justification error — extra statement implies a decision rule is part of the hypothesis.\n"
            "**Applied to:** Carol Ambiguous\n"
        )

    # Add a new comment to comments.md Q1 section (so new_comment_in_comments_md passes)
    with open(tmp_path / "comments.md", "a") as f:
        f.write(
            "\n### Major errors or misconceptions\n"
            '- "Have you considered what symbols statisticians use to represent population parameters here?"\n'
        )

    return tmp_path

```

- [ ] **Step 5: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_load_scenario_returns_required_keys tests/evals/test_checker.py::test_load_scenario_injects_fixture_dir tests/evals/test_checker.py::test_load_scenario_students_are_strings tests/evals/test_checker.py::test_parse_comments_md_extracts_comments -v
```

Expected: `4 passed`

- [ ] **Step 6: Commit**

```bash
git add tests/evals/checker.py tests/evals/conftest.py tests/evals/test_checker.py
git commit -m "feat(evals): add checker foundation — load_scenario and _parse_comments_md"
```

---

## Task 5: checker.py — `check_grade_files_exist` + `check_grade_schema_valid`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_grade_files_exist, check_grade_schema_valid


def test_grade_files_exist_passes(result_dir, scenario):
    passed, detail = check_grade_files_exist(str(result_dir), scenario)
    assert passed
    assert "5/5" in detail


def test_grade_files_exist_fails_when_file_missing(result_dir, scenario):
    (result_dir / "workspace" / "grades" / "111111_grades.json").unlink()
    passed, detail = check_grade_files_exist(str(result_dir), scenario)
    assert not passed
    assert "111111" in detail


def test_grade_schema_valid_passes(result_dir, scenario):
    passed, detail = check_grade_schema_valid(str(result_dir), scenario)
    assert passed


def test_grade_schema_valid_fails_when_key_missing(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "222222_grades.json"
    data = json.loads(path.read_text())
    del data["flags"]
    path.write_text(json.dumps(data))
    passed, detail = check_grade_schema_valid(str(result_dir), scenario)
    assert not passed
    assert "222222" in detail
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_grade_files_exist_passes -v
```

Expected: `FAILED` — `ImportError: cannot import name 'check_grade_files_exist'`

- [ ] **Step 3: Implement the functions**

Append to `tests/evals/checker.py`:
```python
def check_grade_files_exist(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    missing = [
        sid for sid in scenario["students"]
        if not os.path.exists(os.path.join(grades_dir, f"{sid}_grades.json"))
    ]
    if missing:
        return False, f"Missing grade files: {missing}"
    n = len(scenario["students"])
    return True, f"{n}/{n} files created"


def check_grade_schema_valid(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    required_keys = {"grades", "comments", "explanations", "flags"}
    invalid = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        if not required_keys.issubset(data.keys()):
            invalid.append(sid)
    if invalid:
        return False, f"Missing required keys in: {invalid}"
    return True, f"all {len(scenario['students'])} valid"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "grade_files_exist or grade_schema_valid" -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add check_grade_files_exist and check_grade_schema_valid"
```

---

## Task 6: checker.py — `check_no_null_grades`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_no_null_grades


def test_no_null_grades_passes(result_dir, scenario):
    passed, detail = check_no_null_grades(str(result_dir), scenario)
    assert passed
    assert "all populated" in detail


def test_no_null_grades_fails_when_grade_is_null(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "333333_grades.json"
    data = json.loads(path.read_text())
    data["grades"]["Q1"] = None
    path.write_text(json.dumps(data))
    passed, detail = check_no_null_grades(str(result_dir), scenario)
    assert not passed
    assert "333333" in detail


def test_no_null_grades_fails_when_comment_is_null(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "444444_grades.json"
    data = json.loads(path.read_text())
    data["comments"]["Q1"] = None
    path.write_text(json.dumps(data))
    passed, detail = check_no_null_grades(str(result_dir), scenario)
    assert not passed
    assert "444444" in detail
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_no_null_grades_passes -v
```

Expected: `FAILED` — `ImportError: cannot import name 'check_no_null_grades'`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
def check_no_null_grades(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    qid = scenario["question_id"]
    nulls = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        for field in ("grades", "comments", "explanations"):
            if data[field].get(qid) is None:
                nulls.append(f"{sid}.{field}")
    if nulls:
        return False, f"Null values: {nulls}"
    return True, "all populated"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "no_null" -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add check_no_null_grades"
```

---

## Task 7: checker.py — `check_iterative_writes`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_iterative_writes


def test_iterative_writes_passes_with_spread(result_dir, scenario):
    grades_dir = result_dir / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario["students"]):
        path = grades_dir / f"{sid}_grades.json"
        os.utime(path, (base + i * 10, base + i * 10))
    passed, detail = check_iterative_writes(str(result_dir), scenario)
    assert passed
    assert "spread" in detail


def test_iterative_writes_fails_on_batch_write(result_dir, scenario):
    grades_dir = result_dir / "workspace" / "grades"
    same_time = time.time()
    for sid in scenario["students"]:
        path = grades_dir / f"{sid}_grades.json"
        os.utime(path, (same_time, same_time))
    passed, detail = check_iterative_writes(str(result_dir), scenario)
    assert not passed
    assert "batch write detected" in detail


def test_iterative_writes_uses_threshold_from_scenario(result_dir, scenario):
    # Spread of 3s should fail with default 5s threshold
    grades_dir = result_dir / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario["students"]):
        path = grades_dir / f"{sid}_grades.json"
        os.utime(path, (base + i * 0.6, base + i * 0.6))  # 0.6s apart = 2.4s spread
    passed, _ = check_iterative_writes(str(result_dir), scenario)
    assert not passed
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_iterative_writes_passes_with_spread -v
```

Expected: `FAILED` — `ImportError: cannot import name 'check_iterative_writes'`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
def check_iterative_writes(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    threshold = scenario.get("iterative_write_threshold_seconds", 5)
    mtimes = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        mtimes.append(os.path.getmtime(path))
    spread = max(mtimes) - min(mtimes)
    if spread <= threshold:
        return False, f"spread {spread:.1f}s — batch write detected (threshold: {threshold}s)"
    return True, f"spread {spread:.1f}s (threshold: {threshold}s)"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "iterative_writes" -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add check_iterative_writes"
```

---

## Task 8: checker.py — `check_valid_rubric_categories` + `check_correct_response_empty_comment`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_valid_rubric_categories, check_correct_response_empty_comment


def test_valid_rubric_categories_passes(result_dir, scenario):
    passed, detail = check_valid_rubric_categories(str(result_dir), scenario)
    assert passed


def test_valid_rubric_categories_fails_on_unknown_category(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "555555_grades.json"
    data = json.loads(path.read_text())
    data["grades"]["Q1"] = "Completely Wrong"
    path.write_text(json.dumps(data))
    passed, detail = check_valid_rubric_categories(str(result_dir), scenario)
    assert not passed
    assert "555555" in detail


def test_correct_response_empty_comment_passes(result_dir, scenario):
    passed, detail = check_correct_response_empty_comment(str(result_dir), scenario)
    assert passed
    assert "111111" in detail


def test_correct_response_empty_comment_fails_when_nonempty(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "111111_grades.json"
    data = json.loads(path.read_text())
    data["comments"]["Q1"] = "Good job!"
    path.write_text(json.dumps(data))
    passed, detail = check_correct_response_empty_comment(str(result_dir), scenario)
    assert not passed
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_valid_rubric_categories_passes -v
```

Expected: `FAILED` — `ImportError`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
def check_valid_rubric_categories(result_dir: str, scenario: dict) -> tuple:
    fixture_dir = scenario["_fixture_dir"]
    with open(os.path.join(fixture_dir, "rubric.md")) as f:
        rubric_text = f.read()
    valid = {line[2:].strip() for line in rubric_text.splitlines() if line.startswith("- ")}

    grades_dir = os.path.join(result_dir, "workspace", "grades")
    qid = scenario["question_id"]
    invalid = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        grade = data["grades"].get(qid)
        if grade is not None and grade not in valid:
            invalid.append(f"{sid}: '{grade}'")
    if invalid:
        return False, f"Invalid categories: {invalid}"
    return True, f"all {len(scenario['students'])} valid categories"


def check_correct_response_empty_comment(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    qid = scenario["question_id"]
    failing = []
    for sid in scenario["correct_students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        comment = data["comments"].get(qid)
        if comment != "":
            failing.append(f"{sid}: comment is {repr(comment)}")
    if failing:
        return False, f"Correct-response comments not empty: {failing}"
    n = len(scenario["correct_students"])
    return True, f"{', '.join(scenario['correct_students'])} comment is empty string"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "rubric_categories or correct_response" -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add check_valid_rubric_categories and check_correct_response_empty_comment"
```

---

## Task 9: checker.py — `check_comment_single_sentence` + `check_comment_ends_with_question`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_comment_single_sentence, check_comment_ends_with_question


def test_comment_single_sentence_passes(result_dir, scenario):
    passed, detail = check_comment_single_sentence(str(result_dir), scenario)
    assert passed


def test_comment_single_sentence_fails_on_two_sentences(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "222222_grades.json"
    data = json.loads(path.read_text())
    data["comments"]["Q1"] = "Is this right? Have you checked the notation?"
    path.write_text(json.dumps(data))
    passed, detail = check_comment_single_sentence(str(result_dir), scenario)
    assert not passed
    assert "222222" in detail


def test_comment_ends_with_question_passes(result_dir, scenario):
    passed, detail = check_comment_ends_with_question(str(result_dir), scenario)
    assert passed


def test_comment_ends_with_question_fails_on_statement(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "444444_grades.json"
    data = json.loads(path.read_text())
    data["comments"]["Q1"] = "This hypothesis is reversed."
    path.write_text(json.dumps(data))
    passed, detail = check_comment_ends_with_question(str(result_dir), scenario)
    assert not passed
    assert "444444" in detail
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_comment_single_sentence_passes -v
```

Expected: `FAILED` — `ImportError`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
def check_comment_single_sentence(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    qid = scenario["question_id"]
    failing = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        comment = data["comments"].get(qid, "")
        if not comment:
            continue
        count = len(re.findall(r'[.?!]', comment))
        if count != 1:
            failing.append(f"{sid}: '{comment}' ({count} terminal marks)")
    if failing:
        return False, f"Multi-sentence or no-sentence comments: {failing}"
    return True, "all non-empty comments: 1 sentence"


def check_comment_ends_with_question(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    qid = scenario["question_id"]
    failing = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        comment = data["comments"].get(qid, "")
        if comment and not comment.rstrip().endswith("?"):
            failing.append(sid)
    if failing:
        return False, f"Comments not ending with ?: {failing}"
    return True, "all non-empty comments end with ?"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "single_sentence or ends_with_question" -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add comment format assertions"
```

---

## Task 10: checker.py — `check_comment_reuse_verbatim`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_comment_reuse_verbatim


def test_comment_reuse_verbatim_passes(result_dir, scenario):
    passed, detail = check_comment_reuse_verbatim(str(result_dir), scenario)
    assert passed
    assert "222222" in detail
    assert "444444" in detail


def test_comment_reuse_verbatim_fails_when_paraphrased(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "222222_grades.json"
    data = json.loads(path.read_text())
    data["comments"]["Q1"] = "Have you used the correct symbol for the population mean?"
    path.write_text(json.dumps(data))
    passed, detail = check_comment_reuse_verbatim(str(result_dir), scenario)
    assert not passed
    assert "222222" in detail


def test_comment_reuse_verbatim_fails_when_empty(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "444444_grades.json"
    data = json.loads(path.read_text())
    data["comments"]["Q1"] = ""
    path.write_text(json.dumps(data))
    passed, detail = check_comment_reuse_verbatim(str(result_dir), scenario)
    assert not passed
    assert "444444" in detail
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_comment_reuse_verbatim_passes -v
```

Expected: `FAILED` — `ImportError`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
def check_comment_reuse_verbatim(result_dir: str, scenario: dict) -> tuple:
    fixture_dir = scenario["_fixture_dir"]
    comments_map = _parse_comments_md(os.path.join(fixture_dir, "comments.md"))
    qid = scenario["question_id"]
    reuse_cases = scenario.get("reuse_cases", {})

    grades_dir = os.path.join(result_dir, "workspace", "grades")
    failing = []
    for sid, category in reuse_cases.items():
        expected = comments_map.get(qid, {}).get(category, [])
        if not expected:
            failing.append(f"{sid}: no fixture comment for category '{category}'")
            continue
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        actual = data["comments"].get(qid, "")
        if actual not in expected:
            failing.append(f"{sid}: '{actual}' not in fixture comments for '{category}'")
    if failing:
        return False, f"Verbatim reuse failed: {failing}"
    return True, f"exact match for {list(reuse_cases.keys())}"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "reuse_verbatim" -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add check_comment_reuse_verbatim"
```

---

## Task 11: checker.py — `check_decisions_updated` + `check_decisions_entry_format`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_decisions_updated, check_decisions_entry_format


def test_decisions_updated_passes(result_dir, scenario):
    passed, detail = check_decisions_updated(str(result_dir), scenario)
    assert passed
    assert "new entry" in detail


def test_decisions_updated_fails_when_unchanged(result_dir, scenario):
    # Overwrite with fixture baseline (empty)
    fixture_dir = scenario["_fixture_dir"]
    import shutil
    shutil.copy(os.path.join(fixture_dir, "decisions.md"), result_dir / "decisions.md")
    passed, detail = check_decisions_updated(str(result_dir), scenario)
    assert not passed


def test_decisions_entry_format_passes(result_dir, scenario):
    passed, detail = check_decisions_entry_format(str(result_dir), scenario)
    assert passed
    assert "required fields present" in detail


def test_decisions_entry_format_fails_when_missing_ruling(result_dir, scenario):
    with open(result_dir / "decisions.md", "w") as f:
        f.write("## Q1 — 2026-04-23\n**Case:** some case\n**Applied to:** someone\n")
    passed, detail = check_decisions_entry_format(str(result_dir), scenario)
    assert not passed
    assert "**Ruling:**" in detail
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_decisions_updated_passes -v
```

Expected: `FAILED` — `ImportError`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
def check_decisions_updated(result_dir: str, scenario: dict) -> tuple:
    fixture_dir = scenario["_fixture_dir"]
    qid = scenario["question_id"]
    with open(os.path.join(fixture_dir, "decisions.md")) as f:
        baseline = f.read()
    with open(os.path.join(result_dir, "decisions.md")) as f:
        current = f.read()
    baseline_count = baseline.count(f"## {qid} —")
    current_count = current.count(f"## {qid} —")
    new_entries = current_count - baseline_count
    if new_entries < 1:
        return False, "no new entries"
    return True, f"{new_entries} new entry/entries"


def check_decisions_entry_format(result_dir: str, scenario: dict) -> tuple:
    fixture_dir = scenario["_fixture_dir"]
    qid = scenario["question_id"]
    with open(os.path.join(fixture_dir, "decisions.md")) as f:
        baseline = f.read()
    with open(os.path.join(result_dir, "decisions.md")) as f:
        current = f.read()
    new_content = current[len(baseline):]
    if not new_content.strip():
        return False, "no new entries to check"
    required = ["**Case:**", "**Ruling:**", "**Applied to:**", f"## {qid} —"]
    missing = [field for field in required if field not in new_content]
    if missing:
        return False, f"missing required fields: {missing}"
    return True, "required fields present"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "decisions" -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add decisions assertions"
```

---

## Task 12: checker.py — `check_new_comment_in_comments_md` + `check_merge_preserves_other_questions`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import check_new_comment_in_comments_md, check_merge_preserves_other_questions


def test_new_comment_in_comments_md_passes(result_dir, scenario):
    passed, detail = check_new_comment_in_comments_md(str(result_dir), scenario)
    assert passed


def test_new_comment_in_comments_md_fails_when_unchanged(result_dir, scenario):
    import shutil
    fixture_dir = scenario["_fixture_dir"]
    shutil.copy(os.path.join(fixture_dir, "comments.md"), result_dir / "comments.md")
    passed, detail = check_new_comment_in_comments_md(str(result_dir), scenario)
    assert not passed


def test_merge_preserves_other_questions_passes(result_dir, scenario):
    passed, detail = check_merge_preserves_other_questions(str(result_dir), scenario)
    assert passed
    assert "Q2" in detail


def test_merge_preserves_other_questions_fails_when_q2_overwritten(result_dir, scenario):
    path = result_dir / "workspace" / "grades" / "111111_grades.json"
    data = json.loads(path.read_text())
    data["grades"]["Q2"] = None   # simulate overwrite
    path.write_text(json.dumps(data))
    passed, detail = check_merge_preserves_other_questions(str(result_dir), scenario)
    assert not passed
    assert "111111" in detail
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_new_comment_in_comments_md_passes -v
```

Expected: `FAILED` — `ImportError`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
def _extract_q_section(text: str, qid: str) -> str:
    lines = text.splitlines()
    in_section = False
    section_lines = []
    for line in lines:
        if line.strip() == f"## {qid}":
            in_section = True
            continue
        if line.startswith("## ") and in_section:
            break
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines)


def check_new_comment_in_comments_md(result_dir: str, scenario: dict) -> tuple:
    fixture_dir = scenario["_fixture_dir"]
    qid = scenario["question_id"]
    with open(os.path.join(fixture_dir, "comments.md")) as f:
        baseline = f.read()
    with open(os.path.join(result_dir, "comments.md")) as f:
        current = f.read()
    baseline_section = _extract_q_section(baseline, qid)
    current_section = _extract_q_section(current, qid)
    if len(current_section.strip()) <= len(baseline_section.strip()):
        return False, f"{qid} section unchanged"
    return True, f"{qid} section updated"


def check_merge_preserves_other_questions(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    prepopulate = scenario.get("prepopulate", {})
    if not prepopulate:
        return True, "no other questions to check"
    failing = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        for other_qid, expected in prepopulate.items():
            for field in ("grades", "comments", "explanations"):
                actual = data[field].get(other_qid)
                exp_val = expected.get(field)
                if actual != exp_val:
                    failing.append(
                        f"{sid}.{field}.{other_qid}: expected {repr(exp_val)}, got {repr(actual)}"
                    )
    if failing:
        return False, f"Other question data corrupted: {failing}"
    other_qids = list(prepopulate.keys())
    return True, f"{other_qids} data unchanged in all {len(scenario['students'])} files"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -k "new_comment or merge_preserves" -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add new_comment_in_comments_md and merge_preserves assertions"
```

---

## Task 13: checker.py — `run_all_assertions`

**Files:**
- Modify: `tests/evals/checker.py`
- Modify: `tests/evals/test_checker.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/evals/test_checker.py`:
```python
from checker import run_all_assertions, ASSERTIONS


def test_run_all_assertions_returns_all_keys(result_dir, scenario):
    # Use spread mtimes so iterative_writes passes
    grades_dir = result_dir / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario["students"]):
        os.utime(grades_dir / f"{sid}_grades.json", (base + i * 10, base + i * 10))

    results = run_all_assertions(str(result_dir), scenario)
    expected_keys = {fn.__name__.replace("check_", "") for fn in ASSERTIONS}
    assert set(results.keys()) == expected_keys


def test_run_all_assertions_result_has_pass_and_detail(result_dir, scenario):
    grades_dir = result_dir / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario["students"]):
        os.utime(grades_dir / f"{sid}_grades.json", (base + i * 10, base + i * 10))

    results = run_all_assertions(str(result_dir), scenario)
    for name, result in results.items():
        assert "pass" in result, f"missing 'pass' in {name}"
        assert "detail" in result, f"missing 'detail' in {name}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py::test_run_all_assertions_returns_all_keys -v
```

Expected: `FAILED` — `ImportError: cannot import name 'run_all_assertions'`

- [ ] **Step 3: Implement**

Append to `tests/evals/checker.py`:
```python
ASSERTIONS = [
    check_grade_files_exist,
    check_no_null_grades,
    check_iterative_writes,
    check_valid_rubric_categories,
    check_correct_response_empty_comment,
    check_comment_single_sentence,
    check_comment_ends_with_question,
    check_comment_reuse_verbatim,
    check_grade_schema_valid,
    check_decisions_updated,
    check_decisions_entry_format,
    check_new_comment_in_comments_md,
    check_merge_preserves_other_questions,
]


def run_all_assertions(result_dir: str, scenario: dict) -> dict:
    results = {}
    for fn in ASSERTIONS:
        name = fn.__name__.replace("check_", "")
        passed, detail = fn(result_dir, scenario)
        results[name] = {"pass": passed, "detail": detail}
    return results
```

- [ ] **Step 4: Run ALL checker tests**

```bash
conda run -n grading_toolkit pytest tests/evals/test_checker.py -v
```

Expected: all tests pass. If any fail, fix before continuing.

- [ ] **Step 5: Commit**

```bash
git add tests/evals/checker.py tests/evals/test_checker.py
git commit -m "feat(evals): add run_all_assertions and ASSERTIONS registry"
```

---

## Task 14: runner.py — `provision_directory`

**Files:**
- Create: `tests/evals/runner.py`
- Create: `tests/evals/test_runner.py`

- [ ] **Step 1: Write the failing tests**

`tests/evals/test_runner.py`:
```python
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(__file__))

from runner import provision_directory, _find_toolkit_root
from checker import load_scenario

SCENARIO_PATH = os.path.join(
    os.path.dirname(__file__),
    "scenarios", "grade-question", "scenario.yml"
)


@pytest.fixture
def scenario():
    return load_scenario(SCENARIO_PATH)


def test_provision_creates_workspace_dirs(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=False)
    assert (tmp_path / "workspace" / "grades").is_dir()
    assert (tmp_path / "workspace" / "transcriptions").is_dir()
    assert (tmp_path / "workspace" / "pages").is_dir()


def test_provision_copies_top_level_fixtures(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=False)
    assert (tmp_path / "workflow.yml").exists()
    assert (tmp_path / "rubric.md").exists()
    assert (tmp_path / "comments.md").exists()
    assert (tmp_path / "decisions.md").exists()


def test_provision_copies_transcriptions_to_workspace(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=False)
    trans_dir = tmp_path / "workspace" / "transcriptions"
    for sid in scenario["students"]:
        assert (trans_dir / f"{sid}.md").exists(), f"Missing {sid}.md"


def test_provision_copies_scripts(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=False)
    scripts_dir = tmp_path / "scripts"
    assert scripts_dir.is_dir()
    assert (scripts_dir / "check_progress.py").exists()


def test_provision_creates_grade_stubs_with_null_q1(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=False)
    for sid in scenario["students"]:
        path = tmp_path / "workspace" / "grades" / f"{sid}_grades.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["grades"]["Q1"] is None
        assert data["comments"]["Q1"] is None


def test_provision_prepopulates_q2(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=False)
    for sid in scenario["students"]:
        path = tmp_path / "workspace" / "grades" / f"{sid}_grades.json"
        data = json.loads(path.read_text())
        assert data["grades"]["Q2"] == "Correct"
        assert data["comments"]["Q2"] == ""
        assert data["explanations"]["Q2"] == "Correct."


def test_provision_injects_skill_into_claude_md(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=True)
    claude_md = (tmp_path / "CLAUDE.md").read_text()
    assert "grade-question" in claude_md.lower()
    assert len(claude_md) > 100


def test_provision_writes_empty_claude_md_without_skill(tmp_path, scenario):
    fixture_dir = scenario["_fixture_dir"]
    provision_directory(str(tmp_path), fixture_dir, scenario, with_skill=False)
    claude_md = (tmp_path / "CLAUDE.md").read_text()
    assert claude_md.strip() == ""
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
conda run -n grading_toolkit pytest tests/evals/test_runner.py::test_provision_creates_workspace_dirs -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'runner'`

- [ ] **Step 3: Implement `runner.py`**

`tests/evals/runner.py`:
```python
import json
import os
import shutil
import subprocess
import sys
import time
import yaml
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from checker import load_scenario, run_all_assertions


def _find_toolkit_root(file: str) -> str:
    """Navigate up from tests/evals/ to repo root."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(file))))


def provision_directory(dest_dir: str, fixture_dir: str, scenario: dict, with_skill: bool):
    os.makedirs(dest_dir, exist_ok=True)

    # Copy top-level fixture files
    for item in os.listdir(fixture_dir):
        src = os.path.join(fixture_dir, item)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dest_dir, item))

    # Copy submissions/ as-is
    shutil.copytree(
        os.path.join(fixture_dir, "submissions"),
        os.path.join(dest_dir, "submissions"),
    )

    # Copy transcriptions/ → workspace/transcriptions/
    workspace_trans = os.path.join(dest_dir, "workspace", "transcriptions")
    os.makedirs(workspace_trans, exist_ok=True)
    for f in os.listdir(os.path.join(fixture_dir, "transcriptions")):
        shutil.copy2(
            os.path.join(fixture_dir, "transcriptions", f),
            os.path.join(workspace_trans, f),
        )

    # Create remaining workspace dirs
    for subdir in ("workspace/grades", "workspace/pages"):
        os.makedirs(os.path.join(dest_dir, subdir), exist_ok=True)

    # Copy scripts from skills/grade-init/scripts/
    toolkit_root = _find_toolkit_root(__file__)
    scripts_src = os.path.join(toolkit_root, "skills", "grade-init", "scripts")
    scripts_dst = os.path.join(dest_dir, "scripts")
    os.makedirs(scripts_dst, exist_ok=True)
    for f in os.listdir(scripts_src):
        if f.endswith(".py"):
            shutil.copy2(os.path.join(scripts_src, f), os.path.join(scripts_dst, f))

    # Pre-populate grade stubs
    qid = scenario["question_id"]
    prepopulate = scenario.get("prepopulate", {})
    for sid in scenario["students"]:
        stub = {
            "submission_id": sid,
            "grades": {qid: None},
            "comments": {qid: None},
            "explanations": {qid: None},
            "flags": [],
        }
        for other_qid, vals in prepopulate.items():
            for field in ("grades", "comments", "explanations"):
                stub[field][other_qid] = vals.get(field)
        grade_path = os.path.join(dest_dir, "workspace", "grades", f"{sid}_grades.json")
        with open(grade_path, "w") as f:
            json.dump(stub, f, indent=2)

    # Inject skill or write empty CLAUDE.md
    skill_content = ""
    if with_skill:
        toolkit_root = _find_toolkit_root(__file__)
        skill_path = os.path.join(toolkit_root, "skills", "grade-question", "SKILL.md")
        with open(skill_path) as f:
            skill_content = f.read()
    with open(os.path.join(dest_dir, "CLAUDE.md"), "w") as f:
        f.write(skill_content)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
conda run -n grading_toolkit pytest tests/evals/test_runner.py -v
```

Expected: all 8 pass.

- [ ] **Step 5: Commit**

```bash
git add tests/evals/runner.py tests/evals/test_runner.py
git commit -m "feat(evals): add provision_directory and test_runner"
```

---

## Task 15: runner.py — `run_claude`, `write_results`, `compare_results`, CLI

**Files:**
- Modify: `tests/evals/runner.py`

No unit tests for `run_claude` (it shells out to `claude`). `write_results` and `compare_results` are tested implicitly via the end-to-end flow described in the spec's Verification section.

- [ ] **Step 1: Implement `run_claude`**

Append to `tests/evals/runner.py`:
```python
_BEHAVIORAL_KEYS = [
    "files_read_before_grading",
    "progress_check_at_start",
    "strategy_confirmation",
    "ask_up_before_writing",
    "collaborative_draft",
    "qc_rescan_mentioned",
    "final_progress_check",
]


def run_claude(work_dir: str, query: str) -> tuple:
    """Run claude -p in work_dir. Returns (combined_output, duration_seconds)."""
    start = time.time()
    result = subprocess.run(
        ["claude", "-p", query, "--dangerously-skip-permissions"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    duration = time.time() - start
    return result.stdout + result.stderr, duration
```

- [ ] **Step 2: Implement `write_results`**

Append to `tests/evals/runner.py`:
```python
def write_results(
    results_dir: str,
    timestamp_str: str,
    scenario_name: str,
    skill_version: str,
    with_structural: dict,
    without_structural: dict,
    with_log_path: str,
    without_log_path: str,
) -> str:
    data = {
        "timestamp": timestamp_str,
        "scenario": scenario_name,
        "skill_version": skill_version,
        "results": {
            "with_skill": {
                "structural": with_structural,
                "behavioral": {k: {"pass": None, "note": ""} for k in _BEHAVIORAL_KEYS},
                "stdout_log": os.path.basename(with_log_path),
            },
            "without_skill": {
                "structural": without_structural,
                "behavioral": {k: {"pass": None, "note": ""} for k in _BEHAVIORAL_KEYS},
                "stdout_log": os.path.basename(without_log_path),
            },
        },
    }
    output_path = os.path.join(results_dir, f"{timestamp_str}-results.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    return output_path
```

- [ ] **Step 3: Implement `compare_results`**

Append to `tests/evals/runner.py`:
```python
def compare_results(results_dir: str):
    result_files = sorted(
        f for f in os.listdir(results_dir) if f.endswith("-results.json")
    )
    if not result_files:
        print("No results found.")
        return

    by_scenario: dict = {}
    for fname in result_files:
        with open(os.path.join(results_dir, fname)) as f:
            data = json.load(f)
        date = data["timestamp"][:10]
        name = data["scenario"]
        by_scenario.setdefault(name, []).append((date, data))

    for scenario_name, runs in by_scenario.items():
        print(f"\nscenario: {scenario_name}\n")
        dates = [r[0] for r in runs]
        pad = 32
        print(" " * pad + "  ".join(f"{d:>10}" for d in dates))
        for run_type in ("with_skill", "without_skill"):
            for check_type in ("structural", "behavioral"):
                scores = []
                for _, d in runs:
                    check_data = d["results"][run_type][check_type]
                    total = len(check_data)
                    passed = sum(1 for v in check_data.values() if v.get("pass") is True)
                    scores.append(f"{passed}/{total}")
                label = f"{run_type} / {check_type}"
                print(f"  {label:<{pad-2}}" + "  ".join(f"{s:>10}" for s in scores))
```

- [ ] **Step 4: Implement the CLI entry point**

Append to `tests/evals/runner.py`:
```python
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run grade-question skill evals")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--scenario",
        metavar="SCENARIO_PATH",
        help="Scenario path relative to tests/evals/scenarios/ (e.g. grade-question/basic-workflow)",
    )
    group.add_argument(
        "--compare",
        action="store_true",
        help="Print regression table across all saved results",
    )
    args = parser.parse_args()

    evals_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(evals_dir, "results")
    toolkit_root = _find_toolkit_root(__file__)

    if args.compare:
        compare_results(results_dir)
        return

    scenario_path = os.path.join(evals_dir, "scenarios", args.scenario, "scenario.yml")
    scenario = load_scenario(scenario_path)
    fixture_dir = scenario["_fixture_dir"]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    run_root = os.path.join(results_dir, ts)
    os.makedirs(run_root, exist_ok=True)

    for label, with_skill in (("with_skill", True), ("without_skill", False)):
        work_dir = os.path.join(run_root, label)
        print(f"\n[{label}] Provisioning {work_dir} ...")
        provision_directory(work_dir, fixture_dir, scenario, with_skill=with_skill)

        print(f"[{label}] Running claude -p ...")
        output, duration = run_claude(work_dir, scenario["query"])
        log_path = os.path.join(results_dir, f"{ts}-{label}-stdout.txt")
        with open(log_path, "w") as f:
            f.write(output)
        print(f"[{label}] Completed in {duration:.1f}s. Log: {log_path}")

        assertions = run_all_assertions(work_dir, scenario)
        passed = sum(1 for v in assertions.values() if v["pass"])
        total = len(assertions)
        print(f"[{label}] Structural: {passed}/{total} passed")
        for name, result in assertions.items():
            status = "PASS" if result["pass"] else "FAIL"
            print(f"  [{status}] {name}: {result['detail']}")

        if label == "with_skill":
            with_structural = assertions
            with_log = log_path
        else:
            without_structural = assertions
            without_log = log_path

    results_path = write_results(
        results_dir, ts, scenario["name"], "1.0.0",
        with_structural, without_structural, with_log, without_log,
    )
    print(f"\nResults written to: {results_path}")
    print("Open stdout logs and fill in behavioral pass/fail manually.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Verify the CLI help text works**

```bash
conda run -n grading_toolkit python tests/evals/runner.py --help
```

Expected: usage text showing `--scenario` and `--compare` options with no errors.

- [ ] **Step 6: Run all tests one final time**

```bash
conda run -n grading_toolkit pytest tests/evals/ -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add tests/evals/runner.py
git commit -m "feat(evals): add runner CLI — run_claude, write_results, compare_results"
```

---

## Verification Checklist

After all tasks complete, validate the full system end-to-end:

- [ ] `python tests/evals/runner.py --scenario grade-question` runs without error
- [ ] Two temp directories are created and populated (`workflow.yml`, `workspace/transcriptions/*.md`, `scripts/check_progress.py` all present)
- [ ] `claude -p` runs in both directories and writes grade JSONs to `workspace/grades/`
- [ ] `<timestamp>-results.json` is written with all 13 structural assertions populated
- [ ] Open the with_skill stdout log and manually fill in behavioral pass/fail
- [ ] **Regression test:** remove the ask-up paragraph from `skills/grade-question/SKILL.md`, re-run, confirm `decisions_updated` regresses from pass → fail in `with_skill`
- [ ] Restore `SKILL.md` after regression test

---

## Constraints Not Tested

| Constraint | Why |
|---|---|
| Comment does not reveal the answer | Requires semantic comparison against answer key — human judgment only |
| Progress check every 10 students (Step 3e) | 5-student scenario never reaches the 10-student threshold |
