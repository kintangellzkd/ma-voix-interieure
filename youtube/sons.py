"""Sons d'ambiance synthétisés (numpy/scipy), pour que chaque scène ait sa propre texture.

- neige   : vent d'hiver par rafales, léger sifflement, poudrerie dans les branches.
- aurores : lac calme (clapotis de petites vagues sur la rive) et nappe très douce.

La pluie garde son filtre ffmpeg (ambiances.Pluie.audio), déjà distinct.
Usage : python3 youtube/sons.py neige aurores --secondes 60  (écrit des aperçus .wav)
"""
import argparse
import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000


def _bruit(rng, n):
    return rng.standard_normal(n).astype(np.float32)


def _filtre(x, kind, f, ordre=2):
    sos = butter(ordre, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x).astype(np.float32)


def _lent(rng, n, fmin, fmax, k=5):
    """Enveloppe lente aléatoire dans [0, 1] (somme de sinus à phases aléatoires)."""
    t = np.arange(n, dtype=np.float32) / SR
    e = np.zeros(n, np.float32)
    for _ in range(k):
        e += np.sin(2 * np.pi * rng.uniform(fmin, fmax) * t + rng.uniform(0, 2 * np.pi)).astype(np.float32)
    e = (e - e.min()) / (e.max() - e.min() + 1e-9)
    return e


def _norm(x, crete=0.5):
    return x * (crete / (np.abs(x).max() + 1e-9))


def neige(duree, graine=7):
    rng = np.random.default_rng(graine)
    n = int(duree * SR)
    rafale = _lent(rng, n, 0.02, 0.12) ** 1.6
    canaux = []
    for c in range(2):
        corps = _filtre(_filtre(_bruit(rng, n), "lowpass", 700), "highpass", 60) * (0.25 + 0.75 * rafale)
        sifflet = np.zeros(n, np.float32)
        for f0 in (430, 610, 820):
            bande = _filtre(_bruit(rng, n), "bandpass", [f0 * 0.96, f0 * 1.04])
            sifflet += _norm(bande, 1.0) * (_lent(rng, n, 0.03, 0.1, 3) * rafale) ** 2.2
        poudre = _filtre(_bruit(rng, n), "highpass", 3000) * rafale ** 2.5
        x = _norm(corps, 1.0) + 0.22 * sifflet + 0.06 * _norm(poudre, 1.0)
        canaux.append(x)
    return _norm(np.stack(canaux, 1), 0.6)


def aurores(duree, graine=11):
    rng = np.random.default_rng(graine)
    n = int(duree * SR)
    t = np.arange(n, dtype=np.float32) / SR
    # Clapotis : une petite vague toutes les 2,5 à 6 s, montée 0,35 s, retrait 1,4 s.
    k = np.arange(int(3.5 * SR), dtype=np.float32) / SR
    noyau = (1 - np.exp(-k / 0.12)) * np.exp(-k / 0.9)
    pluie_fine = np.exp(-k / 0.25) * (k > 0.25)
    canaux = []
    for c in range(2):
        imp, imp2 = np.zeros(n, np.float32), np.zeros(n, np.float32)
        x = rng.uniform(0, 2)
        while x < duree - 4:
            a = rng.uniform(0.4, 1.0)
            imp[int(x * SR)] = a
            imp2[int((x + rng.uniform(0.2, 0.5)) * SR)] = a * rng.uniform(0.3, 0.8)
            x += rng.uniform(2.5, 6.0)
        env = _conv(imp, noyau, n)
        env2 = _conv(imp2, pluie_fine, n)
        vague = _filtre(_filtre(_bruit(rng, n), "lowpass", 900), "highpass", 120) * env
        ruissel = _filtre(_bruit(rng, n), "bandpass", [1800, 5000]) * env2
        canaux.append(_norm(vague, 1.0) + 0.18 * _norm(ruissel, 1.0))
    eau = np.stack(canaux, 1)
    # Nappe : accord grave (la, mi, la, do#) qui respire très lentement, légèrement désaccordé.
    nappe = np.zeros((n, 2), np.float32)
    for f, g in ((110, 1.0), (164.8, 0.7), (220, 0.5), (277.2, 0.3)):
        for c, d in enumerate((-0.25, 0.25)):
            nappe[:, c] += g * np.sin(2 * np.pi * (f + d) * t).astype(np.float32) * (0.3 + 0.7 * _lent(rng, n, 0.01, 0.04, 3))
    vent = _filtre(_bruit(rng, n), "lowpass", 300)[:, None] * 0.5
    return _norm(_norm(eau, 1.0) + 0.16 * _norm(nappe, 1.0) + 0.08 * _norm(vent, 1.0), 0.6)


def _conv(imp, noyau, n):
    """Convolution FFT par blocs (rapide sur 20 min)."""
    from scipy.signal import oaconvolve
    return oaconvolve(imp, noyau)[:n].astype(np.float32)


