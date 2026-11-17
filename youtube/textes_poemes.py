"""Poèmes originaux pour la série « Poèmes pour s'endormir ».

Un recueil par ambiance. Chaque poème : (titre, [strophes]) ; une strophe est
un texte multi-lignes, affiché d'un bloc à l'écran pendant sa lecture.
"""

RECUEILS = {
    "neige": dict(
        scene="neige",
        titre="Poèmes pour s'endormir",
        sous_titre="sous la neige",
        poemes=[
            ("Ce que dit la neige", [
                "La neige ne dit rien.\nElle descend, simplement,\ncomme une main qui se pose\nsur une épaule fatiguée.",
                "Elle ne demande pas\nsi ta journée fut bonne.\nElle couvre les chemins,\nles erreurs, les traces,",
                "et le monde recommence,\nblanc,\net sans reproche.",
            ]),
            ("La lampe", [
                "Il y a une lampe allumée\nquelque part dans la nuit.\nTu n'as pas besoin de savoir où.",
                "Il suffit de savoir\nqu'elle existe.",
                "Ferme les yeux.\nLa chaleur est déjà là,\ndans ta poitrine qui se lève\net redescend,\ncomme la neige sur le toit.",
            ]),
            ("Inventaire du soir", [
                "Ce que j'ai fait aujourd'hui\nsuffit.",
                "Ce que je n'ai pas fait\nattendra la lumière.",
                "Je pose mes pensées\nune à une sur le rebord,\ncomme des gants mouillés\nqui sècheront pendant la nuit.",
            ]),
            ("Les sapins", [
                "Les sapins ne dorment pas.\nIls veillent.",
                "Debout dans le froid,\npatients comme des grands-pères,\nils gardent la colline",
                "pour que toi,\ntu puisses t'en aller doucement\ndans le sommeil.",
            ]),
        ],
    ),
    "aurores": dict(
        scene="aurores",
        titre="Poèmes pour s'endormir",
        sous_titre="sous les aurores",
        poemes=[
            ("Le ciel respire", [
                "Regarde.\nLe ciel respire.",
                "Il inspire du vert,\nil expire du violet,\nsans se presser,\nsans rien prouver à personne.",
                "Respire avec lui.\nUn peu de lumière qui entre.\nUn peu de nuit qui sort.",
            ]),
            ("Le lac", [
                "Le lac a gardé tout le jour\nses vagues et ses vents.",
                "Maintenant il se tait,\net dans son silence\nle ciel entier\nvient se regarder.",
                "Sois ce lac.\nLaisse tes pensées se poser.\nCe qui est beau\nviendra s'y refléter.",
            ]),
            ("Très loin au nord", [
                "Quelque part, très loin au nord,\nquelqu'un regarde le même ciel.",
                "Vous ne vous connaîtrez jamais.\nPourtant, ce soir,\nvous respirez la même nuit.",
                "Personne n'est vraiment seul\nsous un ciel pareil.\nToi non plus.",
            ]),
            ("Lâcher", [
                "Tu peux lâcher la journée\ncomme on lâche une corde\naprès avoir tiré longtemps.",
                "Tes mains s'ouvrent.\nTes épaules descendent.",
                "Le ciel, lui, continue\nde danser sans toi.\nEt c'est très bien ainsi.",
            ]),
        ],
    ),
    "pluie": dict(
        scene="pluie",
        titre="Poèmes pour s'endormir",
        sous_titre="sous la pluie",
        poemes=[
            ("La pluie travaille", [
                "La pluie travaille pour toi.",
                "Elle lave les rues,\nelle remplit les rivières,\nelle frappe doucement à la vitre",
                "pour te dire\nque tu peux t'arrêter.",
            ]),
            ("Les fenêtres", [
                "Dans la ville, une à une,\nles fenêtres s'éteignent.",
                "Derrière chacune,\nquelqu'un de fatigué\npose sa tête\net laisse la pluie\nparler à sa place.",
                "Tu peux faire pareil.\nLa pluie a assez de mots\npour tout le monde.",
            ]),
            ("Sans parapluie", [
                "Ce soir, tu n'as plus besoin\nde parapluie.",
                "Plus rien à protéger.\nPlus rien à retenir.",
                "Laisse la pluie couler\nsur les pensées du jour,\njusqu'à ce qu'elles deviennent\nlégères comme l'eau.",
            ]),
            ("Demain", [
                "Demain, les flaques\ngarderont un morceau de ciel.\nDemain, l'air sentira la terre.",
                "Mais demain est loin.",
                "Pour l'instant, il n'y a\nque ce lit, cette pluie,\net ton souffle\nqui ralentit.",
            ]),
        ],
    ),
}
