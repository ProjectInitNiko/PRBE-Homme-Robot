# Cahier des charges - PRBE Homme-Robot

**Projet :** Simulation du mouvement humain et interaction homme-robot dans RoboDK  
**Contexte :** PRBE 2026 - ISAE-SUPMECA - Ligne ALIX  
**Equipe :** Niko Khachidze, Luc Fantasia, Alexandre Nowak  
**Encadrants :** Francesco Ciampi, Thierno Diallo  
**Periode :** avril 2026 - juin 2026  
**Version :** v0.1 - document de travail

## 1. Contexte et objectif du projet

Le projet porte sur la simulation d'interactions entre un operateur humain et un robot mobile/manipulateur dans l'environnement RoboDK, en s'appuyant sur la ligne ALIX de l'ISAE-SUPMECA.

L'objectif principal est de representer un humain mobile ou articulable dans RoboDK, puis de simuler des scenarios d'interaction homme-robot permettant d'evaluer les conditions de securite et d'organisation du travail.

Le verrou technique principal est l'integration d'un modele humain exploitable dans un environnement de simulation robotique. RoboDK permet de simuler des robots industriels, mais ne propose pas directement de modele humain cinematique adapte au pilotage articulaire. Le projet vise donc a construire un pont entre un mannequin humain au format URDF et une simulation RoboDK.

## 2. Perimetre du projet

### 2.1 Perimetre fonctionnel

Le projet se concentre sur deux scenarios valides en reunion :

- **Scenario 1 - Coexistence :** l'humain et le robot partagent un meme environnement, mais ne travaillent pas sur une meme tache.
- **Scenario 2 - Synchronisation :** le robot et l'humain interviennent dans un meme processus de production, avec une coordination temporelle indirecte.

Les modes de cooperation et de collaboration directe ne font pas partie du perimetre principal de la demonstration finale. Ils peuvent etre mentionnes comme perspectives.

### 2.2 Perimetre technique

Le projet utilise :

- **RoboDK** pour la simulation robotique.
- **Python** pour l'automatisation et le pilotage.
- **URDF** pour la description du mannequin humain.
- **Human Model Generator (HMG)** pour generer un mannequin anthropometrique.
- Les donnees disponibles de la plateforme **ALIX** et du robot **Myrmidon 100**.

Le mannequin humain sera d'abord simplifie pour garantir une integration realiste dans RoboDK. La premiere version technique se concentre sur une chaine cinematique reduite, avec priorite au bras droit et a la validation de l'import URDF.

### 2.3 Hors perimetre

Les elements suivants ne sont pas vises dans la version principale du projet :

- Contact physique direct entre l'humain et le robot.
- Simulation biomecanique complete du corps humain.
- Capture de mouvement en temps reel par camera.
- Controle dynamique complet de l'equilibre humain.
- Validation normative industrielle complete prealable a une mise en production.

Ces points pourront etre presentes comme limites ou perspectives.

## 3. Scenarios retenus

### 3.1 Scenario 1 - Coexistence

#### Description

Dans ce scenario, l'humain et le robot evoluent dans un meme environnement de travail, mais n'ont pas d'interaction directe ou indirecte sur une piece commune. Le robot suit sa trajectoire, tandis que l'operateur peut etre present dans l'espace.

L'objectif est d'assurer que le robot adapte son comportement en fonction de la presence humaine afin d'eviter tout contact.

#### Regles de fonctionnement

- Si un humain est detecte a moins de **1 m**, le robot ralentit.
- Si un humain est detecte a moins de **0,5 m**, le robot s'arrete completement.
- Si un humain bloque un passage de porte pendant **30 secondes**, le robot recule pour lui laisser le passage.
- Si l'humain se deplace et libere la zone, le robot reprend son trajet.
- En espace ouvert, le robot s'arrete et attend que l'humain sorte de la zone critique.

#### Exigences fonctionnelles

| ID | Exigence | Priorite |
|---|---|---|
| COEX-F1 | Detecter la presence d'un humain dans la zone de deplacement du robot | Haute |
| COEX-F2 | Ralentir le robot lorsque la distance humain-robot devient inferieure a 1 m | Haute |
| COEX-F3 | Arreter le robot lorsque la distance humain-robot devient inferieure a 0,5 m | Haute |
| COEX-F4 | Gerer le cas d'un humain immobile devant une porte pendant 30 s | Moyenne |
| COEX-F5 | Reprendre automatiquement le trajet lorsque la zone redevient libre | Moyenne |

#### Criteres de validation

- La simulation montre visuellement les zones de ralentissement et d'arret.
- Le comportement du robot change lorsque l'humain entre dans les zones critiques.
- Le cas de blocage d'une porte est modelise par une logique temporelle simple.

### 3.2 Scenario 2 - Synchronisation

#### Description

