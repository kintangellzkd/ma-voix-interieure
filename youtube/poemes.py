#!/usr/bin/env python3
"""Série « Poèmes pour s'endormir » : poèmes originaux lus d'une voix douce
sur les ambiances (neige, aurores, pluie), sans aucune marque.

- Vidéo longue 16:9 : le recueil (4 poèmes) puis l'ambiance seule jusqu'à la fin.
- Shorts 9:16 : un poème par Short.

Voix : Kokoro (ONNX, voix ff_siwis), modèle dans $KOKORO_DIR (défaut /home/user/tts).
Les boucles vidéo viennent de sortie/ambiances/{scene}-boucle.mp4 (ambiances.py).

Usage : python3 youtube/poemes.py neige aurores pluie [--minutes 20] [--shorts] [--apercu]
"""
import argparse
import hashlib
import os
import re
import subprocess
import tempfile
import shutil

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import ambiances as amb
import sons
import generer_videos as gv
from textes_poemes import RECUEILS

SR = 24000
KOKORO_DIR = os.environ.get("KOKORO_DIR", "/home/user/tts")
SORTIE = os.path.join(gv.RACINE, "youtube", "sortie", "poemes")
SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"
VITESSE = 0.8

# Rythme de lecture (secondes)
P_PHRASE, P_STROPHE, P_TITRE, P_POEME, INTRO = 1.2, 2.8, 2.4, 16.0, 9.0

_tts = None


def voix(texte):
    """Synthèse d'une phrase, mise en cache, silences de bord retirés."""
    global _tts
    cache = os.path.join(SORTIE, "tts")
    os.makedirs(cache, exist_ok=True)
    cle = hashlib.sha1(f"{VITESSE}|{texte}".encode()).hexdigest()[:16]
    f = os.path.join(cache, cle + ".wav")
    if not os.path.exists(f):
        if _tts is None:
            from kokoro_onnx import Kokoro
            _tts = Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"),
                          os.path.join(KOKORO_DIR, "voices-v1.0.bin"))
        s, sr = _tts.create(texte, voice="ff_siwis", speed=VITESSE, lang="fr-fr")
        assert sr == SR
        sf.write(f, s, SR)
    s, _ = sf.read(f, dtype="float32")
    idx = np.where(np.abs(s) > 0.01)[0]
    return s[max(idx[0] - 600, 0): idx[-1] + 2400] if len(idx) else s


def phrases(strophe):
    """Découpe une strophe en phrases ; un saut de ligne sans ponctuation devient une virgule."""
    lignes = strophe.split("\n")
    txt = " ".join(l if re.search(r"[.,;:!?]$", l) or i == len(lignes) - 1 else l + ","
                   for i, l in enumerate(lignes))
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", txt) if p.strip()]


def lire_poeme(titre, strophes, t0, morceaux, ecrans):
    """Ajoute la lecture d'un poème à partir de t0 ; renvoie l'instant de fin."""
    t = t0
    a = voix(titre + ".")
    morceaux.append((t, a))
    ecrans.append((t - 1.0, t + len(a) / SR + P_TITRE - 0.4, "titre", titre))
    t += len(a) / SR + P_TITRE
    for st in strophes:
        debut = t
        for ph in phrases(st):
            a = voix(ph)
            morceaux.append((t, a))
            t += len(a) / SR + P_PHRASE
        t += P_STROPHE - P_PHRASE
        ecrans.append((debut - 0.8, t - 0.6, "strophe", st))
    return t


def piste_voix(morceaux, duree, dst):
    v = np.zeros(int(duree * SR) + SR, np.float32)
    for t, a in morceaux:
        i = int(t * SR)
        v[i:i + len(a)] += a[: len(v) - i]
    v *= 0.85 / max(np.abs(v).max(), 1e-6)
    sf.write(dst, v, SR)


# ---------- images de texte ----------

