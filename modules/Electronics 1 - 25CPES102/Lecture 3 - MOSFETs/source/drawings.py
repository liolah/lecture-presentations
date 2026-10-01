"""L3 native drawings (circuits + plots), replacing low-resolution or relabelled figures (review.md 1, 3a, 3b, figure
quality rule). Each function draws inside the area starting at (ox, oy) and returns useful node points.
Colour keys for givens: 'g1'..'g4' (tokens); default ink 'navy'.
"""
from circuits import (wire, dot, terminal, ground, label, arrow, resistor, capacitor, vsource, acsource,
                      dep_isource, switch, nmos, mos4)
from plots import Plot
import kit


def dc_example(sl, ox, oy, col=None, size=19, h=470):
    """Sedra NMOS DC example: divider bias R_G1/R_G2, R_D, R_S, V_DD. About 330 x (h + 50) pt from (ox, oy)."""
    c = {'vdd': 'navy', 'rg': 'navy', 'r': 'navy'}; c.update(col or {})
    xl, xr = ox + 60, ox + 250
    yt, yb = oy + 60, oy + h
    xm = (xl + xr) / 2
    terminal(sl, (xm, oy + 14))
    wire(sl, (xm, oy + 19.5), (xm, yt))
    label(sl, (xm + 14, oy + 12), '+V_{DD} = 10 V', color=c['vdd'], size=size, bold=True)
    wire(sl, (xl, yt), (xr, yt)); dot(sl, (xm, yt))
    wire(sl, (xl, yb), (xr, yb)); dot(sl, (xm, yb))
    ground(sl, (xm, yb))
    yg = (yt + yb) / 2
    resistor(sl, (xl, yt), (xl, yg)); resistor(sl, (xl, yg), (xl, yb)); dot(sl, (xl, yg))
    label(sl, (xl - 18, (yt + yg) / 2), 'R_{G1} = 10 MΩ', color=c['rg'], size=size, align='r', bold=True)
    label(sl, (xl - 18, (yg + yb) / 2), 'R_{G2} = 10 MΩ', color=c['rg'], size=size, align='r', bold=True)
    t = nmos(sl, (xr - 44, yg))
    wire(sl, (xl, yg), (xr - 44, yg))
    (xd, yd), (xs, ys) = t['drain'], t['source']
    resistor(sl, (xr, yt), (xr, yd - 34)); wire(sl, (xr, yd - 34), (xr, yd))
    resistor(sl, (xr, ys + 34), (xr, yb)); wire(sl, (xr, ys), (xr, ys + 34))
    label(sl, (xr + 18, (yt + yd - 34) / 2), 'R_{D} = 6 kΩ', color=c['r'], size=size, bold=True)
    label(sl, (xr + 18, (ys + 34 + yb) / 2), 'R_{S} = 6 kΩ', color=c['r'], size=size, bold=True)
    return {'G': (xl, yg), 'D': (xr, yd - 12), 'S': (xr, ys + 14)}


def cs_feedback(sl, ox, oy, col=None, size=18):
    """Sedra CS amplifier with drain-to-gate feedback bias R_G, coupling capacitors, load R_L. ~560 x 450 pt."""
    c = {'vdd': 'navy', 'rg': 'navy', 'r': 'navy'}; c.update(col or {})
    yt, yd, yg, yb = oy + 30, oy + 160, oy + 270, oy + 420
    xin, xn, xg = ox + 50, ox + 200, ox + 270
    t = nmos(sl, (xg, yg))
    (xd, ydr), (xs, ys) = t['drain'], t['source']
    # supply and drain
    terminal(sl, (xd, yt)); label(sl, (xd + 14, yt), '+V_{DD} = 15 V', color=c['vdd'], size=size, bold=True)
    resistor(sl, (xd, yt + 5.5), (xd, yd)); dot(sl, (xd, yd))
    label(sl, (xd + 16, (yt + yd) / 2 + 4), 'R_{D} = 10 kΩ', color=c['r'], size=size, bold=True)
    wire(sl, (xd, yd), (xd, ydr))
    wire(sl, (xs, ys), (xs, yb)); ground(sl, (xs, yb))
    # feedback resistor from drain to gate
    wire(sl, (xd, yd), (xn, yd))
    resistor(sl, (xn, yd), (xn, yg)); dot(sl, (xn, yg))
    label(sl, (xn - 16, (yd + yg) / 2), 'R_{G} = 10 MΩ', color=c['rg'], size=size, align='r', bold=True)
    wire(sl, (xn, yg), (xg, yg))
    # input: source, coupling capacitor
    capacitor(sl, (xin + 50, yg), (xn, yg))
    wire(sl, (xin, yg), (xin + 50, yg)); dot(sl, (xin, yg))
    acsource(sl, (xin, yg), (xin, yb)); ground(sl, (xin, yb))
    label(sl, (xin - 30, (yg + yb) / 2), 'v_{i}', size=size + 2, align='r', w=60)
    arrow(sl, (xin + 8, yg + 70), (xin + 58, yg + 70), color='text2')
    label(sl, (xin + 64, yg + 70), 'R_{in}', color='text2', size=size, w=80)
    # output: coupling capacitor, load
    xo = xd + 160
    wire(sl, (xd, yd), (xd + 40, yd))
    capacitor(sl, (xd + 40, yd), (xd + 110, yd))
    wire(sl, (xd + 110, yd), (xo, yd)); dot(sl, (xo, yd))
    resistor(sl, (xo, yd), (xo, yb)); ground(sl, (xo, yb))
    label(sl, (xo - 16, (yd + yb) / 2 + 40), 'R_{L} = 10 kΩ', color=c['r'], size=size, bold=True, w=130, align='r')
    wire(sl, (xo, yd), (xo + 44, yd)); terminal(sl, (xo + 50, yd))
    label(sl, (xo + 62, yd), 'v_{o}', size=size + 2, w=50)
    label(sl, ((xd + 40 + xd + 110) / 2, yd - 34), 'C_{C}', color='text2', size=16, align='c', w=60)
    label(sl, ((xin + 50 + xn) / 2, yg + 34), 'C_{C}', color='text2', size=16, align='c', w=60)
    return {'G': (xn, yg), 'D': (xd, yd)}


