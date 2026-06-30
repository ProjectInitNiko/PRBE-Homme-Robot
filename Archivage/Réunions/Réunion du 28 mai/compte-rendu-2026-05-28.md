# Compte rendu — Réunion PRBE du 28 mai 2026

**Date :** 28 mai 2026  
**Durée :** ~54 min  
**Participants :** Niko (Nikoloz Khachidze), équipe PRBE, encadrants (Francesco Ciampi, Thierno Diallo)  
**Outil :** Google Meet (enregistrement Fathom)

> **Note de lecture :** le compte rendu auto-généré par Fathom remplace systématiquement le nom du logiciel de simulation par « Fathom » (qui est l'outil d'enregistrement). Partout où il était question de « licence Fathom » ou de « convention Fathom », il faut lire **RoboDK**.

---

## 1. Scénarios — périmètre resserré

Deux scénarios sont confirmés comme prioritaires. Par rapport au 20 mai, le périmètre est simplifié.

### Scénario 1 — Sécurité

Le robot **s'arrête complètement** dès qu'un humain est détecté dans une zone de sécurité à faible distance, et coexiste avec l'opérateur sans créer de danger.

*(Simplification depuis le 20 mai : on retient l'arrêt complet à faible distance plutôt que la logique ralentissement 1 m / arrêt 0,5 m.)*

**Points à préciser (soulevés par l'encadrant) :**
- **Réduire le temps d'attente** : le seuil de **30 s** (logique « porte » du 20 mai) est jugé trop long → raccourcir le délai de réaction du robot.
- **Nature des contraintes** : déterminer si les contraintes de sécurité sont **strictes / fortes** ou souples.
- **Justifier la priorité** : expliciter pourquoi la **sécurité** est prioritaire dans ce scénario (sur quelle base : importance, niveau de risque…).

### Scénario 2 — Synchronisation (échange de pièces)

Le robot livre une pièce du stock dans une zone définie, l'opérateur la récupère, l'assemble, puis le robot reprend la pièce assemblée. Voir §2 pour le mécanisme de passation.

### Hors périmètre — et pourquoi

L'équipe ne simulera **pas** les aspects ci-dessous. Deux raisons distinctes : soit l'aspect **n'est pas nécessaire** aux objectifs, soit il relève des **perspectives** (traitable plus tard, « si on avait plus de temps »).

| Aspect écarté | Raison |
|---|---|
| Mécanique fine du mouvement humain | **Pas nécessaire** — les scénarios reposent sur les positions / déplacements, pas sur une biomécanique réaliste. |
| Contact physique direct homme-robot | **Pas nécessaire** — le scénario sécurité impose un arrêt *avant* tout contact ; la synchro est une passation sans contact simultané. |
| Capture du robot / opérateur par caméra | **Perspective** — utile pour relier l'espace réel ↔ la simulation, mais traitable plus tard (déjà cité dans les perspectives du rapport). |

> De façon générale, parmi les modes de collaboration H-R envisageables, certains ne sont pas nécessaires à nos objectifs, d'autres relèvent des perspectives à traiter avec plus de temps.

---

## 2. Stratégie de synchronisation — déclencheurs plutôt que temps fixe

L'idée d'un **intervalle de temps fixe** (10-15-20 s) pour la passation est **rejetée** : peu fiable, échoue si l'opérateur est retardé — on ne parlerait plus vraiment de synchronisation.

**Solution retenue — déclencheurs (triggers) :** la synchronisation ne repose **pas seulement sur le temps**, mais aussi sur des **événements**. Le robot peut émettre des **sons** ou des **signaux lumineux** (fonction trigger), dans les deux sens de la passation :
- **Robot → opérateur** : message sonore / lumineux quand le robot **dépose** une pièce → elle est prête à être récupérée.
- **Opérateur → robot** : signal quand l'opérateur a **déposé une pièce assemblée** → prête à être reprise par le robot.

**Mise en œuvre côté code :** ajouts simples, type `insert log` (ou équivalent) à des positions clés — un log / signal quand le robot arrive en position, un autre quand la pièce est déposée. La synchronisation repose sur l'**enchaînement d'états**, pas sur une temporisation.

---

## 3. Schéma cinématique & formulation mathématique — retours encadrants

### Schéma cinématique
- Produire le schéma en **vue frontale** *et* **vue latérale** (pas une seule projection).
- La norme **ISO 3952** (symboles de schémas cinématiques) est citée, mais **à vérifier** : Ciampi doute qu'elle soit réellement / correctement appliquée. Confirmer la conformité avant de s'appuyer dessus.

### Formulation mathématique (à REVOIR)
- **Reprendre la définition des bases** : poser clairement le **repère de base** et son utilisation.
- Définir **comment sont exprimées les rotations**.
- Rester **synthétique sur les DDL** : ne pas entrer dans trop de détails (sinon trop compliqué) — s'appuyer sur le repère de base.
- **Récupérer le cours de SYRO** comme référence.
- Dans le **rapport final** : préciser **à quelle rotation on fait référence** et fournir une **base mathématique** claire.

---

## 4. Bloqueurs identifiés

### 4.1 Convention de système de coordonnées (à trancher)

Ambiguïté sur la convention de repères à utiliser : **convention par défaut de RoboDK** vs **convention propre au robot UR** (Universal Robots).

- Le robot a sa propre définition de repère de base (axe Z porteur du bras, X / Y définis par la base) ; RoboDK propose une convention X, Y, Z standard.
- Tant que la convention n'est pas fixée, la **modélisation cinématique précise est bloquée**.
- Peu importe la convention choisie au fond — l'important est d'en **choisir une et de la documenter clairement** (repère de référence + comment sont exprimées rotations / vitesses / positions des articulations). C'est la base mathématique du modèle.

### 4.2 Licence RoboDK

Erreur de licence au lancement : message **« maintenance not removed »** qui empêche d'exécuter la simulation.

- Dépannage prévu : **tester sur un autre PC** pour écarter un problème spécifique à la machine / à la licence.

---

## 5. Plan de développement (3-4 semaines)

Objectif : passer de la **phase active** (cadrage / modélisation) à la **phase de développement** complète, pour soutenir la présentation finale.

**Séquence de travail :**
1. **Tester l'environnement** RoboDK, puis **tester Python dans l'environnement**.
2. **Intégrer la partie cinématique** : déterminer **quoi actionner pour déplacer l'humain**, et **définir les fonctions qui pilotent les joints** (articulation par articulation).
3. Une fois que **ça marche dans Python**, le transposer **dans la simulation**.
4. **Intégrer la librairie GitHub dans RoboDK** — et clarifier **les exigences** que ça implique.

**Logique :** une interface Python opérationnelle est le socle pour construire et tester les scénarios. On valide d'abord qu'on sait actionner chaque articulation, puis on associe chaque joint du modèle à la simulation.

---

## 6. Prochaines étapes

| # | Tâche | Responsable | Échéance |
|---|---|---|---|
| 1 | Résoudre l'erreur de licence RoboDK (tester sur un autre PC) | Niko | avant prochaine réunion |
| 2 | Trancher **et documenter** la convention de repères (RoboDK vs UR) | Niko | avant prochaine réunion |
| 3 | Tester l'environnement + l'interface Python (contrôle des joints, fonctions d'actionnement) | Niko | phase de dev |
| 4 | Intégrer la librairie GitHub dans RoboDK + clarifier les exigences | Équipe | phase de dev |
| 5 | Schéma cinématique en **vue frontale + latérale** | Équipe | — |
| 6 | **Vérifier la conformité ISO 3952** du schéma | Équipe | — |
| 7 | Revoir la formulation mathématique (repère de base, rotations) + récupérer le **cours de SYRO** | Équipe | — |
| 8 | Préciser scénario 1 : réduire le délai (30 s), nature des contraintes, justification priorité sécurité | Équipe | — |
| 9 | Préparer le point d'avancement | Équipe | mercredi 3 juin |

**Perspective (mentionnée par Diallo) :** après le cahier des charges, **explorer une autre méthode de modélisation humaine** — pas obligatoire, mais à garder en tête.

---

*Prochain RDV : mercredi 3 juin 2026 — revue des avancées (environnement + interface Python, convention de repères, schéma).*
