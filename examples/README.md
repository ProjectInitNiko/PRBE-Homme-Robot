# Mannequins d'exemple

## `Niko_v1.urdf`

Premier mannequin généré (2026-05-10).

| Paramètre | Valeur |
|---|---|
| Taille `H` | 1.665 m |
| Masse `m` | 59 kg |
| Sortie observée | masse 59.0 kg, taille 1.67 m |
| Validation iDynTree | matrice de masse définie positive sur 100 mouvements aléatoires ✓ |
| Taille fichier | 86 KB |
| Nombre de links | 27 + liens intermédiaires `_f1` |
| DDL articulaires | 54 |

## Notes

Les chemins meshes sont **relatifs** (`../external/human-model-generator/code/models/humanModelTemplate/meshes/...`). Pour que la viz fonctionne, tu dois avoir cloné HMG dans `external/` à la racine du repo (voir [INSTALL.md](../INSTALL.md)).

## Regénérer ou créer un nouveau mannequin

```powershell
cd ../external/human-model-generator/code
# (édite config.py pour ajuster H, m, mesures)
conda activate hmgenv
python main.py
# ... entrer un nom (ex : Luc_v1)

# Convertir les chemins en relatifs et placer dans examples/
cd ../../../..
python scripts/fix_urdf_paths.py "external/human-model-generator/code/models/humanModels/Luc_v1.urdf" "examples/Luc_v1.urdf"
```
