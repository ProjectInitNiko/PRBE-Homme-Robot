# -*- coding: utf-8 -*-
"""
Tache_Bras.py — v3 (refonte complete, 11/06) : pick & place d'une piece
cubique sur une table, bras gauche 6 DDL, corps fixe.

Scenario :
  Le mannequin est debout devant une table. Une piece cubique est posee
  pres du BORD AVANT de la table, a sa GAUCHE. Il la saisit de la main
  gauche, la deplace vers la DROITE et la repose sur la meme table.

REGLES v3 (retours Niko 11/06, "reprendre a zero") :

  1. LE COUDE PART EN ARRIERE, JAMAIS EN AVANT. La position du coude ne
     depend que de l'epaule ; sur ce rig la flexion d'epaule POSITIVE le
     tire en arriere (sonde _probe_coude : flexion +10 => coude Z 41->7).
     La flexion est donc BORNEE a [-8, +25] pour TOUT le scenario : le
     bras ne bascule jamais vers l'avant, la main avance par le pli du
     coude. Consequence geometrique : la piece doit etre pres du bord
     avant de la table (Z=300 et non 400 — a 400 il FAUT avancer le
     coude, c'est ce qui pourrissait la v2). Verification integree :
     le Z du coude est scanne sur TOUTE la trajectoire precalculee.

  2. MOUVEMENT DYNAMIQUE. La lenteur de la v2 venait de l'IK calculee A
     CHAQUE FRAME pendant l'animation (~400 appels FK par image). La v3
     PRECALCULE toute la trajectoire articulaire (IK seulement sur les
     postures cles, hors animation), puis la JOUE a cadence fixe : zero
     calcul pendant la lecture, vitesses articulaires ~80-140 deg/s
     (rythme humain), profil doux (smoothstep) par phase, micro-pauses
     saisie/depose.

A LANCER : RoboDK ouvert, station avec le rig 22 DDL.
    C:\\RoboDK\\Python-Embedded\\python.exe scripts\\Tache_Bras.py
    options : --check (precalcul + verifs seulement, pas d'animation)
              --frames (laisser les reperes visibles)

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
TABLE_CZ = 485           # centre du plateau devant le mannequin (Z)
CUBE = 80                # arete de la piece cubique
PICK_X, PICK_Z = 330, 300        # piece au depart : a GAUCHE, pres du bord
PLACE_X, PLACE_Z = 80, 300       # depose : 25 cm vers la DROITE, meme bord
                                 # (bord avant : seule zone atteignable
                                 # avec le coude qui reste en ARRIERE)
GRASP_CLEAR = 35         # centre de la main au-dessus du haut du cube (saisie)
HI = 1030                # hauteur de transit (centre paume) : plafond
                         # atteignable coude en arriere. Cube et doigts a
                         # paume-115 = 915, soit ~15 mm au-dessus du
                         # plateau : la piece GLISSE juste au-dessus de la
                         # table — le geste humain pour 25 cm de deport
                         # (on ne souleve pas a 15 cm), valide au mesh
TRANSIT_Z = 280          # transit legerement RAMENE vers le corps (geste
                         # humain : on porte pres de soi) — et plus
                         # atteignable que Z=300 a cette hauteur
DT = 0.025               # cadence de lecture (s/frame) — la trajectoire est
                         # precalculee, la lecture ne fait QUE appliquer+rendre

# ---------------- bras gauche : DDL, axes, limites (deg) ----------------
ARM = [
    ("shoulderL_abduction", "z", -90, 135),
    ("shoulderL_flexion",   "x", -120, 90),
    ("shoulderL_rotation",  "y", -45, 180),
    ("elbowL_flexion",      "x", -145, 0),    # NEGATIF = plier vers l'AVANT
    ("wristL_flexion",      "x", -50, 60),
    ("wristL_deviation",    "z", -30, 20),
]
ROT = {"x": rotx, "y": roty, "z": rotz}

# Bornes du scenario. LA contrainte v3 est la FLEXION D'EPAULE >= -8 :
# le bras ne bascule jamais en avant => le coude ne part jamais en avant
# (verifie en plus par le scan coude sur la trajectoire complete).
# Vers l'ARRIERE en revanche on autorise large (+38, extension humaine
# ~45-60) : c'est ce qui donne la hauteur de transit coude recule.
LIM_SCEN = [(-45, 25), (-8, 38), (-45, 60), (-130, 0), (-40, 55), (-25, 20)]

# ORIENTATION DE LA MAIN : le bras n'a pas de pronation d'avant-bras, on
# garde la main dans son orientation de repos (verticale, doigts vers le
# bas) = identite du repere poignet. Stricte quand la main PORTE la piece,
# souple a main vide.
R_GRASP = Mat([[1.0, 0.0, 0.0, 0.0],
               [0.0, 1.0, 0.0, 0.0],
               [0.0, 0.0, 1.0, 0.0],
               [0.0, 0.0, 0.0, 1.0]])
WO = 65.0           # poids orientation stricte (mm equivalents par radian)
WO_LIBRE = 22.0     # orientation souple (main vide)
LAM = 5.0           # amortissement DLS

# Posture de confort (tache secondaire de l'IK) : selectionne la branche
# "coude en arriere" — epaule legerement en extension, coude plie.
Q_CONF = [0.0, 12.0, 15.0, -80.0, 0.0, 0.0]
WQ = 1.2

RDK = Robolink()
print("Station :", RDK.ActiveStation().Name())

# Remise a zero AVANT de capturer le repos (sinon les residus d'une
# animation precedente corrompent tout le modele FK).
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
    """Pose absolue (Mat 4x4) du repere POIGNET pour les 6 angles q (deg)."""
    P = ROOT
    for (nom, axe, lo, hi), a in zip(ARM, q):
        P = P * REST[nom] * ROT[axe](math.radians(a))
    return P


def fk_coude(q):
    """Position absolue du repere COUDE (ne depend que des 3 DDL epaule)."""
    P = ROOT
    for (nom, axe, lo, hi), a in zip(ARM[:3], q[:3]):
        P = P * REST[nom] * ROT[axe](math.radians(a))
    P = P * REST["elbowL_flexion"]
    r = P.rows
    return [r[0][3], r[1][3], r[2][3]]


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
    """Erreur d'orientation (vecteur monde, ~rad) menant Rc -> Rd."""
    e = [0.0, 0.0, 0.0]
    for k in range(3):
        c = cross(Rc[k], Rd[k])
        e = [e[i] + c[i] for i in range(3)]
    return [0.5 * v for v in e]


