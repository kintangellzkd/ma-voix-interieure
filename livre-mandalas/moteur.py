"""Moteur de dessin des mandalas (traits vectoriels pour coloriage).

Convention : chaque motif est dessiné dans un repère local où l'axe +y part
du centre vers l'extérieur ; `rep` le répète n fois autour du centre.
Les formes sont remplies avec la couleur du papier, ce qui permet de les
superposer (on dessine de l'extérieur vers l'intérieur, puis les couches
du dessus).
"""
import math

TAU = math.tau


def pol(r, a):
    """Point polaire, a en degrés, 0 = haut, sens horaire."""
    t = math.radians(a)
    return (r * math.sin(t), r * math.cos(t))


def bez(p0, c1, c2, p3, n=18):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        pts.append((u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p3[1]))
    return pts


def arc_pts(r, a0, a1, n=None, cx=0, cy=0):
    """Points d'un arc (angles en degrés, convention pol)."""
    n = n or max(4, int(abs(a1 - a0) / 3) + 2)
    return [(cx + pol(r, a0 + (a1 - a0) * i / n)[0], cy + pol(r, a0 + (a1 - a0) * i / n)[1])
            for i in range(n + 1)]


def mirror(pts):
    """Complète une demi-forme (côté gauche, de bas en haut) par symétrie."""
    return pts + [(-x, y) for (x, y) in reversed(pts[:-1])]


def xform(pts, dx=0, dy=0, ang=0, s=1):
    """Rotation (degrés, sens horaire), échelle puis translation."""
    t = math.radians(-ang)
    ca, sa = math.cos(t), math.sin(t)
    return [(dx + s * (x * ca - y * sa), dy + s * (x * sa + y * ca)) for x, y in pts]


def ellipse_pts(cx, cy, rx, ry, ang=0, n=48):
    pts = [(rx * math.cos(TAU * i / n), ry * math.sin(TAU * i / n)) for i in range(n)]
    return xform(pts, cx, cy, ang)


class Mandala:
    def __init__(self, c, ink=(0, 0, 0), paper=(1, 1, 1), lw=1.25):
        self.c = c
        self.ink = ink
        self.paper = paper
        self.lw = lw
        c.setStrokeColorRGB(*ink)
        c.setFillColorRGB(*paper)
        c.setLineJoin(1)
        c.setLineCap(1)

    # -- primitives ---------------------------------------------------------
    def poly(self, pts, fill=True, close=True, lw=None):
        if len(pts) < 2:
            return
        p = self.c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        if close:
            p.close()
        self.c.setLineWidth(lw or self.lw)
        self.c.drawPath(p, stroke=1, fill=1 if (fill and close) else 0)

    def line(self, a, b, lw=None):
        self.poly([a, b], fill=False, close=False, lw=lw)

    def circle(self, r, cx=0, cy=0, fill=True, lw=None):
        self.c.setLineWidth(lw or self.lw)
        self.c.circle(cx, cy, r, stroke=1, fill=1 if fill else 0)

    def dot(self, x, y, r, lw=None):
        self.circle(r, x, y, True, lw or self.lw * 0.8)

    def rep(self, n, fn, offset=0.0):
        for i in range(n):
            self.c.saveState()
            self.c.rotate(-(offset + i * 360.0 / n))
            fn()
            self.c.restoreState()

    def clip(self, pts):
        p = self.c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        self.c.clipPath(p, stroke=0, fill=0)

    @property
    def fine(self):
        return self.lw * 0.62


# ---------------------------------------------------------------------------
# Formes unitaires (repère local, axe +y vers l'extérieur)
# ---------------------------------------------------------------------------

def petal_shape(r0, r1, hw, style="lotus", base=None):
    """Pétale de r0 à r1, demi-largeur hw. Retourne un polygone."""
    L = r1 - r0
    if style == "lotus":
        bw = hw * 0.55 if base is None else base
        half = [(-bw, r0)] + bez((-bw, r0), (-hw * 1.2, r0 + .42 * L), (-hw * .32, r0 + .8 * L), (0, r1))
    elif style == "round":
        bw = hw * 0.5 if base is None else base
        half = [(-bw, r0)] + bez((-bw, r0), (-hw * 1.32, r0 + .5 * L), (-hw * .95, r1), (0, r1))
    elif style == "pointed":
        half = [(0, r0)] + bez((0, r0), (-hw * 1.33, r0 + .28 * L), (-hw * .85, r0 + .72 * L), (0, r1))
    elif style == "drop":  # goutte : rond vers le centre, pointe vers l'extérieur
        half = [(0, r0)] + bez((0, r0), (-hw * 1.36, r0), (-hw * .3, r1 - .42 * L), (0, r1))
    elif style == "dome":  # bulbe à pointe effilée
        bw = hw * 0.55 if base is None else base
        half = ([(-bw, r0)] + bez((-bw, r0), (-hw * 1.3, r0 + .22 * L), (-hw * 1.15, r0 + .62 * L), (-hw * .42, r0 + .8 * L))
                + bez((-hw * .42, r0 + .8 * L), (-hw * .14, r0 + .88 * L), (-hw * .03, r1 - .07 * L), (0, r1)))
    elif style == "spade":  # pointe fine, ventre arrondi
        bw = hw * 0.35 if base is None else base
        half = ([(-bw, r0)] + bez((-bw, r0), (-hw * 1.4, r0 + .05 * L), (-hw * 1.1, r0 + .55 * L), (-hw * .25, r0 + .78 * L))
                + bez((-hw * .25, r0 + .78 * L), (-hw * .05, r0 + .86 * L), (0, r1 - .05 * L), (0, r1)))
    else:
        raise ValueError(style)
    return mirror(half)


