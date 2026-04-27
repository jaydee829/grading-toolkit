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
