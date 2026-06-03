# Opérateur humain articulé dans RoboDK — la méthode de A à Z

> Comment on est passé d'un fichier STEP figé (mannequin SolidWorks) à un opérateur
> articulé à 22 DDL qui marche dans RoboDK, sans URDF et sans Build Mechanism.
> Rédigé le 03-04/06/2026. Scripts dans `scripts/` — la station RoboDK se
> reconstruit en ~10 s avec `scripts/rig_active_station.py` (voir §9 Persistance).

---

## 1. Le problème de départ

- Le modèle humain du projet est défini par l'URDF `Niko_v2_PRBE.urdf` (22 DDL,
  axes et limites validés iDynTree) — mais **RoboDK n'importe pas l'URDF**.
- L'outil **Build Mechanism** de RoboDK est inadapté : chaînes **série** uniquement,
  7 axes max, rotation forcée autour de Z. Un humain = un **arbre** (5 branches
  depuis le tronc) à 22 DDL.
- Les pièces SolidWorks sont presque toutes en `.SLDPRT` (illisible par RoboDK),
  mais l'assemblage complet existe en STEP : `Manikin_1.STEP`.

**Stratégie retenue :** importer le STEP, le découper en segments anatomiques, et
reconstruire l'articulation à la main avec des **Reference Frames imbriqués** +
l'**API Python**. L'URDF sert de table de référence (quels DDL, quels axes,
quelles limites) — pas de fichier d'import.

---

## 2. Vue d'ensemble du pipeline

```
Manikin_1.STEP (assemblage SolidWorks)
   │  RDK.AddFile()                       → 1 objet fusionné
   │  objet.setParam("Split")  (API)      → 17 sous-solides
   │  identification par GÉOMÉTRIE (bbox) → 15 segments anatomiques nommés
   │  repères imbriqués aux articulations → 22 DDL (axes + limites URDF)
   │  objet.setParentStatic(repère)       → segments attachés à leur articulation
   │  garde-à-vous (correction du bras)   → pose de repos propre
   └─ scripts de mouvement (bouge/neutre) → poses, marche militaire, marche avant
```

Tout est piloté par l'API Python depuis le terminal, RoboDK ouvert :
`C:\RoboDK\Python-Embedded\python.exe` (le module `robodk` y est préinstallé).

---

## 3. Décomposer le mannequin (Split)

```python
blob = RDK.AddFile(r"...\Manikin_1.STEP")   # 1 seul objet fusionné
blob.setParam("Split")                       # 17 sous-solides enfants
```

Le STEP arrive comme **un seul objet**. La commande `Split` (équivalent API du
clic droit > Split object) le découpe selon les solides de l'assemblage :
**17 sous-solides**, déjà **positionnés au bon endroit** (c'est tout l'intérêt
du STEP assemblage : pas besoin de replacer les pièces).

⚠️ **Piège important** : les sous-solides issus du Split sont des items
**type 7** (`ITEM_TYPE_CURVE` pour l'API !) et non de vrais objets (type 5).
Conséquences :
- `Save()`, `GetPoints()` ne fonctionnent pas dessus ;
- `MergeItems()` **fait crasher RoboDK** (vécu, à ne jamais refaire) ;
- leurs **poses ne survivent pas** à une sauvegarde/réouverture du `.rdk`
  (voir §9 Limites).

---

## 4. Identifier les membres (par géométrie, pas par les noms)

Les sous-solides s'appellent `Manikin_1-0` … `Manikin_1-16` : aucun nom utile.
On les identifie donc **par leur position** :

1. Pour chaque sous-solide : bounding box via `item.setParam("BoundingBox")`
   → centre `(x, y, z)`.
2. On compare ce centre à une table d'**ancres anatomiques** (`ANCHORS` dans
   `build_human_robodk.py`) : 15 points mesurés une fois sur le STEP
   (bassin, torse, tête, bras×2, avant-bras×2, mains×2, cuisses×2, tibias×2, pieds×2).
3. Chaque sous-solide est rattaché à l'ancre **la plus proche** → 17 sous-solides
   regroupés en **15 segments** (le tibia droit et le pied droit sont en 2 morceaux).

**Convention gauche/droite** : définie en cliquant dans RoboDK (renommage manuel
des premiers segments), puis vérifiée par géométrie. Résultat : **X+ = côté GAUCHE
du mannequin** (il regarde vers **+Z**). Les segments sont renommés
`bassin, torso, tete, bras_g/d, avant_bras_g/d, main_g/d, cuisse_g/d, tibia_g/d, pied_g/d`.