def heart_shape(y0, H, W):
    """Cœur pointe vers le centre (en y0), lobes vers l'extérieur."""
    half = ([(0, y0)] + bez((0, y0), (-.62 * W, y0 + .38 * H), (-.62 * W, y0 + 1.0 * H), (-.28 * W, y0 + H))
            + bez((-.28 * W, y0 + H), (-.08 * W, y0 + H), (0, y0 + .9 * H), (0, y0 + .78 * H)))
    return mirror(half)


def leaf_shape(L, W):
    """Feuille en amande, base à l'origine, pointe en (0, L)."""
    half = [(0, 0)] + bez((0, 0), (-W * 1.25, L * .25), (-W * .9, L * .75), (0, L))
    return mirror(half)


def star_shape(cx, cy, R, n=5, k=0.45, ang=0):
    pts = []
    for i in range(2 * n):
        rr = R if i % 2 == 0 else R * k
        x, y = pol(rr, ang + i * 180.0 / n)
        pts.append((cx + x, cy + y))
    return pts


def flame_shape(r0, r1, hw):
    """Flamme : ventre arrondi, pointe effilée légèrement ondulée."""
    L = r1 - r0
    bw = hw * .5
    half = ([(-bw, r0)] + bez((-bw, r0), (-hw * 1.2, r0 + .25 * L), (-hw * .95, r0 + .5 * L), (-hw * .45, r0 + .7 * L))
            + bez((-hw * .45, r0 + .7 * L), (-hw * .12, r0 + .82 * L), (-hw * .1, r1 - .1 * L), (0, r1)))
    return mirror(half)


# ---------------------------------------------------------------------------
# Anneaux
# ---------------------------------------------------------------------------

def ring_petals(m, r0, r1, n, style="lotus", width=1.0, inner=1, vein=False, offset=0.0,
                dots=False, lw=None):
    rm = (r0 + r1) / 2
    hw = rm * math.sin(math.pi / n) * width
    L = r1 - r0

    def unit():
        m.poly(petal_shape(r0, r1, hw, style), lw=lw)
        for k in range(1, inner + 1):
            f = 1 - 0.3 * k
            if f <= 0.2:
                break
            m.poly(petal_shape(r0, r0 + L * f, hw * (1 - 0.27 * k), style), lw=m.fine)
        if vein:
            m.line((0, r0 + .08 * L), (0, r0 + L * (1 - 0.3 * inner) - .06 * L if inner else r1 - .12 * L), m.fine)
        if dots:
            m.dot(0, r0 + L * (0.86 if style != "drop" else 0.35), max(1.6, hw * .16), m.fine)
    m.rep(n, unit, offset)


def ring_scallops(m, r0, r1, n, inner=0, pointed=False, dots=False, offset=0.0, lw=None):
    h = 180.0 / n
    x0, y0 = pol(r0, -h)

    def unit():
        if pointed:
            half = [(x0, y0)] + bez((x0, y0), (x0 * 1.05, y0 + (r1 - y0) * .62), (x0 * .3, r1 - (r1 - y0) * .1), (0, r1))
            pts = mirror(half)
        else:
            yc = (r1 - .25 * y0) / .75
            pts = [(x0, y0)] + bez((x0, y0), (x0 * 1.02, yc), (-x0 * 1.02, yc), (-x0, y0), 24)
        pts = pts + arc_pts(r0, h, -h)[1:-1]
        m.poly(pts, lw=lw)
        for k in range(1, inner + 1):
            f = 1 - 0.32 * k
            rr = r0 + (r1 - r0) * f
            xx = x0 * (1 - 0.26 * k)
            if pointed:
                half = [(xx, y0)] + bez((xx, y0), (xx * 1.05, y0 + (rr - y0) * .62), (xx * .3, rr - (rr - y0) * .1), (0, rr))
                m.poly(mirror(half), fill=False, close=False, lw=m.fine)
            else:
                yc = (rr - .25 * y0) / .75
                m.poly([(xx, y0)] + bez((xx, y0), (xx * 1.02, yc), (-xx * 1.02, yc), (-xx, y0), 24),
                       fill=False, close=False, lw=m.fine)
        if dots:
            m.dot(0, r0 + (r1 - r0) * (.5 if inner == 0 else (1 - .32 * inner) * .5), max(1.5, (r1 - r0) * .1), m.fine)
    m.rep(n, unit, offset)