# ------------------------------------------------------------------ orage ---
def eclairs(duree, graine=23):
    """Instants des éclairs : (t, distance 0..1, variante). Partagés entre l'image et le son."""
    rng = np.random.default_rng(graine)
    ev, t = [], rng.uniform(6, 14)
    while t < duree - 15:
        ev.append((round(float(t), 2), float(rng.uniform(0, 1)) ** 1.8, int(rng.integers(0, 3))))
        t += rng.uniform(22, 65)
    return ev


def _grains(rng, n, taux, tau_ms):
    """Crépitement : impulsions aléatoires (Poisson) adoucies par une décroissance courte."""
    imp = np.zeros(n, np.float32)
    k = rng.poisson(taux * n / SR)
    pos = rng.integers(0, n, k)
    imp[pos] = rng.uniform(0.2, 1.0, k).astype(np.float32) ** 2
    m = np.arange(int(tau_ms * 5e-3 * SR), dtype=np.float32)
    return _conv(imp, np.exp(-m / (tau_ms * 1e-3 * SR)), n)


def orage(duree, graine=29):
    rng = np.random.default_rng(graine)
    n = int(duree * SR)
    rafale = _lent(rng, n, 0.03, 0.15) ** 1.3
    canaux = []
    for c in range(2):
        # pluie battante : grondement large bande + crépitement des gouttes
        nappe = _filtre(_filtre(_bruit(rng, n), "highpass", 350), "lowpass", 9000)
        patter = _filtre(_bruit(rng, n), "highpass", 1500) * _grains(rng, n, 2500, 3)
        pluie = _norm(nappe, 1.0) * (0.75 + 0.25 * rafale) + 0.9 * _norm(patter, 1.0)
        vent = _filtre(_filtre(_bruit(rng, n), "lowpass", 600), "highpass", 50) * (0.15 + 0.85 * rafale)
        sifflet = _filtre(_bruit(rng, n), "bandpass", [520, 580]) * rafale ** 2.5
        canaux.append(0.55 * _norm(pluie, 1.0) + 0.45 * _norm(vent, 1.0) + 0.12 * _norm(sifflet, 1.0))
    fond = np.stack(canaux, 1)
    fond = 0.35 * fond / (np.abs(fond).max() + 1e-9)

    tonnerre = np.zeros((n, 2), np.float32)
    for t0, dist, _ in eclairs(duree):
        retard = 0.25 + dist * 3.5                    # la lumière arrive avant le son
        force = 1.0 - 0.6 * dist
        L = int(14 * SR)
        k = np.arange(L, dtype=np.float32) / SR
        env = np.zeros(L, np.float32)
        for _ in range(rng.integers(4, 9)):           # roulement : plusieurs grondements
            d = rng.uniform(0, 3.5) * (0.4 + dist)
            a = rng.uniform(0.4, 1.0)
            tau = rng.uniform(1.5, 4.5)
            env += a * np.clip(k - d, 0, None) ** 0.3 * np.exp(-np.clip(k - d, 0, None) / tau) * (k >= d)
        env /= env.max() + 1e-9
        gr = _filtre(_filtre(_bruit(rng, L), "lowpass", 140 + 260 * (1 - dist)), "highpass", 25)
        gr = _norm(gr, 1.0) * env
        if dist < 0.45:                               # proche : claquement sec
            cl = _filtre(_bruit(rng, L), "bandpass", [900, 5000]) * np.exp(-k / 0.18)
            gr += 0.7 * (1 - dist) * _norm(cl, 1.0)
        i0 = int((t0 + retard) * SR)
        j = min(n, i0 + L) - i0
        if j <= 0:
            continue
        pan = rng.uniform(-0.4, 0.4)
        tonnerre[i0:i0 + j, 0] += gr[:j] * force * (1 - pan)
        tonnerre[i0:i0 + j, 1] += gr[:j] * force * (1 + pan)
    x = fond + 0.75 * tonnerre / (np.abs(tonnerre).max() + 1e-9)
    x = np.tanh(1.6 * x) / np.tanh(1.6)                # compression douce : fort sans saturer
    return _norm(x, 0.89)


SONS = {"neige": neige, "aurores": aurores, "orage": orage}


def fichier(scene, duree, dossier):
    """Chemin d'un .wav (mis en cache) pour la scène et la durée demandées, ou None."""
    if scene not in SONS:
        return None
    os.makedirs(dossier, exist_ok=True)
    dst = os.path.join(dossier, f"{scene}-{int(duree)}s.wav")
    if not os.path.exists(dst):
        sf.write(dst, SONS[scene](duree), SR, subtype="PCM_16")
    return dst


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="+")
    ap.add_argument("--secondes", type=int, default=60)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    for s in a.scenes:
        print(fichier(s, a.secondes, a.out))
