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


from checker import check_decisions_updated, check_decisions_entry_format


def test_decisions_updated_passes(result_dir, scenario):
    passed, detail = check_decisions_updated(str(result_dir), scenario)
    assert passed
    assert "new entry" in detail


def test_decisions_updated_fails_when_unchanged(result_dir, scenario):
    import shutil
    fixture_dir = scenario["_fixture_dir"]
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
    data["grades"]["Q2"] = None
    path.write_text(json.dumps(data))
    passed, detail = check_merge_preserves_other_questions(str(result_dir), scenario)
    assert not passed
    assert "111111" in detail


from checker import run_all_assertions, ASSERTIONS


def test_run_all_assertions_returns_all_keys(result_dir, scenario):
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


def test_run_all_assertions_skips_interaction_required_in_unattended_mode(result_dir, scenario):
    interaction_required = scenario.get("interaction_required_assertions", [])
    assert interaction_required, "scenario must define interaction_required_assertions"
    import time
    grades_dir = result_dir / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario["students"]):
        os.utime(grades_dir / f"{sid}_grades.json", (base + i * 10, base + i * 10))
    results = run_all_assertions(str(result_dir), scenario, unattended=True)
    for name in interaction_required:
        assert results[name]["pass"] is None, f"{name} should be null in unattended mode"
        assert "skipped" in results[name]["detail"]


def test_run_all_assertions_runs_interaction_required_when_attended(result_dir, scenario):
    import time
    grades_dir = result_dir / "workspace" / "grades"
    base = time.time()
    for i, sid in enumerate(scenario["students"]):
        os.utime(grades_dir / f"{sid}_grades.json", (base + i * 10, base + i * 10))
    results = run_all_assertions(str(result_dir), scenario, unattended=False)
    for name in scenario.get("interaction_required_assertions", []):
        assert results[name]["pass"] is not None, f"{name} should run when unattended=False"
