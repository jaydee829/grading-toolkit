---
name: grade-rubric
description: Use when comments.md has no entries yet for a specific question, or when the rubric boundaries for that question feel unclear. Run before the grade-question loop for that question. Usage: /grade-rubric Q1a
---

# Grade Rubric

Calibrate the rubric for a specific question. Takes a question ID as argument (e.g., `/grade-rubric Q1a`).

## Step 1: Load Context

Read:
- `workflow.yml` — question list, paths
- `rubric.md` — all category definitions
- `answer_key.md` — find the section matching the question ID
- `instructor_profile.md` — priority misconceptions and comment style
- `comments.md` — any existing entries for this question

## Step 2: Confirm the Correct Answer

Show the answer key section for this question and ask:
"Does this accurately capture what a full-credit response should include? Any additions or clarifications before we calibrate?"

Update `answer_key.md` if the instructor provides corrections.

## Step 3: Categorization Dialogue

Generate 5–7 plausible example responses at different error levels using the answer key as reference. Skew toward error types flagged as priorities in `instructor_profile.md`.

For each example, present it and ask the instructor to assign a rubric category:
> "A student writes: '[generated response]'
> Which rubric category applies? If a comment is needed, what should it say?"

Cover at least these response types:
1. Almost correct — minor wording/terminology slip
2. Almost correct — one mechanism missing from the justification
3. Correct method, wrong direction on a key quantity
4. Correct intuition, missing causal chain
5. Wrong method selection
6. Completely incoherent or blank

## Step 4: Record Results

For each categorized response that warrants a comment:
1. Append to `comments.md` under:
   ```
   ## <QuestionID> / <Category>
   - <comment text>
   ```
   Create the heading if it doesn't exist.

2. For any ruling that distinguishes two rubric categories (e.g., "I consider X to be Major, not Minor"), append to `decisions.md`:
   ```
   ## <QuestionID> Rubric Calibration — <YYYY-MM-DD>
   - <ruling description>
   ```

## Step 5: Set Comment Strategy

Ask: "For grading this question, which comment strategy should be used?
- **strict** — only reuse comments already in comments.md; flag new errors for your review
- **collaborative** — agent proposes draft comments for new errors; you approve before saving
- **relaxed** — agent generates and saves new comments autonomously, following your style"

Update `workflow.yml:comment_strategy` with the value, or note it applies only to this question.
