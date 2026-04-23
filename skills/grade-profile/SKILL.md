---
name: grade-profile
description: Use when an instructor_profile.md does not yet exist for this subject area, or when updating existing grading style preferences. Reusable across assignments — run once per instructor/subject, not once per assignment.
---

# Grade Profile

Create or update `instructor_profile.md` for the current project. The profile is portable — it can be saved to a shared location (e.g., `~/.claude/grading/<subject>_profile.md`) and referenced from multiple assignment workflow.yml files.

## Step 1: Check for Existing Profile

Check the path at `workflow.yml:project.profile` (default: `instructor_profile.md`). If the file exists:
- Show its current contents
- Ask: "Would you like to update a section, or start from scratch?"
- If updating: ask which section, then rewrite only that section

## Step 2: Ask Profile Questions

Ask these one at a time:

**1. Subject area**
"What subject area does this profile apply to? This label will appear at the top of the profile for easy identification."

**2. Strictness calibrations**
"Are there specific topics or error types where you apply stricter or more lenient standards than a default rubric? Describe them.
Example: 'Strict: students must not accept the null hypothesis without justification. Lenient: informal language about p-values is acceptable.'"

**3. Terminology standards**
"Are there specific terms, notation, or naming conventions you require or prohibit?"

**4. Priority misconceptions**
"What are the two or three most common conceptual errors students make in this subject that you want the grading agent to flag consistently?"

**5. Comment style**
"How should feedback comments be phrased? Options:
- Socratic questions only (never corrections)
- Leading questions (hint toward the answer)
- Direct corrections acceptable"

**6. Edge case philosophy**
"When uncertain between two adjacent rubric categories, do you prefer to round up (benefit of the doubt) or round down (conservative)?"

## Step 3: Write instructor_profile.md

```markdown
# Instructor Grading Profile
Subject area: <subject>
Last updated: <YYYY-MM-DD>

## Strictness Calibrations
<answers from Q2>

## Terminology Standards
<answers from Q3>

## Priority Misconceptions
<answers from Q4>

## Comment Style
<answers from Q5>

## Edge Case Philosophy
<answers from Q6>
```

Save to the path in `workflow.yml:project.profile`. If the user wants to save it to a user-level path (e.g., `~/.claude/grading/<subject>_profile.md`), update `workflow.yml:project.profile` to that path so future skills find it automatically.
