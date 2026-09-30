# Workflow

## A. New module
1. Put the originals in `reference/<module>/` (read-only).
2. Create `modules/<Name> - <code>/module.py` (NAME, SHORT, CODE, AUTHOR, CREDIT, FAMILY) and `profile.md`.
3. Pick a family. If none fits, start a new family in **discovery**: survey → sample rounds with the user → approve → consolidate.

## B. Family design (per identity)
1. **Survey**: render the originals (`tools/render.py DECK --sheet`) and inventory content types.
2. **Brief**: list the teaching patterns the module needs and the notation rules.
3. **Sample rounds** (`families/<f>/explore/roundN/`): the same ~6–8 real slides in 2–3 directions → render →
   critique (the impeccable/taste lenses) → show the user → narrow down. Log each agreed point in `design/decisions.md`.
4. **Consolidate** after approval: `tokens.json`, `principles.md`, `patterns.md`, `template.pptx`, `lib/`, gallery.

## C. Per lecture (after the family is approved)
1. **Survey**: `source/digest.md`, covering slide by slide what each figure shows, the example data, the issues, and a figure triage (keep+clean / rebuild(why) / drop).
2. **Content review**: `source/review.md`, one row per finding: category (clarity, density, repetition, terminology,
   sequencing, technical, clerical), proposal, status (proposed / agreed / done / rejected). Technical points are checked in `check.py`.
3. **Compose**: `data.py` (content), `check.py` (computed answers), `build.py` (uses the family's `lib/`).
4. **Verify**: `check.py` passes; `tools/lint.py` has 0 ERRORs; renders reviewed at full resolution.
5. **Release**: `(present).pptx` (teaching states) + `(student).pdf` (final states). Update `docs/STATUS.md` and commit (one commit per lecture).

## Engine notes (inherited from the old project)
- Set `AutoSize` before `WordWrap=False`, otherwise the box collapses to zero width.
- Calling `ZOrder` while iterating shapes skips some; use `deckkit.send_back`.
- Layout indexes shift after `Duplicate()`; look layouts up by name.
- A cancelled build can leave a deck open in PowerPoint; `tools/unlock.py DECK` closes it without saving.
