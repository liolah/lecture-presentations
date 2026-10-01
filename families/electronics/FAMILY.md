# Family: electronics

Visual identity for the Electronics modules (Electronics 1, 25CPES102; later Electronics 2 if added).

## Status: approved (style X "Schematic", user, 2026-10-01)
- Tokens: `design/tokens.json`. Components: `lib/kit.py` (slides, cards, tags, givens, elaborate solutions, tables),
  `lib/circuits.py` (native schematics between terminal points), `lib/plots.py` (computed native plots).
- Worked examples: colour-coded givens (`g1`..`g4`) in the Given list, on the circuit and in every substitution
  (`kit.gc`); elaborate steps with a one-line reason each (`kit.solution`); usually 2 slides per example.
- Figures: textbook figures kept and enhanced (`figures.py`); circuits and graphs that are not crisp are redrawn natively.
- Exploration history: `explore/round1` (rejected: too close to sheet notes), `explore/round2` (X chosen over Y).
- Pending: `design/patterns.md` (pattern catalogue) and a PowerPoint template, to be written from L3 once its draft 2 is reviewed.

## What this family has to serve (from the survey of L3–L5)
- **Textbook figures dominate.** Sedra/Smith instructor figures, drawn in a soft steel-blue on white, and some web images.
  They are kept and cleaned, so the design has to look good *around white-background figures*.
- **Equations everywhere.** Device equations, derivations and small-signal models. The originals are MathType or
  blurry PNG; the plan is native (OMML) equations.
- **Worked examples.** Circuit + given values → a step-by-step solution (the originals have none).
- **Recurring kinds of slide:** device operation (cross-section + a statement), characteristic curves with their region
  equations, circuit configurations (op-amp family), models (small-signal / hybrid-π), mode tables, comparisons.

## Files
- `design/decisions.md`: agreed design points, dated, with reasons (also records rejected directions).
- `explore/`: prototypes, clearly exploratory.
- `lib/`: builders (created during consolidation). `figures.py` places cleaned reference figures;
  `eqn.py` produces native equations.