def ring_triangles(m, r0, r1, n, inner=1, offset=0.0, dots=False):
    h = 180.0 / n

    def unit():
        a, b = pol(r0, -h), pol(r0, h)
        m.poly([a, (0, r1), b] + arc_pts(r0, h, -h)[1:-1])
        for k in range(1, inner + 1):
            f = 1 - 0.33 * k
            m.poly([(a[0] * f, r0 + 1.0), (0, r0 + (r1 - r0) * f), (b[0] * f, r0 + 1.0)], fill=False, close=False, lw=m.fine)
        if dots:
            m.dot(0, r0 + (r1 - r0) * .25, max(1.4, (r1 - r0) * .07), m.fine)
    m.rep(n, unit, offset)


def ring_beads(m, r, n, f=0.8, inner=False, offset=0.0, lw=None):
    s = r * math.sin(math.pi / n) * f

    def unit():
        m.circle(s, 0, r, lw=lw)
        if inner and s > 4:
            m.circle(s * .45, 0, r, lw=m.fine)
    m.rep(n, unit, offset)


def ring_lattice(m, r0, r1, n, offset=0.0):
    step = 360.0 / n

    def unit():
        for sgn in (1, -1):
            p0, p3 = pol(r0, 0), pol(r1, sgn * step)
            q1, q2 = pol(r0 + (r1 - r0) * .45, sgn * step * .15), pol(r1 - (r1 - r0) * .45, sgn * step * .85)
            m.poly([p0] + bez(p0, q1, q2, p3), fill=False, close=False, lw=m.fine)
    m.rep(n, unit, offset)
    m.circle(r1, fill=False)
    m.circle(r0, fill=False)


def ring_rays(m, r0, r1, n, offset=0.0, lw=None):
    m.rep(n, lambda: m.line((0, r0), (0, r1), lw or m.fine), offset)


def ring_wave(m, r, amp, k, phase=0.0, fill=False, lw=None):
    pts = [pol(r + amp * math.sin(k * t + phase), math.degrees(t))
           for t in [TAU * i / (k * 24) for i in range(k * 24)]]
    m.poly(pts, fill=fill, lw=lw)


def ring_braid(m, r0, r1, k, beads=True):
    rm, amp = (r0 + r1) / 2, (r1 - r0) / 2
    m.circle(r1)
    ring_wave(m, rm, amp * .95, k, 0)
    ring_wave(m, rm, amp * .95, k, math.pi)
    if beads:
        ring_beads(m, rm, k * 2, f=0.18, offset=0)
    m.circle(r0, fill=False)


def ring_hearts(m, r0, r1, n, offset=0.0, inner=True):
    L = r1 - r0
    W = (r0 + L / 2) * math.sin(math.pi / n) * 1.6

    def unit():
        m.poly(heart_shape(r0, L, W))
        if inner:
            m.poly(heart_shape(r0 + L * .2, L * .6, W * .58), lw=m.fine)
    m.rep(n, unit, offset)


def ring_leaves(m, r0, r1, n, width=1.0, offset=0.0, veins=True):
    L = r1 - r0
    W = (r0 + L / 2) * math.sin(math.pi / n) * width

    def unit():
        m.poly(xform(leaf_shape(L, W), 0, r0))
        if veins:
            m.line((0, r0 + 2), (0, r1 - L * .1), m.fine)
            for j in range(1, 4):
                y = r0 + L * (0.2 + 0.18 * j)
                for sg in (1, -1):
                    m.line((0, y - L * .08), (sg * W * .55, y + L * .02), m.fine)
    m.rep(n, unit, offset)


def ring_flames(m, r0, r1, n, offset=0.0, inner=True):
    hw = (r0 + r1) / 2 * math.sin(math.pi / n) * .95
    L = r1 - r0

    def unit():
        m.poly(flame_shape(r0, r1, hw))
        if inner:
            m.poly(flame_shape(r0, r0 + L * .6, hw * .55), lw=m.fine)
    m.rep(n, unit, offset)


def ring_stars(m, r, n, size, points=5, offset=0.0, inner=False):
    def unit():
        m.poly(star_shape(0, r, size, points, 0.45))
        if inner:
            m.circle(size * .22, 0, r, lw=m.fine)
    m.rep(n, unit, offset)


def crescent_pts(cx, cy, R, ang=0, thick=0.42):
    """Croissant de lune ; ang oriente les cornes (0 = cornes vers +y)."""
    d = R * thick
    r2 = R * 0.92
    # intersection des cercles C1 (0,0,R) et C2 (0,d,r2)
    y = (R * R - r2 * r2 + d * d) / (2 * d)
    x = math.sqrt(max(R * R - y * y, 0))
    a1 = math.degrees(math.atan2(x, y))
    outer = [pol(R, a) for a in [a1 + (360 - 2 * a1) * i / 40 for i in range(41)]]
    a2 = math.degrees(math.atan2(-x, y - d))
    a2b = math.degrees(math.atan2(x, y - d))
    inner = [(pol(r2, a)[0], pol(r2, a)[1] + d) for a in
             [a2 + ((a2b % 360) - (a2 % 360)) * i / 40 for i in range(41)]]
    return xform(outer + inner, cx, cy, ang)


