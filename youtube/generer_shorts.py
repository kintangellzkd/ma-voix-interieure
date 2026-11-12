#!/usr/bin/env python3
"""Shorts YouTube verticaux (1080x1920, 40 s), un par fréquence du catalogue.

Même boucle d'ondes que les vidéos de 10 min, cadrée en vertical ; l'audio
est un extrait de 40 s du fichier hz/ (fondus aux deux bouts).

Usage : python3 youtube/generer_shorts.py [hz-432 ...] [--out DOSSIER]
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw

import generer_videos as gv

W, H = 1080, 1920
DUREE = 40
DEBUT_AUDIO = 120            # on prend l'extrait au cœur du fichier


def calque_short(sc):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    f = sc.freq
    gv.centrer(dr, W, f"{f['hz']:g} Hz", gv.police("InterDisplay-ExtraLight.otf", 190), 230, gv.CREME + (240,))
    gv.centrer(dr, W, f["title"], gv.police("Inter-Light.otf", 62), 470, gv.CREME + (220,))
    gv.centrer(dr, W, f["wave"].upper() + "  ·  ÉCOUTEURS", gv.police("Inter-Regular.otf", 30),
               565, gv.OR + (210,), esp=4)
    gv.centrer(dr, W, "Version complète de 10 min", gv.police("Inter-Medium.otf", 40), H - 330, gv.CREME + (230,))
    gv.centrer(dr, W, "sur la chaîne", gv.police("Inter-Light.otf", 40), H - 275, gv.CREME + (200,))
    gv.centrer(dr, W, "MA VOIX INTÉRIEURE", gv.police("Inter-Medium.otf", 26), H - 190, gv.OR + (200,), esp=8)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--out", default=os.path.join(gv.RACINE, "youtube", "sortie", "shorts"))
    arg = ap.parse_args()
    freqs = json.load(open(os.path.join(gv.RACINE, "catalog.json"), encoding="utf-8"))["frequences"]
    if arg.ids:
        freqs = [f for f in freqs if f["id"] in arg.ids]
    os.makedirs(arg.out, exist_ok=True)
    for f in freqs:
        print(f"== short {f['id']}", flush=True)
        sc = gv.Scene(f, gv.TEINTES.get(int(f["hz"]), gv.OR), W, H, calque_short)
        tmp = tempfile.mkdtemp(prefix="short-")
        try:
            boucle = os.path.join(tmp, "boucle.mp4")
            gv.rendre_boucle(sc, boucle)
            subprocess.run([
                "ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", boucle,
                "-ss", str(DEBUT_AUDIO), "-t", str(DUREE), "-i", os.path.join(gv.RACINE, f["audio_url"]),
                "-map", "0:v", "-map", "1:a", "-t", str(DUREE),
                "-vf", f"fade=t=in:st=0:d=1,fade=t=out:st={DUREE - 2}:d=2",
                "-af", f"afade=t=in:st=0:d=1.5,afade=t=out:st={DUREE - 2.5}:d=2.5",
                *gv.X264, "-c:a", "aac", "-b:a", "160k",
                os.path.join(arg.out, f"{f['id']}-short.mp4")], check=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
