# Lessons learned: read before building anything

Mistakes already made in this project, and the rule that prevents each one. Add to this file whenever something
costs a rebuild. Newest at the bottom of each section.

## Design process
| mistake | cost | rule |
|---|---|---|
| Round 1 reused the sheet-notes vocabulary (Bahnschrift/Segoe UI, navy, answer chips, progress dots) | a whole design round rejected | Lecture identities come from `reference/templates/`, never from `Presentation Designs`. Before showing a design, compare it with the sheet-notes gallery: shared fonts, palette or signature components mean it is not new. |
| Asked the user to choose between variants on a 7-slide sample | user preferred to judge on real material | When a style choice is pending, build the **full lecture in every candidate style** (one code path, the style chosen by tokens) and let the user compare the real thing. |
| Proposed too much rebuilding | user: "don't overdo it" | Keep and clean reference figures; propose a rebuild only for figures that are wrong or unreadable, and list them as `ask user` in `review.md`. |

## Engine and PowerPoint gotchas
| symptom | cause | fix (already in the code) |
|---|---|---|
| `V_{DD}` in an equation rendered as "VDD" | `deckkit.text` applies its own `_{}` subscript markup to the LaTeX source | Equation boxes use `text(..., raw=True)` (`kit.eq` does this) |
| Units and single-letter labels stay italic | latex2mathml drops `\mathrm` on single letters | `eqn.py` rewrites `\mathrm{..}` to `\text{..}`; write units as `\ \mathrm{V}`, and `\mathrm{k}\Omega` (not `\mathrm{k\Omega}`) |
| Spacing between paired equations vanished | `\qquad`/`\quad` are dropped by MML2OMML | Use `,\ \ \ \ \ ` (explicit spaces) |
| `\prime` rendered as the word "prime" | sed ate the backslash | Edit LaTeX in Python sources with the Edit tool, never sed |
| `Slide.Export` failed | COM needs absolute paths | `render.py` uses absolute paths; do the same in any new script |
| Title invisible on Y title/section slides | a white frame drawn after the title covered it | Send background frames back: `.ZOrder(1)` (or draw them first) |
| "Another slide already has this name" | slide names must be unique | `kit.slide` appends `s<index>` |
| `g_m` in a Bebas Neue title showed as "G_M" | all-caps display face | `kit.slide` sets subscripted symbols in titles in the body font, italic |
| Long section title overlapped the numeral | fixed title box, bottom-anchored | `section_slide` shrinks titles longer than 22 chars |
| `fmt(50, 0)` gave "5" | stripped trailing zeros of integers | `check.fmt` only strips after a decimal point |
| Figure extraction hung once, and the process could not be killed | transient COM stall; `Stop-Process`/`tasklist` are blocked here | `figures.py --missing` re-extracts only absent figures; run long jobs in the background and check progress via file timestamps |

| `\color{..}` coloured the rest of the equation; Office's converter dropped colours | `\color` is a switch; MML2OMML ignores `mathcolor` | Use `\textcolor{#hex}{..}` (or `kit.gc('g1', ..)`); `eqn.py` carries the colour through with private-use sentinels and splits the runs |
| Re-running a sharpening pass would sharpen again | in-place image processing is not idempotent | `figures.py` crops into `raw/` and enhances raw/ -> final, always |
| Plot labels collided with the load line and with axis ticks | labels placed at fixed positions | `drawings.load_line` places curve labels where the line clears the whole label width; the x-axis label sits right of the arrow |
| Example circuit spilled out of its card on the right | fixed drawing width, card too narrow | Check a drawing's right-most label against the card edge; put labels on the free side |

## Working efficiently here
- **Shell policy (lean-ctx):** `python -c`, python heredocs, `tasklist`, `Stop-Process` and redirects into project files are blocked. Write
  scripts to the scratchpad and run them. `ctx_shell` may stay pinned to another project root: start commands with
  `cd "<repo>" &&`, and use native Read for files outside the root.
- **Timings:** one full-lecture build (COM + states + PDF) takes about 3–5 min per style; a render takes about 1–2 min. Run both styles in
  one background job, then render, then read `sheet.jpg` first and open full-size PNGs only for suspicious slides.
- **Review order after a build:** contact sheet → slides with long titles, dense steps, or many equations → structural
  slides (title, section, closing). Most defects so far were overlaps, empty space and font-case problems.
- **Before sending to the user:** check all equations render (no raw LaTeX), no title is hidden, and the student PDF has no step dots.
