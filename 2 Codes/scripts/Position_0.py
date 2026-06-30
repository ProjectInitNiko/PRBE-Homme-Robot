# -*- coding: utf-8 -*-
"""
Position_0.py — Remet le mannequin au GARDE-A-VOUS exact (position zero).

A lancer quand on veut repartir d'un etat propre : apres une animation
interrompue, un script qui a laisse le bras en l'air, ou des residus
accumules (chaque animation se termine a quelques degres pres ; les petits
ecarts s'additionnent au fil des runs).

Reconstruit le zero du rig (cf. rig_active_station.py, section 8) :
  - les 22 DDL -> rotation IDENTITE (la translation du repere ne bouge
    jamais, on la conserve telle quelle) ;
  - epaule du cote X+ (= gauche) : rotz(-42 deg) pour plaquer le bras que
    la pose STEP d'origine ecarte du corps ;
  - jambes resserrees : cheville ramenee a l'aplomb de la hanche (angle
    recalcule depuis les positions des reperes, pied contre-tourne).

Ne touche ni la Table, ni la Piece, ni la camera.
    C:\\RoboDK\\Python-Embedded\\python.exe scripts\\Position_0.py
"""
import math
import sys
from robolink import Robolink, ITEM_TYPE_FRAME
from robodk.robomath import Mat, rotz

DOF = [
    "shoulderL_abduction", "shoulderL_flexion", "shoulderL_rotation",
    "elbowL_flexion", "wristL_flexion", "wristL_deviation",
    "shoulderR_abduction", "shoulderR_flexion", "shoulderR_rotation",
    "elbowR_flexion", "wristR_flexion", "wristR_deviation",
    "hipL_abduction", "hipL_flexion", "hipL_rotation", "kneeL_flexion",
    "ankleL_flexion",
    "hipR_abduction", "hipR_flexion", "hipR_rotation", "kneeR_flexion",
    "ankleR_flexion",
]


def _zero(fr):
    """Rotation identite, translation conservee."""
    p = fr.Pose()
    fr.setPose(Mat([[1, 0, 0, p[0, 3]], [0, 1, 0, p[1, 3]],
                    [0, 0, 1, p[2, 3]], [0, 0, 0, 1]]))


def remettre_a_zero(RDK, verbose=True):
    """Remet les 22 DDL au garde-a-vous exact. Importable par les scripts
    d'animation (a appeler AVANT de capturer le repos)."""
    F = {}
    for nm in DOF:
        fr = RDK.Item(nm, ITEM_TYPE_FRAME)
        if not fr.Valid():
            sys.exit(f"ERREUR : repere {nm} introuvable — rig 22 DDL absent ?")
        F[nm] = fr

    # 1) tout a zero (les positions absolues redeviennent celles de la pose STEP)
    for nm in DOF:
        _zero(F[nm])

    # 2) bras gauche (cote X+) plaque le long du corps
    F["shoulderL_abduction"].setPose(
        F["shoulderL_abduction"].Pose() * rotz(math.radians(-42.0)))

    # 3) jambes resserrees : meme calcul que le rig (cheville a l'aplomb de la
    #    hanche), possible car a l'etape 1 les reperes sont aux positions STEP
    for u in ("R", "L"):
        hp = F[f"hip{u}_abduction"].PoseAbs()
        ap = F[f"ankle{u}_flexion"].PoseAbs()
        ang = math.atan2(ap[0, 3] - hp[0, 3], hp[1, 3] - ap[1, 3])
        F[f"hip{u}_abduction"].setPose(F[f"hip{u}_abduction"].Pose() * rotz(-ang))
        F[f"ankle{u}_flexion"].setPose(F[f"ankle{u}_flexion"].Pose() * rotz(ang))
        if verbose:
            print(f"  jambes resserrees ({u}) : {math.degrees(ang):+.1f} deg")


if __name__ == "__main__":
    RDK = Robolink()
    print("Station :", RDK.ActiveStation().Name())
    remettre_a_zero(RDK)
    RDK.Render(True)
    print("Position 0 : mannequin au garde-a-vous.")
