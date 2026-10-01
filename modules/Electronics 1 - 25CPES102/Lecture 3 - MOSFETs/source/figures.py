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

FIGS = {
    'structure':    (2, {5}, SEDRA),                       # NMOS 3-D view + cross-section
    'channel':      (4, {7}, SEDRA),                       # induced n-channel, V_GS > V_t
    'taper':        (6, {5}, SEDRA),                       # channel tapers as V_DS increases
    'iv_family':    (10, {5}, SEDRA),                      # i_D-v_DS family + test circuit
    'triode_curve': (12, {2050}, SEDRA),                   # single i_D-v_DS curve, triode/saturation annotated
    'dc_example':   (16, {2050, 2051, 2, 6, 7, 8}, 'circuit adapted from web source; labels by Dr. S. Osama'),
}


def path(key):
    return os.path.join(OUT, key + '.png')


def credit(key):
    return FIGS[key][2]


if __name__ == '__main__':
    import figcrop
    for k, (s, ids, _) in FIGS.items():
        print(k, *figcrop.crop(DECK, s, ids, path(k), scale=3))
