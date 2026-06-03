#!/usr/bin/env python3
"""build_human_robodk.py — Construit l'operateur articule dans RoboDK a partir de
l'assemblage SolidWorks exporte en STEP (Manikin_1.STEP), SANS passer par l'URDF.

Pourquoi : RoboDK n'importe pas un arbre humain branche a 22 DDL (102 joints) en un
seul mecanisme. On part des 15 segments du STEP, deja positionnes, et on construit la
hierarchie d'articulation a la main (Reference Frames + setParentStatic + API Python).

Pipeline (valide en live le 03/06/2026 sur RoboDK 6.0.4) :
  1. Station propre + import du STEP            -> 1 objet fusionne.
  2. obj.setParam('Split')                      -> 17 sous-solides positionnes.
  3. Re-identification par GEOMETRIE (bbox)     -> 15 segments anatomiques.
  4. 1 Reference Frame par articulation + setParentStatic -> bassin -> membres.
  5. drive(joint, axe, theta) = frame.setPose(rest * rot(axe, theta)) -> pilotage.

`build_operator(RDK)` est REUTILISABLE (importe par walk_human_robodk.py).

Usage (build + pose de demo) :
    "C:\\RoboDK\\Python-Embedded\\python.exe" build_human_robodk.py [chemin\\Manikin_1.STEP]
"""
import sys
import math
from pathlib import Path

try:
    from robolink import Robolink, ITEM_TYPE_OBJECT
except ImportError:
    sys.exit("Utilise le python embarque de RoboDK : C:\\RoboDK\\Python-Embedded\\python.exe")

try:
    from robodk.robomath import transl, rotx, roty, rotz
except Exception:  # noqa: BLE001
    from robodk import transl, rotx, roty, rotz

DEFAULT_STEP = Path(r"D:\PRBE_Homme_Robot\Documents Teams\Modeles de simulation\Manikin\Manikin_1.STEP")

# --- Ancres anatomiques (centre bbox, mm), MESUREES sur Manikin_1.STEP ---
# Y = hauteur, X = lateral (+ = cote droit modele), Z = profondeur (avant = +Z).
ANCHORS = {
    "Hips":      (0, 958, 0),
    "Torso":     (15, 1260, 0),
    "Head":      (20, 1584, 30),
    "ArmRUpper": (274, 1283, 13),
    "ArmRFore":  (436, 1122, 73),
    "ArmRHand":  (554, 956, 161),
    "ArmLUpper": (-177, 1265, -26),
    "ArmLFore":  (-248, 1056, 67),
    "ArmLHand":  (-326, 864, 128),
    "LegRUpper": (87, 703, -38),
    "LegRLower": (144, 292, -50),
    "LegRFoot":  (213, 37, -20),
    "LegLUpper": (-103, 710, -37),
    "LegLLower": (-179, 315, -101),
    "LegLFoot":  (-257, 63, -101),
}

# (nom_joint, segment_parent, segment_enfant) — ordre racine-d'abord.
CHAINS = [
    ("waist", "Hips", "Torso"), ("neck", "Torso", "Head"),
    ("shoulderR", "Torso", "ArmRUpper"), ("elbowR", "ArmRUpper", "ArmRFore"),
    ("wristR", "ArmRFore", "ArmRHand"),
    ("shoulderL", "Torso", "ArmLUpper"), ("elbowL", "ArmLUpper", "ArmLFore"),
    ("wristL", "ArmLFore", "ArmLHand"),
    ("hipR", "Hips", "LegRUpper"), ("kneeR", "LegRUpper", "LegRLower"),
    ("ankleR", "LegRLower", "LegRFoot"),
    ("hipL", "Hips", "LegLUpper"), ("kneeL", "LegLUpper", "LegLLower"),
    ("ankleL", "LegLLower", "LegLFoot"),
]

_ROT = {"x": rotx, "y": roty, "z": rotz}


def rot(axis, deg):
    return _ROT[axis](math.radians(deg))


def _bbox_center(it):
    bb = it.setParam("BoundingBox")
    mn, mx = bb["min"], bb["max"]
    return [(mn[i] + mx[i]) / 2.0 for i in range(3)]


def _nearest_anchor(c):
    best, bestd = None, 1e18
    for name, a in ANCHORS.items():
        d = sum((c[i] - a[i]) ** 2 for i in range(3))
        if d < bestd:
            best, bestd = name, d
    return best, math.sqrt(bestd)


def resolve_step(arg=None):
    step = Path(arg) if arg else DEFAULT_STEP
    if step.exists():
        return step
    hits = list(Path(r"D:\PRBE_Homme_Robot\Documents Teams").rglob("Manikin_1.STEP"))
    return hits[0] if hits else None


def build_operator(RDK, step=None, verbose=True):
    """Construit l'operateur dans une station propre. Renvoie un dict :
       {base, joint_frame{jname:Item}, rest_local{jname:Pose}, seg_objs, hips_anchor}."""
    step = resolve_step(step)
    if not step:
        raise FileNotFoundError("Manikin_1.STEP introuvable")

    RDK.AddStation("PRBE_Operateur")
    blob = RDK.AddFile(str(step))
    if not blob or not blob.Valid():
        raise RuntimeError("AddFile a echoue")
    blob.setParam("Split")
    subs = blob.Childs()
    if verbose:
        print(f"Import + split -> {len(subs)} sous-solides")

    seg_objs = {name: [] for name in ANCHORS}
    for s in subs:
        seg, _ = _nearest_anchor(_bbox_center(s))
        seg_objs[seg].append(s)

    base = RDK.AddFrame("Human_Base")
    base.setPoseAbs(transl(*ANCHORS["Hips"]))
    for o in seg_objs["Hips"]:
        o.setParentStatic(base)

    seg_frame = {"Hips": base}
    joint_frame, rest_local = {}, {}
    for jname, parent, child in CHAINS:
        if not seg_objs[child]:
            continue
        pa, ca = ANCHORS[parent], ANCHORS[child]
        jc = [(pa[i] + ca[i]) / 2.0 for i in range(3)]
        fr = RDK.AddFrame(jname, seg_frame[parent])
        fr.setPoseAbs(transl(*jc))
        for o in seg_objs[child]:
            o.setParentStatic(fr)
        seg_frame[child] = fr
        joint_frame[jname] = fr
        rest_local[jname] = fr.Pose()

    if verbose:
        print(f"Hierarchie : {len(joint_frame)} articulations")
    return {"base": base, "joint_frame": joint_frame, "rest_local": rest_local,
            "seg_objs": seg_objs, "hips_anchor": ANCHORS["Hips"]}


def set_joint(op, jname, axis, deg):
    """Actionne un joint : pose locale = repos * rotation(axe, angle)."""
    op["joint_frame"][jname].setPose(op["rest_local"][jname] * rot(axis, deg))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    RDK = Robolink()
    print(f"RoboDK {RDK.Version()}")
    op = build_operator(RDK, step=arg)

    # Pose de demo (preuve d'articulation)
    for jname, axis, deg in [("shoulderR", "z", -50), ("elbowR", "z", -75),
                             ("kneeL", "x", 70), ("neck", "y", 25)]:
        if jname in op["joint_frame"]:
            set_joint(op, jname, axis, deg)
    print("Pose de demo appliquee.")

    out = Path(__file__).resolve().parent.parent / "examples" / "human_robodk.rdk"
    try:
        RDK.Save(str(out))
        print(f"Station sauvee : {out}")
    except Exception as e:  # noqa: BLE001
        print(f"(Save ignore : {e})")


if __name__ == "__main__":
    main()
