#!/usr/bin/env python3
"""Vidéos d'ambiance pour mettre en fond : scènes calmes dessinées en code,
en boucle parfaite, avec un son d'ambiance synthétisé (vent, pluie...).

Scènes :
  neige     nuit d'hiver, sapins, lune, neige qui tombe (3 profondeurs) ; vent doux
  aurores   aurores boréales au-dessus d'un lac et des montagnes ; vent léger
  pluie     pluie douce la nuit sur une vitre embuée de lumières ; pluie

Usage :
  python3 youtube/ambiances.py neige --apercu        # une image fixe
  python3 youtube/ambiances.py neige --minutes 60    # la vidéo
"""
import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generer_videos as gv  # noqa: E402

W, H = 1920, 1080
FPS = 30
LOOP_S = 30
TAU = 2 * np.pi


def degrade(haut, bas, h=H, w=W, courbe=1.0):
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None] ** courbe
    c = np.array(haut, np.float32) / 255 * (1 - t) + np.array(bas, np.float32) / 255 * t
    return np.repeat(c, w, axis=1)


def halo(img, cx, cy, rayon, couleur, force):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d2 = ((x - cx) ** 2 + (y - cy) ** 2) / rayon ** 2
    img += np.exp(-d2)[..., None] * np.array(couleur, np.float32) / 255 * force
    return img


def etoiles(rng, n, hmax):
    return (rng.uniform(0, W, n), rng.uniform(0, hmax, n), rng.uniform(0.15, 0.7, n),
            rng.uniform(0, TAU, n), rng.integers(1, 4, n))


def poser(img, x0, y0, s, lum, couleur):
    """Petit point lumineux gaussien (flocon, étoile, goutte)."""
    R = max(1, int(s * 3))
    x1, x2 = max(int(x0) - R, 0), min(int(x0) + R + 1, W)
    y1, y2 = max(int(y0) - R, 0), min(int(y0) + R + 1, H)
    if x1 >= x2 or y1 >= y2:
        return
    gx = np.arange(x1, x2, dtype=np.float32) - x0
    gy = np.arange(y1, y2, dtype=np.float32)[:, None] - y0
    g = np.exp(-(gx * gx + gy * gy) / (s * s)) * lum
    img[y1:y2, x1:x2] += g[..., None] * couleur


def silhouette_montagnes(rng, base, ampl, couleur, n=6):
    xs = np.arange(W, dtype=np.float32) / W
    y = np.full(W, base, np.float32)
    for k in range(1, n + 1):
        y -= ampl / k * np.abs(np.sin(TAU * (k * 0.7 * xs + rng.uniform())))
    masque = np.arange(H, dtype=np.float32)[:, None] >= y[None, :]
    return masque, couleur


def sapins(rng, n, ybase, hmin, hmax, couleur, larg=0.42):
    """Calque RGBA de sapins dessinés en triangles empilés (anticrénelé x2)."""
    S = 2
    img = Image.new("L", (W * S, H * S), 0)
    dr = ImageDraw.Draw(img)
    for _ in range(n):
        x = rng.uniform(-40, W + 40) * S
        h = rng.uniform(hmin, hmax) * S
        yb = (ybase + rng.uniform(-12, 12)) * S
        etages = 5
        for e in range(etages):
            t0 = e / etages
            haut = yb - h * (t0 * 0.85 + 0.15)
            bas = yb - h * t0 * 0.75
            demi = h * larg * (1 - t0 * 0.8) * 0.5
            dr.polygon([(x, haut - h * 0.18), (x - demi, bas), (x + demi, bas)], fill=255)
        dr.rectangle([x - h * 0.02, yb - h * 0.05, x + h * 0.02, yb + 4 * S], fill=255)
    m = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    return m[..., None], np.array(couleur, np.float32) / 255


