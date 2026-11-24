"""Fonds animés verticaux pour les Shorts « Pause », un par message.

Rendus en 540x960 (doux, sans détail fin) puis agrandis en 1080x1920 par ffmpeg.
Chaque scène : image(t, duree, b) -> tableau float32 HxWx3 dans [0, 1], où b (0..1)
est le souffle : 1 = poumons pleins. L'image respire avec le guide.
"""
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 540, 960, 30
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)


def degrade(haut, bas, courbe=1.0, h=H):
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None] ** courbe
    c = np.float32(haut) / 255 * (1 - t) + np.float32(bas) / 255 * t
    return np.repeat(c, W, axis=1)


def halo(img, cx, cy, r, coul, force):
    img += np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / r ** 2)[..., None] * np.float32(coul) / 255 * force


def bruit_periodique(rng, h, w, sigma, ratio=1.0):
    b = rng.standard_normal((h, w))
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    f = np.exp(-(fx ** 2 * (w / sigma) ** 2 + fy ** 2 * (h / sigma * ratio) ** 2))
    t = np.real(np.fft.ifft2(np.fft.fft2(b) * f))
    return ((t - t.min()) / (t.max() - t.min())).astype(np.float32)


def vers_np(pil):
    return np.asarray(pil, np.float32)[..., :3] / 255


# 1 -------------------------------------------------------------- lever de soleil
class Lever:
    def __init__(self):
        rng = np.random.default_rng(1)
        self.hor = int(H * 0.60)
        xs = np.arange(W)
        m = sum(rng.uniform(6, 22) * np.sin(xs / W * np.pi * k + rng.uniform(0, 6)) for k in (1, 2.3, 4.1))
        self.crete = (self.hor - 28 - m).astype(np.int32)
        self.ondes = bruit_periodique(rng, H, W, 40, ratio=0.15)

    def image(self, t, d, b=0.0):
        p = t / d
        chaud = 0.55 + 0.45 * p
        ciel = degrade((30, 40, 80), (int(240 * chaud), int(150 * chaud + 40), int(110 * chaud)), 1.6,
                       h=self.hor)
        img = np.zeros((H, W, 3), np.float32)
        img[: self.hor] = ciel
        sy = self.hor - 10 - 200 * p - 70 * b              # le soleil monte, et plus encore à l'inspiration
        halo(img, W / 2, sy, 160 + 110 * b, (255, 170, 90), 0.55 + 0.45 * b)
        disque = np.clip(42 - np.hypot(X - W / 2, Y - sy), 0, 1.5)[..., None] / 1.5
        img = img * (1 - disque) + disque * np.float32([1.0, 0.86, 0.62])
        for x in range(W):                                  # montagnes au loin
            img[self.crete[x]: self.hor, x] = np.float32([0.16, 0.12, 0.16]) * (0.8 + 0.4 * p)
        # eau : reflet du ciel, assombri, avec une colonne de soleil qui scintille
        ref = img[self.hor - 1:: -1][: H - self.hor] * 0.55
        ond = np.roll(self.ondes, int(t * 20), axis=0)[: H - self.hor]
        col = np.exp(-((X[: H - self.hor] - W / 2) / (40 + 0.25 * Y[: H - self.hor])) ** 2)
        scint = col * np.clip(ond * 2.2 - 0.9, 0, 1) * (0.9 + 0.6 * b)
        img[self.hor:] = ref + scint[..., None] * np.float32([1.0, 0.8, 0.55])
        return np.clip(img * 0.85, 0, 1)


# 2 -------------------------------------------------------------- plume
class Plume:
    def __init__(self):
        rng = np.random.default_rng(2)
        L = 300
        im = Image.new("RGBA", (160, L + 20), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        pts = [(80 + 10 * np.sin(i / L * 2.5), 10 + i) for i in range(L)]
        for i in range(20, L - 10, 3):
            x, y = pts[i]
            larg = 62 * np.sin(np.pi * (i - 20) / (L - 30)) ** 0.7
            for s in (-1, 1):
                dr.line([(x, y), (x + s * larg, y - 34 + rng.uniform(-4, 4))], fill=(245, 240, 235, 150), width=2)
        dr.line(pts, fill=(250, 248, 240, 230), width=3)
        self.plume = im.filter(ImageFilter.GaussianBlur(0.8))
        self.bokeh = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(20, 60), rng.uniform(0.08, 0.2))
                      for _ in range(18)]

    def image(self, t, d, b=0.0):
        img = degrade((70, 60, 105), (175, 135, 150), 0.9)
        for bx, by, r, a in self.bokeh:
            halo(img, bx, (by - t * 8) % H, r * (1 + 0.4 * b), (255, 225, 230), a * (1 + b))
        base = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
        ang = 25 * np.sin(t * 0.7)
        pl = self.plume.rotate(ang + 20, resample=Image.BICUBIC, expand=True)
        x = W / 2 + 90 * np.sin(t * 0.55) - pl.width / 2
        y = -60 + (H * 0.55) * t / d - 180 * b
        base.alpha_composite(pl, (int(x), int(y)))
        return np.clip(vers_np(base) * 0.85, 0, 1)


