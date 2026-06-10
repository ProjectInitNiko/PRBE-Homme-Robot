# -*- coding: utf-8 -*-
"""
Tache_Bras.py — Scenario membres superieurs : pick & place d'une piece
cubique sur une table (reunion du 04/06 : "tache bras", main + bras qui
s'articulent, le corps reste fixe).

Scenario :
  Le mannequin est debout devant une table. Une piece cubique est posee
  sur la table a sa GAUCHE. Il la saisit de la main gauche, la deplace
  vers la DROITE et la repose sur la meme table.

A LANCER : RoboDK ouvert, station avec le rig 22 DDL, mannequin au
GARDE-A-VOUS (le script capture le repos au demarrage).
    python Tache_Bras.py

Construction : la table et la piece sont creees si absentes (AddShape,
geometrie locale centree -> position par setPose, objets type 5 dont la
pose EST persistee dans le .rdk — pas de bug type 7).

Cinematique : bras gauche = 6 DDL (epaule abduction Z / flexion X /
rotation Y, coude flexion X, poignet flexion X / deviation Z), memes
conventions que Mouvement_v2 (pose = REST x rot(axe, angle), limites
humaines). L'effecteur = centre de la paume (bbox de la main au repos).
IK numerique : moindres carres amortis (Jacobien par differences finies),
position seule, limites respectees par clamp.

Convention station : X+ = cote GAUCHE du mannequin, +Z = devant, Y = haut.
"""
import math
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from robolink import Robolink, ITEM_TYPE_FRAME
from robodk.robomath import Mat, transl, rotx, roty, rotz, invH

# ---------------- parametres de la scene (mm) ----------------
TABLE_TOP = 900          # hauteur de la surface de la table
TABLE_SX, TABLE_SZ = 1100, 550   # plateau : largeur (X) x profondeur (Z)
TABLE_TH = 40            # epaisseur plateau
TABLE_CZ = 455           # centre du plateau devant le mannequin (Z)
CUBE = 80                # arete de la piece cubique
PICK_X, PICK_Z = 330, 400        # piece au depart : a GAUCHE (X+)
PLACE_X, PLACE_Z = 80, 400       # depose : 25 cm vers la DROITE (rester
                                 # anatomique : pas de traversee complete
                                 # du corps avec le bras gauche)
PALM = 55                # distance paume <-> centre du cube a la saisie
APPROACH = 50            # hauteur d'approche au-dessus du cube
STEPS = 18               # pas d'interpolation par phase
DT = 0.025               # tempo animation (s)

# ---------------- bras gauche : DDL, axes, limites (deg) ----------------
ARM = [
    ("shoulderL_abduction", "z", -90, 135),
    ("shoulderL_flexion",   "x", -90, 90),
    ("shoulderL_rotation",  "y", -45, 180),
    ("elbowL_flexion",      "x",   0, 145),
    ("wristL_flexion",      "x", -50, 60),
    ("wristL_deviation",    "z", -30, 20),
]
ROT = {"x": rotx, "y": roty, "z": rotz}

# posture naturelle pour CE scenario (saisie sur table) : l'IK position
# seule part en contorsions (coude au ciel, paume vers le haut, poignet en
# butee) si on la laisse libre -> 3 garde-fous :
LIM_SCEN = [(-45, 60), (-90, 20), (-30, 30), (0, 120), (-25, 25), (-15, 15)]
W = [1.0, 1.0, 0.4, 1.0, 0.3, 0.3]          # cout de mouvement (poignet cher)
Q_NAT = [10, -45, 0, 50, 0, 0]              # posture de reference (biais)
K_NAT = 0.002                               # rappel postural (doux !)
NAT_ZONE = 25.0                             # rappel actif seulement pres de la cible (mm)

RDK = Robolink()
print("Station :", RDK.ActiveStation().Name())


# ---------------- scene : table + piece ----------------

def _box_tris(sx, sy, sz):
    """12 triangles d'un pave centre sur l'origine de l'objet."""
    x, y, z = sx / 2.0, sy / 2.0, sz / 2.0
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
         (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    quads = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
             (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)]
    tris = []
    for a, b, c, d in quads:
        tris += [v[a], v[b], v[c], v[a], v[c], v[d]]
    return tris


def _add_box(name, sx, sy, sz, pos, color):
    it = RDK.Item(name)
    if it.Valid() and it.Type() == 5:
        return it
    tris = []
    if name == "Table":
        # plateau (origine objet = centre de la SURFACE du plateau)
        for p in _box_tris(sx, TABLE_TH, sz):
            tris.append((p[0], p[1] - TABLE_TH / 2.0, p[2]))
        # 4 pieds
        for px, pz in ((sx/2-40, sz/2-40), (-(sx/2-40), sz/2-40),
                       (sx/2-40, -(sz/2-40)), (-(sx/2-40), -(sz/2-40))):
            for p in _box_tris(40, TABLE_TOP - TABLE_TH, 40):
                tris.append((p[0] + px, p[1] - TABLE_TH - (TABLE_TOP - TABLE_TH)/2.0, p[2] + pz))
    else:
        tris = _box_tris(sx, sy, sz)
    obj = RDK.AddShape([list(p) for p in tris])
    obj.setName(name)
    obj.setColor(color)
    obj.setPose(transl(*pos))
    return obj


