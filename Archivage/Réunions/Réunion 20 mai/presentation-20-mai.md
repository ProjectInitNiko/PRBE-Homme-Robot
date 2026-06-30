# Présentation 20 mai

_Source : `Présentation 20 mai.pptx`_

## Diapositive 1

### Simulation du mouvement humain et interaction homme-robot dans RoboDK

- Nikoloz Khachidze, Alexandre nowak, Luc Fantasia
- Avril 2026 - Juin 2026

## Diapositive 2

### Scénarios d’interaction

- Scénario 1 : Coexistance
- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 3

### Scénario 1 : Coexistence

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- La coexistence :
- Présence du robot et de l'humain dans une même zone de travail.
- Cependant les deux entités n'ont aucune interaction que cela soit de manière directe ou indirecte.
- Besoin :
- L'humain est le robot ne doivent pas rentrer en contact. Pour cela des détecteurs de présence qui seront positionner sur le robot devront être présent de chaque côté du robot.

## Diapositive 4

### Scénario 1 : Coexistence

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- Règles :
- Ralentissements à 1 m, puis arrêt a 50 cm. (A vérifier dans les ISO)
- Si passage d'une porte & présence d'un humain.
- Alors arrêt du robot. (Fonctionnement normal)
- Si l'humain bouge est n'est plus devant le robot.
- Alors le robot reprend son trajet.
- Si l'humain ne bouge pas (toujours présent) au bout de 30 secs.
- Alors le robot recule pour laisser passer l'humain, puis reprend son trajet.
- Si juste présence humaine.
- Alors arrêt jusqu’à ce que l'humain bouge.

## Diapositive 5

### Scénario 1 : Coexistence

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- DDL de l'humain :
- Nous avons besoin de seulement des membres inférieurs pour mouvoir notre humain.
- Il n'y a pas d'utilité a simuler les mouvements des membres supérieures de la tête et du torse car l'humain ne doit pas interagir avec des éléments.
- Au total il y aura 10 degrés de liberté pour les membres inférieures.
- Modélisation d'un membre :
- Buste -> (3 degrés) -> Partie supérieure -> (1 degrés) -> Partie inférieure -> (1 degrés) -> Pied

## Diapositive 6

### Scénarios d’interaction

- Scénario 2 : Synchronisation
- | ISAE-Supméca – Institut supérieur de mécanique de Paris |

## Diapositive 7

### Scénario 2 : Synchronisation

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- La synchronisation:
- Présence du robot et de l'humain dans une même zone de travail.
- De plus les deux entités ont une interaction indirecte mais en aucun cas direct.
- Besoin :
- Dans ce cas nous considérons que le robot est l'humain travaillent tous les deux sur la même ligne de production. Ici le robot va prendre des pièces dans un stock et va les poser sur une plateforme en attendant que l'humain les récupères.
- On considère que l'humain assemble les pièces apporter par le robot.
- Le robot va avoir besoin d'un détecteur de pièce.

## Diapositive 8

### Scénario 2 : Synchronisation

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- Règles :
- Pour ce qui est de l'arrêt du robot du a la proximité d'un humain les règles de changent pas depuis le scénario 1.
- Le robot apporte des sets de pièces entiers.
- S'il n'y a pas assez de pièces il ne les apporte pas à l'opérateur.
- Il ne peut poser seulement que deux sets de pièces sur la plateforme de l'humain (2 en attente et 1 en assemblage est une configuration possible).
- Dans le cas ou il y a deux sets de pièces sur la plateforme de l'opérateur le robot attend avant des les poser dans une position qui ne gêne pas l'utilisateur.

## Diapositive 9

### Scénario 2 : Synchronisation

- | ISAE-Supméca – Institut supérieur de mécanique de Paris |
- DDL de l'humain :
- Pour les membres inférieures même configuration que le scénarios 1 (10 DDL).
- Buste -> (3 degrés) -> Partie supérieure -> (1 degrés) -> Partie inférieure -> (1 degrés) -> Pied
- Nous considérons ici que les DDL de la tête, cou et celles internes au buste ne sont pas utiles.
- Les bras seront les seuls membres avec des DDL.
- Buste -> (3 degrés) -> Bras-> (1 degrés) -> Avant-bras -> (2 degrés) -> Main

## Diapositive 10

### ISAE-Supméca

- Institut supérieur de mécanique de Paris
- 3 rue Fernand Hainaut 93407 Saint-Ouen Cedex
- Tél. 01 49 45 29 00 – www.isae-supmeca.fr
- Ministère de l'Enseignement supérieuret de la Recherche