RG = cols(R_GRASP)


def clamp(q):
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


def ik(tpos, q0, tol_p=6.0, tol_o=0.09, iters=240, patience=22, wo=WO):
    """IK 6 DOF position + orientation, DLS amortie, posture secondaire
    Q_CONF (branche coude en arriere). Bornee par LIM_SCEN => la flexion
    d'epaule ne peut JAMAIS depasser +25/-8 : le coude reste en arriere
    par construction. Retourne (q, residu_pos_mm, residu_ori_deg)."""
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
        s = np_ + wo * no_
        if s < best_s - 0.05:
            best_s, best_q, stale = s, q[:], 0
        else:
            stale += 1
        if np_ < tol_p and no_ < tol_o:
            return q, np_, math.degrees(no_)
        if stale >= patience:
            break
        x = ep + [wo * v for v in eo]
        # Jacobien 6x6 par differences finies
        J = [[0.0] * 6 for _ in range(6)]
        for j in range(6):
            dq = list(q)
            dq[j] += 0.5
            Pj = fk_pose(dq)
            pj = eff_pos(Pj)
            dphi = ori_err(Rc, cols(Pj))
            for i in range(3):
                J[i][j] = (pj[i] - p[i]) / 0.5
                J[3 + i][j] = wo * dphi[i] / 0.5
        # DLS + tache posturale secondaire (s'estompe pres de la cible)
        wq2 = (WQ * min(1.0, np_ / 60.0)) ** 2
        reg = LAM * LAM + wq2
        JTJ = [[sum(J[k][i] * J[k][r] for k in range(6)) + (reg if i == r else 0)
                for r in range(6)] for i in range(6)]
        b = [sum(J[k][j] * x[k] for k in range(6)) + wq2 * (Q_CONF[j] - q[j])
             for j in range(6)]
        dq = _solve6(JTJ, b)
        # rebroussement si le pas complet empire le score
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
    P = fk_pose(best_q)
    rp = math.sqrt(sum((tpos[i] - eff_pos(P)[i])**2 for i in range(3)))
    ro = math.degrees(math.sqrt(sum(v*v for v in ori_err(cols(P), RG))))
    return best_q, rp, ro


