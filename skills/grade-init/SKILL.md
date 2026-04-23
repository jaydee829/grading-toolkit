---
name: grade-init
description: Use when starting a new grading assignment and the project workspace does not yet exist — no workflow.yml, no grade stubs, no scripts directory. Run before any other grade-* skill.
---

# Grade Init

Initialize a new grading project. Follow these steps in order without skipping.

## Step 1: Environment Detection

Run these commands and note the output — present the results as suggestions in Step 2:

```bash
conda env list
```

```bash
# On Windows (TeX Live):
where pdftoppm 2>nul || dir /s /b "C:\texlive\*pdftoppm.exe" 2>nul
# On Mac/Linux:
which pdftoppm || find /usr -name pdftoppm 2>/dev/null
```

## Step 2: Gather Setup Information

Ask the following questions, presenting detected values as defaults:

1. **Project name** — suggest: current directory name
2. **Course name** — suggest: parent directory name
3. **Instructor name**
4. **Python run prefix** — show detected conda envs; suggest the one that looks course-related; user can specify `conda run -n <env>`, `python`, or a custom prefix
5. **Question list** — ask for IDs (e.g., Q1a, Q1b, Q2a) and a one-line description for each. Allow multi-line entry.
6. **Rubric** — existing file to import? If yes, copy to `rubric.md`. If no, create from the default 8-category template at the end of this document.
7. **Answer key** — path to existing file, or create blank `answer_key.md`
8. **Student roster** — path to existing `metadata.yml`, or create blank template:
   ```yaml
   # submissions/metadata.yml
   # One entry per student PDF:
   # <SID>.pdf:
   #   submitters:
   #     - name: Student Name
   #       sid: "student_id"
   #   score: 0.0
   ```
9. **Output format** — csv, json, or both; ask for any CSV column preferences

## Step 3: Detect PDF Type

Copy all scripts from this skill's `scripts/` directory to the project's `scripts/` directory.

Then run:
```
<run_prefix> scripts/check_pdf_type.py submissions/<first_pdf_filename>
```

Use the output (`text_layer` or `image_layer`) in workflow.yml. If `image_layer`, also ask:
- pdftoppm path (suggest the path found in Step 1, or `/usr/bin/pdftoppm` on Linux/Mac)
- DPI (suggest 150)
- Max pages (suggest 20)

## Step 4: Write workflow.yml

Create `workflow.yml` at the project root:

```yaml
project:
  name: "<project_name>"
  course: "<course_name>"
  instructor: "<instructor_name>"
  created_at: "<YYYY-MM-DD today>"
  profile: "instructor_profile.md"

submissions:
  directory: "submissions/"
  metadata: "submissions/metadata.yml"
  pdf_type: "<text_layer|image_layer>"
  pdf_renderer:
    tool: "pdftoppm"
    path: "<pdftoppm_path>"
    dpi: <dpi>
    max_pages: <max_pages>

python:
  run_prefix: "<run_prefix>"

questions:
  - id: "<id>"
    description: "<description>"
  # repeat for each question

comment_strategy: "collaborative"

output:
  format: "<csv|json|both>"
  csv_path: "grades.csv"
  json_dir: "workspace/grades/"

paths:
  rubric: "rubric.md"
  answer_key: "answer_key.md"
  comments: "comments.md"
  decisions: "decisions.md"
  transcriptions: "workspace/transcriptions/"
  grades: "workspace/grades/"
  pages: "workspace/pages/"
  scripts: "scripts/"
```

## Step 5: Create Directories and Files

Create these directories (if they don't exist):
- `submissions/`
- `workspace/transcriptions/`
- `workspace/grades/`
- `workspace/pages/`
- `scripts/`

Create blank files if not already imported:
- `rubric.md` (see default template below, or use imported rubric)
- `answer_key.md`
- `comments.md`
- `decisions.md`

## Step 6: Create Grade Stubs

Read `submissions/metadata.yml`. For each student, create `workspace/grades/<SID>_grades.json`:

```json
{
  "submission_id": "<SID>",
  "student_name": "<name>",
  "grades": { "<Q1>": null, "<Q2>": null },
  "comments": { "<Q1>": null, "<Q2>": null },
  "explanations": { "<Q1>": null, "<Q2>": null },
  "flags": []
}
```

Replace `<Q1>`, `<Q2>`, etc. with the actual question IDs from workflow.yml. Every question must have a null entry in every student's file.

## Step 7: Check for Instructor Profile

If `instructor_profile.md` does not exist:
> "No instructor profile found. Would you like to create one now with /grade-profile? A profile captures your grading style and can be reused across assignments. You can also skip this and run /grade-profile later."

## Default Rubric Template

```markdown
# Rubric

## Correct
Full credit. No comment needed.

## Minor communication error
Minor notation, terminology, or arithmetic/transcription error that does not affect the substance of the argument.

## Multiple minor communication errors
Two or more independent minor communication errors.

## Minor justification error
Minor error in logic or justification — one key element is missing or one mechanism is described incorrectly.

## Multiple minor justification errors
Two or more independent minor justification errors.

## Major errors or misconceptions
Fundamentally wrong approach, or a core misconception about the concept being tested.

## Incoherent/incomplete evidence of understanding
The response fails to construct a coherent argument. Use only when the reasoning is genuinely impossible to follow — not merely wrong or brief.

## Blank
No response, or a response with no written justification (e.g., a checkbox selected with no explanation).
```
