# Usage

Comment générer un mannequin et le visualiser au quotidien.

## Générer un mannequin

1. Ouvrir un terminal dans le dossier HMG :

	```powershell
	cd external\human-model-generator\code
	```

2. (Optionnel) Éditer `config.py` pour ajuster taille `H` et masse `m` :

	```python
	H = 1.78   # taille en mètres
	m = 72.0   # masse en kilos
	```

	Tu peux aussi raffiner les 12 mesures anthropométriques (cou, tronc, bras, jambes — voir `models/README.md` dans HMG).

3. Lancer :

	```powershell
	conda activate hmgenv
	python main.py
	```

	Quand demandé : taper un nom (ex : `Luc_v1`), valider.

	→ le `.urdf` sort dans `external/human-model-generator/code/models/humanModels/`.

## Post-traiter le `.urdf` pour qu'il soit portable

Par défaut, HMG met **des chemins absolus** dans le `.urdf` (`D:\...\meshes\Pelvis.stl`). Si tu envoies le fichier à quelqu'un d'autre, ses meshes ne s'afficheront pas.

Pour rendre les chemins relatifs (depuis `examples/`) :

```powershell
python scripts\fix_urdf_paths.py "external\human-model-generator\code\models\humanModels\Luc_v1.urdf" "examples\Luc_v1.urdf"
```

Le script remplace les chemins absolus par `../external/human-model-generator/code/models/humanModelTemplate/meshes/...`.

## Visualiser

### Méthode 1 — drag & drop

Glisse-dépose un fichier `.urdf` sur `scripts\view_urdf_drop.bat`.

### Méthode 2 — terminal

```powershell
conda run -n hmgenv --no-capture-output python scripts\view_urdf.py examples\Niko_v1.urdf
```

### Contrôles dans le viewer

- **clic gauche + glisser** : rotation
- **clic droit + glisser** : translation
- **molette** : zoom
- **fermer la fenêtre** : quitter

## Flux PRBE typique

```
1. Ajuster H/m dans config.py    →  python main.py    →  Niko_v2.urdf (chemins absolus)
2. fix_urdf_paths.py             →  examples/Niko_v2.urdf (portable)
3. view_urdf.py examples/Niko_v2.urdf  →  vérification visuelle
4. (à venir) freeze_spine.py     →  examples/Niko_v2_armonly.urdf
5. import dans RoboDK            →  pilotage IK depuis l'API Python
```

## Pour la suite (TODO)

- [ ] Script `freeze_spine.py` : passe les revolute épine (jL5S1, jL4L3, jL1T12, jT9T8 + leurs `_rotx/_roty/_rotz`) en `fixed`
- [ ] Premier import dans RoboDK + observations (base flottante, échelle, types de joints)
- [ ] Wrapper Python autour de l'API RoboDK pour piloter le bras droit en IK
