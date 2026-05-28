# Compte rendu — Réunion PRBE du 28 mai 2026

**Date :** 28 mai 2026  
**Durée :** ~54 min  
**Participants :** Niko (Nikoloz Khachidze) + encadrant  
**Outil :** Google Meet (enregistrement Fathom)

> **Note de lecture :** le compte rendu auto-généré par Fathom remplace systématiquement le nom du logiciel de simulation par « Fathom » (qui est l'outil d'enregistrement de la réunion). Partout où il était question de « licence Fathom » ou de « convention Fathom », il faut lire **RoboDK**.

---

## 1. Scénarios — périmètre resserré

Deux scénarios sont confirmés comme prioritaires. Par rapport au 20 mai, le périmètre est simplifié.

### Scénario 1 — Sécurité

Le robot **s'arrête complètement** dès qu'un humain est détecté dans une zone de sécurité à faible distance, et coexiste avec l'opérateur sans créer de danger.

*(Simplification depuis le 20 mai : on retient l'arrêt complet à faible distance plutôt que la logique ralentissement 1 m / arrêt 0,5 m.)*

### Scénario 2 — Synchronisation

Le robot livre une pièce du stock dans une zone définie, l'opérateur la récupère puis réalise son assemblage.

### Hors périmètre (confirmé)

L'équipe ne simulera **pas** :
- la mécanique fine du mouvement humain ;
- le contact physique direct homme-robot ;
- la capture du robot par caméra.

Ces aspects ne sont pas essentiels aux objectifs actuels du projet.

---

## 2. Stratégie de synchronisation — déclencheurs plutôt que temps fixe

L'idée d'un **intervalle de temps fixe** (10-15-20 s) pour la passation est **rejetée** : peu fiable, échoue si l'opérateur est retardé. On ne parlerait plus de synchronisation.

**Solution retenue — déclencheurs (triggers) :**
- À son arrivée, le robot émet une **alerte visuelle / sonore** confirmant que la pièce est prête à être récupérée.
- La passation est conditionnée par cet événement, pas par un chrono.

**Mise en œuvre côté code :** ajouts simples, type `insert log` (ou équivalent) à des positions clés — un log quand le robot arrive en position, un signal quand la pièce est déposée. La synchronisation repose sur l'enchaînement d'états, pas sur une temporisation.

---

## 3. Bloqueurs identifiés

### 3.1 Convention de système de coordonnées (à trancher)

Ambiguïté sur la convention de repères à utiliser : **convention par défaut de RoboDK** vs **convention propre au robot UR** (Universal Robots).

- Le robot a sa propre définition de repère de base (axe Z porteur du bras, X/Y définis par la base) ; RoboDK propose une convention X, Y, Z standard.
- Tant que la convention n'est pas fixée, la **modélisation cinématique précise est bloquée**.
- Peu importe la convention choisie au fond — l'important est d'en **choisir une et de la documenter clairement** (repère de référence + comment sont exprimées rotations / vitesses / positions des articulations). C'est la base mathématique du modèle.

### 3.2 Licence RoboDK

Erreur de licence au lancement : message **« maintenance not removed »** qui empêche d'exécuter la simulation.

- Dépannage prévu : **tester sur un autre PC** pour écarter un problème spécifique à la machine / à la licence.

---

## 4. Plan de développement (3-4 semaines)

Objectif : passer de la **phase active** (cadrage / modélisation) à la **phase de développement** complète, pour soutenir la présentation finale.

**Focus :**
1. **Tester l'interface Python** en pilotant les articulations **une par une** (contrôle individuel des joints).
2. **Intégrer le modèle cinématique complet** une fois l'interface validée.

**Logique :** une interface Python opérationnelle est le socle nécessaire pour ensuite construire et tester les scénarios dans l'environnement de simulation. On valide d'abord qu'on sait actionner chaque articulation, puis on associe chaque joint du modèle à la simulation.

---

## 5. Prochaines étapes

| # | Tâche | Responsable | Échéance |
|---|---|---|---|
| 1 | Résoudre l'erreur de licence RoboDK (tester sur un autre PC) | Niko | avant prochaine réunion |
| 2 | Clarifier et **documenter** la convention de repères choisie pour le modèle robot | Niko | avant prochaine réunion |
| 3 | Tester l'interface Python (contrôle des articulations + intégration cinématique) | Niko | phase de dev |
| 4 | Planifier / préparer le point d'avancement | Équipe | mercredi 3 juin |

---

*Prochain RDV : mercredi 3 juin 2026 — revue des avancées (interface Python + convention de repères).*
