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
humaines). L'effecteur = centre de la main (bbox au repos).

IK numerique 6 DOF : position ET orientation (DLS amortie, Jacobien 6x6
par differences finies, limites par clamp, multi-start). L'orientation de
la main est CONTRAINTE (sinon la paume part de travers / poignet a
l'envers) : on la maintient verticale, doigts vers le bas, comme au repos.
Le bras n'a pas de pronation d'avant-bras, donc "paume a plat" est evite
(il tordrait le bras) ; le poids WO equilibre position vs orientation.

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
GRASP_CLEAR = 35         # centre de la main au-dessus du haut du cube (saisie)
APPROACH = 45            # hauteur d'approche / de levee (le cube degage la table)
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

# bornes du scenario (incluses dans les limites humaines)
LIM_SCEN = [(-45, 60), (-90, 20), (-45, 45), (0, 130), (-40, 50), (-25, 20)]

# ORIENTATION DE LA MAIN — c'est le coeur du fix : l'IK position seule
# laissait la paume dans une orientation quelconque (de travers, doigts en
# l'air = "poignet a l'envers"). On contraint maintenant l'orientation du
# repere POIGNET.
# Geometrie mesuree (_diag_main_geom) dans le repere poignet au repos :
#   - doigts le long de  -Y_local
#   - normale de paume le long de  Z_local  (axe le plus fin)
# Le bras n'a PAS de pronation d'avant-bras (poignet = flexion + deviation
# seulement) : imposer "paume a plat vers le bas" le tord et degrade la
# position. On garde donc la main dans son ORIENTATION DE REPOS — verticale,
# doigts vers le bas (-Y monde), paume vers l'avant (+Z monde) — qui est
# naturelle, atteignable, et empeche tout retournement du poignet.
# Cible = orientation identite du repere poignet (= sa pose au repos).
R_GRASP = Mat([[1.0, 0.0, 0.0, 0.0],
               [0.0, 1.0, 0.0, 0.0],
               [0.0, 0.0, 1.0, 0.0],
               [0.0, 0.0, 0.0, 1.0]])
WO = 65.0           # poids de l'orientation (mm equivalents par radian) :
                    # assez pour tenir la main droite, pas trop pour ne pas
                    # voler la position au bras
LAM = 5.0           # amortissement DLS (petit : sinon sur-amorti = pas de
                    # convergence ; remonte pres des singularites via clamp)

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


def fk_pose(q):
    """Pose absolue (Mat 4x4) du repere POIGNET pour les 6 angles q (deg).
    L'orientation de ce repere = orientation de la main (rigide)."""
    P = ROOT
    for (nom, axe, lo, hi), a in zip(ARM, q):
        P = P * REST[nom] * ROT[axe](math.radians(a))
    return P


def eff_pos(P):
    """Position monde de l'effecteur (centre paume) depuis la pose poignet."""
    r = (P * transl(*E_LOCAL)).rows
    return [r[0][3], r[1][3], r[2][3]]


def cols(M):
    r = M.rows
    return [[r[0][c], r[1][c], r[2][c]] for c in range(3)]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def ori_err(Rc, Rd):
    """Erreur d'orientation (vecteur monde, ~rad) menant Rc -> Rd.
    Formule de Siciliano : 0.5 * somme(col_c x col_d)."""
    e = [0.0, 0.0, 0.0]
    for k in range(3):
        c = cross(Rc[k], Rd[k])
        e = [e[i] + c[i] for i in range(3)]
    return [0.5 * v for v in e]


RG = cols(R_GRASP)


def clamp(q):
    """Bornes du scenario (incluses dans les limites humaines de ARM)."""
    return [max(lo, min(hi, a)) for (lo, hi), a in zip(LIM_SCEN, q)]


def _solve6(A, b):
    """Resout A y = b (6x6) par elimination de Gauss avec pivot partiel."""
    n = 6
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        if abs(piv) < 1e-12:
            continue
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c] / piv
                M[r] = [M[r][k] - f * M[c][k] for k in range(n + 1)]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]