Dans ce scenario, le robot et l'operateur participent a un meme processus industriel, mais sans contact direct. Le robot livre des lots de pieces a l'operateur, l'operateur assemble les pieces, puis le robot recupere les pieces assemblees ou retourne vers la zone de stock.

L'objectif est de reduire les temps d'inactivite de l'operateur en coordonnant le rythme du robot avec le rythme de travail humain.

#### Workflow retenu

1. Le robot preleve un lot de pieces au stock.
2. Le robot transporte le lot vers la zone de travail de l'operateur.
3. Le robot depose le lot si la zone est disponible.
4. L'operateur assemble les pieces.
5. Le robot recupere les pieces assemblees ou repart chercher un nouveau lot.
6. Les regles de securite du scenario de coexistence restent actives.

#### Regles de fonctionnement

- Le robot ne doit pas deposer un lot si la zone de travail est saturee.
- La zone de travail doit contenir au maximum **2 lots simultanement** : un lot en assemblage et un lot en attente.
- Un detecteur d'etat doit indiquer si la zone de depot est libre ou occupee.
- Si un humain entre dans la zone critique du robot, les regles de ralentissement et d'arret s'appliquent.
- Le robot doit attendre dans une position non genante si la zone de depot n'est pas disponible.

#### Exigences fonctionnelles

| ID | Exigence | Priorite |
|---|---|---|
| SYNC-F1 | Representer une zone de stock, une zone de depot et une zone de travail operateur | Haute |
| SYNC-F2 | Modeliser l'etat de la zone de depot : libre, occupee, saturee | Haute |
| SYNC-F3 | Limiter le nombre de lots simultanes dans la zone operateur | Haute |
| SYNC-F4 | Faire attendre le robot si la zone de depot est saturee | Haute |
| SYNC-F5 | Appliquer les regles de securite de coexistence pendant la livraison | Haute |
| SYNC-F6 | Montrer une coordination temporelle entre travail humain et trajet robot | Moyenne |

#### Criteres de validation

- La simulation montre un cycle complet stock -> operateur -> retour.
- Le robot ne depose pas de lot lorsque la zone est saturee.
- La securite reste prioritaire sur la synchronisation.
- Le scenario illustre une activite simultanee et coordonnee, et pas seulement une sequence independante de taches.

## 4. Modele humain

### 4.1 Objectif du modele humain

Le modele humain doit permettre de representer un operateur dans RoboDK avec un niveau de detail suffisant pour visualiser les interactions et les distances de securite.

Le projet ne vise pas une simulation biomecanique exhaustive. Le modele doit rester simple, pilotable et exploitable dans le temps disponible.

### 4.2 Choix de modelisation

Le mannequin est genere a partir de HMG sous forme d'un fichier URDF. La premiere version disponible est `examples/Niko_v1.urdf`.

Pour la demonstration technique, les choix actuels sont :

- Utiliser un mannequin anthropometrique scalable.
- Figer l'epine pour reduire le nombre de degres de liberte.
- Valider d'abord l'import RoboDK avant d'etendre le modele.
- Piloter prioritairement le bras droit pour les gestes de manipulation.

### 4.3 Degres de liberte utiles

Pour les scenarios retenus :

- Les jambes sont utiles pour representer le deplacement ou la posture de l'operateur.
- Les bras sont utiles pour le scenario de synchronisation, lorsque l'operateur assemble ou recupere des pieces.
- La tete, les doigts et les mouvements internes fins du buste ne sont pas prioritaires.

La version v1 du demonstrateur privilegie une cinematique simplifiee et robuste plutot qu'un corps humain completement articule.

## 5. Securite et references normatives

Le projet s'appuie sur les references suivantes :

- **ISO 10218-1** : exigences de securite pour les robots industriels, cote fabricant.
- **ISO 10218-2** : exigences de securite pour les applications robotisees et l'integration en cellule.
- **ISO/TS 15066** : specifications relatives aux operations collaboratives homme-robot.

Pour les scenarios retenus, le principe principal est la **surveillance de vitesse et de separation**. Le robot doit adapter sa vitesse ou s'arreter selon la distance a l'operateur.

Les distances retenues pour la simulation sont :

| Zone | Distance | Comportement robot |
|---|---:|---|
| Zone normale | > 1 m | Trajet nominal |
| Zone de ralentissement | <= 1 m | Vitesse reduite |
| Zone d'arret | <= 0,5 m | Arret complet |

Ces distances sont les valeurs validees pour le scenario de projet. Elles devront etre justifiees dans le rapport par rapport aux normes et aux contraintes reelles de la plateforme ALIX.

## 6. Exigences non fonctionnelles et contraintes

### 6.1 Exigences de simulation

