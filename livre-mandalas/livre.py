"""Génère l'intérieur (PDF noir et blanc) et la couverture (PDF couleur) du livre
« Mandalas de la Voix Intérieure » au format Amazon KDP 8,5 x 11 pouces.

    python3 livre.py            -> sortie/interieur.pdf et sortie/couverture.pdf
"""
import os
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contenu import PAGES, SECTIONS  # noqa: E402
from dessins import designs  # noqa: E402
from moteur import Mandala, compose, lotus_center, ring_beads  # noqa: E402

TITRE = "Mandalas de la Voix Intérieure"
SOUS_TITRE = "45 mandalas à colorier pour méditer"
THEMES = "Chakras · Kundalini · Paix · Aube"
AUTEUR = "Essential Human Academy"
ANNEE = 2026

W, H = 8.5 * inch, 11 * inch
VERT, OR, CREME = HexColor("#1C2820"), HexColor("#C09A4E"), HexColor("#FFFDF8")
NOIR, GRIS = HexColor("#000000"), HexColor("#555555")

FONTS = {"om": "FreeSerif"}
for name, path in [("Caladea", "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"),
                   ("Caladea-Italic", "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf"),
                   ("Caladea-Bold", "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"),
                   ("FreeSerif", "/usr/share/fonts/truetype/freefont/FreeSerif.ttf")]:
    pdfmetrics.registerFont(TTFont(name, path))

TEXTE = ParagraphStyle("texte", fontName="Caladea", fontSize=12.5, leading=18.5, alignment=TA_JUSTIFY,
                       textColor=NOIR)
CENTRE = ParagraphStyle("centre", parent=TEXTE, alignment=TA_CENTER)
AFFIRM = ParagraphStyle("affirm", fontName="Caladea-Italic", fontSize=17, leading=23, alignment=TA_CENTER)

DESSINS = designs(FONTS)
SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sortie")


# --- utilitaires ------------------------------------------------------------------

def spaced(c, text, x, y, font, size, spacing=2.2, color=NOIR, align="center"):
    """Texte en capitales espacées."""
    c.saveState()
    c.setFillColor(color)
    w = sum(c.stringWidth(ch, font, size) for ch in text) + spacing * (len(text) - 1)
    if align == "center":
        x -= w / 2
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(spacing)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()


def para(c, text, style, x, y_top, width):
    p = Paragraph(text, style)
    _, h = p.wrap(width, 1000)
    p.drawOn(c, x, y_top - h)
    return y_top - h


def ornement(c, cx, cy, r, ink=NOIR, paper=(1, 1, 1)):
    c.saveState()
    c.translate(cx, cy)
    m = Mandala(c, ink=ink.rgb() if hasattr(ink, "rgb") else ink, paper=paper, lw=0.7)
    lotus_center(m, r, 8)
    c.restoreState()


def filet(c, x0, x1, y, color=NOIR, lw=0.6):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x0, y, x1, y)


def numero(c, n):
    c.setFont("Caladea", 10)
    c.setFillColor(GRIS)
    c.drawCentredString(W / 2, 0.45 * inch, str(n))


def dessiner_mandala(c, cle, cx, cy, R, ink=(0, 0, 0), paper=(1, 1, 1), lw=1.25):
    c.saveState()
    c.translate(cx, cy)
    m = Mandala(c, ink=ink, paper=paper, lw=lw)
    DESSINS[cle](m, R)
    c.restoreState()


# --- pages ------------------------------------------------------------------------

def page_titre(c):
    dessiner_mandala(c, "finale-voix", W / 2, H * .6, 2.3 * inch, lw=.9)
    spaced(c, AUTEUR.upper(), W / 2, H - 1.0 * inch, "Caladea", 10, 3)
    c.setFillColor(NOIR)
    c.setFont("Caladea", 34)
    c.drawCentredString(W / 2, 3.15 * inch, "Mandalas")
    c.setFont("Caladea-Italic", 24)
    c.drawCentredString(W / 2, 2.72 * inch, "de la Voix Intérieure")
    filet(c, W / 2 - 1 * inch, W / 2 + 1 * inch, 2.45 * inch)
    c.setFont("Caladea", 14)
    c.drawCentredString(W / 2, 2.1 * inch, SOUS_TITRE)
    spaced(c, THEMES.upper(), W / 2, 1.75 * inch, "Caladea", 10, 2)


