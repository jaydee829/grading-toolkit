---
name: grade-question
description: Use when transcriptions exist and you are ready to grade all students on a specific question. Students with existing non-null grades for that question are skipped. Usage: /grade-question Q1a
---

# Grade Question

Grade all student submissions for a specified question. Takes a question ID as argument.

## Step 1: Load All Context

**Read every one of these before grading a single student:**
- `workflow.yml` — questions list, comment_strategy, run_prefix, paths
- `rubric.md` — all category definitions verbatim
- `comments.md` — the entire section for this question (search for `## <QuestionID>`)
- `decisions.md` — all prior rulings for this question
- `instructor_profile.md` — strictness calibrations, priority misconceptions, comment style
- `answer_key.md` — the correct answer for this question

Confirm the question ID exists in `workflow.yml`. If it doesn't, stop and report the available question IDs.

Run:
```
<run_prefix> scripts/check_progress.py
```

Show how many students have null grades for this question.

## Step 2: Confirm Comment Strategy

Show: "Current comment strategy: [value from workflow.yml]. Override for this session? (strict / collaborative / relaxed / keep)"

Record the active strategy for this session.

## Step 3: Grading Loop

For each student whose grade for this question is null in `workspace/grades/<SID>_grades.json`:

### 3a: Read the response
Open `workspace/transcriptions/<SID>.md`. Find the section matching `## <QuestionID>`.

### 3b: Assign rubric category
Compare the response against the answer key and rubric. Apply `instructor_profile.md` calibrations:
- If a strictness calibration from the profile applies to this response, honor it
- If uncertain between two categories, apply the edge-case philosophy from the profile

### 3c: Find or generate a comment

1. Search `comments.md` for a comment under `## <QuestionID> / <category>` that matches this error. **Reuse verbatim** if found.

2. If no matching comment exists:
   - **Strict:** Write grade with empty comment string and add flag: `"<QuestionID>: comment needed — [1-sentence error description]"`
   - **Collaborative:** Propose a draft comment, wait for instructor approval, then save approved comment to `comments.md` under the appropriate heading
   - **Relaxed:** Write a comment following the style rules in `instructor_profile.md`, save it to `comments.md`

**Comment rules (always apply regardless of strategy):**
- Phrased as a question — never a correction or statement
- Does not reveal the answer or lead directly to it
- One sentence only
- For Correct responses: empty string — write nothing

### 3d: Write to grade file immediately

Read the existing `workspace/grades/<SID>_grades.json`, update only this question's fields, and write back:

```json
{
  "grades":       { "<QuestionID>": "<rubric category string>" },
  "comments":     { "<QuestionID>": "<comment string or empty string>" },
  "explanations": { "<QuestionID>": "<1–2 sentence rationale citing rubric and answer key>" }
}
```

Merge carefully — preserve all other questions' existing data.

**Write after every single student. Never batch.**

### 3e: Progress check

Every 10 students, run:
```
<run_prefix> scripts/check_progress.py
```

### 3f: Ask-up protocol

When genuinely uncertain (the response sits between two categories, or raises a new edge case not covered by the rubric or prior decisions), stop and ask:

> "Student [name]: '[brief excerpt]' — I'm uncertain between [Category A] and [Category B] because [specific reason]. Which applies here?"

After receiving the ruling, append to `decisions.md`:
```markdown
## <QuestionID> — <YYYY-MM-DD>
**Case:** [description of the ambiguous response]
**Ruling:** [Category] — [brief justification]
**Applied to:** [student name]
```

## Step 4: QC Pass

After all students for this question are graded:

1. Read every ruling added to `decisions.md` during this session (today's date, this question)
2. For each ruling, re-scan the students graded EARLIER in this session (before the ruling was made)
3. Identify any whose grade is now inconsistent with the new ruling

For each inconsistency:
- **Strict / Collaborative:** List the student name, old grade, and suggested new grade. Ask: "Should I update these?"
- **Relaxed:** Apply the correction automatically. Append to the affected student's JSON `flags`:
  ```json
  "flags": ["<QuestionID>: grade updated from '<old>' to '<new>' — ruling: <brief description>"]
  ```

4. Run `check_progress.py` one final time. Confirm zero nulls remain for this question.

5. Scan every student graded this session. For each whose comment for this question is an empty string and whose grade is not Correct or Blank:
   - **Strict:** Generate an appropriate comment (phrased as a question, one sentence, not revealing the answer). Save it to `comments.md` under `## <QuestionID> / ### <category>`. Update the grade stub with the new comment and remove the flag entry.
   - **Collaborative / Relaxed:** List the student, their grade, and the flag description. Ask: "These students need comments — should I draft one for each?" Wait for instructor input before writing.
