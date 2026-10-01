# Round 1: three light directions on the same MOSFET sample (EXPLORATORY)

**Sample:** 7 real slides from L3: title, lecture map, section divider, concept with a cleaned Sedra figure, the
triode/saturation equations, the DC worked example (step-by-step) and a summary table.

**Build:** `python build.py` (all variants) → `.build/electronics/round1/<V>/`.

**Compare:** `python ../compare.py round1 1,4,5,6 A,B,C out.jpg`.

## Same in all three: proposed regardless of direction
- **Native equations (OMML):** they replace the blurry PNG and MathType equations. They are editable in PowerPoint, sharp in the PDF, and use Cambria Math.
  Subscripts are upright labels (V_GS) and variables are italic. Body text italicises quantity symbols the same way.
- **Cleaned reference figures:** cut from the original slides at about 3× resolution, with the pasted masks flattened, and credited ("Figure: Sedra & Smith").
- **Worked example as a step reveal:** in the presenting deck the question stays visible and each step appears in turn (6 states), with node voltages
  appearing on the circuit as they are found. The student PDF shows the final state. The answer goes in one chip, followed by a ✓ check of the assumption.
- **Navigation:** a lecture map with outcomes; section slides that show where we are; the section name above each title; footer and page number.
- **Real titles** in title placeholders, so the PDF outline works.

## The directions
| | A: Engineering notebook | B: Datasheet | C: Textbook editorial |
|---|---|---|---|
| page | warm paper `F8F5EE` | pure white | cool grey `F2F4F7` |
| type | Bahnschrift SemiBold headings, Segoe UI body | Segoe UI Semibold throughout, Consolas labels | Georgia headings, Segoe UI body |
| colour | ink `1F2A37`, steel blue `1F5F8B` (matches the Sedra figure blue), copper `A8481A` for results | near-black, one burnt orange `C2410C` | deep navy, blue `2B5C8A`, red `A61B1B` for results |
| figures | on white plates with a hairline | bare (white on white) | on white rounded cards |

## Critique (taste/impeccable lenses + teaching use)
**A, notebook**
- Strengths:
  - The warm page cuts projector glare.
  - Steel blue echoes the textbook figures, so the figures look as if they belong.
  - Bahnschrift (DIN) has an engineering voice and reads well from a distance.
  - The plates make pasted textbook figures look deliberate.
  - The role colours are clear: blue = found quantities, copper = the answer.
- Risks:
  - Two accents need discipline.
  - The plates add a frame around every figure.
  - The tinted page shows when a student prints the PDF (minor).

**B, datasheet**
- Strengths: the cleanest and most neutral; figures blend into the page; best for printing.
- Risks:
  - Most generic: it could be any company's deck.
  - Monospace labels used as a "technical costume" (flagged by the impeccable craft floor).
  - One orange for both found values and the answer blurs the roles.
  - A pure white page glares on projectors.
  - Hairlines under titles add noise.

**C, editorial**
- Strengths: an academic "textbook" feel; the serif titles have character.
- Risks:
  - Three type voices (Georgia, Segoe UI, Cambria Math).
  - Serif titles are less legible from the back of a room.
  - Cards everywhere become scaffolding.
  - The thick coloured left bar on the definition card is a known cliché.
  - The navy section band is heavy.
  - The cool grey makes white figures look like stickers.

**Recommendation:** A as the base. Possibly borrow B's bare-figure approach (decide on the plates) and keep A's two-role colour.

## Open questions for the user (round 1)
1. Direction (A / B / C / mix).
2. Figure framing: plate vs bare.
3. The section label above titles (it carries navigation, but impeccable bans "eyebrows"): keep it, move it to the footer, or drop it?
4. Subscripts in equations: upright (ISO style) or italic (as in the Sedra figures)?
5. Rebuild the s16 example circuit? The original web image shows a PMOS-style transistor (arrow on the top terminal, pointing in),
   which is inconsistent with the NMOS problem and its answer. The native redraw is used in this sample.
