import json
import os
import sys
import time
import pytest

sys.path.insert(0, os.path.dirname(__file__))
from checker import load_scenario, run_all_assertions

STRICT_SCENARIO_PATH = os.path.join(
    os.path.dirname(__file__),
    "scenarios", "grade-question-strict", "scenario.yml"
)

_STRICT_REUSE_COMMENTS = {
    "Minor communication error": "Are you using the right symbol to represent a population mean here?",
    "Minor justification error": "Does this hypothesis reflect what would be true if there were no difference between groups?",
}

_STRICT_PASSING_GRADES = {
    "111111": ("Correct", "", "Correct answer."),
    "222222": ("Minor communication error", _STRICT_REUSE_COMMENTS["Minor communication error"], "Used sample mean notation."),
    "333333": ("Correct", "", "Correct answer."),
    "444444": ("Minor justification error", _STRICT_REUSE_COMMENTS["Minor justification error"], "Reversed null and alternative."),
    "555555": ("Major errors or misconceptions", "Have you considered what symbols statisticians use to represent population parameters here?", "Used verbal description only."),
}


@pytest.fixture
def scenario_strict():
    return load_scenario(STRICT_SCENARIO_PATH)


@pytest.fixture
def result_dir_strict(tmp_path, scenario_strict):
    import shutil
    grades_dir = tmp_path / "workspace" / "grades"
    grades_dir.mkdir(parents=True)

    qid = scenario_strict["question_id"]
    prepopulate = scenario_strict.get("prepopulate", {})

    for sid in scenario_strict["students"]:
        grade, comment, explanation = _STRICT_PASSING_GRADES[sid]
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

    fixture_dir = scenario_strict["_fixture_dir"]
    shutil.copy(os.path.join(fixture_dir, "decisions.md"), tmp_path / "decisions.md")
    shutil.copy(os.path.join(fixture_dir, "comments.md"), tmp_path / "comments.md")

    # Strict mode: no decisions entry (no ask-up triggered), but new comment IS written
    with open(tmp_path / "comments.md", "a") as f:
        f.write(
            "\n### Major errors or misconceptions\n"
            '- "Have you considered what symbols statisticians use to represent population parameters here?"\n'
        )

    return tmp_path


def test_strict_scenario_loads():
    scenario = load_scenario(STRICT_SCENARIO_PATH)
    assert scenario["name"] == "grade-question-strict-workflow"
    assert "333333" in scenario["correct_students"]
    assert "111111" in scenario["correct_students"]


def test_strict_scenario_has_interaction_required_for_decisions():
    scenario = load_scenario(STRICT_SCENARIO_PATH)
    ir = scenario.get("interaction_required_assertions", [])
    assert "decisions_updated" in ir
    assert "decisions_entry_format" in ir
    assert "new_comment_in_comments_md" not in ir


def test_strict_all_assertions_pass(result_dir_strict, scenario_strict):
    grades_dir = result_dir_strict / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario_strict["students"]):
        os.utime(grades_dir / f"{sid}_grades.json", (base + i * 10, base + i * 10))

    results = run_all_assertions(str(result_dir_strict), scenario_strict, unattended=True)
    failing = {name: r for name, r in results.items() if r["pass"] is False}
    assert not failing, f"Assertions failed: {failing}"
