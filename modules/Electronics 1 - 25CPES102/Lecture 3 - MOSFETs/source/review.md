# L3 MOSFETs: content review

Status: proposed · agreed · done · rejected · ask user. Categories: clarity, density, repetition, terminology, sequencing,
technical, clerical, missing.

| # | slide | category | finding | proposal | status |
|---|---|---|---|---|---|
| 1 | 16 | technical | The example circuit (a web image) draws the transistor with its arrow on the **top** terminal pointing **in** (PMOS-style source), but the problem (Sedra's NMOS divider-bias example) and its answer V_D = 7 V assume an NMOS. The pasted label boxes also cut the wires. | Redraw the circuit natively as an NMOS (arrow on the source, pointing out) | ask user (shown in the round-1 sample) |
| 2 | 16 | missing | No solution on the slide | Step-by-step solution computed in check.py: V_G = 5 V; quadratic 18I² − 25I + 8 = 0; reject 0.89 mA (V_GS = −0.33 V < V_t); I_D = 0.5 mA, V_D = 7 V; saturation checked | proposed |
| 3 | 21 | missing | Small-signal example has no solution | Compute in check.py when L3 is converted | proposed |
| 4 | 1 | clerical | Title says "Lecture 2"; stray backtick | "Lecture 3" | proposed |
| 5 | 9 | clerical | "MOSEFTs" | "MOSFETs" | proposed |
| 6 | all | missing | No lecture map, outcomes, section structure or summary | Lecture map + outcomes; 5 sections; summary with a regions table | proposed |
| 7 | 3, 4, 5, 7 | repetition | Animated web GIFs repeat the cross-section idea (s5 is a 220-frame GIF with no text) | Drop them; the Sedra cross-sections carry the idea, revealed in steps | proposed |
| 8 | all | terminology | Older Sedra notation (V_t, k'_n(W/L), no V_OV); V_t clashes with the thermal voltage V_T in L4 | Decide the notation standard (see profile.md) | ask user |
| 9 | 12–14 | clarity | Triode/saturation equations are tiny blurry PNGs, spread over 3 slides with the same curve | One slide: curve + both equations, revealed in steps | proposed |
| 10 | 23 | clerical | Closing slide footer carries the legacy code 18ELEC05H | Closing slide with credits (Dr. Sameh Osama Ezzat) | proposed |
