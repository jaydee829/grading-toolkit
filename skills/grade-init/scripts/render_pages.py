import os
import shutil
import subprocess
import sys
import yaml


def load_workflow(project_root="."):
    with open(os.path.join(project_root, "workflow.yml")) as f:
        return yaml.safe_load(f)


def render_all(project_root="."):
    config = load_workflow(project_root)
    renderer = config["submissions"]["pdf_renderer"]
    pdftoppm = renderer["path"]
    dpi = str(renderer["dpi"])
    max_pages = str(renderer["max_pages"])

    subs_dir = os.path.join(project_root, config["submissions"]["directory"])
    pages_dir = os.path.join(project_root, config["paths"]["pages"])

    pdfs = sorted(f for f in os.listdir(subs_dir) if f.endswith(".pdf"))
    ok, skipped, errors = 0, 0, []

    for pdf_fname in pdfs:
        sub_id = os.path.splitext(pdf_fname)[0]
        out_dir = os.path.join(pages_dir, sub_id)

        if os.path.isdir(out_dir) and any(f.endswith(".png") for f in os.listdir(out_dir)):
            skipped += 1
            continue

        os.makedirs(out_dir, exist_ok=True)
        out_prefix = os.path.join(out_dir, "page")
        pdf_path = os.path.join(subs_dir, pdf_fname)

        cmd = [pdftoppm, "-r", dpi, "-f", "1", "-l", max_pages, "-png", pdf_path, out_prefix]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except OSError as exc:
            shutil.rmtree(out_dir, ignore_errors=True)
            errors.append({"sub_id": sub_id, "stderr": str(exc)})
            continue

        if result.returncode != 0:
            shutil.rmtree(out_dir, ignore_errors=True)
            errors.append({"sub_id": sub_id, "stderr": result.stderr.strip()})
        else:
            ok += 1

    print(f"Rendered: {ok} | Skipped: {skipped} | Errors: {len(errors)}")
    for e in errors:
        print(f"  ERROR {e['sub_id']}: {e['stderr']}")
    return ok, skipped, errors


if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    try:
        render_all(project_root)
    except FileNotFoundError as exc:
        print(f"Error: {exc}. Make sure workflow.yml exists and run /grade-init first.", file=sys.stderr)
        sys.exit(1)
