# -*- coding: utf-8 -*-
"""
Marche_Avant.py — L'operateur marche TOUT DROIT devant lui (marche naturelle).

A LANCER DANS ROBODK (clic droit > Run) depuis la station avec le rig 22 DDL,
operateur au repos / garde-a-vous (le script capture le repos au demarrage).

Principe :
  - hanches qui balancent avant/arriere, genou qui se plie pendant le balance
  - bras souples en opposition des jambes (coude legerement plie)
  - le CORPS AVANCE a la vitesse des pas (longueur de pas calculee depuis
    l'amplitude de hanche) -> pas de glisse visible
  - il marche vers SON regard (+Z monde). A la fin, il REVIENT au centre
    (position d'origine de Human_Base).

Regle les amplitudes/vitesse dans la section REGLAGES.
"""
from robolink import Robolink
from robodk.robomath import rotx, roty, rotz, transl
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
REST = {nom: F[nom].Pose() for nom in DDL}         # pose de repos (capturee au demarrage)
BASE = RDK.Item("Human_Base")
BASE_REST = BASE.Pose()                            # position de depart du corps
HOME = transl(0, 958, 0)                           # position d'origine (au centre, 1er repere)


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
# REGLAGES de la marche
# =======================================================================
HANCHE_AV = 30    # jambe vers l'avant (deg)
HANCHE_ARR = 12   # jambe vers l'arriere (deg)
GENOU = 50        # pliage du genou pendant le balance (deg)
CHEVILLE = 8      # pointe de pied relevee pendant le balance (deg)
BRAS_AV = 25      # bras vers l'avant (deg)
BRAS_ARR = 15     # bras vers l'arriere (deg)
COUDE = 20        # coude legerement plie (marche naturelle)
NB_PAS = 8        # nombre de pas
IMAGES_PAR_PAS = 14   # fluidite
DT = 0.04         # pause entre images (s)

LONGUEUR_JAMBE = 790.0   # hanche -> cheville (mm, mesure sur le modele)
SENS = +1                # +1 = devant lui (+Z monde). Mets -1 pour marche arriere.

# longueur d'un pas deduite du balancement de hanche (pour avancer sans glisser)
LONGUEUR_PAS = LONGUEUR_JAMBE * (math.sin(math.radians(HANCHE_AV)) + math.sin(math.radians(HANCHE_ARR)))


def pose_pas(ph):
    """Pose de marche pour une phase `ph` (radians). Jambe droite devant sur [0, pi]."""
    s = math.sin(ph)
    # hanches : avant = negatif (amplitude asymetrique avant/arriere)
    a = (HANCHE_AV + HANCHE_ARR) / 2.0
    c = (HANCHE_AV - HANCHE_ARR) / 2.0
    bouge("hipR_flexion", -(a * s + c))
    bouge("hipL_flexion", -(a * -s + c))
    # genou plie pendant le balance (jambe qui revient vers l'avant)
    bouge("kneeR_flexion", GENOU * max(0.0, math.cos(ph)))
    bouge("kneeL_flexion", GENOU * max(0.0, -math.cos(ph)))
    # pointe de pied relevee pendant le balance (pour ne pas racler le sol)
    bouge("ankleR_flexion", -CHEVILLE * max(0.0, math.cos(ph)))
    bouge("ankleL_flexion", -CHEVILLE * max(0.0, -math.cos(ph)))
    # bras en opposition, coude souple
    sa = (BRAS_AV + BRAS_ARR) / 2.0
    sc = (BRAS_ARR - BRAS_AV) / 2.0
    bouge("shoulderR_flexion", sa * s + sc)
    bouge("shoulderL_flexion", -sa * s + sc)
    bouge("elbowR_flexion", COUDE)
    bouge("elbowL_flexion", COUDE)


def avance(dist):
    """Place le corps a `dist` mm devant sa position de depart."""
    BASE.setPose(BASE_REST * transl(0, 0, SENS * dist))


def marche(nb_pas=NB_PAS, images_par_pas=IMAGES_PAR_PAS, dt=DT):
    """Anime la marche en avant, puis remet l'operateur au centre (HOME)."""
    for i in range(nb_pas * images_par_pas + 1):
        ph = math.pi * i / images_par_pas      # 1 pas = une demi-periode
        RDK.Render(False)
        pose_pas(ph)
        avance(LONGUEUR_PAS * ph / math.pi)
        RDK.Render(True)
        time.sleep(dt)
    # fin : repos + retour a la position initiale, au centre
    RDK.Render(False)
    neutre()
    BASE.setPose(HOME)
    RDK.Render(True)


if __name__ == "__main__":
    d_tot = LONGUEUR_PAS * NB_PAS / 1000.0
    print("Marche avant : {} pas (~{:.1f} m)...".format(NB_PAS, d_tot))
    marche()
    print("Arrive !")
