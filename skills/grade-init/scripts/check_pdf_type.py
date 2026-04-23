import sys
import pdfplumber

MIN_TEXT_CHARS = 100


def detect_pdf_type(pdf_path: str) -> str:
    """Returns 'text_layer' or 'image_layer'."""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:3]:
            text = page.extract_text() or ""
            if len(text.strip()) >= MIN_TEXT_CHARS:
                return "text_layer"
    return "image_layer"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_pdf_type.py <pdf_path>")
        sys.exit(1)
    print(detect_pdf_type(sys.argv[1]))