def applique(q):
    for (nom, axe, lo, hi), a in zip(ARM, q):
        F[nom].setPose(REST[nom] * ROT[axe](math.radians(a)))


# ---------------- choregraphie v3 : cles -> trajectoire precalculee ------
cube_y = TABLE_TOP + CUBE / 2.0          # centre du cube
GRASP_Y = cube_y + CUBE / 2.0 + GRASP_CLEAR   # centre main, cube en main

q_rest = [0.0] * 6

# Cles FK de la MONTEE : le coude PART EN ARRIERE (flexion epaule
# positive) pendant que le pli du coude monte la main devant la poitrine.
# L'epaule part FRANCHEMENT en extension (+34/+36) des l'amorce : pendant
# le pli, l'arc de l'avant-bras balaie vers l'avant, et la face avant de
# la table n'est qu'a 50 mm de la main au repos — epaule a +14 ca frotte
# (17 collisions mesh), a +34 ca passe (0, banc _tune_keys). La descente
# du retour reutilise ces cles en miroir.
QK_A = [-6.0, 34.0, 5.0, -30.0, -30.0, 0.0]    # amorce : epaule bien ARRIERE
QK_B = [-12.0, 36.0, 10.0, -95.0, -35.0, 0.0]  # main haute pres du corps

# Cibles cartesiennes (resolues en cles articulaires par IK, HORS animation)
P_PREPICK = (PICK_X, GRASP_Y + 35, PICK_Z - 10)
P_PICK = (PICK_X, GRASP_Y, PICK_Z)
P_HI_PICK = (PICK_X, HI, TRANSIT_Z)
P_HI_MID = ((PICK_X + PLACE_X) / 2.0, HI, TRANSIT_Z)
P_HI_PLACE = (PLACE_X, HI, TRANSIT_Z)
P_PLACE = (PLACE_X, GRASP_Y, PLACE_Z)

# phases : (label, vitesse deg/frame, pause_s, evenement_de_fin)
# Les cles de chaque phase sont resolues dans build_trajectoire().
# Le rendu RoboDK coute ~80 ms/frame (mesure 11/06) : c'est LUI la cadence
# reelle, pas DT. Les pas sont donc dimensionnes pour un geste dynamique a
# ~12 fps rendus : 6 deg/frame ~ 70 deg/s effectifs sur les grands gestes.
V_VIF = 6.0      # deg max/frame pour les grands gestes
V_FIN = 3.0      # approche / depose : plus pose


def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def catmull(pts, u):
    """Point sur la spline Catmull-Rom 6D passant par pts (u dans [0,1],
    parametrisation par longueur de corde). 2 points = segment droit."""
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


def _resample(keys, v_frame):
    """Echantillonne la spline articulaire passant par keys en frames a
    vitesse bornee : nombre de frames dimensionne sur le plus grand ecart
    articulaire, profil smoothstep (doux au depart et a l'arrivee)."""
    span = 0.0
    for a, b in zip(keys, keys[1:]):
        span += max(abs(x - y) for x, y in zip(a, b))
    n = max(4, int(math.ceil(span / v_frame)))
    out = []
    for s in range(1, n + 1):
        t = s / n
        t = t * t * (3 - 2 * t)                  # smoothstep
        out.append(clamp(catmull(keys, t)))
    return out


