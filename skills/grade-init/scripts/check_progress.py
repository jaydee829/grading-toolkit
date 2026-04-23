import json
import os
import sys
import yaml


def load_workflow(project_root="."):
    with open(os.path.join(project_root, "workflow.yml")) as f:
        return yaml.safe_load(f)


def get_progress(project_root="."):
    config = load_workflow(project_root)
    questions = [q["id"] for q in config["questions"]]
    grades_dir = os.path.join(project_root, config["paths"]["grades"])
    trans_dir = os.path.join(project_root, config["paths"]["transcriptions"])

    grade_files = sorted(f for f in os.listdir(grades_dir) if f.endswith("_grades.json"))
    transcribed = set(
        f[:-3] for f in os.listdir(trans_dir) if f.endswith(".md")
    )

    graded = {q: 0 for q in questions}
    corrupt_files = []
    for fname in grade_files:
        try:
            with open(os.path.join(grades_dir, fname)) as f:
                data = json.load(f)
            for q in questions:
                if data.get("grades", {}).get(q) is not None:
                    graded[q] += 1
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            corrupt_files.append({"file": fname, "error": str(exc)})
            print(f"[WARN] Skipping {fname}: {exc}")

    return {
        "total_students": len(grade_files),
        "transcribed": len(transcribed),
        "questions": questions,
        "graded": graded,
        "corrupt_files": corrupt_files,
    }


def print_progress(project_root="."):
    p = get_progress(project_root)
    n = p["total_students"]
    print(f"Students: {n} | Transcribed: {p['transcribed']}/{n}\n")
    for q in p["questions"]:
        done = p["graded"][q]
        bar = "#" * done + "." * (n - done)
        print(f"  {q:6s} [{bar}] {done}/{n}")


if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    print_progress(project_root)
