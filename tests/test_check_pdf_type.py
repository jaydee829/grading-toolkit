import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "grade-init", "scripts"))

from check_pdf_type import detect_pdf_type, MIN_TEXT_CHARS


def _mock_pdf(text_per_page):
    pages = []
    for text in text_per_page:
        page = MagicMock()
        page.extract_text.return_value = text
        pages.append(page)
    pdf = MagicMock()
    pdf.pages = pages
    pdf.__enter__ = lambda s: s
    pdf.__exit__ = MagicMock(return_value=False)
    return pdf


def test_text_layer_detected_when_first_page_has_text():
    long_text = "a" * (MIN_TEXT_CHARS + 1)
    with patch("check_pdf_type.pdfplumber.open", return_value=_mock_pdf([long_text])):
        assert detect_pdf_type("test.pdf") == "text_layer"


def test_image_layer_detected_when_all_pages_empty():
    with patch("check_pdf_type.pdfplumber.open", return_value=_mock_pdf(["", "", ""])):
        assert detect_pdf_type("test.pdf") == "image_layer"


def test_text_layer_detected_on_second_page():
    long_text = "a" * (MIN_TEXT_CHARS + 1)
    with patch("check_pdf_type.pdfplumber.open", return_value=_mock_pdf(["", long_text])):
        assert detect_pdf_type("test.pdf") == "text_layer"


def test_image_layer_when_text_below_threshold():
    short_text = "a" * (MIN_TEXT_CHARS - 1)
    with patch("check_pdf_type.pdfplumber.open", return_value=_mock_pdf([short_text])):
        assert detect_pdf_type("test.pdf") == "image_layer"
