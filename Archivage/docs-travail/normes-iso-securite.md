# Normes ISO — Sécurité Robots Industriels et Collaboratifs

## Vue d'ensemble

Trois normes principales régissent la sécurité des robots industriels et collaboratifs :

- **ISO 10218-1** : Exigences pour les **fabricants** de robots
- **ISO 10218-2** : Exigences pour les **intégrateurs** de cellules robotiques
- **ISO/TS 15066** : Spécifications techniques pour les **robots collaboratifs** (intégrée dans ISO 10218-2:2025)

---

## ISO 10218-1 : Robots industriels (Fabricants)

### Objectif
Définir les exigences de sécurité que les fabricants de robots doivent respecter lors de la **conception et construction** du matériel et du contrôleur.

### Cible
Fabricants de robots (OEM) : FANUC, Yaskawa, ABB, KUKA, Universal Robots, etc.

### Périmètre
- Conception mécanique sûre
- Architecture du système de contrôle
- Fonctions d'arrêt (arrêt protégé, arrêt d'urgence)
- Surveillance de la vitesse et de la force
- Sorties de sécurité requises du robot

### Évolution 2025
La révision **ISO 10218-1:2025** introduit :
- Deux classes de robots industriels :
  - **Classe 1** : Robots très faibles, risques limités → exigences de contrôle réduites (PL b)
  - **Classe 2** : Robots standard
- Expansion significative de la **sécurité fonctionnelle** et de la **cybersécurité**
- Intégration normative de ISO/TS 15066

