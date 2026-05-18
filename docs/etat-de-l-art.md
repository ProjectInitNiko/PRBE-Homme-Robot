# État de l'art — Simulation du mouvement humain et interaction homme-robot dans RoboDK

**Projet PRBE 2026 — Sujet #47**
**Équipe :** Nikoloz Khachidze, Luc Fantasia, Alex Nowak
**Encadrants :** Francesco Ciampi, Thierno Diallo — ISAE-Supméca
**Date :** mai 2026

---

## 1. Introduction et contexte

Dans les environnements industriels collaboratifs modernes, les robots et les opérateurs humains partagent de plus en plus leur espace de travail. Concevoir, valider et optimiser ces interactions est un enjeu central de **sécurité, d'ergonomie et d'efficacité opérationnelle**.

Les outils de simulation industrielle (RoboDK, CATIA, Gazebo) modélisent bien les robots mais peinent à représenter fidèlement le mouvement humain. La ligne **ALIX** de l'ISAE-Supméca est un cas concret : un bras robotisé manipule des pièces sur un convoyeur en présence d'un opérateur humain. Modéliser cet opérateur de façon réaliste et articulée dans l'environnement de simulation reste un problème ouvert.

Cet état de l'art recense les approches existantes pour représenter un mannequin humain articulé, le mettre en mouvement et l'intégrer dans un simulateur de type RoboDK.

---

## 2. Représentation numérique du corps humain

### 2.1 Modèles géométriques et cinématiques

La représentation d'un opérateur humain en simulation repose sur deux niveaux :

- **Niveau géométrique** : les segments du corps (tronc, membres) modélisés par des solides simples (cylindres, boîtes, ellipsoïdes) ou des maillages 3D
- **Niveau cinématique** : les liaisons articulaires entre segments, définissant les degrés de liberté (DoF) du squelette

Le compromis central est entre **réalisme** (nombre de DoF élevé) et **complexité computationnelle** (temps de simulation, stabilité numérique).

**Modèles de référence :**

| Modèle | Segments | DoF | Source |
|--------|----------|-----|--------|
| Modèle IIT/HMG (Latella 2019) | 23 links | 48 DoF internes | Thèse IIT, arXiv:1912.01136 |
| Modèle DHM Maurice (2019) | 21 segments | 45 DoF | HAL hal-02389726 |
| Modèle simplifié Kim (2009) | cylindres/sphères | ~30 DoF | IROS 2009 |
| SMPL/SMPL-X (MPI) | 23 joints | 72 params de pose | smpl.is.tue.mpg.de |

### 2.2 Paramétrage anthropométrique

Pour que le mannequin corresponde à la morphologie d'un opérateur réel, les paramètres géométriques (longueurs des segments, masses, moments d'inertie) sont dérivés des **tables anthropométriques** :

- **Winter (1990)** : ratios segment/taille totale, coefficients de masse relative
- **Herman (2007)** : complément avec données de population industrielle
- **Formules analytiques** : masse d'un segment = coefficient × masse corporelle totale ; longueur = coefficient × taille

Ces tables permettent de générer automatiquement un mannequin paramétré à partir de deux valeurs : **taille (m)** et **masse (kg)**.

### 2.3 Format de description — URDF

Le format **URDF (Unified Robot Description Format)** est le standard XML de représentation des chaînes cinématiques articulées, issu de ROS. Il décrit :

- Les `<link>` : segments avec géométrie, collision et inertie
- Les `<joint>` : liaisons entre segments (type, axe, limites)

**Limites URDF pour le corps humain :**
- URDF standard ne supporte que les joints à 1 DoF (revolute, prismatic)
- Les articulations humaines (épaule, hanche) ont 3 DoF sphériques → nécessite des **virtual links** intermédiaires (un lien fictif par DoF)
- Cette extension non-standard est documentée dans l'Annexe B de Latella 2019

**Note sur RoboDK :** RoboDK ne dispose pas de support URDF natif. Une étape de **conversion Python** est nécessaire pour importer un modèle URDF dans l'environnement RoboDK (confirmé par Tola & Corke 2023, arXiv:2308.00514).

---

## 3. Outils de génération de mannequin

### 3.1 Human Model Generator (HMG) — IIT