def ring_crescents(m, r, n, size, offset=0.0, ang=0):
    def unit():
        m.poly(crescent_pts(0, r, size, ang))
    m.rep(n, unit, offset)


def feather_unit(m, r0, r1, hw):
    L = r1 - r0
    shape = petal_shape(r0 + L * .1, r1, hw, "pointed")
    m.poly(shape)
    m.c.saveState()
    m.clip(shape)
    for j in range(1, 9):
        y = r0 + L * (0.12 + j * 0.095)
        for sg in (1, -1):
            m.line((0, y), (sg * hw * 1.3, y + L * .12), m.fine)
    m.c.restoreState()
    m.poly(shape, fill=False)
    m.line((0, r0), (0, r1 - L * .04), m.fine)
    m.circle(hw * .22, 0, r0 + L * .3, lw=m.fine)


def ring_feathers(m, r0, r1, n, width=1.0, offset=0.0):
    hw = (r0 + r1) / 2 * math.sin(math.pi / n) * width
    m.rep(n, lambda: feather_unit(m, r0, r1, hw), offset)


def butterfly(m, cx, cy, s, ang=0):
    def E(x, y, rx, ry, a):
        return xform(ellipse_pts(x, y, rx, ry, a), cx, cy, ang)
    for sg in (1, -1):
        m.poly(E(sg * .42 * s, -.3 * s, .32 * s, .22 * s, -sg * 35))
        m.poly(E(sg * .48 * s, .22 * s, .5 * s, .32 * s, sg * 30))
        m.poly(E(sg * .5 * s, .26 * s, .22 * s, .13 * s, sg * 30), lw=m.fine)
        m.poly(E(sg * .42 * s, -.32 * s, .12 * s, .08 * s, -sg * 35), lw=m.fine)
        ant = xform([(sg * .02 * s, .45 * s)] + bez((sg * .02 * s, .45 * s), (sg * .05 * s, .7 * s), (sg * .2 * s, .78 * s), (sg * .28 * s, .85 * s), 10), cx, cy, ang)
        m.poly(ant, fill=False, close=False, lw=m.fine)
        ex, ey = xform([(sg * .28 * s, .85 * s)], cx, cy, ang)[0]
        m.dot(ex, ey, max(1.2, .04 * s), m.fine)
    m.poly(E(0, .02 * s, .07 * s, .5 * s, 0))


def bird(m, cx, cy, s, ang=0):
    """Colombe stylisée vue de face, ailes déployées, tête vers +y."""
    pts_wing = []
    for sg in (1, -1):
        w = ([(sg * .06 * s, .1 * s)]
             + bez((sg * .06 * s, .1 * s), (sg * .3 * s, .35 * s), (sg * .6 * s, .55 * s), (sg * .95 * s, .62 * s))
             + bez((sg * .95 * s, .62 * s), (sg * .82 * s, .45 * s), (sg * .78 * s, .38 * s), (sg * .7 * s, .3 * s))
             + bez((sg * .7 * s, .3 * s), (sg * .6 * s, .22 * s), (sg * .55 * s, .2 * s), (sg * .45 * s, .14 * s))
             + bez((sg * .45 * s, .14 * s), (sg * .36 * s, .06 * s), (sg * .3 * s, .04 * s), (sg * .2 * s, -.02 * s))
             + [(sg * .06 * s, -.05 * s)])
        pts_wing.append(w)
        m.poly(xform(w, cx, cy, ang))
        for j, (a, b) in enumerate([((.25, .2), (.62, .5)), ((.22, .08), (.5, .22))]):
            m.line(*xform([(sg * a[0] * s, a[1] * s), (sg * b[0] * s, b[1] * s)], cx, cy, ang), m.fine)
    tail = [(-.1 * s, -.2 * s), (-.22 * s, -.55 * s), (-.08 * s, -.5 * s), (0, -.58 * s), (.08 * s, -.5 * s), (.22 * s, -.55 * s), (.1 * s, -.2 * s)]
    m.poly(xform(tail, cx, cy, ang))
    m.poly(xform(ellipse_pts(0, -.05 * s, .12 * s, .27 * s), cx, cy, ang))
    m.poly(xform(ellipse_pts(0, .26 * s, .085 * s, .09 * s), cx, cy, ang))
    m.poly(xform([(-.03 * s, .34 * s), (0, .42 * s), (.03 * s, .34 * s)], cx, cy, ang), lw=m.fine)


def ring_butterflies(m, r, n, s, offset=0.0):
    m.rep(n, lambda: butterfly(m, 0, r, s), offset)


def ring_birds(m, r, n, s, offset=0.0):
    m.rep(n, lambda: bird(m, 0, r, s), offset)


