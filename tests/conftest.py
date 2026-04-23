import json
import os
import pytest
import yaml


SAMPLE_WORKFLOW = {
    "project": {
        "name": "Test GR1",
        "course": "Test 101",
        "instructor": "Dr. Test",
        "created_at": "2026-01-01",
        "profile": "instructor_profile.md",
    },
    "submissions": {
        "directory": "submissions/",
        "metadata": "submissions/metadata.yml",
        "pdf_type": "image_layer",
        "pdf_renderer": {
            "tool": "pdftoppm",
            "path": "/usr/bin/pdftoppm",
            "dpi": 150,
            "max_pages": 20,
        },
    },
    "python": {"run_prefix": "conda run -n grading_toolkit python"},
    "questions": [
        {"id": "Q1a", "description": "Describe the bias-variance tradeoff"},
        {"id": "Q1b", "description": "Name two shrinkage methods"},
    ],
    "comment_strategy": "collaborative",
    "output": {
        "format": "csv",
        "csv_path": "grades.csv",
        "json_dir": "workspace/grades/",
    },
    "paths": {
        "rubric": "rubric.md",
        "answer_key": "answer_key.md",
        "comments": "comments.md",
        "decisions": "decisions.md",
        "transcriptions": "workspace/transcriptions/",
        "grades": "workspace/grades/",
        "pages": "workspace/pages/",
        "scripts": "scripts/",
    },
}

SAMPLE_STUDENTS = [
    {
        "submission_id": "111",
        "student_name": "Alice Smith",
        "grades": {"Q1a": None, "Q1b": None},
        "comments": {"Q1a": None, "Q1b": None},
        "explanations": {"Q1a": None, "Q1b": None},
        "flags": [],
    },
    {
        "submission_id": "222",
        "student_name": "Bob Jones",
        "grades": {"Q1a": None, "Q1b": None},
        "comments": {"Q1a": None, "Q1b": None},
        "explanations": {"Q1a": None, "Q1b": None},
        "flags": [],
    },
]


@pytest.fixture
def project_dir(tmp_path):
    """Minimal project directory: workflow.yml, grade stubs, empty directories."""
    (tmp_path / "workflow.yml").write_text(yaml.dump(SAMPLE_WORKFLOW))

    for path in [
        "submissions",
        "workspace/grades",
        "workspace/transcriptions",
        "workspace/pages",
        "scripts",
    ]:
        (tmp_path / path).mkdir(parents=True, exist_ok=True)

    for student in SAMPLE_STUDENTS:
        fname = f"{student['submission_id']}_grades.json"
        (tmp_path / "workspace/grades" / fname).write_text(
            json.dumps(student, indent=2)
        )

    return tmp_path
