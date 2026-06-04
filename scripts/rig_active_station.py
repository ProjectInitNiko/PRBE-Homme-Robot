# -*- coding: utf-8 -*-
"""
rig_active_station.py — Pose les reperes (22 DDL) sur la station ACTIVE,
a partir des sous-solides du Split deja presents (blob Manikin_1).

- Garde les noms donnes par Niko (bassin, torso, tete, bras_g, ...).
- Deduit la convention gauche/droite des noms de Niko (verifiee par geometrie)
  et nomme les DDL en consequence (R = droit = _d).
- Complete le renommage des morceaux restants selon la meme convention.
- Meme logique de rig que build_operator_v2 : rotules 3 frames imbriques
  (hanches/epaules), 2 (poignets), 1 (genou/coude/cheville), buste fige,
  axes anatomiques + limites URDF, reperes au centre des boules.
"""
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from robolink import Robolink, ITEM_TYPE_FRAME
from robodk.robomath import transl, rotx, roty, rotz, Mat
from build_human_robodk import ANCHORS, _bbox_center, _nearest_anchor

ROT = {"x": rotx, "y": roty, "z": rotz}
D2R = math.pi / 180.0
EX = r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\examples"

# limites URDF (rad) ; abduction=Z, flexion=X, rotation=Y
HIP = [("abduction", "z", (-0.785, 0.524)), ("flexion", "x", (-2.094, 0.262)), ("rotation", "y", (-0.785, 0.785))]
SHO = [("abduction", "z", (-2.356, 1.571)), ("flexion", "x", (-1.571, 1.571)), ("rotation", "y", (-0.785, 3.142))]
KNEE = [("flexion", "x", (0.0, 2.356))]
ELBOW = [("flexion", "x", (0.0, 2.531))]
ANKLE = [("flexion", "x", (-0.524, 0.873))]
WRIST = [("flexion", "x", (-0.873, 1.047)), ("deviation", "z", (-0.524, 0.349))]

# partie anatomique (fr) -> cle d'ancre geometrique (sans le cote)
FR2PART = {"bassin": "Hips", "torso": "Torso", "tete": "Head",
           "avant_bras": "ArmFore", "bras": "ArmUpper", "main": "ArmHand",
           "cuisse": "LegUpper", "tibia": "LegLower", "pied": "LegFoot"}
PART2FR = {"Hips": "bassin", "Torso": "torso", "Head": "tete",
           "ArmUpper": "bras", "ArmFore": "avant_bras", "ArmHand": "main",
           "LegUpper": "cuisse", "LegLower": "tibia", "LegFoot": "pied"}

RDK = Robolink()
station = RDK.ActiveStation()
print("Station active :", station.Name())

# --- 1) retrouver le blob et ses sous-solides ---
blob = None
for it in station.Childs():
    if it.Type() == 5 and len(it.Childs()) >= 15:
        blob = it
        break
if blob is None:
    sys.exit("ERREUR : pas d'objet avec 15+ sous-solides dans la station active.")
kids = blob.Childs()
print("Blob :", blob.Name(), "->", len(kids), "sous-solides")

# --- 2) identification geometrique (cles 'modele' : R = X+) ---
seg = {n: [] for n in ANCHORS}
for k in kids:
    key, dist = _nearest_anchor(_bbox_center(k))
    seg[key].append(k)

# --- 3) convention gauche/droite d'apres les noms de Niko ---
# nom de Niko -> cle geometrique de l'item
def parse_fr(name):
    n = name.split("-", 1)[-1].lower()
    side = "G" if n.endswith("_g") else ("D" if n.endswith("_d") else None)
    stem = n[:-2] if side else n
    return FR2PART.get(stem), side

votes = []   # (nom, cote_geo, cote_niko) ; swap si _g de Niko == cote 'R' geometrique
for key, items in seg.items():
    geo_side = key[3] if key.startswith(("Arm", "Leg")) else None
    for it in items:
        part, side = parse_fr(it.Name())
        if part and side and geo_side:
            expected_part = key[:3] + key[4:]   # ex: ArmRUpper -> ArmUpper
            if part != expected_part:
                print(f"ATTENTION : {it.Name()} identifie geometriquement comme {key} (pas {part})")
            votes.append((it.Name(), geo_side, side))

if not votes:
    # Import frais (pas de renommage manuel) -> convention etablie le 04/06 :
    # X+ = cote GAUCHE du mannequin, +Z = devant (verifiee par les renommages de Niko).
    print("Pas de nom _g/_d -> convention par defaut : X+ = GAUCHE.")
    SWAP = True
else:
    swap_set = set((g == "R" and s == "G") or (g == "L" and s == "D") for _, g, s in votes)
    if len(swap_set) != 1:
        for v in votes:
            print("  vote:", v)
        sys.exit("ERREUR : noms incoherents entre eux — dis-moi quel cote est le bon.")
    SWAP = swap_set.pop()
print("Convention :", "X+ = GAUCHE (R/L inverses vs hier)" if SWAP else "X+ = droit (comme hier)")

def user_side(geo_side):
    """Cote 'utilisateur' (R=droit) pour un cote geometrique du modele."""
    if SWAP:
        return "L" if geo_side == "R" else "R"
    return geo_side

