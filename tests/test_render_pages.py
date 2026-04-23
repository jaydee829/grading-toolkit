import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call

from render_pages import render_all


def test_renders_pdf_and_creates_output_dir(project_dir):
    # Place a fake PDF in submissions/
    (project_dir / "submissions" / "111.pdf").write_bytes(b"%PDF-1.4")

    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("render_pages.subprocess.run", return_value=mock_result) as mock_run:
        ok, skipped, errors = render_all(str(project_dir))

    assert ok == 1
    assert skipped == 0
    assert errors == []
    # pdftoppm was called with correct args
    args = mock_run.call_args[0][0]
    assert "-r" in args
    assert "150" in args
    assert "-png" in args


def test_skips_already_rendered(project_dir):
    sub_dir = project_dir / "workspace/pages/111"
    sub_dir.mkdir(parents=True)
    (sub_dir / "page-01.png").write_bytes(b"PNG")
    (project_dir / "submissions" / "111.pdf").write_bytes(b"%PDF-1.4")

    with patch("render_pages.subprocess.run") as mock_run:
        ok, skipped, errors = render_all(str(project_dir))

    assert skipped == 1
    assert ok == 0
    mock_run.assert_not_called()


def test_records_error_on_nonzero_returncode(project_dir):
    (project_dir / "submissions" / "111.pdf").write_bytes(b"%PDF-1.4")

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "pdftoppm: command not found"

    with patch("render_pages.subprocess.run", return_value=mock_result):
        ok, skipped, errors = render_all(str(project_dir))

    assert ok == 0
    assert len(errors) == 1
    assert errors[0]["sub_id"] == "111"
