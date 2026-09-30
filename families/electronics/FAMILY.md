# Family: electronics

Visual identity for the Electronics modules (Electronics 1, 25CPES102; later Electronics 2 if added).

## Status: exploring
There is no approved design system yet. Work happens in `explore/roundN/`: the same MOSFET sample in a few directions,
reviewed with the user each round. `design/tokens.json` is written **only after** the user approves the sample.

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
