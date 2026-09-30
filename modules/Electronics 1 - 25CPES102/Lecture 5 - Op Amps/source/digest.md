# L5 Op Amps: survey digest (first pass)

Source: `reference/electronics_1/25CPES102_Lecture_5_Op Amps.pptx` (23 slides). Renders: `.build/renders/25CPES102_Lecture_5_Op_Amps/`.
Triage: **K** keep+clean · **R** rebuild (why) · **D** drop. The full triage is done when this lecture is converted.

| # | content | notes / triage |
|---|---|---|
| 1 | title/countdown | countdown **D** |
| 2–4 | electronics levels; op amp at transistor level (Wikipedia); IC 741 photo | **K** (credit Wikipedia) |
| 5–6 | op amp model, ideal op amp (electronics-tutorials) | **K** |
| 7–9 | inverting configuration: circuit GIF with pasted R1/R2 masks; derivation PNG; example as a 408×246 PNG (**≈26 px/in, blurry**) | circuit **K** (clean masks); derivation → native; example circuit is a rebuild candidate (**R?**) |
| 10 | weighted summer (MathType) | eq → native |
| 11–12 | non-inverting, voltage follower (loading eq) | eq → native |
| 13–17 | difference amp: 5 slides, same circuit with pasted R labels; v_Id, v_Icm, CMRR, superposition condition, A_d | **check that the pasted labels match the equation indices**; merge into fewer slides with states |
| 18–19 | output saturation (web GIFs) | **K** |
| 20–21 | integrator, differentiator | eq → native |
| 22 | finite open-loop gain, "Wrong assumption" | eq → native; explain the result, not just show it |
| 23 | thank you | **D** → closing |

Content flags: 741-centric; no GBW or slew rate (consider whether they belong in Electronics 1); no summary.
