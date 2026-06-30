# -*- coding: utf-8 -*-
"""
Marche_Trajectoire.py — L'operateur marche le long d'une TRAJECTOIRE EXTERNE
(non lineaire), definie par des waypoints dans un fichier JSON.

A LANCER DANS ROBODK (clic droit > Run) depuis la station avec le rig 22 DDL,
operateur au repos / garde-a-vous (le script capture le repos au demarrage).

Principe (demande reunion du 04/06) :
  - la trajectoire est DEFINIE EN EXTERNE : trajectoires\\trajectoire_S.json
    (liste de points [x, z] au sol, en mm) -> modifiable sans toucher au code
  - les waypoints sont lisses par une spline Catmull-Rom -> courbe douce
  - le corps SUIT la courbe par abscisse curviligne : position sur la courbe
    + orientation vers la tangente (il regarde toujours ou il va)
  - meme cycle de marche et meme anti-glisse que Marche_Avant : le corps
    avance a la vitesse des pas (longueur de pas deduite du balancement
    de hanche), donc pas de patinage le long de la courbe
  - la trajectoire est tracee au sol dans la station (courbe bleue)

Usage terminal (RoboDK ouvert) :
    python Marche_Trajectoire.py [chemin\\trajectoire.json] [--reste]
    --reste : ne pas revenir au centre a la fin (rester au bout du chemin)
"""
from robolink import Robolink
from robodk.robomath import rotx, roty, rotz, transl
import bisect
import json
import math
import sys
import time

RDK = Robolink()

# ---- Les 22 DDL : nom -> (axe, limite_basse_deg, limite_haute_deg) ----
DDL = {
    # JAMBE DROITE (5)
    "hipR_abduction": ("z", -45, 30),   "hipR_flexion": ("x", -120, 15),  "hipR_rotation": ("y", -45, 45),
    "kneeR_flexion":  ("x", 0, 135),    "ankleR_flexion": ("x", -30, 50),
    # JAMBE GAUCHE (5)
    "hipL_abduction": ("z", -30, 45),   "hipL_flexion": ("x", -120, 15),  "hipL_rotation": ("y", -45, 45),
    "kneeL_flexion":  ("x", 0, 135),    "ankleL_flexion": ("x", -30, 50),
    # BRAS DROIT (6)
    "shoulderR_abduction": ("z", -135, 90), "shoulderR_flexion": ("x", -90, 90), "shoulderR_rotation": ("y", -45, 180),
    "elbowR_flexion": ("x", 0, 145),
    "wristR_flexion": ("x", -50, 60),   "wristR_deviation": ("z", -30, 20),
    # BRAS GAUCHE (6)
    "shoulderL_abduction": ("z", -90, 135), "shoulderL_flexion": ("x", -90, 90), "shoulderL_rotation": ("y", -45, 180),
    "elbowL_flexion": ("x", 0, 145),
    "wristL_flexion": ("x", -50, 60),   "wristL_deviation": ("z", -30, 20),
}

ROT = {"x": rotx, "y": roty, "z": rotz}
F = {nom: RDK.Item(nom) for nom in DDL}            # les reperes
REST = {nom: F[nom].Pose() for nom in DDL}         # pose de repos (capturee au demarrage)
BASE = RDK.Item("Human_Base")
HOME = transl(0, 958, 0)                           # position d'origine (au centre)
Y0 = BASE.Pose().Pos()[1]                          # hauteur du bassin (958 mm)


def bouge(nom, deg):
    """Tourne un DDL de `deg` degres depuis le repos (borne aux limites)."""
    axe, lo, hi = DDL[nom]
    deg = max(lo, min(hi, deg))
    F[nom].setPose(REST[nom] * ROT[axe](math.radians(deg)))


def neutre():
    """Remet les articulations au repos (le corps reste ou il est)."""
    for nom in DDL:
        F[nom].setPose(REST[nom])


# =======================================================================
# REGLAGES
# =======================================================================
TRAJET_DEFAUT = r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\trajectoires\trajectoire_S.json"
HANCHE_AV = 30    # jambe vers l'avant (deg)
HANCHE_ARR = 12   # jambe vers l'arriere (deg)
GENOU = 50        # pliage du genou pendant le balance (deg)
CHEVILLE = 8      # pointe de pied relevee pendant le balance (deg)
BRAS_AV = 25      # bras vers l'avant (deg)
BRAS_ARR = 15     # bras vers l'arriere (deg)
COUDE = 20        # coude legerement plie
IMAGES_PAR_PAS = 14   # fluidite
DT = 0.04         # pause entre images (s)
TRACER = True     # dessiner la trajectoire au sol dans la station

LONGUEUR_JAMBE = 790.0   # hanche -> cheville (mm)
LONGUEUR_PAS = LONGUEUR_JAMBE * (math.sin(math.radians(HANCHE_AV)) + math.sin(math.radians(HANCHE_ARR)))


# =======================================================================
# Trajectoire : JSON -> spline Catmull-Rom -> abscisse curviligne
# =======================================================================
def charge_waypoints(chemin):
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    pts = [tuple(map(float, p)) for p in data["points_xz_mm"]]
    if len(pts) < 2:
        raise SystemExit("ERREUR : il faut au moins 2 waypoints.")
    return data.get("nom", "(sans nom)"), pts