# 3 -------------------------------------------------------------- sablier
class Sablier:
    def image(self, t, d, b=0.0):
        img = degrade((30, 24, 22), (70, 50, 38))
        halo(img, W * 0.5, H * 0.80, 220 + 160 * b, (255, 190, 130), 0.25 + 0.55 * b)
        base = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        dr = ImageDraw.Draw(base, "RGBA")
        cx, haut, bas, lg = W / 2, H * 0.64, H * 0.95, 120
        mil = (haut + bas) / 2
        p = 0.15 + 0.7 * t / d
        # sable du haut (triangle qui se vide) et du bas (tas qui monte)
        hs = (mil - haut - 12) * (1 - p)
        k = hs / (mil - haut)
        dr.polygon([(cx - lg * k, mil - hs - 6), (cx + lg * k, mil - hs - 6), (cx, mil - 6)], fill=(215, 175, 115))
        hb = (bas - mil - 14) * p
        dr.polygon([(cx - lg + 8, bas - 8), (cx + lg - 8, bas - 8), (cx + lg * 0.25, bas - 8 - hb),
                    (cx - lg * 0.25, bas - 8 - hb)], fill=(215, 175, 115))
        fl = 1 + 0.5 * np.sin(t * 40)
        dr.line([(cx, mil - 6), (cx, bas - 8 - hb)], fill=(225, 185, 125, 200), width=int(2 + fl))
        verre = [(cx - lg, haut), (cx + lg, haut), (cx + 8, mil), (cx + lg, bas), (cx - lg, bas), (cx - 8, mil)]
        dr.line(verre + [verre[0]], fill=(240, 225, 210, 150), width=3)
        for yy in (haut - 10, bas + 10):
            dr.rounded_rectangle([cx - lg - 22, yy - 9, cx + lg + 22, yy + 9], 5, fill=(95, 62, 40))
        return np.clip(vers_np(base) * 0.95, 0, 1)


# 4 -------------------------------------------------------------- ronds dans l'eau
class Ronds:
    def __init__(self):
        rng = np.random.default_rng(4)
        self.gouttes = [(t0, rng.uniform(0.2, 0.8) * W, rng.uniform(0.55, 0.9) * H)
                        for t0 in np.arange(0.5, 80, 4.5) + rng.uniform(0, 1.5, 18)]
        self.caust = bruit_periodique(rng, H, W, 8)

    def image(self, t, d, b=0.0):
        img = degrade((18, 52, 66), (8, 26, 36))
        c = np.roll(self.caust, (int(t * 6), int(t * 4)), axis=(0, 1))
        img += (np.clip(c * 2 - 1.0, 0, 1) * 0.06)[..., None] * np.float32([0.6, 0.9, 1.0])
        for t0, gx, gy in self.gouttes:
            a = t - t0
            if a < 0 or a > 9:
                continue
            dist = np.hypot(X - gx, (Y - gy) * 1.9)          # légère perspective
            for j in range(3):
                r = a * 55 - j * 28
                if r <= 0:
                    continue
                img += (np.exp(-((dist - r) / 5) ** 2) * 0.5 * np.exp(-a / 3.5) * (1 - 0.25 * j))[..., None] \
                    * np.float32([0.8, 0.95, 1.0])
        if b > 0.01:
            dist = np.hypot(X - W / 2, (Y - H * 0.70) * 1.9)
            for j, k in enumerate((1.0, 0.82, 0.64)):
                r = 30 + 230 * b * k
                img += (np.exp(-((dist - r) / 7) ** 2) * 0.55 * b * (1 - 0.25 * j))[..., None] \
                    * np.float32([0.85, 0.97, 1.0])
        return np.clip(img, 0, 1)


