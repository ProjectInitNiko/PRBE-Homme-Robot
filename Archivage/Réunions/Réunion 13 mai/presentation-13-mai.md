# Présentation 13 mai

_Source : `Présentation 13 mai.pptx`_

## Diapositive 1

### Simulation du mouvement humain et interaction homme-robot dans RoboDK

- Nikoloz Khachidze, Alexandre nowak, Luc Fantasia
- Avril 2026 - Juin 2026

## Diapositive 2

### Contexte du projet

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 3

### Contexte du projet

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- L’évolution des systèmes industriels collaboratifs conduit à une intégration
- croissante des robots au sein d’environnements partagés avec les opérateurs
- humains.
- L’objectif est de développer un modèle humain simplifié capable de :
- de reproduire des mouvements humains cohérents
- d’interagir avec un robot dans un environnement collaboratif
- de permettre l’analyse de scénarios homme-robot
- Cette simulation permettra :
- d’anticiper les interactions homme-robot
- d’évaluer les risques de collision
- d’analyser les contraintes ergonomiques
- de tester différents scénarios avant une implantation réelle

## Diapositive 4

### Scénarios d’interaction

- Scénario 1 : partage d’espace
- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 5

### Scénario 1 : partage d’espace

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- L’opérateur et le robot travaillent ensemble dans la même zone. Le mannequin doit
- pouvoir se déplacer sans risque dans l’environnement pendant que le robot exécute
- une tâche.
- Objectifs :
- visualiser les zones de proximité
- étudier les risques de collision
- Outils :
- déplacement du mannequin
- distance minimale
- arrêt ou ralentissement du robot

## Diapositive 6

### Scénarios d’interaction

- Scénario 2 : transmission d’objet
- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 7

### Scénario 2 : transmission d’objet

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- Le mannequin saisit un objet puis le transmet au robot.
- Objectifs :
- synchronisation des mouvements
- interaction bras/robot
- validation des trajectoires
- Outils :
- mouvement du bras
- positionnement de la main
- trajectoires synchronisées

## Diapositive 8

### Exigences fonctionnelles

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 9

### xigences fonctionnelles

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- EF1 : La simulation d'un mannequin humain articulé doit s'effectuer dans l'environnement de RoboDK pilotée grâce Python.
- EF2 : Le mannequin devra pouvoir réaliser des mouvements simples des membres
- supérieurs et inférieurs.
- EF3 : Le système devra permettre l’animation synchronisée du mannequin et du robot.
- EF4 : Les situations de proximité entre l’humain et le robot doivent être détectées.
- EF5 : Le robot doit s'arrêter ou ralentir lors d'une situation de proximité.
- EF6 : Le robot doit garder une distance minimale de 1 m avec l'humain.
- Exigences fonctionnelles

## Diapositive 10

### Limites

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 11

### Limites

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- Le mannequin devra rester simplifié afin de limiter la complexité cinématique.
- Les mouvements devront rester cohérents visuellement sans viser une reproduction biomécanique complète.
- La simulation devra rester compatible avec RoboDK et son API Python.

## Diapositive 12

### Modèle cinématique et degrés de liberté

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 13

### Modèle cinématique et degrés de liberté

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- Le choix des degrés de liberté (DDL) constitue un compromis entre :
- le réalisme des mouvements,
- la complexité cinématique,
- les performances de calcul,
- et la compatibilité avec l’environnement RoboDK.

## Diapositive 14

### ISAE-Supméca

- Institut supérieur de mécanique de Paris
- 3 rue Fernand Hainaut 93407 Saint-Ouen Cedex
- Tél. 01 49 45 29 00 – www.isae-supmeca.fr
- Ministère de l'Enseignement supérieuret de la Recherche
