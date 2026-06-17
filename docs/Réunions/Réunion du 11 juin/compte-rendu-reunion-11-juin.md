# Compte rendu — Session de travail PRBE du 11 juin 2026

_Source : transcript Fathom (https://fathom.video/calls/707467582, ~55 min) + notes prises par Luc pendant la séance, fusionnées ici._

**Participants :** Niko, équipe PRBE (Luc, Alex), encadrants (Francesco Ciampi, Thierno Diallo)
**Type :** session de travail 14 h (3-4 h, licence RoboDK temporaire fournie) — enregistrement Fathom de ~55 min

> **Note transcription :** Fathom a étiqueté tout le monde « Nikoloz Khachidze » et l'audio est très dégradé (mélange FR/EN, traduction auto). À lire avec recul. Décodages : **« MLX » / « Alise » = la ligne ALIX**, **« Submega » = Supméca**, les « Fathom » répétés = l'outil d'enregistrement qui bave dans le texte. Les notes de Luc ont servi à recouper et préciser les points ambigus.

---

## 1. Licence RoboDK

- Licence temporaire OK, aucun souci pour la session. (Rappel : c'est cette licence qui permettait de travailler sur place.)

## 2. Bug de l'« éclaté » — toujours présent, contourné

- Le bug du mannequin qui explose à la réouverture **est toujours là**. Niko montre **la solution Python** (`fix_reattache_segments.py`) qui « remet tout le corps en place » — présentée comme un contournement, pas une correction de la cause racine.
- Les encadrants découvrent qu'il y a **des scripts Python** embarqués et tiquent un peu (« pas normal ça »).
- Fausse alerte pendant la démo : des vidéos qui « ne marchaient plus » → **c'était juste le réseau** (cf. point 3).

## 3. Dépendances en ligne — à vérifier et documenter

- Demande encadrants : **vérifier si le code dépend de fonctions / vérifications en ligne** (le souci réseau pendant la démo a mis la puce à l'oreille).
- Pas de liaison spécifique au GitHub. Librairies citées : `math`, `sys`, `pathlib`, `robolink/robodk`.
- **À faire :** tester l'exécution **hors-ligne** et **documenter les dépendances en ligne** s'il y en a.

## 4. Marche sur trajectoire — comprendre et expliquer la courbe

- La marche **suit bien la trajectoire** ; clés **rapprochées** → démarche plus **naturelle**, moins militaire. Validé (« très très bien »).
- Demande encadrants + Luc : **savoir expliquer comment le mannequin suit la courbe**. Le mécanisme à décrire :
  - **Discrétisation de la courbe** (objet `AddCurve` : prend premier/dernier points, découpe en ~10 points, échantillonne par segment),
  - **puis déplacement des points** : le mannequin est déplacé le long des points discrétisés.
- Savoir aussi **comment modifier la courbe** et **comment la courbe se rapporte au déplacement** (lien courbe ↔ mouvement).
- Esprit : *« on n'a pas besoin de comprendre tout le code, mais la logique du code »* — sinon impossible à modifier et de répondre aux questions en soutenance.
- Pas de demande de modifier la courbe ; juste **être capable de l'expliquer** (et de savoir comment on la modifierait).

## 5. Tâche bras (pick & place) — retours et degré de liberté

- Scénario montré : le bras prend une pièce et se déplace (vidéo + démo live).
- **Degré de liberté manquant** identifié (poignet) pour un mouvement vraiment naturel. À valoriser dans le rapport : **dire explicitement que le bras n'est pas naturel avec tel degré de liberté**, puis **expliquer les choix et les solutions** retenus (« testé sans ce DDL → trajectoire non faisable / pas naturelle → perspective : ajouter un DDL »). Les encadrants **ne demandent pas** de l'ajouter, juste de le documenter et de justifier.
- **Coude :** la v3 (coude qui part en arrière) est la bonne direction vs l'ancien « coude qui sortait dans le mauvais sens ». Reste **une collision à l'arrière** à surveiller, mais c'est déjà bien mieux.
- **Ergonomie :** certaines postures ne sont pas tenables longtemps → c'est de l'ingénierie qui vient **après** ; l'objectif d'abord = **comprendre comment atteindre la pièce**.

## 6. Position de la pièce — la trouver et l'externaliser

- Question clé des encadrants : *« si je change la position de la pièce, le bras s'adapte-t-il ? »* → **démo live concluante** : Niko change les coordonnées, le bras va chercher la pièce ailleurs → **ça s'adapte**.
- À expliquer dans le rapport : **comment le bras trouve la position de la pièce** (quel type d'information / de paramètre il utilise pour la localiser).
- **Définition des paramètres** : montrer que si l'on change la **position d'une pièce** (y compris celle tenue par la main), **la trajectoire s'adapte aussi**.
- **Exigence :** pouvoir changer la position de la pièce **sans toucher au code de trajectoire** → externaliser via **fichier / interface externe**.
- **Point plus large** (souligné par Luc) qui découle du précédent : identifier **quels types de paramètres on peut sortir du code** pour les modifier **tout en gardant un code toujours fonctionnel** (exemple : la pièce saisie par le bras). Bien lister ces paramètres externalisables.
- **À tester** avec plusieurs positions de pièce + **documenter dans le rapport**.

## 7. `Position_0` — validé

- Script `Position_0.py` (remise au garde-à-vous) montré : utile entre deux animations (marche → tâche bras ne repartait pas du bon point). Encadrants : *« des choses qui marchent, très bien »*.

## 8. Intégration dans la ligne ALIX

- Prochaine étape jugée intéressante et **à faire** : **intégrer le mannequin simplifié dans la ligne ALIX**.
- **Recentrer sur le `human frame`**, puis le placer dans l'espace avec une trajectoire définie.
- Si ça coince, réutiliser les modèles déjà existants. Permet d'avoir des références spatiales pour définir des trajectoires.

## 9. Test sur le vrai robot + vidéos

- **Tester la simulation sur le robot réel**, capturer **des vidéos courtes** pour la présentation.
- Verdict encadrants : **la modélisation est finie** → le temps restant doit servir à **écrire le rapport** et préparer la soutenance.

---

## 10. Rapport — consignes et structure

**Ne PAS mettre de code brut dans le rapport.** À la place, des **schémas / formes** qui montrent ce que fait le code.

### Logique de rédaction (cadrage Luc)
- Pour **chaque problème rencontré** : exposer **le problème, pourquoi il survient, puis la solution**. Exemples à traiter explicitement : la **tâche** bras, le **bras**, la **saisie**, la **courbe**.
- Décrire **comment on définit les paramètres** (et lesquels sont externalisables — cf. point 6).
- La qualité prime sur la quantité.

### Structure attendue (encadrants + Luc, concordantes)
1. **Contexte + objectifs** : ce qu'est l'activité, le périmètre, le cadre, l'expérimentation, les objectifs.
2. **Cahier des charges** : comment on l'a défini (pas « formation »).
3. **État de l'art** : approches existantes (basées apprentissage, etc.) pour situer la proposition.
4. **Modèle conceptuel** : comment on résout le problème + nos propositions (ex. comment modéliser un mannequin). Inclure :
   - le **schéma cinématique** (partie mathématique),
   - le **schéma de développement** (création mannequin → modèle 3D → génération du mouvement naturel → définition de la trajectoire → adaptation du mouvement à la trajectoire),
   - l'**arborescence des repères** (chaque repère associé à une partie du corps, ordre spécifique).
   - **Schémas et formes, pas de code pur.**
5. **Développement.**
6. **Tests et résultats** : problèmes identifiés + corrections ; ce qui est résolu (montré), ce qui ne l'est pas (mis en perspective).
7. **Conclusions** : revenir sur les objectifs annoncés (atteints / non atteints), montrer les aspects **positifs et négatifs**, ce qu'on a fait ou pas fait + perspectives.

- **Longueur :** la qualité prime sur la quantité — **pas besoin de 40 pages**, ne pas remplir pour remplir.

## 11. Poster, présentation, rapport — trois niveaux de détail

- Rapport / présentation / poster = **même contenu, quantité d'info décroissante** : **rapport** (très détaillé) → **présentation** (moins détaillée) → **poster** (très synthétique).
- Le poster montre **le type d'activité**, pas les détails spécifiques : titre, auteur(s), puis les grandes parties.
- **Les encadrants envoient un template de poster + des guidelines de présentation.** (M. Moro plus expert sur les posters, validation en équipe.)

## 12. Présentation — consignes

- **Durée :** ~30 min (max 30-35), compter ~1 min par image.
- **Première page :** nom, titre de l'activité, date.
- **Slides de séparation de chapitres** (slide titre entre les parties) — bonne organisation, mais **pas de sous-sections** (trop lourd).
- **Peu de texte** par slide ; police ~**16-18**.
- Même plan que le rapport : contexte → cahier des charges → modèle conceptuel → développement → conclusion.
- **Template Supméca** utilisable pour les slides (ou Canva).
- **Vidéos :** courtes (**10-15 s**) intégrées dans les slides, **pas en haute résolution / poids léger** (240p suffit). **Ne pas** mettre une vidéo de 3 min dans le diaporama → la garder à part (support Teams) et **préparer une vidéo de ~3 min**.
- **Posture orale :** être **sûr** de ce qu'on dit, éviter les « je ne sais pas, peut-être ».

## 13. IA & responsabilité (point des encadrants)

- L'usage de l'IA / des outils est **accepté**, mais **on reste responsable** : il faut **comprendre ce qu'il y a dans les codes** (la grande partie, sinon impossible de modifier / répondre).
- En soutenance, **c'est celui qui a fait la partie qui répond** aux questions → chacun doit connaître **toute l'activité**, même la partie qu'il n'a pas présentée.

## 14. Logistique soutenance

- **Sujet #47** — soutenance **semaine du 20 (20-26 juin)**, créneau évoqué **15 h** ; ordre de passage à confirmer (Niko/équipe possiblement parmi les premiers).
- **Grille d'évaluation** accessible. Critères : respect du temps, mise en forme / qualité graphique, clarté, qualité technique du cahier des charges.
- **Prochaine réunion la semaine prochaine** pour boucler la partie tests ; encadrants dispo.
- Demande explicite des encadrants : **« nettoyer un peu les notes »**.

---

## Prochaines étapes (Niko)

- [ ] Tester l'exécution **hors-ligne** + documenter les éventuelles dépendances en ligne
- [ ] Savoir **expliquer la génération de la trajectoire** (logique `AddCurve` : discrétisation puis déplacement des points, et comment on la modifierait — pas le code ligne à ligne)
- [ ] **Externaliser la position de la pièce** (fichier/interface) + tester plusieurs positions + documenter ; **lister les paramètres externalisables** en gardant un code fonctionnel
- [ ] Documenter **comment le bras trouve la position de la pièce** (type de paramètre)
- [ ] **Intégrer le mannequin simplifié dans la ligne ALIX** (recentrer sur `human frame`, tester avec trajectoires)
- [ ] **Tester la simu sur le robot réel** + capturer des **vidéos courtes**
- [ ] **Rédiger le rapport** selon la structure (schémas cinématique + développement, arborescence des repères, **pas de code brut**, logique « problème → pourquoi → solution »)
- [ ] Récupérer **template poster + guidelines** (envoi encadrants) puis **préparer la présentation** (template Supméca, vidéos 10-15 s, **vidéo 3 min** à part)
- [ ] Documenter le **DDL manquant (poignet)** comme perspective dans le rapport (le bras n'est pas naturel avec tel DDL → choix et solutions)
- [ ] Vérifier la **collision arrière** du coude (tâche bras v3)

---

*Prochain RDV : **semaine prochaine** (à caler) — finaliser la partie tests. Soutenance : **semaine du 20-26 juin**.*
