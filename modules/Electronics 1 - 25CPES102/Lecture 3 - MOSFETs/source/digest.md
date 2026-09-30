# L3 MOSFETs: survey digest

Source: `reference/electronics_1/25CPES102_Lecture_3_MOSFETs.pptx` (23 slides, Keynote "White" theme, 26.67×15 in).
Renders: `.build/renders/25CPES102_Lecture_3_MOSFETs/`.

## Slide by slide
Triage: **K** keep+clean · **R** rebuild (why) · **D** drop.

| # | title (as found) | content | figures → triage |
|---|---|---|---|
| 1 | Title / countdown | says "Lecture 2" (wrong); stray backtick; blurry 645 px background photo; countdown + laser.wav | background photo **D**; countdown **D** (offer separately) |
| 2 | MOSFET (section-like) | NMOS 3-D structure + cross-section (Sedra) | Sedra 3-D+section **K** |
| 3 | Operation with no gate voltage | band diagram (web), Keynote-style animated S/D GIF, cross-section | band diagram **K**; GIF **D** (animated, dark-background, duplicates the cross-section) |
| 4 | Creating a channel | definition of V_t, "inversion layer"; channel cross-section (Sedra); animated GIF | Sedra induced-channel **K**; GIF **D** |
| 5 | (no title) | 220-frame animated GIF, full slide | **D** (the teaching point is on s4; could be replaced later by a native build, *if agreed*) |
| 6 | Operation as V_DS is increased | Sedra tapered channel | **K** |
| 7 | same | pinch-off statement; web dark GIF + Sedra | Sedra **K**; web GIF **D** |
| 8 | CMOS | Sedra CMOS cross-section | **K** |
| 9 | n- vs p-channel "MOSEFTs" (typo) | symbols (web image) | **K** (clean) |
| 10 | I–V curves | Sedra I_D–V_DS family + test circuit | **K** |
| 11 | I–V curves | Sedra I_D–V_GS (saturation) | **K** |
| 12 | Triode region | Sedra single curve with annotations; triode equations as **tiny PNGs (≈20 px/in)** | curve **K**; equations **R → native equations** (blurry) |
| 13 | Triode region | r_DS equation + the same curve | curve **K**; equations **R → native** |
| 14 | Saturation region | saturation equation PNG + curve | **R → native** eq; curve **K** |
| 15 | Saturation region | large-signal equivalent circuit (Sedra) over the curve, highlight box | **K** |
| 16 | MOSFETs in DC circuits | **Example**: V_DD=10 V, R_G1=R_G2=10 MΩ, R_D=R_S=6 kΩ, V_t=1 V, k'_n(W/L)=1 mA/V²; find V_D. Circuit is a web JPEG with 4 white label boxes pasted over it | circuit **K** (clean the masks → one clean image); solution to add (computed) |
| 17 | Current mirror | web circuit with 3 white masks; I_O/I_REF MathType | circuit **K**; equation → native |
| 18 | MOSFET as amplifier | load line (web), Sedra circuit, v_DS = V_DD − R_D i_D (MT) | **K**; eq → native |
| 19 | Linear amplifier / g_m | 8 MathType equations + 16 debris rectangles + 27 animation steps (derivation) | equations → native derivation with a step reveal |
| 20 | Linear amplifier | Sedra small-signal models (a, b) + g_m | **K**; eq → native |
| 21 | Example | small-signal gain and R_in; V_t=1.5 V, k'_n(W/L)=0.25 mA/V², V_A=50 V; circuit EMF (147 KB) | **K**; solution to add (computed) |
| 22 | MOSFET as switch | web GIF (red wire highlight) | **K** |
| 23 | Thank you | Gabriola, thumbs-up clip-art, legacy footer 18ELEC05H | **D** → closing slide with credits |

## Issues found (for review.md)
- Lecture number: s1 says "Lecture 2"; the file says Lecture 3.
- Titles are inconsistent: red underlined Times (s9–22), black Helvetica Light (s3–8), large red section-style (s2).
- There is no lecture map, recap or summary; the deck ends at "switch" with no wrap-up.
- s16 and s21 examples have no solutions. The s16 answer (computed separately): V_G = 5 V, I_D = 0.5 mA, V_GS = 2 V, V_D = 7 V
  (the other root, I_D = 0.89 mA, gives V_GS < V_t and is rejected). Formalise this in check.py.
- s5 and the animated GIFs carry the "channel forms" idea without explanation; s4 already has it.
- Notation: V_t, k'_n(W/L) (older Sedra).
