"""Native schematic drawing for the electronics family (style X). Parts are drawn BETWEEN two terminal points
(schemdraw-style), so a circuit is a list of coordinates; every part is an editable PowerPoint shape that can be
coloured (e.g. per given, colour key 'g1'..'g4') and state-tagged for step reveals.

Conventions (Sedra & Smith): zig-zag resistors; simplified enhancement NMOS (body tied to source, arrow on the
source pointing OUT); PMOS arrow pointing IN; dependent sources are diamonds. Coordinates in points.
"""
import math
from deckkit import line, poly, box, text, OVAL, rgb, T, F

INK = 'navy'
WW = T['shape'].get('wire_w', 2.0)


def _named(shapes, name):
    for s in shapes:
        if s is not None and name:
            s.Name = name
    return shapes


def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L, L


def _pt(a, u, d, n=0.0):
    """Point at distance d along unit vector u from a, offset n along the normal."""
    return (a[0] + u[0] * d - u[1] * n, a[1] + u[1] * d + u[0] * n)


# ------------------------------------------------------------------ basics
def wire(sl, *pts, color=INK, w=None, name='ckt'):
    if len(pts) == 2:
        return line(sl, pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=color, w=w or WW, name=name)
    return poly(sl, list(pts), color=color, w=w or WW, name=name)


def dot(sl, p, color=INK, r=4.5, name='ckt'):
    return box(sl, p[0] - r, p[1] - r, 2 * r, 2 * r, fill=color, kind=OVAL, name=name)


def terminal(sl, p, color=INK, r=5.5, name='ckt'):
    return box(sl, p[0] - r, p[1] - r, 2 * r, 2 * r, fill='surface', line=color, lw=WW, kind=OVAL, name=name)


def ground(sl, p, color=INK, name='ckt'):
    x, y = p
    out = [line(sl, x, y, x, y + 12, color=color, w=WW, name=name)]
    for i, half in enumerate((15, 9.5, 4)):
        yy = y + 12 + i * 5.5
        out.append(line(sl, x - half, yy, x + half, yy, color=color, w=WW, name=name))
    return out


def label(sl, p, s, color=INK, size=19, align='l', anchor='m', w=220, bold=False, name='ckt label'):
    """Markup label (R_{D} = 10 kΩ). align l: starts at p; r: ends at p; c: centred on p."""
    x = p[0] if align == 'l' else (p[0] - w if align == 'r' else p[0] - w / 2)
    y = p[1] - size * 0.75 if anchor == 'm' else (p[1] - size * 1.5 if anchor == 'b' else p[1])
    return text(sl, x, y, w, size * 1.5, s, size=size, font=F['body'], color=color, align=align, anchor='m',
                bold=bold, name=name)


def arrow(sl, a, b, color=INK, w=1.75, name='ckt'):
    ln = line(sl, a[0], a[1], b[0], b[1], color=color, w=w, arrow=True, name=name)
    ln.Line.EndArrowheadLength = 2; ln.Line.EndArrowheadWidth = 2
    return ln


# ------------------------------------------------------------------ two-terminal parts
def resistor(sl, a, b, color=INK, body=58, amp=10, n=6, name='ckt'):
    u0, u1, L = _unit(a, b)
    u = (u0, u1)
    s = (L - body) / 2
    pts = [a, _pt(a, u, s)]
    step = body / n
    for i in range(n):
        pts.append(_pt(a, u, s + step * (i + 0.5), amp if i % 2 == 0 else -amp))
    pts += [_pt(a, u, s + body), b]
    return poly(sl, pts, color=color, w=WW, name=name)


def capacitor(sl, a, b, color=INK, gap=10, plate=30, name='ckt'):
    u0, u1, L = _unit(a, b)
    u = (u0, u1)
    m1, m2 = (L - gap) / 2, (L + gap) / 2
    out = [wire(sl, a, _pt(a, u, m1), color=color, name=name), wire(sl, _pt(a, u, m2), b, color=color, name=name)]
    for d in (m1, m2):
        p1, p2 = _pt(a, u, d, plate / 2), _pt(a, u, d, -plate / 2)
        out.append(line(sl, p1[0], p1[1], p2[0], p2[1], color=color, w=WW + 1, name=name))
    return out


def _circle_part(sl, a, b, r, color, name):
    u0, u1, L = _unit(a, b)
    u = (u0, u1)
    c = _pt(a, u, L / 2)
    out = [wire(sl, a, _pt(a, u, L / 2 - r), color=color, name=name),
           wire(sl, _pt(a, u, L / 2 + r), b, color=color, name=name),
           box(sl, c[0] - r, c[1] - r, 2 * r, 2 * r, fill='surface', line=color, lw=WW, kind=OVAL, name=name)]
    return out, c, u


def vsource(sl, a, b, color=INK, r=22, name='ckt'):
    """DC source; '+' at the a end."""
    out, c, u = _circle_part(sl, a, b, r, color, name)
    pp, pm = _pt(c, u, -r * 0.5), _pt(c, u, r * 0.5)
    out.append(text(sl, pp[0] - 10, pp[1] - 12, 20, 24, '+', size=18, color=color, align='c', anchor='m', name=name))
    out.append(text(sl, pm[0] - 10, pm[1] - 12, 20, 24, '−', size=18, color=color, align='c', anchor='m', name=name))
    return out


