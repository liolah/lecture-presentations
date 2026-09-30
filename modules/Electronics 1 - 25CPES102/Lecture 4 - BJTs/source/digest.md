# L4 BJTs: survey digest (first pass)

Source: `reference/electronics_1/25CPES102_Lecture_4_BJTs.pptx` (19 slides). Renders: `.build/renders/25CPES102_Lecture_4_BJTs/`.
Triage: **K** keep+clean · **R** rebuild (why) · **D** drop. The full triage is done when this lecture is converted.

| # | content | notes / triage |
|---|---|---|
| 1 | title/countdown | countdown **D**; stray backtick |
| 2–4 | structure: Sedra npn/pnp slab + 3-D + symbol; near-duplicate build slides | **K** figures; merge into 1–2 slides with states |
| 5–10 | active mode (web electron-flow figure), I_E=I_C+I_B, β, α (MathType, **repeated identically on 4 slides**) | web figure **K**; equations → native, shown once and built up |
| 11 | modes table (EMF) + V_C−V_B criterion + saturation note + Sedra i_C–v_CE curves | table → native table (**R**: clarity, cheap); curves **K** |
| 12 | CB/CE/CC configurations (web GIF) | **K** |
| 13–15 | Example "analyze … β=100", same prompt ×3, three circuits (one 132×202 px ≈19 px/in, **blurry**) | blurry circuit is a rebuild candidate (**R?**, agree with the user); add computed solutions |
| 16 | small-signal / g_m: equations as PNG snippets, 16 debris rects | equations → native derivation |
| 17 | hybrid-π models (Sedra) | **K** |
| 18 | CE amplifier (5.8 MB bitmap EMF), deck ends abruptly | **K**; needs analysis/summary (content) |
| 19 | thank you (legacy footer 18ECE05C) | **D** → closing slide |

Content flags: V_T (thermal) vs L3's V_t; the saturation criterion stated as V_C − V_B < −0.4 V (older Sedra); no summary.
