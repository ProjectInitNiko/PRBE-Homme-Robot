# -*- coding: utf-8 -*-
"""Supprime les stations vides « New Station... » et active PRBE_Operateur_v2."""
from robodk.robolink import Robolink, ITEM_TYPE_STATION

RDK = Robolink()
for st in RDK.ItemList(ITEM_TYPE_STATION):
    nom = st.Name()
    if nom.startswith("New Station") and len(st.Childs()) == 0:
        print("Supprime station vide :", nom)
        st.Delete()

target = RDK.Item("PRBE_Operateur_v2", ITEM_TYPE_STATION)
if target.Valid():
    RDK.setActiveStation(target)
print("Station active :", RDK.ActiveStation().Name())