def acsource(sl, a, b, color=INK, r=22, name='ckt'):
    """Signal source: circle with a sine; '+' marked near the a end."""
    out, c, u = _circle_part(sl, a, b, r, color, name)
    pts = [(c[0] - r * 0.6 + i * r * 1.2 / 16, c[1] - r * 0.35 * math.sin(i / 16 * 2 * math.pi)) for i in range(17)]
    out.append(poly(sl, pts, color=color, w=1.75, name=name))
    pp = _pt(c, u, -r - 10, -14)
    out.append(text(sl, pp[0] - 10, pp[1] - 12, 20, 24, '+', size=16, color=color, align='c', anchor='m', name=name))
    return out


def dep_isource(sl, a, b, color=INK, s=26, name='ckt'):
    """Dependent current source (diamond) with the current arrow pointing from a to b."""
    u0, u1, L = _unit(a, b)
    u = (u0, u1)
    c = _pt(a, u, L / 2)
    out = [wire(sl, a, _pt(a, u, L / 2 - s), color=color, name=name),
           wire(sl, _pt(a, u, L / 2 + s), b, color=color, name=name)]
    d = box(sl, c[0] - s * 0.72, c[1] - s * 0.72, s * 1.44, s * 1.44, fill='surface', line=color, lw=WW, name=name)
    d.Rotation = 45
    out.append(d)
    out.append(arrow(sl, _pt(c, u, -s * 0.5), _pt(c, u, s * 0.55), color=color, w=1.75, name=name))
    return out


def switch(sl, a, b, closed=False, color=INK, name='ckt'):
    """Single-pole switch between a and b (lever from a)."""
    u0, u1, L = _unit(a, b)
    u = (u0, u1)
    p1, p2 = _pt(a, u, L * 0.3), _pt(a, u, L * 0.7)
    out = [wire(sl, a, p1, color=color, name=name), wire(sl, p2, b, color=color, name=name),
           dot(sl, p1, color=color, r=4, name=name), dot(sl, p2, color=color, r=4, name=name)]
    tip = p2 if closed else _pt(a, u, L * 0.66, 22)
    out.append(line(sl, p1[0], p1[1], tip[0], tip[1], color=color, w=WW + 0.5, name=name))
    return out


# ------------------------------------------------------------------ transistors
def nmos(sl, gate, color=INK, h=84, gap=10, lead=34, flip=False, pmos=False, name='ckt'):
    """Simplified enhancement MOSFET. `gate` = (x, y) of the gate plate's centre; the gate lead comes from the left
    (or from the right when flip=True). NMOS: arrow on the source pointing out; pmos=True: arrow pointing in and
    drain/source swapped (source on top). Returns terminal points {'gate', 'drain', 'source'} (lead ends)."""
    sgn = -1 if flip else 1
    xg, yc = gate
    xc = xg + sgn * gap
    xd = xc + sgn * lead
    top, bot = yc - h / 2, yc + h / 2
    out = [line(sl, xg, yc - h * 0.36, xg, yc + h * 0.36, color=color, w=WW, name=name),
           line(sl, xc, top, xc, bot, color=color, w=WW + 0.75, name=name)]
    yt, yb = top + 8, bot - 8
    ys, yd = (yt, yb) if pmos else (yb, yt)
    out.append(line(sl, xc, yd, xd, yd, color=color, w=WW, name=name))
    if pmos:                                   # arrow into the channel
        out.append(line(sl, xd, ys, xc + sgn * lead * 0.3, ys, color=color, w=WW, name=name))
        a = arrow(sl, (xc + sgn * lead * 0.32, ys), (xc + sgn * 2, ys), color=color, w=WW, name=name)
    else:                                      # arrow out of the channel
        a = arrow(sl, (xc, ys), (xc + sgn * lead * 0.72, ys), color=color, w=WW, name=name)
        out.append(line(sl, xc + sgn * lead * 0.7, ys, xd, ys, color=color, w=WW, name=name))
    a.Line.EndArrowheadLength = 3; a.Line.EndArrowheadWidth = 3
    out.append(a)
    return {'gate': (xg, yc), 'drain': (xd, yd), 'source': (xd, ys), 'shapes': out}


def mos4(sl, gate, pmos=False, color=INK, h=96, gap=12, lead=40, name='ckt'):
    """4-terminal MOSFET symbol (body terminal with arrow: in for n-channel, out for p-channel). Returns terminals."""
    xg, yc = gate
    xc = xg + gap
    xd = xc + lead
    top, bot = yc - h / 2, yc + h / 2
    out = [line(sl, xg, yc - h * 0.4, xg, yc + h * 0.4, color=color, w=WW, name=name)]
    seg = h / 7
    for k in (0, 3, 6):                        # broken channel = enhancement device
        out.append(line(sl, xc, top + k * seg, xc, top + (k + 1) * seg, color=color, w=WW + 0.75, name=name))
    yd, ys = top + seg / 2, bot - seg / 2
    out += [line(sl, xc, yd, xd, yd, color=color, w=WW, name=name), line(sl, xc, ys, xd, ys, color=color, w=WW, name=name),
            line(sl, xc, yc, xd, yc, color=color, w=WW, name=name)]
    if pmos:
        a = arrow(sl, (xc + 4, yc), (xc + lead * 0.65, yc), color=color, w=WW, name=name)
    else:
        a = arrow(sl, (xc + lead * 0.75, yc), (xc + 4, yc), color=color, w=WW, name=name)
    a.Line.EndArrowheadLength = 3; a.Line.EndArrowheadWidth = 3
    out.append(a)
    return {'gate': (xg, yc), 'drain': (xd, yd), 'source': (xd, ys), 'body': (xd, yc)}