- **Source :** [github.com/gbionics/human-model-generator](https://github.com/gbionics/human-model-generator)
- **Licence :** BSD-3 (utilisation libre y compris académique)
- **Organisation :** Fondazione Istituto Italiano di Tecnologia (IIT), Dynamic Interaction Control Lab
- **Description :** Générateur Python de mannequin humain complet au format URDF, scalable via 12 paramètres anthropométriques (taille, masse, circonférences)
- **Structure générée :** 23 links, ~102 joints (54 revolute = DoF articulaires, 48 fixed = points d'attache musculaires), bras droit = 7 DoF (épaule 3 + coude 2 + poignet 2)
- **Stack technique :** Python 3.11, numpy, idyntree, urchin, urdf-modifiers (conda recommandé)
- **Statut PRBE :** Mannequin `Niko_v1.urdf` généré (H=1.665 m, m=59 kg, masse-matrix définie positive ✓)

### 3.2 SMPL / SMPL-X (MPI Tübingen)

- **Source :** [smpl.is.tue.mpg.de](https://smpl.is.tue.mpg.de/)
- **Licence :** Académique non commerciale
- **Description :** Modèle statistique du corps humain appris sur 1700+ scans. Paramétré par un vecteur de **forme** (10 valeurs, variations morphologiques de la population) et un vecteur de **pose** (72 valeurs = 24 joints × 3 axes)
- **SMPL-X** : extension avec mains (26 DoF/main) et expressions faciales
- **Format :** Exportable en URDF, adapté pour l'animation à partir de données mocap
- **Pertinence PRBE :** Intéressant comme alternative si HMG montre des limites d'import RoboDK

### 3.3 MakeHuman (open source)

- **Licence :** GNU Affero GPL
- **Description :** Logiciel de création de mannequins humains paramétriques, export STL/OBJ
- **Pertinence PRBE :** Moins adapté (pas de URDF direct, pipeline plus lourd)

---

## 4. Méthodes d'animation du mannequin

### 4.1 Animation par cinématique directe (FK)

La **cinématique directe (Forward Kinematics)** consiste à spécifier les angles de chaque joint pour obtenir la pose globale du mannequin. C'est l'approche la plus simple dans RoboDK via l'API Python :

```python
from robolink import Robolink
RDK = Robolink()
robot = RDK.Item("HumanMannequin")
robot.setJoints([0, 45, 90, 0, 0, 0])  # angles en degrés
RDK.Render()
```

**Avantages :** Simple, déterministe, pas de singularités
**Limites :** Difficile de spécifier des poses naturelles directement en angles ; pas de contrainte sur la position de la main

### 4.2 Animation par cinématique inverse (IK)

La **cinématique inverse (Inverse Kinematics)** calcule les angles articulaires pour qu'un effecteur (la main, le pied) atteigne une position cible dans l'espace. C'est l'approche recommandée pour les scénarios H-R réalistes.

**IK analytique (Kim et al. 2009) :**
- Membres inférieurs : solution analytique exacte (pas de singularité numérique)
- Membres supérieurs : redondance du bras → optimisation sous contrainte (minimiser couple ou distance à posture neutre)

**IK numérique dans RoboDK :**
```python
target_pose = transl(500, 200, 800)  # Position cible [mm]
joint_solution = robot.SolveIK(target_pose)
if joint_solution:
    robot.setJoints(joint_solution)
```

**Gestion de la redondance humaine :** Le bras humain a 7 DoF pour positionner la main (6 DoF nécessaires) → 1 DoF redondant. Critères de sélection de la solution : minimisation du couple articulaire, maximisation de la distance aux butées, posture la plus naturelle.

### 4.3 Animation depuis données mocap

Le **motion capture (mocap)** permet de capturer des mouvements humains réels et de les rejouer sur le mannequin. Pipeline :

1. Capture des marqueurs ou IMU → données de position 3D ou d'angles articulaires
2. Conversion au format articulaire du mannequin (scaling proportionnel)
3. Lecture frame par frame dans RoboDK

**Formats standards :** BVH, C3D, FBX

```python
# Principe : boucle animation depuis séquence articulaire
import time
motion_sequence = load_mocap_data("walking.bvh")  # liste de poses
for joints in motion_sequence:
    robot.setJoints(joints)
    RDK.Render()
    time.sleep(1/30)  # 30 fps
```

**Projet de référence :** KinectPython (Ang, github.com/KonstantinosAng/KinectPython) — capture Kinect2 en temps réel → RoboDK pour coordination H-R synchronisée.

---

## 5. Intégration dans RoboDK

### 5.1 Architecture cinématique dans RoboDK

RoboDK représente les chaînes cinématiques via une hiérarchie de **Frames** (repères) et d'**Objets** (géométries). Pour un mannequin :

```
Frame_Pelvis (racine)
├── Frame_Spine → Objet_Torso
│   ├── Frame_ShoulderR → Objet_UpperArmR
│   │   └── Frame_ElbowR → Objet_ForeArmR
│   │       └── Frame_WristR → Objet_HandR
│   └── Frame_ShoulderL → ...
├── Frame_HipR → Objet_ThighR
│   └── Frame_KneeR → Objet_LowerLegR
│       └── Frame_AnkleR → Objet_FootR
└── Frame_HipL → ...
```

Chaque Frame est positionnée par rapport à son parent via une matrice de transformation homogène (translation + rotation).

### 5.2 Import de pièces STEP

Workflow pour l'approche "import pièces séparées" (fichiers disponibles : dossier Manikin/\*.STEP) :

1. `File > Open` pour chaque pièce STEP → elle apparaît comme un Objet dans RoboDK
2. Créer une Frame par joint via `Add > Reference Frame`
3. Lier chaque Objet à sa Frame parent (drag-and-drop dans l'arborescence)
4. Positionner les Frames aux emplacements anatomiques corrects

### 5.3 Import URDF (via Add-in)

RoboDK propose un [Import URDF Add-in](https://robodk.com/addin/com.robodk.app.importurdf) permettant d'importer directement un fichier URDF comme mécanisme articulé. C'est la voie privilégiée avec le mannequin HMG :

- Pré-requis : `Niko_v1.urdf` + dossiers de meshes accessibles
- Points de vigilance : inertie valide (définie positive ✓ confirmé), limites articulaires en radians, chemins relatifs des meshes

---

## 6. Analyse ergonomique et sécurité H-R

### 6.1 Indicateurs ergonomiques

Maurice et al. (2019) définissent trois indicateurs calculables en post-simulation :

| Indicateur | Calcul | Seuil d'alerte |
|------------|--------|----------------|
| Écart posture neutre | Distance articulaire à la posture de repos | Joint proche de la butée |
| Couple articulaire | τ = J^T · F (Jacobien transposé × force externe) | Dépasse capacité musculaire |
| Fatigue temporelle | Modèle exponentiel sur historique couple/angle | Accumulation > seuil |

### 6.2 Analyse des zones de proximité

Objectif PRBE : détecter et caractériser les zones d'interaction entre l'enveloppe du mannequin et l'enveloppe du robot. RoboDK permet :

- Vérification de collision en temps réel (`RDK.setCollisionActive(True)`)
- Calcul de distance minimale entre objets via l'API Python
- Génération de zones de sécurité (plans, sphères, boîtes)

---

## 7. Synthèse et choix retenus pour PRBE 2026

### 7.1 Chaîne d'implémentation retenue

```
HMG (IIT, BSD-3)
  └─ Paramétré : H=1.665 m, m=59 kg [tables Winter/Herman, Latella 2019 Ch.3]
  └─ Structure URDF : 23 links, virtual links pour joints sphériques [Latella 2019 Annexe B]
       │
       ▼
Conversion Python → RoboDK
  └─ Import via URDF Add-in ou reconstruction manuelle STEP
  └─ Hiérarchie Frames/Objets dans RoboDK
       │
       ▼
Animation
  └─ Périmètre démo : bras droit seul (épine figée)
  └─ IK analytique membres inférieurs [Kim et al. 2009, section III-B]
  └─ FK / setJoints pour les scénarios H-R
       │
       ▼
Analyse H-R dans RoboDK
  └─ Indicateurs ergonomiques [Maurice et al. 2019]
  └─ Zones de proximité / détection collision
```

### 7.2 Périmètre de la démo

Décision prise en session de travail (mai 2026) :
- **Périmètre initial :** bras droit seul (7 DoF), épine figée (joints L5S1/L4L3/L1T12/T9T8 → fixed)
- **Raison :** Réduire la complexité de l'IK pour une première démo fonctionnelle avant mi-juin
- **Extension possible :** membres inférieurs (locomotion) en phase 2 si le temps le permet

### 7.3 Questions ouvertes

- [ ] Import `Niko_v1.urdf` dans RoboDK via URDF Add-in — à tester (étape critique)
- [ ] Conversion Python des fichiers STEP Manikin → mécanisme articulé alternatif
- [ ] Définir le scénario H-R concret sur ligne ALIX (gestes à représenter)
- [ ] Évaluer si les indicateurs ergonomiques (couple articulaire) sont calculables en Python pur sans LQP

---

## 8. Références

1. **Kim, S., Kim, C., You, B., Oh, S.** (2009). *Stable whole-body motion generation for humanoid robots to imitate human motions.* IEEE/RSJ IROS 2009, St. Louis.

2. **Latella, C.** (2019). *Human Whole-Body Dynamics Estimation for Enhancing Physical Human-Robot Interaction.* Thèse de doctorat, Università di Genova / IIT. arXiv:1912.01136.

3. **Tola, D., Corke, P.** (2023). *Understanding URDF: A Dataset and Analysis.* Aarhus University / QUT. arXiv:2308.00514.

4. **Maurice, P., Padois, V., Measson, Y., Bidaud, P.** (2019). *Digital Human Modeling for Collaborative Robotics.* In: *DHM and Posturography*, Elsevier. HAL: hal-02389726.

5. **RoboDK Python API Documentation.** https://robodk.com/doc/en/PythonAPI/index.html

6. **RoboDK-API GitHub.** https://github.com/RoboDK/RoboDK-API

7. **RoboDK Import URDF Add-in.** https://robodk.com/addin/com.robodk.app.importurdf

8. **Ang, K.** (2021). *KinectPython — Human-Robot Collaboration via Kinect2 and RoboDK.* GitHub. https://github.com/KonstantinosAng/KinectPython

9. **Pavlakos, G. et al.** (2019). *Expressive Body Capture: 3D Hands, Face, and Body from a Single Image (SMPL-X).* CVPR 2019. https://smpl-x.is.tue.mpg.de/

10. **Human Model Generator (HMG).** Fondazione IIT, Dynamic Interaction Control Lab. https://github.com/gbionics/human-model-generator
