# Rapport PRBE — projet LaTeX

Rapport du projet *Simulation du mouvement humain et interaction homme-robot dans
RoboDK* (sujet #47, ligne ALIX, ISAE-SUPMÉCA). Gabarit repris du template école.

## Structure

Le rapport est un **fichier unique** : tout le contenu (préambule, page de garde,
les 7 sections, annexe, bibliographie) est dans `main.tex`.

```
rapport/
├── main.tex              # rapport complet (préambule + page de garde + sections 1–7 + annexe)
├── references.bib        # bibliographie
├── Page_Garde/           # fond ISAE (watermark) + logo
├── Images/               # logos
└── figures/              # captures RoboDK + schémas cinématiques
```

## Compiler

### Tectonic (le plus simple en local, un seul binaire)
```
tectonic -X compile main.tex
```
Gère automatiquement bibtex et les passes multiples ; télécharge les paquets au
premier run.

### Overleaf
Compresser le dossier `rapport/` en `.zip`, *New Project → Upload Project*,
fichier principal `main.tex`, compilateur **pdfLaTeX**.

### MiKTeX / TeX Live
```
pdflatex main
bibtex main
pdflatex main
pdflatex main
```
(2 passes après bibtex pour résoudre la table des matières et les `\cref`.)

## Répartition

- **Niko** : sections 4 (modèle conceptuel — partie RoboDK), 5, 6, 7.
- **Alex / Luc** : contexte, cahier des charges, état de l'art, cinématique formelle.

## À finaliser

- Remplacer les figures `bras_seq*` par de vraies captures de `Tache_Bras.py` (table + cube).
- Raccorder les sections 1–3 (placeholders) avec les contenus d'Alex & Luc.
- Vérifier les amplitudes du tableau des 22 DDL et compléter les DOI dans `references.bib`.
