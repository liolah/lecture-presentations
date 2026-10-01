# Lecture Presentations

Redesign university lecture decks, visually and as teaching, one module at a time. The first module is Electronics.
A lecture is taught material, not a decorated document. Every design choice has to earn its place by making
something easier to understand, read or present.

## Start of every session
1. Read `docs/STATUS.md` to see what stage each lecture is at and what the next step is, and `docs/lessons.md` (mistakes
   already made and the rules that prevent them; add to it whenever something costs a rebuild).
2. Read the active family's `FAMILY.md`, then only the docs it points to for the task at hand.
3. For a specific lecture, read its `source/digest.md` and `source/review.md`. Don't re-survey the original deck.

## Layout (fixed)
| path | what |
|---|---|
| `reference/` | original inputs (decks, templates). **Read-only: never write here.** |
| `modules/<Module> - <code>/` | `module.py` (constants), `profile.md` (content profile), one folder per lecture |
| `modules/.../Lecture N - Topic/` | deliverables `(present).pptx` + `(student).pdf`; `source/` holds digest, review, data, check, build |
| `families/<family>/` | one design system (visual identity): `design/`, `lib/`, `explore/` |
| `foundation/` | quality floor shared by every family: rules and thresholds only, no colours or fonts |
| `tools/` | the engine (build, states, render, lint, survey), ported from `Desktop\Presentation Designs` (see `docs/provenance.md`) |
| `docs/` | STATUS, project decisions, workflow, provenance |
| `.build/` | scratch only (renders, digests, intermediate builds); git-ignored |

## Rules
- **Design before mass editing.** A family's design is approved on one sample before any lecture is converted.
  Everything in `families/<f>/explore/` is exploratory and is never used for deliverables.
- **Figures.** A textbook or reference screenshot is kept and cleaned: crop it, remove debris and pasted masks,
  frame it and credit it. Rebuild a figure only when cleaning can't make it readable or correct, and agree each rebuild
  with the user (log it in the lecture's `review.md`). Don't overdo it.
- **Answers are computed.** Every number in a worked example is produced and checked in `source/check.py`.
- **Content changes are reviewed, never silent.** Log each one in `source/review.md` with its category and reason.
  A technically questionable point is investigated. If it can't be resolved, ask the user.
- **Split, never shrink.** If content doesn't fit at the token sizes, split it across states or slides.
- **Keep decisions apart:** design → `families/<f>/design/decisions.md`; content → `modules/<M>/profile.md` and
  the lecture's `review.md`; engine/process → `docs/decisions.md`.
- **Author and credit (Electronics 1):** author Dr. Zahraa Ismail; thanks and credit to Dr. Sameh Osama Ezzat, who prepared the
  original material.
- **Default colours:** dark text on a light background.
- Decks are built by scripts. Never hand-edit a deliverable; change the script and rebuild.
- Shell policy: `python -c` and `powershell.exe` are blocked, so write scripts to files. PowerPoint COM needs absolute paths.
  A deck the user has open in PowerPoint is locked: don't close it, ask the user.

## Skills
- `.claude/skills/lectures`: the per-lecture workflow (survey → review → compose → verify → release).
- Consult these, don't obey them blindly: `impeccable` (typeset / layout / colorize / critique / quieter / distill) and `taste`
  (`design-taste-frontend`, `minimalist-ui`) as critique lenses on renders; `dataviz` for plots. Ignore their
  web-only rules (CSS, motion, dark mode). The family's own docs always take priority.

## Families
| family | modules | status |
|---|---|---|
| `electronics` | Electronics 1 (25CPES102) | **exploring**: sample rounds with the user (see `families/electronics/FAMILY.md`) |
