#!/usr/bin/env python3
"""Vidéos YouTube « Waves » de 10 minutes, une par fréquence du catalogue.

Pour chaque fréquence de catalog.json :
  1. l'audio hz/hz-XXX.m4a (10 min, binaural) est repris tel quel ;
  2. une boucle visuelle parfaitement périodique de LOOP_S secondes est rendue
     (ondes concentriques qui respirent, ligne d'onde, poussière lumineuse) ;
  3. la boucle est répétée jusqu'à 10 min (copie de flux, sans ré-encodage),
     avec un fondu au noir à l'ouverture et à la fermeture ;
  4. une miniature 1280x720 est produite.

Usage :
  python3 youtube/generer_videos.py               # toutes les fréquences
  python3 youtube/generer_videos.py hz-432 hz-528 # seulement celles-ci
  options : --out DOSSIER  --apercu (boucle seule, pas de vidéo 10 min)
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080
FPS = 30
LOOP_S = 20                 # durée de la boucle visuelle
DUREE_S = 10 * 60           # durée finale = durée des fichiers hz/
POLICE = "/usr/share/fonts/opentype/inter/"

# Teinte d'accent par fréquence (du grave chaud vers l'aigu violet),
# toujours posée sur le vert profond et l'or de la marque.
TEINTES = {
    174: (196, 122, 62),   # ambre
    285: (201, 141, 92),   # cuivre
    396: (196, 104, 92),   # rose terre
    417: (214, 150, 80),   # orange doux
    432: (192, 154, 78),   # or de la marque
    528: (126, 180, 120),  # vert cœur
    639: (104, 176, 168),  # turquoise
    741: (110, 150, 205),  # bleu gorge
    852: (138, 128, 210),  # indigo
    963: (182, 140, 214),  # violet
}
FOND = np.array([28, 40, 32], np.float32) / 255      # #1C2820
CREME = (255, 253, 248)
OR = (192, 154, 78)


def police(nom, taille):
    return ImageFont.truetype(os.path.join(POLICE, nom), taille)


# ---------------------------------------------------------------- image ---
class Scene:
    def __init__(self, freq, teinte):
        self.freq = freq
        self.teinte = np.array(teinte, np.float32) / 255
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        self.cx, self.cy = W / 2, H * 0.46
        self.x, self.y = x, y
        self.d = np.hypot(x - self.cx, (y - self.cy) * 1.04) / H
        # fond : dégradé radial vert profond -> presque noir, vignette
        v = np.clip(self.d / 0.95, 0, 1)
        fond = FOND * (1.25 - 0.85 * v ** 1.4)[..., None]
        fond += self.teinte * (0.10 * np.exp(-(self.d / 0.55) ** 2))[..., None]
        self.fond = fond.astype(np.float32)
        # bruit fixe très léger : casse les bandes du dégradé sans coûter
        rng = np.random.default_rng(int(freq["hz"]))
        self.grain = (rng.standard_normal((H, W, 1)) * 0.0045).astype(np.float32)
        # poussière lumineuse : trajectoires fermées sur la boucle
        n = 70
        self.p_r = rng.uniform(0.12, 0.62, n)
        self.p_a = rng.uniform(0, 2 * np.pi, n)
        self.p_k = rng.choice([-1, 1], n)            # 1 tour par boucle
        self.p_w = rng.uniform(0.04, 0.10, n)         # ondulation radiale
        self.p_m = rng.integers(1, 4, n)
        self.p_ph = rng.uniform(0, 2 * np.pi, n)
        self.p_s = rng.uniform(1.2, 3.2, n)
        self.p_l = rng.uniform(0.25, 0.9, n)
        # les ondes s'effacent derrière les mentions du bas
        self.calme = (1 - 0.65 * np.clip((y / H - 0.84) / 0.05, 0, 1)).astype(np.float32)
        self.texte = self._texte()

    def _texte(self):
        """Calque RGBA du texte, rendu une seule fois."""
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        def centre(txt, f, y, couleur, esp=0):
            if esp:
                largeur = sum(dr.textlength(c, font=f) for c in txt) + esp * (len(txt) - 1)
                x = (W - largeur) / 2
                for c in txt:
                    dr.text((x, y), c, font=f, fill=couleur)
                    x += dr.textlength(c, font=f) + esp
            else:
                dr.text(((W - dr.textlength(txt, font=f)) / 2, y), txt, font=f, fill=couleur)
        hz = f"{self.freq['hz']:g} Hz"
        centre(hz, police("InterDisplay-ExtraLight.otf", 132), H * 0.46 - 92, CREME + (235,))
        centre(self.freq["title"], police("Inter-Light.otf", 40), H * 0.46 + 70, CREME + (200,))
        centre(self.freq["wave"].upper() + "  ·  ÉCOUTEURS RECOMMANDÉS",
               police("Inter-Regular.otf", 20), H - 118, OR + (190,), esp=3)
        centre("MA VOIX INTÉRIEURE", police("Inter-Medium.otf", 18), H - 78, CREME + (120,), esp=6)
        a = np.asarray(img).astype(np.float32) / 255
        return a[..., :3], a[..., 3:4]

    def image(self, t):
        ph = 2 * np.pi * t / LOOP_S                 # phase de boucle 0..2π
        d = self.d
        souffle = 0.5 - 0.5 * np.cos(ph)            # 1 respiration par boucle
        lum = np.zeros((H, W), np.float32)
        # ondes concentriques qui partent du centre : une nouvelle toutes
        # les LOOP_S / n secondes, chacune traverse l'écran en une boucle
        n = 7
        for i in range(n):
            u = (t / LOOP_S + i / n) % 1.0          # 0..1
            r = 0.06 + u * 0.78
            fade = math.sin(math.pi * u) ** 1.6
            larg = 0.004 + 0.010 * u
            lum += fade * 0.40 * np.exp(-((d - r) / larg) ** 2)
            lum += fade * 0.10 * np.exp(-((d - r) / (larg * 6)) ** 2)
        # halo central qui respire
        lum += (0.30 + 0.25 * souffle) * np.exp(-(d / (0.16 + 0.03 * souffle)) ** 2)
        # ligne d'onde horizontale (2 crêtes défilent par boucle)
        yy = (self.y - H * 0.80) / H
        xx = self.x / W
        onde = 0.018 * np.sin(2 * np.pi * (3 * xx - 2 * t / LOOP_S)) * np.sin(np.pi * xx)
        onde2 = 0.012 * np.sin(2 * np.pi * (5 * xx + t / LOOP_S) + 1.3) * np.sin(np.pi * xx)
        env = np.sin(np.pi * xx) ** 2
        lum += env * 0.35 * np.exp(-((yy - onde) / 0.0022) ** 2)
        lum += env * 0.18 * np.exp(-((yy - onde2) / 0.0018) ** 2)
        lum *= self.calme                           # zone du texte du bas
        img = self.fond + lum[..., None] * self.teinte[None, None, :] * 0.9
        img += (lum ** 2)[..., None] * 0.25        # cœur des ondes plus clair
        img = self._poussiere(img, ph)
        img = img + self.grain
        rgb, al = self.texte
        img = img * (1 - al) + rgb * al
        return np.clip(img, 0, 1)

    def _poussiere(self, img, ph):
        a = self.p_a + self.p_k * ph
        r = self.p_r + self.p_w * np.sin(self.p_m * ph + self.p_ph) * 0.3
        px = self.cx + np.cos(a) * r * H * 1.15
        py = self.cy + np.sin(a) * r * H * 0.95
        sc = 0.5 + 0.5 * np.sin(2 * ph + self.p_ph)   # scintillement
        for x0, y0, s, l, c in zip(px, py, self.p_s, self.p_l, sc):
            R = int(s * 4)
            x1, x2 = max(int(x0) - R, 0), min(int(x0) + R + 1, W)
            y1, y2 = max(int(y0) - R, 0), min(int(y0) + R + 1, H)
            if x1 >= x2 or y1 >= y2:
                continue
            gx = self.x[y1:y2, x1:x2] - x0
            gy = self.y[y1:y2, x1:x2] - y0
            g = np.exp(-(gx * gx + gy * gy) / (s * s)) * l * (0.35 + 0.65 * c)
            img[y1:y2, x1:x2] += g[..., None] * (self.teinte * 0.6 + 0.4)
        return img


# ---------------------------------------------------------------- vidéo ---
X264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
        "-g", str(FPS * 2), "-bf", "2", "-profile:v", "high", "-movflags", "+faststart"]


def rendre_boucle(scene, dst):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", *X264, "-an", dst], stdin=subprocess.PIPE)
    n = LOOP_S * FPS
    for k in range(n):
        f = scene.image(k / FPS)
        p.stdin.write((f * 255 + 0.5).astype(np.uint8).tobytes())
        if k % 60 == 0:
            print(f"    image {k}/{n}", flush=True)
    p.stdin.close()
    if p.wait():
        sys.exit("ffmpeg a échoué")


def assembler(boucle, audio, dst, tmp):
    """Ouverture (fondu du noir) + boucles copiées + fermeture (fondu au noir)."""
    ouv = os.path.join(tmp, "ouv.mp4")
    fer = os.path.join(tmp, "fer.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", boucle,
                    "-vf", "fade=t=in:st=0:d=4", *X264, ouv], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", boucle,
                    "-vf", f"fade=t=out:st={LOOP_S - 6}:d=6", *X264, fer], check=True)
    n = DUREE_S // LOOP_S
    liste = os.path.join(tmp, "liste.txt")
    with open(liste, "w") as fh:
        fh.write(f"file '{ouv}'\n")
        fh.writelines(f"file '{boucle}'\n" for _ in range(n - 2))
        fh.write(f"file '{fer}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                    "-i", liste, "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c", "copy", "-shortest", "-movflags", "+faststart", dst],
                   check=True)


def miniature(scene, freq, dst):
    """Miniature YouTube 1280x720 : grande fréquence, titre, mention 10 min."""
    # on retire le texte de la vidéo : on repart du rendu sans calque texte
    rgb, al = scene.texte
    scene.texte = (rgb, al * 0)
    base = Image.fromarray((scene.image(LOOP_S * 0.42) * 255).astype(np.uint8))
    scene.texte = (rgb, al)
    img = base.resize((1280, 720), Image.LANCZOS).convert("RGBA")
    calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(calque)
    def centre(txt, f, y, c):
        dr.text(((1280 - dr.textlength(txt, font=f)) / 2, y), txt, font=f, fill=c)
    centre(f"{freq['hz']:g} Hz", police("InterDisplay-Light.otf", 210), 150, CREME + (255,))
    centre(freq["title"], police("Inter-Medium.otf", 56), 420, CREME + (240,))
    centre("10 MIN  ·  " + freq["wave"].upper(), police("Inter-SemiBold.otf", 34), 515, OR + (255,))
    ombre = calque.filter(ImageFilter.GaussianBlur(10))
    noir = Image.new("RGBA", img.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: int(v * 0.6)))
    img = Image.alpha_composite(Image.alpha_composite(img, noir), calque)
    img.convert("RGB").save(dst, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--out", default=os.path.join(RACINE, "youtube", "sortie"))
    ap.add_argument("--apercu", action="store_true")
    arg = ap.parse_args()
    with open(os.path.join(RACINE, "catalog.json"), encoding="utf-8") as fh:
        freqs = json.load(fh)["frequences"]
    if arg.ids:
        freqs = [f for f in freqs if f["id"] in arg.ids]
    os.makedirs(arg.out, exist_ok=True)
    for f in freqs:
        hz = int(f["hz"])
        print(f"== {f['id']} · {f['title']}", flush=True)
        scene = Scene(f, TEINTES.get(hz, OR))
        tmp = tempfile.mkdtemp(prefix=f["id"] + "-")
        try:
            miniature(scene, f, os.path.join(arg.out, f"{f['id']}-miniature.jpg"))
            boucle = os.path.join(tmp, "boucle.mp4")
            rendre_boucle(scene, boucle)
            if arg.apercu:
                shutil.copy(boucle, os.path.join(arg.out, f"{f['id']}-boucle.mp4"))
                continue
            audio = os.path.join(RACINE, f["audio_url"])
            assembler(boucle, audio, os.path.join(arg.out, f"{f['id']}-10min.mp4"), tmp)
            print(f"   -> {f['id']}-10min.mp4", flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