# ------------------------------------------------------------------ neige ---
class Neige:
    nom = "Neige qui tombe · nuit d'hiver"

    def __init__(self):
        rng = np.random.default_rng(7)
        img = degrade((8, 14, 30), (34, 48, 78), courbe=1.3)
        img = halo(img, W * 0.76, H * 0.20, 260, (150, 170, 210), 0.30)
        img = halo(img, W * 0.76, H * 0.20, 46, (230, 236, 248), 0.9)
        self.etoiles = etoiles(rng, 260, H * 0.55)
        m, c = silhouette_montagnes(rng, H * 0.62, H * 0.16, (26, 38, 62))
        img = np.where(m[..., None], np.array(c, np.float32) / 255, img)
        for n, yb, hmin, hmax, col in [(60, H * 0.80, 90, 170, (18, 28, 46)),
                                       (34, H * 0.92, 180, 320, (10, 16, 28)),
                                       (12, H * 1.02, 380, 620, (5, 8, 15))]:
            a, cc = sapins(rng, n, yb, hmin, hmax, col)
            img = img * (1 - a) + cc * a
        # sol enneigé
        y = np.arange(H, dtype=np.float32)[:, None, None]
        sol = np.clip((y - H * 0.90) / (H * 0.10), 0, 1)
        img = img * (1 - sol * 0.6) + np.array([0.55, 0.62, 0.74], np.float32) * sol * 0.6
        self.fond = img.astype(np.float32)
        # flocons : (nombre, passages par boucle, taille, luminosité)
        self.couches = []
        for n, vit, smin, smax, lum in [(520, 1, 0.8, 1.4, 0.45), (260, 2, 1.4, 2.4, 0.65),
                                        (70, 3, 2.6, 4.2, 0.85)]:
            self.couches.append(dict(
                x=rng.uniform(0, W, n), y0=rng.uniform(0, 1, n), vit=vit,
                s=rng.uniform(smin, smax, n), lum=lum * rng.uniform(0.6, 1, n),
                bal=rng.uniform(8, 40, n), fb=rng.integers(1, 4, n), ph=rng.uniform(0, TAU, n)))

    def image(self, t):
        ph = TAU * t / LOOP_S
        img = self.fond.copy()
        ex, ey, el, ep, ef = self.etoiles
        for x, y, l, p, f in zip(ex, ey, el, ep, ef):
            poser(img, x, y, 0.9, l * (0.6 + 0.4 * math.sin(f * ph + p)), np.float32([0.85, 0.9, 1]))
        blanc = np.float32([0.92, 0.95, 1.0])
        for c in self.couches:
            yy = ((c["y0"] + c["vit"] * t / LOOP_S) % 1.0) * (H + 40) - 20
            xx = c["x"] + c["bal"] * np.sin(c["fb"] * ph + c["ph"])
            for x, y, s, l in zip(xx, yy, c["s"], c["lum"]):
                poser(img, x, y, s, l, blanc)
        return np.clip(img, 0, 1)

    audio = ("anoisesrc=c=brown:a=0.5:r=48000,lowpass=f=420,highpass=f=40,"
             "volume='1.6*(0.7+0.3*sin(2*PI*t*0.07))':eval=frame")


# ---------------------------------------------------------------- aurores ---
class Aurores:
    nom = "Aurores boréales · lac de nuit"

    def __init__(self):
        rng = np.random.default_rng(11)
        self.horizon = int(H * 0.60)
        hz = self.horizon
        self.ciel = degrade((4, 8, 18), (14, 26, 40), h=hz, courbe=1.2)
        self.etoiles = etoiles(rng, 320, hz * 0.95)
        m, c = silhouette_montagnes(rng, hz, H * 0.055, (7, 11, 18), n=4)
        self.mont = (m[:hz], np.array(c, np.float32) / 255)
        a, cc = sapins(rng, 90, hz + 4, 60, 150, (3, 5, 9), larg=0.36)
        self.sapins = (a[:hz + 6], cc)
        y, x = np.mgrid[0:hz, 0:W].astype(np.float32)
        self.x, self.y = x / W, y / hz

    def ciel_frame(self, ph):
        img = self.ciel.copy()
        ex, ey, el, ep, ef = self.etoiles
        for xs, ys, l, p, f in zip(ex, ey, el, ep, ef):
            poser(img, xs, ys, 0.9, l * (0.6 + 0.4 * math.sin(f * ph + p)), np.float32([0.85, 0.9, 1]))
        x, y = self.x, self.y
        for k, (base, amp, vert, rose, phase) in enumerate([(0.42, 0.10, 1.0, 0.0, 0.0),
                                                            (0.30, 0.07, 0.7, 0.5, 2.1)]):
            y0 = (base + amp * np.sin(TAU * (1.3 * x) + ph + phase)
                  + 0.04 * np.sin(TAU * (3.1 * x) - 2 * ph + phase))
            dy = y0 - y                                   # > 0 au-dessus de la lisière
            bord = np.exp(-np.clip(-dy, 0, None) ** 2 / 0.0006)
            rideau = np.where(dy > 0, np.exp(-dy / (0.16 + 0.05 * np.sin(ph + k))), bord)
            rayons = 0.45 + 0.55 * np.sin(TAU * 22 * x + 3 * np.sin(ph + TAU * 2 * x) + phase) ** 4
            souffle = 0.75 + 0.25 * np.sin(ph * 2 + TAU * x + phase)
            inten = (rideau * rayons * souffle * np.clip(np.sin(np.pi * x) * 1.6, 0, 1))[..., None]
            haut = np.clip(dy / 0.25, 0, 1)[..., None]
            couleur = (np.float32([0.25, 0.95, 0.55]) * (1 - haut * rose)
                       + np.float32([0.70, 0.35, 0.85]) * haut * rose)
            img += inten * couleur * 0.55 * vert
        m, c = self.mont
        img = np.where(m[..., None], c, img)
        a, cc = self.sapins
        img = img * (1 - a[:len(img)]) + cc * a[:len(img)]
        return img

    def image(self, t):
        ph = TAU * t / LOOP_S
        ciel = self.ciel_frame(ph)
        hz = self.horizon
        out = np.zeros((H, W, 3), np.float32)
        out[:hz] = ciel
        # reflet dans le lac : miroir, assombri, légèrement ondulé
        n = H - hz
        rows = np.arange(n)
        ond = (3 * np.sin(rows / 6.0 + 2 * ph) * (rows / n)).astype(int)
        src = np.clip(hz - 1 - rows, 0, hz - 1)
        refl = ciel[src]
        refl = np.stack([np.roll(refl[i], ond[i], axis=0) for i in range(n)])
        fade = (0.55 * (1 - rows / n * 0.6))[:, None, None]
        out[hz:] = refl * fade + np.float32([0.01, 0.02, 0.03])
        return np.clip(out, 0, 1)

    audio = ("anoisesrc=c=brown:a=0.4:r=48000,lowpass=f=300,highpass=f=35,"
             "volume='1.3*(0.65+0.35*sin(2*PI*t*0.05))':eval=frame")


