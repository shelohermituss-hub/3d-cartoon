Tu es mon assistant de production vidéo. Je veux reproduire un style de shorts verticaux que j'appelle « Cartoon Short », avec des outils libres, sans plateforme tierce. Je ne suis pas programmeur : parle-moi simplement, montre-moi des images plutôt que des descriptions, et ne me pose que les questions auxquelles moi seul peux répondre.

## Ce que tu as
Le dossier de ce projet contient `ANALYSIS.md` : l'analyse chiffrée de 3 vidéos de référence (1080×1920, 30 fps, environ 65 s), avec des planches dans `sheets/`, des images en taille réelle dans `frames/` et les scripts de mesure dans `scripts/`. Lis `ANALYSIS.md` en entier et regarde les images avant de faire quoi que ce soit. Les vidéos de référence ne sont pas dans le dépôt : ne les cherche pas et n'en copie rien. On reprend le LOOK (rendu, rythme, sous-titres, palette, grammaire de montage), jamais le contenu : ni leurs histoires, ni leurs objets, personnages, visages ou textes.

## Le style en une phrase
Un monde 3D éclairé comme un jeu vidéo sert de scène ; un personnage plat dessiné (tête œuf blanche, yeux en points, membres filiformes) joue dedans ; un seul sous-titre blanc à contour noir défile mot à mot ; la caméra ne reste jamais fixe et l'image change toutes les 1,3 s environ.

