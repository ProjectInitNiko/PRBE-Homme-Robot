# Architecture HMG

Lecture détaillée du repo [Human Model Generator](https://github.com/gbionics/human-model-generator) (IIT, BSD-3-Clause).

## Pipeline

```
config.py (H, m, 12 mesures)
   │
   ├── linkDimensions  ←  scaleLink(H)        # toutes les longueurs/largeurs des 22 segments
   ├── linkMass        ←  scaleMass(m)        # masses via De Leva 1996 (% de m total)
   ├── jointPosition   ←  scaleJoint(linkDim) # positions des joints articulaires
   └── musclePosition  ←  scaleMuscleJoint    # frames d'attache musculaire
        │
        ▼
   modifyModels.py  →  applique tout sur le template URDF (urdf-modifiers)
        │
        ▼
   modifyMeshModels.py  →  ajoute les meshes (skin / muscles / colonne) — optionnel
        │
        ▼
   utils.write_urdf_to_file()  →  models/humanModels/<nom>.urdf
        │
        ▼
   iDynTree :  consistance physique (matrice de masse) + viz
```

## Architecture cinématique

Le template `humanModelTemplate.urdf` contient **102 joints** : ~54 articulaires (`revolute`) + 48 fixes (frames d'attache musculaire + mains + birkens).

### Décompte des DDL articulaires

| Région | Joints articulaires | DDL |
|---|---|---|
| Épine (L5→T8) | jL5S1, jL4L3, jL1T12 (rotx+roty) + jT9T8 (rotx+roty+rotz) | 9 |
| Cou + tête | jT1C7 (3) + jC1Head (rotx+roty) | 5 |
| Clavicules | jC7Right/LeftShoulder (3+3) | 6 |
| Bras D | jRightShoulder (3) + jRightElbow (roty+rotz) + jRightWrist (rotx+rotz) | 7 |
| Bras G | idem | 7 |
| Jambe D | jRightHip (3) + jRightKnee (2) + jRightAnkle (3) + jRightBallFoot (1) + jRightHeel (1) | 10 |
| Jambe G | idem | 10 |
| **Total** | | **~54** |

## Points d'architecture importants

1. **URDF décompose les joints multi-axes en mono-axe** (`jShoulder_rotx`, `_roty`, `_rotz`). Standard URDF — pas de joint sphérique 3-DDL natif. Conséquence : **ordre des rotations figé**, à respecter dans toute IK.

2. **Mains et pieds = blocs rigides** (`jHandCOM` est `fixed`). Pas de doigts mobiles.

3. **Pas de base flottante dans le template** — c'est `dynComp.setFloatingBase("Pelvis")` qui l'ajoute côté iDynTree au runtime. Pour RoboDK : choix à faire (ancrer le pelvis ou ajouter joint floating).

4. **Tous les segments sont des `<box size="1 1 1"/>`** dans le template — `urdf-modifiers` les redimensionne via `setLinkLength`. RoboDK avale les box sans souci.

5. **Trick π** : pour les segments cylindriques (cou, bras, jambes), `X = Y = mesure_input / π`. Donc les mesures attendues en input sont des **circonférences**, pas des diamètres.

6. **Scaling longueur** ∝ `H × ratio` (Drillis-Contini-like). Ex : `Head.X = 0.13·H`, `UpperArm.Y = 0.186·H`.

7. **Scaling masse** via De Leva 1996 (% du m total). Ex : `UpperLeg = 0.1447·m`, `Hand = 0.0059·m`.

## Anatomie d'un `.urdf` généré

Pour H=1.665 m, m=59 kg (défauts du `config.py`) : fichier de **86 KB**, contenant pour chaque link :

```xml
<link name="Pelvis">
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="6.9797"/>                   <!-- = 0.1183 × 59 ≈ 6.98 kg ✓ -->
    <inertia ixx="..." iyy="..." izz="..."/> <!-- tenseur scalé proprement -->
  </inertial>
  <visual name="Pelvis">
    <geometry>
      <mesh filename=".../Pelvis.stl" scale="1. 1. 1."/>
    </geometry>
    ...
  </visual>
  <visual name="Pelvis_RightRecAbd"> ... </visual>     <!-- + 4 muscles -->
  <visual name="Pelvis_SpinalCord"> ... </visual>      <!-- + colonne -->
  <collision>
    <geometry>
      <box size="0.225 0.318 0.130"/>                  <!-- box simplifiée -->
    </geometry>
  </collision>
</link>
```

Et entre les links, des liens intermédiaires `*_f1` à inertie 1e-5 kg pour décomposer les rotations multi-axes en chaîne mono-axe.
