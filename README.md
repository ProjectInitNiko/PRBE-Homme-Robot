# PRBE Homme-Robot 2026

Simulation du mouvement humain et interaction Homme-Robot dans **RoboDK**, dans le cadre du module **PRBE 2026** de l'ISAE-SUPMECA (sujet #47, plateforme [ALIX](https://alix.isae-supmeca.fr/)).

## Équipe

- **Niko Khachidze** ([@ProjectInitNiko](https://github.com/ProjectInitNiko))
- **Luc**
- **Alex**

**Encadrants :** Francesco Ciampi, Thierno Diallo
**Période :** mi-avril → fin juin 2026 (100 h autonomes + 14 h encadrées, soutenance fin juin)

## Verrou technique

Aucun logiciel n'intègre proprement le mouvement d'un opérateur humain dans une simulation robotique de type RoboDK. Notre objectif : construire ce pont.

## Approche

1. **Mannequin humain anthropomorphique** scalable au format URDF, généré via [HMG (Human Model Generator)](https://github.com/gbionics/human-model-generator) — IIT, BSD-3-Clause.
2. **Import dans RoboDK** comme chaîne cinématique pilotable.
3. **Animation du mouvement** : trois approches en évaluation
	- analytique (trajectoires articulaires écrites à la main)
	- IA (mapping depuis bases de données mocap)
	- **cinématique inverse** (approche privilégiée — RoboDK natif, ou `ikpy` / `pinocchio`)

## Stack

- **Python 3.11**
- **conda / Miniconda** pour l'environnement (deps natives lourdes)
- **HMG** : `numpy` + `urchin` + `idyntree` + `urdf-modifiers`
- **RoboDK** + son API Python

## Décisions v1

- **Périmètre démo v1** : bras droit seulement (7 DDL), épine figée
- **Base flottante** (pelvis) : décision après test import RoboDK
- Voir [`docs/decisions-v1.md`](docs/decisions-v1.md) pour la justification

## Démarrage rapide

Voir [INSTALL.md](INSTALL.md) pour le setup complet (Miniconda, env conda, clone HMG).

Une fois installé :

```bash
# 1. Générer un mannequin
cd external/human-model-generator/code
conda run -n hmgenv --no-capture-output python main.py
# (entrer un nom quand demandé, ex : Niko_v1)

# 2. Visualiser
cd ../../../scripts
view_urdf_drop.bat   # drag & drop d'un .urdf dessus
```

Ou pour visualiser l'exemple fourni :

```bash
scripts/view_Niko_v1.bat
```

## Structure du repo

```
.
├── README.md                ← ce fichier
├── INSTALL.md               ← setup complet (Miniconda, env, HMG)
├── USAGE.md                 ← générer mannequin + visualiser + flux
├── environment.yml          ← spécification env conda
├── LICENSE                  ← MIT (notre code)
├── docs/
│   ├── architecture-hmg.md  ← pipeline HMG + 54 DDL + scaling π / De Leva
│   └── decisions-v1.md      ← décisions techniques (bras droit, épine figée)
├── scripts/
│   ├── view_urdf.py         ← viewer iDynTree générique
│   ├── view_Niko_v1.bat     ← raccourci sur l'exemple
│   └── view_urdf_drop.bat   ← drag & drop d'un .urdf
├── examples/
│   └── Niko_v1.urdf         ← mannequin H=1.665 m, m=59 kg (chemins meshes relatifs)
└── external/                ← (gitignored) emplacement pour cloner HMG
    └── human-model-generator/
```

## Crédits & licences

- Notre code : MIT (voir [LICENSE](LICENSE))
- **HMG** : BSD-3-Clause, © Fondazione Istituto Italiano di Tecnologia. Citation : Fiori, Latella, Tatarelli, Pucci, *« An automatic anthropometric model generation tool for scalable human whole-body musculoskeletal modeling »*, SIAMOC 2024.
- Meshes HMG : CC-BY (skin, [Blendswap #11604](https://blendswap.com/blend/11604)) et CC-BY-SA (muscles, [Blendswap #26915](https://blendswap.com/blend/26915) + [BodyParts3D](https://lifesciencedb.jp/bp3d/)).