def _cr(p0, p1, p2, p3, t):
    """Point de Catmull-Rom (uniforme) entre p1 et p2, t dans [0,1]."""
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t
                        + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                        + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)
                 for k in range(2))


def lisse(waypoints, par_segment=24):
    """Spline Catmull-Rom a travers les waypoints -> polyligne dense."""
    P = [waypoints[0]] + list(waypoints) + [waypoints[-1]]
    dense = []
    for i in range(len(waypoints) - 1):
        for j in range(par_segment):
            dense.append(_cr(P[i], P[i + 1], P[i + 2], P[i + 3], j / par_segment))
    dense.append(waypoints[-1])
    return dense


def abscisses(dense):
    """Longueurs cumulees le long de la polyligne."""
    S = [0.0]
    for a, b in zip(dense, dense[1:]):
        S.append(S[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return S


def point_et_tangente(dense, S, s):
    """Position (x,z) + tangente unitaire (tx,tz) a l'abscisse s (mm)."""
    s = max(0.0, min(S[-1], s))
    i = min(max(bisect.bisect_left(S, s), 1), len(S) - 1)
    seg = S[i] - S[i - 1] or 1e-9
    u = (s - S[i - 1]) / seg
    a, b = dense[i - 1], dense[i]
    x = a[0] + u * (b[0] - a[0])
    z = a[1] + u * (b[1] - a[1])
    tx, tz = b[0] - a[0], b[1] - a[1]
    n = math.hypot(tx, tz) or 1e-9
    return (x, z), (tx / n, tz / n)


def tracer_trajectoire(dense):
    """Dessine la courbe au sol dans la station (best effort)."""
    try:
        vieux = RDK.Item("Trajectoire_Marche")
        if vieux.Valid() and vieux.Name() == "Trajectoire_Marche":
            vieux.Delete()
        courbe = RDK.AddCurve([[p[0], 10.0, p[1]] for p in dense])
        if courbe.Valid():
            courbe.setName("Trajectoire_Marche")
            courbe.setColorCurve([0.1, 0.3, 0.9, 1])
    except Exception as e:  # noqa: BLE001
        print("(trace de la trajectoire ignoree : {})".format(e))


# =======================================================================
# Cycle de marche (identique a Marche_Avant)
# =======================================================================
def pose_pas(ph):
    """Pose de marche pour une phase `ph` (radians). Jambe droite devant sur [0, pi]."""
    s = math.sin(ph)
    a = (HANCHE_AV + HANCHE_ARR) / 2.0
    c = (HANCHE_AV - HANCHE_ARR) / 2.0
    bouge("hipR_flexion", -(a * s + c))
    bouge("hipL_flexion", -(a * -s + c))
    bouge("kneeR_flexion", GENOU * max(0.0, math.cos(ph)))
    bouge("kneeL_flexion", GENOU * max(0.0, -math.cos(ph)))
    bouge("ankleR_flexion", -CHEVILLE * max(0.0, math.cos(ph)))
    bouge("ankleL_flexion", -CHEVILLE * max(0.0, -math.cos(ph)))
    sa = (BRAS_AV + BRAS_ARR) / 2.0
    sc = (BRAS_ARR - BRAS_AV) / 2.0
    bouge("shoulderR_flexion", sa * s + sc)
    bouge("shoulderL_flexion", -sa * s + sc)
    bouge("elbowR_flexion", COUDE)
    bouge("elbowL_flexion", COUDE)


def place_corps(dense, S, s):
    """Place le corps a l'abscisse s : position sur la courbe + regard tangent."""
    (x, z), (tx, tz) = point_et_tangente(dense, S, s)
    theta = math.atan2(tx, tz)          # le mannequin regarde vers +Z local
    BASE.setPose(transl(x, Y0, z) * roty(theta))


def marche_trajectoire(dense, S, retour_centre=True):
    """Anime la marche le long de la courbe, du debut a la fin."""
    L = S[-1]
    nb_images = int(math.ceil(L / LONGUEUR_PAS * IMAGES_PAR_PAS))
    for i in range(nb_images + 1):
        ph = math.pi * i / IMAGES_PAR_PAS          # 1 pas = une demi-periode
        s = min(L, LONGUEUR_PAS * ph / math.pi)    # anti-glisse : s = vitesse des pas
        RDK.Render(False)
        pose_pas(ph)
        place_corps(dense, S, s)
        RDK.Render(True)
        time.sleep(DT)
    # fin : repos (oriente comme a l'arrivee)
    RDK.Render(False)
    neutre()
    if retour_centre:
        BASE.setPose(HOME)
    RDK.Render(True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--reste"]
    reste = "--reste" in sys.argv[1:]
    chemin = args[0] if args else TRAJET_DEFAUT

    nom, waypoints = charge_waypoints(chemin)
    dense = lisse(waypoints)
    S = abscisses(dense)
    if TRACER:
        tracer_trajectoire(dense)
    print("Trajectoire '{}' : {} waypoints, {:.1f} m, ~{} pas".format(
        nom, len(waypoints), S[-1] / 1000.0, int(round(S[-1] / LONGUEUR_PAS))))
    marche_trajectoire(dense, S, retour_centre=not reste)
    p = BASE.Pose().Pos()
    print("Arrive ! Position finale Human_Base : x={:.0f} y={:.0f} z={:.0f} (retour_centre={})".format(
        p[0], p[1], p[2], not reste))
