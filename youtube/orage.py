#!/usr/bin/env python3
"""Ambiance « Orage » : nuages qui filent, pluie battante en diagonale, éclairs
synchronisés avec le tonnerre (sons.orage / sons.eclairs).

La boucle de 30 s (nuages + pluie) est rendue une fois ; les éclairs (flash du
ciel + foudre) sont posés à l'assemblage aux mêmes instants que le tonnerre.

Usage : python3 youtube/orage.py --minutes 20 [--apercu] [--vbit 520k]
"""
import argparse
import os
import subprocess
import tempfile
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import ambiances as amb
import generer_videos as gv
import sons

W, H, LOOP_S, TAU = amb.W, amb.H, amb.LOOP_S, amb.TAU
SORTIE = os.path.join(gv.RACINE, "youtube", "sortie", "ambiances")


def texture_nuages(rng, h, w, sigma):
    """Bruit filtré dans le domaine fréquentiel : texture périodique (se raccorde à elle-même)."""
    b = rng.standard_normal((h, w))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.exp(-(fx ** 2 * (w / sigma) ** 2 + fy ** 2 * (h / sigma * 2.2) ** 2))
    t = np.real(np.fft.ifft2(np.fft.fft2(b) * f))
    t = (t - t.min()) / (t.max() - t.min())
    return t.astype(np.float32)


class Orage:
    nom = "Orage · pluie battante et tonnerre"

    def __init__(self):
        rng = np.random.default_rng(31)
        self.fond = amb.degrade((14, 16, 22), (30, 33, 42), courbe=0.8)
        hc = int(H * 0.72)
        self.n1 = texture_nuages(rng, hc, W, 9) ** 1.4
        self.n2 = texture_nuages(rng, hc, W, 18) ** 1.8
        prof = np.clip(1 - np.linspace(0, 1, hc, dtype=np.float32) ** 1.5, 0, 1)[:, None]
        self.n1 *= prof
        self.n2 *= prof
        self.hc = hc
        # sol : collines et arbres, presque noirs
        m, c = amb.silhouette_montagnes(rng, H * 0.80, 70, (12, 13, 17))
        self.colline = m[..., None].astype(np.float32)
        self.arbres, self.c_arbres = amb.sapins(rng, 46, H * 0.86, 90, 230, (7, 8, 10), larg=0.38)
        n = 1500
        self.x0 = rng.uniform(0, W * 1.3, n)
        self.y0 = rng.uniform(0, 1, n)
        self.vit = rng.integers(14, 22, n)          # passages par boucle : pluie rapide
        self.long = rng.uniform(30, 80, n)
        self.lum = rng.integers(40, 110, n)
        self.pente = 0.32

    def image(self, t):
        img = self.fond.copy()
        d1 = int(round(W * t / LOOP_S))             # 1 tour de texture par boucle
        d2 = int(round(2 * W * t / LOOP_S))
        n1 = np.roll(self.n1, d1, axis=1)
        n2 = np.roll(self.n2, d2, axis=1)
        nuages = 0.55 * n1 + 0.45 * n2
        img[: self.hc] = img[: self.hc] * (1 - 0.55 * nuages[..., None]) + \
            nuages[..., None] * np.float32([0.27, 0.28, 0.33])
        img = img * (1 - self.colline) + self.colline * np.float32([12, 13, 17]) / 255
        img = img * (1 - self.arbres) + self.arbres * self.c_arbres
        pl = Image.new("L", (W, H), 0)
        dr = ImageDraw.Draw(pl)
        yy = ((self.y0 + self.vit * t / LOOP_S) % 1.0) * (H + 160) - 80
        for x0, y, L, l in zip(self.x0, yy, self.long, self.lum):
            x = (x0 - self.pente * y) % (W * 1.3) - W * 0.15
            dr.line([(x, y), (x + self.pente * L, y - L)], fill=int(l), width=1)
        pl = np.asarray(pl.filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32) / 255
        img += pl[..., None] * np.float32([0.62, 0.66, 0.75])
        return np.clip(img, 0, 1)


def foudre(graine, dst, xpos=None):
    """Calque RGBA d'un éclair ramifié avec halo."""
    rng = np.random.default_rng(graine)
    S = 2
    trait = Image.new("L", (W * S, H * S), 0)
    dr = ImageDraw.Draw(trait)

    def branche(x, y, y_fin, larg, prof):
        while y < y_fin:
            nx = x + rng.normal(0, 26) * S
            ny = y + rng.uniform(18, 46) * S
            dr.line([(x, y), (nx, ny)], fill=255, width=max(1, int(larg)))
            if prof < 2 and rng.uniform() < 0.12:
                branche(nx, ny, ny + rng.uniform(80, 260) * S, larg * 0.5, prof + 1)
            x, y = nx, ny
            larg *= 0.985

    x = (xpos if xpos is not None else rng.uniform(0.25, 0.75)) * W * S
    branche(x, rng.uniform(0.05, 0.15) * H * S, rng.uniform(0.74, 0.84) * H * S, 5 * S, 0)
    trait = trait.resize((W, H), Image.LANCZOS)
    halo = trait.filter(ImageFilter.GaussianBlur(14))
    halo2 = trait.filter(ImageFilter.GaussianBlur(60))
    a = np.clip(np.asarray(trait, np.float32) + 1.4 * np.asarray(halo, np.float32)
                + 1.2 * np.asarray(halo2, np.float32), 0, 255)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 225, 230, 255
    rgba[..., 3] = a.astype(np.uint8)
    Image.fromarray(rgba).save(dst)


