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


def check_nonzero_grades_have_comments(result_dir: str, scenario: dict) -> tuple:
    grades_dir = os.path.join(result_dir, "workspace", "grades")
    qid = scenario["question_id"]
    skip_grades = {"Correct", "Blank", None}
    failing = []
    for sid in scenario["students"]:
        path = os.path.join(grades_dir, f"{sid}_grades.json")
        with open(path) as f:
            data = json.load(f)
        grade = data["grades"].get(qid)
        comment = data["comments"].get(qid, "")
        if grade not in skip_grades and not comment:
            failing.append(f"{sid}: grade='{grade}' but comment is empty")
    if failing:
        return False, f"Non-correct grades with empty comments: {failing}"
    return True, "all non-correct grades have comments"


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


ASSERTIONS = [
    check_grade_files_exist,
    check_no_null_grades,
    check_iterative_writes,
    check_valid_rubric_categories,
    check_correct_response_empty_comment,
    check_nonzero_grades_have_comments,
    check_comment_single_sentence,
    check_comment_ends_with_question,
    check_comment_reuse_verbatim,
    check_grade_schema_valid,
    check_decisions_updated,
    check_decisions_entry_format,
    check_new_comment_in_comments_md,
    check_merge_preserves_other_questions,
]


def run_all_assertions(result_dir: str, scenario: dict, unattended: bool = True) -> dict:
    interaction_required = set(scenario.get("interaction_required_assertions", []))
    results = {}
    for fn in ASSERTIONS:
        name = fn.__name__.replace("check_", "")
        if unattended and name in interaction_required:
            results[name] = {"pass": None, "detail": "skipped — interaction required in unattended mode"}
        else:
            passed, detail = fn(result_dir, scenario)
            results[name] = {"pass": passed, "detail": detail}
    return results