def ring_olive(m, r, n, s, offset=0.0):
    """Rameaux d'olivier le long d'un cercle."""
    span = 360.0 / n

    def unit():
        stem = arc_pts(r, -span * .42, span * .42, 16)
        m.poly(stem, fill=False, close=False, lw=m.fine * 1.3)
        for j in range(7):
            a = -span * .38 + j * span * .76 / 6
            x, y = pol(r, a)
            side = 1 if j % 2 == 0 else -1
            tilt = a + 90 - side * 42
            m.poly(xform(leaf_shape(s, s * .3), x, y, tilt))
            m.line((x, y), xform([(0, s * .8)], x, y, tilt)[0], m.fine)
        x, y = pol(r + s * .1, span * .45)
        m.circle(s * .18, x, y)
    m.rep(n, unit, offset)


def ring_mountains(m, r0, r1, n, offset=0.0):
    h = 180.0 / n

    def unit():
        a, b = pol(r0, -h * 1.15), pol(r0, h * 1.15)
        top = (0, r1)
        m.poly([a, top, b] + arc_pts(r0, h * 1.15, -h * 1.15)[1:-1])
        L = r1 - r0
        sx = abs(a[0]) * .3
        m.poly([(-sx, r1 - L * .3), (-sx * .45, r1 - L * .22), (0, r1 - L * .32), (sx * .45, r1 - L * .22), (sx, r1 - L * .3), top],
               lw=m.fine)
    m.rep(n, unit, offset)


def ring_drops(m, r0, r1, n, inward=False, offset=0.0, inner=True):
    hw = (r0 + r1) / 2 * math.sin(math.pi / n) * .9

    def unit():
        if inward:
            pts = [(x, r0 + r1 - y) for x, y in petal_shape(r0, r1, hw, "drop")]
        else:
            pts = petal_shape(r0, r1, hw, "drop")
        m.poly(pts)
        if inner:
            L = r1 - r0
            cy = r0 + L * (.28 if not inward else .72)
            m.circle(hw * .4, 0, cy, lw=m.fine)
    m.rep(n, unit, offset)


def ring_spirals(m, r, n, s, offset=0.0):
    def unit():
        pts = []
        for i in range(60):
            t = i / 59 * TAU * 1.6
            rr = s * (1 - i / 70)
            pts.append((rr * math.sin(t), r + rr * math.cos(t)))
        m.poly(pts, fill=False, close=False, lw=m.fine * 1.3)
        m.dot(0, r, s * .12, m.fine)
    m.rep(n, unit, offset)


def ring_swirls(m, r0, r1, n, offset=0.0):
    """Volutes d'air : S entrelacés."""
    step = 360.0 / n

    def unit():
        L = r1 - r0
        p0 = pol(r0, 0)
        p3 = pol(r1, step * .9)
        m.poly([p0] + bez(p0, pol(r0 + L * .9, -step * .2), pol(r1 - L * .9, step * 1.1), p3), fill=False, close=False, lw=m.fine * 1.3)
        cx, cy = pol(r1 - L * .02, step * .9)
        cur = []
        for i in range(40):
            t = i / 39 * TAU * 1.2
            rr = L * .18 * (1 - i / 45)
            cur.append((cx + rr * math.sin(t + math.pi), cy + rr * math.cos(t + math.pi)))
        m.poly(cur, fill=False, close=False, lw=m.fine * 1.3)
    m.rep(n, unit, offset)


def ring_gems(m, r0, r1, n, offset=0.0):
    hw = (r0 + r1) / 2 * math.sin(math.pi / n) * .85

    def unit():
        L = r1 - r0
        mid = r0 + L * .5
        m.poly([(0, r0), (-hw, mid), (0, r1), (hw, mid)])
        m.poly([(0, r0 + L * .2), (-hw * .5, mid), (0, r1 - L * .2), (hw * .5, mid)], lw=m.fine)
        m.line((-hw, mid), (hw, mid), m.fine)
    m.rep(n, unit, offset)


def ring_eyes(m, r, n, s, offset=0.0):
    def unit():
        eye(m, 0, r, s, 90)
    m.rep(n, unit, offset)


def ring_clouds(m, r0, r1, n, offset=0.0):
    h = 180.0 / n

    def unit():
        L = r1 - r0
        x0, y0 = pol(r0, -h)
        pts = [(x0, y0)]
        bumps = [(-.62, .55, .38), (-.18, 1.0, .5), (.38, .7, .42)]
        prev = (x0, y0)
        for bx, by, br in bumps:
            px, py = bx * abs(x0), r0 + by * L
            pts += bez(prev, (prev[0] - abs(x0) * .1, py + br * L * .9), (px - abs(x0) * .2, py + br * L * .6), (px, py), 12)
            prev = (px, py)
        pts += bez(prev, (prev[0] + abs(x0) * .4, prev[1] + L * .3), (-x0 + abs(x0) * .05, y0 + L * .5), (-x0, y0), 12)
        pts += arc_pts(r0, h, -h)[1:-1]
        m.poly(pts)
    m.rep(n, unit, offset)


# ---------------------------------------------------------------------------
# Centres
# ---------------------------------------------------------------------------

