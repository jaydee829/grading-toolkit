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
    return True, f"{', '.join(scenario['correct_students'])} comment is empty string"


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
