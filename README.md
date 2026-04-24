# grading-toolkit

A Claude Code plugin providing AI-assisted grading skills for academic instructors.
Grade any assignment — free response, multiple choice, coding — from PDF submissions to final CSV/JSON export.

## Install

```bash
/plugin marketplace add <your-github-username>/grading-toolkit
/plugin install grading-toolkit@<your-github-username>
/reload-plugins
```

## Skills

| Skill | When to run |
|---|---|
| `/grade-init` | Once per assignment — initializes workspace |
| `/grade-profile` | Once per instructor/subject — sets grading style |
| `/grade-rubric Q1a` | Once per question before grading |
| `/grade-transcribe` | Once per assignment — PDF → text |
| `/grade-question Q1a` | Per question when ready to grade |
| `/grade-export` | On demand — generates CSV/JSON output |

## Typical Workflow

```
/grade-init         ← creates workflow.yml, grade stubs, copies scripts
/grade-profile      ← captures instructor style (optional but recommended)
/grade-rubric Q1a   ← calibrate rubric, seed comments.md
/grade-transcribe   ← PDF → transcription files
/grade-question Q1a ← grade all students on Q1a
/grade-question Q1b ← grade all students on Q1b
/grade-export       ← generate grades.csv
```

## Python Scripts

After `/grade-init`, these scripts live in your project's `scripts/` directory:

| Script | Usage |
|---|---|
| `check_pdf_type.py <pdf>` | Detect text vs. image layer |
| `render_pages.py [project_root]` | Batch PDF-to-PNG conversion |
| `extract_text.py [project_root]` | Extract text-layer PDFs |
| `check_progress.py [project_root]` | Show completion matrix |
| `export_grades.py [project_root]` | Generate CSV/JSON output |

## Requirements

- Python 3.9+ with `pdfplumber` and `pyyaml`
- pdftoppm (TeX Live or poppler-utils) for image-layer PDFs
- Claude Code with plugin support