def page_copyright(c):
    y = 4.2 * inch
    lignes = [
        f"<b>{TITRE}</b><br/>{SOUS_TITRE}",
        f"© {ANNEE} {AUTEUR}. Tous droits réservés.",
        "Aucune partie de ce livre ne peut être reproduite, stockée ou transmise sous quelque forme que ce "
        "soit sans l'autorisation écrite de l'éditeur, à l'exception de la copie des pages de coloriage "
        "pour un usage strictement personnel.",
        "Ce livre propose une pratique de détente et de méditation. Il ne remplace en aucun cas un avis, "
        "un diagnostic ou un traitement médical ou psychologique.",
        "Les méditations guidées et les fréquences évoquées dans ce livre sont disponibles dans "
        "l'application <i>Ma Voix Intérieure</i> d'Essential Human Academy.",
        "Première édition · Imprimé à la demande",
    ]
    st = ParagraphStyle("cp", parent=TEXTE, fontSize=10, leading=14, alignment=TA_CENTER, textColor=GRIS)
    for t in lignes:
        y = para(c, t, st, 1.5 * inch, y, W - 3 * inch) - 10


def page_appartient(c):
    ornement(c, W / 2, H * .62, 1.6 * inch)
    c.setFont("Caladea-Italic", 26)
    c.setFillColor(NOIR)
    c.drawCentredString(W / 2, H * .36, "Ce livre appartient à")
    filet(c, 2 * inch, W - 2 * inch, H * .27, lw=.8)
    c.setFont("Caladea", 12)
    c.setFillColor(GRIS)
    c.drawCentredString(W / 2, H * .2, "Commencé le  ________________")


def page_texte(c, titre, blocs, n):
    spaced(c, AUTEUR.upper(), W / 2, H - .9 * inch, "Caladea", 8.5, 2.5, GRIS)
    c.setFont("Caladea", 28)
    c.setFillColor(NOIR)
    c.drawCentredString(W / 2, H - 1.75 * inch, titre)
    filet(c, W / 2 - .7 * inch, W / 2 + .7 * inch, H - 2.0 * inch)
    y = H - 2.45 * inch
    for b in blocs:
        if b.startswith("##"):
            y -= 6
            spaced(c, b[2:].strip().upper(), W / 2, y - 10, "Caladea-Bold", 10, 2)
            y -= 26
        else:
            y = para(c, b, TEXTE, 1.25 * inch, y, W - 2.5 * inch) - 11
    numero(c, n)


INTRO = [
    "Bienvenue dans ce livre de coloriage méditatif, conçu dans l'esprit de l'application "
    "<i>Ma Voix Intérieure</i>. Chaque mandala accompagne un thème de pratique : l'aube, les chakras, "
    "la kundalini, la paix, la relaxation, le guide intérieur, la gratitude, la libération, les "
    "éléments et la géométrie sacrée.",
    "Le mot <i>mandala</i> signifie « cercle » en sanskrit. Depuis des siècles, on le dessine pour "
    "rassembler l'attention vers un centre. Colorier un mandala, c'est offrir à l'esprit un point "
    "d'appui : la main travaille, le souffle ralentit, les pensées se posent.",
    "## Comment utiliser ce livre",
    "Chaque mandala est imprimé sur une page de droite. Sur la page de gauche, tu trouveras son "
    "histoire, une affirmation à répéter, des couleurs suggérées et un espace pour noter ton "
    "intention. Rien n'est obligatoire : suis l'ordre du livre ou choisis le mandala qui t'appelle.",
    "Si tu utilises des feutres ou des encres, glisse une feuille cartonnée sous la page pour "
    "protéger la suivante. Les crayons de couleur, les pastels secs et les feutres à pointe fine "
    "conviennent très bien.",
]

