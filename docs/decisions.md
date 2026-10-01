# Project decisions (engine, process, structure)

Design decisions belong to each family (`families/<f>/design/decisions.md`). Content decisions belong to module
profiles and lecture reviews. Newest entries at the bottom.

| date | decision | why | source |
|---|---|---|---|
| 2026-10-01 | New repo, separate from `Presentation Designs`; the engine is **copied** into `tools/`, not shared | the two projects evolve independently; the engine is small (~3k lines); provenance is recorded | Claude |
| 2026-10-01 | Families = visual identities; a module picks one in `module.py`; `foundation/` holds the shared quality floor (rules only) | modules may differ visually but share academic quality standards | user brief |
| 2026-10-01 | Originals moved unchanged to `reference/` (electronics_1, computer_architecture, project_management, templates) | one read-only home for inputs | Claude |
| 2026-10-01 | Deliverables per lecture: presenting PPTX (step builds) + student PDF (final states, solutions included) | user choice | user |
| 2026-10-01 | Reference figures are kept and cleaned, not rebuilt; rebuilds are agreed one by one | user: "don't overdo it" | user |
| 2026-10-01 | Design is agreed on one sample, over rounds with the user, before any lecture is converted | user: probe the design together before committing | user |
| 2026-10-01 | taste + impeccable installed as user-level skills without impeccable's hooks | hooks would run on every edit in every project and download an engine binary | user |
| 2026-10-01 | `render.py` output path made absolute | COM `Slide.Export` fails with relative paths | Claude |
| 2026-10-01 | Equations are native OMML generated from LaTeX (`tools/eqn.py`), injected after the COM build | editable, crisp in the PDF; replaces MathType and PNG equations; verified to render in PowerPoint and survive `states.py` duplication | Claude |
| 2026-10-01 | Reference figures are cleaned by rendering only their shapes from the original slide at 3× (`tools/figcrop.py`) | flattens pasted label masks into one picture; never modifies the original | Claude |
| 2026-10-01 | Exploration variants carry their own tokens (`DECK_TOKENS`), one process per variant | deckkit reads tokens at import | Claude |