def eye(m, cx, cy, s, ang=0):
    """Œil en amande, s = demi-longueur ; ang = 90 pour un œil horizontal."""
    half_top = bez((-s, 0), (-s * .5, s * .62), (s * .5, s * .62), (s, 0), 20)
    half_bot = bez((s, 0), (s * .5, -s * .62), (-s * .5, -s * .62), (-s, 0), 20)
    pts = [(-s, 0)] + half_top + half_bot
    # ang=90 : horizontal ; on travaille ici en horizontal puis on tourne de ang-90
    m.poly(xform(pts, cx, cy, ang - 90))
    ix, iy = cx, cy
    m.circle(s * .36, ix, iy)
    m.circle(s * .16, ix, iy, lw=m.fine)
    m.dot(ix + s * .08, iy + s * .08, s * .05, m.fine)


def flower_of_life(m, R, rings=2, frame=True):
    """Fleur de vie de rayon R (3 rayons de cercle si rings=2)."""
    rho = R / (rings + 1)
    centers = set()
    for q in range(-rings - 1, rings + 2):
        for r_ in range(-rings - 1, rings + 2):
            x = rho * (q + r_ / 2)
            y = rho * (r_ * math.sqrt(3) / 2)
            if math.hypot(x, y) <= rho * rings + 1e-6:
                centers.add((round(x, 4), round(y, 4)))
    m.circle(R)
    m.c.saveState()
    m.clip(arc_pts(R - .5, 0, 360, 120))
    for x, y in centers:
        m.circle(rho, x, y, fill=False, lw=m.fine * 1.3)
    m.c.restoreState()
    if frame:
        m.circle(R, fill=False)


def seed_of_life(m, R):
    rho = R / 2
    m.circle(R)
    m.circle(rho, fill=False, lw=m.fine * 1.3)
    for i in range(6):
        x, y = pol(rho, i * 60)
        m.circle(rho, x, y, fill=False, lw=m.fine * 1.3)


def metatron(m, R):
    rr = R / 3.2
    pts = [(0, 0)] + [pol(rr * 2, i * 60) for i in range(6)] + [pol(rr * 4, i * 60) for i in range(6)]
    scale = (R - rr * .5) / (rr * 4 + rr * .5)
    pts = [(x * scale, y * scale) for x, y in pts]
    rad = rr * .5 * scale
    m.circle(R)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            m.line(pts[i], pts[j], m.fine)
    for x, y in pts:
        m.circle(rad, x, y, fill=False, lw=m.fine * 1.3)
    m.circle(R, fill=False)


def interlaced_yantra(m, R):
    """Yantra de triangles entrelacés (inspiré du Sri Yantra, non canonique)."""
    m.circle(R)
    tris = [(-.55, 1.0), (-.33, .64), (-.12, .4), (.06, .2),          # pointes vers le haut
            (.55, -1.0), (.36, -.66), (.18, -.44), (.0, -.27), (-.1, -.12)]  # vers le bas
    for b, a in tris:
        hw = min(math.sqrt(1 - b * b), abs(a - b) * .62)
        m.poly([(-hw * R, b * R), (0, a * R), (hw * R, b * R)], fill=False)
    m.dot(0, .02 * R, R * .03)


