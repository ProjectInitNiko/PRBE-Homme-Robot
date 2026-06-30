# Décisions v1

Choix techniques pris pour la première démo PRBE.

## Périmètre v1 : bras droit seulement, épine figée

**Décision :** la première démo pilote uniquement le **bras droit** (7 DDL), avec l'épine **figée** (joints `revolute` de l'épine convertis en `fixed`).

**Justification :**
- 7 DDL bras = suffisants pour un IK vers une cible 6-DDL (la main atteint un point dans l'espace avec orientation libre).
- L'épine (9 DDL) alourdit l'IK, n'apporte rien à un scénario d'interaction main-cible, et démultiplie les configurations dégénérées.
- Une fois la chaîne `pelvis → T8 → claviculeD → bras D → main D` validée en RoboDK, on rouvrira l'épine si le scénario PRBE l'exige.

**Joints à figer (épine) :**
- `jL5S1_rotx`, `jL5S1_roty`
- `jL4L3_rotx`, `jL4L3_roty`
- `jL1T12_rotx`, `jL1T12_roty`
- `jT9T8_rotx`, `jT9T8_roty`, `jT9T8_rotz`

À automatiser dans un futur `scripts/freeze_spine.py`.

## Base flottante (pelvis) : décision après test RoboDK

**Décision reportée.** On importe d'abord `examples/Niko_v1.urdf` tel quel dans RoboDK et on observe.

**Options possibles :**
- **Ancrer le pelvis au monde** : mannequin fixe (debout), simple, suffit pour interaction H-R en station debout statique. Privilégié si l'observation RoboDK montre que la base flottante pose problème.
- **Garder la base flottante** : simulation dynamique complète (équilibre, marche). Beaucoup plus dur. Probablement hors scope PRBE.

## Choix de solver IK : à arbitrer

Trois pistes, en attente du test RoboDK :
- **Solver IK natif RoboDK** — si la chaîne s'importe proprement, c'est le plus simple.
- **`ikpy`** — solver Python pur, lit directement l'URDF, intégrable hors RoboDK pour debug.
- **`pinocchio`** — bibliothèque biomécanique de référence (CNRS LAAS), plus rapide mais install lourd.

Décision après le test d'import.

## Approche d'animation : cinématique inverse privilégiée

Trois approches étaient possibles pour le PRBE :

| Approche | Avec HMG | Verdict |
|---|---|---|
| **Analytique** (trajectoires écrites à la main) | HMG fournit le squelette ; on écrit `q(t)` | Possible mais peu réaliste, pas extensible |
| **IA (database mocap)** | HMG fournit la cinématique cible ; on mappe AMASS / Human3.6M | Riche mais lourd à mettre en place, hors scope 100h |
| **Cinématique inverse** | Solver IK pilote les joints HMG vers une cible | ✅ Choisi. Naturel, extensible, démontrable |
