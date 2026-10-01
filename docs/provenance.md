# Provenance of the engine

`tools/` was copied on 2026-10-01 from `C:\Users\hesha\Desktop\Presentation Designs\tools` at commit
`aa148ee` (2026-09-30), **including uncommitted work in that repo**:
- the new `pptcom.py`, `fontmetrics.json` and `fonts.conf` (a python-pptx stand-in for PowerPoint COM, with calibrated text measurement);
- local edits to `deckkit.py`, `render.py` and `survey.py`.

| file | from the old project | changed here |
|---|---|---|
| family.py | family resolution, tokens, scratch | `DECK_TOKENS` override for exploration variants |
| deckkit.py | COM helpers applying tokens | `text(raw=True)` (no markup, for LaTeX); token `text.italic_symbols` (italic base letter of v_{GS}) |
| states.py | tagged states → progressive build + final-state build | tokens `progress.solution` / `progress.single` (no step dots in the student PDF or on single-state slides); defaults keep the old behaviour |
| render.py | slide PNGs + contact sheets (hash-cached) | absolute output path (COM needs it) |
| lint.py | token/contrast/off-canvas lint | (planned) overflow, image ppi, debris, missing title, uncredited figures |
| review.py, regress.py, survey.py, unlock.py | as is | — |
| pptcom.py | COM stand-in (Linux/CI) | not yet smoke-tested here |

New in this project: `eqn.py` (LaTeX → native OMML equations via Office's MML2OMML.XSL; needs `pip install latex2mathml`),
`figcrop.py` (clean a figure out of an original slide), `shapes.py` (list shape ids and boxes for a slide).

Not copied (specific to sheet notes): `binmath.py`, `export_design.py`, `families/sheet-notes/**`, the BUE sheet template.
When fixing an engine bug that also exists in the old project, note it here so it can be ported back.
