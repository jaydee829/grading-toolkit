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
