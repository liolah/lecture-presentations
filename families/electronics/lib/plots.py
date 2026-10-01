"""Native plots (axes + curves computed from device equations) for the electronics family.

A Plot maps data coordinates to slide points; curves are freeforms, so they are crisp, recolourable and taggable.
"""
from deckkit import line, poly, text, box, OVAL, F

INK = 'navy'


class Plot:
    def __init__(self, sl, x, y, w, h, xmax, ymax, xlabel='', ylabel='', color=INK, name='plot'):
        self.sl, self.x, self.y, self.w, self.h = sl, x, y, w, h
        self.xmax, self.ymax, self.name = xmax, ymax, name
        ox, oy = self.p(0, 0)
        a1 = line(sl, ox, oy, x + w + 14, oy, color=color, w=1.75, arrow=True, name=name)
        a2 = line(sl, ox, oy, ox, y - 14, color=color, w=1.75, arrow=True, name=name)
        for a in (a1, a2):
            a.Line.EndArrowheadLength = 2; a.Line.EndArrowheadWidth = 2
        if xlabel:      # right of the axis arrow, so it never meets tick labels under the axis
            text(sl, x + w + 22, oy - 15, 110, 30, xlabel, size=20, font=F['body'], color=color, name=name)
        if ylabel:
            text(sl, ox - 6, y - 44, 160, 30, ylabel, size=20, font=F['body'], color=color, name=name)

    def p(self, vx, vy):
        return (self.x + vx / self.xmax * self.w, self.y + self.h - vy / self.ymax * self.h)

    def curve(self, f, x0, x1, n=60, color=INK, w=2.5, dash=None, name=None):
        pts = [self.p(x0 + (x1 - x0) * i / n, f(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]
        s = poly(self.sl, pts, color=color, w=w, name=name or self.name)
        if dash:
            s.Line.DashStyle = dash
        return s

    def seg(self, a, b, color=INK, w=2.5, dash=None, name=None):
        pa, pb = self.p(*a), self.p(*b)
        return line(self.sl, pa[0], pa[1], pb[0], pb[1], color=color, w=w, dash=dash, name=name or self.name)

    def point(self, v, color=INK, r=7, name=None):
        px, py = self.p(*v)
        return box(self.sl, px - r, py - r, 2 * r, 2 * r, fill=color, kind=OVAL, name=name or self.name)

    def note(self, v, s, color=INK, size=18, dx=10, dy=-30, w=260, align='l', name=None):
        px, py = self.p(*v)
        return text(self.sl, px + dx if align == 'l' else px + dx - w, py + dy, w, 28, s, size=size, font=F['body'],
                    color=color, align=align, name=name or self.name)

    def xtick(self, v, s, color='text2', size=17):
        px, py = self.p(v, 0)
        line(self.sl, px, py, px, py + 6, color=color, w=1.25, name=self.name)
        text(self.sl, px - 50, py + 8, 100, 26, s, size=size, font=F['body'], color=color, align='c', name=self.name)

    def ytick(self, v, s, color='text2', size=17):
        px, py = self.p(0, v)
        line(self.sl, px - 6, py, px, py, color=color, w=1.25, name=self.name)
        text(self.sl, px - 110, py - 13, 100, 26, s, size=size, font=F['body'], color=color, align='r', name=self.name)
