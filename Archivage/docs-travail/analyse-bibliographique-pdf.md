# Analyse bibliographique — Sources PDF

> Analyse de 4 papiers scientifiques identifiés comme sources pour l'état de l'art du projet PRBE 2026 (Simulation du mouvement humain et interaction H-R dans RoboDK, ISAE-Supméca, sujet #47).
> Date : 2026-05-12

---

## PDF 1 — Stable Whole-Body Motion Generation for Humanoid Robots to Imitate Human Motions

**Auteurs :** Seungsu Kim, ChangHwan Kim, Bumjae You, Sangrok Oh
**Date :** 2009
**Source :** IEEE/RSJ IROS 2009, St. Louis, USA

### Résumé

Pipeline offline pour convertir des données de motion capture humaine en mouvements stables pour un robot humanoïde. Trois étapes : (1) modèle simplifié du corps humain pour estimer la trajectoire ZMP sans capteurs de force, (2) mapping cinématique pour adapter les mouvements membres supérieurs et inférieurs via scaling, (3) mapping dynamique sur la trajectoire du pelvis pour garantir la stabilité (ZMP dans la zone de support). Validé sur le robot MAHRU (KIST) avec une séquence de danse.

### Méthodes clés

- **Modèle corps simplifié** : cylindres, sphères, boîtes ; paramètres estimés par optimisation sur mocap + force plate
- **Mapping cinématique** : scaling géométrique pied/pelvis/ZMP, IK analytique membres inférieurs, optimisation pour les bras (redondants)
- **Mapping dynamique** : modèle pendule inversé + calcul CoM à partir du ZMP désiré, ajustement itératif du pelvis via Jacobien du CoM
- **ZMP (Zero Moment Point)** comme critère central de stabilité

### Pertinence pour PRBE

| Élément | Usage concret |
|---------|---------------|
| Modèle corps simplifié | Directement transposable pour construire un mannequin léger dans RoboDK |
| IK analytique membres inférieurs | Adaptable à un modèle 6-DoF par jambe |
| Scaling proportionnel | Méthode de mise à l'échelle selon la morphologie de l'opérateur |
| Pipeline mocap → articulaire | Montre comment convertir une trajectoire humaine en commandes joints |

### Limites

- Papier de 2009 — pas d'API Python, pas de URDF natif
- Partie "stabilité dynamique" moins critique pour un mannequin RoboDK cinématique
- Nécessite mocap réel pour initialiser le modèle simplifié

**Pertinence PRBE : Haute**

---

## PDF 2 — Human Whole-Body Dynamics Estimation for Enhancing Physical Human-Robot Interaction

**Auteurs :** Claudia Latella (superviseur : Francesco Nori)
**Date :** 2019 (arXiv:1912.01136v1)
**Source :** Thèse de doctorat — Università di Genova / IIT (Istituto Italiano di Tecnologia), Dynamic Interaction Control Lab

### Résumé

Thèse de 148 pages développant un framework pour l'estimation simultanée du mouvement et de la dynamique du corps humain entier en temps réel. Le modèle humain : système multi-corps articulé (23 links mobiles, 48 DoF internes), paramétré via données Xsens MVN. Algorithme d'estimation MAP combinant IMU, capteurs F/T et mocap. **C'est la base technique du générateur HMG de l'IIT** — dont le projet PRBE utilise déjà le repo.

### Méthodes clés

- **Modèle multi-corps** : 23 links (héritage Xsens MVN), joints à 3 DoF (spherical), géométries simples (parallélépipèdes, cylindres, sphères)
- **Propriétés inertielles** : tables anthropométriques Winter 1990 / Herman 2007, formules analytiques, densité isotrope par segment
- **URDF humain** : Annexe B entière dédiée — extension non-standard pour joints sphériques (URDF standard = joints mono-axe uniquement)
- **Dynamique inverse** : algorithme RNEA + estimateur MAP probabiliste

### Pertinence pour PRBE

| Élément | Usage concret |
|---------|---------------|
| Modèle 23 links / 48 DoF | Spec complète du modèle HMG : noms, géométries, frames, orientations |
| Tables anthropométriques | Formules reproductibles pour paramétrer la morphologie de l'opérateur |
| Annexe B (URDF) | Gestion des joints sphériques via virtual links — crucial pour l'import dans RoboDK |
| Annexe C (IK offline) | Méthode IK applicable sans matériel Xsens |

### Limites

- Thèse dense — parties utiles pour PRBE : Chapitre 3 + Annexes B et C
- Framework temps-réel nécessite IMU Xsens (matériel non dispo en simulation pure)
- Extension URDF non-standard = incompatibilité partielle avec les parseurs standards

**Pertinence PRBE : Haute** — référence directe du HMG, lecture indispensable avant tout travail d'import.

---

## PDF 3 — Understanding URDF: A Dataset and Analysis

**Auteurs :** Daniella Tola (Aarhus University), Peter Corke (QUT)
**Date :** Août 2023 (arXiv:2308.00514v1)
**Source :** Article de recherche, arXiv (cs.RO)

### Résumé

Premier dataset public de fichiers URDF (322 fichiers, 195 robots uniques) issu de 6 sources. Analyse statistique des patterns de construction URDF : types de maillages, types de joints, conventions de nommage. Constate que **RoboDK ne supporte pas le format URDF nativement** — une étape de conversion est nécessaire.

### Méthodes clés

- Dataset URDF : 322 fichiers catégorisés par source, type, fabricant
- Xacro : macro-langage XML pour générer des URDF modulaires (utilisé par HMG)
- Scripts Python pour parser, valider et comparer des URDF

### Pertinence pour PRBE

| Élément | Usage concret |
|---------|---------------|
| Constat RoboDK sans URDF natif | Confirme qu'une étape de conversion Python est nécessaire |
| Guide bonnes pratiques URDF | Comprendre et modifier le URDF généré par HMG |
| Xacro | Comprendre comment le HMG génère le URDF final |
| Scripts Python | Base réutilisable pour parser/valider le URDF du mannequin |

### Limites

- Papier purement descriptif — pas de solution technique à l'import RoboDK
- Centré sur les robots industriels, peu d'exemples humanoïdes

**Pertinence PRBE : Moyenne** — guide utile pour la chaîne URDF → RoboDK, pas une solution en soi.

---

## PDF 4 — Digital Human Modeling for Collaborative Robotics

**Auteurs :** Pauline Maurice (LORIA/Inria), Vincent Padois (ISIR, Sorbonne), Yvan Measson (CEA-LIST), Philippe Bidaud (ISIR/ONERA)
**Date :** 2019
**Source :** Chapitre de livre — *DHM and Posturography*, Elsevier 2019. HAL : hal-02389726

### Résumé

Chapitre de référence sur la simulation numérique humaine pour la robotique collaborative. Première partie : limitations des outils DHS existants (Jack, DELMIA, IMMA, RAMSIS) face aux scénarios de co-manipulation. Deuxième partie : contrôleur LQP (Linear Quadratic Programming) pour animer un mannequin 21 segments / 45 DoF en respectant dynamique, contacts et contraintes biomécaniques. Validation sur une tâche de co-manipulation avec un robot d'assistance.

### Méthodes clés

- **Contrôleur LQP** : optimisation quadratique multi-tâches avec contraintes d'inégalité (limites articulaires, friction, dynamique)
- **Modèle DHM** : 21 segments rigides, 45 DoF, scalable par coefficients anthropométriques
- **ZMP preview control** pour l'équilibre
- **Indicateurs ergonomiques** : position (écart à la posture neutre) + couple articulaire + modèle de fatigue temporelle

### Pertinence pour PRBE

| Élément | Usage concret |
|---------|---------------|
| Revue critique des outils DHS | Justifie les limites de RoboDK seul pour l'analyse ergonomique complète |
| Indicateurs ergonomiques | Méthodes de calcul applicables pour l'objectif sécurité/ergonomie de PRBE |
| Modèle 21 segments / 45 DoF | Comparable au HMG, avec spécification applicative (membres sup + inf + tronc) |
| Scénario co-manipulation | Correspond exactement au contexte ligne ALIX (opérateur + robot collaboratif) |

### Limites

- Contrôleur LQP nécessite un moteur physique (XDE ou équivalent) — non disponible nativement dans RoboDK
- Génération de placement des pieds reste manuelle
- Niveau de complexité mathématique élevé pour une implémentation Python from scratch

**Pertinence PRBE : Haute** — les indicateurs ergonomiques et la structure de simulation sont réutilisables même sans le LQP complet.

---

## Synthèse et recommandations

### Vue d'ensemble

Ces quatre papiers couvrent les trois niveaux du projet :

| Niveau | Source | Contribution |
|--------|--------|-------------|
| **Modèle** | Thèse IIT (PDF 2) + URDF paper (PDF 3) | Spec du mannequin, pipeline URDF → RoboDK |
| **Mouvement** | Kim et al. IROS 2009 (PDF 1) | IK analytique + scaling + pipeline mocap → joints |
| **Analyse** | Maurice et al. HAL (PDF 4) | Indicateurs ergonomiques, scénarios co-manipulation |

### Chaîne d'implémentation recommandée

```
HMG (IIT)
  └─ paramétré via tables Winter/Herman  [PDF 2, Chapitre 3]
  └─ structure URDF via                  [PDF 3] + [PDF 2, Annexe B]
       │
       ▼
Conversion Python → RoboDK
  └─ IK analytique membres inférieurs    [PDF 1, section III-B]
  └─ optimisation bras (scaling + IK)    [PDF 1, section III-A]
       │
       ▼
Scénarios H-R dans RoboDK
  └─ indicateurs ergonomiques            [PDF 4]
  └─ zones de proximité / conflit → analyse sécurité
```

### Ordre de lecture recommandé

1. **PDF 2 — Thèse IIT** (Chapitres 3 + Annexes B/C) — comprendre le modèle HMG en profondeur avant tout
2. **PDF 4 — DHM for Collaborative Robotics** — définir les métriques et objectifs d'analyse
3. **PDF 1 — Stable Whole-Body Motion** — pipeline de génération de mouvements
4. **PDF 3 — Understanding URDF** — référence technique lors de la conversion HMG → RoboDK

### Points à investiguer

- [ ] Vérifier si des plugins tiers permettent l'import URDF dans RoboDK
- [ ] Explorer l'Annexe C (IK offline) de la thèse IIT pour l'implémentation Python
- [ ] Évaluer si les indicateurs ergonomiques du PDF 4 sont calculables en Python pur (Jacobien transposé) sans LQP complet
