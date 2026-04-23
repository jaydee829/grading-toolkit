---
name: grade-transcribe
description: Use when student PDFs have not yet been transcribed, or when a transcription run was interrupted and needs to resume. Safe to restart — already-transcribed students are skipped automatically.
---

# Grade Transcribe

Convert all student submission PDFs to markdown transcription files in `workspace/transcriptions/`. Already-transcribed students are skipped automatically — restart safely at any time.

## Step 1: Load Config and Check Progress

Read `workflow.yml` for `pdf_type`, renderer config, `python.run_prefix`, and paths.

Run:
```
<run_prefix> scripts/check_progress.py
```

If all students are already transcribed, say so and stop. Otherwise show which students remain.

## Step 2: Text-Layer Path

If `pdf_type == "text_layer"`:

```
<run_prefix> scripts/extract_text.py
```

This extracts text from each untranscribed PDF and writes to `workspace/transcriptions/<SID>.md`. After it completes, run `check_progress.py` again to confirm the transcription count.

## Step 3: Image-Layer Path

If `pdf_type == "image_layer"`:

### 3a: Render PDFs to PNG

```
<run_prefix> scripts/render_pages.py
```

Skips already-rendered student directories.

### 3b: Vision Transcription

For each student whose `workspace/transcriptions/<SID>.md` does NOT yet exist:

1. Read all PNG files in `workspace/pages/<SID>/` using the Read tool (view each image)
2. Transcribe the full written content

**Transcription format — use this exact structure:**
```markdown
# Transcription: <student_name> (<SID>)

## <QuestionID>
<transcribed handwritten/typed text verbatim>

## <QuestionID>
<transcribed text>
```

For blank responses:
```markdown
## Q2a
[BLANK]
```

3. Write the file to `workspace/transcriptions/<SID>.md` **immediately after transcribing** — do not wait or batch multiple students.

**Checkpoint protocol:** After writing each file, confirm it exists on disk. If the session ends before all students are transcribed, restart `/grade-transcribe` — it will pick up where it left off.

## Step 4: Verify

Run `check_progress.py` at the end. Confirm transcription count equals total students. For any missing, read the student's PDF directly and note any issues (corrupt file, missing pages) by appending to their grade stub's `flags` array:

```json
"flags": ["transcription: PDF missing pages 3–4, Q2b may be incomplete"]
```