---

## 5. Associer les repères aux membres (le rig 22 DDL)

### Principe : 1 repère = 1 DDL

Un Reference Frame de RoboDK peut tourner librement, mais on s'impose la règle :
**chaque repère ne tourne que sur UN axe**. Une articulation à plusieurs DDL =
**plusieurs repères imbriqués au même point** :

| Articulation | DDL | Repères imbriqués (ordre) | Axes |
|---|---|---|---|
| Hanche (×2)  | 3 (rotule) | `hip_abduction` → `hip_flexion` → `hip_rotation` | Z, X, Y |
| Genou (×2)   | 1 | `knee_flexion` | X |
| Cheville (×2)| 1 | `ankle_flexion` | X |
| Épaule (×2)  | 3 (rotule) | `shoulder_abduction` → `shoulder_flexion` → `shoulder_rotation` | Z, X, Y |
| Coude (×2)   | 1 | `elbow_flexion` | X |
| Poignet (×2) | 2 | `wrist_flexion` → `wrist_deviation` | X, Z |

Total : **22 DDL**, conformes au cahier des charges (§4.3). Le **buste est figé** :
bassin + torse + tête sont attachés directement à `Human_Base`.

Axes anatomiques (repère monde : **Y = haut**, X = latéral, Z = profondeur) :
- **flexion** = rotation autour de **X** (plan sagittal — avant/arrière)
- **abduction** = rotation autour de **Z** (plan frontal — écarter/serrer)
- **rotation** = rotation autour de **Y** (axe long du membre)

Chaque DDL porte les **limites articulaires de l'URDF** (ex. genou 0…135°,
hanche flexion -120…+15°).

### Où placer le repère ? Au centre de la « boule »

Le mannequin a des sphères aux articulations. Le centre du repère = centre de la
boule = **milieu de l'intersection des bounding box des 2 segments** (la boule
appartient aux deux) :

```python
centre[i] = (max(min_parent[i], min_enfant[i]) + min(max_parent[i], max_enfant[i])) / 2
```

**Cas particulier de l'épaule** : le torse « déborde » sur le bras, l'intersection
des bbox ment. On prend l'extrémité **proximale** (haute et intérieure) de la bbox
du bras. *(Le centre exact de la sphère d'épaule reste à caler finement — voir §9.)*

### Attacher les segments : `setParentStatic`

```python
frame = RDK.AddFrame("kneeR_flexion", parent_frame)
frame.setPoseAbs(transl(*centre_du_joint))
segment.setParentStatic(frame)    # change le parent SANS bouger la géométrie
```

`setParentStatic` est la clé : il re-parente l'objet **en conservant sa position
absolue**. La hiérarchie finale :

```
Human_Base (bassin, torse, tête figés)
├── hipR_abduction → hipR_flexion → hipR_rotation [cuisse_d]
│       └── kneeR_flexion [tibia_d] └── ankleR_flexion [pied_d]
├── hipL_… (idem jambe gauche)
├── shoulderR_abduction → shoulderR_flexion → shoulderR_rotation [bras_d]
│       └── elbowR_flexion [avant_bras_d] └── wristR_flexion → wristR_deviation [main_d]
└── shoulderL_… (idem bras gauche)
```

Quand un repère tourne, **tout ce qui est en dessous suit** (segments + repères
enfants) : exactement la cinématique d'un squelette.

### Garde-à-vous (pose de repos)

La pose d'origine du STEP a le bras gauche écarté d'environ 42°. Correction :
toutes les rotations à zéro + **une seule abduction de -42° sur `shoulderL_abduction`**
(valeur déduite de la géométrie épaule→poignet). C'est intégré à la fin du rebuild :
l'opérateur démarre toujours bras le long du corps.

Script de reconstruction complet : **`scripts/rig_active_station.py`** (~10 s).

---

## 6. Faire bouger : le principe `repos × rotation`

Au lancement d'un script de mouvement, on **capture la pose de repos** de chaque
repère. Bouger un DDL = repartir du repos et tourner sur SON axe :

```python
REST = {nom: frame.Pose() for nom in DDL}                    # capturé au démarrage

def bouge(nom, deg):
    axe, lo, hi = DDL[nom]
    deg = max(lo, min(hi, deg))                              # borné aux limites humaines
    F[nom].setPose(REST[nom] * ROT[axe](math.radians(deg)))  # repos * rotation
```

C'est le cœur de **`Mouvement_v2.py`** (le modèle pour écrire ses propres
mouvements) et des deux marches. ⚠️ Lancer ces scripts **opérateur au repos**,
sinon le « repos » capturé est faux.

