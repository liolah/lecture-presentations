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


def fmt(x, nd=2):
    s = f'{x:.{nd}f}'.rstrip('0').rstrip('.')
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
    print('ok')
