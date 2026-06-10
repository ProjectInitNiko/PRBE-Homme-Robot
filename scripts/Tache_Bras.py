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
HOME_Y = 1070            # hauteur de transit (centre main) : la main passe
                         # PAR-DESSUS la table. Atteignable + degage le plateau
                         # (doigts ~115 mm sous le centre -> ~955 > haut table 900)
STEPS = 14               # pas par segment cartesien
DT = 0.02                # tempo animation (s)

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


def _residu(q, tpos):
    P = fk_pose(q)
    ep = [tpos[i] - eff_pos(P)[i] for i in range(3)]
    no_ = math.sqrt(sum(v*v for v in ori_err(cols(P), RG)))
    return math.sqrt(sum(v*v for v in ep)), math.degrees(no_)


def ik(tpos, q0, tol_p=6.0, tol_o=0.09, iters=240, patience=22):
    """IK 6 DOF position + orientation, DLS amortie. S'arrete des que la
    cible est atteinte OU que le residu stagne (patience) — indispensable
    pour ne pas mouliner 500 iterations sur un point hors d'atteinte.
    Retourne (q, residu_pos_mm, residu_ori_deg)."""
    q = clamp(list(q0))
    best_q, best_s, stale = q[:], 1e18, 0
    for _ in range(iters):
        P = fk_pose(q)
        p = eff_pos(P)
        Rc = cols(P)
        ep = [tpos[i] - p[i] for i in range(3)]
        eo = ori_err(Rc, RG)
        np_ = math.sqrt(sum(v*v for v in ep))
        no_ = math.sqrt(sum(v*v for v in eo))
        s = np_ + WO * no_                       # score combine
        if s < best_s - 0.05:                    # progres (meme fin)
            best_s, best_q, stale = s, q[:], 0
        else:
            stale += 1
        if np_ < tol_p and no_ < tol_o:
            return q, np_, math.degrees(no_)
        if stale >= patience:                    # plus de progres -> stop
            break
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
    rp, ro = _residu(best_q, tpos)               # renvoie le MEILLEUR vu
    return best_q, rp, ro


def ik_multi(tpos, q0):
    """Warm-start, puis seeds SEULEMENT si la position n'est pas atteinte.
    L'orientation a un plancher (~16-40 deg, bras sans pronation) : on ne
    juge la sortie que sur la POSITION, sinon on relance des seeds en vain
    alors que le point est deja bon."""
    def score(rp, ro):
        return rp + 1.0 * ro                       # priorite a la position
    bq, bp, bo = ik(tpos, q0)
    if bp < 12:                                    # contact atteint -> fini
        return bq, bp, bo
    for s in ([20, -55, 10, 80, -10, 0],          # bras devant, coude plie
              [0, -45, 20, 60, 0, 0]):
        q, rp, ro = ik(tpos, s)
        if score(rp, ro) < score(bp, bo):
            bq, bp, bo = q, rp, ro
        if bp < 12:
            break
    return bq, bp, bo


def applique(q):
    for (nom, axe, lo, hi), a in zip(ARM, q):
        F[nom].setPose(REST[nom] * ROT[axe](math.radians(a)))


# ---------------- choregraphie : CHEMIN CARTESIEN anti-collision ----------------
# Le probleme des collisions vient de l'interpolation dans l'espace des
# ARTICULATIONS : entre deux poses sans collision, la main peut quand meme
# plonger dans la table en chemin. On pilote donc l'EFFECTEUR (centre main)
# dans l'espace CARTESIEN, le long d'un chemin que l'on route explicitement
# AU-DESSUS de la table. Regle : on ne franchit la zone de la table (en Z)
# qu'a haute altitude (HOME_Y) ; les approches/depots sont VERTICAUX.
cube_y = TABLE_TOP + CUBE / 2.0          # centre du cube
cube_top = cube_y + CUBE / 2.0           # haut du cube
GRASP_Y = cube_top + GRASP_CLEAR         # centre main quand elle tient le cube
mx, mz = (PICK_X + PLACE_X) / 2.0, (PICK_Z + PLACE_Z) / 2.0

q_rest = [0.0] * 6
rest_pos = eff_pos(fk_pose(q_rest))      # main au repos (devant le bassin)
zc = rest_pos[2]                         # Z cote corps, en-deca du bord de table

# chemin de l'effecteur : (label, position monde, evenement)
PATH = [
    ("montee",     (PICK_X, HOME_Y, zc),                 None),     # monter cote corps
    ("survol_pick",(PICK_X, HOME_Y, PICK_Z),             None),     # franchir par le haut
    ("approche",   (PICK_X, GRASP_Y + APPROACH, PICK_Z), None),     # descente
    ("saisie",     (PICK_X, GRASP_Y, PICK_Z),            "grab"),
    ("levee",      (PICK_X, HOME_Y, PICK_Z),             None),     # remontee verticale
    ("transfert",  (mx, HOME_Y, mz),                     "snap2"),  # transit en hauteur
    ("pre_depose", (PLACE_X, HOME_Y, PLACE_Z),           None),
    ("depose",     (PLACE_X, GRASP_Y, PLACE_Z),          "release"),  # descente verticale
    ("degage",     (PLACE_X, HOME_Y, PLACE_Z),           None),     # remontee verticale
    ("survol_back",(PLACE_X, HOME_Y, zc),                None),     # franchir au retour
    ("repos",      rest_pos,                             None),     # revenir au repos
]

SNAP = "--snap" in sys.argv
SNAPDIR = r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\scripts\_debug_reperes"


def snap(name):
    if SNAP:
        RDK.Render(True)
        RDK.Command("Snapshot", SNAPDIR + "\\" + name + ".png")


def cart_seg(p_from, p_to, q, steps=STEPS):
    """Anime l'effecteur en LIGNE DROITE p_from -> p_to (ease-in-out), en
    resolvant l'IK a chaque pas (warm-start = rapide). Calcul et rendu
    entrelaces : le bras bouge tout de suite, pas d'attente prealable."""
    for s in range(1, steps + 1):
        t = s / steps
        t = t * t * (3 - 2 * t)
        tgt = [p_from[i] + (p_to[i] - p_from[i]) * t for i in range(3)]
        q, _, _ = ik(tgt, q, iters=60, patience=8)
        applique(q)
        RDK.Render(True)
        time.sleep(DT)
    return q


print("--- Animation (chemin cartesien, anti-collision table) ---")
station = RDK.ActiveStation()
wrist = F[ARM[-1][0]]
if "--frames" not in sys.argv:                # demo propre : cacher les reperes
    for fr in RDK.ItemList(ITEM_TYPE_FRAME):
        fr.setVisible(False, False)
piece.setParentStatic(station)                # remettre la piece au depart
piece.setPose(transl(PICK_X, cube_y, PICK_Z))
applique(q_rest)
RDK.Render(True)
time.sleep(0.3)

q, cur = q_rest, rest_pos
for label, pos, event in PATH:
    q = cart_seg(cur, pos, q)
    cur = pos
    if event == "grab":
        piece.setParentStatic(wrist)          # la piece suit la main
        print("  piece saisie")
        snap("tache_1_saisie")
    elif event == "snap2":
        snap("tache_2_transfert")
    elif event == "release":
        piece.setParentStatic(station)
        piece.setPose(transl(PLACE_X, cube_y, PLACE_Z))   # posee a plat, a la cible
        print(f"  piece deposee en ({PLACE_X:.0f}, {cube_y:.0f}, {PLACE_Z:.0f})")
        snap("tache_3_depose")
snap("tache_4_final")
print("Fini — piece deplacee de gauche a droite, sans toucher la table.")
