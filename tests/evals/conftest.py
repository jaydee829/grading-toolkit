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

_REUSE_COMMENTS = {
    "Minor communication error": "Are you using the right symbol to represent a population mean here?",
    "Minor justification error": "Does this hypothesis reflect what would be true if there were no difference between groups?",
}

_PASSING_GRADES = {
    "111111": ("Correct", "", "Correct answer."),
    "222222": ("Minor communication error", _REUSE_COMMENTS["Minor communication error"], "Used sample mean notation instead of population mean."),
    "333333": ("Minor justification error", _REUSE_COMMENTS["Minor justification error"], "Included a rejection rule in the hypothesis statement."),
    "444444": ("Minor justification error", _REUSE_COMMENTS["Minor justification error"], "Reversed null and alternative hypotheses."),
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

    with open(tmp_path / "decisions.md", "a") as f:
        f.write(
            "\n## Q1 — 2026-04-23\n"
            "**Case:** Student wrote correct hypotheses but included a p-value rejection rule.\n"
            "**Ruling:** Minor justification error — extra statement implies a decision rule is part of the hypothesis.\n"
            "**Applied to:** Carol Ambiguous\n"
        )

    with open(tmp_path / "comments.md", "a") as f:
        f.write(
            "\n### Major errors or misconceptions\n"
            '- "Have you considered what symbols statisticians use to represent population parameters here?"\n'
        )

    return tmp_path
