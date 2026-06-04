# -*- coding: utf-8 -*-
"""
rebuild_operateur.py — Rebuild complet de l'opérateur en UNE commande.
(Workaround au bug de persistance .rdk : sous-solides type 7 = poses non sauvées.)

Usage (RoboDK ouvert) :
    C:\\RoboDK\\Python-Embedded\\python.exe scripts\\rebuild_operateur.py

Enchaîne : nouvelle station + import STEP + Split  ->  rig 22 DDL (garde-à-vous)
           ->  programmes (Mouvement_v2, marches) + vue de profil.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ETAPES = ["rebuild_prep.py", "rig_active_station.py", "rebuild_finish.py"]

for script in ETAPES:
    print("=" * 60)
    print(">>>", script)
    r = subprocess.run([sys.executable, str(HERE / script)])
    if r.returncode != 0:
        sys.exit(f"ECHEC a l'etape {script} (code {r.returncode})")

print("=" * 60)
print("Rebuild complet OK — opérateur prêt (garde-à-vous, 22 DDL).")
