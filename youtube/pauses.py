#!/usr/bin/env python3
"""Shorts « Pause » : courts messages pour s'arrêter et respirer, lus avec la voix
ElevenLabs « Aurore » (celle des méditations), sur un fond animé propre à chaque
message (fonds_pause.py) et un bol tibétain qui résonne (au début, à chaque
respiration, à la fin). Sans marque.

Chaque phrase est synthétisée séparément puis posée sur une ligne de temps avec de
vraies pauses ; pendant « Respire », un guide « inspire… / expire… » s'affiche.

Clé : variable ELEVENLABS_API_KEY (jamais dans le dépôt).
Usage : python3 youtube/pauses.py [1 2 ...]   (défaut : tous)
"""
import hashlib
import io
import re
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
from poemes import SR, piste_voix
import fonds_pause

VOIX_ID = os.environ.get("ELEVENLABS_VOICE", "ucMmKRQbfDEYyb2IIGax")   # « Aurore - Calm & Warm »
MODELE = "eleven_v3"                     # accepte des indications de ton : [smiling], [warmly]…
REGLAGES = dict(stability=0.5, similarity_boost=0.8, use_speaker_boost=True)
SORTIE = os.path.join(poemes.gv.RACINE, "youtube", "sortie", "pauses")

# Script : phrases (avec indications de ton entre crochets, non affichées) et
# respirations ("IN", secondes) / ("OUT", secondes). Une phrase « Respire… » ou
# « Expire… » juste avant devient le guide de respiration à l'écran.
IN, OUT = (lambda s=3.0: ("IN", s)), (lambda s=3.5: ("OUT", s))
PAUSE = lambda s: ("PAUSE", s)          # silence voulu
SCRIPTS = [
    ("lever", ["[warmly] Hey ! Arrête-toi deux secondes.", "[smiling] Prends ce moment pour toi.",
               "[softly] Respire…", IN(2.0), "[warmly] Ça va aller. Ça va passer. C'est correct.",
               "[softly] Expire…", OUT(), "[smiling] Bonne journée !"]),
    ("plume", ["[playfully] Psst… tes épaules sont collées à tes oreilles.",
               "[laughs softly] On les descend ?", "[softly] Respire…", IN(), "[softly] Expire…", OUT(),
               "[smiling] Ahh, c'est mieux. Bonne journée !"]),
    ("sablier", ["[cheerfully] Hey ! Ta liste peut attendre dix secondes. Promis.",
                 "[softly] Respire…", IN(), "[softly] Expire…", OUT(),
                 "[smiling] Tu vois ? Le monde tourne encore. Bonne journée !"]),
    ("ronds", ["[playfully] Petit test : desserre ta mâchoire.", "[chuckles] T'étais crispé, hein ?",
               "[softly] Respire…", IN(), "[softly] Expire…", OUT(), "[smiling] Parfait. Bonne journée !"]),
    ("nuages", ["[warmly] Hey… ce que tu ressens là, c'est correct.", "[softly] Respire…", IN(2.0),
                "[warmly] Ça va passer, comme un nuage.", "[softly] Expire…", OUT(),
                "[smiling] Bonne journée !"]),
    ("tasse", ["[cheerfully] Pause café… sans le café !", PAUSE(1.8), "[warmly] Juste toi, deux secondes.",
               "[softly] Respire…", IN(), "[softly] Expire…", OUT(),
               "[smiling] Bon, tu peux y retourner. Bonne journée !"]),
]

P_PHRASE = 1.3          # silence entre deux phrases
P_AVANT_RESPIRE = 0.8   # silence supplémentaire avant « Respire… »
TEMPO = 0.88            # voix ralentie (hauteur conservée)


def affiche(texte):
    return re.sub(r"\[[^\]]*\]\s*", "", texte).strip()


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
    lent = cache.replace(".wav", f"-t{TEMPO}.wav")
    if not os.path.exists(lent):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cache, "-af", f"atempo={TEMPO}", lent], check=True)
    a, _ = sf.read(lent, dtype="float32")
    fort = np.where(np.abs(a) > 0.01)[0]
    if len(fort):
        a = a[max(0, fort[0] - 600): fort[-1] + 2400]
    return a


def calque(W, H, kind, txt, grand=False):
    """Texte large pour mobile (phrases et guide « inspire… / expire… »)."""
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
    ombre = img.filter(ImageFilter.GaussianBlur(22))
    noir = Image.new("RGBA", img.size, (0, 0, 0, 0))
    noir.putalpha(ombre.getchannel("A").point(lambda v: min(255, int(v * 1.6))))
    return Image.alpha_composite(noir, img)