# 5 -------------------------------------------------------------- nuages
class Nuages:
    def __init__(self):
        rng = np.random.default_rng(5)
        self.n1 = bruit_periodique(rng, H, W * 2, 9, ratio=0.45)
        self.n2 = bruit_periodique(rng, H, W * 2, 4, ratio=0.45)

    def image(self, t, d, b=0.0):
        img = degrade((55, 105, 170), (165, 195, 225), 1.2)
        n = 0.6 * np.roll(self.n1, int(t * 14), axis=1)[:, :W] + 0.4 * np.roll(self.n2, int(t * 7), axis=1)[:, :W]
        a = np.clip((n - 0.5) * 3.5, 0, 1)[..., None]
        ombre = np.clip((n - 0.68) * 3, 0, 1)[..., None]
        nuage = np.float32([0.97, 0.97, 1.0]) * (1 - 0.25 * ombre)
        halo(img, W * 0.5, H * 0.14, 100 + 110 * b, (255, 230, 180), 0.55 * b)
        a = a * (1 - 0.45 * b)
        img = img * (1 - a) + nuage * a
        bande = 1 - 0.45 * np.exp(-((Y - H * 0.42) / 150) ** 2) - 0.3 * np.exp(-((Y - H * 0.62) / 120) ** 2)
        return np.clip(img * (0.78 + 0.14 * b) * bande[..., None], 0, 1)


# 6 -------------------------------------------------------------- tasse fumante
class Tasse:
    def __init__(self):
        self.rng = np.random.default_rng(6)
        self.vols = [(self.rng.uniform(0, 6), self.rng.uniform(-30, 30)) for _ in range(4)]

    def image(self, t, d, b=0.0):
        img = degrade((32, 24, 20), (78, 52, 36))
        halo(img, W * 0.85, H * 0.15, 300, (255, 200, 140), 0.22)
        halo(img, W * 0.5, H * 0.86, 230 + 120 * b, (255, 180, 110), 0.18 + 0.3 * b)
        base = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
        cx, top = W / 2, H * 0.80
        vap = Image.new("L", (W, H), 0)
        dv = ImageDraw.Draw(vap)
        for ph, dx in self.vols:
            pts = []
            ht = H * (0.58 - 0.22 * b)
            for yy in np.arange(top - 10, ht, -6):
                hgt = (top - yy) / (top - ht)
                x = cx + dx * (1 - hgt) + 28 * hgt * np.sin(yy * 0.025 + t * 1.3 + ph)
                pts.append((x, yy))
            for i in range(len(pts) - 1):
                a = int((140 + 100 * b) * (1 - i / len(pts)) * min(1, i / 4 + 0.2))
                dv.line([pts[i], pts[i + 1]], fill=a, width=10)
        vap = vap.filter(ImageFilter.GaussianBlur(9))
        blanc = Image.new("RGBA", (W, H), (245, 235, 225, 0))
        blanc.putalpha(vap)
        base.alpha_composite(blanc)
        dr = ImageDraw.Draw(base)
        dr.ellipse([cx - 175, H * 0.955 - 18, cx + 175, H * 0.955 + 18], fill=(30, 20, 16))     # soucoupe
        dr.rounded_rectangle([cx - 115, top, cx + 115, H * 0.95], 40, fill=(222, 210, 195))   # tasse
        dr.ellipse([cx + 92, top + 30, cx + 168, top + 110], outline=(222, 210, 195), width=14)
        dr.ellipse([cx - 115, top - 18, cx + 115, top + 18], fill=(205, 192, 178))
        dr.ellipse([cx - 102, top - 12, cx + 102, top + 12], fill=(95, 55, 30))                 # thé
        return np.clip(vers_np(base) * 0.92, 0, 1)


SCENES = {"lever": Lever, "plume": Plume, "sablier": Sablier, "ronds": Ronds, "nuages": Nuages,
          "tasse": Tasse}


def rendre(nom, duree, dst, souffle=lambda t: 0.0):
    sc = SCENES[nom]()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-vf", "scale=1080:1920:flags=bicubic", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "16", "-pix_fmt", "yuv420p", "-an", dst], stdin=subprocess.PIPE)
    for k in range(int(duree * FPS)):
        p.stdin.write((sc.image(k / FPS, duree, souffle(k / FPS)) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg a échoué")


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    planche = Image.new("RGB", (W * 6 // 2, H // 2))
    for i, nom in enumerate(SCENES):
        im = SCENES[nom]().image(20, 40)
        planche.paste(Image.fromarray((im * 255).astype(np.uint8)).resize((W // 2, H // 2)), (i * W // 2, 0))
    planche.save(f"{out}/fonds-pause.jpg", quality=88)