RITUEL = [
    "<b>1. Arriver.</b> Installe-toi dans un endroit calme. Pose ton téléphone, ou lance une "
    "méditation de l'application en fond sonore.",
    "<b>2. Respirer.</b> Ferme les yeux et suis trois respirations lentes. Sens le contact de "
    "tes pieds sur le sol et de tes mains sur la page.",
    "<b>3. Poser une intention.</b> Lis l'affirmation à voix haute ou intérieurement, puis écris "
    "ton intention du jour sur la page de gauche.",
    "<b>4. Colorier.</b> Commence par le centre ou par l'extérieur, selon ton envie. Quand ton "
    "esprit s'échappe, ramène-le simplement au geste, sans te juger.",
    "<b>5. Remercier.</b> Avant de refermer le livre, prends un instant pour regarder ce que tu "
    "as créé. Note la date sous le mandala : il devient la trace d'un moment de paix.",
    "## Les couleurs des chakras",
    "<b>Racine</b> rouge · <b>Sacré</b> orange · <b>Plexus solaire</b> jaune · <b>Cœur</b> vert ou "
    "rose · <b>Gorge</b> bleu · <b>Troisième œil</b> indigo · <b>Couronne</b> violet ou blanc.",
]


def page_essai(c, n):
    spaced(c, "PAGE D'ESSAI DES COULEURS", W / 2, H - 1.0 * inch, "Caladea", 11, 3)
    c.setFont("Caladea-Italic", 12)
    c.setFillColor(GRIS)
    c.drawCentredString(W / 2, H - 1.35 * inch, "Teste ici tes crayons et tes feutres avant de commencer.")
    c.setStrokeColor(NOIR)
    c.setFillColor(HexColor("#FFFFFF"))
    cols, rows = 6, 8
    r = .42 * inch
    x0 = W / 2 - (cols - 1) * 1.05 * inch / 2
    y0 = H - 2.2 * inch
    c.setLineWidth(1)
    for j in range(rows):
        for i in range(cols):
            c.circle(x0 + i * 1.05 * inch, y0 - j * 1.02 * inch, r, stroke=1, fill=0)
            c.setLineWidth(.5)
            c.line(x0 + i * 1.05 * inch - r * .8, y0 - j * 1.02 * inch - r - 6,
                   x0 + i * 1.05 * inch + r * .8, y0 - j * 1.02 * inch - r - 6)
            c.setLineWidth(1)
    numero(c, n)


