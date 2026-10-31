#!/usr/bin/env python3
"""Écrit youtube/youtube.md : titre, description et tags prêts à coller
pour chaque vidéo de fréquence (tirés de catalog.json)."""
import json, os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat = json.load(open(os.path.join(RACINE, "catalog.json"), encoding="utf-8"))
out = ["# Vidéos YouTube · Fréquences (10 min)\n",
       "Fichiers produits par `python3 youtube/generer_videos.py` dans `youtube/sortie/` :",
       "`hz-XXX-10min.mp4` (vidéo) et `hz-XXX-miniature.jpg` (miniature 1280x720).\n"]
for f in cat["frequences"]:
    hz = f"{f['hz']:g} Hz"
    onde = f["wave"]
    out += [f"---\n\n## {hz} · {f['title']}\n",
            "**Titre**\n",
            f"```\n{hz} · {f['title']} | {onde} binaural · 10 min de méditation\n```\n",
            "**Description**\n",
            "```",
            f"{hz} · {f['title']} — {f['subtitle']}.",
            "",
            f["description"],
            "",
            f"🎧 Mets tes écouteurs : un battement binaural {onde} est placé sous la fréquence {hz}. "
            "Chaque oreille reçoit un son légèrement différent ; c'est ton cerveau qui crée l'onde.",
            "",
            "Installe-toi, ferme les yeux, laisse les ondes faire le reste. Dix minutes suffisent.",
            "",
            "Ma Voix Intérieure — méditations guidées d'Essential Human Academy.",
            "Contact : info@ehacademy.ca",
            "",
            "Ces sons accompagnent la détente ; ils ne remplacent pas un avis médical. "
            "Ne pas écouter en conduisant.",
            "",
            f"#{int(f['hz'])}Hz #meditation #binaural #frequence #mavoixinterieure",
            "```\n",
            "**Tags**\n",
            "```",
            ", ".join([f"{hz}", f"{int(f['hz'])} hz", f"fréquence {hz}", onde.lower(),
                       "binaural", "battements binauraux", "méditation", "méditation 10 minutes",
                       "relaxation", "solfège sacré", "ondes cérébrales", "Ma Voix Intérieure",
                       "Essential Human Academy"]),
            "```\n"]
open(os.path.join(RACINE, "youtube", "youtube.md"), "w", encoding="utf-8").write("\n".join(out))
print("youtube/youtube.md écrit")