table = _add_box("Table", TABLE_SX, TABLE_TOP, TABLE_SZ,
                 (0, TABLE_TOP, TABLE_CZ), [0.55, 0.38, 0.21, 1])
piece = _add_box("Piece", CUBE, CUBE, CUBE,
                 (PICK_X, TABLE_TOP + CUBE / 2.0, PICK_Z), [0.95, 0.55, 0.10, 1])
print("Scene : Table + Piece en place")

# ---------------- modele FK du bras gauche ----------------
F = {nom: RDK.Item(nom, ITEM_TYPE_FRAME) for nom, *_ in ARM}
for nom, fr in F.items():
    if not fr.Valid():
        sys.exit(f"ERREUR : frame {nom} introuvable — rig 22 DDL absent ?")
REST = {nom: F[nom].Pose() for nom, *_ in ARM}
ROOT = F[ARM[0][0]].Parent().PoseAbs()     # pose absolue du parent de l'epaule

# effecteur : centre de la paume au repos, exprime dans le dernier frame
main = None
for it in RDK.ItemList():
    if it.Type() == 7 and it.Name() == "Manikin_1-main_g":
        main = it
if main is None:
    sys.exit("ERREUR : Manikin_1-main_g introuvable.")
bb = main.setParam("BoundingBox")
hand0 = [(bb["min"][i] + bb["max"][i]) / 2.0 for i in range(3)]
wrist_abs0 = F[ARM[-1][0]].PoseAbs()
E_LOCAL = invH(wrist_abs0) * transl(*hand0)
e = E_LOCAL.rows
E_LOCAL = (e[0][3], e[1][3], e[2][3])
print(f"Effecteur (paume) au repos : ({hand0[0]:.0f}, {hand0[1]:.0f}, {hand0[2]:.0f})")


def fk(q):
    """Position absolue de la paume pour les 6 angles q (deg)."""
    P = ROOT
    for (nom, axe, lo, hi), a in zip(ARM, q):
        P = P * REST[nom] * ROT[axe](math.radians(a))
    P = P * transl(*E_LOCAL)
    r = P.rows
    return [r[0][3], r[1][3], r[2][3]]


def clamp(q):
    """Bornes du scenario (incluses dans les limites humaines de ARM)."""
    return [max(lo, min(hi, a)) for (lo, hi), a in zip(LIM_SCEN, q)]


def ik(target, q0, tol=8.0, iters=200):
    """Moindres carres amortis PONDERES vers `target` (position, mm),
    avec rappel postural vers Q_NAT. Retourne (q, residu)."""
    q = clamp(list(q0))
    lam2 = 25.0 ** 2                     # amortissement (mm^2)
    for _ in range(iters):
        p = fk(q)
        err = [target[i] - p[i] for i in range(3)]
        n = math.sqrt(sum(e * e for e in err))
        if n < tol:
            return q, n
        # Jacobien 3x6 par differences finies
        J = [[0.0] * 6 for _ in range(3)]
        for j in range(6):
            dq = list(q)
            dq[j] += 0.5
            pj = fk(dq)
            for i in range(3):
                J[i][j] = (pj[i] - p[i]) / 0.5
        # dq = W^2 J^T (J W^2 J^T + lam I)^-1 err  (poids = cout par DDL)
        JJT = [[sum(W[k] * W[k] * J[i][k] * J[r][k] for k in range(6))
                + (lam2 if i == r else 0) for r in range(3)] for i in range(3)]
        # inversion 3x3 (Cramer)
        a, b, c = JJT[0]; d, e2, f = JJT[1]; g, h, i2 = JJT[2]
        det = a*(e2*i2-f*h) - b*(d*i2-f*g) + c*(d*h-e2*g)
        inv = [[(e2*i2-f*h)/det, (c*h-b*i2)/det, (b*f-c*e2)/det],
               [(f*g-d*i2)/det, (a*i2-c*g)/det, (c*d-a*f)/det],
               [(d*h-e2*g)/det, (b*g-a*h)/det, (a*e2-b*d)/det]]
        v = [sum(inv[i][k] * err[k] for k in range(3)) for i in range(3)]
        for j in range(6):
            q[j] += W[j] * W[j] * sum(J[i][j] * v[i] for i in range(3))
            if n < NAT_ZONE:                     # rappel postural doux,
                q[j] += K_NAT * (Q_NAT[j] - q[j])  # seulement pres du but
        q = clamp(q)
    p = fk(q)
    return q, math.sqrt(sum((target[i] - p[i]) ** 2 for i in range(3)))