def star_polygon(m, R, n, k, fill=False, lw=None):
    pts = [pol(R, i * k * 360.0 / n) for i in range(n)]
    if math.gcd(n, k) == 1:
        order = [pts[(i * 1) % n] for i in range(n)]
        m.poly(order, fill=fill, lw=lw)
    else:
        g = math.gcd(n, k)
        for s in range(g):
            m.poly([pol(R, (s + i * k) * 360.0 / n) for i in range(n // g)], fill=fill, lw=lw)


def sun_center(m, R, n=12):
    ring_triangles(m, R * .55, R, n, inner=1)
    ring_flames(m, R * .55, R * .92, n, offset=180.0 / n, inner=False)
    m.circle(R * .55)
    m.circle(R * .4, lw=m.fine)
    ring_beads(m, R * .475, n * 2, f=.5)
    m.circle(R * .3)


def lotus_center(m, R, n=8):
    ring_petals(m, R * .35, R, n, "lotus", width=1.25, inner=1, offset=180.0 / n)
    ring_petals(m, R * .3, R * .82, n, "lotus", width=1.1, inner=1)
    m.circle(R * .32)
    ring_beads(m, R * .22, 10, f=.7)
    m.circle(R * .12)


def om(m, cx, cy, size, fonts):
    c = m.c
    c.saveState()
    c.setFont(fonts["om"], size)
    t = c.beginText()
    t.setTextRenderMode(2)
    w = c.stringWidth("ॐ", fonts["om"], size)
    t.setTextOrigin(cx - w / 2, cy - size * .3)
    c.setLineWidth(m.fine)
    t.textOut("ॐ")
    c.drawText(t)
    c.restoreState()


def serpent_coil(m, R, turns=3.2, head=True):
    """Serpent enroulé (spirale en bande avec écailles et tête)."""
    w = R / (turns + 1.2) * .62
    pitch = R / (turns + 1.2)
    a0 = pitch * .35
    th1 = turns * TAU

    def rad(th):
        return a0 + pitch * th / TAU

    def width(th):
        return w * min(1.0, 0.15 + th / (TAU * .8))

    N = 400
    ths = [th1 * i / N for i in range(N + 1)]
    outer = [pol(rad(t) + width(t) / 2, math.degrees(t)) for t in ths]
    inner = [pol(rad(t) - width(t) / 2, math.degrees(t)) for t in reversed(ths)]
    m.poly(outer + inner)
    for i in range(6, N, 7):
        t = ths[i]
        m.line(pol(rad(t) - width(t) / 2, math.degrees(t)), pol(rad(t) + width(t) / 2, math.degrees(t)), m.fine)
    if head:
        t = th1
        hx, hy = pol(rad(t), math.degrees(t))
        # direction tangente
        dx, dy = pol(rad(t + .05), math.degrees(t + .05))
        ang = math.degrees(math.atan2(dx - hx, dy - hy))
        headp = xform(mirror([(0, -w * .2)] + bez((0, -w * .2), (-w * 1.0, w * .2), (-w * .9, w * 1.3), (0, w * 1.6))), hx, hy, ang)
        m.poly(headp)
        for sg in (1, -1):
            ex, ey = xform([(sg * w * .32, w * .95)], hx, hy, ang)[0]
            m.dot(ex, ey, w * .1, m.fine)
        tg = xform([(0, w * 1.6), (0, w * 2.0), (-w * .15, w * 2.25), (0, w * 2.0), (w * .15, w * 2.25)], hx, hy, ang)
        m.poly(tg, fill=False, close=False, lw=m.fine)


def serpent_arms(m, r0, r1, n, twist=110, w=None):
    """n serpents en spirale qui montent du centre (bandes ondulées)."""
    w = w or (r0 + r1) / 2 * TAU / n * .22
    N = 120

    def unit():
        ts = [i / N for i in range(N + 1)]

        def P(t, off):
            r = r0 + (r1 - r0) * t
            a = twist * t + 9 * math.sin(t * TAU * 1.5)
            ww = w * (0.25 + .75 * min(1, t * 4)) * (1 - .25 * t)
            # décalage perpendiculaire approx. en angle
            return pol(r, a + math.degrees(off * ww / 2 / max(r, 1)))
        side1 = [P(t, 1) for t in ts]
        side2 = [P(t, -1) for t in reversed(ts)]
        hx, hy = pol(r1, twist + 9 * math.sin(TAU * 1.5))
        m.poly(side1 + side2)
        for i in range(5, N, 6):
            m.line(P(ts[i], 1), P(ts[i], -1), m.fine)
        ang = twist + 9 * math.sin(TAU * 1.5) + 25
        m.poly(xform(ellipse_pts(0, 0, w * .55, w * .85), hx, hy, ang))
        ex, ey = xform([(0, w * .3)], hx, hy, ang)[0]
        m.dot(ex, ey, w * .1, m.fine)
    m.rep(n, unit)


def sun_moon(m, R):
    """Équilibre solaire et lunaire (Ida et Pingala)."""
    m.circle(R)
    upper = [(x, y + R / 2) for x, y in arc_pts(R / 2, 180, 0, 40)]
    lower = [(x, y - R / 2) for x, y in arc_pts(R / 2, 0, -180, 40)]
    m.poly(upper + lower, fill=False, close=False)
    m.circle(R * .14, 0, R / 2)
    m.circle(R * .14, 0, -R / 2)
    ring_stars(m, R * .72, 1, R * .1, 5, offset=270)
    m.poly(crescent_pts(*pol(R * .72, 90), R * .1, -45))


# --- yantras des chakras ----------------------------------------------------

def yantra(m, which, R, fonts):
    if which == "racine":
        ring_petals(m, R * .78, R, 4, "round", width=1.0, inner=1, offset=45)
        m.circle(R * .8)
        s = R * .8 / math.sqrt(2) * .98
        m.poly([(-s, -s), (-s, s), (s, s), (s, -s)])
        m.poly([(-s * .78, s * .45), (s * .78, s * .45), (0, -s * .9)], lw=m.fine * 1.4)
        m.circle(s * .28, 0, s * .0, lw=m.fine)
    elif which == "sacre":
        ring_petals(m, R * .72, R, 6, "round", width=1.0, inner=1)
        m.circle(R * .74)
        m.poly(crescent_pts(0, -R * .05, R * .48, 0, .5))
        m.circle(R * .14, 0, R * .32, lw=m.fine)
    elif which == "plexus":
        ring_petals(m, R * .72, R, 10, "lotus", width=1.1, inner=1)
        m.circle(R * .74)
        m.circle(R * .66, fill=False, lw=m.fine)
        s = R * .6
        m.poly([pol(s, 0 + 180), pol(s, 120 + 180), pol(s, 240 + 180)])
        m.poly([pol(s * .55, 180), pol(s * .55, 300), pol(s * .55, 60)], lw=m.fine)
        m.circle(s * .14)
    elif which == "coeur":
        ring_petals(m, R * .72, R, 12, "round", width=1.05, inner=1)
        m.circle(R * .74)
        s = R * .7
        m.poly([pol(s, 0), pol(s, 120), pol(s, 240)])
        m.poly([pol(s, 180), pol(s, 300), pol(s, 60)])
        m.poly(heart_shape(-s * .3, s * .58, s * .55), lw=m.fine * 1.4)
    elif which == "gorge":
        ring_petals(m, R * .74, R, 16, "lotus", width=1.15, inner=1)
        m.circle(R * .76)
        s = R * .7
        m.poly([pol(s, 180), pol(s, 300), pol(s, 60)])
        m.circle(s * .36, 0, s * .1)
        m.circle(s * .18, 0, s * .1, lw=m.fine)
    elif which == "troisieme-oeil":
        for sg in (1, -1):
            pts = petal_shape(R * .45, R, R * .42, "round")
            m.poly(xform(pts, 0, 0, sg * 90))
            m.poly(xform(petal_shape(R * .45, R * .82, R * .26, "round"), 0, 0, sg * 90), lw=m.fine)
        m.circle(R * .5)
        s = R * .46
        m.poly([pol(s, 180), pol(s, 300), pol(s, 60)], lw=m.fine * 1.4)
        om(m, 0, -R * .02, R * .38, fonts)
    elif which == "couronne":
        ring_petals(m, R * .55, R, 40, "pointed", width=1.4, inner=0)
        ring_petals(m, R * .5, R * .9, 20, "lotus", width=1.25, inner=1, offset=9)
        ring_petals(m, R * .42, R * .72, 20, "round", width=1.2, inner=1)
        m.circle(R * .44)
        ring_beads(m, R * .36, 16, f=.7)
        m.circle(R * .28)
        star_polygon(m, R * .28, 6, 2)
        m.circle(R * .09)
    else:
        raise ValueError(which)


# ---------------------------------------------------------------------------
# Composeur
# ---------------------------------------------------------------------------

RING_FUNCS = {
    "petals": ring_petals, "scallops": ring_scallops, "triangles": ring_triangles,
    "lattice": ring_lattice, "hearts": ring_hearts, "leaves": ring_leaves,
    "flames": ring_flames, "feathers": ring_feathers, "mountains": ring_mountains,
    "drops": ring_drops, "swirls": ring_swirls, "gems": ring_gems, "clouds": ring_clouds,
}


def compose(m, R, bands, center, fonts=None):
    """bands : liste de (poids, type, options) de l'extérieur vers l'intérieur.

    Types spéciaux : 'gap' (espace), 'circle' (simple cercle),
    'beads', 'braid', 'wave', 'stars', 'crescents', 'butterflies', 'birds',
    'olive', 'spirals', 'eyes', 'rays'.
    center : (poids, fonction(m, r)).
    """
    total = sum(b[0] for b in bands) + center[0]
    r = R
    for w, kind, opt in bands:
        r1 = r
        r0 = r - R * w / total
        opt = dict(opt)
        frame = opt.pop("frame", kind not in ("petals", "scallops", "triangles", "gap", "hearts",
                                              "leaves", "flames", "feathers", "mountains", "clouds", "drops"))
        if frame:
            m.circle(r1)
        n = opt.pop("n", 24)
        if kind == "gap":
            pass
        elif kind == "circle":
            pass
        elif kind == "beads":
            ring_beads(m, (r0 + r1) / 2, n, **opt)
        elif kind == "braid":
            ring_braid(m, r0, r1, n, **opt)
        elif kind == "wave":
            ring_wave(m, (r0 + r1) / 2, (r1 - r0) * .45, n, **opt)
        elif kind == "stars":
            ring_stars(m, (r0 + r1) / 2, n, (r1 - r0) * .5, **opt)
        elif kind == "crescents":
            ring_crescents(m, (r0 + r1) / 2, n, (r1 - r0) * .45, **opt)
        elif kind == "butterflies":
            ring_butterflies(m, (r0 + r1) / 2, n, (r1 - r0) * .55, **opt)
        elif kind == "birds":
            ring_birds(m, (r0 + r1) / 2 - (r1 - r0) * .08, n, (r1 - r0) * .78, **opt)
        elif kind == "olive":
            ring_olive(m, (r0 + r1) / 2, n, (r1 - r0) * .42, **opt)
        elif kind == "spirals":
            ring_spirals(m, (r0 + r1) / 2, n, (r1 - r0) * .42, **opt)
        elif kind == "eyes":
            ring_eyes(m, (r0 + r1) / 2, n, (r1 - r0) * .42, **opt)
        elif kind == "rays":
            ring_rays(m, r0, r1, n, **opt)
        elif kind == "serpents":
            serpent_arms(m, r0, r1, n, **opt)
        else:
            ext = opt.pop("ext", 0)
            RING_FUNCS[kind](m, r0, r1 + R * ext, n, **opt)
        r = r0
    if center[1] is not None:
        center[1](m, r)
    return r
