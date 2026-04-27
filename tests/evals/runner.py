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
