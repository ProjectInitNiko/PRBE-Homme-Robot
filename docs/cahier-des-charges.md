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
- **Python** pour le pilotage.
- **URDF** pour la description du mannequin humain.
- **Human Model Generator (HMG)** pour generer un mannequin anthropometrique.
- Les donnees disponibles de la plateforme **ALIX** et du robot **Myrmidon 100**.

Le mannequin humain sera d'abord simplifie pour garantir une integration realiste dans RoboDK.

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
- Le cas de blocage d'une porte ne doit pas conduire a l'arret de l'humain et du robot sans fin.

### 3.2 Scenario 2 - Synchronisation

#### Description

Dans ce scenario, le robot et l'operateur participent a un meme processus industriel, mais sans contact direct. Le robot depose une piece dans une zone de transfert, puis l'operateur vient recuperer cette piece dans une fenetre de temps donnee.

L'objectif est de montrer une vraie synchronisation temporelle entre le robot et l'operateur : le robot doit liberer la zone avant l'arrivee de l'humain, et l'humain doit recuperer la piece dans le delai prevu sans entrer en conflit avec le mouvement du robot.

#### Workflow retenu

1. Le robot preleve une piece au stock.
2. Le robot transporte la piece vers la zone de transfert.
3. Le robot depose la piece dans la zone de transfert pendant un intervalle autorise.
4. Le robot quitte la zone de transfert ou se place dans une position d'attente non genante.
5. L'operateur recupere la piece dans la fenetre de temps definie.
6. Les regles de securite du scenario de coexistence restent actives pendant toute la sequence.

#### Regles de fonctionnement

- Une seule piece est prise en compte dans la zone de transfert pour chaque cycle.
- La recuperation par l'operateur doit se faire dans une fenetre temporelle definie apres le depot de la piece.
- Le robot et l'operateur ne doivent pas occuper simultanement la zone de transfert.
- Si l'operateur arrive trop tot ou si le robot tarde a quitter la zone, les regles de ralentissement et d'arret s'appliquent.
- Le robot doit attendre dans une position non genante lorsque la fenetre de transfert n'est pas disponible.

#### Exigences fonctionnelles

| ID | Exigence | Priorite |
|---|---|---|
| SYNC-F1 | Representer une zone de stock, une zone de transfert et une zone operateur | Haute |
| SYNC-F2 | Modeliser l'etat de la zone de transfert : libre, occupee par le robot, piece disponible, occupee par l'operateur | Haute |
| SYNC-F3 | Definir une fenetre temporelle de recuperation de la piece par l'operateur | Haute |
| SYNC-F4 | Empecher l'occupation simultanee de la zone de transfert par le robot et l'operateur | Haute |
| SYNC-F5 | Appliquer les regles de securite de coexistence pendant le depot et la recuperation | Haute |
| SYNC-F6 | Montrer une coordination temporelle entre depot robot et recuperation humaine | Moyenne |

#### Criteres de validation

- La simulation montre un cycle complet stock -> zone de transfert -> recuperation operateur.
- L'operateur recupere la piece dans la fenetre temporelle prevue.
- Le robot et l'operateur ne se trouvent pas simultanement dans la zone de transfert.
- La securite reste prioritaire sur la synchronisation.
- Le scenario illustre une activite temporellement coordonnee, et pas seulement une sequence independante de taches.

## 4. Modele humain

### 4.1 Objectif du modele humain

Le modele humain doit permettre de representer un operateur dans RoboDK avec un niveau de detail suffisant pour visualiser les interactions et les distances de securite.

Le projet ne vise pas une simulation biomecanique exhaustive. Le modele doit rester simple, pilotable et exploitable dans le temps disponible.

### 4.2 Choix de modelisation

Le mannequin est genere a partir de HMG sous forme d'un fichier URDF.

Pour la demonstration technique, les choix actuels sont :

- Utiliser un mannequin anthropometrique scalable.
- Figer l'epine pour reduire le nombre de degres de liberte.
- Valider d'abord l'import RoboDK avant d'etendre le modele.

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

## 8. Livrables attendus

### Livrables intermediaires

- Cahier des charges valide.
- Formulation mathematique cinematique du mannequin.
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

## 12. Criteres de reussite du projet

Le projet sera considere reussi si :

- Un mannequin humain est integre ou represente de maniere exploitable dans RoboDK.
- Les deux scenarios retenus sont clairement formalises.
- La simulation montre des comportements de securite coherents : ralentissement, arret, attente.
- Le scenario de synchronisation illustre une coordination temporelle entre robot et operateur.
- Les choix techniques sont justifies par les exigences, les contraintes RoboDK et les normes de securite.
