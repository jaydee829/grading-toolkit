import os
import sys
import yaml
import pdfplumber


def load_workflow(project_root="."):
    with open(os.path.join(project_root, "workflow.yml")) as f:
        return yaml.safe_load(f)


def extract_all(project_root="."):
    config = load_workflow(project_root)
    subs_dir = os.path.join(project_root, config["submissions"]["directory"])
    trans_dir = os.path.join(project_root, config["paths"]["transcriptions"])
    os.makedirs(trans_dir, exist_ok=True)

    pdfs = sorted(f for f in os.listdir(subs_dir) if f.endswith(".pdf"))
    ok, skipped = 0, 0

    for pdf_fname in pdfs:
        sub_id = os.path.splitext(pdf_fname)[0]
        out_path = os.path.join(trans_dir, f"{sub_id}.md")

        if os.path.exists(out_path):
            skipped += 1
            continue

        pdf_path = os.path.join(subs_dir, pdf_fname)
        parts = []

        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                parts.append(f"## Page {i}\n\n{text}\n")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))

        ok += 1
        print(f"[OK] {sub_id}")

    print(f"\nExtracted: {ok} | Skipped: {skipped}")
    return ok, skipped


if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    extract_all(project_root)
