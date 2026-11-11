# DOCUMENTATION STYLE « 3D CARTOON SHORTS (NEW) »

Texte de référence fourni par l'auteur (11/11/2026). Il prime sur `ANALYSIS.md` quand les deux divergent
(voir `docs/ECARTS.md`).

## 0. Principe général
- Format : 9:16 (1080×1920) ou 16:9 (1920×1080), 30 images par seconde.
- Objectif : un spectateur sur téléphone ne doit pas deviner qu'un outil l'a fait.
- Ordre d'importance : les personnages d'abord, puis la caméra, le décor, la post-production, la lumière.
- Pur en t : chaque image est une fonction du temps seulement. Pas de hasard libre, pas d'état entre les images. On peut sauter n'importe où dans le film et obtenir la même image.
- Les cinq passes : Build (personnages, jeu, décor de base), Caméra, Environnement, Post-traitement, Shading. Chaque passe garde ce que les autres ont fait.
- Règles dures :
  - Le film s'ouvre sur un visage expressif, jamais sur un décor vide ni un dos.
  - Tout ce qui est dans un lieu est dans chaque plan de ce lieu.
  - Un accessoire qui saute à l'écran fait échouer le film.
  - On n'écrit jamais dans l'audio.

## 1. STYLE DU PERSONNAGE
### Anatomie
- Tête : ronde, blanche, grosse, avec un contour d'encre épais. Sa taille ne change jamais. On ne la grossit ni ne la réduit.
- Visage : des courbes noires qui changent d'un dessin à l'autre, sans transition.
- Torse : en forme d'œuf, avec des vêtements dessinés dessus.
- Membres : bras et jambes fins, comme des bâtons d'encre.
- Jamais : pas de nez, d'oreilles, de doigts, de couleurs de peau, de gants ni de bottes.

### Un personnage = un fichier de description
Il se décrit à partir d'une phrase (âge, carrure, vêtements, une couleur propre, un signe distinctif).

| Mot dans la phrase | Réglage |
|---|---|
| mince, élancé / moyen / trapu, rond | torso.body.build : slim (largeur 0,60-0,72), medium (0,75-0,87), stout (0,90-1,0), curvy, egg, pill |
| enfant / ado | build: 'kid' avec jambes 0,72 et bras 0,62 / jambes ~1,08 |
| grand / petit | limbs.legLen 1,42-1,45 / 1,1-1,15, toujours écrire aussi armLen (0,9-1,0) |
| chemise, chemisier, pull, gilet, veste, manteau | outfit.layers[], du plus intérieur au plus extérieur |
| tablier, cravate, nœud papillon, écharpe, ceinture, boutons, poche, bretelles | une couche après le vêtement qui les porte |
| rayures, tartan, tweed, pois | pattern sur un seul vêtement |
| jupe, robe | outfit.skirt : longueur genou ou cheville, forme évasée ou cloche |
| pantalon, jean, short | la couleur de la bande du bassin (outfit.trousers) |
| cheveux | hair.style : bald, bald_sides, receding, short, side_part, curly, bob, long, bun, ponytail, pigtails, messy, spiky |
| barbe, moustache | facialHair.kind : full, goatee, stubble, moustache, walrus, handlebar, mutton |
| lunettes | glasses.kind : round, square, half, sun, cateye, oval |
| chapeau | hat.kind : ballcap, flatcap, beanie, headscarf, strawhat, chef, bowler, tophat, officer, headband, none |
| grands yeux, gros sourcils | face.eyeSize 0,97-1,04, browThick 1,3-1,5 |

### Règles d'écriture
- Une couleur forte par personnage.
- Pas deux personnages principaux avec le même chapeau et la même couleur.
- Un héros a 3 à 6 détails sur le torse, un figurant 1 à 3.
- Un seul motif chargé par personnage, peu contrasté sauf le tartan.
- Sous un chapeau : cheveux courts.
- Toutes les couleurs s'écrivent en hexadécimal à 6 chiffres. Une valeur erronée retombe sur la couleur par défaut.

