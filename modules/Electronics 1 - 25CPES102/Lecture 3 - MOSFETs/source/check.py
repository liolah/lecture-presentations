"""Computed answers for L3 worked examples. Builds import these; nothing is typed by hand.

Run directly to print and assert the results.
"""
import math


def ex_dc_drain_voltage(VDD=10, RG1=10e6, RG2=10e6, RD=6e3, RS=6e3, Vt=1.0, kWL=1e-3):
    """Slide 16 (Sedra NMOS DC example): voltage divider bias, source degeneration. Find V_D.

    Assume saturation: I_D = 1/2 kWL (V_GS - Vt)^2 with V_GS = V_G - I_D R_S  ->  quadratic in I_D.
    """
    VG = VDD * RG2 / (RG1 + RG2)
    # 1/2 k (VG - Vt - RS I)^2 = I   ->  a I^2 + b I + c = 0
    a = 0.5 * kWL * RS ** 2
    b = -(kWL * RS * (VG - Vt) + 1)
    c = 0.5 * kWL * (VG - Vt) ** 2
    disc = b * b - 4 * a * c
    roots = sorted(((-b - math.sqrt(disc)) / (2 * a), (-b + math.sqrt(disc)) / (2 * a)))
    sols = []
    for I in roots:
        VGS = VG - I * RS
        sols.append({'ID': I, 'VGS': VGS, 'valid': VGS > Vt})
    ok = [s for s in sols if s['valid']]
    assert len(ok) == 1, sols
    ID, VGS = ok[0]['ID'], ok[0]['VGS']
    VS = ID * RS
    VD = VDD - ID * RD
    VDS = VD - VS
    VOV = VGS - Vt
    assert VDS >= VOV, 'not in saturation'
    # the same quadratic in slide units (I in mA, R in kOhm, k in mA/V^2): a I^2 + b I + c = 0
    k_, rs_ = kWL * 1e3, RS / 1e3
    quad = (0.5 * k_ * rs_ ** 2, -(k_ * rs_ * (VG - Vt) + 1), 0.5 * k_ * (VG - Vt) ** 2)
    return {
        'VG': VG, 'ID': ID, 'VGS': VGS, 'VS': VS, 'VD': VD, 'VDS': VDS, 'VOV': VOV,
        'roots_mA': [r * 1e3 for r in roots], 'rejected_VGS': sols[1]['VGS'] if sols[0]['valid'] else sols[0]['VGS'],
        'quad_mA': quad,
    }


def ex_cs_amp_feedback_bias(VDD=15.0, RD=10e3, RG=10e6, RL=10e3, Vt=1.5, kWL=0.25e-3, VA=50.0):
    """Slide 21 (Sedra CS amplifier, drain-to-gate feedback bias R_G). Find A_v = v_o/v_i and R_in.

    DC (r_o neglected, as Sedra does): no gate current, so V_GS = V_D = V_DD - R_D I_D,
    with I_D = 1/2 kWL (V_GS - Vt)^2. Small signal: g_m = kWL (V_GS - Vt), r_o = V_A / I_D,
    A_v ~= -g_m (R_D || R_L || r_o) (R_G's feedback current neglected), R_in = R_G / (1 - A_v) (Miller).
    """
    # 1/2 k (VDD - RD I - Vt)^2 = I
    a = 0.5 * kWL * RD ** 2
    b = -(kWL * RD * (VDD - Vt) + 1)
    c = 0.5 * kWL * (VDD - Vt) ** 2
    disc = b * b - 4 * a * c
    roots = sorted(((-b - math.sqrt(disc)) / (2 * a), (-b + math.sqrt(disc)) / (2 * a)))
    ok = [I for I in roots if VDD - RD * I > Vt]
    assert len(ok) == 1, roots
    ID = ok[0]
    VGS = VD = VDD - RD * ID
    assert VD >= VGS - Vt                      # saturation (always true when drain is tied to gate through R_G)
    gm = kWL * (VGS - Vt)
    ro = VA / ID
    Rp = 1 / (1 / RD + 1 / RL + 1 / ro)
    Av = -gm * Rp
    Rin = RG / (1 - Av)
    # exact (R_G feedback included): v_o (1/Rp + 1/RG) = v_i (1/RG - g_m)
    Av_exact = (1 / RG - gm) / (1 / Rp + 1 / RG)
    other = [I for I in roots if I != ID][0]
    return {'ID': ID, 'VGS': VGS, 'VD': VD, 'gm': gm, 'ro': ro, 'Rp': Rp, 'Av': Av, 'Rin': Rin,
            'Av_exact': Av_exact, 'Rin_exact': RG / (1 - Av_exact),
            'roots_mA': [r * 1e3 for r in roots], 'other_mA': other * 1e3, 'other_VGS': VDD - RD * other,
            # quadratic in slide units (I in mA): a I^2 + b I + c = 0
            'quad_mA': (0.5 * kWL * 1e3 * (RD / 1e3) ** 2, -(kWL * 1e3 * (RD / 1e3) * (VDD - Vt) + 1),
                        0.5 * kWL * 1e3 * (VDD - Vt) ** 2)}


def fmt(x, nd=2):
    s = f'{x:.{nd}f}'
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('-', '−')


if __name__ == '__main__':
    r = ex_dc_drain_voltage()
    # slide form: with I_D in mA and R in kOhm:  1/2 * 1 * (4 - 6 I)^2 = I  ->  18 I^2 - 25 I + 8 = 0
    assert abs(r['VG'] - 5) < 1e-12
    assert abs(r['ID'] - 0.5e-3) < 1e-12 and abs(r['VD'] - 7) < 1e-9
    assert abs(r['roots_mA'][1] - 8 / 9) < 1e-9          # 0.889 mA root, rejected
    assert abs(r['rejected_VGS'] - (5 - 6 * 8 / 9)) < 1e-9  # -0.33 V < Vt
    assert r['quad_mA'] == (18.0, -25.0, 8.0)
    for k, v in r.items():
        print(k, v)
    a = ex_cs_amp_feedback_bias()
    # Sedra's published values: I_D = 1.06 mA, V_D = 4.4 V, g_m = 0.725 mA/V, r_o = 47 k, A_v = -3.3, R_in = 2.33 M
    assert abs(a['ID'] - 1.06e-3) < 0.01e-3 and abs(a['VD'] - 4.4) < 0.05
    assert abs(a['gm'] - 0.725e-3) < 0.005e-3 and abs(a['ro'] - 47e3) < 0.5e3
    assert abs(a['Av'] + 3.3) < 0.05 and abs(a['Rin'] - 2.33e6) < 0.02e6
    assert abs(a['Av_exact'] - a['Av']) < 0.01          # R_G feedback is negligible, as the slide assumes
    for k, v in a.items():
        print(k, v)
    print('ok')
