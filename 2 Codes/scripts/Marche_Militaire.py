# -*- coding: utf-8 -*-
"""
Marche_Militaire.py — L'operateur marque le pas (marche militaire sur place).

A LANCER DANS ROBODK (clic droit > Run) depuis la station avec le rig 22 DDL,
operateur en pose NEUTRE (le script capture le repos au demarrage).

Principe de la marche militaire :
  - genoux qui montent haut, alternes
  - bras RAIDES (coude quasi tendu) qui balancent en OPPOSITION des jambes
  - buste droit (il est fige, parfait pour un militaire)

Regle les amplitudes/vitesse dans la section REGLAGES.
"""
from robolink import Robolink
from robodk.robomath import rotx, roty, rotz
import math
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
REST = {nom: F[nom].Pose() for nom in DDL}         # pose neutre (capturee au demarrage)


def bouge(nom, deg):
    """Tourne un DDL de `deg` degres depuis le repos (borne aux limites)."""
    axe, lo, hi = DDL[nom]
    deg = max(lo, min(hi, deg))
    F[nom].setPose(REST[nom] * ROT[axe](math.radians(deg)))


def neutre():
    """Remet tout l'operateur droit."""
    for nom in DDL:
        F[nom].setPose(REST[nom])


# =======================================================================
# REGLAGES de la marche militaire
# =======================================================================
HANCHE = 55      # levee de cuisse (deg) — genou haut
GENOU = 65       # pliage du genou quand la jambe monte (deg)
CHEVILLE = 15    # pointe de pied quand la jambe est levee (deg)
BRAS_AV = -45    # bras vers l'AVANT (deg, negatif = devant)
BRAS_ARR = 20    # bras vers l'ARRIERE (deg)
COUDE = 8        # coude quasi tendu = bras raide militaire
NB_PAS = 8       # nombre de pas au total
IMAGES_PAR_PAS = 12   # fluidite (images par pas)
DT = 0.04        # pause entre images (s) — plus petit = plus rapide


def pose_marche(ph):
    """Pose complete de la marche pour une phase `ph` (radians).
       Jambe droite levee sur [0, pi], jambe gauche sur [pi, 2pi]."""
    s = math.sin(ph)
    lift_d = max(0.0, s)     # jambe droite qui monte
    lift_g = max(0.0, -s)    # jambe gauche qui monte

    # jambes : genou haut + pointe de pied
    bouge("hipR_flexion", -HANCHE * lift_d)
    bouge("kneeR_flexion", GENOU * lift_d)
    bouge("ankleR_flexion", CHEVILLE * lift_d)
    bouge("hipL_flexion", -HANCHE * lift_g)
    bouge("kneeL_flexion", GENOU * lift_g)
    bouge("ankleL_flexion", CHEVILLE * lift_g)

    # bras raides, en opposition : bras droit devant quand jambe gauche monte
    u_d = (1.0 - s) / 2.0    # 0 = bras D derriere, 1 = bras D devant
    u_g = (1.0 + s) / 2.0
    bouge("shoulderR_flexion", BRAS_ARR + (BRAS_AV - BRAS_ARR) * u_d)
    bouge("shoulderL_flexion", BRAS_ARR + (BRAS_AV - BRAS_ARR) * u_g)
    bouge("elbowR_flexion", COUDE)
    bouge("elbowL_flexion", COUDE)


def marche(nb_pas=NB_PAS, images_par_pas=IMAGES_PAR_PAS, dt=DT):
    """Anime la marche militaire sur place."""
    for i in range(nb_pas * images_par_pas + 1):
        ph = math.pi * i / images_par_pas      # 1 pas = une demi-periode
        RDK.Render(False)
        pose_marche(ph)
        RDK.Render(True)
        time.sleep(dt)
    neutre()
    RDK.Render(True)


if __name__ == "__main__":
    print("Marche militaire : {} pas...".format(NB_PAS))
    marche()
    print("Repos !")