### Références
- [ISO 10218-1:2025 - Robotics — Safety requirements — Part 1: Industrial robots](https://www.iso.org/standard/73933.html)
- [ISO 10218-1:2025—Robots And Robotic Devices Safety - The ANSI Blog](https://blog.ansi.org/ansi/iso-10218-1-2025-robots-and-robotic-devices-safety/)
- [Industrial Robot Safety Standards: ISO 10218, ISO/TS 15066 & CE Marking (2026)](https://www.evsint.com/industrial-robot-safety-standards-iso-10218-ce-marking-2026/)

---

## ISO 10218-2 : Applications et cellules robotiques (Intégrateurs)

### Objectif
Spécifier les exigences de sécurité pour l'**intégration, la mise en service, l'exploitation, la maintenance et le démantèlement** des robots dans des environnements industriels.

### Cible
Intégrateurs de systèmes et utilisateurs finaux.

### Périmètre
- Évaluation des risques de la cellule robotique complète (pas seulement le robot isolé)
- Protection des opérateurs (intégration, programmation, maintenance)
- Méthodes de protection :
  - Barrières périmètriques (garde-corps)
  - Détecteurs de présence (capteurs)
  - Arrêts d'urgence et verrouillages
- Vérification des fonctions de sécurité avant mise en production

### Responsabilités de l'intégrateur
- Évaluer les risques pour la cellule complète (taille des pièces, trajectoires, vitesse, machines liées)
- Impliquer l'utilisateur dans l'évaluation des risques (opérateurs, maintenance)
- Vérifier que chaque fonction de sécurité fonctionne correctement :
  - Mesurer les distances d'arrêt réelles vs calculées
  - Tester chaque verrouillage et circuit E-stop
  - Confirmer la logique des PLC de sécurité

### Évolution 2025
La révision **ISO 10218-2:2025** :
- Passe de 80 à **234 pages** (expansion majeure)
- Intègre les exigences collaboratives de **ISO/TS 15066**
- Permet une prise en compte plus différenciée des risques réels

### Références
- [ISO 10218-2:2025 - Robotics — Safety requirements — Part 2: Industrial robot applications and robot cells](https://www.iso.org/standard/73934.html)
- [ISO 10218-2:2025—Industrial Robot Applications - The ANSI Blog](https://blog.ansi.org/ansi/iso-10218-2-2025-industrial-robot-applications/)
- [EN ISO 10218-2: Robot systems and integration](https://www.gt-engineering.it/en/technical-standards/en-iso-standards/en-iso-10218-1-safety-requirements-for-industrial-robots/en-iso-10218-2/)

---

## ISO/TS 15066 : Robots collaboratifs

### Objectif
Fournir des directives détaillées sur la sécurité des **opérations collaboratives** homme-robot, en particulier les limites de force et de vitesse.

### Statut actuel
- **ISO/TS 15066:2016** était la spécification technique principale jusqu'en 2025
- Depuis **ISO 10218-2:2025**, ses exigences ont été **intégrées normativement** dans la norme principale
- Reste valide pour les évaluations héritées, mais pour les nouvelles installations → utiliser ISO 10218-2:2025

### Quatre techniques d'opération collaborative

1. **Coexistence** : même environnement, pas la même activité
2. **Synchronisation** : l'un utilise les pièces que l'autre apporte, sans interaction directe
3. **Coopération** : même espace, travaillent sur la même pièce sans se toucher directement
4. **Collaboration** : les deux travaillent dans le même espace avec interaction entre eux

### Modes de protection collaborative

a) **Arrêt surveillé à sécurité intégrée** (*Safety rated monitored stop*)
b) **Guidage manuel** (*Hand guiding*)
c) **Surveillance de vitesse et séparation** (*Speed and separation monitoring*)
d) **Limitation de puissance et de force** (*Power and force limiting*)

### Limitation de puissance et de force (PFL)

**Principe** : Le robot peut entrer en contact avec l'humain, mais les forces/pressions doivent rester sous des **seuils de douleur biomécanique**.

**Base scientifique** : Étude de l'Université de Mayence (Allemagne) sur 100 sujets → établit les seuils de force et de pression pour **29 zones du corps humain**.

**Tableau Annexe A** : Valeurs maximales de force et de pression autorisées par région corporelle (ex : tête, torse, bras, mains).

**Formule de vitesse maximale** : Dépend de :
- Masse effective au point de contact (masse robot + charge utile + effecteur)
- Géométrie de contact
- Limite de force applicable à la zone du corps

### Références
- [ISO/TS 15066:2016 - Robots and robotic devices — Collaborative robots](https://www.iso.org/standard/62996.html)
- [Standardizing Collaborative Robots: What is ISO/TS 15066? - Engineering.com](https://www.engineering.com/standardizing-collaborative-robots-what-is-iso-ts-15066/)
- [ISO/TS 15066 Explained: Force & Speed Limits for Cobots](https://eureka.patsnap.com/article/isots-15066-explained-force-speed-limits-for-cobots)
- [Tech Papers: ISO/TS 15066 Explained | Robotiq](https://www.automate.org/robotics/tech-papers/iso-ts-15066-explained)

---

## Mesures de sécurité selon les normes

### Niveaux de sécurité (Safety Integrity Level)

- **Lvl 1** : Safety rated monitored stop (arrêt surveillé)
- **Lvl 2** : Hand guiding (guidage manuel)
- **Lvl 3** : Speed & separation monitoring (surveillance vitesse et séparation)
- **Lvl 4** : Power & force limiting (limitation puissance et force)

### Application au projet PRBE

Pour les scénarios **Synchronisation** et **Coexistence** :
- Utiliser **Lvl 3** (Speed & separation monitoring) comme baseline
- Implémenter des zones de détection de présence
- Calculer les distances de sécurité en fonction de la vitesse du robot
- Tester les temps de réaction du système (capteurs → arrêt robot)

---

## Synthèse pour le projet

| Norme           | Concerne             | Pertinence PRBE                                                      |
| --------------- | -------------------- | -------------------------------------------------------------------- |
| ISO 10218-1     | Fabricants robots    | Contexte (connaître les capacités sécurité du robot ALIX)           |
| ISO 10218-2     | Intégrateurs         | **Directement applicable** — conception cellule, évaluation risques  |
| ISO/TS 15066    | Collaboration H-R    | **Directement applicable** — scénarios collaboratifs, limites force  |

**Prochaines étapes** :
1. Identifier le robot ALIX et ses capacités sécuritaires (ISO 10218-1)
2. Définir les zones de sécurité de la cellule (ISO 10218-2)
3. Appliquer les seuils de force/vitesse aux scénarios collaboratifs (ISO/TS 15066)

---

*Document créé le 19 mai 2026 pour le [[Projet PRBE 2026]]*