### Carrures (valeurs du moteur)
- slim : largeur 0,64, hauteur 0,90.
- medium : 0,80, 0,92.
- stout : 0,96, 0,95.
- egg : 0,94, 0,98.
- pill : 0,87, 1,0.
- kid : 0,64, 0,56, avec jambes et bras plus courts.

### Vêtements disponibles
Chemise, chemisier, pull, gilet, veste, manteau, tablier, cravate, nœud papillon, écharpe, ceinture, boutons, poche, patte de boutonnage, bretelles, jupe. Chaque vêtement a un dos dessiné. Les jupes s'adaptent automatiquement quand le personnage s'assoit.

### Vérification
Rendre le personnage de face et de trois quarts. La silhouette doit le distinguer des autres, les lunettes et la barbe doivent rester dans le contour, aucun cheveu au-dessus d'un chapeau.

## 2. VISAGES
Un visage = trois parties qui changent sans transition : yeux, sourcils, bouche.

- Yeux : open, smug (paupière plate, sûr de soi), half, blink, arc (heureux), wide (choc), wince (douleur), angry, sad, look_l, look_r, stare, pinpoint.
- Sourcils : on, off, up, down, knit, worried, quizzical.
- Bouche : rest, smile, frown, smirk, D, Dtongue, crescent (grand sourire), grid (dents serrées), o, wide (cri), flat, tight, gulp.
- Préréglages d'expression (expr) : fear, terror, dread, gulp, confused, relief, hope, dawning, horror, stare, blank.

Parole :
- Les lèvres se synchronisent automatiquement. La bouche est petite quand on parle, et c'est le corps qui joue.
- Cri : un mot terminé par « ! » donne les grandes formes de bouche.
- Les yeux restent fixes pendant la parole.

Rythme du visage (appliqué par le moteur) :
- Yeux et sourcils changent au plus une fois toutes les 8 images.
- Les sourcils restent verrouillés pendant une phrase, sauf un lever sur le mot le plus accentué.
- Un clin d'œil dure 2 images et il y en a au moins 7 images ouvertes entre deux.
- Le sourire aux yeux fermés (arc) est un accent de 6 à 10 images dans un dialogue. Pour le garder : hold: true.

Réglages par personnage : écart des yeux, taille des yeux, hauteur des yeux, couleur des yeux, épaisseur des sourcils, taille et largeur de la bouche. Ils sont limités à une plage pour que tous les visages restent dans la même main de dessin.

## 3. ANIMATION DES PERSONNAGES
### Les lois
1. Tout se joue sur des images entières, sans flou de mouvement.
2. Trois vitesses : le visage change instantanément, les gestes durent 2 à 4 images puis s'arrêtent, le corps bouge en environ 10 images.
3. Les impacts s'arrêtent net.
4. Les arrêts sont immobiles : pas de respiration, pas de balancement. La vie vient du visage et de la caméra.
5. Le visage d'abord, le corps une image après, la tête en tête.
6. Pas de hochement de tête pendant qu'on parle.

### La chronologie d'un personnage
Elle contient : où il se tient au départ, des valeurs de base, des clips (gestes), la marche, les expressions, les paroles, les clignements, le regard, les pieds posés, et l'assise.
Ordre des couches : repos, base, visage, racine de marche, clips, jambes de marche, pieds posés, regard.

### Pour chaque réplique
1. Le visage d'abord : l'expression de celui qui parle, juste avant la phrase. La réaction d'un auditeur, 1 à 3 images après le mot déclencheur.
2. Une action de corps par réplique, liée à un mot, une image après le visage, puis un arrêt immobile. Chaque mouvement de bras a une fin : un maintien suivi d'un retour, un clip suivant sur la même main, ou une passation.
3. Réactions fortes : un nouveau visage avec wide, wince, angry ou sad déclenche aussi un recul, un sursaut, une inclinaison ou un affaissement du corps 2 images plus tard. On le coupe avec react: false pour un moment neutre.
4. Regard : viser la personne, mais 2 à 3 unités vers la caméra, sinon le visage tourne de profil et disparaît. Les pupilles se posent sur la cible une image avant la réaction.

