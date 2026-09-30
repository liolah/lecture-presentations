# Electronics 1 (25CPES102): content profile

## Originals
`reference/electronics_1/`: L3 MOSFETs (23 slides), L4 BJTs (19), L5 Op Amps (23). They were built in Keynote on a 26.67×15 in canvas
by Dr. Sameh Osama Ezzat (last modified Oct–Nov 2025). L1–L2 are not present.

## Arc (as found)
MOSFET structure → channel formation → V_DS effects/pinch-off → CMOS → I–V regions → DC circuits → current mirror →
amplifier and small-signal g_m → switch · BJT structure → active mode and current gains → modes → configurations → DC
circuits → small signal and hybrid-π → CE amplifier · Op-amp levels → ideal op amp → inverting / summer /
non-inverting / follower → difference amp, CMRR → saturation → integrator / differentiator → finite gain.

## Textbook and notation
Figures come from the Sedra/Smith instructor set. The file names (ch.4 = BJTs, ch.5 = FETs) point to an older edition.
The notation follows that edition: V_t (threshold), k'_n(W/L), with no V_OV.
**Open:** keep the older notation to match the figures, or adopt the newer one (V_tn, V_OV = V_GS − V_tn)?
Either way, use it consistently and follow Sedra's case convention: v_GS total, V_GS DC, v_gs small-signal.

## Cross-lecture issues (content)
- V_t (MOSFET threshold) vs V_T (BJT thermal voltage) clash across L3/L4. Keep the subscripts distinct and explain the difference once.
- Worked examples state only the problem (L3 s16, s21; L4 s13–15; L5 s9). Solutions are to be computed and added.
- No lecture map, learning outcomes, recaps or summaries anywhere.
- Course name spelled three ways; department differs (Computer vs Electrical Eng.); footers carry legacy codes
  18ELEC05H / 18ECE05C / 20ECE05C.

## Misconceptions worth addressing (candidates)
- Treating pinch-off as the current stopping (it is where the current saturates).
- Confusing the saturation region names across devices (MOSFET saturation ≈ BJT active).
- Virtual ground treated as a real ground connection.