# --- 4) completer le renommage selon la convention de Niko ---
prefix = kids[0].Name().split("-", 1)[0]
for key, items in seg.items():
    if key.startswith(("Arm", "Leg")):
        fr_name = PART2FR[key[:3] + key[4:]] + ("_d" if user_side(key[3]) == "R" else "_g")
    else:
        fr_name = PART2FR[key]
    for i, it in enumerate(items):
        part, side = parse_fr(it.Name())
        if part:
            continue   # deja renomme par Niko -> on garde
        new = f"{prefix}-{fr_name}" + (f"_{i+1}" if len(items) > 1 else "")
        it.setName(new)
        print(f"  renomme : {new}  (geo {key})")

# --- 5) geometrie des boules (memes fonctions qu'hier) ---
def seg_bbox(key):
    mn = [1e9, 1e9, 1e9]
    mx = [-1e9, -1e9, -1e9]
    for o in seg[key]:
        bb = o.setParam("BoundingBox")
        for i in range(3):
            mn[i] = min(mn[i], bb["min"][i])
            mx[i] = max(mx[i], bb["max"][i])
    return mn, mx

def joint_center(parent, child):
    pmn, pmx = seg_bbox(parent)
    cmn, cmx = seg_bbox(child)
    return [(max(pmn[i], cmn[i]) + min(pmx[i], cmx[i])) / 2.0 for i in range(3)]

def shoulder_center(arm):
    mn, mx = seg_bbox(arm)
    w, h = mx[0] - mn[0], mx[1] - mn[1]
    x = mn[0] + 0.20 * w if mn[0] >= 0 else mx[0] - 0.20 * w
    y = mx[1] - 0.10 * h
    z = (mn[2] + mx[2]) / 2.0
    return [x, y, z]

# --- 6) construire le rig (jlabel = nom DDL cote UTILISATEUR) ---
def limb(geo_side, kind):
    """liste de (jlabel_user, dofs, seg_parent_geo, seg_enfant_geo)"""
    u = user_side(geo_side)
    if kind == "leg":
        return [(f"hip{u}", HIP, "Hips", f"Leg{geo_side}Upper"),
                (f"knee{u}", KNEE, f"Leg{geo_side}Upper", f"Leg{geo_side}Lower"),
                (f"ankle{u}", ANKLE, f"Leg{geo_side}Lower", f"Leg{geo_side}Foot")]
    return [(f"shoulder{u}", SHO, "Torso", f"Arm{geo_side}Upper"),
            (f"elbow{u}", ELBOW, f"Arm{geo_side}Upper", f"Arm{geo_side}Fore"),
            (f"wrist{u}", WRIST, f"Arm{geo_side}Fore", f"Arm{geo_side}Hand")]

base = RDK.AddFrame("Human_Base")
base.setPoseAbs(transl(*ANCHORS["Hips"]))
for k in ("Hips", "Torso", "Head"):
    for o in seg[k]:
        o.setParentStatic(base)

DOF = {}
for geo_side in ("R", "L"):
    for kind in ("leg", "arm"):
        pf = base
        for jlabel, dofs, parent_seg, segkey in limb(geo_side, kind):
            pos = shoulder_center(segkey) if jlabel.startswith("shoulder") else joint_center(parent_seg, segkey)
            print(f"  {jlabel:11s} @ ({pos[0]:6.0f},{pos[1]:6.0f},{pos[2]:6.0f})")
            last = pf
            for (dofname, axis, lim) in dofs:
                nm = f"{jlabel}_{dofname}"
                fr = RDK.AddFrame(nm, last)
                fr.setPoseAbs(transl(*pos))
                DOF[nm] = dict(frame=fr, axis=axis, lim=lim, rest=fr.Pose())
                last = fr
            for o in seg[segkey]:
                o.setParentStatic(last)
            pf = last
print(f"{len(DOF)} DDL construits.")

# --- 7) couleur unie + reperes visibles + neutre ---
for o in RDK.ItemList():
    if o.type in (5, 7):
        try:
            o.setColor([0.80, 0.84, 0.92, 1])
        except Exception:
            pass
for fr in RDK.ItemList(ITEM_TYPE_FRAME):
    fr.setVisible(True)

# --- 8) garde-a-vous : plaquer le bras ecarte du STEP le long du corps ---
# (le bras du cote X+ est ecarte d'environ 42 deg dans la pose STEP d'origine)
sho_xplus = DOF[f"shoulder{user_side('R')}_abduction"]["frame"]
sho_xplus.setPose(sho_xplus.Pose() * rotz(math.radians(-42.0)))

# --- 9) embarquer le programme de pilotage ---
if "Mouvement_v2" not in [p.Name() for p in RDK.ItemList(10)]:
    RDK.AddFile(r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\scripts\Mouvement_v2.py")

# --- 9) verification visuelle ---
RDK.setViewPose(Mat([[1, 0, 0, 0], [0, 1, 0, -1050], [0, 0, 1, -2300], [0, 0, 0, 1]]))
RDK.Render(True)
RDK.Command("Snapshot", EX + r"\rig_actif_check.png")
print("OK — snapshot examples/rig_actif_check.png")
