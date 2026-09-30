---
name: lectures
description: Workflow for redesigning a university lecture deck in this repo — survey the original, review the content, compose with the module's design family, verify computed answers, render-review, release (presenting PPTX + student PDF). Use for any work on files under modules/ or families/.
---

# Lecture deck workflow

## 0. Load context cheaply
Read, in this order: `CLAUDE.md`, `docs/STATUS.md`, the family's `FAMILY.md` (plus `design/tokens.json`, `patterns.md`
and `decisions.md` once they exist), the module's `profile.md`, and the lecture's `source/digest.md` and `review.md`.
Don't re-read the original deck when a digest exists.

## 1. Gate
If the family's status is not **approved**, don't convert lectures. Work only in `families/<f>/explore/` on the
agreed sample, and bring renders to the user.

## 2. Survey (once per lecture)
- `python tools/render.py "reference/<...>.pptx" --sheet` (absolute or repo-relative path; the output goes to `.build/renders/`).
- `python tools/survey.py <deck>` for text digests.
- Write `source/digest.md`: a slide table (title, content, figures, triage K/R/D) and the issues found.

## 3. Content review → `source/review.md`
One row per finding: `# | slide | category | finding | proposal | status`.
Categories: clarity, density, repetition, terminology, sequencing, technical, clerical, missing (e.g. no solution).
Check technical doubts numerically in `check.py` or against the textbook. If still unsure, mark it `ask user`. Never change it silently.

## 4. Compose
- `data.py`: content only (titles, text, figure refs, example data).
- `check.py`: compute every answer (sympy/numpy); the build imports the results. No hand-typed numbers.
- `build.py`: `family.use('<family>')`, then the family's `lib/` builders. Reference figures go through `figures.py`
  (crop, clean, credit); equations through `eqn.py` (native OMML).
- Tag the step reveals (`@k`, `@dimK`, `@final`). Cover, section and closing slides get `#nochrome`.

## 5. Verify
`python source/check.py` → `python tools/lint.py <source.pptx>` (0 ERRORs) → render and inspect the changed slides at full
resolution: figures, equations, overlaps, text fit.

## 6. Release
`(present).pptx` = teaching states; `(student).pdf` = final states, solutions included. Update `docs/STATUS.md`,
append to the decision logs, and make one commit per lecture.
