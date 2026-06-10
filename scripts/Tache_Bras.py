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
# version embarquee dans la station : __file__ pointe vers un dossier temp,
# il faut le chemin absolu du repo pour trouver Position_0
sys.path.insert(0, r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\scripts")
from robolink import Robolink, ITEM_TYPE_FRAME
from robodk.robomath import Mat, transl, rotx, roty, rotz, invH

# ---------------- parametres de la scene (mm) ----------------
TABLE_TOP = 900          # hauteur de la surface de la table
TABLE_SX, TABLE_SZ = 1100, 550   # plateau : largeur (X) x profondeur (Z)
TABLE_TH = 40            # epaisseur plateau
TABLE_CZ = 485           # centre du plateau devant le mannequin (Z).
                         # 485 et pas 455 : a 455 la face avant (Z=180) touche
                         # la main au garde-a-vous (collision mesh au repos).
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
    ("shoulderL_flexion",   "x", -120, 90),   # flexion humaine reelle : 180
    ("shoulderL_rotation",  "y", -45, 180),
    ("elbowL_flexion",      "x",   0, 145),
    ("wristL_flexion",      "x", -50, 60),
    ("wristL_deviation",    "z", -30, 20),
]
ROT = {"x": rotx, "y": roty, "z": rotz}

# bornes du scenario (incluses dans les limites humaines).
# Flexion epaule jusqu'a -120 (30 deg au-dessus de l'horizontale) : sans
# ca, lever la main pres du corps pour franchir le bord de table est
# inatteignable et l'IK se contorsionne.
LIM_SCEN = [(-45, 60), (-120, 20), (-45, 45), (0, 130), (-40, 50), (-25, 20)]

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

# POSTURE DE CONFORT — l'IK seule a plusieurs "branches" de solutions et,
# sans preference, elle tombe dans des poses contorsionnees (bras croise
# devant le corps, coude a fond, poignets aux butees = le mouvement
# "n'importe quoi"). La posture est integree comme TACHE SECONDAIRE dans
# les moindres carres amortis (poids WQ << tache principale) : elle
# selectionne la branche naturelle (epaule ecartee a gauche, coude mi-plie,
# poignet neutre) et eloigne des butees, sans voler la cible a l'IK.
Q_CONF = [30.0, -60.0, 30.0, 50.0, 10.0, 0.0]
# Posture "main pres du corps" pour MONTER/DESCENDRE le long du corps :
# coude bien PLIE (le geste humain : on remonte la main pres de la poitrine
# puis on etend le bras). Sans ce guide, l'IK reste sur la branche coude
# mi-plie / epaule vrillee -> coude qui semble se plier a l'envers + blocage
# au franchissement du bord de table.
Q_FOLD = [25.0, -95.0, 35.0, 105.0, -10.0, 0.0]
WQ = 1.2            # poids posture (via WQ^2) — assez pour departager les
                    # branches, assez faible pour ~2 mm de biais a l'equilibre

RDK = Robolink()
print("Station :", RDK.ActiveStation().Name())

# REMISE A ZERO systematique avant de capturer le repos : le script fait
# confiance a l'etat courant du mannequin (REST = poses au demarrage) ; si
# une animation precedente a ete interrompue bras en l'air, tout le modele
# FK serait corrompu. Position_0 garantit le garde-a-vous exact.
from Position_0 import remettre_a_zero
remettre_a_zero(RDK, verbose=False)
print("Mannequin remis a zero (garde-a-vous).")


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


