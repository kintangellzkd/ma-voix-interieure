"""Textes du livre : sections et pages d'accompagnement de chaque mandala."""

SECTIONS = {
    "aube": ("I", "L'aube", "La pratique de chaque matin"),
    "chakras": ("II", "Les chakras", "Aligner ses sept centres d'énergie"),
    "kundalini": ("III", "La kundalini", "L'énergie qui s'éveille"),
    "paix": ("IV", "La paix", "Revenir au calme"),
    "relaxation": ("V", "Relaxation et nuit", "Relâcher le corps et l'esprit"),
    "guide": ("VI", "Le guide intérieur", "Écouter sa propre sagesse"),
    "attraction": ("VII", "La loi d'attraction", "J'ai, je suis, j'ai reçu"),
    "liberation": ("VIII", "La libération", "Refermer ce qui pèse encore"),
    "motivation": ("IX", "La motivation", "Commencer sa journée au sommet"),
    "elements": ("X", "Les cinq éléments", "Terre, eau, feu, air, éther"),
    "sacre": ("XI", "Géométrie sacrée et fréquences", "L'harmonie des formes et des sons"),
    "finale": ("XII", "Ma voix intérieure", "Le retour à soi"),
}

# (clé du dessin, section, titre, sous-titre, texte, affirmation, couleurs suggérées)
PAGES = [
    ("aube-force", "aube", "La force de l'aube", "La pratique de fond",
     "Chaque matin, la lumière revient sans effort. Avant de colorier, pose les mains sur la page et "
     "suis trois respirations lentes. Commence par le soleil du centre, puis laisse les couleurs "
     "s'ouvrir vers l'extérieur, comme le jour qui se lève et gagne tout l'horizon.",
     "Je m'éveille avec la lumière. Ce jour est neuf.",
     "Or, jaune pâle, pêche, rose aurore"),
    ("aube-rayon", "aube", "Le premier rayon", "Le moment où tout commence",
     "Il suffit d'un rayon pour dissiper la nuit. Colorie chaque rayon comme une intention posée "
     "pour la journée : un rayon pour la patience, un pour la douceur, un pour le courage. "
     "Les nuages du cercle intérieur se teintent lentement de lumière.",
     "Un seul rayon suffit pour éclairer mon chemin.",
     "Jaune soleil, orangé, blanc nacré, bleu ciel"),
    ("aube-souffle", "aube", "Le souffle du matin", "Arriver, respirer, s'installer",
     "Le matin, le souffle est encore lent. Inspire en traçant un contour, expire en remplissant "
     "une forme. Les feuilles et les vagues de ce mandala suivent ce rythme : rien à forcer, "
     "seulement suivre le mouvement de la respiration.",
     "Mon souffle me ramène ici, maintenant.",
     "Vert tendre, turquoise, jaune doux, crème"),
    ("aube-horizon", "aube", "L'horizon doré", "La tiédeur qui s'installe",
     "Les montagnes gardent encore un peu de nuit pendant que le ciel s'embrase. Laisse le "
     "centre briller et les sommets prendre des teintes plus profondes. Remarque la tiédeur "
     "qui se répand dans ta poitrine à mesure que la page se remplit.",
     "Je me tiens debout face à ma journée, avec calme et confiance.",
     "Or, violet, prune, rose saumon"),

    ("chakra-racine", "chakras", "Muladhara", "Le chakra racine · base de la colonne",
     "Muladhara est la racine, l'élément terre, le lien avec le sol et le corps. Son yantra "
     "réunit un carré, un triangle tourné vers le bas et quatre pétales. Colorie lentement, "
     "en sentant le poids de ton corps sur ta chaise : tu es là, porté par la terre.",
     "Mes racines me portent. Je suis en sécurité.",
     "Rouge, brun, terre de Sienne, ocre"),
    ("chakra-sacre", "chakras", "Svadhisthana", "Le chakra sacré · bas-ventre",
     "Svadhisthana est relié à l'eau, à la créativité et au plaisir d'être en vie. Six pétales "
     "entourent un croissant de lune. Laisse ta main être souple : les vagues et les gouttes de "
     "ce mandala invitent à colorier sans chercher la perfection.",
     "Je laisse la vie couler en moi avec joie.",
     "Orange, corail, abricot, bleu d'eau"),
    ("chakra-plexus", "chakras", "Manipura", "Le chakra du plexus solaire",
     "Manipura, « la cité des joyaux », est le feu intérieur : la volonté, la confiance, l'élan. "
     "Dix pétales entourent un triangle de feu. Choisis des couleurs franches et assumées, "
     "comme une décision que l'on prend pour soi.",
     "J'avance avec confiance. Ma force est tranquille.",
     "Jaune d'or, ambre, orange vif, cuivre"),
    ("chakra-coeur", "chakras", "Anahata", "Le chakra du cœur",
     "Anahata signifie « le son qui n'est pas frappé ». Ses douze pétales entourent deux "
     "triangles entrelacés : la rencontre du ciel et de la terre. Pense à une personne que tu "
     "aimes, ou à toi-même, en coloriant les cœurs du deuxième anneau.",
     "J'aime et je me laisse aimer.",
     "Vert émeraude, vert d'eau, rose tendre"),
    ("chakra-gorge", "chakras", "Vishuddha", "Le chakra de la gorge",
     "Vishuddha est le centre de l'expression et de la vérité. Seize pétales entourent un "
     "triangle et un cercle de pleine lune. C'est le chakra de ta voix intérieure qui devient "
     "parole : colorie en fredonnant doucement, si tu en as envie.",
     "Ma voix exprime ma vérité avec douceur.",
     "Bleu turquoise, bleu ciel, cyan, argent"),
    ("chakra-troisieme-oeil", "chakras", "Ajna", "Le chakra du troisième œil",
     "Ajna, entre les sourcils, est le siège de l'intuition. Deux pétales encadrent la syllabe "
     "sacrée Om. Avant de commencer, ferme les yeux quelques instants et laisse une couleur "
     "venir d'elle-même : c'est elle que tu poseras au centre.",
     "Je fais confiance à ce que je ressens.",
     "Indigo, bleu nuit, violet profond, argent"),
    ("chakra-couronne", "chakras", "Sahasrara", "Le chakra couronne · le lotus aux mille pétales",
     "Sahasrara se représente par un lotus aux mille pétales, ouvert au sommet de la tête. "
     "Ce mandala demande de la patience : chaque pétale est une petite méditation. Tu peux le "
     "colorier sur plusieurs jours, un anneau à la fois.",
     "Je fais partie de plus grand que moi.",
     "Violet, lavande, blanc, or"),
    ("chakra-alignement", "chakras", "L'alignement des sept", "De la racine à la couronne",
     "Les sept yantras sont réunis dans un même cercle. Colorie-les dans l'ordre, de la "
     "racine (en haut) jusqu'à la couronne, en suivant le sens des aiguilles d'une montre, "
     "et nomme intérieurement chaque centre en le terminant.",
     "Mes sept centres vibrent en harmonie.",
     "Les couleurs de l'arc-en-ciel, du rouge au violet"),

    ("kundalini-serpent", "kundalini", "Le serpent endormi", "L'énergie lovée à la base",
     "La tradition représente la kundalini comme un serpent enroulé trois fois et demie à la "
     "base de la colonne. Colorie ses écailles une à une, sans te presser : l'éveil ne se "
     "force pas, il s'accueille quand le terrain est prêt.",
     "J'accueille mon énergie avec patience.",
     "Vert jade, or, rouge profond, brun"),
    ("kundalini-shakti", "kundalini", "L'éveil de Shakti", "Le mouvement qui monte",
     "Sept serpents s'élancent du lotus central, comme une énergie qui se déploie en spirale. "
     "Suis leur courbe avec ton crayon avant de colorier : ce geste circulaire, répété, "
     "apaise le mental et réveille le corps.",
     "Mon énergie circule librement.",
     "Rouge, orange, or, violet"),
    ("kundalini-ida-pingala", "kundalini", "Ida et Pingala", "Les deux courants",
     "Ida, le courant lunaire, et Pingala, le courant solaire, s'enroulent autour de l'axe "
     "central. Au centre, le soleil et la lune s'équilibrent. Colorie une moitié dans des tons "
     "frais, l'autre dans des tons chauds, et observe ce qui se passe en toi.",
     "Le jour et la nuit s'équilibrent en moi.",
     "Argent et bleu nuit / or et orangé"),
    ("kundalini-flamme", "kundalini", "La flamme qui s'élève", "Le feu intérieur",
     "Des couronnes de flammes entourent un cœur de feu. Commence par les flammes extérieures "
     "dans des tons sombres et rapproche-toi du centre avec des couleurs de plus en plus "
     "lumineuses, comme une flamme qui gagne en clarté.",
     "Je nourris ma flamme intérieure.",
     "Rouge carmin, orange, jaune, blanc doré"),

    ("paix-colombe", "paix", "La colombe", "Le messager de la paix",
     "La colombe déploie ses ailes au cœur d'une couronne de rameaux d'olivier. En la "
     "coloriant, dédie ce mandala à quelqu'un, ou à un lieu du monde qui a besoin de paix. "
     "Ton intention voyage avec elle.",
     "Je suis un lieu de paix.",
     "Blanc, gris perle, vert olive, bleu ciel"),
    ("paix-olivier", "paix", "Le rameau d'olivier", "La réconciliation",
     "Offrir un rameau d'olivier, c'est faire un pas vers l'autre. Ce mandala est fait de "
     "feuilles : colorie-les en pensant à une relation que tu aimerais apaiser, sans rien "
     "attendre en retour.",
     "Je choisis la paix plutôt que d'avoir raison.",
     "Vert olive, vert sauge, argent, ocre doux"),
    ("paix-lotus", "paix", "Le lotus sur l'eau calme", "La pureté qui naît de la boue",
     "Le lotus pousse dans l'eau trouble et fleurit sans être sali. Les ondulations extérieures "
     "représentent la surface de l'eau qui se calme. Colorie les pétales du plus grand au plus "
     "petit, en ralentissant à chaque couche.",
     "Ce que je traverse me fait fleurir.",
     "Rose lotus, blanc, vert d'eau, bleu clair"),
    ("paix-lac", "paix", "Le lac intérieur", "La surface immobile",
     "Quand l'eau est agitée, on ne voit pas le fond. Quand elle se calme, tout devient clair. "
     "Les vagues du centre s'apaisent d'anneau en anneau : utilise des bleus de plus en plus "
     "doux à mesure que tu t'approches du cœur.",
     "Mon esprit se pose comme l'eau d'un lac.",
     "Bleu marine, bleu lagon, turquoise, blanc"),
    ("paix-shanti", "paix", "Shanti", "Paix en soi, paix autour de soi",
     "Shanti, la paix, se répète trois fois à la fin des mantras : paix du corps, paix de "
     "l'esprit, paix du monde. Huit colombes entourent la graine de vie. Prononce intérieurement "
     "« shanti » à chaque oiseau terminé.",
     "Om shanti, shanti, shanti.",
     "Blanc, lavande, bleu ciel, or pâle"),

    ("relax-vagues", "relaxation", "La relaxation profonde", "Le corps qui se dépose",
     "Les vagues vont et viennent, comme la respiration pendant le sommeil. Avant de commencer, "
     "relâche tes épaules, ta mâchoire, tes mains. Colorie lentement, à la lumière du soir, "
     "sans objectif de terminer.",
     "Je relâche tout ce qui n'a plus besoin d'être tenu.",
     "Bleu nuit, bleu-gris, mauve, sable"),
    ("relax-lune", "relaxation", "La lune bienveillante", "La douceur du soir",
     "La lune éclaire sans éblouir. Ce mandala est fait pour la fin de journée : des croissants, "
     "des étoiles, un ciel qui s'apaise. Tu peux noter sous l'intention une chose pour laquelle "
     "tu dis merci aujourd'hui.",
     "Je me repose dans la douceur de la nuit.",
     "Argent, bleu nuit, violet, jaune pâle"),
    ("relax-etoiles", "relaxation", "Le ciel étoilé", "Se sentir petit et relié",
     "Sous un ciel étoilé, nos soucis reprennent leur juste taille. Colorie chaque étoile comme "
     "une pensée que tu poses et que tu laisses briller seule, sans avoir à t'en occuper "
     "ce soir.",
     "Je fais partie de quelque chose d'immense.",
     "Bleu profond, indigo, or, blanc"),

    ("guide-oeil", "guide", "Le guide intérieur", "Le regard qui voit juste",
     "Au centre, un œil ouvert : non pas celui qui juge, mais celui qui voit clair. Pose-toi "
     "une question avant de colorier, puis oublie-la. Il arrive que la réponse se présente "
     "d'elle-même au détour d'un pétale.",
     "La réponse est déjà en moi.",
     "Indigo, turquoise, or, violet"),
    ("guide-etoile", "guide", "L'étoile qui guide", "Un point fixe dans le ciel",
     "Les voyageurs se repéraient à l'étoile. Ton étoile, ce sont tes valeurs profondes. "
     "Inscris-en une au crayon à papier dans le cercle central avant de colorier par-dessus : "
     "elle restera cachée dans le mandala.",
     "Je sais ce qui compte pour moi.",
     "Or, bleu nuit, argent, blanc"),
    ("guide-silence", "guide", "Le silence", "Om, le son primordial",
     "La syllabe Om représente le son d'où tout émerge et dans lequel tout retourne. Colorie "
     "ce mandala dans le silence complet, sans musique, et écoute ce qui reste quand le bruit "
     "s'arrête.",
     "Dans le silence, j'entends ma voix intérieure.",
     "Safran, or, blanc, bordeaux"),

    ("attraction-recu", "attraction", "J'ai, je suis, j'ai reçu", "L'état de celui qui a déjà reçu",
     "Au centre, des joyaux. Colorie-les comme si ce que tu souhaites était déjà là : avec la "
     "gratitude de celui qui a reçu. Visualise, ressens, puis lâche prise en refermant ton "
     "crayon.",
     "J'ai, je suis, j'ai reçu. Merci.",
     "Émeraude, rubis, saphir, or"),
    ("attraction-gratitude", "attraction", "La gratitude", "Le cœur qui remercie",
     "La gratitude transforme ce que l'on a en suffisance. Chaque cœur de ce mandala peut "
     "porter un merci : pour une personne, un instant, un repas, ton souffle. Compte-les en "
     "coloriant.",
     "Ma vie est remplie de raisons de dire merci.",
     "Rose, rouge doux, pêche, or"),
    ("attraction-abondance", "attraction", "L'abondance", "Le lotus qui donne",
     "Une fleur ne retient pas son parfum. Ce lotus généreux, aux pétales superposés, rappelle "
     "que l'abondance circule : on reçoit d'autant mieux qu'on sait donner.",
     "Je reçois et je donne avec joie.",
     "Or, vert, fuchsia, turquoise"),

    ("liberation-plumes", "liberation", "Plumes légères", "Ce qui ne pèse plus",
     "Une plume ne résiste pas au vent. Avant de commencer, pense à une chose qui pèse encore. "
     "À chaque plume coloriée, laisse-la s'alléger un peu, sans forcer : simplement lui "
     "permettre de partir.",
     "Je laisse partir ce qui ne m'appartient plus.",
     "Gris perle, bleu ciel, beige, blanc"),
    ("liberation-papillon", "liberation", "Le papillon", "La métamorphose",
     "La chenille ne sait pas encore qu'elle volera. Ce mandala célèbre les transformations, "
     "même celles qui font peur au début. Ose des couleurs vives sur les ailes : c'est le "
     "moment de te montrer.",
     "Je me transforme et c'est une bonne chose.",
     "Bleu morpho, orange, jaune, noir"),
    ("liberation-envol", "liberation", "L'envol", "Refermer un chapitre",
     "Les oiseaux prennent leur envol au-dessus d'une couronne de plumes. Le passé ne "
     "disparaît pas, mais il cesse de nous retenir. Colorie le centre en dernier, comme une "
     "porte qui se referme doucement.",
     "Je suis libre d'avancer.",
     "Bleu ciel, blanc, or, vert d'eau"),

    ("motivation-sommet", "motivation", "Au sommet", "Commencer sa journée en haut",
     "Le sommet ne s'atteint qu'un pas après l'autre. Les montagnes de ce mandala entourent un "
     "soleil levant. Colorie une montagne par jour si tu le souhaites : chaque petite victoire "
     "compte.",
     "Pas à pas, j'atteins mes sommets.",
     "Bleu ardoise, blanc neige, or, orange"),
    ("motivation-elan", "motivation", "L'élan", "La décision d'avancer",
     "Des pointes s'élancent vers l'extérieur, comme une énergie qui part du centre pour aller "
     "vers le monde. Choisis une action, même petite, que tu feras aujourd'hui, et écris-la "
     "dans ton intention.",
     "J'ai l'énergie de faire ce qui compte.",
     "Rouge vif, orange, jaune, magenta"),

    ("element-terre", "elements", "La terre", "La stabilité",
     "La terre porte, nourrit et stabilise. Le carré au centre est sa forme traditionnelle. "
     "Colorie pieds nus si tu le peux, en sentant le sol sous toi.",
     "La terre me porte et me soutient.",
     "Brun, ocre, vert mousse, terre cuite"),
    ("element-eau", "elements", "L'eau", "La fluidité",
     "L'eau contourne l'obstacle sans s'arrêter. Gouttes, vagues et tresses composent ce "
     "mandala. Laisse tes couleurs se fondre les unes dans les autres, en dégradés.",
     "Je m'adapte avec souplesse.",
     "Bleu, turquoise, vert d'eau, argent"),
    ("element-feu", "elements", "Le feu", "La transformation",
     "Le feu transforme tout ce qu'il touche. Ces flammes peuvent accueillir une intention : "
     "ce que tu veux voir changer dans ta vie. Colorie-les du rouge au jaune, de la base "
     "vers la pointe.",
     "Je transforme mes épreuves en lumière.",
     "Rouge, orange, jaune, or"),
    ("element-air", "elements", "L'air", "Le mouvement et le souffle",
     "L'air ne se voit pas, mais tout ce qui vit le respire. Les volutes de ce mandala suivent "
     "le mouvement du vent. Respire profondément entre chaque anneau.",
     "Je respire la vie pleinement.",
     "Bleu pâle, blanc, lilas, jaune paille"),
    ("element-ether", "elements", "L'éther", "L'espace qui contient tout",
     "L'éther est l'espace dans lequel les quatre autres éléments existent. Ce mandala est fait "
     "d'étoiles et de géométrie : laisse aussi certaines zones en blanc, comme des respirations "
     "de lumière.",
     "J'ai de l'espace en moi.",
     "Violet, bleu nuit, argent, blanc"),

    ("sacre-fleur-de-vie", "sacre", "La fleur de vie", "La géométrie de la création",
     "Dix-neuf cercles identiques se croisent et dessinent des pétales : c'est la fleur de vie, "
     "motif présent dans de nombreuses cultures. Colorie les pétales par familles de couleurs "
     "pour faire apparaître des étoiles cachées.",
     "Tout est relié.",
     "Or, turquoise, violet, rose"),
    ("sacre-yantra", "sacre", "Le yantra de l'harmonie", "Les triangles entrelacés",
     "Inspiré des yantras de l'Inde, ce dessin entrelace des triangles tournés vers le ciel et "
     "vers la terre. Le point central, le bindu, est le lieu de l'unité. Colorie de l'extérieur "
     "vers le centre, et termine par le point.",
     "Les contraires s'unissent en moi.",
     "Rouge, or, rose, bleu profond"),
    ("sacre-metatron", "sacre", "Le cube de Métatron", "L'équilibre des formes",
     "Treize cercles reliés entre eux par des lignes droites : tout l'équilibre de la "
     "géométrie dans une seule figure. Utilise une règle si tu le souhaites, et prends plaisir "
     "à découvrir les formes qui se cachent dans les croisements.",
     "Mon esprit est clair et ordonné.",
     "Bleu, argent, violet, or"),
    ("sacre-frequences", "sacre", "Les fréquences sacrées", "Le son devenu forme",
     "Les ondes concentriques évoquent les fréquences que tu retrouves dans l'application : "
     "174, 285, 396, 417, 432, 528, 639, 741, 852 et 963 Hz. Écoute l'une d'elles pendant "
     "que tu colories et laisse le son guider le choix des couleurs.",
     "Je vibre en harmonie avec la vie.",
     "Toutes les couleurs, du grave (sombre) à l'aigu (clair)"),

    ("finale-voix", "finale", "Ma voix intérieure", "Le retour à soi",
     "Voici le dernier mandala du livre : un lotus, des cœurs, et au centre la syllabe Om. "
     "Il rassemble tout le chemin parcouru. Colorie-le avec les couleurs que tu as le plus "
     "aimées au fil des pages : elles disent quelque chose de toi.",
     "J'écoute ma voix intérieure. Elle me guide.",
     "Tes couleurs préférées"),
]
