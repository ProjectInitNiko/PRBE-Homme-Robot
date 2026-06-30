# -*- coding: utf-8 -*-
"""
rebuild_prep.py — Étape 1 du rebuild : nouvelle station + import STEP + Split.
Lancer ensuite rig_active_station.py (étape 2), puis rebuild_finish.py (étape 3).
"""
from robodk.robolink import Robolink

STEP = r"D:\PRBE_Homme_Robot\Documents Teams\Modèles de simulation\Manikin\Manikin_1.STEP"

RDK = Robolink()
print("RoboDK OK, version :", RDK.Version())

RDK.AddStation("PRBE_Operateur_v2")
print("Station creee.")

blob = RDK.AddFile(STEP)
if not blob.Valid():
    raise SystemExit("ERREUR : import STEP echoue.")
print("STEP importe :", blob.Name())

blob.setParam("Split")
n = len(blob.Childs())
print("Split OK :", n, "sous-solides")
if n < 15:
    raise SystemExit("ERREUR : moins de 15 sous-solides apres Split.")
