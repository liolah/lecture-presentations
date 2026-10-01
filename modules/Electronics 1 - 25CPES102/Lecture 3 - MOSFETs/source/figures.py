"""Cleaned reference figures for L3, cut from the original deck (tools/figcrop.py).

Each entry: key -> (original slide, shape ids, credit). Run this file to (re)extract into source/figures/.
Triage and reasons are in digest.md; only K (keep+clean) figures are listed here.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, 'tools', 'family.py')):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))

DECK = os.path.join(ROOT, 'reference', 'electronics_1', '25CPES102_Lecture_3_MOSFETs.pptx')
OUT = os.path.join(HERE, 'figures')
SEDRA = 'Sedra & Smith, Microelectronic Circuits'
WEB = 'web source, via the original lecture slides'

FIGS = {
    'structure':    (2, {5}, SEDRA),                       # NMOS 3-D view + cross-section
    'band':         (3, {3}, WEB),                         # energy bands, source-body-drain, no gate voltage
    'channel':      (4, {7}, SEDRA),                       # induced n-channel, V_GS > V_t
    'taper':        (6, {5}, SEDRA),                       # channel tapers as V_DS increases
    'cmos':         (8, {6}, SEDRA),                       # CMOS cross-section (NMOS + PMOS in n-well)
    'symbols':      (9, {1026}, WEB),                      # n- and p-channel symbols
    'iv_family':    (10, {5}, SEDRA),                      # i_D-v_DS family + test circuit
    'transfer':     (11, {8}, SEDRA),                      # i_D-v_GS in saturation
    'triode_curve': (12, {2050}, SEDRA),                   # single i_D-v_DS curve, triode/saturation annotated
    'large_signal': (15, {2}, SEDRA),                      # large-signal equivalent circuit in saturation
    'mirror':       (17, {3074, 2, 6, 7}, WEB),            # current mirror (pasted masks flattened)
    'amp_circuit':  (18, {5}, SEDRA),                      # CS amplifier, conceptual circuit
    'load_line':    (18, {4105}, WEB),                     # load line on the i_D-v_DS family
    'model_a':      (20, {34}, SEDRA),                     # small-signal model
    'model_b':      (20, {35}, SEDRA),                     # small-signal model with r_o
    'cs_feedback':  (21, {8196}, SEDRA),                   # CS amp with R_G feedback bias (LOW-RES: rebuild candidate)
    'switch':       (22, {6146}, WEB),                     # MOSFET as a switch (LOW-RES: rebuild candidate)
}


def path(key):
    return os.path.join(OUT, key + '.png')


def credit(key):
    return FIGS[key][2]


if __name__ == '__main__':
    import figcrop
    want = sys.argv[1:]                         # optional keys; '--missing' = only figures not yet extracted
    for k, (s, ids, _) in FIGS.items():
        if want == ['--missing'] and os.path.exists(path(k)) or (want and want != ['--missing'] and k not in want):
            continue
        print(k, *figcrop.crop(DECK, s, ids, path(k), scale=3), flush=True)