def ik_multi(target, q0, tol=8.0):
    """IK avec multi-start : warm-start d'abord, sinon seeds varies
    (minima locaux frequents avec le coude borne 0-145)."""
    import random
    rng = random.Random(0)               # reproductible
    best_q, best_r = ik(target, q0, tol)
    if best_r < 30:
        return best_q, best_r
    seeds = [list(Q_NAT),
             [0.0] * 6,
             [20, -60, 0, 80, 0, 0],     # bras devant, coude bien plie
             [-20, -70, 0, 40, 0, 0]]    # bras tendu devant-bas
    seeds += [[rng.uniform(lo, hi) for lo, hi in LIM_SCEN] for _ in range(5)]
    for s in seeds:
        q, r = ik(target, s, tol)
        if r < best_r:
            best_q, best_r = q, r
        if best_r < tol:
            break
    return best_q, best_r


def applique(q):
    for (nom, axe, lo, hi), a in zip(ARM, q):
        F[nom].setPose(REST[nom] * ROT[axe](math.radians(a)))


def anime(q_from, q_to, steps=STEPS):
    for s in range(1, steps + 1):
        t = s / steps
        t = t * t * (3 - 2 * t)          # lissage ease-in-out
        applique([qa + (qb - qa) * t for qa, qb in zip(q_from, q_to)])
        RDK.Render(True)
        time.sleep(DT)


# ---------------- choregraphie ----------------
cube_y = TABLE_TOP + CUBE / 2.0
GRASP_Y = cube_y + CUBE / 2.0 + PALM - 35    # paume qui coiffe le cube
targets = [
    ("approche",  (PICK_X, GRASP_Y + APPROACH, PICK_Z)),
    ("saisie",    (PICK_X, GRASP_Y, PICK_Z)),
    ("levee",     (PICK_X, GRASP_Y + APPROACH, PICK_Z)),
    ("transfert", ((PICK_X + PLACE_X) / 2.0, GRASP_Y + APPROACH, (PICK_Z + PLACE_Z) / 2.0)),
    ("pre-depose", (PLACE_X, GRASP_Y + APPROACH, PLACE_Z)),
    ("depose",    (PLACE_X, GRASP_Y, PLACE_Z)),
    ("degage",    (PLACE_X, GRASP_Y + APPROACH, PLACE_Z)),
]

q_rest = [0.0] * 6
configs, q = {}, q_rest
CRITIQUES = {"saisie": 30, "depose": 30}     # seuil serre au contact,
SEUIL_TRANSIT = 50                            # tolerant en transit (en vol)
print("--- IK ---")
ok = True
for nom, tgt in targets:
    q, res = ik_multi(tgt, q)
    configs[nom] = q
    seuil = CRITIQUES.get(nom, SEUIL_TRANSIT)
    flag = "OK " if res < seuil else "!! "
    if res >= seuil:
        ok = False
    print(f"  {flag}{nom:10s} cible ({tgt[0]:5.0f},{tgt[1]:5.0f},{tgt[2]:5.0f})  residu {res:5.1f} mm")
if not ok:
    print("!! residus hors seuil — scene peut-etre hors d'atteinte, ajuster les parametres")

SNAP = "--snap" in sys.argv
SNAPDIR = r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\scripts\_debug_reperes"


def snap(name):
    if SNAP:
        RDK.Render(True)
        RDK.Command("Snapshot", SNAPDIR + "\\" + name + ".png")


print("--- Animation ---")
station = RDK.ActiveStation()
wrist = F[ARM[-1][0]]
# demo propre : masquer les reperes du rig (--frames pour les garder)
# NB : le 2e parametre (visible_frame) est requis pour les items frame
if "--frames" not in sys.argv:
    for fr in RDK.ItemList(ITEM_TYPE_FRAME):
        fr.setVisible(False, False)
# remettre la piece au depart (re-run propre)
piece.setParentStatic(station)
piece.setPose(transl(PICK_X, cube_y, PICK_Z))
applique(q_rest)
RDK.Render(True)
time.sleep(0.4)

anime(q_rest, configs["approche"])
anime(configs["approche"], configs["saisie"])
piece.setParentStatic(wrist)                  # saisie : la piece suit la main
print("  piece saisie")
snap("tache_1_saisie")
anime(configs["saisie"], configs["levee"])
anime(configs["levee"], configs["transfert"])
snap("tache_2_transfert")
anime(configs["transfert"], configs["pre-depose"])
anime(configs["pre-depose"], configs["depose"])
piece.setParentStatic(station)                # lacher
# snap : reposer la piece a plat sur la table, exactement a la cible
piece.setPose(transl(PLACE_X, cube_y, PLACE_Z))
print(f"  piece deposee en ({PLACE_X:.0f}, {cube_y:.0f}, {PLACE_Z:.0f})")
snap("tache_3_depose")
anime(configs["depose"], configs["degage"])
anime(configs["degage"], q_rest)
RDK.Render(True)
snap("tache_4_final")
print("Fini — piece deplacee de gauche a droite.")
