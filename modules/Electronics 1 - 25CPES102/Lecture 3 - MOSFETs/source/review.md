# L3 MOSFETs: content review

Status: proposed · agreed · done · rejected · ask user. Categories: clarity, density, repetition, terminology, sequencing,
technical, clerical, missing.

| # | slide | category | finding | proposal | status |
|---|---|---|---|---|---|
| 0 | — | — | **Draft 1 (2026-10-01)** applies every *proposed* row below, so the user can review the full lecture; nothing is final until the user approves | — | — |
| 1 | 16 | technical | The example circuit (a web image) draws the transistor with its arrow on the **top** terminal pointing **in** (PMOS-style source), but the problem (Sedra's NMOS divider-bias example) and its answer V_D = 7 V assume an NMOS. The pasted label boxes also cut the wires. | Redraw the circuit natively as an NMOS (arrow on the source, pointing out) | agreed (user, 2026-10-01); done |
| 2 | 16 | missing | No solution on the slide | Step-by-step solution computed in check.py: V_G = 5 V; quadratic 18I² − 25I + 8 = 0; reject 0.89 mA (V_GS = −0.33 V < V_t); I_D = 0.5 mA, V_D = 7 V; saturation checked | done (draft) |
| 3 | 21 | missing | Small-signal example has no solution | Computed in check.py (matches Sedra's published values): I_D = 1.06 mA, V_GS = V_D = 4.4 V, g_m = 0.728 mA/V, r_o = 47 kΩ, A_v ≈ −3.29 V/V, R_in = R_G/(1 − A_v) = 2.33 MΩ. Exact analysis that keeps R_G's feedback current differs by < 0.1 % | done (draft) |
| 3a | 21 | clarity | The circuit image is 243×153 px: blurry when projected | Rebuild natively (CS stage, R_G feedback, coupling capacitors, R_L) | agreed (figure-quality rule, 2026-10-01); done in draft 2 |
| 3b | 22 | clarity | Switch figure is a 267×146 px web GIF: blurry | Rebuilt natively: MOSFET switch ≡ switch model | done (draft 2) |
| 3g | 9, 15, 17, 18, 20 | clarity | Symbols (web, 590×344), large-signal model, current mirror (web, masks), CS amplifier and small-signal models (Sedra JPGs ≈ 450–700 px) are soft when projected | Redrawn natively in `drawings.py` (crisp, editable, colourable) | done (draft 2) |
| 3h | 18 | clarity | Load-line graph is a 454×305 px web GIF | Replaced by a native plot computed from the square law (k′_n(W/L) = 1 mA/V², V_DD = 10 V, R_D = 1.25 kΩ), points A (edge of triode) and B (cutoff) computed | done (draft 2) |
| 3i | 16, 21 | missing | Worked solutions were compact | Each example spans 2 slides with elaborate steps, a one-line reason per step, and colour-coded givens (list, circuit labels, substitutions); the rejected roots are shown and explained | done (draft 2), per the user's preference |
| 3j | all kept figures | clarity | Raster figures interpolated | `figures.py` enhancement pass (sharpen + clean white) from raw/ crops | done (draft 2) |
| 3c | 17 (new) | sequencing | Students meet the DC example without a method | New slide "DC analysis: assume, solve, check" before the example | done (draft) |
| 3d | 18–21 | clarity | The g_m derivation was 8 MathType objects with 27 animation steps and 16 debris shapes | One native derivation in 4 revealed steps, ending in A_v = −g_m R_D | done (draft) |
| 3e | 20 | missing | r_o and V_A appear in the s21 example without introduction | One line on the models slide: r_o = V_A/I_D models the slope of the saturation curves (V_A: Early voltage) | done (draft) |
| 3f | 9 | terminology | The symbols image puts the arrow on the body (4-terminal symbols) | Text explains the body-arrow convention; PMOS conducts for v_GS < V_t with V_t negative (older Sedra) | done (draft) |
| 4 | 1 | clerical | Title says "Lecture 2"; stray backtick | "Lecture 3" | proposed |
| 5 | 9 | clerical | "MOSEFTs" | "MOSFETs" | proposed |
| 6 | all | missing | No lecture map, outcomes, section structure or summary | Lecture map + outcomes; 5 sections; summary with a regions table | proposed |
| 7 | 3, 4, 5, 7 | repetition | Animated web GIFs repeat the cross-section idea (s5 is a 220-frame GIF with no text) | Drop them; the Sedra cross-sections carry the idea, revealed in steps | proposed |
| 8 | all | terminology | Older Sedra notation (V_t, k'_n(W/L), no V_OV); V_t clashes with the thermal voltage V_T in L4 | Decide the notation standard (see profile.md) | ask user |
| 9 | 12–14 | clarity | Triode/saturation equations are tiny blurry PNGs, spread over 3 slides with the same curve | One slide: curve + both equations, revealed in steps | proposed |
| 10 | 23 | clerical | Closing slide footer carries the legacy code 18ELEC05H | Closing slide with credits (Dr. Sameh Osama Ezzat) | proposed |