def ik(tpos, q0, tol_p=6.0, tol_o=0.09, iters=240, patience=22, wo=WO,
       qconf=None):
    """IK 6 DOF position + orientation, DLS amortie. S'arrete des que la
    cible est atteinte OU que le residu stagne (patience) — indispensable
    pour ne pas mouliner 500 iterations sur un point hors d'atteinte.
    wo = poids d'orientation : strict (WO) quand la main porte la piece,
    souple a main vide (la main peut s'incliner, comme un humain).
    qconf = posture de confort guidant le choix de branche (Q_CONF, ou
    Q_FOLD pour les phases pres du corps).
    Retourne (q, residu_pos_mm, residu_ori_deg)."""
    qc = Q_CONF if qconf is None else qconf
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
        s = np_ + wo * no_                       # score combine
        if s < best_s - 0.05:                    # progres (meme fin)
            best_s, best_q, stale = s, q[:], 0
        else:
            stale += 1
        if np_ < tol_p and no_ < tol_o:
            return q, np_, math.degrees(no_)
        if stale >= patience:                    # plus de progres -> stop
            break
        x = ep + [wo * v for v in eo]            # tache 6D (pos mm ; ori ponderee)
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
                J[3 + i][j] = wo * dphi[i] / 0.5
        # DLS en equations normales, avec tache posturale secondaire :
        # (J^T J + (LAM^2 + wq2) I) dq = J^T x + wq2 (Q_CONF - q)
        # Le poids postural S'ESTOMPE avec le residu : il departage les
        # branches LOIN de la cible, puis s'efface (sinon il vole les
        # derniers millimetres a la tache).
        wq2 = (WQ * min(1.0, np_ / 60.0)) ** 2
        reg = LAM * LAM + wq2
        JTJ = [[sum(J[k][i] * J[k][r] for k in range(6)) + (reg if i == r else 0)
                for r in range(6)] for i in range(6)]
        b = [sum(J[k][j] * x[k] for k in range(6)) + wq2 * (qc[j] - q[j])
             for j in range(6)]
        dq = _solve6(JTJ, b)
        # rebroussement : si le pas complet EMPIRE le score (overshoot,
        # frequent pres du zero exact ou des butees), on le reduit de
        # moitie — sinon l'IK oscille sur place et le critere de
        # stagnation conclut a tort "bloque".
        scale, q_try = 1.0, None
        for _ in range(3):
            q_try = clamp([q[j] + scale * dq[j] for j in range(6)])
            Pt = fk_pose(q_try)
            ept = [tpos[i] - eff_pos(Pt)[i] for i in range(3)]
            eot = ori_err(cols(Pt), RG)
            st = math.sqrt(sum(v*v for v in ept)) + wo * math.sqrt(sum(v*v for v in eot))
            if st < s:
                break
            scale *= 0.5
        q = q_try
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
    for s in ([45, -85, 45, 40, 35, 5],           # bras leve au-dessus de la table
              [30, -60, 30, 50, 10, 0]):          # prehension naturelle
        q, rp, ro = ik(tpos, s)
        if score(rp, ro) < score(bp, bo):
            bq, bp, bo = q, rp, ro
        if bp < 12:
            break
    return bq, bp, bo


def applique(q):
    for (nom, axe, lo, hi), a in zip(ARM, q):
        F[nom].setPose(REST[nom] * ROT[axe](math.radians(a)))


# ---------------- choregraphie : SPLINE CARTESIENNE fluide ----------------
# v2 "mouvement humain". Les recettes (diagnostics _diag_points/_diag_bord) :
#   1. CHEMIN par via-points VALIDES atteignables (l'ancien transit haut
#      colle au corps etait hors d'atteinte -> l'IK se contorsionnait) ;
#   2. SPLINE Catmull-Rom au lieu de segments en creneau : pas d'arrets
#      nets a chaque coin, la main suit une courbe continue ;
#   3. ORIENTATION par phase : stricte quand la main PORTE la piece,
#      souple a main vide (un humain laisse la main s'incliner en chemin —
#      et ca etend l'atteignabilite au-dessus du bord de table) ;
#   4. VITESSE ARTICULAIRE BORNEE (DQ_MAX) : aucun saut de configuration ;
#   5. profil en cloche par phase + micro-pauses a la saisie / depose.
# Collision table : on ne survole le plateau (Z > 180) que paume >= 1025
# (doigts ~115 mm sous la paume -> ils passent au-dessus des 900 mm).
cube_y = TABLE_TOP + CUBE / 2.0          # centre du cube
cube_top = cube_y + CUBE / 2.0           # haut du cube
GRASP_Y = cube_top + GRASP_CLEAR         # centre main quand elle tient le cube

