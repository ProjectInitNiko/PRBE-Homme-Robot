# -*- coding: utf-8 -*-
"""
rebuild_finish.py — Étape 3 du rebuild : ré-embarquer les programmes
(Mouvement_v2, Marche_Militaire, Marche_Avant) + vue de profil.
"""
from robodk.robolink import Robolink
from robodk.robomath import Mat

SCRIPTS = r"D:\PRBE_Homme_Robot\PRBE-Homme-Robot\scripts"
PROGS = ["Mouvement_v2.py", "Marche_Militaire.py", "Marche_Avant.py", "Marche_Trajectoire.py"]

RDK = Robolink()
print("Station :", RDK.ActiveStation().Name())

existants = [p.Name() for p in RDK.ItemList(10)]  # 10 = ITEM_TYPE_PROGRAM_PYTHON
for prog in PROGS:
    nom = prog[:-3]
    if nom in existants:
        print("Deja present :", nom)
        continue
    RDK.AddFile(SCRIPTS + "\\" + prog)
    print("Ajoute :", nom)

# Vue de profil validee le 04/06 (setViewPose capricieux mais cette matrice passe)
RDK.setViewPose(Mat([[0, 0, 1, 0], [0, 1, 0, -950], [-1, 0, 0, -3200], [0, 0, 0, 1]]))
print("Vue de profil appliquee.")
