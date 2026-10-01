"""L3 MOSFETs: full lecture build (DRAFT: the family design is not approved yet; built in both candidate styles).

Usage:  python build.py          (X and Y)        python build.py X
Output: ../draft/ELEC1 L3 MOSFETs draft-<V> (present).pptx  +  (student).pdf     (scratch in .build/electronics/L3/)
Content decisions and their reasons: review.md. Computed answers: check.py. Figures: figures.py.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, 'tools', 'family.py')):
    ROOT = os.path.dirname(ROOT)
FAM = os.path.join(ROOT, 'families', 'electronics')

if len(sys.argv) == 1:
    for v in 'XY':
        subprocess.run([sys.executable, __file__, v], check=True)
    sys.exit(0)

V = sys.argv[1]
os.environ['DECK_TOKENS'] = os.path.join(FAM, 'explore', 'round2', V, 'tokens.json')
sys.path[:0] = [os.path.join(ROOT, 'tools'), HERE, os.path.join(FAM, 'explore', 'round1')]
import family
family.use('electronics')
import kit
from kit import *                           # noqa
import eqn, states
import circuit, check, figures as FIG
import importlib.util

spec = importlib.util.spec_from_file_location('module', os.path.join(os.path.dirname(os.path.dirname(HERE)), 'module.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)

LNO, TOPIC = 3, 'MOSFETs'
kit.setup(f'{M.SHORT}  ·  Lecture {LNO}  ·  {TOPIC}')
OUT = family.scratch('electronics', 'L3', V)
DRAFT = os.path.join(os.path.dirname(HERE), 'draft')
f = check.fmt
KP = r"k_n^{\prime}\frac{W}{L}"            # k'_n (W/L), Sedra's (older-edition) notation


def fig(sl, key, x, y, w, h, align='c'):
    return figure(sl, FIG.path(key), FIG.credit(key), x, y, w, h, align=align)


SECTIONS = [('Structure and operation', 'how a channel forms; the threshold voltage'),
            ('I–V characteristics', 'cutoff, triode and saturation'),
            ('MOSFETs in DC circuits', 'finding the operating point'),
            ('The MOSFET as an amplifier', 'transconductance, small-signal model'),
            ('The MOSFET as a switch', '')]
OUTCOMES = ['Explain how v_{GS} creates a channel and how v_{DS} pinches it off',
            'Pick the right region and use its i_{D} equation',
            'Find the DC operating point of a MOSFET circuit',
            'Find g_{m} and the gain of a simple MOSFET amplifier']
SEC = {i: f'{i} · {t}' for i, (t, _) in enumerate(SECTIONS, 1)}
SAT = rf"i_D = \frac{{1}}{{2}}\,{KP}\,(v_{{GS}}-V_t)^2"
TRI = rf"i_D = {KP}\left[(v_{{GS}}-V_t)\,v_{{DS}}-\frac{{1}}{{2}}v_{{DS}}^2\right]"


def text_col(sl, x, y, w, items, size=None):
    return points(sl, x, y, w, items, size=size or 24)


# ------------------------------------------------------------------ 1 structure and operation
def s_device(pres, lay):
    sl = slide(pres, lay, 'The n-channel enhancement MOSFET', section=SEC[1])
    fig(sl, 'structure', MX, 160, W - 2 * MX, 390)
    text_col(sl, MX, 580, W - 2 * MX, [
        ('@1', 'Four terminals: **source** (S), **gate** (G), **drain** (D) and **body** (B).'),
        ('@2', 'A thin oxide (SiO₂) insulates the gate, so the gate draws **no current**.'),
        ('@3', 'The channel region between the n⁺ source and drain has length L and width W.')], size=23)


def s_no_gate(pres, lay):
    sl = slide(pres, lay, 'With no gate voltage, no current flows', section=SEC[1])
    fig(sl, 'band', MX, 175, 640, 470)
    text_col(sl, 760, 190, W - MX - 760, [
        ('@1', 'Source and drain are n⁺, the body is p-type: two **back-to-back pn junctions** lie between source '
               'and drain.'),
        ('@2', 'Whatever the polarity of v_{DS}, one junction is reverse-biased, so i_{D} ≈ 0.'),
        ('@3', 'The energy barrier (left) keeps the electrons of the source away from the drain.')])


def s_channel(pres, lay):
    sl = slide(pres, lay, 'Creating a channel: the threshold voltage', section=SEC[1])
    fig(sl, 'channel', 700, 175, 668, 545)
    x, w = MX, 580
    y = text_col(sl, x, 190, w, [
        ('@1', 'A positive v_{GS} pushes holes away from the region under the gate and draws electrons in from '
               'the n⁺ source and drain.'),
        ('@2', 'Once enough electrons gather, they form an n-type **inversion layer**: the channel linking source '
               'to drain.')])
    panel(sl, x, y + 10, w, 170, name='def @3')
    label_tag(sl, x + 26, y + 32, 'Definition', name='def @3')
    text(sl, x + 26, y + 76, w - 52, 100, '**Threshold voltage V_{t}**: the value of v_{GS} at which the channel '
         'just forms.', size=24, name='def @3')


def s_taper(pres, lay):
    sl = slide(pres, lay, 'Increasing v_{DS}: the channel tapers and pinches off', section=SEC[1])
    fig(sl, 'taper', 720, 175, 648, 545)
    x, w = MX, 600
    y = text_col(sl, x, 185, w, [
        ('@1', 'Along the channel, the voltage rises from 0 at the source to v_{DS} at the drain.'),
        ('@2', 'The gate-to-channel voltage therefore falls from v_{GS} to v_{GS} − v_{DS}: the channel gets '
               'shallower toward the drain.')], size=23)
    panel(sl, x, y + 6, w, 200, name='def @3')
    label_tag(sl, x + 26, y + 28, 'Pinch-off', name='def @3')
    text(sl, x + 26, y + 72, w - 52, 130, 'When v_{DS} = v_{GS} − V_{t}, the channel depth at the drain end falls '
         'to almost zero. Increasing v_{DS} further barely changes i_{D}: the current **saturates**.', size=22,
         name='def @3')


def s_cmos(pres, lay):
    sl = slide(pres, lay, 'CMOS: NMOS and PMOS on one chip', section=SEC[1])
    fig(sl, 'cmos', MX, 160, W - 2 * MX, 420)
    text_col(sl, MX, 610, W - 2 * MX, [
        ('@1', 'The PMOS transistor is built in an **n-well**, with p⁺ source and drain.'),
        ('@2', 'Thick oxide isolates neighbouring devices. CMOS circuits use both types together.')], size=23)


def s_symbols(pres, lay):
    sl = slide(pres, lay, 'Circuit symbols: n-channel and p-channel', section=SEC[1])
    fig(sl, 'symbols', MX, 175, 640, 470)
    text_col(sl, 760, 190, W - MX - 760, [
        ('@1', 'In these symbols the arrow is on the body: it points **in** for an n-channel device and **out** '
               'for a p-channel device.'),
        ('@2', 'PMOS: holes carry the current and every voltage and current is reversed. It conducts when '
               'v_{GS} < V_{t}, with V_{t} negative.')])


# ------------------------------------------------------------------ 2 I-V characteristics
def s_family(pres, lay):
    sl = slide(pres, lay, 'The i_{D}–v_{DS} family of curves', section=SEC[2])
    fig(sl, 'iv_family', MX, 165, 700, 565, align='l')
    text_col(sl, 840, 185, W - MX - 840, [
        ('@1', 'Each curve is one value of v_{GS} > V_{t}.'),
        ('@2', 'Left of the dashed line (v_{DS} < v_{GS} − V_{t}): **triode**. i_{D} rises with v_{DS}.'),
        ('@3', 'Right of it: **saturation**. i_{D} is set by v_{GS} alone.'),
        ('@4', 'For v_{GS} ≤ V_{t}: **cutoff**, i_{D} = 0.')])


def s_transfer(pres, lay):
    sl = slide(pres, lay, 'In saturation, i_{D} depends only on v_{GS}', section=SEC[2])
    fig(sl, 'transfer', MX, 165, 600, 565, align='l')
    x, w = 740, W - MX - 740
    y = text_col(sl, x, 190, w, [('@1', 'Measured in saturation, the transfer characteristic is a parabola that '
                                        'starts at v_{GS} = V_{t}.')])
    eq(sl, x, y + 10, SAT, size=28, w=w, st='@2')
    text_col(sl, x, y + 120, w, [('@3', 'Doubling (v_{GS} − V_{t}) quadruples i_{D}: the **square law**.')])


def s_regions(pres, lay):
    sl = slide(pres, lay, 'Triode and saturation: one curve, two equations', section=SEC[2])
    fig(sl, 'triode_curve', MX, 175, 690, 480, align='l')
    x, w = 810, W - MX - 810
    y = 185
    for st, name, cond, latex in (('@2', 'Triode', 'v_{DS} < v_{GS} − V_{t}', TRI),
                                  ('@3', 'Saturation', 'v_{DS} ≥ v_{GS} − V_{t}', SAT)):
        _, tw = label_tag(sl, x, y, name, name='lab ' + st)
        text(sl, x + tw + 16, y - 2, w - tw - 16, 32, cond, size=22, color='navy', name='lab ' + st, anchor='m')
        eq(sl, x, y + 46, latex, size=26, w=w, st=st)
        y += 190
    text(sl, x, y, w, 70, 'Both require v_{GS} > V_{t}: without a channel, i_{D} = 0 (cutoff).', size=21,
         color='text2', name='note @4')


def s_resistor(pres, lay):
    sl = slide(pres, lay, 'Small v_{DS}: a voltage-controlled resistor', section=SEC[2])
    fig(sl, 'triode_curve', 760, 175, 608, 420)
    x, w = MX, 640
    y = text_col(sl, x, 185, w, [('@1', 'For v_{DS} ≪ 2(v_{GS} − V_{t}) the v_{DS}² term is negligible:')], size=23)
    eq(sl, x + 26, y, rf"i_D \approx {KP}\,(v_{{GS}}-V_t)\,v_{{DS}}", size=27, w=w, st='@1')
    y = text_col(sl, x, y + 80, w, [('@2', 'The channel behaves as a resistor whose value v_{GS} sets:')], size=23)
    eq(sl, x + 26, y, rf"r_{{DS}} = \left[{KP}\,(v_{{GS}}-V_t)\right]^{{-1}}", size=27, w=w, st='@2')
    text_col(sl, x, y + 96, w, [('@3', 'This is the region used when the MOSFET acts as a closed switch '
                                       '(Section 5).')], size=23)


def s_large_signal(pres, lay):
    sl = slide(pres, lay, 'Large-signal model in saturation', section=SEC[2])
    fig(sl, 'large_signal', MX, 160, W - 2 * MX, 380)
    text_col(sl, MX, 570, 760, [
        ('@1', 'In saturation the MOSFET acts as a **voltage-controlled current source** from drain to source.'),
        ('@2', 'The gate draws no current: i_{G} = 0.')], size=23)
    eq(sl, 880, 580, SAT, size=28, w=W - MX - 880, st='@3')


# ------------------------------------------------------------------ 3 DC circuits
def s_recipe(pres, lay):
    sl = slide(pres, lay, 'DC analysis: assume, solve, check', section=SEC[3])
    cw, gap = 400, 48
    for i, (st, head, body) in enumerate((
            ('@1', 'Assume', 'a region, usually saturation (and v_{GS} > V_{t}).'),
            ('@2', 'Solve', 'with that region’s i_{D} equation and KVL/KCL. Reject roots that give v_{GS} < V_{t}.'),
            ('@3', 'Check', 'the assumption: saturation needs v_{DS} ≥ v_{GS} − V_{t}. If it fails, redo it in '
                            'triode.'))):
        x = MX + i * (cw + gap)
        c = card(sl, x, 200, cw, 300, name='card ' + st)
        badge(sl, x + 30, 232, i + 1, d=44, st=st)
        text(sl, x + 30, 296, cw - 60, 50, head, size=34 if kit.ANG else 30, font=F['heading'], bold=not kit.ANG,
             color='navy', name='head ' + st)
        text(sl, x + 30, 356, cw - 60, 220, body, size=23, color='navy', name='body ' + st)
    text(sl, MX, 540, W - 2 * MX, 40, 'The gate draws no current, so gate-bias resistors form an unloaded divider.',
         size=21, color='text2', name='note @4')


def s_ex_dc(pres, lay):
    r = check.ex_dc_drain_voltage()
    sl = slide(pres, lay, 'Example: find the drain voltage', section=SEC[3])
    text(sl, MX, 140, W - 2 * MX, 34, 'Given V_{t} = 1 V and k′_{n}(W/L) = 1 mA/V². The gate draws no current.',
         size=23, color='text2', name='question')
    card(sl, MX, 196, 520, 540, name='circuit card')
    nodes = circuit.dc_example(sl, MX + 150, 236, color='navy', size=19)
    for (px, py), s, st, col in ((nodes['G'], f"V_{{G}} = {f(r['VG'])} V", '@2', 'accent'),
                                 (nodes['S'], f"V_{{S}} = {f(r['VS'])} V", '@6', 'accent'),
                                 (nodes['D'], f"V_{{D}} = {f(r['VD'])} V", '@6', 'answer')):
        text(sl, px + 16, py - 34, 160, 30, s, size=19, font=LABEL, color=col, bold=True, name='node ' + st)
    x, w = 640, W - MX - 640
    y = steps(sl, x, 200, w, [
        ('@2', 'Gate voltage: the divider is unloaded',
         rf"V_G = V_{{DD}}\,\frac{{R_{{G2}}}}{{R_{{G1}}+R_{{G2}}}} = {f(r['VG'])}\ \mathrm{{V}}", None),
        ('@3', 'Assume saturation, with V_{GS} = V_{G} − I_{D}R_{S}   (I in mA, R in kΩ)',
         r"I_D = \frac{1}{2}(1)\,(5-6I_D-1)^2", None),
        ('@4', 'Solve the quadratic',
         rf"18I_D^2-25I_D+8=0\ \Rightarrow\ I_D={f(r['roots_mA'][1])}\ \text{{or}}\ {f(r['roots_mA'][0])}\ \mathrm{{mA}}",
         None),
        ('@5', f"I_{{D}} = {f(r['roots_mA'][1])} mA would give V_{{GS}} = {f(r['rejected_VGS'])} V < V_{{t}} "
               f"(no channel): reject.", None,
         f"So I_{{D}} = {f(r['ID'] * 1e3)} mA and V_{{GS}} = {f(r['VGS'])} V."),
        ('@6', 'Drain voltage',
         rf"V_D = V_{{DD}} - I_DR_D = 10 - {f(r['ID'] * 1e3)}(6) = {f(r['VD'])}\ \mathrm{{V}}", None),
    ], label_size=20, eq_size=25)
    rw = result(sl, x + 48, y - 4, f"V_{{D}} = {f(r['VD'])} V", name='answer @6')
    text(sl, x + 48 + rw + 24, y - 2, w - rw - 80, 60,
         f"✓ V_{{DS}} = {f(r['VDS'])} V ≥ V_{{GS}} − V_{{t}} = {f(r['VOV'])} V: saturation holds.",
         size=19, color='ok', name='check @6')


def s_mirror(pres, lay):
    sl = slide(pres, lay, 'The current mirror', section=SEC[3])
    fig(sl, 'mirror', 760, 170, 608, 540)
    x, w = MX, 640
    y = text_col(sl, x, 185, w, [
        ('@1', 'Q_{1} is diode-connected (gate tied to drain), so it is in saturation. R_{SET} sets its current '
               'I_{REF}, and with it V_{GS}.'),
        ('@2', 'Q_{2} has the same V_{GS}. If it is also in saturation, its current scales with W/L:')], size=23)
    eq(sl, x + 26, y, r"\frac{I_O}{I_{REF}} = \frac{(W/L)_2}{(W/L)_1}", size=30, w=w, st='@2')
    text_col(sl, x, y + 100, w, [('@3', 'Identical transistors copy the current: I_{O} = I_{REF}.')], size=23)


# ------------------------------------------------------------------ 4 amplifier
def s_load_line(pres, lay):
    sl = slide(pres, lay, 'Amplifier action: the load line', section=SEC[4])
    fig(sl, 'amp_circuit', MX, 170, 290, 470)
    fig(sl, 'load_line', 380, 170, 640, 470)
    x, w = 1050, W - MX - 1050
    eq(sl, x, 180, r"v_{DS} = V_{DD} - R_D\,i_D", size=26, w=w, st='@1')
    text_col(sl, x, 250, w, [
        ('@2', 'Bias the MOSFET in saturation, between A and B.'),
        ('@3', 'A small change in v_{GS} moves the operating point along the line: a **large** change in v_{DS}.')],
        size=21)


def s_gm(pres, lay):
    sl = slide(pres, lay, 'Small-signal operation: the transconductance g_{m}', section=SEC[4])
    y = steps(sl, MX, 175, W - 2 * MX, [
        ('@1', 'The gate voltage is the bias plus a small signal', r"v_{GS} = V_{GS} + v_{gs}", None),
        ('@2', 'Substitute into the saturation equation',
         rf"i_D = \frac{{1}}{{2}}{KP}(V_{{GS}}-V_t)^2 + {KP}(V_{{GS}}-V_t)\,v_{{gs}} + \frac{{1}}{{2}}{KP}\,v_{{gs}}^2",
         None),
        ('@3', 'If v_{gs} ≪ 2(V_{GS} − V_{t}), the last term is negligible: the signal current is linear in v_{gs}',
         rf"i_d = g_m v_{{gs}},\ \ \ \ \ g_m = {KP}\,(V_{{GS}}-V_t)", None),
        ('@4', 'With a drain resistor R_{D}, the voltage gain is', r"A_v = \frac{v_{ds}}{v_{gs}} = -g_m R_D", None),
    ], label_size=21, eq_size=26)


def s_models(pres, lay):
    sl = slide(pres, lay, 'Small-signal equivalent circuits', section=SEC[4])
    fig(sl, 'model_a', MX, 165, 620, 400)
    fig(sl, 'model_b', MX + 676, 165, 620, 400)
    text_col(sl, MX, 600, 620, [('@1', 'The MOSFET as a voltage-controlled current source g_{m}v_{gs}; '
                                        'no current into the gate.')], size=22)
    text_col(sl, MX + 676, 600, 620, [('@2', 'Adding r_{o} = V_{A}/I_{D} models the slight slope of the saturation '
                                             'curves (V_{A}: the Early voltage).')], size=22)


def s_ex_amp(pres, lay):
    a = check.ex_cs_amp_feedback_bias()
    sl = slide(pres, lay, 'Example: gain and input resistance', section=SEC[4])
    text(sl, MX, 138, W - 2 * MX, 60, 'V_{t} = 1.5 V, k′_{n}(W/L) = 0.25 mA/V², V_{A} = 50 V. Coupling capacitors '
         'are short circuits for the signal. Find A_{v} = v_{o}/v_{i} and R_{in}.', size=21, color='text2',
         name='question')
    fig(sl, 'cs_feedback', MX, 215, 520, 420)
    x, w = 640, W - MX - 640
    y = steps(sl, x, 212, w, [
        ('@2', 'DC: no gate current, so V_{GS} = V_{D}  (I in mA)',
         r"V_D = 15 - 10I_D,\ \ \ \ \ I_D = \frac{1}{2}(0.25)\,(V_D-1.5)^2",
         f"I_{{D}} = {f(a['ID'] * 1e3)} mA,  V_{{GS}} = V_{{D}} = {f(a['VD'], 1)} V"),
        ('@3', 'Small-signal parameters',
         rf"g_m = 0.25\,({f(a['VGS'], 1)}-1.5) = {f(a['gm'] * 1e3, 3)}\ \mathrm{{mA/V}},\ \ \ \ \ "
         rf"r_o = \frac{{50}}{{{f(a['ID'] * 1e3)}}} = {f(a['ro'] / 1e3, 0)}\ \mathrm{{k}}\Omega", None),
        ('@4', 'Gain (R_{G} carries negligible signal current)',
         rf"A_v \approx -g_m\,(R_D\,\|\,R_L\,\|\,r_o) = -{f(a['gm'] * 1e3, 3)}\,({f(a['Rp'] / 1e3)}) = {f(a['Av'])}\ "
         rf"\mathrm{{V/V}}", None),
        ('@5', 'Input resistance: R_{G} bridges input and output (Miller effect)',
         rf"R_{{in}} = \frac{{R_G}}{{1-A_v}} = \frac{{10}}{{{f(1 - a['Av'])}}} = {f(a['Rin'] / 1e6)}\ \mathrm{{M}}\Omega",
         None),
    ], label_size=19, eq_size=23)
    rw = result(sl, x + 48, y - 6, f"A_{{v}} ≈ {f(a['Av'], 1)} V/V", size=22, name='answer @5')
    result(sl, x + 48 + rw + 20, y - 6, f"R_{{in}} = {f(a['Rin'] / 1e6)} MΩ", size=22, name='answer @5')


# ------------------------------------------------------------------ 5 switch
def s_switch(pres, lay):
    sl = slide(pres, lay, 'The MOSFET as a switch', section=SEC[5])
    fig(sl, 'switch', MX, 175, 640, 470)
    text_col(sl, 760, 190, W - MX - 760, [
        ('@1', 'v_{GS} < V_{t}: **cutoff**. The switch is **open** and i_{D} = 0.'),
        ('@2', 'v_{GS} high and v_{DS} small: deep **triode**. The switch is **closed**, with a small resistance '
               'r_{DS}.'),
        ('@3', 'Driving the gate between these two states is the basis of digital logic.')])


def s_summary(pres, lay):
    sl = slide(pres, lay, 'Summary: three regions of operation', section=f'Lecture {LNO} · summary')
    y = table(sl, MX, 180, [246, 430, W - 2 * MX - 676], ['Region', 'Condition', 'Drain current'], [
        ('Cutoff', 'v_{GS} ≤ V_{t}', ('eq', r"i_D = 0")),
        ('Triode', 'v_{GS} > V_{t},  v_{DS} < v_{GS} − V_{t}', ('eq', TRI)),
        ('Saturation', 'v_{GS} > V_{t},  v_{DS} ≥ v_{GS} − V_{t}', ('eq', SAT))])
    points(sl, MX, y + 20, W - 2 * MX, [
        ('', 'DC problems: **assume** a region, **solve**, then **check** the assumption.'),
        ('', 'Small signals: g_{m} = k′_{n}(W/L)(V_{GS} − V_{t}); a common-source stage has A_{v} = −g_{m}R_{D}.')],
           size=22, gap=12)


def main():
    pres, lay = new_pres()
    src = os.path.join(OUT, f'L3-{V}-source.pptx')
    try:
        title_slide(pres, lay, M, LNO, 'MOSFETs', 'Metal-oxide-semiconductor\nfield-effect transistors',
                    fig=(FIG.path('structure'), FIG.credit('structure')))
        map_slide(pres, lay, LNO, SECTIONS, OUTCOMES)
        section_slide(pres, lay, 1, SECTIONS[0][0], ['The device and its terminals', 'No gate voltage: no current',
                                                    'The threshold voltage', 'Tapering and pinch-off',
                                                    'CMOS; n- and p-channel symbols'], SECTIONS)
        for s in (s_device, s_no_gate, s_channel, s_taper, s_cmos, s_symbols):
            s(pres, lay)
        section_slide(pres, lay, 2, SECTIONS[1][0], ['The i_{D}–v_{DS} family', 'Saturation: the square law',
                                                    'Triode and saturation equations', 'Resistor and large-signal '
                                                    'models'], SECTIONS)
        for s in (s_family, s_transfer, s_regions, s_resistor, s_large_signal):
            s(pres, lay)
        section_slide(pres, lay, 3, SECTIONS[2][0], ['Assume, solve, check', 'Example: the drain voltage',
                                                    'The current mirror'], SECTIONS)
        for s in (s_recipe, s_ex_dc, s_mirror):
            s(pres, lay)
        section_slide(pres, lay, 4, SECTIONS[3][0], ['The load line', 'Transconductance g_{m}',
                                                    'Small-signal models', 'Example: gain and input resistance'],
                      SECTIONS)
        for s in (s_load_line, s_gm, s_models, s_ex_amp):
            s(pres, lay)
        section_slide(pres, lay, 5, SECTIONS[4][0], ['Cutoff: an open switch', 'Deep triode: a closed switch'],
                      SECTIONS)
        s_switch(pres, lay)
        s_summary(pres, lay)
        closing_slide(pres, lay, 'Lecture 4: Bipolar junction transistors (BJTs)', M.CREDIT,
                      'who prepared the original material for this lecture',
                      ['Sedra & Smith, Microelectronic Circuits (Oxford University Press)',
                       'other diagrams from web sources via the original slides'])
        pres.SaveAs(src)
    finally:
        pres.Close()
    print('equations:', eqn.inject(src, roman_subs=False))
    built = {m: states.build(src, OUT, m) for m in ('teaching', 'solution')}
    os.makedirs(DRAFT, exist_ok=True)
    stem = f'{M.SHORT} L{LNO} {TOPIC} draft-{V}'
    shutil.copyfile(built['teaching'][0], os.path.join(DRAFT, f'{stem} (present).pptx'))
    shutil.copyfile(built['solution'][1], os.path.join(DRAFT, f'{stem} (student).pdf'))
    print('released to', DRAFT)


main()
