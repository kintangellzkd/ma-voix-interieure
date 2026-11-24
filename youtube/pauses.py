#!/usr/bin/env python3
"""Shorts « Pause » : courts messages pour s'arrêter et respirer, lus avec la voix
ElevenLabs de l'auteur, sur les images d'ambiance (neige, aurores, pluie) et un bol tibétain qui
résonne (au début, à chaque respiration, à la fin). Sans marque.

Chaque phrase est synthétisée séparément puis posée sur une ligne de temps avec de
vraies pauses ; pendant « Respire », un guide « inspire… / expire… » s'affiche.

Clé : variable ELEVENLABS_API_KEY (jamais dans le dépôt).
Usage : python3 youtube/pauses.py [1 2 ...]   (défaut : tous)
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import poemes
from poemes import SR, piste_voix, assembler

VOIX_ID = os.environ.get("ELEVENLABS_VOICE", "n7xHuG7KKUMlBjUY9h0K")   # « Christian Voix »
MODELE = "eleven_multilingual_v2"
REGLAGES = dict(stability=0.62, similarity_boost=0.85, style=0.12, use_speaker_boost=True, speed=0.9)
SORTIE = os.path.join(poemes.gv.RACINE, "youtube", "sortie", "pauses")

RESPIRE = "__respire__"   # pause guidée : inspire 3 s, expire 3,5 s

# (scène, [phrases]) ; RESPIRE insère une respiration guidée.
SCRIPTS = [
    ("pluie", ["Hé… stop.", "Rien ne presse.", "Tu peux prendre un moment pour toi.",
               "Respire.", RESPIRE, "Tu as le droit de t'arrêter deux secondes.",
               "Respire.", RESPIRE, "Bonne journée."]),
    ("neige", ["Tes épaules.", "Elles sont montées jusqu'à tes oreilles, hein ?",
               "Laisse-les redescendre.", "Respire.", RESPIRE, "Voilà.",
               "Juste ça, c'est déjà beaucoup.", "Bonne journée."]),
    ("aurores", ["Si tu lis ceci, c'est un signe.", "Pas un signe de l'univers…",
                 "juste un signe que tu peux ralentir.", "Respire.", RESPIRE,
                 "Ta liste peut attendre trente secondes.", "Respire encore.", RESPIRE,
                 "Allez. Bonne journée."]),
    ("pluie", ["Desserre ta mâchoire.", "Oui, toi.", "Laisse ta langue se poser.",
               "Respire.", RESPIRE, "Tu n'as rien à prouver, là, maintenant.",
               "Respire.", RESPIRE, "Bonne journée."]),
    ("neige", ["Ce que tu ressens en ce moment…", "c'est correct.",
               "Ça va passer, comme un nuage.", "Respire.", RESPIRE,
               "Tu n'es pas obligé de tout régler aujourd'hui.", "Respire.", RESPIRE,
               "Bonne journée."]),
    ("aurores", ["T'en fais beaucoup.", "Je le sais.", "Alors, pour les vingt prochaines secondes…",
                 "tu ne fais rien.", "Respire.", RESPIRE, "Rien d'autre.", "Respire.", RESPIRE,
                 "Bonne journée."]),
]

P_COURTE, P_LONGUE, INSPIRE, EXPIRE = 0.9, 1.6, 3.0, 3.5


def voix(texte):
    """Synthèse ElevenLabs (PCM 24 kHz), mise en cache, silences retirés."""
    cle = hashlib.sha1(json.dumps([VOIX_ID, MODELE, REGLAGES, texte]).encode()).hexdigest()[:16]
    cache = os.path.join(SORTIE, "tts", cle + ".wav")
    if not os.path.exists(cache):
        cle_api = os.environ["ELEVENLABS_API_KEY"]
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOIX_ID}?output_format=pcm_24000",
            data=json.dumps(dict(text=texte, model_id=MODELE, language_code="fr",
                                 voice_settings=REGLAGES)).encode(),
            headers={"xi-api-key": cle_api, "Content-Type": "application/json"})
        pcm = urllib.request.urlopen(req, timeout=120).read()
        a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        sf.write(cache, a, SR)
    a, _ = sf.read(cache, dtype="float32")
    fort = np.where(np.abs(a) > 0.01)[0]
    if len(fort):
        a = a[max(0, fort[0] - 600): fort[-1] + 2400]
    return a


def calque(W, H, kind, txt, grand=False):
    """Texte large pour mobile ; « inspire/expire » avec un cercle de respiration."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    f = ImageFont.truetype(poemes.SERIF, 96 if kind == "strophe" else 84)
    mots, lignes = txt.split(), [""]
    for m in mots:                                   # retour à la ligne automatique
        essai = (lignes[-1] + " " + m).strip()
        if dr.textlength(essai, font=f) > W * 0.82 and lignes[-1]:
            lignes.append(m)
        else:
            lignes[-1] = essai
    pas = int(f.size * 1.4)
    y = H * 0.42 - pas * len(lignes) / 2
    for l in lignes:
        poemes.gv.centrer(dr, W, l, f, y, poemes.gv.CREME + (245,))
        y += pas
    if kind == "fin":
        r = 210 if txt.startswith("inspire") else 150
        cx, cy = W / 2, H * 0.62
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=poemes.gv.CREME + (170,), width=4)
    ombre = img.filter(ImageFilter.GaussianBlur(16))
    noir = Image.new("RGBA", img.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: int(v * 0.8)))
    return Image.alpha_composite(noir, img)


