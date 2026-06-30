# PRBE Homme-Robot 2026

Simulation du mouvement humain et interaction Homme-Robot dans **RoboDK**, dans le cadre du module **PRBE 2026** de l'ISAE-SUPMECA (sujet #47, plateforme [ALIX](https://alix.isae-supmeca.fr/)).

## Équipe

- **Niko Khachidze** ([@ProjectInitNiko](https://github.com/ProjectInitNiko))
- **Luc**
- **Alex**

**Encadrants :** Francesco Ciampi, Thierno Diallo
**Période :** mi-avril → fin juin 2026 (100 h autonomes + 14 h encadrées, soutenance fin juin)

## Verrou technique

Aucun logiciel n'intègre proprement le mouvement d'un opérateur humain dans une simulation robotique de type RoboDK. Notre objectif : construire ce pont — un opérateur anthropomorphique 22 DDL piloté dans RoboDK (marches + tâche de manipulation par cinématique inverse).

## Organisation du dépôt

Le dépôt est structuré par **type de livrable** pour en faciliter la lecture :

| Dossier | Contenu |
| --- | --- |
| **`1 Matériel pédagogique/`** | Documents fournis par l'équipe encadrante : sujet PRBE, bibliographie, template de présentation Supméca |
| **`2 Codes/`** | Codes (versions finales) : scripts RoboDK, modèles URDF, trajectoires, stations `.rdk` finales, fiche d'explication des codes |
| **`3 Documents finaux/`** | Cahier des charges, rapport (PDF + source LaTeX), présentation, poster |
| **`4 Captures d'écran/`** | Captures de résultats de la simulation (opérateur, marches, tâche bras, trajectoires) |
| **`5 Vidéos/`** | Vidéos de la simulation |
| **`Archivage/`** | Comptes-rendus de réunions, documents de travail et éléments intermédiaires hors des catégories ci-dessus |

> `external/` (dépendance HMG) et `Archivage/_local/` (artefacts de labo) ne sont pas versionnés — voir `.gitignore`.

## Approche

1. **Mannequin humain anthropomorphique** scalable au format URDF, généré via [HMG (Human Model Generator)](https://github.com/gbionics/human-model-generator) — IIT, BSD-3-Clause.
2. **Import dans RoboDK** comme chaîne cinématique pilotable (rig à 22 DDL).
3. **Animation du mouvement** : marches (militaire, avant, trajectoire externe) et tâche de manipulation du bras par **cinématique inverse** (DLS).

## Stack

- **Python 3.11** + **conda / Miniconda** (deps natives lourdes)
- **HMG** : `numpy` + `urchin` + `idyntree` + `urdf-modifiers`
- **RoboDK** + son API Python

## Démarrage rapide

Voir [`2 Codes/INSTALL.md`](2%20Codes/INSTALL.md) pour le setup complet (Miniconda, env conda, clone HMG), puis [`2 Codes/USAGE.md`](2%20Codes/USAGE.md).

```bash
# 1. Générer un mannequin (HMG cloné dans external/)
cd external/human-model-generator/code
conda run -n hmgenv --no-capture-output python main.py
# (entrer un nom quand demandé, ex : Niko_v1)

# 2. Visualiser un .urdf
cd "../../../2 Codes/scripts"
view_urdf_drop.bat   # drag & drop d'un .urdf dessus
```

Ou pour visualiser le modèle fourni :

```bash
"2 Codes/scripts/view_Niko_v1.bat"
```

## Crédits & licences

- Notre code : MIT (voir [LICENSE](LICENSE))
- **HMG** : BSD-3-Clause, © Fondazione Istituto Italiano di Tecnologia. Citation : Fiori, Latella, Tatarelli, Pucci, *« An automatic anthropometric model generation tool for scalable human whole-body musculoskeletal modeling »*, SIAMOC 2024.
- Meshes HMG : CC-BY (skin, [Blendswap #11604](https://blendswap.com/blend/11604)) et CC-BY-SA (muscles, [Blendswap #26915](https://blendswap.com/blend/26915) + [BodyParts3D](https://lifesciencedb.jp/bp3d/)).
