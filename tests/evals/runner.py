import json
import os
import shutil
import subprocess
import sys
import time
import yaml
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from checker import load_scenario, run_all_assertions


def _find_toolkit_root(file: str) -> str:
    """Navigate up from tests/evals/ to repo root."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(file))))


def provision_directory(dest_dir: str, fixture_dir: str, scenario: dict, with_skill: bool):
    os.makedirs(dest_dir, exist_ok=True)

    # Copy top-level fixture files
    for item in os.listdir(fixture_dir):
        src = os.path.join(fixture_dir, item)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dest_dir, item))

    # Copy submissions/ as-is
    shutil.copytree(
        os.path.join(fixture_dir, "submissions"),
        os.path.join(dest_dir, "submissions"),
    )

    # Copy transcriptions/ → workspace/transcriptions/
    workspace_trans = os.path.join(dest_dir, "workspace", "transcriptions")
    os.makedirs(workspace_trans, exist_ok=True)
    for f in os.listdir(os.path.join(fixture_dir, "transcriptions")):
        shutil.copy2(
            os.path.join(fixture_dir, "transcriptions", f),
            os.path.join(workspace_trans, f),
        )

    # Create remaining workspace dirs
    for subdir in ("workspace/grades", "workspace/pages"):
        os.makedirs(os.path.join(dest_dir, subdir), exist_ok=True)

    # Copy scripts from skills/grade-init/scripts/
    toolkit_root = _find_toolkit_root(__file__)
    scripts_src = os.path.join(toolkit_root, "skills", "grade-init", "scripts")
    scripts_dst = os.path.join(dest_dir, "scripts")
    os.makedirs(scripts_dst, exist_ok=True)
    for f in os.listdir(scripts_src):
        if f.endswith(".py"):
            shutil.copy2(os.path.join(scripts_src, f), os.path.join(scripts_dst, f))

    # Pre-populate grade stubs
    qid = scenario["question_id"]
    prepopulate = scenario.get("prepopulate", {})
    for sid in scenario["students"]:
        stub = {
            "submission_id": sid,
            "grades": {qid: None},
            "comments": {qid: None},
            "explanations": {qid: None},
            "flags": [],
        }
        for other_qid, vals in prepopulate.items():
            for field in ("grades", "comments", "explanations"):
                stub[field][other_qid] = vals.get(field)
        grade_path = os.path.join(dest_dir, "workspace", "grades", f"{sid}_grades.json")
        with open(grade_path, "w") as f:
            json.dump(stub, f, indent=2)

    # Inject skill or write empty CLAUDE.md
    skill_content = ""
    if with_skill:
        toolkit_root = _find_toolkit_root(__file__)
        skill_path = os.path.join(toolkit_root, "skills", "grade-question", "SKILL.md")
        with open(skill_path) as f:
            skill_content = f.read()
    with open(os.path.join(dest_dir, "CLAUDE.md"), "w") as f:
        f.write(skill_content)


_BEHAVIORAL_KEYS = [
    "files_read_before_grading",
    "progress_check_at_start",
    "strategy_confirmation",
    "ask_up_before_writing",
    "collaborative_draft",
    "qc_rescan_mentioned",
    "final_progress_check",
]


def run_claude(work_dir: str, query: str) -> tuple:
    """Run claude -p in work_dir. Returns (combined_output, duration_seconds)."""
    start = time.time()
    result = subprocess.run(
        ["claude", "-p", query, "--dangerously-skip-permissions"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )
    duration = time.time() - start
    return result.stdout + result.stderr, duration


def write_results(
    results_dir: str,
    timestamp_str: str,
    scenario_name: str,
    skill_version: str,
    with_structural: dict,
    without_structural: dict,
    with_log_path: str,
    without_log_path: str,
) -> str:
    data = {
        "timestamp": timestamp_str,
        "scenario": scenario_name,
        "skill_version": skill_version,
        "results": {
            "with_skill": {
                "structural": with_structural,
                "behavioral": {k: {"pass": None, "note": ""} for k in _BEHAVIORAL_KEYS},
                "stdout_log": os.path.basename(with_log_path),
            },
            "without_skill": {
                "structural": without_structural,
                "behavioral": {k: {"pass": None, "note": ""} for k in _BEHAVIORAL_KEYS},
                "stdout_log": os.path.basename(without_log_path),
            },
        },
    }
    output_path = os.path.join(results_dir, f"{timestamp_str}-results.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    return output_path


def compare_results(results_dir: str):
    result_files = sorted(
        f for f in os.listdir(results_dir) if f.endswith("-results.json")
    )
    if not result_files:
        print("No results found.")
        return

    by_scenario: dict = {}
    for fname in result_files:
        with open(os.path.join(results_dir, fname)) as f:
            data = json.load(f)
        date = data["timestamp"][:10]
        name = data["scenario"]
        by_scenario.setdefault(name, []).append((date, data))

    for scenario_name, runs in by_scenario.items():
        print(f"\nscenario: {scenario_name}\n")
        dates = [r[0] for r in runs]
        pad = 32
        print(" " * pad + "  ".join(f"{d:>10}" for d in dates))
        for run_type in ("with_skill", "without_skill"):
            for check_type in ("structural", "behavioral"):
                scores = []
                for _, d in runs:
                    check_data = d["results"][run_type][check_type]
                    total = len(check_data)
                    passed = sum(1 for v in check_data.values() if v.get("pass") is True)
                    scores.append(f"{passed}/{total}")
                label = f"{run_type} / {check_type}"
                print(f"  {label:<{pad-2}}" + "  ".join(f"{s:>10}" for s in scores))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run grade-question skill evals")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--scenario",
        metavar="SCENARIO_PATH",
        help="Scenario path relative to tests/evals/scenarios/ (e.g. grade-question)",
    )
    group.add_argument(
        "--compare",
        action="store_true",
        help="Print regression table across all saved results",
    )
    args = parser.parse_args()

    evals_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(evals_dir, "results")

    if args.compare:
        compare_results(results_dir)
        return

    scenario_path = os.path.join(evals_dir, "scenarios", args.scenario, "scenario.yml")
    scenario = load_scenario(scenario_path)
    fixture_dir = scenario["_fixture_dir"]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    run_root = os.path.join(results_dir, ts)
    os.makedirs(run_root, exist_ok=True)

    with_structural = None
    without_structural = None
    with_log = None
    without_log = None

    for label, with_skill in (("with_skill", True), ("without_skill", False)):
        work_dir = os.path.join(run_root, label)
        print(f"\n[{label}] Provisioning {work_dir} ...")
        provision_directory(work_dir, fixture_dir, scenario, with_skill=with_skill)

        print(f"[{label}] Running claude -p ...")
        output, duration = run_claude(work_dir, scenario["query"])
        log_path = os.path.join(results_dir, f"{ts}-{label}-stdout.txt")
        with open(log_path, "w") as f:
            f.write(output)
        print(f"[{label}] Completed in {duration:.1f}s. Log: {log_path}")

        assertions = run_all_assertions(work_dir, scenario, unattended=True)
        passed = sum(1 for v in assertions.values() if v["pass"])
        total = len(assertions)
        print(f"[{label}] Structural: {passed}/{total} passed")
        for name, result in assertions.items():
            status = "PASS" if result["pass"] else "FAIL"
            print(f"  [{status}] {name}: {result['detail']}")

        if label == "with_skill":
            with_structural = assertions
            with_log = log_path
        else:
            without_structural = assertions
            without_log = log_path

    results_path = write_results(
        results_dir, ts, scenario["name"], "1.0.0",
        with_structural, without_structural, with_log, without_log,
    )
    print(f"\nResults written to: {results_path}")
    print("Open stdout logs and fill in behavioral pass/fail manually.")


if __name__ == "__main__":
    main()
