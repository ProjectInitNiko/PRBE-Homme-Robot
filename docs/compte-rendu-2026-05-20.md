# Compte rendu — Réunion PRBE du 20 mai 2026

**Date :** 20 mai 2026  
**Durée :** ~53 min  
**Participants :** Niko (Nikoloz Khachidze), Luc, Alex, Francesco Ciampi (encadrant), Thierno Diallo (encadrant)  
**Outil :** Google Meet + Teams (partage écran)

---

## 1. Scénarios retenus

Deux scénarios sont officiellement validés pour le projet.

### Scénario 1 — Coexistence (focus sécurité)

Objectif : assurer la sécurité de l'opérateur pendant le fonctionnement du Myrmidon 100.

**Infrastructure :** les détecteurs de présence du Myrmidon 100 sont déjà intégrés — aucun ajout matériel nécessaire.

**Règles de déplacement :**
- Ralentissement à **1 m** de présence humaine détectée
- Arrêt complet à **0,5 m**

*(Note : les distances de 1,5-2 m issues de l'analyse ISO/TS 15066 étaient trop conservatrices pour ce contexte ; Ciampi a validé 1 m pour le ralentissement.)*

**Logique d'interaction — passage de porte :**
- Si un humain est détecté à une porte et ne bouge pas pendant **30 secondes**, le robot recule pour lui céder le passage, puis reprend son trajet.

**Logique d'interaction — espace ouvert :**
- Le robot s'arrête et attend que l'humain se déplace de lui-même (la place est disponible autour).

---

### Scénario 2 — Synchronisation (focus efficacité)

Objectif : réduire les temps d'inactivité humain en faisant livrer les pièces par le robot pendant que l'opérateur travaille.

**Workflow :**
1. Robot prélève des pièces au stock
2. Robot livre les pièces dans la zone de travail de l'opérateur
3. Opérateur assemble les pièces
4. Robot récupère les pièces assemblées
5. Robot retourne les pièces assemblées au stock (ou zone dédiée)

**Contraintes :**
- Maximum **2 lots** simultanément dans la zone de travail : 1 en cours d'assemblage + 1 en attente (évite l'encombrement)
- Un détecteur d'état sera nécessaire au niveau de la zone de travail pour savoir si des lots sont déjà présents

**Sécurité :** les règles de coexistence (ralentissement/arrêt) s'appliquent également dans ce scénario.

**Point clé soulevé par Ciampi :** la synchronisation implique que l'humain et le robot opèrent *en même temps* sur la zone — ce n'est pas simplement diviser des tâches séquentielles. L'objectif est une vraie dynamique temporelle coordonnée.

---

## 2. Modèle cinématique du mannequin humain

**Approche retenue :** cinématique classique (non data-driven, non SMPL), pour permettre la simulation en temps réel dans RoboDK.

> SMPL a été écarté : modèle basé sur des milliers de scans 3D, plus adapté à la vidéo/animation qu'à la simulation robotique temps réel.

### Degrés de liberté retenus

| Segment | DDL | Détail |
|---|---|---|
| Buste → Cuisse (×2) | 3 par jambe | Mouvements fluides et courbés |
| Cuisse → Mollet (×2) | 1 par jambe | Flexion genou (pivot) |
| Cheville → Pied (×2) | 1 par jambe | Pivot cheville |
| **Total jambes** | **10** | |
| Épaule (×2) | 3 par bras | |
| Coude (×2) | 1 par bras | |
| Poignet (×2) | 2 par bras | |
| **Total bras** | **6** | |

**Simplifications :** pas de tête, cou, ni doigts — non critiques pour les scénarios définis.

**Choix justifié :** l'état de l'art (littérature URDF, travaux existants) confirme ces degrés de liberté pour des mannequins orientés déplacement et manipulation simple.

---

## 3. Plan sur 6 semaines

La semaine 1 est la semaine en cours (20 mai 2026). La semaine 6 couvre la période du 20 au 26 juin 2026 — la date précise de soutenance reste à confirmer.

