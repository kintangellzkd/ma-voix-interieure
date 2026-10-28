"""Les 44 mandalas du livre : composition de chaque planche."""
from moteur import (compose, sun_center, lotus_center, yantra, flower_of_life, seed_of_life, metatron,
                    interlaced_yantra, star_polygon, serpent_coil, sun_moon, eye, om, ring_petals,
                    ring_beads, ring_hearts, ring_stars, ring_wave, ring_crescents, ring_butterflies,
                    ring_birds, ring_flames, ring_drops, ring_gems, ring_spirals, ring_triangles,
                    ring_scallops, ring_leaves, butterfly, bird, crescent_pts, heart_shape, pol, xform)


def B(w, kind, **opt):
    return (w, kind, opt)


# --- centres réutilisables ---------------------------------------------------

def c_sun(n=12):
    return lambda m, r: sun_center(m, r, n)


def c_lotus(n=8):
    return lambda m, r: lotus_center(m, r, n)


def c_yantra(which, fonts):
    def f(m, r):
        m.circle(r)
        yantra(m, which, r * .96, fonts)
    return f


def c_flower(m, r):
    flower_of_life(m, r, 2)


def c_seed(m, r):
    seed_of_life(m, r)
    m.circle(r * .5 * .25)


def c_star(n, k, inner=None):
    def f(m, r):
        m.circle(r)
        star_polygon(m, r * .95, n, k)
        m.circle(r * .38)
        if inner:
            inner(m, r * .38)
    return f


def c_heart(m, r):
    m.circle(r)
    ring_beads(m, r * .86, 20, f=.55)
    m.circle(r * .74)
    m.poly(heart_shape(-r * .55, r * 1.0, r * .95))
    m.poly(heart_shape(-r * .38, r * .68, r * .62), lw=m.fine)
    m.poly(heart_shape(-r * .22, r * .38, r * .34), lw=m.fine)


def c_eye(m, r):
    m.circle(r)
    ring_petals(m, r * .7, r * .98, 12, "pointed", width=1.1, inner=0)
    m.circle(r * .72)
    eye(m, 0, 0, r * .62, 90)


def c_serpent(m, r):
    m.circle(r)
    serpent_coil(m, r * .9, 3.0)


def c_sunmoon(m, r):
    sun_moon(m, r)


def c_butterfly(m, r):
    m.circle(r)
    butterfly(m, 0, -r * .05, r * .82)


def c_dove(m, r):
    m.circle(r)
    bird(m, 0, -r * .02, r * .9)


def c_crescent(m, r):
    m.circle(r)
    ring_stars(m, r * .78, 8, r * .1, 4, offset=22.5)
    m.poly(crescent_pts(0, 0, r * .55, -40, .45))
    m.circle(r * .07, *pol(r * .2, 120))


def c_om(fonts):
    def f(m, r):
        m.circle(r)
        ring_beads(m, r * .88, 24, f=.55)
        m.circle(r * .76)
        om(m, 0, -r * .05, r * 1.0, fonts)
    return f


def c_drop(m, r):
    m.circle(r)
    ring_drops(m, r * .3, r * .95, 6, inner=True)
    m.circle(r * .32)
    m.circle(r * .15, lw=m.fine)


def c_flame(m, r):
    m.circle(r)
    ring_flames(m, r * .35, r * .95, 8, inner=True)
    ring_flames(m, r * .3, r * .7, 8, offset=22.5, inner=False)
    m.circle(r * .32)
    m.circle(r * .16, lw=m.fine)


def c_square(m, r):
    m.circle(r)
    s = r * .68
    m.poly([(-s, -s), (-s, s), (s, s), (s, -s)])
    m.poly([pol(r * .96, a) for a in (0, 90, 180, 270)])
    m.poly([(-s * .62, -s * .62), (-s * .62, s * .62), (s * .62, s * .62), (s * .62, -s * .62)], lw=m.fine)
    m.circle(s * .42)
    ring_petals(m, s * .12, s * .4, 8, "round", width=1.1, inner=0)
    m.circle(s * .12)


