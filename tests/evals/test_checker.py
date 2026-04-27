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
    grades_dir = result_dir / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario["students"]):
        path = grades_dir / f"{sid}_grades.json"
        os.utime(path, (base + i * 0.6, base + i * 0.6))  # 2.4s spread < 5s threshold
    passed, _ = check_iterative_writes(str(result_dir), scenario)
    assert not passed