# ------------------------------------------------------------------ pluie ---
class Pluie:
    nom = "Pluie douce · lumières de la ville"

    def __init__(self):
        rng = np.random.default_rng(3)
        img = degrade((10, 12, 20), (26, 22, 30))
        # bokeh : lumières floues de la ville derrière la vitre
        bok = Image.new("RGB", (W, H), (0, 0, 0))
        dr = ImageDraw.Draw(bok)
        cols = [(255, 190, 110), (255, 150, 90), (120, 170, 255), (255, 220, 160), (200, 120, 160)]
        for _ in range(70):
            x, y = rng.uniform(0, W), rng.uniform(H * 0.35, H * 0.95)
            r = rng.uniform(14, 60)
            c = cols[rng.integers(len(cols))]
            k = rng.uniform(0.25, 0.6)
            dr.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * k) for v in c))
        bok = np.asarray(bok.filter(ImageFilter.GaussianBlur(18))).astype(np.float32) / 255
        self.fond = img + bok
        self.bok_ph = rng.uniform(0, TAU, 1)
        n = 900
        self.x = rng.uniform(0, W, n)
        self.y0 = rng.uniform(0, 1, n)
        self.vit = rng.integers(6, 10, n)                 # passages par boucle
        self.long = rng.uniform(18, 46, n)
        self.lum = rng.uniform(0.10, 0.28, n)
        # gouttes posées sur la vitre (fixes, scintillent)
        self.g = (rng.uniform(0, W, 140), rng.uniform(0, H, 140), rng.uniform(1.5, 4, 140),
                  rng.uniform(0, TAU, 140))

    def image(self, t):
        ph = TAU * t / LOOP_S
        img = self.fond * (0.92 + 0.08 * math.sin(ph))
        couleur = np.float32([0.75, 0.8, 0.95])
        yy = ((self.y0 + self.vit * t / LOOP_S) % 1.0) * (H + 80) - 40
        for x, y, L, l in zip(self.x, yy, self.long, self.lum):
            x0 = int(x)
            y1, y2 = max(int(y - L), 0), min(int(y), H)
            if y1 >= y2 or not 0 <= x0 < W - 1:
                continue
            ramp = np.linspace(0, l, y2 - y1, dtype=np.float32)[:, None]
            img[y1:y2, x0] += ramp * couleur
            img[y1:y2, x0 + 1] += ramp * couleur * 0.4
        gx, gy, gs, gp = self.g
        for x, y, s, p in zip(gx, gy, gs, gp):
            poser(img, x, y, s, 0.10 + 0.06 * math.sin(ph + p), np.float32([0.9, 0.92, 1]))
        return np.clip(img, 0, 1)

    audio = ("anoisesrc=c=pink:a=0.35:r=48000,highpass=f=300,lowpass=f=6000,"
             "volume=0.9[a];anoisesrc=c=brown:a=0.4:r=48000,lowpass=f=250,volume=0.8[b];"
             "[a][b]amix=inputs=2:normalize=0")