### Gestes disponibles
- wave, point, shrug, akimbo, hand_to_temple, brace, talk_hands, carry.
- shock_pop, shock_jump, wince, head_turn, look_at, turn.
- lean_over, lean_back, hop_bounce, react (recul, penché, affaissé).
- sip, eat, bite, pick_up, put_down, raise_prop, shake, sign.
- glasses_lower, glasses_off, glasses_on.
- grab_collar (se tenir à 1 à 1,2 unité de la cible).
- sit_on, sit_down, stand_up, kneel, cane_twirl, cap_lift, hat_launch, saw_stroke, sledge_swing.

### Marche
- Pas de 9 images, longueur de pas 1,25 à 1,5 fois la longueur de jambe.
- Le corps monte et descend à chaque pas, comme un balancement de poids.
- Les bras se balancent à l'opposé des jambes.
- Course : pas de 6 images, avec une envolée de 2 images où les deux pieds quittent le sol.
- Arrêt : les pieds se posent côte à côte, le bassin se calme, puis le personnage est immobile.
- La marche doit finir avant la réplique qui en a besoin.
- Sorties en trois quarts : jamais plus de 10 images de dos.

### Hauteur et lieux
- Un personnage peut flotter, tomber, sauter, ou se tenir sur un pont. Le monde n'a pas de collision : on écrit la hauteur.
- Un personnage dans deux lieux se fait avec place, pas avec deux copies.
- Un changement de lieu en plein plan est une téléportation visible : il doit tomber sur une coupe.

### Mise en scène pour les visages
- Le visage ne se dessine que si la tête est à moins de 95° de la caméra. Garder les orateurs entre 20° et 60°.
- Deux personnes qui se parlent : à 1,5 à 1,8 unité l'une de l'autre, toutes deux tournées de 45° à 70° vers la caméra.
- Ne jamais ouvrir sur un personnage de dos.

## 4. ANGLES DE CAMÉRA
### Grammaire de base (Build)
1. La caméra est sur celui qui parle. On ne coupe vers un auditeur que pour une réaction, puis on revient.
2. Une coupe toutes les 1,5 à 3 s, sur le début d'une phrase ou une action, avec un angle ou une taille clairement différents.
3. Un personnage est entièrement dans le cadre ou entièrement dehors, jamais à moitié.
4. Les actions importantes se passent à l'écran, pas pendant une coupe. Le plan démarre au moins 0,3 s avant l'action.
5. Pas de changement de visage ni de geste dans les 3 images d'une coupe.
6. Personnages grands : tête de 300 à 430 px de large sur les plans de parole, un plan large par lieu (180-250 px).
7. Basse : caméra entre la poitrine et les yeux, regard légèrement vers le haut, jamais d'en haut.
8. Toujours en mouvement : poussée de 8 à 12 %, orbite de 10 à 20°, ou suivi d'un marcheur. still: true pour un vrai arrêt.
9. Roulis de 1 à 5°, qui dérive d'un degré sur le plan.
10. Profondeur au premier plan : un objet bas dans le tiers proche, deux personnes en profondeur, ou par-dessus l'épaule.

### Chiffres de cadrage (1080×1920)
- Taille de la tête en px = 4160 / distance, pour un champ de 26°.
- Un plan à deux personnes doit empiler les profondeurs, ou garder la paire à environ 1,9 unité.
- Trois personnes : têtes de 250 px minimum, décalées, à 14-16 unités.
- Solo : centre de la tête entre 35 et 65 % en largeur, 34 à 50 % en hauteur.

