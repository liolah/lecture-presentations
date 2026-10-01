"""Minimal native schematic drawing (exploratory; used only for circuits we agree to rebuild).

Draws with deckkit primitives, so parts are editable PowerPoint shapes and can be tagged for step reveals.
Coordinates in points. Sedra-style symbols: zig-zag resistors, simplified enhancement NMOS (arrow on the source,
pointing out of the channel).
"""
from deckkit import line, poly, box, text, OVAL, tag


def resistor_v(sl, x, y0, y1, color='navy', w=2.0, body=64, amp=11, n=6, name='ckt'):
    """Vertical resistor between (x, y0) and (x, y1); zig-zag body centred."""
    ym = (y0 + y1) / 2
    b0, b1 = ym - body / 2, ym + body / 2
    pts = [(x, y0), (x, b0)]
    step = body / n
    for i in range(n):
        pts.append((x + (amp if i % 2 == 0 else -amp), b0 + step * (i + 0.5)))
    pts += [(x, b1), (x, y1)]
    return poly(sl, pts, color=color, w=w, name=name)


def wire(sl, pts, color='navy', w=2.0, name='ckt'):
    return poly(sl, pts, color=color, w=w, name=name)


def dot(sl, x, y, color='navy', r=4.5, name='ckt'):
    return box(sl, x - r, y - r, 2 * r, 2 * r, fill=color, kind=OVAL, name=name)


def terminal(sl, x, y, color='navy', r=5, name='ckt'):
    return box(sl, x - r, y - r, 2 * r, 2 * r, fill='surface', line=color, lw=2.0, kind=OVAL, name=name)


def ground(sl, x, y, color='navy', w=2.0, name='ckt'):
    out = [line(sl, x, y, x, y + 14, color=color, w=w, name=name)]
    for i, half in enumerate((16, 10, 4)):
        yy = y + 14 + i * 6
        out.append(line(sl, x - half, yy, x + half, yy, color=color, w=w, name=name))
    return out


def nmos(sl, xg, yc, color='navy', w=2.0, h=84, gap=10, lead=34, name='ckt'):
    """Simplified NMOS: gate plate at xg (vertical), channel line at xg+gap.
    Returns dict of terminal points: gate (xg, yc), drain (xd, top), source (xd, bottom)."""
    xc = xg + gap
    xd = xc + lead
    top, bot = yc - h / 2, yc + h / 2
    line(sl, xg, yc - h * 0.36, xg, yc + h * 0.36, color=color, w=w, name=name)       # gate plate
    line(sl, xc, top, xc, bot, color=color, w=w + 0.5, name=name)                      # channel
    yd, ys = top + 8, bot - 8
    line(sl, xc, yd, xd, yd, color=color, w=w, name=name)                              # drain lead
    a = line(sl, xc, ys, xc + lead * 0.72, ys, color=color, w=w, arrow=True, name=name)  # source lead, arrow out
    a.Line.EndArrowheadLength = 3; a.Line.EndArrowheadWidth = 3
    line(sl, xc + lead * 0.70, ys, xd, ys, color=color, w=w, name=name)
    return {'gate': (xg, yc), 'drain': (xd, yd), 'source': (xd, ys)}


def dc_example(sl, ox, oy, color='navy', label='text2', size=20, vals=None):
    """Sedra NMOS DC example: V_DD, divider R_G1/R_G2 on the gate, R_D on the drain, R_S on the source.
    Occupies about 330 x 520 pt from (ox, oy). Returns node points for labels."""
    vals = vals or {}
    xl, xr = ox + 60, ox + 250          # left (divider) and right (transistor) rails
    yt, yb = oy + 60, oy + 470          # top and bottom rails
    xm = (xl + xr) / 2
    terminal(sl, xm, oy + 14, color=color)
    wire(sl, [(xm, oy + 19), (xm, yt)], color=color)
    text(sl, xm + 14, oy - 6, 220, 34, vals.get('vdd', '+V_{DD} = 10 V'), size=size, color=color)
    wire(sl, [(xl, yt), (xr, yt)], color=color); dot(sl, xm, yt, color=color)
    wire(sl, [(xl, yb), (xr, yb)], color=color); dot(sl, xm, yb, color=color)
    ground(sl, xm, yb, color=color)
    # divider
    yg = (yt + yb) / 2
    resistor_v(sl, xl, yt, yg, color=color)
    resistor_v(sl, xl, yg, yb, color=color)
    dot(sl, xl, yg, color=color)
    text(sl, ox - 110, (yt + yg) / 2 - 16, 150, 34, vals.get('rg1', 'R_{G1} = 10 MΩ'), size=size, color=color, align='r')
    text(sl, ox - 110, (yg + yb) / 2 - 16, 150, 34, vals.get('rg2', 'R_{G2} = 10 MΩ'), size=size, color=color, align='r')
    # transistor: drain/source leads end on the right rail x
    t = nmos(sl, xr - 44, yg, color=color)
    wire(sl, [(xl, yg), (xr - 44, yg)], color=color)
    xd, yd = t['drain']; xs, ys = t['source']
    resistor_v(sl, xr, yt, yd - 34, color=color)
    wire(sl, [(xr, yd - 34), (xr, yd)], color=color)
    resistor_v(sl, xr, ys + 34, yb, color=color)
    wire(sl, [(xr, ys), (xr, ys + 34)], color=color)
    text(sl, xr + 18, (yt + yd - 34) / 2 - 16, 170, 34, vals.get('rd', 'R_{D} = 6 kΩ'), size=size, color=color)
    text(sl, xr + 18, (ys + 34 + yb) / 2 - 16, 170, 34, vals.get('rs', 'R_{S} = 6 kΩ'), size=size, color=color)
    return {'G': (xl, yg), 'D': (xr, yd - 10), 'S': (xr, ys + 12), 'gate_lead': ((xl + xr - 44) / 2, yg)}
