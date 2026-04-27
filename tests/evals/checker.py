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
            comment = line[3:].rstrip('"')
            result[current_q][current_cat].append(comment)
    return result