q_rest = [0.0] * 6
rest_pos = eff_pos(fk_pose(q_rest))      # main au repos (devant le bassin)

HI = 1085                                # plafond de transit valide (IK ~2-9 mm)
WO_LIBRE = 22.0                          # orientation souple (main vide)
DQ_MAX = 8.0                             # deg max par pas d'animation
P_REST = tuple(rest_pos)
P_GRASP = (PICK_X, GRASP_Y, PICK_Z)
P_PLACE = (PLACE_X, GRASP_Y, PLACE_Z)

# --- phase "tendre" en ESPACE ARTICULAIRE --------------------------------
# Suivre une cible cartesienne pendant que le bras se reconfigure en grand
# (bras pendant -> etendu au-dessus de la table) fait balayer la main
# n'importe ou en chemin : l'IK instantanee et la pose appliquee (vitesse
# bornee) divergent. Pour ce geste a main vide on interpole donc entre des
# POSTURES CLES choisies A LA MAIN (FK pure, banc d'essai _probe_poses,
# validees visuellement en vue de cote par snapshots) :
#   - coude <= 100 deg et main DEVANT le coude (l'IK seule produisait des
#     clefs coude 120-130 / epaule levee = "aile de poulet", defaut releve
#     par Niko en vue de cote) ;
#   - poignet flechi ~50 deg en franchissant le bord (doigts recourbes
#     vers l'avant -> extension verticale reduite, ca passe au-dessus du
#     plateau ; verifie par collision MESH RoboDK, pas par approximation).
QK_TEND = [
    list(q_rest),                       # garde-a-vous
    [18, -60, 28, 75, 15, 6],           # la main monte pres du corps
    [25, -75, 30, 95, 48, 8],           # mi-hauteur, doigts recourbes,
                                        # main RETRACTEE (Zmax ~210 < face)
    [28, -98, 20, 110, 45, 10],         # haut, toujours retractee
                                        # (main Ymin 923 > plateau, bbox mesh)
    [34, -98, 38, 95, -30, 10],         # s'allonge au-dessus du plateau
                                        # (poignet passe en extension, Ymin 961)
    [33, -90, 37, 60, 20, 10],          # pres de la piece, le poignet revient
]
P_TEND_FIN = eff_pos(fk_pose(QK_TEND[-1]))   # ou la derniere clef pose la main

# Franchissement du bord de table (face avant a Z=180) : on MONTE d'abord
# pres du corps coude PLIE, et on ne pousse vers l'avant qu'une fois la
# paume au-dessus de ~1040 (doigts > 925 > plateau 900).
# phases : (label, mode, donnees, poids ori, posture, pas, pause_s, evenement)
#   mode "joint" : donnees = postures cles (interpolation articulaire)
#   mode "cart"  : donnees = via-points cartesiens (IK par pas)
PHASES = [
    ("tendre", "joint", QK_TEND, WO_LIBRE, Q_FOLD, 40, 0.0, None),
    ("saisir", "cart",                               # glisse sur la piece, lent
     [P_TEND_FIN, (PICK_X, GRASP_Y + 18, PICK_Z + 8), P_GRASP],
     WO, Q_CONF, 14, 0.35, "grab"),
    ("transporter", "cart",                          # arc au-dessus de la table
     [P_GRASP, (PICK_X, HI, PICK_Z), ((PICK_X + PLACE_X) / 2.0, HI + 5, PICK_Z),
      (PLACE_X, HI, PLACE_Z)],
     WO, Q_CONF, 30, 0.0, "snap2"),
    ("deposer", "cart",                              # descente verticale, lente
     [(PLACE_X, HI, PLACE_Z), (PLACE_X, GRASP_Y + 10, PLACE_Z), P_PLACE],
     WO, Q_CONF, 12, 0.35, "release"),
    ("degager", "cart",                              # remonter main encore droite
     [P_PLACE, (PLACE_X, HI, PLACE_Z)],
     WO, Q_CONF, 10, 0.0, None),
    ("ramener", "cart",                              # revenir haut, puis
     [(PLACE_X, HI, PLACE_Z), (140, 1055, 290),      # redescendre pres du corps
      (150, 1045, 185), (150, 1020, 135), (160, 920, 115), P_REST],
     WO_LIBRE, Q_FOLD, 52, 0.0, None),
]

