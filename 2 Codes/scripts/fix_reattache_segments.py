# -*- coding: utf-8 -*-
"""
fix_reattache_segments.py — Repare le mannequin eclate a la reouverture du
.rdk SANS rebuild (quelques secondes), en re-jouant le re-basage geometrique
perdu a la sauvegarde.

Cause (diagnostic du 10/06) : pour les sous-solides type 7 (courbes issues
du Split), le .rdk sauve les points BRUTS d'origine — la compensation posee
par setParentStatic au moment du rig n'est PAS persistee. A l'ouverture,
RoboDK applique la transformation du frame parent sur ces points bruts
-> double transformation -> mannequin eclate. Les frames, vrais items a
pose persistee, restent corrects.

Remede, segment par segment :
  1) memoriser la pose relative de chaque frame, puis remettre chaque
     frame en etat de CONSTRUCTION (translation seule, rotation identite —
     l'etat dans lequel le rig d'origine a pose ses compensations)
  2) setParent(station)      — detache en KEEP-RELATIVE : la compensation
     (identite au chargement) ne change pas -> le segment retombe sur ses
     points bruts = position d'import, mannequin recompose
     setParentStatic(frame)  — re-attache en preservant l'absolu : la
     compensation F_build^-1 est re-posee, exactement comme au rig
  3) restaurer les poses memorisees (garde-a-vous, jambes resserrees) :
     la geometrie suit les frames

!! NE PAS envelopper dans RDK.Render(False) : le re-basage des type 7
echoue silencieusement sans rendu actif (constate le 10/06 — deux
tentatives identiques en Render(False) = aucun effet, la meme sequence
render actif fonctionne).

A relancer A CHAQUE OUVERTURE du .rdk (la sauvegarde re-perd le re-basage).
Filet de securite si etat incoherent : scripts/rebuild_operateur.py (~30 s).

!! PAS IDEMPOTENT : sur une station SAINE (fraichement rebuildee ou deja
reparee), le re-basage s'appliquerait une fois de trop et eclaterait le
mannequin. Une garde detecte l'etat via un segment du tronc et refuse de
tourner si la station est saine (--force pour outrepasser).

Usage (RoboDK ouvert, station chargee) :
    python fix_reattache_segments.py [--skip nom1,nom2] [--force]
    --skip  : segments a ne pas toucher (ex. deja repares a la main)
    --force : sauter la garde de detection
"""
import math
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from robolink import Robolink, ITEM_TYPE_FRAME
from robodk.robomath import transl

# ancres d'import des segments du tronc (cf. build_human_robodk.ANCHORS),
# en dur pour que le script reste autonome une fois embarque dans la station
TRONC = {"tete": (20, 1584, 30), "torso": (15, 1260, 0), "bassin": (0, 958, 0)}

skip = set()
if "--skip" in sys.argv:
    skip = set(sys.argv[sys.argv.index("--skip") + 1].split(","))

t0 = time.time()
RDK = Robolink()
station = RDK.ActiveStation()
print("Station :", station.Name())


def _d(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def garde_station_cassee():
    """True si le mannequin est eclate (double transformation detectee)."""
    for it in RDK.ItemList():
        if it.Type() != 7:
            continue
        part = it.Name().split("-", 1)[-1]
        if part not in TRONC:
            continue
        bb = it.setParam("BoundingBox")
        c = [(bb["min"][i] + bb["max"][i]) / 2.0 for i in range(3)]
        a = TRONC[part]
        F = it.Parent().PoseAbs().rows
        fa = [sum(F[i][j] * a[j] for j in range(3)) + F[i][3] for i in range(3)]
        d_sain, d_casse = _d(c, a), _d(c, fa)
        etat = "CASSEE (double transformation)" if d_casse < d_sain else "saine"
        print(f"Garde ({part}) : d_sain={d_sain:.0f} mm, d_casse={d_casse:.0f} mm -> station {etat}")
        return d_casse < d_sain
    sys.exit("Garde impossible : aucun segment du tronc (tete/torso/bassin) trouve.")


if "--force" not in sys.argv and not garde_station_cassee():
    sys.exit("Rien a faire — relancer avec --force pour outrepasser la garde.")

frames = RDK.ItemList(ITEM_TYPE_FRAME)
solids = [it for it in RDK.ItemList() if it.Type() == 7]
if not solids:
    sys.exit("Rien a reparer : aucun sous-solide type 7 dans la station.")
parent_of = {}
for s in solids:
    nm = s.Name()
    if nm in skip or nm.split("-", 1)[-1] in skip:
        print(f"  (skip : {nm})")
        continue
    p = s.Parent()
    if p.Type() == 3:
        parent_of[s] = p
    else:
        print(f"  (ignore : {nm} n'est pas sous un frame)")
print(f"{len(frames)} frames, {len(parent_of)} segments a re-attacher")

# 1) frames -> etat de construction (translation seule)
saved = []
for fr in frames:
    pose = fr.Pose()
    saved.append((fr, pose))
    r = pose.rows
    fr.setPose(transl(r[0][3], r[1][3], r[2][3]))

# 2) re-basage : detacher en keep-relative, re-attacher en statique
for s, fr in parent_of.items():
    s.setParent(station)
    s.setParentStatic(fr)
    print(f"  re-attache : {s.Name():26s} -> {fr.Name()}")

# 3) restaurer les poses (garde-a-vous, jambes resserrees, ...)
for fr, pose in saved:
    fr.setPose(pose)

print(f"OK — {len(parent_of)} segments re-attaches en {time.time() - t0:.1f} s")