def construire(script):
    """Ligne de temps : voix, écrans, et instants des coups de bol (force)."""
    morceaux, ecrans, coups, t = [], [], [(0.2, 1.0)], 2.2
    guide = None                                   # début du « Respire… » / « Expire… » parlé
    for p in script:
        if isinstance(p, tuple) and p[0] == "PAUSE":
            t += p[1]
            continue
        if isinstance(p, tuple):
            kind, d = p
            debut = guide if guide is not None else t
            if kind == "IN":
                coups.append((debut - 0.1, 0.5))
            ecrans.append((debut, t + d, "fin", "inspire…" if kind == "IN" else "expire…"))
            t += d
            guide = None
            continue
        tags = re.match(r"(\s*\[[^\]]*\]\s*)*", p).group(0).strip()
        bouts = re.split(r"(?<=[.!?])\s+", affiche(p))      # une phrase à la fois : débit posé
        if len(bouts) > 1:
            for k, bout in enumerate(bouts):
                a = voix(f"[calmly] {tags} {bout}".strip())
                morceaux.append((t, a))
                d = len(a) / SR
                ecrans.append((t - 0.2, t + d + 0.8, "strophe", bout))
                t += d + P_PHRASE
            continue
        a = voix(f"[calmly] {p}")
        morceaux.append((t, a))
        d = len(a) / SR
        txt = affiche(p)
        if txt.lower().rstrip("….") == "respire" and morceaux[:-1]:
            # un temps avant « Respire… » : on décale cette phrase
            t += P_AVANT_RESPIRE
            morceaux[-1] = (t, a)
        if txt.lower().rstrip("….") in ("respire", "expire"):
            guide = t
        else:
            # pendant une inspiration en cours, la phrase s'affiche par-dessus le cercle
            ecrans.append((t - 0.2, t + d + 0.8, "strophe", txt))
        t += d + P_PHRASE
    coups.append((t - 0.3, 0.9))
    return morceaux, ecrans, coups, t + 5.0


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


def courbe_souffle(ecrans):
    """b(t) : monte de 0 à 1 pendant « inspire », redescend pendant « expire »."""
    phases = [(a, b, 1.0 if txt.startswith("inspire") else 0.0)
              for a, b, kind, txt in ecrans if kind == "fin"]

    def b(t):
        val = 0.0
        for a, fin, cible in phases:
            if t < a:
                break
            x = min(1.0, (t - a) / max(fin - a, 0.1))
            x = x * x * (3 - 2 * x)                     # douceur
            val = val + (cible - val) * x if t < fin else cible
        return val
    return b


def video(scene, ecrans, total, dst, tmp):
    """Fond animé de la scène, qui respire avec le guide, + textes en fondu (sans son)."""
    fond = os.path.join(tmp, "fond.mp4")
    fonds_pause.rendre(scene, total, fond, courbe_souffle(ecrans))
    entrees, graphe = ["-i", fond], [f"[0:v]fade=t=in:st=0:d=1.5,fade=t=out:st={total - 3}:d=3[b0]"]
    for i, (a, b, kind, txt) in enumerate(ecrans):
        a, d = max(a, 0.3), b - max(a, 0.3)
        png = os.path.join(tmp, f"e{i}.png")
        calque(1080, 1920, kind, txt).save(png)
        entrees += ["-loop", "1", "-framerate", "30", "-t", f"{d:.2f}", "-i", png]
        fi = min(0.8, d / 3)
        graphe.append(f"[{i + 1}:v]format=rgba,fade=t=in:st=0:d={fi:.2f}:alpha=1,"
                      f"fade=t=out:st={d - 0.8:.2f}:d=0.8:alpha=1,setpts=PTS+{a:.2f}/TB[t{i}]")
        graphe.append(f"[b{i}][t{i}]overlay=eof_action=pass:format=auto[b{i + 1}]")
    graphe.append(f"[b{len(ecrans)}]format=yuv420p[v]")
    script = os.path.join(tmp, "graphe.txt")
    open(script, "w").write(";\n".join(graphe))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entrees, "-filter_complex_script", script,
                    "-map", "[v]", "-t", str(total), "-c:v", "libx264", "-preset", "medium",
                    "-b:v", "2500k", "-maxrate", "3500k", "-bufsize", "6000k", "-r", "30", dst], check=True)


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
        video(scene, ecrans, total, brut, tmp)
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