def cs_amp(sl, ox, oy, size=19):
    """Conceptual common-source amplifier: v_GS = V_GS + v_gs drives the gate; R_D to V_DD; output v_DS. ~300 x 440."""
    xs, yg = ox + 40, oy + 270
    t = nmos(sl, (ox + 150, yg))
    (xd, yd), (xso, ys) = t['drain'], t['source']
    yb, yn, yt = oy + 420, oy + 160, oy + 40
    terminal(sl, (xd, yt)); label(sl, (xd + 14, yt), 'V_{DD}', size=size)
    resistor(sl, (xd, yt + 5.5), (xd, yn)); dot(sl, (xd, yn))
    label(sl, (xd + 16, (yt + yn) / 2), 'R_{D}', size=size)
    arrow(sl, (xd - 18, yn - 60), (xd - 18, yn - 20), color='text2'); label(sl, (xd - 24, yn - 46), 'i_{D}', size=17,
                                                                              align='r', w=50, color='text2')
    wire(sl, (xd, yn), (xd, yd))
    wire(sl, (xd, yn), (xd + 60, yn)); terminal(sl, (xd + 66, yn)); label(sl, (xd + 78, yn), 'v_{DS}', size=size, w=80)
    wire(sl, (xso, ys), (xso, yb)); ground(sl, (xso, yb))
    wire(sl, (xs, yg), (ox + 150, yg))
    vsource(sl, (xs, yg), (xs, yb)); ground(sl, (xs, yb))
    label(sl, (xs + 30, (yg + yb) / 2), 'v_{GS}', size=size, w=80)
    return t


def mirror(sl, ox, oy, size=19):
    """Basic NMOS current mirror: R_SET sets I_REF through diode-connected Q1; Q2 copies it (I_O). ~420 x 470."""
    yc, yt, yb = oy + 300, oy + 50, oy + 440
    q1 = nmos(sl, (ox + 200, yc), flip=True)
    q2 = nmos(sl, (ox + 300, yc))
    x1, x2, xm = q1['drain'][0], q2['drain'][0], ox + 250
    wire(sl, (ox + 200, yc), (ox + 300, yc)); dot(sl, (xm, yc))
    yn = oy + 190
    wire(sl, (x1, q1['drain'][1]), (x1, yn)); dot(sl, (x1, yn))
    wire(sl, (x1, yn), (xm, yn), (xm, yc))
    resistor(sl, (x1, yt + 5.5), (x1, yn)); terminal(sl, (x1, yt)); label(sl, (x1 + 14, yt), 'V_{DD}', size=size)
    label(sl, (x1 - 18, (yt + yn) / 2), 'R_{SET}', size=size, align='r', w=90)
    arrow(sl, (x1 + 20, yn - 70), (x1 + 20, yn - 25), color='g1'); label(sl, (x1 + 28, yn - 48), 'I_{REF}', size=17,
                                                                           color='g1', bold=True, w=90)
    wire(sl, (x2, q2['drain'][1]), (x2, oy + 110)); terminal(sl, (x2, oy + 104))
    arrow(sl, (x2 + 22, oy + 130), (x2 + 22, oy + 180), color='g2'); label(sl, (x2 + 30, oy + 155), 'I_{O}', size=17,
                                                                              color='g2', bold=True, w=60)
    for x, q in ((x1, q1), (x2, q2)):
        wire(sl, (x, q['source'][1]), (x, yb))
    wire(sl, (x1, yb), (x2, yb)); ground(sl, (xm, yb)); dot(sl, (xm, yb))
    label(sl, (x1 - 50, yc), 'Q_{1}', size=size, align='r', w=60)
    label(sl, (x2 + 50, yc), 'Q_{2}', size=size, w=60)