### La caméra à trajectoire (path)
Un mouvement continu à travers des clés. Chaque clé donne une position, une cible et un champ.
- Les clés peuvent être sur un personnage ({ who, offset }) ou sur un objet en mouvement.
- stop: true met la vitesse à zéro sur une clé.
- Tremblement (`shake`) : 1 au repos, 2 à un sursaut, 3 en panique, 0,5 quand on retient son souffle. Marche (`walk`) : de 0 à 1, le balancement de celui qui tient la caméra.
- Balayage rapide : deux clés espacées de 5 à 7 images, avec une clé du milieu visant de côté.
- Au-dessus des têtes : passer à au moins 1 unité de toute tête, ou rester à 4 unités et plus.
- Vols : ne jamais viser un mur vide, garder le prochain sujet dans le cadre.

### Raccords entre lieux sans coupe visible
Deux plans path dont la dernière et la première image se ressemblent.
- Vers l'avant dans une surface : voler vers un mur jusqu'à ce qu'il remplisse le cadre, couper, sortir d'un autre mur en mouvement.
- À travers un mur en arrière : une image passe de la pièce à l'extérieur, à vitesse ça se lit comme un passage.
- Surface de l'eau : sortir en arrière en regardant vers le bas marche bien, entrer vers l'avant donne un flash.
- Balayage : même ciel des deux côtés, tournant dans le même sens.
- Chevaucher un objet en mouvement.
- Un passage dure moins de 8 images : 5 images sombres se lisent comme un passage, 8 sont trop longues.

### Les cinq jeux d'instructions de caméra
| Nom | Sensation | Recette | Convient à |
|---|---|---|---|
| Dread Cuts | Coupes sèches sur les mots, caméra basse qui regarde vers le haut, horizon incliné qui dérive | Coupe toutes les 1,2 à 3,5 s, champ 26-32°, hauteur poitrine à tête, poussée de 10-15 % ou orbite de 10-15° à chaque plan, roulis de 2 à 5° qui change de côté, arrêt complet seulement pour un silence. Le dernier plan pousse sur celui qui sait | Dialogue, tension, horreur. C'est le choix par défaut |
| One Take | Une seule caméra qui flotte, survole les têtes, traverse une porte | Un seul plan path pour tout le film. Les vols atterrissent sur le premier mot de la phrase, ils vont par-dessus les têtes ou à travers une porte | Histoires dans un seul espace, poursuites |
| Found Footage | Quelqu'un filme avec un téléphone, grand angle, tremblante | Champ 46° à 4-5 unités du visage. Balayage rapide entre orateurs, coupe seulement là où la bande sauterait. Zoom de 46° à 18° pour lire au loin. Le personnage qui filme n'apparaît jamais | Horreur, mystère, récits « j'y étais » |
| The Watcher | Quelque chose observe | Très longue focale (9-16°) depuis 15-25 unités, parfaitement de niveau, jamais plus vite qu'un rampement (environ 0,5 unité/s). Caché derrière un cadre de porte. Peu de coupes, arrêts longs, finit serré sur un visage | Angoisse, filature, secrets |
| Through the Steel | « La caméra va où va le son » | Trouver ce qui traverse les murs (un son, un signal, un appel) et faire voyager la caméra avec. Raccords sur des images identiques des deux côtés, passages de moins de 8 images. Entre les passages, rester près des visages, champ 26°, poussée lente | Histoires en plusieurs lieux reliés par un fil |

Un jeu d'instructions est une sensation et une logique, jamais des coordonnées à recopier. On l'invente pour chaque film. Combiner est bienvenu : Through the Steel est né en mélangeant les vols de One Take et les coupes de Dread Cuts.

### Revue
- film_sheet du film entier pour le rythme des coupes et les visages.
- film_sheet avec strip à plein débit sur chaque mouvement rapide : une caméra dans une tête n'apparaît que sur une image.
- render_frames sur la première image de chaque plan.
- film_probe pour les plans et la garde des accessoires.
- Déplacer les effets sonores liés aux coupes si la nouvelle caméra les a déplacées.