| ID | Exigence | Priorite |
|---|---|---|
| SIM-NF1 | La simulation doit etre comprehensible visuellement par un observateur externe | Haute |
| SIM-NF2 | Les zones de securite doivent etre identifiables dans RoboDK | Haute |
| SIM-NF3 | Les comportements du robot doivent etre reproductibles d'une execution a l'autre | Haute |
| SIM-NF4 | Les scripts doivent pouvoir etre relances et modifies par les membres de l'equipe | Moyenne |
| SIM-NF5 | Les hypotheses utilisees doivent etre explicites dans le rapport | Haute |

### 6.2 Contraintes materielles

- Le projet s'appuie sur la plateforme ALIX et le robot Myrmidon 100.
- Les detecteurs de presence existants sont privilegies ; l'ajout de materiel n'est pas l'objectif principal.
- Les donnees exactes du robot et des capteurs doivent etre collectees ou estimees de maniere justifiee.

### 6.3 Contraintes logicielles

- RoboDK est l'environnement de simulation cible.
- Les scripts de generation, post-traitement et pilotage sont developpes en Python.
- Le format URDF est utilise pour decrire le mannequin humain.
- Les dependances externes doivent rester documentees et installables par l'equipe.

### 6.4 Contraintes humaines et planning

- Le projet est mene sur une periode courte, jusqu'a la soutenance de fin juin.
- Les taches doivent etre reparties pour permettre un travail en parallele.
- Les choix techniques doivent rester compatibles avec le temps disponible et les competences de l'equipe.

## 7. Donnees a collecter

Pour rendre la simulation plus realiste, les donnees suivantes doivent etre recuperees ou estimees :

| Donnee | Utilite | Responsable propose |
|---|---|---|
| Dimensions de la zone ALIX | Placement des zones dans RoboDK | Equipe |
| Caracteristiques du Myrmidon 100 | Vitesse, encombrement, trajectoires | Equipe |
| Vitesse TCP du robot | Calcul et parametrage securite | Equipe |
| Temps d'arret du robot | Validation distance d'arret | Equipe |
| Type et portee des capteurs de presence | Detection humain | Equipe |
| Position des portes et passages | Scenario coexistence | Equipe |
| Capacite de la zone de depot | Scenario synchronisation | Equipe |

## 8. Livrables attendus

### Livrables intermediaires

- Cahier des charges valide.
- Etat de l'art argumente.
- Formulation cinematique du mannequin.
- Import du mannequin humain dans RoboDK.
- Demonstrateur simple du scenario de coexistence.
- Demonstrateur simple du scenario de synchronisation.

### Livrables finaux

- Simulation RoboDK des scenarios retenus.
- Scripts Python associes.
- Rapport final.
- Support de soutenance.

## 9. Planning previsionnel

| Semaine | Dates | Objectif principal |
|---|---|---|
| S1 | 20-26 mai | Finaliser le cahier des charges, les scenarios, les exigences et le Gantt |
| S2 | 27 mai-2 juin | Finaliser les DDL du mannequin et completer l'etat de l'art |
| S3 | 3-9 juin | Developper la structure cinematique et tester l'integration RoboDK |
| S4 | 10-16 juin | Simuler les articulations et valider les scenarios |
| S5 | 17-23 juin | Implementer les zones de securite, ralentissements et arrets |
| S6 | 24-30 juin | Finaliser, corriger et preparer la soutenance |

## 10. Repartition provisoire des taches

La repartition doit montrer que les travaux sont menes en parallele par les trois membres de l'equipe.

| Membre | Responsabilites principales |
|---|---|
| Niko | Import RoboDK, tests URDF, validation technique du mannequin |
| Luc | Normes de securite, exigences liees aux scenarios, donnees ALIX |
| Alex | Structuration du cahier des charges, planning, Gantt, integration documentaire |

Cette repartition est provisoire et pourra etre ajustee selon les disponibilites et les resultats des premiers tests.

## 11. Risques identifies

| Risque | Impact | Mesure de reduction |
|---|---|---|
| Import URDF incomplet dans RoboDK | Bloque la simulation du mannequin | Tester rapidement `Niko_v1.urdf`, puis simplifier le modele si necessaire |
| Trop grand nombre de DDL | IK instable ou difficile a piloter | Figer l'epine et commencer par une chaine reduite |
| Donnees ALIX incompletes | Distances et vitesses approximatives | Utiliser des hypotheses explicites puis les remplacer par les valeurs reelles |
| Planning court | Demonstrateur incomplet | Prioriser coexistence + synchronisation simple |
| Normes difficiles a exploiter | Justification securite fragile | Se limiter aux exigences directement utiles au projet |

## 12. Criteres de reussite du projet

Le projet sera considere reussi si :

- Un mannequin humain est integre ou represente de maniere exploitable dans RoboDK.
- Les deux scenarios retenus sont clairement formalises.
- La simulation montre des comportements de securite coherents : ralentissement, arret, attente.
- Le scenario de synchronisation illustre une coordination temporelle entre robot et operateur.
- Les choix techniques sont justifies par l'etat de l'art, les contraintes RoboDK et les normes de securite.