SCENES = {"neige": Neige, "aurores": Aurores, "pluie": Pluie}


def rendre(scene, dst):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *gv.X264, "-an", dst],
                         stdin=subprocess.PIPE)
    n = LOOP_S * FPS
    for k in range(n):
        p.stdin.write((scene.image(k / FPS) * 255 + 0.5).astype(np.uint8).tobytes())
        if k % 90 == 0:
            print(f"    image {k}/{n}", flush=True)
    p.stdin.close()
    if p.wait():
        sys.exit("ffmpeg a échoué")


def assembler(boucle, filtre_audio, minutes, dst, tmp):
    total = minutes * 60
    ouv, fer = os.path.join(tmp, "ouv.mp4"), os.path.join(tmp, "fer.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", boucle, "-vf", "fade=t=in:st=0:d=5",
                    *gv.X264, ouv], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", boucle, "-vf",
                    f"fade=t=out:st={LOOP_S - 8}:d=8", *gv.X264, fer], check=True)
    n = total // LOOP_S
    liste = os.path.join(tmp, "liste.txt")
    with open(liste, "w") as fh:
        fh.write(f"file '{ouv}'\n")
        fh.writelines(f"file '{boucle}'\n" for _ in range(n - 2))
        fh.write(f"file '{fer}'\n")
    audio = os.path.join(tmp, "audio.m4a")
    fin = f"aformat=channel_layouts=stereo,afade=t=in:st=0:d=6,afade=t=out:st={total - 10}:d=10"
    import sons
    wav = sons.fichier(os.path.basename(boucle).split("-")[0], total, os.path.join(tmp, "sons"))
    if wav:
        entree = ["-i", wav, "-af", fin]
    elif "[" in filtre_audio:
        entree = ["-filter_complex", f"{filtre_audio},{fin}[out]", "-map", "[out]"]
    else:
        entree = ["-f", "lavfi", "-i", f"{filtre_audio},{fin}"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entree, "-t", str(total),
                    "-c:a", "aac", "-b:a", "160k", audio], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", liste,
                    "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest",
                    "-movflags", "+faststart", dst], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="+", choices=list(SCENES))
    ap.add_argument("--minutes", type=int, default=60)
    ap.add_argument("--apercu", action="store_true")
    ap.add_argument("--out", default=os.path.join(gv.RACINE, "youtube", "sortie", "ambiances"))
    arg = ap.parse_args()
    os.makedirs(arg.out, exist_ok=True)
    for nom in arg.scenes:
        sc = SCENES[nom]()
        if arg.apercu:
            Image.fromarray((sc.image(LOOP_S * 0.3) * 255).astype(np.uint8)).save(
                os.path.join(arg.out, f"{nom}-apercu.jpg"), quality=90)
            continue
        print(f"== {nom}", flush=True)
        tmp = tempfile.mkdtemp(prefix=nom + "-")
        try:
            boucle = os.path.join(arg.out, f"{nom}-boucle.mp4")
            if not os.path.exists(boucle):
                rendre(sc, boucle)
            assembler(boucle, sc.audio, arg.minutes,
                      os.path.join(arg.out, f"{nom}-{arg.minutes}min.mp4"), tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()


# ------------------------------------------------------------- miniatures ---
TITRES = {
    "neige": ("Neige qui tombe", "Nuit d'hiver · sons du vent"),
    "aurores": ("Aurores boréales", "Lac de nuit · vent léger"),
    "pluie": ("Pluie douce", "Lumières de la ville · son de pluie"),
}


def miniature(nom, dst, duree="1 H"):
    """Miniature 1280x720 : la scène, un grand titre, la durée. Sans marque."""
    sc = SCENES[nom]()
    img = Image.fromarray((sc.image(LOOP_S * 0.3) * 255).astype(np.uint8))
    img = img.resize((1280, 720), Image.LANCZOS).convert("RGBA")
    calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(calque)
    titre, sous = TITRES[nom]
    gv.centrer(dr, 1280, titre, gv.police("InterDisplay-Light.otf", 128), 210, gv.CREME + (255,))
    gv.centrer(dr, 1280, sous, gv.police("Inter-Regular.otf", 40), 380, gv.CREME + (225,))
    gv.centrer(dr, 1280, duree, gv.police("Inter-SemiBold.otf", 44), 460, (255, 255, 255, 235), esp=6)
    ombre = calque.filter(ImageFilter.GaussianBlur(12))
    noir = Image.new("RGBA", img.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: int(v * 0.7)))
    Image.alpha_composite(Image.alpha_composite(img, noir), calque).convert("RGB").save(dst, quality=92)
