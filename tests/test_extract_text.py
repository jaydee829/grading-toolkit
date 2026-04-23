import os
import sys
import pytest
from unittest.mock import MagicMock, patch

from extract_text import extract_all


def _mock_pdf(pages_text):
    pages = []
    for text in pages_text:
        page = MagicMock()
        page.extract_text.return_value = text
        pages.append(page)
    pdf = MagicMock()
    pdf.pages = pages
    pdf.__enter__ = MagicMock(return_value=pdf)
    pdf.__exit__ = MagicMock(return_value=False)
    return pdf


def test_extracts_text_and_writes_transcription(project_dir):
    (project_dir / "submissions" / "111.pdf").write_bytes(b"%PDF-1.4")
    mock_pdf = _mock_pdf(["Q1a answer text here", "Q1b answer text here"])

    with patch("extract_text.pdfplumber.open", return_value=mock_pdf):
        ok, skipped, errors = extract_all(str(project_dir))

    assert ok == 1
    out = (project_dir / "workspace/transcriptions/111.md").read_text()
    assert "Q1a answer text here" in out
    assert "## Page 1" in out


def test_skips_already_extracted(project_dir):
    (project_dir / "submissions" / "111.pdf").write_bytes(b"%PDF-1.4")
    (project_dir / "workspace/transcriptions" / "111.md").write_text("already done")

    with patch("extract_text.pdfplumber.open") as mock_open:
        ok, skipped, errors = extract_all(str(project_dir))

    assert skipped == 1
    assert ok == 0
    mock_open.assert_not_called()


def test_handles_none_text_as_empty_string(project_dir):
    (project_dir / "submissions" / "111.pdf").write_bytes(b"%PDF-1.4")
    mock_pdf = _mock_pdf([None])

    with patch("extract_text.pdfplumber.open", return_value=mock_pdf):
        ok, skipped, errors = extract_all(str(project_dir))

    assert ok == 1
    out = (project_dir / "workspace/transcriptions/111.md").read_text()
    assert "## Page 1" in out


def test_records_error_on_pdfplumber_exception(project_dir):
    (project_dir / "submissions" / "111.pdf").write_bytes(b"%PDF-1.4")

    with patch("extract_text.pdfplumber.open", side_effect=Exception("Corrupt PDF")):
        ok, skipped, errors = extract_all(str(project_dir))

    assert ok == 0
    assert len(errors) == 1
    assert errors[0]["sub_id"] == "111"
    assert "Corrupt PDF" in errors[0]["error"]
    # No partial file should be left
    assert not (project_dir / "workspace/transcriptions/111.md").exists()