## 5. PASSE DE SHADING
### But
Faire que les personnages et les accessoires aient l'air éclairés par la scène, pas collés par-dessus. Chaque scène demande son éclairage : dramatique, doux, propre, lumière dure du dessus pour un moment tendu.

### Ce qui doit rester vrai
- Les personnages gardent leur dessin, leurs couleurs et leurs expressions.
- Les visages restent la première chose qu'on voit.
- Le jeu et les chronologies ne changent pas.
- Aucun scintillement. Les ombrages bougent doucement dans un plan.

### L'outil
Il lit les lumières du décor comme des données. Les personnages sont en 2.5D, donc la forme vient du dessin : la tête ombrée comme une sphère sur son disque, le corps comme un cylindre, une ombre dessinée nette, un mince bord de lumière, des jambes plus sombres, l'ombre de la tête sur la poitrine.
Réglages par lieu : exposition, saturation, teinte de la lumière principale, dureté, lumière de contour (rim), lumière basse (low), plancher d'ombre (floor), minimum de lumière (keyMin), lumières supplémentaires, comportement du métal (metal).
Il y a aussi zones, states et steps pour les changements de lumière sur les coupes.

### Ce qui fait que ça marche
- Lumière et ombre en deux couleurs par lieu : une lumière chaude du côté de la lampe, une ombre froide de l'autre côté. C'est l'essentiel de la passe.
- Un plancher par lieu pour que les visages ne tournent pas à la boue.
- Une lumière mourante perd sa couleur, elle ne reste pas orange.
- Le métal garde sa couleur : on désature la lumière dessus.
- À contre-jour, le visage est entièrement du côté de l'ombre, donc l'ombre porte la chaleur.
- Les chapeaux s'ombrent avec la tête, sans lumière de contour.
- Les anneaux et les éclairs sont de la lumière : on ne les ombre jamais.
- Plafonner la lumière de remplissage sous la lumière principale, sinon l'ombre dessinée se retourne.
- Les accessoires gardent seulement un reflet net, sinon un disque plat devient une sucette.

### Scintillement : comment il a été réglé
Une lumière qui clignote orientait l'ombre, donc les bords durs basculaient au rythme du clignotement. Correction intégrée : la direction ignore le clignotement, les régions se fondent sur la distance, la lumière se lit sur une fenêtre autour de t, le clignotement n'atteint que le niveau, doucement. Votre part : mettre des steps sur les changements durs, adoucir les ambiances sur une caméra sans coupe, regarder les bandes.

### Vérifications
- film_check shade_jumps : les sauts d'ombrage par plan et par personnage.
- film_check calm : sauts de lumière quand la caméra est immobile.
- film_check same : dessins, jeu, accessoires et plans inchangés.
- Puis des images consécutives en plein format sur les pires endroits.
- Si quelque chose paraît bizarre, vérifier d'abord la passe précédente.

## 6. LES AUTRES PASSES, EN BREF
- Environnement : Blender construit le décor une fois à partir d'un script, en fichiers .glb par lieu. Une équipe de trois agents : Blender (le modèle 3D), textures (les images), intégration (la lumière et le rendu en direct). Il faut de la profondeur dans chaque plan, du détail près de la caméra, des lumières visibles et des surfaces qui racontent quelque chose.
- Post-traitement : brume qui grandit avec la distance, profondeur de champ, lueur sur les lumières, particules adaptées au lieu, étalonnage de couleur et vignette par lieu. Les personnages restent nets.
- Chiffres de référence : densité d'air environ 0,03, lumière dans l'air 0,25-0,3, ouverture du flou de profondeur 26-30, lueur 0,3 au-dessus de 0,75, plus de 1 000 grains de poussière, étalonnage de 10 à 15 %.