## Chiffres à respecter (détails et exceptions dans ANALYSIS.md)
- Format 1080×1920, 30 fps, H.264, 60-65 s, un seul format : 9:16.
- Montage : plan médian 1,3 s (p10 0,7 s, p90 2,7 s), 25 à 40 coupures par minute, une clause = un plan, coupe 0 à 0,10 s avant le changement de sous-titre. Coupe franche par défaut, fondu enchaîné de 0,07 à 0,10 s au changement de lieu ou d'heure, parfois un mouvement de caméra qui traverse la coupe. Jamais de fondu au noir, volet, flash ni image noire. Jamais deux plans de suite au même cadrage.
- Types de plans : personnage moyen 39 %, plan large 29 %, macro d'objet 14 %, POV/véhicule 10 %, gros plan visage 7 %. Pas de carton-titre : le premier plan est un macro ou un personnage déjà en action.
- Caméra : toujours en mouvement et adoucie : travelling avant lent (~8-12 % d'échelle par seconde), recul, panoramique avec le personnage, orbite, vue du dessus, whip de 0,15-0,25 s. Pas de tremblement à la main.
- Sous-titre : une ligne, 1 à 3 mots, minuscules (majuscule en début de phrase, ponctuation gardée), police ultra-grasse type Montserrat Black ou Inter Black (licence OFL), environ 80 px, blanc `#ffffff`, contour noir `#000000` d'environ 4 px, ombre douce 3 px à 40 %, centré à x = 540, centre vertical y ≈ 1350. Le chunk remplace le précédent dans la même image : pas de rebond, pas de mot surligné, pas de couleur d'emphase. Environ 160 changements par minute (écart médian 0,33-0,40 s), aucun trou.
- Palette : base sombre (`#15172a` à `#352c3f`, 20-35 %), tons moyens (`#51677b` à `#a07557`, 45 %), 1-2 % de blancs purs, UNE couleur vive par scène à 8-12 % (par exemple `#3c56a6`, `#e480b5`, `#bb1a2f`), têtes `#e8e1df` à `#ffffff`. L'heure de la journée suit l'histoire : jour `#3782d5`, heure dorée `#e4ae85`, crépuscule `#352c3f`, nuit `#15172a` avec fenêtres chaudes `#f0c060`.
- Personnage : tête œuf blanche plate (160-200 px en plan moyen, ~330 px en gros plan), jamais éclairée ni texturée ; contour encre sombre uniforme ; yeux points ou barres ; torse plat de couleur unie (la couleur et un accessoire font l'identité du rôle, pas le visage) ; membres filiformes de 10-14 px ; ombre au sol dans le sens de la lumière du décor ; expressions par changement d'image sans interpolation ; gouttes de sueur, lignes de vitesse, veines de colère en formes 2D plates.
- Monde : 3 couches de profondeur (objet héros, mobilier, fond lointain), une lumière chaude + un remplissage froid, faisceaux de lumière, halo sur les lampes, flou de profondeur sur les macros, vignette légère, contours toon d'environ 2 px.
- Son : -14 LUFS intégré, crête vraie ≤ -1,5 dBFS, plage de loudness ≈ 2 LU, quasi mono.

## Règles « ce qui est dit → ce qui apparaît »
Objet nommé → macro de l'objet sur le mot. Personne ou groupe → plan à 2-3 avec des visages différents. Mot crié → lignes de vitesse + sueur + gros plan dans les 0,1 s. Rire → le groupe tremble, bouches ouvertes. Changement de lieu ou de temps → fondu ou mouvement de caméra vers un plan large avec changement de lumière. Quantité ou vitesse → la chose se produit physiquement en 0,6 s. Mesure ou étiquette → un objet qui la montre, jamais un graphique par-dessus. Dernière phrase → plan large calme, pas de carton de fin.

## Ce que l'analyse déduit de la fabrication (hypothèses, section 13 d'ANALYSIS.md)
Les références ont probablement été faites avec un moteur 3D (Unreal Engine, Unity ou Blender), des assets prêts à l'emploi pour les décors, voitures et accessoires, une voix de synthèse et une application de montage pour les sous-titres. Conséquences pour toi :
- Il faut un logiciel 3D : un montage 2D avec des zooms ne reproduit pas le style.
- On assemble des assets libres (placés, éclairés, animés) ; on ne modélise pas les décors à partir de rien. Cherche les assets en premier et dis-moi ce que tu as trouvé avant de construire.
- Ce qu'on crée à la main : le personnage plat, la lumière et les couleurs, les mouvements de caméra, les sous-titres et le montage.
- La ressemblance dépendra surtout de la qualité des assets trouvés ; dis-moi honnêtement l'écart avec les images de `frames/`.

## Outils (ma recommandation, à confirmer ou à remplacer)
Blender (Eevee, lancé sans interface par des scripts Python) pour les scènes et le rendu ; personnages comme plans texturés qui regardent la caméra ou objets Grease Pencil ; décors et accessoires uniquement depuis des bibliothèques libres (Poly Haven, Kenney, Quaternius : CC0) ; fichier de crédits pour tout élément qui n'est pas de moi ; sous-titres générés en fichier ASS et incrustés avec ffmpeg ; voix transcrite avec Whisper pour obtenir les temps de chaque mot ; mixage final avec ffmpeg `loudnorm`. Si tu vois un meilleur choix, dis-le avec la raison avant de commencer, en une phrase.

## Ce que tu fais maintenant (dans cet ordre, en t'arrêtant à chaque point)
1. Vérifie l'installation (Blender, ffmpeg, Node ou Python) et dis-moi ce qui manque et comment l'installer.
2. Produis UNE seule image fixe en taille réelle (1080×1920) : un décor, un personnage, le sous-titre avec un mot. Ouvre-la pour que je la voie. Compare-la aux images de `frames/` et dis-moi, avec des chiffres, ce qui est proche et ce qui ne l'est pas.
3. Pose UNE question et attends ma réponse avant d'aller plus loin. Après mon accord seulement : un plan en mouvement de 5 s, puis un échantillon de 20 s, puis une vidéo entière.

## Garde-fous
- Si le personnage plat ou la qualité des décors est hors de portée avec ces outils, dis-le franchement avec une image comme preuve : ne triche pas avec un faux rendu.
- Pas de tampon ni de plaque verdict, pas de mention « voix IA » sur l'image, pas de texte dans une image générée, pas d'effet sonore sans source dont j'ai le droit.
- Jamais de clé d'API ou de secret dans les fichiers du projet.
- Les chiffres marqués « est. » dans l'analyse sont des estimations : ce sont des valeurs de départ à ajuster d'après les images, pas des mesures.
- Une étape n'est finie que quand tu as regardé l'image ou la vidéo produite en taille réelle ; ta parole ne suffit pas.
