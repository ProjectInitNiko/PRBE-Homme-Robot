# -*- coding: utf-8 -*-
"""
Mouvement_v2.py — MODELE pour piloter l'operateur v2 (22 DDL).

A LANCER DANS ROBODK (clic droit > Run) depuis la station PRBE_Operateur_v2,
operateur en pose NEUTRE (le script capture le repos au demarrage).

PRINCIPE :
  - chaque DDL = un repere nomme (ex: "hipR_flexion") qui tourne sur UN axe.
  - bouge("nom_du_ddl", angle_en_degres) tourne ce DDL depuis le repos.
  - les angles sont automatiquement borns aux limites du corps humain.
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
    """Tourne un DDL de `deg` degres depuis le repos (born aux limites)."""
    axe, lo, hi = DDL[nom]
    deg = max(lo, min(hi, deg))                    # ne depasse pas le corps humain
    F[nom].setPose(REST[nom] * ROT[axe](math.radians(deg)))


def neutre():
    """Remet tout l'operateur droit."""
    for nom in DDL:
        F[nom].setPose(REST[nom])


# =======================================================================
# TON CODE ICI. Exemples :
# =======================================================================

# --- EXEMPLE 1 : une pose (lever le bras droit + plier le coude) ---
bouge("shoulderR_flexion", -70)   # bras droit vers l'avant
bouge("elbowR_flexion", 90)       # coude plie
RDK.Render(True)
time.sleep(1)

# --- EXEMPLE 2 : une petite animation (le bras qui salue) ---
neutre()
bouge("shoulderR_abduction", 80)  # bras leve sur le cote
for i in range(6):
    RDK.Render(False)
    bouge("elbowR_flexion", 30 + 40 * (i % 2))   # avant-bras qui va et vient
    RDK.Render(True)
    time.sleep(0.3)

neutre()
RDK.Render(True)
print("Fini.")
