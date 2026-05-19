# Distances de Sécurité et Conditions — Interaction Homme-Robot

*Document technique pour [[Projet PRBE 2026]] — Simulation H-R sur ligne ALIX*

---

## 📐 Distances de Sécurité Minimales

### Selon ISO 10218-2 (Barrières périmètriques)

**Configuration standard pour cellules robotiques :**

- **Hauteur minimale de la barrière** : 1 400 mm (55 pouces) au-dessus du sol
- **Distance maximale du bas de la barrière au sol** : 200 mm (7,8 pouces)
- **Distance de sécurité latérale** : Selon ISO 13857 (voir ci-dessous)

**Référence :** [ISO 10218 & ISO/TS 15066 Explained | AMD Machines](https://amdmachines.com/blog/robot-safety-standards-iso-10218-and-ts-15066-explained/)

---

### Selon ISO 13857 (Prévention d'atteinte par les membres)

**Distances de sécurité pour empêcher l'atteinte de zones dangereuses par les membres supérieurs :**

Les valeurs couvrent le **95ᵉ percentile de la population** (personnes de 14 ans et plus).

| Hauteur de structure (h) | Distance de sécurité minimale |
|--------------------------|-------------------------------|
| 1 000 mm                 | Variable selon ouverture      |
| 1 200 mm                 | Variable selon ouverture      |
| 1 400 mm                 | Variable selon ouverture      |
| 1 600 mm                 | Variable selon ouverture      |
| 1 800 mm                 | Variable selon ouverture      |
| 2 000 mm                 | Variable selon ouverture      |
| 2 200 mm                 | Variable selon ouverture      |
| 2 400 mm                 | Variable selon ouverture      |
| **2 500 mm** (risque faible) | Protection complète       |
| **2 700 mm** (risque élevé)  | Protection complète       |

**Distance minimale générale** : La zone de danger doit être à au moins **120 mm** de toute ouverture.

**Référence :** [EN ISO 13857 - Safety Distances Upper Limbs | GT Engineering](https://www.gt-engineering.it/en/technical-standards/en-iso-standards/en-iso-13857-safety-distances/safety-distances-upper-limbs/)

---

### Selon ISO/TS 15066 (Surveillance vitesse et séparation - SSM)

**Formule de distance de séparation minimale (S) :**

```
S(t₀) = vH·(TR + TS) + vR·TR + vs·TS + C + ZR + ZS
```

**Où :**

- **vH** = vitesse de l'opérateur vers le robot (m/s)
  - Valeur typique : **1,6 m/s** (vitesse de marche humaine)

- **vR** = vitesse du robot vers l'opérateur (m/s)
  - Valeur dépendant du robot ALIX (à mesurer)

- **vs** = vitesse du robot pendant l'arrêt (m/s)
  - Décélération progressive

- **TR** = temps de réponse du système (s)
  - Inclut : détection capteur + traitement + envoi signal arrêt
  - Valeur typique : **0,1 à 0,3 s**

- **TS** = temps d'arrêt du robot (s)
  - Dépend de la vitesse, charge, inertie
  - Valeur typique cobots : **0,2 à 0,5 s**
  - Robots industriels rapides : **0,5 à 2 s**

- **C** = marge de sécurité (intrusion) (mm)
  - Basée sur la portée attendue du bras humain
  - Valeur typique : **200 à 300 mm**

- **ZR** = incertitude de position du robot (mm)
  - Précision du système de localisation robot
  - Valeur typique : **10 à 50 mm**

- **ZS** = incertitude de position du capteur (mm)
  - Précision du scanner laser / capteur de présence
  - Valeur typique : **50 à 100 mm**

**Exemple de calcul :**

```
Hypothèses :
- vH = 1,6 m/s (marche normale)
- vR = 0,5 m/s (robot en approche)
- vs = 0,25 m/s (vitesse moyenne pendant arrêt)
- TR = 0,2 s
- TS = 0,4 s
- C = 250 mm = 0,25 m
- ZR = 30 mm = 0,03 m
- ZS = 80 mm = 0,08 m

S = 1,6·(0,2 + 0,4) + 0,5·0,2 + 0,25·0,4 + 0,25 + 0,03 + 0,08
S = 1,6·0,6 + 0,1 + 0,1 + 0,25 + 0,03 + 0,08
S = 0,96 + 0,56
S ≈ 1,52 m

→ Distance de sécurité minimale : environ 1,5 à 2 mètres
```

**Références :**
- [Implementing Speed and Separation Monitoring | PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5117641/)
- [ISO/TS 15066 Technical Specification (PDF)](https://www.diag.uniroma1.it/deluca/pHRI_elective/ISO_TS_15066_2016_en.pdf)

---

## 💪 Limites de Force et Pression (Power & Force Limiting)

### Tableau des seuils biomécanique — ISO/TS 15066 Annexe A

Valeurs maximales de **force (N)** et **pression (N/cm²)** par région corporelle basées sur le seuil de douleur (étude Université de Mayence sur 100 sujets, 29 zones du corps).

**Deux types de contact :**

1. **Contact transitoire (impact bref)** : Valeurs plus élevées tolérées
2. **Contact quasi-statique (pincement prolongé)** : Valeurs réduites (40-65% des valeurs transitoires)

| Région du corps              | Force max (transitoire) | Pression max (transitoire) | Force max (quasi-statique) | Pression max (quasi-statique) |
|------------------------------|-------------------------|----------------------------|----------------------------|-------------------------------|
| **Crâne / Front**            | 130 N                   | 110 N/cm²                  | 65 N                       | 55 N/cm²                      |
| **Face**                     | 65 N                    | 75 N/cm²                   | 35 N                       | 40 N/cm²                      |
| **Cou (muscles)**            | 150 N                   | 140 N/cm²                  | 75 N                       | 70 N/cm²                      |
| **Dos (vertèbres)**          | 210 N                   | 160 N/cm²                  | 110 N                      | 80 N/cm²                      |
| **Dos (muscles)**            | 210 N                   | 160 N/cm²                  | 110 N                      | 80 N/cm²                      |
| **Poitrine**                 | 140 N                   | 110 N/cm²                  | 70 N                       | 55 N/cm²                      |
| **Abdomen**                  | 110 N                   | 110 N/cm²                  | 55 N                       | 55 N/cm²                      |
| **Bassin**                   | 180 N                   | 180 N/cm²                  | 90 N                       | 90 N/cm²                      |
| **Épaule (articulation)**    | 160 N                   | 160 N/cm²                  | 80 N                       | 80 N/cm²                      |
| **Bras (muscle biceps)**     | 150 N                   | 150 N/cm²                  | 75 N                       | 75 N/cm²                      |
| **Avant-bras (muscle)**      | 160 N                   | 160 N/cm²                  | 80 N                       | 80 N/cm²                      |
| **Avant-bras (os radial)**   | 140 N                   | 180 N/cm²                  | 70 N                       | 90 N/cm²                      |
| **Main (paume)**             | 140 N                   | 140 N/cm²                  | 70 N                       | 70 N/cm²                      |
| **Main (dos)**               | 100 N                   | 110 N/cm²                  | 50 N                       | 55 N/cm²                      |
| **Doigts (phalange)**        | 80 N                    | 100 N/cm²                  | 40 N                       | 50 N/cm²                      |
| **Cuisse (muscle)**          | 220 N                   | 220 N/cm²                  | 110 N                      | 110 N/cm²                     |
| **Genou (rotule)**           | 220 N                   | 210 N/cm²                  | 110 N                      | 105 N/cm²                     |
| **Tibia (face avant)**       | 130 N                   | 160 N/cm²                  | 65 N                       | 80 N/cm²                      |
| **Pied (dos)**               | 120 N                   | 150 N/cm²                  | 60 N                       | 75 N/cm²                      |

**Notes importantes :**
- Les valeurs de **pincement (quasi-statique)** sont **40-65% inférieures** aux valeurs d'impact
- Ces seuils représentent le **seuil de douleur**, pas de blessure
- Ce sont des **valeurs conservatrices** issues de recherches scientifiques
- Les valeurs continuent d'être affinées par la recherche

**Références :**
- [ISO/TS 15066 Explained: Force & Speed Limits | Robotiq](https://www.automate.org/robotics/tech-papers/iso-ts-15066-explained)
- [Robot Safety Standards Guide 2026 | GrabaRobot](https://www.grabarobot.com/blog/robot-safety-iso-standards-guide-2026/)
- [Power and Force Limiting Technique | MM Science Journal](https://www.mmscience.eu/journal/issues/june-2021/articles/power-and-force-limiting-technique-at-collaborative-workplace/download)

---

## 🔧 Conditions de Sécurité par Mode Collaboratif

### Mode 1 : Coexistence

**Définition :** Même environnement, pas la même activité.

**Conditions à respecter :**

✅ **Séparation physique ou temporelle obligatoire**
- Barrières physiques (garde-corps, cages)
- OU zones temporelles distinctes (robot actif → humain absent)

✅ **Détection de présence**
- Capteurs périmètriques (laser, rideau lumineux)
- Arrêt automatique si détection humaine dans zone robot

✅ **Signalisation claire**
- Marquage au sol des zones (humain / robot / partagée)
- Signaux lumineux (vert = sûr, rouge = robot actif)

✅ **Distances minimales** (si protection par détection) :
- Appliquer ISO 13857 : hauteur barrière ≥ 1 400 mm
- Distance de sécurité selon vitesse robot

**Niveau de sécurité :** Performance Level (PL) d ou e

---

### Mode 2 : Synchronisation

**Définition :** L'un utilise les pièces que l'autre apporte, sans interaction directe.

**Conditions à respecter :**

✅ **Séquencement temporel strict**
- Logique de contrôle : humain termine → robot démarre
- Pas de chevauchement temporel des activités

✅ **Zone tampon (buffer zone)**
- Espace intermédiaire pour déposer/récupérer les pièces
- Aucun des deux n'entre dans la zone en même temps

✅ **Détection de présence humaine dans zone robot**
- Capteurs de proximité (laser scanner, caméras 3D)
- Arrêt immédiat si humain détecté dans zone robot

✅ **Surveillance vitesse et séparation (SSM)**
- Appliquer la formule ISO/TS 15066 (voir ci-dessus)
- Distance minimale typique : **1,5 à 2 mètres**

✅ **Indicateurs visuels/sonores**
- Signaux avant démarrage robot
- Bip sonore / lumière clignotante

✅ **Temps de réaction système** :
- TR (détection + traitement) ≤ 300 ms
- TS (arrêt robot) mesuré et validé

**Niveau de sécurité :** PL d (Speed & Separation Monitoring)

---

### Mode 3 : Coopération

**Définition :** Même espace, travaillent sur la même pièce sans se toucher directement.

**Conditions à respecter :**

✅ **Surveillance continue vitesse et séparation**
- Distance de sécurité dynamique recalculée en temps réel
- Robot ralentit quand humain s'approche
- Robot s'arrête si distance < seuil minimal

✅ **Capteurs multiples redondants**
- Laser scanners 3D (type SICK, Pilz)
- Caméras de profondeur (détection posture humaine)
- Redondance pour fiabilité PL d

✅ **Zones de travail définies**
- Zone humain prioritaire (robot interdit)
- Zone robot prioritaire (humain averti)
- Zone partagée (surveillance SSM active)

✅ **Limitation de vitesse robot**
- Vitesse réduite en zone collaborative (typ. 250 mm/s max)
- Vitesse normale hors présence humaine

✅ **Arrêt d'urgence accessible**
- Boutons E-stop à portée humain
- Arrêt en moins de 500 ms

**Distances de sécurité** :
- Appliquer formule SSM ISO/TS 15066
- Marge de sécurité C ≥ 250 mm
- Distance typique maintenue : **1 à 1,5 m**

**Niveau de sécurité :** PL d (Speed & Separation Monitoring avancé)

---

### Mode 4 : Collaboration (contact direct possible)

**Définition :** Les deux travaillent dans le même espace avec interaction entre eux (ex : guidage manuel, contact physique).

**Conditions à respecter :**

✅ **Limitation de puissance et force (PFL)**
- Respecter les seuils ISO/TS 15066 Annexe A (voir tableau ci-dessus)
- Mesure en temps réel des forces de contact
- Arrêt si dépassement seuil

✅ **Géométrie de contact sûre**
- Surfaces arrondies (rayon ≥ 10 mm)
- Éviter arêtes vives, pincements
- Effecteurs "soft" (mousse, caoutchouc)

✅ **Vitesse limitée du robot**
- Vitesse TCP (Tool Center Point) ≤ 250 mm/s en zone contact
- Certains cobots : jusqu'à 500 mm/s selon masse effective

✅ **Masse effective réduite**
- Minimiser masse effecteur + charge utile
- Utiliser outils légers

✅ **Surveillance de couple moteur**
- Détection collision par variation couple
- Seuil de couple paramétré selon zone du corps

✅ **Mode guidage manuel (hand guiding)**
- Bouton "homme mort" (dead-man switch)
- Relâchement bouton → arrêt immédiat

✅ **Test de validation** :
- Mesurer forces de contact réelles avec dynamomètre
- Valider conformité avec seuils ISO/TS 15066
- Tests sur toutes les zones du corps potentiellement exposées

**Formule vitesse maximale (approximation) :**

```
v_max ≈ √(2 · E_max / m_eff)

où E_max = f_max² / (2·k)
```

- **f_max** = force maximale autorisée pour la zone du corps (N)
- **k** = constante de raideur du corps humain (N/mm) — typ. 25 à 75 N/mm
- **m_eff** = masse effective au point de contact (robot + charge + effecteur) (kg)

**Exemple :**
- Zone : avant-bras (muscle) → f_max = 160 N (transitoire)
- k = 50 N/mm
- m_eff = 5 kg (cobot léger + effecteur)

```
E_max = 160² / (2 · 50) = 25 600 / 100 = 256 J
v_max ≈ √(2 · 256 / 5) ≈ √102,4 ≈ 10,1 m/s
```

Mais en pratique, vitesse limitée à **0,25 m/s (250 mm/s)** pour garantir sécurité.

**Niveau de sécurité :** PL d ou e (Power & Force Limiting)

**Références :**
- [ISO/TS 15066 Technical Specification (PDF)](https://www.diag.uniroma1.it/deluca/pHRI_elective/ISO_TS_15066_2016_en.pdf)
- [Industrial Robot Safety Standards 2026 | EVS International](https://www.evsint.com/industrial-robot-safety-standards-iso-10218-ce-marking-2026/)

---

## 🎯 Application au Projet PRBE — Ligne ALIX

### Scénarios à modéliser

#### 1. Coexistence
- Opérateur et robot dans même cellule, activités séparées
- **Distance** : barrière virtuelle ou physique à 1,4 m minimum
- **Capteurs** : détection périmétrique

#### 2. Synchronisation ⭐ (priorité)
- Opérateur place pièce → robot récupère pièce
- **Distance** : formule SSM → environ **1,5 à 2 m** de séparation minimale
- **Capteurs** : laser scanner 3D (détection présence zone robot)
- **Temps de réaction** : TR + TS ≤ 0,7 s

#### 3. Coopération (optionnel)
- Opérateur et robot travaillent sur même pièce sans contact
- **Distance** : SSM dynamique, distance maintenue 1 à 1,5 m
- **Capteurs** : surveillance continue position humaine

#### 4. Collaboration (hors scope ?)
- Contact direct humain-robot
- **Force** : respecter seuils Annexe A ISO/TS 15066
- **Vitesse** : ≤ 250 mm/s

---

## 📊 Données à collecter pour RoboDK

Pour paramétrer correctement la simulation, mesurer/obtenir :

✅ **Robot ALIX :**
- Temps d'arrêt TS à différentes vitesses
- Masse effective (bras + effecteur + charge)
- Vitesse maximale TCP
- Précision positionnement (ZR)

✅ **Capteurs de sécurité :**
- Type (laser scanner, caméra 3D, rideau lumineux)
- Temps de réponse TR
- Précision de détection ZS
- Portée et champ de vision

✅ **Environnement :**
- Dimensions cellule ALIX
- Position convoyeur, bacs, zones opérateur
- Marquage au sol existant

✅ **Opérateur (mannequin) :**
- Dimensions anthropométriques (basées sur Niko_v1.urdf)
- Vitesse de marche (1,6 m/s par défaut)
- Zones du corps exposées au robot

---

## 📚 Normes de référence complètes

- **ISO 10218-1:2025** — Robots industriels (fabricants)
- **ISO 10218-2:2025** — Applications et cellules robotiques (intégrateurs)
- **ISO/TS 15066:2016** — Robots collaboratifs (intégré dans ISO 10218-2:2025)
- **ISO 13857:2019** — Distances de sécurité (membres supérieurs et inférieurs)

---

*Document créé le 19 mai 2026 pour [[Projet PRBE 2026]]*
*Basé sur les normes ISO 10218-1/2:2025, ISO/TS 15066:2016, ISO 13857:2019*