def c_mountain(m, r):
    m.circle(r)
    ring_triangles(m, r * .4, r * .98, 6, inner=2)
    ring_triangles(m, r * .4, r * .78, 6, inner=1, offset=30)
    m.circle(r * .42)
    sun_center(m, r * .36, 8)


def c_air(m, r):
    m.circle(r)
    ring_spirals(m, r * .55, 6, r * .28)
    m.circle(r * .26)
    m.circle(r * .12, lw=m.fine)


def c_ether(m, r):
    m.circle(r)
    star_polygon(m, r * .96, 8, 3)
    m.circle(r * .4)
    star_polygon(m, r * .4, 5, 2)
    m.circle(r * .12)


def c_gem(m, r):
    m.circle(r)
    ring_gems(m, r * .25, r * .95, 8)
    m.circle(r * .27)
    star_polygon(m, r * .27, 8, 3, lw=m.fine)


def c_waves(m, r):
    m.circle(r)
    for i, k in enumerate((14, 11, 8)):
        ring_wave(m, r * (.82 - .2 * i), r * .07, k, fill=False)
    m.circle(r * .26)
    m.circle(r * .12, lw=m.fine)


def c_sevens(fonts):
    """Les sept chakras en médaillons."""
    order = ["racine", "sacre", "plexus", "coeur", "gorge", "troisieme-oeil", "couronne"]

    def f(m, r):
        m.circle(r)
        star_polygon(m, r * .98, 7, 3)
        m.circle(r * .36)
        ring_petals(m, r * .1, r * .34, 7, "lotus", width=1.2, inner=0)
        m.circle(r * .1)
    return f, order


def c_frequencies(m, r):
    m.circle(r)
    for i, k in enumerate((18, 13, 9)):
        ring_wave(m, r * (.85 - .2 * i), r * .06, k, 0)
        ring_wave(m, r * (.85 - .2 * i), r * .06, k, 3.14159)
    m.circle(r * .25)
    star_polygon(m, r * .24, 9, 4, lw=m.fine)


def c_yantra_interlaced(m, r):
    m.circle(r)
    ring_petals(m, r * .78, r * .99, 16, "lotus", width=1.15, inner=0)
    m.circle(r * .8)
    interlaced_yantra(m, r * .78)


def c_metatron(m, r):
    metatron(m, r)


# --- planches ------------------------------------------------------------------