poemes.calque = calque          # utilisé par poemes.assembler


def construire(phrases):
    """Ligne de temps : voix, écrans, et instants des coups de bol (force)."""
    morceaux, ecrans, coups, t = [], [], [(0.2, 1.0)], 3.2
    for i, p in enumerate(phrases):
        if p == RESPIRE:
            coups.append((t - 0.1, 0.55))
            ecrans.append((t, t + INSPIRE, "fin", "inspire…"))
            ecrans.append((t + INSPIRE, t + INSPIRE + EXPIRE, "fin", "expire…"))
            t += INSPIRE + EXPIRE + 0.6
            continue
        a = voix(p)
        morceaux.append((t, a))
        d = len(a) / SR
        fin = p.endswith(("…", ".", "?", "!"))
        ecrans.append((t - 0.3, t + d + (1.0 if fin else 0.6), "strophe", p))
        t += d + (P_LONGUE if fin else P_COURTE)
    coups.append((t - 0.6, 0.9))
    return morceaux, ecrans, coups, t + 7.0


def bol_tibetain(duree, coups, dst, f0=196.0):
    """Bol tibétain synthétisé : partiels inharmoniques en doublets (battements
    lents), longue résonance, léger choc du maillet. Rien d'autre."""
    sr = 48000
    n = int(duree * sr)
    t = np.arange(n, dtype=np.float32) / sr
    rng = np.random.default_rng(5)
    partiels = ((1.0, 1.0, 9.0, 0.9), (2.71, 0.55, 6.0, 1.6), (5.15, 0.25, 3.5, 2.4),
                (8.15, 0.10, 2.0, 3.1), (11.7, 0.05, 1.2, 4.0))
    sortie = np.zeros((n, 2), np.float32)
    for t0, force in coups:
        i0 = int(max(t0, 0) * sr)
        k = t[: n - i0]
        x = np.zeros((len(k), 2), np.float32)
        for r, a, tau, bat in partiels:
            f = f0 * r
            for c, sgn in enumerate((-1, 1)):
                ph = rng.uniform(0, 2 * np.pi)
                # doublet : deux modes proches -> battement « wah-wah » typique du bol
                v = np.sin(2 * np.pi * (f - bat / 2) * k + ph) + 0.8 * np.sin(2 * np.pi * (f + bat / 2) * k + ph + sgn)
                x[:, c] += a * v * np.exp(-k / tau)
        choc = rng.standard_normal(min(len(k), int(0.03 * sr))).astype(np.float32)
        choc *= np.exp(-np.arange(len(choc)) / (0.004 * sr)) * 0.15
        x[: len(choc)] += choc[:, None]
        x *= np.clip(k / 0.003, 0, 1)[:, None]
        sortie[i0:] += force * x
    sortie *= 0.32 / (np.abs(sortie).max() + 1e-9)
    sortie *= np.clip((duree - t) / 2.5, 0, 1)[:, None]
    sf.write(dst, sortie, sr)


def short(k):
    scene, phrases = SCRIPTS[k - 1]
    morceaux, ecrans, coups, t = construire(phrases)
    total = round(t)
    tmp = tempfile.mkdtemp(prefix="pause-")
    try:
        w = os.path.join(tmp, "voix.wav")
        piste_voix(morceaux, total, w)
        dst = os.path.join(SORTIE, f"pause-{k}.mp4")
        brut = os.path.join(tmp, "brut.mp4")
        assembler(scene, ecrans, w, total, brut, tmp, vertical=True, vbit="1800k")
        fond = os.path.join(tmp, "fond.wav")
        bol_tibetain(total, coups, fond)
        audio = ("[1:a]aresample=48000,highpass=f=70,aecho=0.8:0.6:45|95:0.18|0.10,"
                 "aformat=channel_layouts=stereo[vx];[vx][2:a]amix=inputs=2:normalize=0,"
                 "loudnorm=I=-16:TP=-1.5:LRA=11[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", brut, "-i", w, "-i", fond, "-map", "0:v",
                        "-c:v", "copy", "-filter_complex", audio, "-map", "[a]", "-t", str(total),
                        "-ar", "48000",
                        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", dst], check=True)
        print("->", dst, f"{total}s", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    for k in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else range(1, len(SCRIPTS) + 1)):
        short(k)
