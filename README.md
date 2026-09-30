# Lecture Presentations

Scripts, design systems and docs for redesigning university lecture decks, one module at a time. The first module is
**Electronics 1 (25CPES102)**.

- Current state and next steps: [docs/STATUS.md](docs/STATUS.md)
- How the project works: [CLAUDE.md](CLAUDE.md) · [docs/workflow.md](docs/workflow.md)
- Why things are the way they are: [docs/decisions.md](docs/decisions.md) and each family's `design/decisions.md`

Requirements: Windows with Microsoft PowerPoint (COM), Python 3.11+ with `pywin32 python-pptx lxml Pillow`.
Originals live read-only in `reference/`. Deliverables live in `modules/<module>/<lecture>/`.
