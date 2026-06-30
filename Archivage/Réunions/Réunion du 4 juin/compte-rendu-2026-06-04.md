# Compte rendu — Réunion PRBE du 4 juin 2026

**Date :** 4 juin 2026  
**Durée :** ~57 min  
**Participants :** Niko (Nikoloz Khachidze), équipe PRBE (Luc, Alex), encadrants (Francesco Ciampi, Thierno Diallo)  
**Outil :** Google Meet (enregistrement Fathom)

> **Note de lecture :** le résumé auto-généré par Fathom transcrit cette fois le nom du logiciel de simulation en « Robodeca ». Partout où il en est question, il faut lire **RoboDK**.

---

## 1. Démo — opérateur articulé 22 DDL fonctionnel

L'opérateur articulé (22 DDL, construit depuis le STEP via l'API Python) est opérationnel dans RoboDK, avec deux animations de marche embarquées (marche militaire sur place + marche avant). La revue d'avancement s'est concentrée sur le bug d'import restant et sur la suite (scénarios, rapport, poster).

---

## 2. Bug critique — le mannequin « explose » à la réouverture

### Symptôme

À la réouverture de la station `.rdk`, le modèle humain « explose » : les membres se détachent et se dispersent.

### Diagnostic (en séance)

**Désalignement de repères** :
- Le repère **`HumanBase`**, qui ancre le modèle, se retrouve **déplacé par rapport à son origine attendue (0,0,0)**.
- Les articulations sont définies par des **repères imbriqués** (jusqu'à 3 par articulation pour décomposer les rotations d'Euler) → structure profonde, sujette aux erreurs si un seul maillon est désaligné.
- La cause racine semble liée au **processus d'import non standard** (STEP → Split → rig par API).

### Contournement trouvé en séance

**Ouvrir le fichier `.rdk` directement** (double-clic depuis l'explorateur), et **non via le menu « Ouvrir »** de RoboDK. Cela contourne le bug — mais ne corrige pas la cause racine.

### Stratégie de débogage retenue

L'objectif est de **comprendre pourquoi** le désalignement se produit, pas seulement de le masquer :
- Ajouter des **`print()` de debug** pour journaliser les positions des repères (`HumanBase` et descendants) **à chaque étape** du processus d'import/rebuild.
- Comparer les poses avant sauvegarde / après réouverture pour localiser l'étape qui décale.

---

## 3. Bonnes pratiques code (retours encadrants)

- Garder le **script principal RoboDK centré sur la logique de simulation**.
- Pour les outils externes, passer par de la **communication inter-processus** (par ex. sockets) plutôt que d'intégrer tout le code dans l'environnement de simulation.

---

## 4. Documentation — cahier des charges & rapport

### Cahier des charges

Le document (**17 pages**) est **terminé** et sera intégré au rapport final. Deux options de structure à trancher :

| Option | Conséquence |
|---|---|
| Cahier des charges en **document à part** | Le rapport contient un **contexte général** qui le présente |
| Cahier des charges en **annexe** | Le rapport **s'y réfère** explicitement |

### Contenu du rapport

- Mettre **en annexe les librairies utilisées**.
- Mettre **le lien du repo GitHub** dans le rapport (et l'ajouter sur Teams).

### Périmètre (confirmé / précisé)

- **Hors périmètre :** simulation biomécanique complète, contact physique direct homme-robot.
- **Perspectives (travaux futurs) :** capture de mouvement en temps réel.
- **Scénario 2 (synchronisation) confirmé** avec les **déclencheurs** (signaux lumineux / sonores) pour signaler qu'une pièce est prête à être prise — coordination humain-robot bidirectionnelle.

---

## 5. Schéma cinématique — version lisible pour le poster

- Produire une **représentation cinématique d'un humain simplifiée et lisible** (*user-friendly*) pour le **poster** et la **présentation finale** — le schéma actuel est trop technique pour un public non expert.
- La faire **avec un outil** (pas à la main).
- Produire aussi un **visuel de la marche en vue de profil** (cinématique de marche) pour le poster / la présentation.

---

## 6. Nouvelles fonctionnalités de simulation

### Marche sur trajectoire

Améliorer la fonction de marche pour **suivre une trajectoire définie en externe** — y compris une trajectoire **qui peut changer (non linéaire)** — au lieu d'un simple déplacement rectiligne. Étapes : définir la trajectoire, puis l'implémenter dans RoboDK.

### Tâche du membre supérieur (bras)

Simuler une **activité de poste de travail** : la **main fixée** (sans déplacement) à côté d'une table, le bras qui s'articule autour — pour simuler une tâche d'opérateur.

---

## 7. Session de travail — mercredi 11 juin

- **Session de travail de 3-4 h planifiée le mercredi 11 juin à 14 h** (organisée par Thierno Diallo).
- Une **licence RoboDK temporaire** sera fournie pour la session.
- **Objectifs de la session :** résoudre le problème de repères + simuler la tâche bras.

---

## 8. Prochaines étapes

| # | Tâche | Responsable | Échéance |
|---|---|---|---|
| 1 | Ajouter des **prints de debug** (positions des repères à chaque étape de l'import) | Niko | avant le 11 juin |
| 2 | **Déposer les fichiers RoboDK sur Teams**, puis déboguer repères / `HumanBase` | Niko | avant le 11 juin |
| 3 | Déposer le **code Python** sur Teams + ajouter le **lien GitHub** (Teams + rapport) | Niko | avant le 11 juin |
| 4 | **Définir une trajectoire de marche externe**, puis l'implémenter dans RoboDK | Niko | — |
| 5 | Simuler la **tâche bras** (main fixe, table) | Niko | session du 11 juin |
| 6 | **Visuel marche vue de profil** (cinématique) pour poster / présentation | Niko | — |
| 7 | **Schéma cinématique simplifié** (avec un outil, lisible pour le poster) | Équipe | — |
| 8 | Trancher la **structure du cahier des charges** (document à part vs annexe) | Équipe | rapport final |
| 9 | Organiser la session 3-4 h du 11 juin + fournir la **licence RoboDK temporaire** | Thierno Diallo | 11 juin, 14 h |

---

*Prochain RDV : **mercredi 11 juin 2026, 14 h** — session de travail de 3-4 h (licence temporaire fournie) : résolution du problème de repères + simulation du bras.*