| Semaine | Dates | Objectif |
|---|---|---|
| S1 | 20–26 mai | Finaliser le cahier des charges (scénarios + exigences + plan 6S avec affectation des tâches) |
| S2 | 27 mai – 2 juin | Finaliser les DDL du mannequin + revue de l'état de l'art |
| S3 | 3–9 juin | Développer la structure cinématique + intégration RoboDK |
| S4 | 10–16 juin | Simuler les articulations + valider les scénarios |
| S5 | 17–23 juin | Implémenter zones de sécurité, arrêts et ralentissements |
| S6 | 24–30 juin | Ajustements finaux + préparation support soutenance |

Les objectifs intermédiaires sont **séquentiels** (chaque étape dépend de la précédente), mais au sein de chaque étape, les sous-tâches peuvent être réalisées **en parallèle** par les 3 membres.

---

## 4. Cahier des charges (livrable S1)

Document unique et complet attendu pour la prochaine réunion. Il doit inclure :

- **Scénarios** : coexistence et synchronisation, décrits avec leurs exigences fonctionnelles
- **Périmètre** : contraintes matérielles, logicielles, humaines
- **Références normes** : ISO 10218-1 (robots collaboratifs — fabricants) et ISO 10218-2 (intégrateurs)
- **Plan 6 semaines** avec **affectation explicite des tâches** par membre (Niko / Luc / Alex)
- **Diagramme de Gantt** montrant le travail en parallèle au sein de chaque étape

> Ciampi : *"On doit voir que vous avez travaillé en parallèle, pas séquentiellement."*

---

## 5. Revue de l'état de l'art (livrable S2)

Pas un état de l'art exhaustif (ce qui prendrait 3-4 mois selon Diallo). L'objectif est une **base argumentée** :

- Résumer les articles clés trouvés (modèles URDF, cinématique, HRC)
- Pour chaque article : expliquer ce qu'il fait, pourquoi il est pertinent (ou non) pour notre cas
- Raconter une **histoire cohérente** qui justifie nos choix techniques

---

## 6. Rapport final — structure attendue

1. Introduction + contexte + objectifs
2. État de l'art (résumé argumenté)
3. **Formulation cinématique mathématique formelle** — les équations qui sous-tendent le modèle
4. Développement (structure cinématique, intégration RoboDK, scénarios)
5. Résultats et validation
6. **Perspectives futures** (obligatoire) :
   - Études anthropométriques (variabilité homme/femme, morphologies)
   - Intégration caméra (ex. Kinect/RealSense) pour synchronisation espace réel ↔ simulation
   - Extension à d'autres modes H-R (coopération, collaboration)

> Ciampi : *"Un bon rapport, c'est une bonne histoire. Début : objectifs et contraintes. Milieu : développement. Fin : ce qu'on ferait si on avait plus de temps."*

---

## 7. Ressources partagées par Ciampi

- **ISO 10218-1 & -2** : accessibles via l'Extranet ISAE-Supméca → Ressources Numériques → Cobad (version HTML + PDF, pas téléchargeable)
- **Article HRC avec robot KUKA + caméra Kinect** : partagé sur le canal Teams du projet — à intégrer dans l'état de l'art
- **Article de review HRC** : partagé sur Teams

---

## 8. Prochaines étapes

| # | Tâche | Responsable | Échéance |
|---|---|---|---|
| 1 | Finaliser le cahier des charges (scénarios + exigences + Gantt + affectation) | Équipe | S1 — avant prochaine réunion |
| 2 | Compléter la revue de l'état de l'art (résumés argumentés) | Équipe | S2 |
| 3 | Formulation mathématique de la cinématique du mannequin | Équipe | S2–S3 |
| 4 | Tester l'import RoboDK (STEP `Manikin_1.STEP` + URDF `Niko_v1.urdf`) | Niko | S1–S2 |
| 5 | Collecter données robot ALIX (TS, masse, vitesse TCP, ZR) | Équipe | S2 |
| 6 | Consulter les articles partagés par Ciampi sur Teams | Équipe | S1 |

---

*Prochain RDV : à confirmer — objectif : valider le cahier des charges finalisé.*