def calque(W, H, kind, txt, grand=False):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    k = 1.35 if grand else 1.0
    if kind == "strophe":
        f = ImageFont.truetype(SERIF, int(58 * k))
        lignes = txt.split("\n")
        pas = int(58 * k * 1.55)
        y = H / 2 - pas * len(lignes) / 2
        for l in lignes:
            gv.centrer(dr, W, l, f, y, gv.CREME + (245,))
            y += pas
    elif kind == "titre":
        gv.centrer(dr, W, txt, gv.police("InterDisplay-Light.otf", int(64 * k)), H / 2 - 50 * k, gv.CREME + (240,))
        dr.line([(W / 2 - 40 * k, H / 2 + 50 * k), (W / 2 + 40 * k, H / 2 + 50 * k)], fill=gv.OR + (200,), width=2)
    elif kind == "recueil":
        titre, sous = txt
        gv.centrer(dr, W, titre, gv.police("InterDisplay-ExtraLight.otf", int(92 * k)), H / 2 - 90 * k, gv.CREME + (245,))
        gv.centrer(dr, W, sous, ImageFont.truetype(SERIF, int(54 * k)), H / 2 + 30 * k, gv.CREME + (220,))
    elif kind == "fin":
        gv.centrer(dr, W, txt, ImageFont.truetype(SERIF, int(52 * k)), H / 2 - 30 * k, gv.CREME + (220,))
    ombre = img.filter(ImageFilter.GaussianBlur(14))
    noir = Image.new("RGBA", img.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: int(v * 0.75)))
    return Image.alpha_composite(noir, img)


# ---------- assemblage ----------

def assembler(scene, ecrans, voix_wav, total, dst, tmp, vertical=False, vbit="480k"):
    W, H = (1080, 1920) if vertical else (1920, 1080)
    boucle = os.path.join(gv.RACINE, "youtube", "sortie", "ambiances", f"{scene}-boucle.mp4")
    if not os.path.exists(boucle):
        sc = amb.SCENES[scene]()
        amb.rendre(sc, boucle)
    entrees = ["-stream_loop", "-1", "-i", boucle, "-i", voix_wav]
    wav = sons.fichier(scene, total, os.path.join(SORTIE, "sons"))
    if wav:
        entrees += ["-i", wav]
    base = 3 if wav else 2
    fond = "crop=608:1080,scale=1080:1920:flags=lanczos," if vertical else ""
    graphe = [f"[0:v]{fond}trim=0:{total},setpts=PTS-STARTPTS,"
              f"fade=t=in:st=0:d=4,fade=t=out:st={total - 6}:d=6[b0]"]
    for i, (a, b, kind, txt) in enumerate(ecrans):
        a = max(a, 0.5)
        d = b - a
        png = os.path.join(tmp, f"e{i}.png")
        calque(W, H, kind, txt, grand=vertical).save(png)
        entrees += ["-loop", "1", "-framerate", "30", "-t", f"{d:.2f}", "-i", png]
        n = i + base
        fi = min(1.2, d / 3)
        graphe.append(f"[{n}:v]format=rgba,fade=t=in:st=0:d={fi}:alpha=1,"
                      f"fade=t=out:st={d - 1.4:.2f}:d=1.4:alpha=1,setpts=PTS+{a:.2f}/TB[t{i}]")
        graphe.append(f"[b{i}][t{i}]overlay=eof_action=pass:format=auto[b{i + 1}]")
    graphe.append(f"[b{len(ecrans)}]format=yuv420p[v]")
    son = "[2:a]anull" if wav else amb.SCENES[scene].audio
    graphe.append(f"{son},atrim=0:{total},volume=0.55,aformat=channel_layouts=stereo[amb]")
    graphe.append("[1:a]aresample=48000,highpass=f=70,lowpass=f=9000,"
                  "aecho=0.8:0.6:45|95:0.18|0.10,volume=1.15,"
                  f"apad,atrim=0:{total},aformat=channel_layouts=stereo[vx]")
    graphe.append(f"[amb][vx]amix=inputs=2:normalize=0,"
                  f"afade=t=in:st=0:d=4,afade=t=out:st={total - 6}:d=6[a]")
    script = os.path.join(tmp, "graphe.txt")
    open(script, "w").write(";\n".join(graphe))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entrees, "-filter_complex_script", script,
                    "-map", "[v]", "-map", "[a]", "-t", str(total),
                    "-c:v", "libx264", "-preset", "medium", "-b:v", vbit, "-maxrate", "1500k",
                    "-bufsize", "3000k", "-g", "60", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", dst], check=True)


