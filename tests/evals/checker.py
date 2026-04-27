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
            comment = line[3:-1]
            result[current_q][current_cat].append(comment)
    return result


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
