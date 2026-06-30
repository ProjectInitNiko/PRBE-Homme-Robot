# Import du mannequin dans RoboDK — procédure & points de vigilance

Étape critique du projet : valider que le mannequin URDF s'importe dans RoboDK et
que ses articulations sont pilotables (manuellement + via l'API Python).

**À faire sur une machine où RoboDK est installé** (poste école / plateforme ALIX) —
RoboDK n'est pas installé sur la machine de dev perso.

## Fichiers à emmener

Le modèle est auto-suffisant si on copie ces deux dossiers ensemble (chemins meshes
relatifs `../external/...`, 67 STL) :

```
PRBE-Homme-Robot/
├── examples/Niko_v2_PRBE.urdf      ← le mannequin 22 DDL
└── external/human-model-generator/ ← les meshes (cloner HMG si absent)
```

Si `external/` est vide : `git clone https://github.com/gbionics/human-model-generator external/human-model-generator`

## Voie 1 — Import manuel (URDF Import add-in)

1. RoboDK > **Outils > Add-ins** > activer **URDF Import** (gratuit, marketplace RoboDK).
2. **Fichier > Ouvrir** > sélectionner `Niko_v2_PRBE.urdf`.
3. Vérifier dans l'arbre station que le mannequin apparaît comme **mécanisme** avec
   ses axes (et non comme objets statiques).
4. Bouger les joints à la main (double-clic sur le mécanisme > panneau des axes).

## Voie 2 — Import + test API (script fourni)

Sur la machine RoboDK, avec le package Python : `pip install robodk`

```
python scripts/robodk_import_test.py
```

Le script importe le fichier, liste les mécanismes chargés, affiche le nombre
d'axes et tente un mouvement à mi-amplitude pour confirmer le pilotage.

## Points de vigilance (à observer pendant le test)

- **Chaîne ramifiée** : RoboDK est pensé pour des robots SÉRIE. Le mannequin est
  un arbre (bassin → 2 bras + 2 jambes). À vérifier en priorité : RoboDK importe-t-il
  l'arbre complet en un seul mécanisme, ou faut-il découper en chaînes série par
  membre (1 chaîne = pelvis→bras D, etc.) ? C'est LE risque technique du sujet
  (cf. Tola & Corke 2023 : pas de support URDF natif RoboDK, on passe par l'add-in).
- **Base flottante** : décider si le pelvis est ancré au monde (mannequin fixe,
  on bouge les membres) ou monté sur une base mobile (locomotion du scénario 1).
  Décision à prendre selon le comportement observé à l'import.
- **Meshes manquants** : si les STL ne sont pas trouvés, RoboDK importe la
  cinématique avec les box de collision (présentes dans l'URDF) → suffisant pour
  tester le pilotage, à défaut du visuel.
- **22 DDL** : 6 par bras (épaule 3 + coude 1 + poignet 2) + 5 par jambe
  (hanche 3 + genou 1 + cheville 1). Vérifier que les amplitudes (limites) sont
  reprises à l'import.

## Si l'import échoue / mécanisme non articulé

- Vérifier que le plugin URDF est bien actif.
- Tester l'alternative STEP : importer `Manikin_1.STEP` (fichier 3D Teams) pour le
  visuel, puis reconstruire/piloter la cinématique via l'API.
- Fallback : importer chaque membre comme chaîne série séparée, synchronisées par script.