def build_trajectoire():
    """Resout toutes les cles (IK hors animation) puis precalcule TOUTES
    les frames. Retourne (frames, events, rapport) avec
    frames = [q, ...], events = {index_frame: nom}, et un rapport texte
    (residus IK + scan coude)."""
    rapport = []

    def cle_ik(nom, cible, q_seed, wo):
        q, rp, ro = ik(cible, q_seed, wo=wo)
        rapport.append(f"  cle {nom:<10} residu {rp:5.1f} mm / {ro:5.1f} deg")
        if rp > 14:
            rapport.append(f"    !! {nom} : cible mal atteinte ({rp:.0f} mm)")
        return q

    # pick d'abord (seed = cle FK de la montee), puis prepick ANCRE sur la
    # branche de pick (meme poids d'orientation) : sans ca, l'approche
    # lente traversait un saut de branche (poignet -16 -> +50 deg).
    q_pick = cle_ik("pick", P_PICK, QK_B, WO)
    q_prepick = cle_ik("prepick", P_PREPICK, q_pick, WO)
    q_hi1 = cle_ik("hi_pick", P_HI_PICK, q_pick, WO)
    q_him = cle_ik("hi_mid", P_HI_MID, q_hi1, WO)
    q_hi2 = cle_ik("hi_place", P_HI_PLACE, q_him, WO)
    q_place = cle_ik("place", P_PLACE, q_hi2, WO)

    phases = [
        ("tendre", [q_rest, QK_A, QK_B, q_prepick], V_VIF, 0.0, None),
        ("saisir", [q_prepick, q_pick], V_FIN, 0.30, "grab"),
        ("transporter", [q_pick, q_hi1, q_him, q_hi2], V_VIF, 0.0, None),
        ("deposer", [q_hi2, q_place], V_FIN, 0.30, "release"),
        ("ramener", [q_place, q_hi2, QK_B, QK_A, q_rest], V_VIF, 0.0, None),
    ]

    frames, events, pauses = [], {}, {}
    for label, keys, v, pause, event in phases:
        fr = _resample(keys, v)
        frames += fr
        if event:
            events[len(frames) - 1] = event
        if pause:
            pauses[len(frames) - 1] = pause
        rapport.append(f"  phase {label:<12} {len(fr):3d} frames")

    # SCAN COUDE : garantie "jamais en avant" sur la trajectoire COMPLETE
    z0 = fk_coude(q_rest)[2]
    zmax, imax = -1e9, 0
    for i, q in enumerate(frames):
        z = fk_coude(q)[2]
        if z > zmax:
            zmax, imax = z, i
    ok = zmax <= z0 + 5.0
    rapport.append(f"  coude : Z repos {z0:.0f} mm, Z max trajectoire "
                   f"{zmax:.0f} mm (frame {imax}) -> "
                   f"{'OK, jamais en avant' if ok else '!! PART EN AVANT'}")
    return frames, events, pauses, rapport, ok


def main():
    print("--- Tache bras v3 : coude en arriere, trajectoire precalculee ---")
    t0 = time.time()
    frames, events, pauses, rapport, coude_ok = build_trajectoire()
    print("\n".join(rapport))
    print(f"Precalcul : {len(frames)} frames en {time.time() - t0:.1f} s "
          f"(~{len(frames) * DT + sum(pauses.values()):.1f} s d'animation)")
    if not coude_ok:
        sys.exit("ABANDON : le coude partirait en avant — cles a corriger.")
    if "--check" in sys.argv:
        print("--check : pas d'animation.")
        return

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

    # LECTURE : zero calcul, cadence reelle tenue sur l'horloge murale
    # (si le rendu prend du retard, on saute le sleep, pas des frames).
    t0 = time.time()
    for i, q in enumerate(frames):
        applique(q)
        RDK.Render(True)
        ev = events.get(i)
        if ev == "grab":
            piece.setParentStatic(wrist)      # la piece suit la main
            print("  piece saisie")
        elif ev == "release":
            piece.setParentStatic(station)
            piece.setPose(transl(PLACE_X, cube_y, PLACE_Z))
            print(f"  piece deposee en ({PLACE_X:.0f}, {cube_y:.0f}, {PLACE_Z:.0f})")
        if i in pauses:
            time.sleep(pauses[i])
            t0 += pauses[i]
        reste = t0 + (i + 1) * DT - time.time()
        if reste > 0:
            time.sleep(reste)
    print(f"Fini en {time.time() - t0:.1f} s - piece deplacee de gauche a "
          f"droite, coude toujours en arriere.")


if __name__ == "__main__":
    main()
