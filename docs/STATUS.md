# Status

Last updated: 2026-10-01

## Current focus
The Electronics design is being explored on one sample (from L3 MOSFETs), round by round with the user. No lecture
is converted until the user approves the sample (see `families/electronics/FAMILY.md`).

## Board
Stages: `—` not started · `survey` digest written · `review` content review done · `sample` design sample ·
`built` rebuilt, awaiting user review · `released` approved deliverables.

| module | lecture | stage | notes |
|---|---|---|---|
| Electronics 1 - 25CPES102 | L1, L2 | — | not in `reference/`: do they exist? |
| Electronics 1 - 25CPES102 | L3 MOSFETs | **built (draft 2)** | style X; 30 slides; circuits and load line redrawn natively; elaborate colour-coded examples (2 slides each). `Lecture 3 - MOSFETs/draft/`. Awaiting user review |
| Electronics 1 - 25CPES102 | L4 BJTs | survey | |
| Electronics 1 - 25CPES102 | L5 Op Amps | survey | |
| Computer Architecture | L1–L9 | — | in `reference/computer_architecture/`, not started |
| Project Management | L1–L10 | — | in `reference/project_management/`, not started |

## Open questions for the user
- Do Electronics 1 Lectures 1–2 exist?
- Is a BUE logo required on title slides?
- Which textbook edition sets the notation (older Sedra/Smith V_t, k'_n vs newer V_tn, V_OV)?

## Design rounds (electronics)
| round | what | status |
|---|---|---|
| 1 | A notebook / B datasheet / C editorial on the 7-slide MOSFET sample (`families/electronics/explore/round1/`) | rejected: too close to sheet notes (see design/decisions.md) |
| 2 | New identities from the reference templates: X "Schematic" (angular, PCB green + copper, Bebas Neue + DM Sans) / Y "Rounded" (pills, teal + coral, Poppins + Nunito); white page, white cards (`explore/round2/`) | **built and rendered; awaiting user feedback**. Comparisons: `.build/round2-compare-a.jpg` / `-b.jpg` (rebuild with `explore/round2/build.py`, then `explore/compare.py`) |

## Next steps
1. **Waiting for the user** to review L3 draft 2.
2. Then: write `design/patterns.md` from L3, release L3 rev1.0, then L4 BJTs and L5 Op Amps one at a time
   (same rules: redraw non-crisp circuits, elaborate colour-coded examples).

## Working on two devices
`git pull --rebase` before starting, commit and push after each finished unit; never force-push.

## How to rebuild the L3 draft
`python "modules/Electronics 1 - 25CPES102/Lecture 3 - MOSFETs/source/build.py"` (style X, from `design/tokens.json`).
Figures: `source/figures.py --missing` (crop into raw/) and `--enhance` (raw/ -> final). Drawings: `source/drawings.py`.
Answers: `source/check.py`. Shared components: `families/electronics/lib/{kit,circuits,plots}.py`.