def switch_pair(sl, ox, oy, size=19):
    """MOSFET switch and its equivalent: V_DD-R_D-drain(v_O); gate driven by v_I. ~620 x 380."""
    yt, yn, yb, yg = oy + 30, oy + 140, oy + 330, oy + 235
    t = nmos(sl, (ox + 110, yg))
    xd = t['drain'][0]
    terminal(sl, (xd, yt)); label(sl, (xd + 14, yt), 'V_{DD}', size=size)
    resistor(sl, (xd, yt + 5.5), (xd, yn)); dot(sl, (xd, yn)); label(sl, (xd + 16, (yt + yn) / 2), 'R_{D}', size=size)
    wire(sl, (xd, yn), (xd, t['drain'][1]))
    wire(sl, (xd, yn), (xd + 60, yn)); terminal(sl, (xd + 66, yn)); label(sl, (xd + 78, yn), 'v_{O}', size=size, w=60)
    wire(sl, (xd, t['source'][1]), (xd, yb)); ground(sl, (xd, yb))
    wire(sl, (ox + 30, yg), (ox + 110, yg)); terminal(sl, (ox + 24, yg)); label(sl, (ox + 8, yg), 'v_{I}', size=size,
                                                                              align='r', w=60)
    label(sl, (ox + 330, (yt + yb) / 2), '≡', size=48, align='c', w=60)
    x2 = ox + 470
    terminal(sl, (x2, yt)); label(sl, (x2 + 14, yt), 'V_{DD}', size=size)
    resistor(sl, (x2, yt + 5.5), (x2, yn)); dot(sl, (x2, yn)); label(sl, (x2 + 16, (yt + yn) / 2), 'R_{D}', size=size)
    wire(sl, (x2, yn), (x2 + 60, yn)); terminal(sl, (x2 + 66, yn)); label(sl, (x2 + 78, yn), 'v_{O}', size=size, w=60)
    switch(sl, (x2, yn), (x2, yb))
    ground(sl, (x2, yb))
    label(sl, (x2 - 26, (yn + yb) / 2), 'open: v_{I} < V_{t}\nclosed: v_{I} high', size=16, align='r', w=200,
          color='text2')


def large_signal(sl, ox, oy, size=20):
    """Large-signal model in saturation: open gate (i_G = 0), dependent source D->S. ~640 x 330 (eq at the right)."""
    xg, xb, xdt = ox + 50, ox + 300, ox + 430
    yt, ybot = oy + 50, oy + 290
    terminal(sl, (xg, yt)); label(sl, (xg - 16, yt), 'G', size=size, align='r', w=40, bold=True)
    label(sl, (xg + 14, yt + 4), 'i_{G} = 0', size=17, color='text2', w=110)
    terminal(sl, (xg, ybot)); label(sl, (xg - 16, ybot), 'S', size=size, align='r', w=40, bold=True)
    label(sl, (xg - 6, yt + 40), '+', size=20, w=30)
    label(sl, (xg - 18, (yt + ybot) / 2), 'v_{GS}', size=size, w=80)
    label(sl, (xg - 6, ybot - 40), '−', size=20, w=30)
    wire(sl, (xg + 5.5, ybot), (xb, ybot)); dot(sl, (xb, ybot))
    wire(sl, (xb, yt), (xdt - 5.5, yt)); terminal(sl, (xdt, yt))
    label(sl, (xdt + 14, yt), 'D', size=size, bold=True, w=40)
    dep_isource(sl, (xb, yt), (xb, ybot))
    label(sl, (xb + 40, yt + 30), 'i_{D}', size=17, color='text2', w=60)
    return (xb + 40, (yt + ybot) / 2)


