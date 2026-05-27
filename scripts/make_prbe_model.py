#!/usr/bin/env python3
"""make_prbe_model.py — Réduit un mannequin HMG aux DDL validés pour le PRBE.

Transforme un URDF généré par human-model-generator (54 DDL articulaires) en
modèle conforme au compte rendu de réunion du 20 mai 2026 : 16 DDL articulaires.

Modèle cible (validé par Ciampi + Diallo, bras symétriques) :
  - Jambes : 10 DDL = par jambe (hanche 3 + genou 1 + cheville 1) x 2
  - Bras (D + G) : 12 DDL = par bras (épaule 3 + coude 1 + poignet 2) x 2
  - Épine, clavicules, cou, tête, doigts : figés (fixed)

Méthode : whitelist. Tout joint `revolute` dont le nom n'est PAS dans KEEP_REVOLUTE
passe en `fixed`. Approche sûre — tout joint ajouté par une future régénération HMG
sera figé par défaut tant qu'il n'est pas explicitement gardé.

Le choix des axes gardés s'appuie sur les limites articulaires du template HMG
(cf. docstring KEEP_REVOLUTE), pas sur une convention supposée :
  - genou/cheville : roty = flexion sagittale (limites [0,135°] / [-30°,+50°])
  - coude         : rotz = flexion (limite [0,145°]) ; roty = pronation (±90°), figé

Usage :
    python make_prbe_model.py [entrée.urdf] [sortie.urdf]
Défauts : examples/Niko_v1.urdf -> examples/Niko_v2_PRBE.urdf
"""

import re
import sys
from pathlib import Path

# --- DDL à conserver (16 au total) ----------------------------------------
# Le suffixe d'axe encode l'articulation physique gardée (voir docstring module).
KEEP_REVOLUTE = {
    # Bras droit — 6 DDL
    "jRightShoulder_rotx", "jRightShoulder_roty", "jRightShoulder_rotz",  # épaule (rotule 3)
    "jRightElbow_rotz",                                                   # coude (flexion)
    "jRightWrist_rotx", "jRightWrist_rotz",                               # poignet (2)
    # Bras gauche — 6 DDL
    "jLeftShoulder_rotx", "jLeftShoulder_roty", "jLeftShoulder_rotz",     # épaule (rotule 3)
    "jLeftElbow_rotz",                                                    # coude (flexion)
    "jLeftWrist_rotx", "jLeftWrist_rotz",                                 # poignet (2)
    # Jambe droite — 5 DDL
    "jRightHip_rotx", "jRightHip_roty", "jRightHip_rotz",                 # hanche (rotule 3)
    "jRightKnee_roty",                                                    # genou (flexion)
    "jRightAnkle_roty",                                                   # cheville (flexion)
    # Jambe gauche — 5 DDL
    "jLeftHip_rotx", "jLeftHip_roty", "jLeftHip_rotz",                    # hanche (rotule 3)
    "jLeftKnee_roty",                                                     # genou (flexion)
    "jLeftAnkle_roty",                                                    # cheville (flexion)
}
EXPECTED_DDL = 22

# Regroupement pour le rapport final.
REGIONS = [
    ("Bras droit", ["jRightShoulder", "jRightElbow", "jRightWrist"]),
    ("Bras gauche", ["jLeftShoulder", "jLeftElbow", "jLeftWrist"]),
    ("Jambe droite", ["jRightHip", "jRightKnee", "jRightAnkle"]),
    ("Jambe gauche", ["jLeftHip", "jLeftKnee", "jLeftAnkle"]),
]

JOINT_RE = re.compile(r'(<joint name=")(?P<name>[^"]+)(" type=")revolute(">)')


def transform(text: str):
    kept, fixed = [], []

    def repl(m):
        name = m.group("name")
        if name in KEEP_REVOLUTE:
            kept.append(name)
            return m.group(0)  # inchangé
        fixed.append(name)
        return f'{m.group(1)}{name}{m.group(3)}fixed{m.group(4)}'

    new_text = JOINT_RE.sub(repl, text)
    return new_text, kept, fixed


def main():
    repo = Path(__file__).resolve().parent.parent
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "examples" / "Niko_v1.urdf"
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else repo / "examples" / "Niko_v2_PRBE.urdf"

    text = src.read_text(encoding="utf-8")
    new_text, kept, fixed = transform(text)

    # Vérifs de cohérence avant écriture.
    unknown = KEEP_REVOLUTE - set(kept)
    if unknown:
        sys.exit(f"ERREUR : joints du KEEP_REVOLUTE absents de l'URDF : {sorted(unknown)}")
    if len(kept) != EXPECTED_DDL:
        sys.exit(f"ERREUR : {len(kept)} DDL gardés, attendu {EXPECTED_DDL}.")

    dst.write_text(new_text, encoding="utf-8")

    print(f"Entrée  : {src}")
    print(f"Sortie  : {dst}")
    print(f"DDL articulaires : {len(kept)} gardés / {len(fixed)} revolute figés en fixed\n")
    for label, prefixes in REGIONS:
        names = [k for k in kept if any(k.startswith(p) for p in prefixes)]
        print(f"  {label:14s} {len(names)} DDL : {', '.join(sorted(names))}")
    print(f"\nFigés (revolute -> fixed) : {len(fixed)}")
    print("  " + ", ".join(sorted(fixed)))


if __name__ == "__main__":
    main()
