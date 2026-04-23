import json
import os
import sys
import pytest

from check_progress import get_progress


def test_counts_null_grades_as_ungraded(project_dir):
    progress = get_progress(str(project_dir))
    assert progress["total_students"] == 2
    assert progress["graded"]["Q1a"] == 0
    assert progress["graded"]["Q1b"] == 0


def test_counts_graded_entries_correctly(project_dir):
    grade_file = project_dir / "workspace/grades/111_grades.json"
    data = json.loads(grade_file.read_text())
    data["grades"]["Q1a"] = "Correct"
    grade_file.write_text(json.dumps(data))

    progress = get_progress(str(project_dir))
    assert progress["graded"]["Q1a"] == 1
    assert progress["graded"]["Q1b"] == 0


def test_transcription_count(project_dir):
    (project_dir / "workspace/transcriptions" / "111.md").write_text("transcription")

    progress = get_progress(str(project_dir))
    assert progress["transcribed"] == 1


def test_questions_list_matches_workflow(project_dir):
    progress = get_progress(str(project_dir))
    assert progress["questions"] == ["Q1a", "Q1b"]


def test_skips_corrupt_json_grade_file(project_dir):
    # Write invalid JSON to one grade file
    corrupt = project_dir / "workspace/grades/111_grades.json"
    corrupt.write_text("{not valid json")

    progress = get_progress(str(project_dir))
    # Should still process student 222; total_students still counts both files
    assert progress["total_students"] == 2
    assert len(progress["corrupt_files"]) == 1
    assert "111_grades.json" in progress["corrupt_files"][0]["file"]


def test_skips_grade_file_missing_grades_key(project_dir):
    # Write valid JSON but without a 'grades' key
    bad_file = project_dir / "workspace/grades/111_grades.json"
    bad_file.write_text('{"submission_id": "111", "student_name": "Alice Smith"}')

    progress = get_progress(str(project_dir))
    # Should not raise; student 111 contributes 0 to all question counts
    assert progress["total_students"] == 2
    assert progress["graded"]["Q1a"] == 0
