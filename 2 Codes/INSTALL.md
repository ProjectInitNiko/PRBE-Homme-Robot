# Installation

Setup complet pour pouvoir générer et visualiser un mannequin URDF.

Testé sur **Windows 10 / PowerShell**. Les étapes sont équivalentes sur Linux/macOS, seuls les chemins changent.

## 1. Miniconda

Si conda n'est pas déjà installé :

1. Télécharger : <https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe>
2. Lancer l'installeur. Options recommandées :
	- **Just Me** (install pour ton compte utilisateur uniquement)
	- **Add Miniconda to my PATH** : ✅ (sinon il faudra utiliser "Anaconda Prompt" pour toutes les commandes ci-dessous)
	- Register as default Python : ❌ (évite les conflits si tu installes un autre Python plus tard)

Vérifier dans un terminal **fraîchement ouvert** :

```powershell
conda --version
```

## 2. Fix SSL (machines avec antivirus / proxy d'entreprise)

Sur certaines machines, conda plante en `CERTIFICATE_VERIFY_FAILED`. C'est l'antivirus ou un proxy local qui intercepte HTTPS. Solution propre (utilise le store CA système) :

```powershell
conda config --set ssl_verify truststore
```

À faire **une seule fois** par machine.

## 3. Cloner ce repo + HMG

```powershell
# Repo principal
git clone https://github.com/ProjectInitNiko/PRBE-Homme-Robot.git
cd PRBE-Homme-Robot

# Dépendance externe (HMG, BSD-3) — clone dans external/
mkdir external
cd external
git clone https://github.com/gbionics/human-model-generator.git
cd ..
```

**Pourquoi pas un submodule git ?** Plus simple à comprendre / à dépanner pour l'équipe. On documente, on clone à la main.

## 4. Créer l'environnement conda

```powershell
conda env create -f environment.yml
```

Ça crée un env nommé `hmgenv` avec Python 3.11 + numpy + idyntree + urchin + urdf-modifiers. **Compte 3-5 min** (téléchargement + résolution de deps).

Vérifier :

```powershell
conda run -n hmgenv python -c "import idyntree.bindings; import urchin; import urdfModifiers; print('OK')"
```

> ⚠️ **Piège Windows** : `idyntree` ne s'importe **pas** via le `python.exe` direct (DLL load failed). Toujours passer par `conda run -n hmgenv python ...` ou activer l'env (`conda activate hmgenv`) avant.

## 5. Désactiver la viz iDynTree dans HMG (optionnel)

Par défaut, `main.py` de HMG ouvre une fenêtre iDynTree à la fin du pipeline, qui bloque le shell. Pour le couper :

Édite `external/human-model-generator/code/config.py` :

```python
OPT_VISUALIZZATION_MODEL = False
```

(notre objectif est RoboDK, donc on n'a pas besoin de la viz iDynTree à chaque génération)

## 6. Test rapide

Visualiser le mannequin d'exemple fourni dans le repo :

```powershell
scripts\view_Niko_v1.bat
```

→ une fenêtre 3D doit s'ouvrir avec le mannequin en T-pose. Ferme la fenêtre pour quitter.

## Pièges connus

| Problème | Cause | Solution |
|---|---|---|
| `CondaSSLError` au `conda create` | antivirus / proxy intercepte HTTPS | `conda config --set ssl_verify truststore` |
| `DLL load failed` à `import idyntree` | `python.exe` direct ne setup pas le PATH des DLLs natives | utiliser `conda run -n hmgenv python ...` |
| Fichier `﻿Niko_v1.urdf` invisible (BOM en tête de nom) | input piped en PowerShell injecte un U+FEFF | ne pas piper le nom, taper au clavier après activation de l'env |
| Meshes pas affichés dans le viewer | chemins meshes absolus dans le `.urdf` | utiliser `examples/Niko_v1.urdf` (chemins relatifs) ou regénérer après avoir cloné HMG dans `external/` |

## Étapes suivantes

Voir [USAGE.md](USAGE.md) pour générer ton propre mannequin, post-traiter les chemins, et lancer la suite.