def designs(fonts):
    sevens, sev_order = c_sevens(fonts)

    def sevens_full(m, R):
        r_end = compose(m, R, [
            B(2.0, "petals", n=28, style="lotus", width=1.2, inner=1),
            B(.7, "beads", n=56, f=.75),
            B(.5, "circle"),
        ], (7, None))
        # médaillons des chakras
        m.circle(r_end)
        ring_scallops(m, r_end * .72, r_end, 21, inner=1)
        m.circle(r_end * .72)
        mr = r_end * .5
        for i, w in enumerate(sev_order):
            cx, cy = pol(mr, i * 360 / 7)
            m.c.saveState()
            m.c.translate(cx, cy)
            m.circle(r_end * .2)
            yantra(m, w, r_end * .18, fonts)
            m.c.restoreState()
        m.c.saveState()
        m.circle(r_end * .27)
        m.c.restoreState()
        m.c.saveState()
        sevens(m, r_end * .27)
        m.c.restoreState()

    def finale(m, R):
        compose(m, R, [
            B(2.2, "petals", n=16, style="lotus", width=1.25, inner=2),
            B(1.6, "petals", n=16, style="lotus", width=1.25, inner=1, offset=11.25, frame=False),
            B(.6, "beads", n=48, f=.7),
            B(1.0, "hearts", n=24),
            B(.4, "circle"),
            B(1.2, "scallops", n=32, inner=1, pointed=True),
            B(.6, "braid", n=16),
        ], (3.2, c_om(fonts)))

    D = {}
    # I. L'aube
    D["aube-force"] = lambda m, R: compose(m, R, [
        B(2.0, "petals", n=24, style="lotus", width=1.2, inner=1, dots=True),
        B(1.2, "scallops", n=24, inner=1, offset=7.5),
        B(.55, "beads", n=48, f=.7),
        B(1.6, "triangles", n=24, inner=1),
        B(.3, "circle"),
    ], (3.6, c_sun(12)))
    D["aube-rayon"] = lambda m, R: compose(m, R, [
        B(2.6, "triangles", n=32, inner=2),
        B(1.0, "clouds", n=16, frame=True),
        B(.6, "beads", n=40, f=.6, inner=False),
        B(1.5, "flames", n=16),
        B(.4, "circle"),
    ], (3.4, c_sun(16)))
    D["aube-souffle"] = lambda m, R: compose(m, R, [
        B(2.2, "petals", n=20, style="round", width=1.15, inner=2),
        B(.9, "wave", n=20, frame=True),
        B(1.4, "leaves", n=20, width=1.05),
        B(.5, "beads", n=30, f=.6),
        B(1.4, "petals", n=12, style="dome", width=1.1, inner=1),
    ], (2.8, c_sun(10)))
    D["aube-horizon"] = lambda m, R: compose(m, R, [
        B(1.6, "scallops", n=18, inner=2, pointed=True),
        B(1.6, "mountains", n=12, frame=True),
        B(.5, "circle"),
        B(1.0, "clouds", n=12),
        B(.5, "beads", n=36, f=.6),
    ], (3.6, c_sun(14)))

    # II. Chakras
    D["chakra-racine"] = lambda m, R: compose(m, R, [
        B(1.8, "petals", n=16, style="round", width=1.15, inner=2),
        B(1.0, "triangles", n=32, inner=0, frame=True),
        B(.5, "beads", n=32, f=.7),
        B(1.2, "scallops", n=16, inner=1, dots=True),
        B(.5, "lattice", n=16),
    ], (4.2, c_yantra("racine", fonts)))
    D["chakra-sacre"] = lambda m, R: compose(m, R, [
        B(2.0, "petals", n=18, style="lotus", width=1.25, inner=2),
        B(.8, "wave", n=18),
        B(1.2, "drops", n=18, frame=True),
        B(.5, "beads", n=36, f=.7),
        B(.6, "crescents", n=12, ang=0),
    ], (4.2, c_yantra("sacre", fonts)))
    D["chakra-plexus"] = lambda m, R: compose(m, R, [
        B(2.0, "triangles", n=30, inner=2),
        B(1.3, "petals", n=20, style="lotus", width=1.2, inner=1, frame=True),
        B(.5, "beads", n=40, f=.7),
        B(1.1, "flames", n=20),
        B(.3, "circle"),
    ], (4.2, c_yantra("plexus", fonts)))
    D["chakra-coeur"] = lambda m, R: compose(m, R, [
        B(2.0, "petals", n=24, style="round", width=1.15, inner=2),
        B(1.1, "hearts", n=24, frame=True),
        B(.4, "circle"),
        B(1.0, "leaves", n=24, width=1.0),
        B(.5, "beads", n=36, f=.7),
    ], (4.2, c_yantra("coeur", fonts)))
    D["chakra-gorge"] = lambda m, R: compose(m, R, [
        B(2.0, "petals", n=32, style="lotus", width=1.25, inner=1),
        B(.9, "braid", n=16),
        B(1.2, "scallops", n=32, inner=1, pointed=True),
        B(.5, "beads", n=48, f=.7),
        B(.6, "wave", n=24),
    ], (4.2, c_yantra("gorge", fonts)))
    D["chakra-troisieme-oeil"] = lambda m, R: compose(m, R, [
        B(1.8, "petals", n=18, style="spade", width=1.2, inner=1),
        B(.7, "stars", n=18, points=5, frame=True),
        B(.4, "circle"),
        B(1.2, "petals", n=18, style="pointed", width=1.2, inner=1),
        B(.6, "eyes", n=6),
        B(.3, "circle"),
    ], (4.0, c_yantra("troisieme-oeil", fonts)))
    D["chakra-couronne"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=48, style="pointed", width=1.3, inner=0),
        B(1.6, "petals", n=36, style="lotus", width=1.25, inner=1, frame=False),
        B(1.3, "petals", n=24, style="round", width=1.2, inner=1),
        B(.5, "beads", n=36, f=.7, frame=True),
    ], (4.4, c_yantra("couronne", fonts)))
    D["chakra-alignement"] = sevens_full

    # III. Kundalini
    D["kundalini-serpent"] = lambda m, R: compose(m, R, [
        B(1.8, "petals", n=21, style="lotus", width=1.2, inner=2),
        B(.9, "braid", n=14),
        B(1.2, "scallops", n=21, inner=1),
        B(.4, "beads", n=42, f=.7),
    ], (5.0, c_serpent))
    D["kundalini-shakti"] = lambda m, R: compose(m, R, [
        B(1.6, "flames", n=24),
        B(.5, "beads", n=48, f=.7, frame=True),
        B(.5, "circle"),
    ], (6.0, lambda m, r: (m.circle(r), __import__("moteur").serpent_arms(m, r * .2, r * .92, 7, twist=140),
                           m.circle(r * .22), c_lotus(7)(m, r * .2))))
    D["kundalini-ida-pingala"] = lambda m, R: compose(m, R, [
        B(1.8, "petals", n=16, style="dome", width=1.15, inner=1),
        B(1.0, "braid", n=12),
        B(.5, "crescents", n=12, ang=0),
        B(.5, "stars", n=12, offset=15),
        B(1.0, "scallops", n=24, inner=1),
    ], (3.6, c_sunmoon))
    D["kundalini-flamme"] = lambda m, R: compose(m, R, [
        B(2.2, "flames", n=14),
        B(1.6, "flames", n=14, offset=180 / 14, frame=True),
        B(.5, "beads", n=28, f=.75),
        B(1.0, "triangles", n=28, inner=1),
        B(.6, "circle"),
    ], (3.0, c_flame))

    # IV. La paix
    D["paix-colombe"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=24, style="round", width=1.1, inner=1),
        B(1.6, "olive", n=8, frame=True),
        B(.4, "circle"),
        B(1.2, "scallops", n=16, inner=1),
    ], (4.0, c_dove))
    D["paix-olivier"] = lambda m, R: compose(m, R, [
        B(2.0, "leaves", n=28, width=1.1),
        B(1.6, "olive", n=6, frame=True),
        B(.5, "beads", n=36, f=.7),
        B(1.2, "leaves", n=16, width=1.05),
        B(.3, "circle"),
    ], (2.6, c_lotus(8)))
    D["paix-lotus"] = lambda m, R: compose(m, R, [
        B(1.0, "wave", n=24, frame=False),
        B(.6, "wave", n=20, frame=False),
        B(.2, "circle", frame=False),
        B(2.6, "petals", n=12, style="lotus", width=1.3, inner=2, frame=True),
        B(1.8, "petals", n=12, style="lotus", width=1.3, inner=1, offset=15),
    ], (2.6, c_lotus(8)))
    D["paix-lac"] = lambda m, R: compose(m, R, [
        B(1.6, "drops", n=20, inward=False),
        B(.9, "braid", n=10),
        B(1.0, "petals", n=20, style="round", width=1.1, inner=1),
        B(.4, "circle"),
    ], (4.6, c_waves))
    D["paix-shanti"] = lambda m, R: compose(m, R, [
        B(1.8, "petals", n=12, style="dome", width=1.15, inner=2),
        B(1.8, "birds", n=8, frame=True),
        B(.5, "circle"),
        B(1.1, "petals", n=24, style="lotus", width=1.2, inner=1),
        B(.5, "beads", n=30, f=.65),
    ], (3.0, c_seed))

    # V. Relaxation et nuit
    D["relax-vagues"] = lambda m, R: compose(m, R, [
        B(1.6, "scallops", n=20, inner=2),
        B(.8, "wave", n=16, frame=True),
        B(.8, "wave", n=12),
        B(1.0, "drops", n=16),
        B(.4, "circle"),
    ], (4.0, c_lotus(10)))
    D["relax-lune"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=16, style="round", width=1.1, inner=1),
        B(1.1, "crescents", n=12, ang=0, frame=True),
        B(.6, "stars", n=24),
        B(1.0, "scallops", n=24, inner=1),
    ], (4.4, c_crescent))
    D["relax-etoiles"] = lambda m, R: compose(m, R, [
        B(1.8, "triangles", n=16, inner=2, dots=True),
        B(1.0, "stars", n=16, frame=True, inner=True),
        B(.5, "beads", n=32, f=.6),
        B(.8, "stars", n=12, offset=15),
        B(.3, "circle"),
    ], (3.6, c_star(8, 3)))

    # VI. Le guide intérieur
    D["guide-oeil"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=20, style="spade", width=1.2, inner=1),
        B(.8, "lattice", n=20),
        B(1.2, "petals", n=20, style="lotus", width=1.2, inner=1),
        B(.5, "beads", n=40, f=.7),
    ], (4.6, c_eye))
    D["guide-etoile"] = lambda m, R: compose(m, R, [
        B(2.0, "triangles", n=24, inner=2),
        B(.6, "stars", n=24, frame=True),
        B(1.2, "petals", n=12, style="pointed", width=1.2, inner=1),
        B(.5, "beads", n=36, f=.65),
    ], (3.6, c_star(12, 5)))
    D["guide-silence"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=18, style="lotus", width=1.25, inner=2),
        B(1.4, "petals", n=18, style="lotus", width=1.25, inner=1, offset=10, frame=False),
        B(.5, "beads", n=36, f=.7),
        B(1.0, "scallops", n=18, inner=1, pointed=True),
    ], (4.0, c_om(fonts)))

    # VII. Loi d'attraction
    D["attraction-recu"] = lambda m, R: compose(m, R, [
        B(1.8, "petals", n=24, style="round", width=1.1, inner=2),
        B(1.0, "gems", n=24, frame=True),
        B(.4, "circle"),
        B(1.2, "petals", n=12, style="dome", width=1.15, inner=1),
        B(.4, "beads", n=30, f=.6),
    ], (3.4, c_gem))
    D["attraction-gratitude"] = lambda m, R: compose(m, R, [
        B(1.6, "hearts", n=20),
        B(.5, "beads", n=40, f=.7, frame=True),
        B(1.2, "petals", n=20, style="round", width=1.1, inner=1),
        B(.9, "hearts", n=14),
        B(.3, "circle"),
    ], (3.6, c_heart))
    D["attraction-abondance"] = lambda m, R: compose(m, R, [
        B(2.0, "petals", n=16, style="lotus", width=1.25, inner=2),
        B(1.6, "petals", n=16, style="lotus", width=1.25, inner=1, offset=11.25, frame=False),
        B(.9, "drops", n=32, frame=True),
        B(.5, "beads", n=32, f=.7),
    ], (3.6, c_lotus(12)))

    # VIII. Libération
    D["liberation-plumes"] = lambda m, R: compose(m, R, [
        B(2.6, "feathers", n=16, width=1.15),
        B(.5, "beads", n=32, f=.7, frame=True),
        B(1.4, "feathers", n=12, width=1.15),
        B(.3, "circle"),
    ], (3.0, c_lotus(8)))
    D["liberation-papillon"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=20, style="round", width=1.1, inner=1),
        B(1.5, "butterflies", n=8, frame=True),
        B(.5, "circle"),
        B(1.0, "leaves", n=16),
    ], (3.6, c_butterfly))
    D["liberation-envol"] = lambda m, R: compose(m, R, [
        B(1.6, "scallops", n=16, inner=2, pointed=True),
        B(1.9, "birds", n=10, frame=True),
        B(.4, "circle"),
        B(1.0, "feathers", n=16, width=1.1),
        B(.3, "circle"),
    ], (3.4, c_lotus(10)))

    # IX. Motivation
    D["motivation-sommet"] = lambda m, R: compose(m, R, [
        B(1.8, "triangles", n=24, inner=2),
        B(1.4, "mountains", n=10, frame=True),
        B(.4, "circle"),
        B(.8, "stars", n=20),
        B(.3, "circle"),
    ], (4.2, c_mountain))
    D["motivation-elan"] = lambda m, R: compose(m, R, [
        B(2.0, "petals", n=20, style="spade", width=1.2, inner=1),
        B(.8, "lattice", n=20),
        B(1.3, "triangles", n=20, inner=2),
        B(.5, "beads", n=40, f=.7),
    ], (4.0, c_sun(10)))

    # X. Les éléments
    D["element-terre"] = lambda m, R: compose(m, R, [
        B(1.8, "leaves", n=24, width=1.1),
        B(1.2, "mountains", n=12, frame=True),
        B(.4, "circle"),
        B(.9, "lattice", n=16),
    ], (4.6, c_square))
    D["element-eau"] = lambda m, R: compose(m, R, [
        B(1.8, "drops", n=18),
        B(.9, "wave", n=18, frame=True),
        B(.9, "braid", n=12),
        B(1.0, "scallops", n=24, inner=1),
    ], (4.0, c_drop))
    D["element-feu"] = lambda m, R: compose(m, R, [
        B(2.2, "flames", n=18),
        B(1.4, "flames", n=18, offset=10, frame=True),
        B(.5, "beads", n=36, f=.7),
        B(1.0, "triangles", n=18, inner=1),
    ], (3.4, c_flame))
    D["element-air"] = lambda m, R: compose(m, R, [
        B(1.6, "feathers", n=20, width=1.1),
        B(1.3, "swirls", n=12, frame=True),
        B(.4, "circle"),
        B(1.0, "petals", n=16, style="round", width=1.1, inner=1),
    ], (3.8, c_air))
    D["element-ether"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=24, style="pointed", width=1.2, inner=1),
        B(.8, "stars", n=24, points=4, frame=True),
        B(.4, "circle"),
        B(1.0, "lattice", n=24),
        B(.5, "beads", n=36, f=.65),
    ], (4.0, c_ether))

    # XI. Géométrie sacrée et fréquences
    D["sacre-fleur-de-vie"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=24, style="lotus", width=1.2, inner=1),
        B(.6, "beads", n=48, f=.7, frame=True),
        B(.3, "circle"),
    ], (6.0, c_flower))
    D["sacre-yantra"] = lambda m, R: compose(m, R, [
        B(1.4, "petals", n=32, style="lotus", width=1.2, inner=1),
        B(.5, "beads", n=48, f=.7, frame=True),
        B(.3, "circle"),
    ], (6.0, c_yantra_interlaced))
    D["sacre-metatron"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=18, style="dome", width=1.15, inner=1),
        B(.6, "braid", n=12),
        B(.3, "circle"),
    ], (6.0, c_metatron))
    D["sacre-frequences"] = lambda m, R: compose(m, R, [
        B(1.6, "petals", n=27, style="round", width=1.1, inner=1),
        B(.8, "wave", n=27, frame=True),
        B(.5, "beads", n=36, f=.7),
        B(1.0, "scallops", n=18, inner=1, pointed=True),
    ], (4.4, c_frequencies))
    D["finale-voix"] = finale
    return D