def page_accompagnement(c, num, entry, n):
    cle, sec, titre, sous_titre, texte, affirmation, couleurs = entry
    rom, nom_sec, _ = SECTIONS[sec]
    spaced(c, f"{rom} · {nom_sec}".upper(), W / 2, H - .9 * inch, "Caladea", 9, 2.5, GRIS)
    ornement(c, W / 2, H - 1.75 * inch, .48 * inch)
    spaced(c, f"MANDALA {num:02d}", W / 2, H - 2.65 * inch, "Caladea-Bold", 10, 3)
    c.setFillColor(NOIR)
    c.setFont("Caladea", 34)
    c.drawCentredString(W / 2, H - 3.25 * inch, titre)
    c.setFont("Caladea-Italic", 14)
    c.setFillColor(GRIS)
    c.drawCentredString(W / 2, H - 3.6 * inch, sous_titre)
    filet(c, W / 2 - .7 * inch, W / 2 + .7 * inch, H - 3.85 * inch)

    y = para(c, texte, TEXTE, 1.25 * inch, H - 4.15 * inch, W - 2.5 * inch)

    # affirmation encadrée
    y -= .35 * inch
    p = Paragraph(f"« {affirmation} »", AFFIRM)
    _, h = p.wrap(W - 3.2 * inch, 500)
    box_h = h + .55 * inch
    c.setStrokeColor(NOIR)
    c.setLineWidth(.7)
    c.roundRect(1.4 * inch, y - box_h, W - 2.8 * inch, box_h, 10, stroke=1, fill=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(W / 2 - .65 * inch, y - 8, 1.3 * inch, 14, stroke=0, fill=1)
    spaced(c, "AFFIRMATION", W / 2, y - .02 * inch - 3, "Caladea", 8, 2.5, GRIS)
    p.drawOn(c, 1.6 * inch, y - box_h + .25 * inch)
    y -= box_h + .35 * inch

    c.setFont("Caladea-Bold", 11)
    c.setFillColor(NOIR)
    c.drawString(1.25 * inch, y, "Couleurs suggérées :")
    c.setFont("Caladea", 11.5)
    c.drawString(1.25 * inch + c.stringWidth("Couleurs suggérées : ", "Caladea-Bold", 11), y, couleurs)
    y -= .45 * inch
    c.setFont("Caladea-Bold", 11)
    c.drawString(1.25 * inch, y, "Mon intention :")
    lignes = max(3, int((y - 1.45 * inch) / (.42 * inch)))
    for k in range(lignes):
        filet(c, 1.25 * inch + (1.15 * inch if k == 0 else 0), W - 1.25 * inch, y - 2 - k * .42 * inch, GRIS, .5)
    y -= lignes * .42 * inch + .2 * inch
    c.setFont("Caladea-Bold", 11)
    c.drawString(1.25 * inch, y, "Date :")
    filet(c, 1.25 * inch + .55 * inch, 3.6 * inch, y - 2, GRIS, .5)
    numero(c, n)


def page_mandala(c, entry):
    cle, _, titre, *_ = entry
    dessiner_mandala(c, cle, W / 2, H / 2 + .12 * inch, 3.68 * inch)
    c.setFont("Caladea-Italic", 10)
    c.setFillColor(GRIS)
    c.drawCentredString(W / 2, .5 * inch, titre)


def page_fin(c, n):
    page_texte(c, "Et maintenant ?", [
        "Tu as traversé les quarante-cinq mandalas de ce livre. Que tu les aies tous coloriés ou "
        "seulement quelques-uns, chaque minute passée ici était une minute offerte à toi-même.",
        "Pour prolonger la pratique, retrouve dans l'application <i>Ma Voix Intérieure</i> les "
        "méditations guidées qui ont inspiré ces pages : <i>La force de l'aube</i>, "
        "<i>Alignement des sept chakras</i>, <i>J'ai, je suis, j'ai reçu</i>, la relaxation "
        "profonde, la libération, le guide intérieur et les fréquences sacrées.",
        "Tu peux aussi recommencer : un mandala colorié une seconde fois, dans d'autres couleurs, "
        "révèle souvent un autre état intérieur. Photocopie tes pages préférées pour ton usage "
        "personnel et compare-les au fil des saisons.",
        "## Un petit service",
        "Si ce livre t'a fait du bien, un avis sur Amazon aide énormément les créateurs "
        "indépendants. Tu peux même y partager la photo de ton mandala préféré.",
        "Merci, et à très bientôt.",
    ], n)
    ornement(c, W / 2, 1.7 * inch, .55 * inch)


def page_notes(c, n):
    spaced(c, "MON JOURNAL DE COULEURS", W / 2, H - 1.0 * inch, "Caladea", 11, 3)
    c.setFont("Caladea-Italic", 12)
    c.setFillColor(GRIS)
    c.drawCentredString(W / 2, H - 1.35 * inch, "Ce que j'ai ressenti, ce que j'ai découvert, ce que je veux garder.")
    y = H - 2.0 * inch
    while y > 1.0 * inch:
        filet(c, 1.0 * inch, W - 1.0 * inch, y, GRIS, .5)
        y -= .42 * inch
    numero(c, n)


def interieur(path):
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(f"{TITRE} - {SOUS_TITRE}")
    c.setAuthor(AUTEUR)
    n = 1
    pages = [
        page_titre,
        page_copyright,
        page_appartient,
        lambda c: page_texte(c, "Bienvenue", INTRO, 4),
        lambda c: page_texte(c, "Le rituel en cinq temps", RITUEL, 5),
        lambda c: page_essai(c, 6),
        lambda c: None,  # page 7 : verso de la page d'essai laissé blanc (le livre ouvre ensuite en vis-à-vis)
    ]
    # page 7 blanche pour que chaque texte tombe à gauche (pair) et chaque mandala à droite (impair)
    for f in pages:
        f(c)
        c.showPage()
        n += 1
    assert n % 2 == 0
    for i, e in enumerate(PAGES, 1):
        page_accompagnement(c, i, e, n)
        c.showPage()
        n += 1
        page_mandala(c, e)
        c.showPage()
        n += 1
    page_fin(c, n)
    c.showPage()
    n += 1
    page_notes(c, n)
    c.showPage()
    n += 1
    page_notes(c, n)
    c.showPage()
    n += 1
    if (n - 1) % 2:  # nombre de pages pair
        c.showPage()
        n += 1
    c.save()
    return n - 1


# --- couverture ---------------------------------------------------------------------

def couverture(path, nb_pages):
    bleed = .125 * inch
    spine = nb_pages * .002252 * inch  # papier blanc, intérieur noir et blanc (KDP)
    CW = 2 * W + spine + 2 * bleed
    CH = H + 2 * bleed
    c = canvas.Canvas(path, pagesize=(CW, CH))
    c.setTitle(f"{TITRE} - couverture")
    c.setFillColor(VERT)
    c.rect(0, 0, CW, CH, stroke=0, fill=1)

    front_x = bleed + W + spine  # bord gauche de la 1re de couverture
    fcx = front_x + W / 2

    # 1re de couverture
    ink, paper = OR.rgb(), VERT.rgb()
    dessiner_mandala(c, "chakra-couronne", fcx, bleed + 3.85 * inch, 2.85 * inch, ink, paper, lw=1.1)
    spaced(c, AUTEUR.upper(), fcx, bleed + H - .85 * inch, "Caladea", 11, 3.5, OR)
    c.setFillColor(CREME)
    c.setFont("Caladea", 54)
    c.drawCentredString(fcx, bleed + H - 1.75 * inch, "Mandalas")
    c.setFont("Caladea-Italic", 32)
    c.drawCentredString(fcx, bleed + H - 2.3 * inch, "de la Voix Intérieure")
    c.setStrokeColor(OR)
    c.setLineWidth(.8)
    c.line(fcx - 1.1 * inch, bleed + H - 2.55 * inch, fcx + 1.1 * inch, bleed + H - 2.55 * inch)
    c.setFont("Caladea", 17)
    c.setFillColor(CREME)
    c.drawCentredString(fcx, bleed + H - 2.9 * inch, SOUS_TITRE)
    # bandeau bas
    spaced(c, THEMES.upper(), fcx, bleed + .5 * inch, "Caladea", 12, 3, OR)

    # 4e de couverture
    bcx = bleed + W / 2
    spaced(c, AUTEUR.upper(), bcx, bleed + H - .85 * inch, "Caladea", 10, 3.5, OR)
    c.setFillColor(CREME)
    c.setFont("Caladea-Italic", 26)
    c.drawCentredString(bcx, bleed + H - 1.55 * inch, "Colorier pour revenir à soi")
    st = ParagraphStyle("dos", fontName="Caladea", fontSize=13, leading=19, alignment=TA_JUSTIFY, textColor=CREME)
    y = bleed + H - 2.0 * inch
    for t in [
        "Quarante-cinq mandalas originaux, nés de l'univers de l'application <i>Ma Voix Intérieure</i>, "
        "pour transformer quelques minutes de coloriage en véritable méditation.",
        "Les sept chakras et leurs yantras, l'éveil de la kundalini, la paix, la force de l'aube, "
        "la relaxation, le guide intérieur, la gratitude, la libération, les cinq éléments, la fleur "
        "de vie et les fréquences sacrées.",
        "Face à chaque mandala : son histoire, une affirmation, des couleurs suggérées et un espace "
        "pour écrire ton intention du jour.",
    ]:
        y = para(c, t, st, bleed + .9 * inch, y, W - 1.8 * inch) - 10
    puces = ["45 mandalas imprimés au recto, page de droite", "Grand format 21,6 x 27,9 cm",
             "Pour adultes et adolescents, débutants et confirmés", "Page d'essai des couleurs et journal intérieur"]
    y -= 6
    c.setFont("Caladea", 12.5)
    for p in puces:
        c.setFillColor(OR)
        c.drawString(bleed + 1.0 * inch, y, "•")
        c.setFillColor(CREME)
        c.drawString(bleed + 1.25 * inch, y, p)
        y -= 20
    ornement(c, bcx - 1.4 * inch, bleed + 1.55 * inch, .85 * inch, OR, VERT.rgb())
    # zone du code-barres (en bas à droite) laissée libre pour KDP : 2 x 1.2 pouces
    c.save()
    return CW / inch, CH / inch, spine / inch


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    nb = interieur(os.path.join(SORTIE, "interieur.pdf"))
    cw, ch, sp = couverture(os.path.join(SORTIE, "couverture.pdf"), nb)
    print(f"Intérieur : {nb} pages · Couverture : {cw:.3f} x {ch:.3f} in (dos {sp:.4f} in)")
