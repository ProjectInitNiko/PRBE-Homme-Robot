# Fiche — Comprendre et expliquer les codes Python RoboDK (PRBE)

> Fiche unique de révision pour la soutenance. Objectif : savoir **expliquer le
> code bloc par bloc** (pas ligne par ligne). Lecture dans l'ordre, chaque partie
> suit le pipeline. À la fin : questions probables du prof + mémo.

---

## 0. L'idée centrale (si tu ne retiens qu'une chose)

RoboDK ne sait pas importer un humain articulé. Alors on **fabrique un squelette à
la main avec des repères**, et on s'impose **une règle** :

> **1 repère = 1 degré de liberté** (il ne tourne que sur **un seul axe**).
> Une articulation à 3 DDL (épaule, hanche) = **3 repères emboîtés** au même point.

Tout le reste découle de ça. **22 DDL** au total :
`2 bras × 6 (épaule 3 + coude 1 + poignet 2) + 2 jambes × 5 (hanche 3 + genou 1 + cheville 1)`.

## Le pipeline en une image

```
1. GÉNÉRATION (hors RoboDK)   HMG : taille H + masse m → mannequin .urdf
2. IMPORT (RoboDK)            Manikin_1.STEP → AddFile + Split → 15 segments
3. RIG (RoboDK)              1 repère par DDL → 22 DDL + garde-à-vous
4. ANIMATION (RoboDK)         pose = repos × rotation → marches + tâche bras
   ROBUSTESSE                 remise à zéro + réparation du .rdk
```

> ⚠️ On a **deux modèles** : l'**URDF** (généré par HMG) sert juste de *table de
> référence* (axes + limites des 22 DDL) ; le **STEP** est ce qu'on importe
> **réellement** dans RoboDK. RoboDK importe mal l'arbre URDF → on rig le STEP à la
> main. **C'est LE point à savoir expliquer.**

---

## 1. Les briques RoboDK (vocabulaire commun à tout le code)

| Notion | Ce que c'est |
|---|---|
| `RDK = Robolink()` | la connexion au RoboDK ouvert ; **tout passe par `RDK`**. |
| **Item** | tout objet de la scène (repère, solide, programme), récupéré par son nom. |
| **type 5 / type 7** | type 5 = objet 3D normal ; **type 7 = sous-solide d'un Split** (fragile, voir §6). |
| **Reference Frame** | un repère = un trièdre = **notre brique d'articulation** (1 axe). |
| **Pose** | matrice 4×4 (position + orientation). `Pose()` = relatif au parent (pour animer) ; `PoseAbs()` = monde (pour mesurer). |
| `setParentStatic(p)` | rattache un objet à un parent **sans le déplacer** → la chaîne cinématique. |
| `Render(False/True)` | gèle / redessine l'affichage (on gèle pendant qu'on pose les 22 DDL). |

**Convention monde** (partout) : **Y = haut**, **X+ = gauche** du mannequin,
**+Z = devant**. Et : **flexion = axe X**, **abduction = axe Z**, **rotation = axe Y**.

---

## 2. Partie 1 — Générer le mannequin (`HMG` → URDF)

Étape **hors RoboDK**. L'outil **HMG** met à l'échelle un humain template à partir
de deux entrées et sort un `.urdf` (la « fiche cinématique » : segments,
articulations, butées).

| Bloc | Rôle |
|---|---|
| `config.py` (`H`, `m`) | taille et masse → toutes les longueurs (∝ H) et masses (% de m, De Leva). |
| `main.py` | génère le fichier `.urdf`. |
| `fix_urdf_paths.py` | une **regex** qui rend les chemins d'images (meshes) **relatifs** → fichier partageable. |

> Détail utile : l'URDF écrit une rotule en **3 articulations mono-axe** (pas de
> joint sphérique en URDF) → ordre des rotations figé. On **n'importe pas** cet
> URDF dans RoboDK (arbre ramifié mal géré) : il sert de **référence** d'axes/limites.

---

## 3. Partie 2 — Construire l'opérateur 22 DDL dans RoboDK

Fichiers : `build_human_robodk.py` (import + identification), `rig_active_station.py`
(le rig), `rebuild_operateur.py` (tout en 1 commande).

### Le déroulé en 5 blocs

