#!/usr/bin/env python3
"""robodk_import_test.py — Teste l'import du mannequin dans RoboDK et vérifie
que la chaîne articulaire est pilotable depuis l'API Python.

À exécuter SUR UNE MACHINE OÙ ROBODK EST INSTALLÉ (poste école / plateforme ALIX),
avec le package `robodk` (pip install robodk) et le plugin "URDF Import" activé
dans RoboDK (Outils > Add-ins > URDF Import).

Usage :
    python robodk_import_test.py [chemin/vers/Niko_v2_PRBE.urdf]
Défaut : examples/Niko_v2_PRBE.urdf (relatif à ce repo)

Ce qu'il fait :
  1. Se connecte à RoboDK (le lance si besoin).
  2. Importe le fichier (AddFile gère l'URDF si le plugin est actif).
  3. Liste ce qui a été chargé (mécanismes / robots / objets).
  4. Pour chaque mécanisme : affiche le nombre d'axes, les joints courants,
     et tente un petit mouvement (joints à mi-amplitude) pour confirmer le pilotage.

NB : RoboDK est conçu pour des robots SÉRIE. Un mannequin humain est une chaîne
RAMIFIÉE (bassin -> 2 bras + 2 jambes). Surveiller si RoboDK importe l'arbre
complet en un seul mécanisme ou s'il faut le découper en chaînes série par membre.
"""
import sys
from pathlib import Path

try:
    from robolink import Robolink, ITEM_TYPE_ROBOT, ITEM_TYPE_OBJECT
except ImportError:
    sys.exit("Package 'robodk' introuvable. Installe-le : pip install robodk")


def main():
    repo = Path(__file__).resolve().parent.parent
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "examples" / "Niko_v2_PRBE.urdf"
    if not src.exists():
        sys.exit(f"Fichier introuvable : {src}")

    RDK = Robolink()
    print(f"RoboDK version : {RDK.Version()}")
    print(f"Import : {src}\n")

    item = RDK.AddFile(str(src))
    if not item.Valid():
        sys.exit("AddFile a échoué. Vérifie que le plugin 'URDF Import' est activé "
                 "(Outils > Add-ins), ou importe le .urdf manuellement (Fichier > Ouvrir).")

    robots = RDK.ItemList(ITEM_TYPE_ROBOT)
    objects = RDK.ItemList(ITEM_TYPE_OBJECT)
    print(f"Mécanismes/robots chargés : {len(robots)}")
    print(f"Objets chargés            : {len(objects)}\n")

    for r in robots:
        joints = r.Joints().list()
        print(f"[{r.Name()}] {len(joints)} axes")
        print(f"  joints courants : {[round(j, 1) for j in joints]}")
        lo, hi = r.JointLimits()
        lo, hi = lo.list(), hi.list()
        try:
            mid = [(a + b) / 2.0 for a, b in zip(lo, hi)]
            r.setJoints(mid)
            print(f"  -> setJoints(mi-amplitude) OK : pilotage confirmé")
        except Exception as e:  # noqa: BLE001
            print(f"  -> setJoints a échoué : {e}")

    if not robots:
        print("Aucun mécanisme articulé importé. RoboDK a probablement chargé le "
              "modèle comme objets statiques. Pistes : activer le plugin URDF, "
              "ou découper le mannequin en chaînes série par membre.")


if __name__ == "__main__":
    main()