SNAP = "--snap" in sys.argv
SNAPDIR = r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\scripts\_debug_reperes"


def snap(name):
    if SNAP:
        RDK.Render(True)
        RDK.Command("Snapshot", SNAPDIR + "\\" + name + ".png")


def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def catmull(pts, u):
    """Point sur la spline Catmull-Rom passant par pts (u dans [0, 1],
    parametrisation par longueur de corde — vitesse homogene le long du
    chemin). Marche en dimension quelconque (3D cartesien ou 6D
    articulaire). 2 points = segment droit."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    L = [_dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(L) or 1.0
    s = u * tot
    i = 0
    while i < len(L) - 1 and s > L[i]:
        s -= L[i]
        i += 1
    t = s / (L[i] or 1.0)
    p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
    return [0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t
                   + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                   + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3)
            for k in range(len(pts[0]))]


def anim_phase(label, mode, data, q, wo=WO, qconf=None, steps=26, pause=0.0):
    """Anime une phase. mode "cart" : spline cartesienne suivie par IK
    warm-start. mode "joint" : interpolation articulaire entre postures
    cles. Dans les deux cas la pose appliquee est a VITESSE ARTICULAIRE
    BORNEE (DQ_MAX deg/pas) -> fluidite garantie."""
    for s in range(1, steps + 1):
        t = s / steps
        t = t * t * (3 - 2 * t)                  # cloche : doux aux extremites
        if mode == "joint":
            qs = catmull(data, t)
        else:
            tgt = catmull(data, t)
            qs, _, _ = ik(tgt, q, iters=60, patience=8, wo=wo, qconf=qconf)
        q = [a + max(-DQ_MAX, min(DQ_MAX, b - a)) for a, b in zip(q, qs)]
        applique(q)
        RDK.Render(True)
        if SNAP and s in (steps // 3, 2 * steps // 3):
            snap(f"ph_{label}_{s:02d}")
        time.sleep(DT)
    if pause:
        time.sleep(pause)
    return q


def main():
    print("--- Animation v2 (spline fluide, posture naturelle) ---")
    station = RDK.ActiveStation()
    wrist = F[ARM[-1][0]]
    if "--frames" not in sys.argv:            # demo propre : cacher les reperes
        for fr in RDK.ItemList(ITEM_TYPE_FRAME):
            fr.setVisible(False, False)
    piece.setParentStatic(station)            # remettre la piece au depart
    piece.setPose(transl(PICK_X, cube_y, PICK_Z))
    applique(q_rest)
    RDK.Render(True)
    time.sleep(0.3)

    q = q_rest
    for label, mode, data, wo, qconf, steps, pause, event in PHASES:
        q = anim_phase(label, mode, data, q, wo=wo, qconf=qconf,
                       steps=steps, pause=pause)
        if event == "grab":
            piece.setParentStatic(wrist)      # la piece suit la main
            print("  piece saisie")
            snap("tache_1_saisie")
        elif event == "snap2":
            snap("tache_2_transfert")
        elif event == "release":
            piece.setParentStatic(station)
            piece.setPose(transl(PLACE_X, cube_y, PLACE_Z))   # posee a plat
            print(f"  piece deposee en ({PLACE_X:.0f}, {cube_y:.0f}, {PLACE_Z:.0f})")
            snap("tache_3_depose")
    snap("tache_4_final")
    print("Fini — piece deplacee de gauche a droite, sans toucher la table.")


if __name__ == "__main__":
    main()