def small_signal(sl, ox, oy, with_ro=False, size=20):
    """Small-signal model: v_gs between G and S, g_m v_gs from D to S (+ r_o). ~470 x 330."""
    xg, xb, xr, xdt = ox + 50, ox + 260, ox + 370, ox + 460
    yt, ybot = oy + 50, oy + 290
    terminal(sl, (xg, yt)); label(sl, (xg - 16, yt), 'G', size=size, align='r', w=40, bold=True)
    terminal(sl, (xg, ybot)); label(sl, (xg - 16, ybot), 'S', size=size, align='r', w=40, bold=True)
    label(sl, (xg - 6, yt + 40), '+', size=20, w=30)
    label(sl, (xg - 18, (yt + ybot) / 2), 'v_{gs}', size=size, w=80)
    label(sl, (xg - 6, ybot - 40), '−', size=20, w=30)
    wire(sl, (xg + 5.5, ybot), (xr if with_ro else xb, ybot)); dot(sl, (xb, ybot))
    wire(sl, (xb, yt), (xdt - 5.5, yt)); terminal(sl, (xdt, yt)); label(sl, (xdt + 14, yt), 'D', size=size, bold=True,
                                                                          w=40)
    dep_isource(sl, (xb, yt), (xb, ybot))
    label(sl, (xb + 34, (yt + ybot) / 2), 'g_{m}v_{gs}', size=size, w=110)
    if with_ro:
        dot(sl, (xr, yt))
        resistor(sl, (xr, yt), (xr, ybot))
        label(sl, (xr + 18, (yt + ybot) / 2 + 40), 'r_{o}', size=size, w=50)


def symbols(sl, ox, oy, size=20):
    """4-terminal n- and p-channel enhancement symbols with labelled terminals. ~560 x 360."""
    for k, (pm, name) in enumerate(((False, 'n-channel'), (True, 'p-channel'))):
        gx = ox + 110 + k * 280
        t = mos4(sl, (gx, oy + 170), pmos=pm)
        (xd, yd), (xs, ys), (xbody, yb) = t['drain'], t['source'], t['body']
        wire(sl, (xd, yd), (xd, oy + 60)); label(sl, (xd + 10, oy + 60), 'D', size=size, bold=True, w=40)
        wire(sl, (xs, ys), (xs, oy + 280)); label(sl, (xs + 10, oy + 280), 'S', size=size, bold=True, w=40)
        wire(sl, (xbody, yb), (xbody + 50, yb)); label(sl, (xbody + 58, yb), 'B', size=size, bold=True, w=40)
        wire(sl, (gx - 70, oy + 170), (gx, oy + 170)); label(sl, (gx - 80, oy + 170), 'G', size=size, bold=True,
                                                             align='r', w=40)
        label(sl, (gx + 20, oy + 340), name, size=size, align='c', w=200, color='text2')


def load_line(sl, x, y, w, h, VDD=10.0, RD=1.25, k=1.0, Vt=1.0, ov=(1, 2, 3, 4)):
    """i_D-v_DS family (k in mA/V^2, RD in kOhm) with the load line and the A (edge of triode) / B (cutoff) points."""
    imax = VDD / RD
    p = Plot(sl, x, y, w, h, xmax=VDD * 1.08, ymax=imax * 1.12, xlabel='v_{DS} (V)', ylabel='i_{D} (mA)')
    line_i = lambda v: (VDD - v) / RD
    for o in ov:                                          # o = v_GS - V_t
        isat = 0.5 * k * o * o
        p.curve(lambda v, o=o: k * (o * v - 0.5 * v * v) if v < o else 0.5 * k * o * o, 0, VDD * 1.05, color='navy',
                w=2.0)
        # label on the plateau, at the first position where the load line stays clear of it
        lab_lo, lab_hi = isat + 0.02 * imax, isat + 0.1 * imax      # label band (data units)
        span = 125 / w * p.xmax                                      # label width in volts
        cands = [o + 0.25 + 0.25 * j for j in range(int((VDD - o) / 0.25))]
        clear = lambda v: line_i(v + span) > lab_hi + 0.03 * imax or line_i(v) < lab_lo - 0.03 * imax
        vx = next((v for v in cands if clear(v) and v + span < VDD * 1.05), o + 0.25)
        p.note((vx, isat), f'v_{{GS}} = V_{{t}} + {o}', size=15, dx=0, dy=-26, w=190, align='l', color='text2')
    p.curve(lambda v: 0.5 * k * v * v, 0, (2 * imax / k) ** 0.5 * 0.98, color='text2', w=1.5, dash=4)
    p.seg((0, imax), (VDD, 0), color='accent', w=3)
    # A: load line meets the triode/saturation boundary  0.5 k v^2 = (VDD - v)/RD
    a = 0.5 * k; b = 1 / RD; c = -VDD / RD
    vA = (-b + (b * b - 4 * a * c) ** 0.5) / (2 * a); iA = (VDD - vA) / RD
    p.point((vA, iA), color='answer'); p.note((vA, iA), 'A', size=20, dx=12, dy=-34)
    p.point((VDD, 0), color='answer'); p.note((VDD, 0), 'B', size=20, dx=-34, dy=-38)
    p.note((VDD * 0.55, (VDD - VDD * 0.55) / RD), 'load line: i_{D} = (V_{DD} − v_{DS})/R_{D}', size=16, dx=16,
           dy=-8, w=340, color='accent')
    p.xtick(VDD, 'V_{DD}'); p.ytick(imax, 'V_{DD}/R_{D}')
    return vA, iA