def assembler(minutes, dst, vbit, tmp):
    total = minutes * 60
    boucle = os.path.join(SORTIE, "orage-boucle.mp4")
    if not os.path.exists(boucle):
        amb.rendre(Orage(), boucle)
    wav = sons.fichier("orage", total, os.path.join(SORTIE, "sons"))
    ev = sons.eclairs(total)
    # flash : deux pulsations rapides + rémanence, plus fort quand l'éclair est proche
    termes = []
    for t0, dist, _ in ev:
        f = 0.42 * (1 - 0.6 * dist)
        termes.append(f"{f:.2f}*(exp(-pow((t-{t0})/0.05,2))+0.7*exp(-pow((t-{t0}-0.17)/0.05,2))"
                      f"+0.35*exp(-abs(t-{t0}-0.17)*4)*gte(t,{t0}+0.17))")
    flash = "+".join(termes) or "0"
    entrees = ["-stream_loop", "-1", "-i", boucle, "-i", wav]
    graphe = [f"[0:v]trim=0:{total},setpts=PTS-STARTPTS,eq=brightness='{flash}':eval=frame,"
              f"fade=t=in:st=0:d=5,fade=t=out:st={total - 8}:d=8[b0]"]
    for v in range(3):
        png = os.path.join(tmp, f"foudre{v}.png")
        foudre(100 + v, png)
        entrees += ["-loop", "1", "-framerate", "30", "-i", png]
        quand = "+".join(f"between(t,{t0},{t0 + 0.09})+between(t,{t0 + 0.15},{t0 + 0.3})"
                         for t0, dist, var in ev if var == v and dist < 0.7) or "0"
        graphe.append(f"[b{v}][{v + 2}:v]overlay=shortest=0:eof_action=repeat:enable='{quand}'[b{v + 1}]")
    graphe.append("[b3]format=yuv420p[v]")
    graphe.append(f"[1:a]afade=t=in:st=0:d=5,afade=t=out:st={total - 10}:d=10[a]")
    script = os.path.join(tmp, "graphe.txt")
    open(script, "w").write(";\n".join(graphe))
    commun = [*entrees, "-filter_complex_script", script, "-map", "[v]", "-t", str(total),
              "-c:v", "libx264", "-preset", "medium", "-b:v", vbit, "-g", "60", "-r", "30"]
    log = os.path.join(tmp, "2pass")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *commun, "-pass", "1", "-passlogfile", log,
                    "-an", "-f", "null", "/dev/null"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *commun, "-pass", "2", "-passlogfile", log,
                    "-map", "[a]", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", dst],
                   check=True)


def miniature(dst, duree):
    sc = Orage()
    img = sc.image(LOOP_S * 0.4)
    img = np.clip(img * 1.25, 0, 1)
    base = Image.fromarray((img * 255).astype(np.uint8)).convert("RGBA")
    tmp = dst + ".foudre.png"
    foudre(101, tmp, xpos=0.86)
    base = Image.alpha_composite(base, Image.open(tmp))
    os.remove(tmp)
    base = base.resize((1280, 720), Image.LANCZOS)
    c = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(c)
    gv.centrer(dr, 1280, "Orage", gv.police("InterDisplay-Light.otf", 150), 190, gv.CREME + (255,))
    gv.centrer(dr, 1280, "Tonnerre · vent · pluie battante", gv.police("Inter-Regular.otf", 42), 380,
               gv.CREME + (230,))
    gv.centrer(dr, 1280, duree, gv.police("Inter-SemiBold.otf", 44), 460, (255, 255, 255, 235), esp=6)
    ombre = c.filter(ImageFilter.GaussianBlur(12))
    noir = Image.new("RGBA", base.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: int(v * 0.75)))
    Image.alpha_composite(Image.alpha_composite(base, noir), c).convert("RGB").save(dst, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=20)
    ap.add_argument("--vbit", default="520k")
    ap.add_argument("--apercu", action="store_true")
    arg = ap.parse_args()
    os.makedirs(SORTIE, exist_ok=True)
    duree = "1 H" if arg.minutes == 60 else f"{arg.minutes} MIN"
    miniature(os.path.join(SORTIE, f"orage-miniature-{arg.minutes}min.jpg"), duree)
    if arg.apercu:
        Image.fromarray((Orage().image(5) * 255).astype(np.uint8)).save(
            os.path.join(SORTIE, "orage-apercu.jpg"), quality=90)
        return
    tmp = tempfile.mkdtemp(prefix="orage-")
    try:
        dst = os.path.join(SORTIE, f"orage-{arg.minutes}min.mp4")
        assembler(arg.minutes, dst, arg.vbit, tmp)
        print("->", dst, f"{os.path.getsize(dst) / 1e6:.0f} Mo", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
