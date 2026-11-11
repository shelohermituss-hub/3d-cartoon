# Écarts entre `ANALYSIS.md` (références) et `docs/STYLE_NEW.md` (nouvelle doc)

Règle : quand les deux divergent, **STYLE_NEW gagne**. Ce tableau dit ce qui change.

| Sujet | ANALYSIS.md (ancien) | STYLE_NEW.md (appliqué) |
|---|---|---|
| Ombrage de la tête | jamais éclairée, blanc plat | 2.5D : sphère sur son disque, bord net, mince rim, ombre de la tête sur la poitrine |
| Taille de la tête | 160-200 px (plan moyen), 330 px (gros plan) | 300-430 px en plan de parole, 180-250 px pour le plan large du lieu |
| Premier plan | macro d'objet ou personnage en action | **un visage expressif**, jamais un décor vide ni un dos |
| Caméra | adoucie, sans tremblement | basse (poitrine-yeux), regard vers le haut, roulis 1-5°, champ 26-32°, `shake` 1 au repos |
| Rythme des coupes | médiane 1,3 s | une coupe toutes les 1,5-3 s (Dread Cuts : 1,2-3,5 s) |
| Format | 9:16 uniquement | 9:16 ou 16:9 |
| Mains | petites mitaines blanches | idem (pas de doigts, pas de gants) |

## Ce qui est en place (11/11/2026)
- `scripts/build/charkit.py` : fichier de description JSON → dessin. Carrures (slim, medium, stout, egg, pill, curvy, kid),
  legLen/armLen, couches de vêtements (chemise, chemisier, pull, gilet, veste, manteau, cardigan, cravate, nœud papillon,
  écharpe, ceinture, boutons, patte, poche, bretelles, tablier, sacoche), jupe, bande de pantalon, motifs (rayures,
  pois, tartan), 13 coiffures, chapeaux (beanie, ballcap, flatcap, officer, bowler, tophat, headband, + formes simples),
  lunettes, barbes, couleur hexadécimale avec repli par défaut, « sous un chapeau : cheveux courts ».
- Visages : les 13 yeux, 7 sourcils, 13 bouches de la doc + les 11 préréglages (et quelques autres).
- Vue de face et de trois quarts (planche de vérification : `python scripts/build/charkit.py sheet characters/X.json OUT.png`).
- Shading 2.5D lu depuis la lumière du décor (direction du soleil convertie dans l'espace caméra) ; chaud côté lumière,
  froid côté ombre, plancher, rim, ombre de la tête sur la poitrine ; l'encre n'est jamais ombrée ; les chapeaux sans rim.
- Caméra du plan d'ouverture : champ 28°, hauteur poitrine, légèrement vers le haut, roulis 3°, objet bas au premier plan.
- Post : lueur 0,3 au-dessus de 0,75, profondeur de champ (personnage net), étalonnage, vignette.

## Pas encore fait
- Animation (chronologies, gestes, marche, lèvres synchronisées, rythme du visage) : sections 2-3.
- Caméra à trajectoire `path`, les cinq jeux d'instructions, raccords entre lieux : section 4.
- Outils de revue (`film_sheet`, `render_frames`, `film_probe`, `film_check`) : à recréer, ils n'existent pas ici.
- Particules (> 1 000 grains de poussière), zones/states/steps de lumière.
- Dos dessiné des vêtements, jupes assises.
