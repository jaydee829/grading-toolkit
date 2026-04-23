import csv
import json
import os
import sys
import yaml


def load_workflow(project_root="."):
    with open(os.path.join(project_root, "workflow.yml")) as f:
        return yaml.safe_load(f)


def load_all_grades(grades_dir, questions):
    students = []
    corrupt_files = []
    for fname in sorted(os.listdir(grades_dir)):
        if not fname.endswith("_grades.json"):
            continue
        try:
            with open(os.path.join(grades_dir, fname)) as f:
                students.append(json.load(f))
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            corrupt_files.append({"file": fname, "error": str(exc)})
            print(f"[WARN] Skipping {fname}: {exc}")
    return students, corrupt_files


def export_csv(students, questions, csv_path):
    fieldnames = ["submission_id", "student_name"]
    for q in questions:
        fieldnames += [f"{q}_grade", f"{q}_comment"]

    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            row = {"submission_id": s["submission_id"], "student_name": s["student_name"]}
            for q in questions:
                row[f"{q}_grade"] = s["grades"].get(q) or ""
                row[f"{q}_comment"] = s["comments"].get(q) or ""
            writer.writerow(row)
    print(f"Exported CSV → {csv_path} ({len(students)} students)")


def export_json(students, questions, json_dir):
    output = {q: [] for q in questions}
    for s in students:
        for q in questions:
            output[q].append({
                "submission_id": s["submission_id"],
                "student_name": s["student_name"],
                "grade": s["grades"].get(q),
                "comment": s["comments"].get(q),
            })
    out_path = os.path.join(json_dir, "grades_by_question.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Exported JSON → {out_path}")


def export(project_root="."):
    config = load_workflow(project_root)
    questions = [q["id"] for q in config["questions"]]
    grades_dir = os.path.join(project_root, config["paths"]["grades"])
    students, corrupt_files = load_all_grades(grades_dir, questions)

    incomplete = sum(
        1 for s in students if any(s["grades"].get(q) is None for q in questions)
    )
    if incomplete:
        print(f"WARNING: {incomplete} student(s) have ungraded questions — output will have empty cells")

    fmt = config["output"]["format"]
    if fmt in ("csv", "both"):
        export_csv(students, questions, os.path.join(project_root, config["output"]["csv_path"]))
    if fmt in ("json", "both"):
        export_json(students, questions, os.path.join(project_root, config["output"]["json_dir"]))


if __name__ == "__main__":
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    export(project_root)