| # | Bloc / action | Rôle |
|---|---|---|
| 1 | `AddFile(STEP)` + `setParam("Split")` | importe l'assemblage (1 bloc) et le **découpe** en ~17 sous-solides **déjà bien placés**. |
| 2 | `ANCHORS` + `_nearest_anchor` | identifie chaque morceau **par sa position** (centre de boîte comparé à 15 ancres anatomiques) → 15 segments nommés. |
| 3 | `joint_center` / `shoulder_center` | calcule **où poser le repère** = centre de la « boule » d'articulation. |
| 4 | double boucle du rig | crée **1 repère par DDL**, emboîtés ; `setParentStatic` accroche le segment → la chaîne. |
| 5 | garde-à-vous | corrige la pose STEP (bras écarté −42°, pieds ramenés à l'aplomb) → démarrage droit. |

**Pourquoi par la position (bloc 2) ?** Parce que les morceaux du Split n'ont pas de
nom utile, et la position ne ment pas (robuste à un ré-import).

**Le bloc 4, le cœur :** pour chaque membre, on enchaîne les articulations ; pour
chaque articulation, un repère par DDL, **chacun enfant du précédent, tous au même
point** ; puis le segment pend au dernier. Résultat → quand `shoulder` tourne, le
bras + l'avant-bras + la main suivent. La hiérarchie :

```
Human_Base (bassin, torse, tête figés)
├── hipR_abduction → hipR_flexion → hipR_rotation [cuisse_d] → kneeR → ankleR
├── … jambe gauche, bras droit, bras gauche
```

### Orchestration

`rebuild_operateur.py` enchaîne **3 scripts** (en ~30 s) : `rebuild_prep` (station +
import + Split) → `rig_active_station` (le rig) → `rebuild_finish` (ré-embarque les
programmes + vue). À relancer car la station ne se sauve pas proprement (voir §6).

---

## 4. Partie 3 — Le pattern qui fait bouger (commun à TOUT)

Modèle : `Mouvement_v2.py`. **Le même socle anime les marches ET la tâche bras.**

> **La formule unique :** `nouvelle_pose = pose_de_repos × rotation(axe, angle)`.

| Bloc | Rôle |
|---|---|
| `DDL = {...}` | pour chaque DDL : son **axe** et ses **butées** humaines. |
| `REST = {nom: F[nom].Pose()}` | **photographie la pose de repos au démarrage**. |
| `bouge(nom, deg)` | borne l'angle aux butées, applique `repos × rotation`. |
| `neutre()` | remet tous les DDL au repos (l'opérateur se redresse). |

> ⚠️ **Règle d'or :** `REST` est capturé au lancement → **toujours démarrer au
> garde-à-vous**, sinon le « repos » est faux et tout le mouvement est faux.

**Boucle d'animation** (toujours la même) :
`Render(False)` → poser tous les DDL de l'image → `Render(True)` → `sleep`.

---

## 5. Partie 4 — Les trois marches

Toutes tournent sur une **horloge angulaire `ph`** : **1 pas = π** (demi-période de
sinus) ; l'opposition bras/jambes vient du **signe du sinus**. Seule la fonction qui
pose le corps change.

### `Marche_Militaire.py` — sur place
- `pose_marche(ph)` : une jambe monte à la fois (`lift = max(0, ±sin)` met l'autre à
  plat → allure raide), bras raides en opposition.
- `marche()` : la boucle. **Aucun déplacement du corps.**

### `Marche_Avant.py` — tout droit (+Z)
Mêmes blocs + `avance(dist)` qui déplace `Human_Base`. Trois idées :
1. foulée **asymétrique** (30° devant / 12° derrière) ;
2. genou plié **seulement pendant le balancé** (jambe d'appui tendue) ;
3. **anti-glisse** : le corps avance **de la longueur réelle d'un pas**
   (`L_pas = L_jambe × (sin 30° + sin 12°) ≈ 560 mm`) → pas de patinage.

### `Marche_Trajectoire.py` — suivre une courbe externe
Se lit en **deux temps** : préparer la trajectoire, puis marcher dessus.

**A — préparer :**

| # | Bloc | Rôle (entrée → sortie) |
|---|---|---|
| 1 | `charge_waypoints` | lit le **JSON** → quelques points `[x, z]` au sol. |
| 2 | `lisse` (+ `_cr`) | **spline Catmull-Rom** : quelques points → courbe lisse `dense`. |
| 3 | `abscisses` | distances cumulées le long de la courbe → `S`. |
| 4 | `point_et_tangente` | à une distance `s` : position + direction (tangente). |

**B — marcher :**

| # | Bloc | Rôle |
|---|---|---|
| 5 | `tracer_trajectoire` | **DESSINE** la courbe bleue (affichage seul, voir encadré). |
| 6 | `pose_pas` | pose jambes/bras (identique à Marche_Avant). |
| 7 | `place_corps` | place le corps sur la courbe **et l'oriente sur la tangente**. |
| 8 | `marche_trajectoire` | boucle : avance `s` à la vitesse des pas, pose le pas, déplace le corps. |

`__main__` enchaîne : `charge_waypoints → lisse → abscisses → tracer → marche`.

**2 concepts à nommer :** *spline Catmull-Rom* (courbe lisse qui passe par tous les
points) et *abscisse curviligne* (on se repère par la distance parcourue `s`, ce qui
permet l'anti-glisse).

> ### 🔵 La ligne bleue : dessin ou trajectoire réelle ? (question piège)
> **C'est un simple dessin — une sortie, pas une entrée.** L'homme suit les points
> `dense` calculés depuis le **JSON**, pas la ligne affichée.
> ```
> trajectoire_S.json   ← LA SEULE source
>    │ charge → lisse
>    ▼
>  dense ──► place_corps()        → DÉPLACE l'homme   (ce qui compte)
>        └─► tracer_trajectoire() → DESSINE la ligne  (juste un témoin)
> ```
> - Modifier la ligne à la main → **aucun effet** ; en plus le code la **supprime
>   et la redessine** à chaque run.
> - Pour changer le parcours → éditer le **JSON** (ou passer un autre fichier en
>   argument). **JSON = la vérité ; la ligne = une photo du JSON.**

---

## 6. Partie 5 — La tâche bras (cinématique inverse)

`Tache_Bras.py` : pick & place d'un cube, bras gauche 6 DDL. Le code le plus
technique. **D'abord les 3 mots de vocabulaire :**

- **FK (cinématique directe)** : angles → **où est la main**. Facile (multiplication
  de matrices).
- **IK (cinématique inverse)** : main voulue **ICI** → quels angles ? Difficile,
  pas de formule → on **itère**.
- **Effecteur** : le point piloté = le **centre de la paume**.

### Les blocs

| Bloc | Rôle |
|---|---|
| `Position_0` (appelé au début) | remet au garde-à-vous **avant** de capturer le repos. |
| `fk_pose(q)` | **FK** : `repos × rotation` accumulé le long du bras → pose de la main. |
| `fk_coude(q)` | position du coude (pour vérifier qu'il ne part pas en avant). |
| `ik(cible, ...)` | **IK** : trouve les angles qui amènent la paume sur la cible. |
| `build_trajectoire()` | résout l'IK sur les **postures clés** + **précalcule** toutes les images. |
| `main()` | **joue** la trajectoire (zéro calcul) + saisit/lâche la pièce. |

### Comment marche l'IK (bloc `ik`, en 4 idées)

1. **Mesurer l'erreur** : écart de position (mm) + écart d'orientation de la main.
2. **Jacobien par différences finies** : on **secoue chaque angle de 0,5°** et on
   regarde de combien la main bouge → matrice 6×6 « effet de chaque angle ».
3. **Pas amorti (DLS)** : on corrige les angles dans le bon sens, avec un terme
   d'**amortissement λ²** qui évite que ça explose quand le bras est tendu
   (singularité). *(C'est la formule `Δq = Jᵀ(JJᵀ + λ²I)⁻¹e` du rapport.)*
4. **Garde-fous** : angles **bornés** aux butées + on **réduit le pas** s'il aggrave
   l'erreur. On répète jusqu'à être assez près (≈6 mm).

> Subtilité utile : une **posture de confort** (`Q_CONF`) pousse l'IK vers la
> solution « **coude en arrière** » (un bras 6 DDL a plusieurs solutions pour une
> même position de main).

### L'astuce de fluidité (bloc `build_trajectoire`)
La v2 calculait l'IK **à chaque image** → saccadé. La **v3 sépare** :
1. IK **seulement sur les postures clés**, hors animation ;
2. **interpolation** entre les clés (spline + profil doux *smoothstep*) ;
3. tout est **précalculé**, puis la lecture **n'applique que des poses** → fluide.

### Saisir / lâcher (bloc `main`)
**Pas de physique** : « saisir » = `piece.setParentStatic(poignet)` (le cube devient
enfant de la main → il suit), « lâcher » = le ré-attacher à la table. **C'est la même
mécanique de repères que le rig.**

### Le coude « jamais en avant »
Deux verrous : (1) on **borne la flexion d'épaule ≥ −8°** (par construction le coude
reste en arrière) ; (2) un **scan** parcourt toute la trajectoire et **refuse de
jouer** si le coude dépasse → c'est une *preuve*, pas une promesse.

---

## 7. Partie 6 — Robustesse

### `Position_0.py` — le garde-à-vous exact
Chaque animation laisse une petite dérive ; elle s'**accumule**. `remettre_a_zero`
**rejoue le garde-à-vous du rig** (rotations à zéro, bras −42°, pieds à l'aplomb).
Importable → appelé avant de capturer le repos (cf. tâche bras).

### `fix_reattache_segments.py` — réparer le mannequin éclaté
**Le bug à raconter :** à la réouverture du `.rdk`, le mannequin **explose**. Les
sous-solides du Split (**type 7**) ne sauvent que leurs points bruts ; la
compensation posée par `setParentStatic` est perdue → **double transformation** à
l'ouverture. Le fix **rejoue ce re-basage** segment par segment (~2 s, sans rebuild).

⚠️ Deux pièges (à citer) : ne **jamais** le faire sous `Render(False)` (échoue en
silence) ; **non idempotent** → une garde refuse de tourner sur une station saine.
Dernier recours : `rebuild_operateur.py` (reconstruction complète).

---

## 8. Questions probables du prof (+ réponses courtes)

- **Pourquoi pas l'URDF directement ?** → RoboDK importe mal un arbre humain 22 DDL ;
  *Build Mechanism* ne fait que des chaînes série. On rig le STEP à la main ; l'URDF
  reste la référence des axes/limites.
- **Comment vous reconnaissez les membres après le Split ?** → par géométrie : centre
  de boîte englobante comparé à 15 ancres anatomiques.
- **Comment une épaule a 3 DDL ?** → 3 repères mono-axe emboîtés au même point (Z, X, Y).
- **Pourquoi il ne glisse pas en marchant ?** → le corps avance de la longueur réelle
  d'un pas (déduite de l'amplitude de hanche).
- **La ligne dans RoboDK pilote l'homme ?** → Non, c'est un dessin de sortie ; le
  parcours vient du JSON (la ligne est redessinée à chaque run).
- **FK vs IK ?** → FK : angles → position. IK : position voulue → angles (itératif).
- **Pourquoi l'IK est "amortie" ?** → le terme λ² évite l'explosion près des
  singularités (bras tendu).
- **Comment l'objet est saisi ?** → re-parentage `setParentStatic`, pas de physique.
- **Pourquoi le mannequin casse à la réouverture ?** → sous-solides type 7 : pose non
  persistée → double transformation. Réparé par `fix_reattache_segments`.

## 9. Mémo final (à se réciter)

1. **1 repère = 1 DDL** ; rotule = 3 repères emboîtés ; **22 DDL**.
2. Pipeline : **HMG→URDF** (réf.) · **STEP→Split** (import) · **rig** (22 repères) ·
   **animation** (`repos × rotation`).
3. Identification des membres **par la position** (ancres + bbox).
4. `setParentStatic` = la chaîne cinématique (saisie d'objet = même mécanique).
5. Animer = `bouge` = `repos × rotation`, borné aux butées ; **lancer au repos**.
6. Marches : horloge `ph`, anti-glisse ; **trajectoire = JSON** (la ligne bleue n'est
   qu'un dessin).
7. Tâche bras : **FK** facile, **IK** itérative (Jacobien diff. finies + DLS amorti),
   **précalcul** pour la fluidité.
8. Robustesse : `Position_0` (dérive) + `fix_reattache_segments` (bug type 7).
