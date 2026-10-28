# Mandalas de la Voix Intérieure

Livre de coloriage méditatif d'Essential Human Academy, prêt pour Amazon KDP (broché).

- `sortie/interieur.pdf` : intérieur, 100 pages, 8,5 x 11 po (21,6 x 27,9 cm), noir et blanc, sans fond perdu
- `sortie/couverture.pdf` : couverture complète (4e + dos + 1re), 17,475 x 11,25 po, fond perdu de 0,125 po inclus
- `sortie/apercu-45-mandalas.png`, `sortie/apercu-couverture.png` : aperçus

Pour régénérer après une modification : `python3 livre.py` (il faut Python 3 et `reportlab`).

| Fichier | Rôle |
|---|---|
| `moteur.py` | moteur de dessin vectoriel (anneaux, pétales, yantras, serpent, colombe…) |
| `dessins.py` | composition des 45 mandalas |
| `contenu.py` | textes : sections, histoire, affirmation, couleurs de chaque mandala |
| `livre.py` | mise en page de l'intérieur et de la couverture |

## Structure du livre

1. Page de titre, copyright, « Ce livre appartient à », Bienvenue, Rituel en cinq temps, Page d'essai des couleurs
2. 45 mandalas : chaque mandala est seul sur la page de droite ; la page de gauche donne son histoire,
   une affirmation, des couleurs suggérées et des lignes pour l'intention du jour
3. « Et maintenant ? » (renvoi vers l'application) et deux pages de journal

| Section | Mandalas |
|---|---|
| I. L'aube | La force de l'aube, Le premier rayon, Le souffle du matin, L'horizon doré |
| II. Les chakras | Muladhara, Svadhisthana, Manipura, Anahata, Vishuddha, Ajna, Sahasrara (avec leur yantra), L'alignement des sept |
| III. La kundalini | Le serpent endormi, L'éveil de Shakti, Ida et Pingala, La flamme qui s'élève |
| IV. La paix | La colombe, Le rameau d'olivier, Le lotus sur l'eau calme, Le lac intérieur, Shanti |
| V. Relaxation et nuit | La relaxation profonde, La lune bienveillante, Le ciel étoilé |
| VI. Le guide intérieur | Le guide intérieur (l'œil), L'étoile qui guide, Le silence (Om) |
| VII. La loi d'attraction | J'ai, je suis, j'ai reçu, La gratitude, L'abondance |
| VIII. La libération | Plumes légères, Le papillon, L'envol |
| IX. La motivation | Au sommet, L'élan |
| X. Les cinq éléments | Terre, Eau, Feu, Air, Éther |
| XI. Géométrie sacrée et fréquences | Fleur de vie, Yantra de l'harmonie, Cube de Métatron, Les fréquences sacrées |
| XII. Finale | Ma voix intérieure |

## Paramètres KDP

- Encre et papier : **noir et blanc, papier blanc** (le dos de 0,2252 po est calculé pour ce papier ;
  si tu choisis le papier crème, change `.002252` en `.0025` dans `livre.py` et régénère)
- Format : **8,5 x 11 po**, fond perdu : **non** pour l'intérieur
- Finition de couverture : **mate** (plus douce pour un livre de méditation)
- La zone du code-barres (en bas à droite de la 4e de couverture) est laissée libre : KDP l'ajoute.
- ISBN : KDP peut en fournir un gratuitement.
- **Contenu généré par IA** : KDP demande de le déclarer. Les dessins ont été générés par programme
  avec l'aide de Claude (IA) : réponds « oui » à la question sur les images et le texte, puis relis les textes.

## Fiche Amazon proposée

**Titre** : Mandalas de la Voix Intérieure
**Sous-titre** : 45 mandalas à colorier pour méditer : chakras, kundalini, paix et aube. Livre de coloriage anti-stress pour adultes avec affirmations
**Auteur / marque** : Essential Human Academy

**Description** :
> Transformez quelques minutes de coloriage en véritable méditation.
>
> Né de l'univers de l'application *Ma Voix Intérieure*, ce livre réunit 45 mandalas originaux autour des grands thèmes de la pratique : les sept chakras et leurs yantras, l'éveil de la kundalini, la paix, la force de l'aube, la relaxation, le guide intérieur, la gratitude, la libération, les cinq éléments et la géométrie sacrée.
>
> Face à chaque mandala : son histoire, une affirmation positive, des couleurs suggérées et un espace pour écrire votre intention du jour.
>
> • 45 mandalas imprimés au recto, sur la page de droite
> • Grand format 21,6 x 27,9 cm
> • Page d'essai des couleurs et journal intérieur
> • Pour adultes et adolescents, débutants comme confirmés
>
> Un cadeau idéal pour les amoureux du yoga, de la méditation et du développement personnel.

**7 mots-clés** : coloriage mandala adulte anti-stress · livre coloriage chakras · mandala méditation zen · kundalini yoga cadeau · coloriage spirituel affirmations positives · art-thérapie relaxation adulte · géométrie sacrée fleur de vie

**Catégories** : Loisirs créatifs > Coloriage pour adultes ; Spiritualité > Méditation ; Santé, forme > Gestion du stress
