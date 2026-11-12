#!/usr/bin/env python3
"""Série « Moments » : vidéos calmes de 10 min pour des occasions précises.

Chaque moment reprend une fréquence du catalogue (audio hz/ inchangé) avec
son propre titre, sa teinte et, pour Noël, de la neige qui tombe.

Usage : python3 youtube/generer_moments.py [dormir noel ...] [--out DOSSIER]
"""
import argparse
import json
import os
import shutil
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import generer_videos as gv

MOMENTS = [
    dict(id="dormir", hz="hz-174", titre="Avant de dormir",
         sous_titre="Poser la journée, laisser le corps descendre",
         teinte=(96, 108, 178)),
    dict(id="moment-important", hz="hz-396", titre="Avant un moment important",
         sous_titre="Un examen, une entrevue, une conversation",
         teinte=(192, 154, 78)),
    dict(id="ceux-qui-manquent", hz="hz-639", titre="Pour ceux qui nous manquent",
         sous_titre="Un moment doux pour penser à eux",
         teinte=(196, 140, 158)),
    dict(id="noel", hz="hz-528", titre="Nuit de Noël",
         sous_titre="Le calme au milieu des fêtes",
         teinte=(206, 98, 86), neige=True),
    dict(id="nouvel-an", hz="hz-417", titre="Nouvel An",
         sous_titre="Fermer l'année, poser ses intentions",
         teinte=(222, 190, 122)),
]


def calque_moment(m):
    def calque(sc):
        W, H = sc.w, sc.h
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        f = sc.freq
        gv.centrer(dr, W, m["titre"], gv.police("InterDisplay-ExtraLight.otf", 104), H * 0.46 - 78, gv.CREME + (240,))
        gv.centrer(dr, W, m["sous_titre"], gv.police("Inter-Light.otf", 36), H * 0.46 + 60, gv.CREME + (200,))
        gv.centrer(dr, W, f"{f['hz']:g} HZ  ·  {f['wave'].upper()}  ·  ÉCOUTEURS RECOMMANDÉS",
                   gv.police("Inter-Regular.otf", 20), H - 118, gv.OR + (190,), esp=3)
        gv.centrer(dr, W, "MA VOIX INTÉRIEURE  ·  MOMENTS", gv.police("Inter-Medium.otf", 18),
                   H - 78, gv.CREME + (120,), esp=6)
        return img
    return calque


def miniature(sc, m, dst):
    rgb, al = sc.texte
    sc.texte = (rgb, al * 0)
    base = Image.fromarray((sc.image(gv.LOOP_S * 0.42) * 255).astype(np.uint8))
    sc.texte = (rgb, al)
    img = base.resize((1280, 720), Image.LANCZOS).convert("RGBA")
    calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(calque)
    taille = 132 if len(m["titre"]) <= 16 else 96
    gv.centrer(dr, 1280, m["titre"], gv.police("InterDisplay-Light.otf", taille), 230 if taille > 100 else 250,
               gv.CREME + (255,))
    gv.centrer(dr, 1280, f"{sc.freq['hz']:g} Hz  ·  10 min", gv.police("Inter-SemiBold.otf", 44), 440, gv.OR + (255,))
    ombre = calque.filter(ImageFilter.GaussianBlur(10))
    noir = Image.new("RGBA", img.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: int(v * 0.6)))
    img = Image.alpha_composite(Image.alpha_composite(img, noir), calque)
    img.convert("RGB").save(dst, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--out", default=os.path.join(gv.RACINE, "youtube", "sortie", "moments"))
    ap.add_argument("--apercu", action="store_true", help="miniatures seulement")
    arg = ap.parse_args()
    freqs = {f["id"]: f for f in json.load(open(os.path.join(gv.RACINE, "catalog.json"),
                                                 encoding="utf-8"))["frequences"]}
    os.makedirs(arg.out, exist_ok=True)
    for m in MOMENTS:
        if arg.ids and m["id"] not in arg.ids:
            continue
        print(f"== moment {m['id']}", flush=True)
        f = freqs[m["hz"]]
        sc = gv.Scene(f, m["teinte"], calque_texte=calque_moment(m), neige=m.get("neige", False))
        miniature(sc, m, os.path.join(arg.out, f"{m['id']}-miniature.jpg"))
        if arg.apercu:
            continue
        tmp = tempfile.mkdtemp(prefix="moment-")
        try:
            boucle = os.path.join(tmp, "boucle.mp4")
            gv.rendre_boucle(sc, boucle)
            gv.assembler(boucle, os.path.join(gv.RACINE, f["audio_url"]),
                         os.path.join(arg.out, f"{m['id']}-10min.mp4"), tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