def ik(tpos, q0, tol_p=6.0, tol_o=0.05, iters=500):
    """IK 6 DOF position + orientation (paume vers le bas), DLS amortie.
    Retourne (q, residu_pos_mm, residu_ori_deg)."""
    q = clamp(list(q0))
    for _ in range(iters):
        P = fk_pose(q)
        p = eff_pos(P)
        Rc = cols(P)
        ep = [tpos[i] - p[i] for i in range(3)]
        eo = ori_err(Rc, RG)
        np_ = math.sqrt(sum(v*v for v in ep))
        no_ = math.sqrt(sum(v*v for v in eo))
        if np_ < tol_p and no_ < tol_o:
            return q, np_, math.degrees(no_)
        x = ep + [WO * v for v in eo]            # tache 6D (pos mm ; ori ponderee)
        # Jacobien 6x6 par differences finies (lignes 0-2 position, 3-5 orient)
        J = [[0.0] * 6 for _ in range(6)]
        for j in range(6):
            dq = list(q)
            dq[j] += 0.5
            Pj = fk_pose(dq)
            pj = eff_pos(Pj)
            dphi = ori_err(Rc, cols(Pj))         # petite rotation Rc -> Rj
            for i in range(3):
                J[i][j] = (pj[i] - p[i]) / 0.5
                J[3 + i][j] = WO * dphi[i] / 0.5
        # DLS : dq = J^T (J J^T + lam^2 I)^-1 x
        JJT = [[sum(J[i][k] * J[r][k] for k in range(6)) + (LAM * LAM if i == r else 0)
                for r in range(6)] for i in range(6)]
        y = _solve6(JJT, x)
        for j in range(6):
            q[j] += sum(J[i][j] * y[i] for i in range(6))
        q = clamp(q)
    P = fk_pose(q)
    ep = [tpos[i] - eff_pos(P)[i] for i in range(3)]
    no_ = math.sqrt(sum(v*v for v in ori_err(cols(P), RG)))
    return q, math.sqrt(sum(v*v for v in ep)), math.degrees(no_)


def ik_multi(tpos, q0):
    """Multi-start : warm-start puis seeds varies (minima locaux frequents
    avec l'orientation contrainte). Score = pos + 3 mm/deg d'orientation."""
    import random
    rng = random.Random(0)
    def score(r):
        return r[0] + 3.0 * r[1]
    best = ik(tpos, q0)
    if score((best[1], best[2])) < 20:
        return best
    seeds = [[20, -55, 10, 80, -10, 0],     # bras devant, coude plie, paume bas
             [0, -45, 20, 60, 0, 0],
             [-15, -65, 25, 50, -15, 0],
             [0.0] * 6]
    seeds += [[rng.uniform(lo, hi) for lo, hi in LIM_SCEN] for _ in range(6)]
    bq, bp, bo = best
    for s in seeds:
        q, rp, ro = ik(tpos, s)
        if score((rp, ro)) < score((bp, bo)):
            bq, bp, bo = q, rp, ro
        if score((bp, bo)) < 10:
            break
    return bq, bp, bo


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
# l'effecteur est le CENTRE de la main ; paume vers le bas, la main coiffe
# le cube -> on vise au-dessus du haut du cube.
cube_y = TABLE_TOP + CUBE / 2.0          # centre du cube
cube_top = cube_y + CUBE / 2.0           # haut du cube
GRASP_Y = cube_top + GRASP_CLEAR         # centre main quand elle tient le cube
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
print("--- IK 6 DOF (position + paume vers le bas) ---")
ok = True
for nom, tgt in targets:
    q, rp, ro = ik_multi(tgt, q)
    configs[nom] = q
    flag = "OK " if (rp < 25 and ro < 12) else "!! "
    if rp >= 25 or ro >= 12:
        ok = False
    print(f"  {flag}{nom:10s} cible ({tgt[0]:5.0f},{tgt[1]:5.0f},{tgt[2]:5.0f})  "
          f"pos {rp:5.1f} mm  paume {ro:4.1f} deg")
if not ok:
    print("!! residus hors seuil — verifier l'atteignabilite / l'orientation")

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