---

## 7. La marche militaire (`Marche_Militaire.py`)

Marche **sur place** (marquer le pas). Le cycle est une sinusoïde de phase `ph` :
**1 pas = une demi-période**.

```python
s = sin(ph)
lift_droite = max(0, s)      # jambe droite montée sur [0, π]
lift_gauche = max(0, -s)     # jambe gauche sur [π, 2π]
```

- **Jambes** : `hip_flexion = -55° × lift` (cuisse haute), `knee = +65° × lift`,
  `ankle = +15° × lift` (pointe de pied). Le `max(0, …)` fait que la jambe au sol
  reste parfaitement droite — militaire.
- **Bras raides** (coude 8°) en **opposition** : interpolation entre +20° (arrière)
  et -45° (avant) pilotée par `(1 ∓ s)/2` — bras droit devant quand jambe gauche monte.
- **Buste** : rien à faire, il est figé — garde-à-vous permanent.

---

## 8. La marche avant (`Marche_Avant.py`)

Marche **naturelle** qui avance **tout droit devant lui (+Z)**.

- **Hanches** : balancier asymétrique **+30° devant / -12° derrière**
  (sinusoïde recentrée : `hip = -(21·sin(ph) + 9)`).
- **Genou** : plié **seulement pendant le balancé** (quand la jambe revient
  devant) : `knee = 50° × max(0, cos(ph))` — la jambe d'appui reste tendue.
- **Cheville** : pointe relevée pendant le balancé (ne racle pas le sol).
- **Bras** : opposition souple ±25/15°, coude 20°.
- **L'astuce anti-glisse** : le corps avance à la vitesse des pas. La longueur
  de pas est **déduite de l'amplitude de hanche** :

  `L_pas = L_jambe × (sin 30° + sin 12°) ≈ 790 × 0.708 ≈ 560 mm`

  et `Human_Base` est translaté de `L_pas × ph/π` le long de +Z. Les pieds se
  posent donc là où la géométrie les amène — pas de patinage visible.
- **Fin** : articulations au repos + **retour au centre** (`Human_Base` à sa
  position d'origine `(0, 958, 0)`).

*(Anecdote : le sens du regard a été déterminé empiriquement — on a déplacé la
base en +Z et constaté qu'il reculait… après une première version moonwalk.)*

---

## 9. Limites connues et reste à faire

| Problème | Détail | Contournement actuel |
|---|---|---|
| **Persistance du `.rdk`** | Les sous-solides type 7 perdent leur pose relative à la réouverture → l'humain « explose » | Relancer `scripts/rig_active_station.py` (~10 s). Fix définitif à l'étude (import « un objet par pièce », ou conversion en vrais objets) |
| API sur type 7 | `Save`, `GetPoints` échouent ; `MergeItems` **crash** | Ne jamais les appeler sur les sous-solides |
| Centre sphère épaule | Repère actuellement à `(206, 1382, 13)` (estimation bbox) | À caler finement (mesure manuelle dans RoboDK) |
| Convention de repères | RoboDK défaut vs robot UR — à trancher pour la suite (réunion du 28/05) | — |

---

## 10. Récap des fichiers

| Fichier | Rôle |
|---|---|
| `scripts/rig_active_station.py` | **Reconstruit tout le rig** sur la station active (identification + renommage + 22 repères + garde-à-vous) |
| `scripts/build_human_robodk.py` | Table `ANCHORS` + helpers géométriques (bbox, plus-proche-ancre) |
| `scripts/Mouvement_v2.py` | Modèle de pilotage : `bouge(nom_ddl, deg)` / `neutre()`, à copier pour écrire ses mouvements |
| `scripts/Marche_Militaire.py` | Marche militaire sur place (embarqué dans la station, clic droit > Run) |
| `scripts/Marche_Avant.py` | Marche naturelle vers l'avant + retour au centre (embarqué aussi) |
| `Niko_v2_PRBE.urdf` | Table de référence des 22 DDL (axes, limites) — validée iDynTree |
| `docs/cahier-des-charges.md` §4.3 | Définition officielle des DDL |
