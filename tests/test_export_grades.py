import csv
import json
import os
import yaml
import pytest

from export_grades import export_csv, export_json, load_all_grades, export


def _write_graded(project_dir, sid, name, q1a, q1b):
    data = {
        "submission_id": sid,
        "student_name": name,
        "grades": {"Q1a": q1a, "Q1b": q1b},
        "comments": {"Q1a": f"{q1a} comment" if q1a else None, "Q1b": None},
        "explanations": {"Q1a": None, "Q1b": None},
        "flags": [],
    }
    (project_dir / "workspace/grades" / f"{sid}_grades.json").write_text(json.dumps(data))
    return data


def test_csv_export_has_correct_columns(project_dir, tmp_path):
    _write_graded(project_dir, "111", "Alice Smith", "Correct", "Minor communication error")
    _write_graded(project_dir, "222", "Bob Jones", "Major errors or misconceptions", "Correct")

    csv_path = str(tmp_path / "grades.csv")
    questions = ["Q1a", "Q1b"]
    students, _ = load_all_grades(str(project_dir / "workspace/grades"), questions)
    export_csv(students, questions, csv_path)

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert "Q1a_grade" in rows[0]
    assert "Q1b_comment" in rows[0]
    assert rows[0]["student_name"] in {"Alice Smith", "Bob Jones"}


def test_json_export_is_question_indexed(project_dir, tmp_path):
    _write_graded(project_dir, "111", "Alice Smith", "Correct", None)

    questions = ["Q1a", "Q1b"]
    students, _ = load_all_grades(str(project_dir / "workspace/grades"), questions)
    json_dir = str(tmp_path)
    export_json(students, questions, json_dir)

    with open(os.path.join(json_dir, "grades_by_question.json")) as f:
        output = json.load(f)

    assert "Q1a" in output
    assert "Q1b" in output
    assert output["Q1a"][0]["submission_id"] == "111"
    assert output["Q1a"][0]["grade"] == "Correct"


def test_warns_on_incomplete_grades(project_dir, tmp_path, capsys):
    # Both students have null grades (from conftest fixture)
    config = yaml.safe_load((project_dir / "workflow.yml").read_text())
    config["output"]["format"] = "csv"
    config["output"]["csv_path"] = str(tmp_path / "grades.csv")
    (project_dir / "workflow.yml").write_text(yaml.dump(config))

    export(str(project_dir))

    captured = capsys.readouterr()
    assert "WARNING" in captured.out


def test_skips_corrupt_json_in_load_all_grades(project_dir):
    corrupt = project_dir / "workspace/grades/111_grades.json"
    corrupt.write_text("{not valid json")

    questions = ["Q1a", "Q1b"]
    students, corrupt_files = load_all_grades(str(project_dir / "workspace/grades"), questions)

    assert len(students) == 1
    assert students[0]["submission_id"] == "222"
    assert len(corrupt_files) == 1
    assert "111_grades.json" in corrupt_files[0]["file"]
