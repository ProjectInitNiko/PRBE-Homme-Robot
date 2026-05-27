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
- Les donnees disponibles de la plateforme **ALIX** et du robot **AMR Mir100**.

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

Les degres de liberte retenus correspondent uniquement a des rotations articulaires, sans prise en compte des degres de liberte en deplacement.

| Segment | DDL | Detail |
|---|---:|---|
| Buste -> Cuisse (x2) | 3 par jambe | Mouvements fluides et courbes |
| Cuisse -> Mollet (x2) | 1 par jambe | Flexion genou, type pivot |
| Cheville -> Pied (x2) | 1 par jambe | Pivot cheville |
| **Total jambes** | **10** | |
| Epaule (x2) | 3 par bras | Rotation de l'epaule |
| Coude (x2) | 1 par bras | Flexion du coude |
| Poignet (x2) | 2 par bras | Orientation du poignet |
| **Total bras** | **12** | 6 DDL par bras, donc 12 DDL pour les deux bras |
| **Total retenu** | **22** | Jambes et bras uniquement |

Pour le scenario 1, le mannequin utilise uniquement les membres inferieurs afin de representer les postures et deplacements de l'operateur. Pour le scenario 2, le mannequin utilise les membres inferieurs et superieurs, car l'operateur doit se deplacer puis recuperer une piece dans la zone de transfert.

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

Le projet a debute par la reunion de lancement du **24 avril** et se termine par la soutenance prevue le **24 juin**. Le planning ci-dessous est construit pour etre repris ensuite sous forme de diagramme de Gantt : chaque periode precise les taches a realiser, les livrables attendus et la repartition entre les membres du groupe.

| Periode | Objectif de la periode | Niko | Luc | Alex | Livrable / jalon |
|---|---|---|---|---|---|
| 24 avril | Lancement du projet et cadrage du besoin | Identifier les contraintes techniques du mannequin et de RoboDK | Identifier les contraintes liees a la securite homme-robot | Structurer les notes de lancement et organiser le depot GitHub | Reunion de lancement, objectifs generaux fixes |
| 25 avril-5 mai | Recherche preliminaire et prise en main du sujet | Rechercher des solutions de mannequin humain et de modelisation cinematique | Rechercher les premieres references sur les interactions H-R et les normes | Regrouper les sources, organiser la documentation et preparer une premiere synthese | Base documentaire initiale |
| 6-12 mai | Preparation de la premiere presentation projet | Etudier les possibilites d'import ou de reconstruction du mannequin dans RoboDK | Formaliser les premiers scenarios et les premiers risques de securite | Mettre en forme la presentation du 13 mai et les exigences initiales | Presentation du 13 mai preparee |
| 13 mai | Presentation intermediaire et clarification du perimetre | Presenter les contraintes RoboDK et les pistes de modelisation | Presenter les modes d'interaction et les normes a etudier | Presenter le contexte, les scenarios et les exigences fonctionnelles | Scenarios et exigences discutes avec les encadrants |
| 14-19 mai | Reprise apres remarques de la reunion du 13 mai | Approfondir la solution d'import partie par partie et les besoins en DDL | Approfondir ISO/TS 15066, ISO 10218-1 et ISO 10218-2 | Corriger la structuration des scenarios et preparer le cahier des charges | Version de travail du cahier des charges |
| 20 mai | Validation des scenarios et des choix principaux | Valider l'approche cinematique classique et les DDL utiles | Valider les distances de securite : ralentissement a 1 m, arret a 0,5 m | Integrer les decisions de reunion dans le cahier des charges et le planning | Deux scenarios retenus : coexistence et synchronisation |
| 21-31 mai | Finalisation du cahier des charges et du planning | Finaliser le tableau des DDL et les besoins techniques RoboDK | Finaliser les exigences de securite et les criteres de validation | Finaliser le cahier des charges, le planning et la repartition des taches | Cahier des charges valide |
| 1-7 juin | Etat de l'art et formulation mathematique | Formaliser la cinematique du mannequin et preparer les tests URDF/RoboDK | Relier les normes aux scenarios et aux zones de securite | Integrer l'etat de l'art et la formulation mathematique au rapport | Etat de l'art et formulation cinematique |
| 8-14 juin | Developpement technique et premiers tests de simulation | Generer ou adapter le mannequin URDF, tester l'import et le pilotage dans RoboDK | Verifier les comportements de securite attendus dans les scenarios | Documenter les tests, les choix techniques et les limites rencontrees | Mannequin exploitable et premiers scripts |
| 15-21 juin | Integration et validation des deux scenarios | Implementer ou ajuster les animations dans RoboDK | Valider ralentissement, arret, attente et synchronisation temporelle | Mettre a jour le rapport avec les resultats et captures de simulation | Demonstrateurs coexistence et synchronisation |
| 22-24 juin | Finalisation avant soutenance | Corriger les derniers points techniques et preparer la demonstration | Verifier la coherence securite/normes dans le rapport et la presentation | Finaliser le rapport, le support de soutenance et coordonner la repetition | Rapport final, support et soutenance du 24 juin |

## 10. Repartition provisoire des taches

La repartition des taches est organisee pour montrer que les travaux avancent en parallele jusqu'a la soutenance du 24 juin, comme demande lors de la reunion du 20 mai.

| Membre | Responsabilites principales |
|---|---|
| Niko | Modelisation technique du mannequin, generation ou adaptation URDF, import dans RoboDK, tests des DDL et validation du comportement cinematique. |
| Luc | Analyse des normes de securite, definition des zones de ralentissement et d'arret, formalisation des contraintes liees aux scenarios et aux donnees ALIX. |
| Alex | Structuration du cahier des charges, formalisation des scenarios, planning/Gantt, integration documentaire, rapport et support de soutenance. |

Les trois axes restent lies : les choix de DDL et les tests RoboDK alimentent la formulation mathematique, les contraintes normatives encadrent les scenarios, et la documentation est mise a jour au fur et a mesure des validations en reunion.

## 12. Criteres de reussite du projet

Le projet sera considere reussi si :

- Un mannequin humain est integre ou represente de maniere exploitable dans RoboDK.
- Les deux scenarios retenus sont clairement formalises.
- La simulation montre des comportements de securite coherents : ralentissement, arret, attente.
- Le scenario de synchronisation illustre une coordination temporelle entre robot et operateur.
- Les choix techniques sont justifies par les exigences, les contraintes RoboDK et les normes de securite.
