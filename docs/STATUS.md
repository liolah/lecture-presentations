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
| Electronics 1 - 25CPES102 | L3 MOSFETs | **built (draft 1)** | full 28-slide lecture in both candidate styles: `Lecture 3 - MOSFETs/draft/` (present PPTX + student PDF). Awaiting user review: style X vs Y, content (`source/review.md`), and the 2 low-res figure rebuilds (3a, 3b) |
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
1. **Waiting for the user** to review the L3 draft (X and Y) and pick or adjust a style.
2. Then: consolidate the chosen style into `families/electronics/design/` (tokens, patterns, template) and promote
   `lib/kit.py` from candidate to approved; release L3 rev1.0; then L4 and L5, one at a time.

## How to rebuild the L3 draft
`python "modules/Electronics 1 - 25CPES102/Lecture 3 - MOSFETs/source/build.py"` (both styles; or pass X / Y).
Figures: `source/figures.py --missing`. Answers: `source/check.py`. Shared components: `families/electronics/lib/kit.py`.