def video_longue(nom, minutes):
    r = RECUEILS[nom]
    morceaux, ecrans = [], [(1.0, INTRO - 0.5, "recueil", (r["titre"], r["sous_titre"]))]
    t = INTRO + 1.5
    for titre, strophes in r["poemes"]:
        t = lire_poeme(titre, strophes, t, morceaux, ecrans) + P_POEME
    ecrans.append((t - P_POEME + 4, t + 6, "fin", "Bonne nuit."))
    print(f"   lecture : {t / 60:.1f} min", flush=True)
    total = minutes * 60
    tmp = tempfile.mkdtemp(prefix="poeme-")
    try:
        w = os.path.join(tmp, "voix.wav")
        piste_voix(morceaux, total, w)
        dst = os.path.join(SORTIE, f"poemes-{nom}-{minutes}min.mp4")
        assembler(r["scene"], ecrans, w, total, dst, tmp)
        print("  ->", dst, f"{os.path.getsize(dst) / 1e6:.0f} Mo", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def shorts(nom):
    r = RECUEILS[nom]
    for k, (titre, strophes) in enumerate(r["poemes"], 1):
        morceaux, ecrans = [], []
        t = lire_poeme(titre, strophes, 2.0, morceaux, ecrans)
        total = round(t + 4)
        tmp = tempfile.mkdtemp(prefix="pshort-")
        try:
            w = os.path.join(tmp, "voix.wav")
            piste_voix(morceaux, total, w)
            dst = os.path.join(SORTIE, "shorts", f"poeme-{nom}-{k}.mp4")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            assembler(r["scene"], ecrans, w, total, dst, tmp, vertical=True, vbit="1800k")
            print("  ->", dst, f"{total}s", flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def miniature(nom, dst):
    r = RECUEILS[nom]
    sc = amb.SCENES[r["scene"]]()
    img = Image.fromarray((sc.image(amb.LOOP_S * 0.3) * 255).astype(np.uint8))
    img = img.resize((1280, 720), Image.LANCZOS).convert("RGBA")
    c = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(c)
    gv.centrer(dr, 1280, "Poèmes", gv.police("InterDisplay-Light.otf", 140), 170, gv.CREME + (255,))
    gv.centrer(dr, 1280, "pour s'endormir", ImageFont.truetype(SERIF, 76), 330, gv.CREME + (250,))
    gv.centrer(dr, 1280, r["sous_titre"].upper() + "  ·  VOIX DOUCE", gv.police("Inter-SemiBold.otf", 34),
               470, gv.OR + (255,), esp=4)
    ombre = c.filter(ImageFilter.GaussianBlur(12))
    noir = Image.new("RGBA", img.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: int(v * 0.75)))
    Image.alpha_composite(Image.alpha_composite(img, noir), c).convert("RGB").save(dst, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("noms", nargs="*", default=list(RECUEILS))
    ap.add_argument("--minutes", type=int, default=20)
    ap.add_argument("--shorts", action="store_true")
    ap.add_argument("--apercu", action="store_true", help="miniatures + voix seulement")
    arg = ap.parse_args()
    os.makedirs(SORTIE, exist_ok=True)
    for nom in arg.noms:
        print(f"== {nom}", flush=True)
        miniature(nom, os.path.join(SORTIE, f"poemes-{nom}-miniature.jpg"))
        if arg.apercu:
            for titre, strophes in RECUEILS[nom]["poemes"]:
                voix(titre + ".")
                for st in strophes:
                    for ph in phrases(st):
                        voix(ph)
            continue
        if arg.shorts:
            shorts(nom)
        else:
            video_longue(nom, arg.minutes)


if __name__ == "__main__":
    main()
