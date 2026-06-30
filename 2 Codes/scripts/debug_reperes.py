# -*- coding: utf-8 -*-
"""
debug_reperes.py — Prints de debug de la persistance des reperes (CR du 04/06).

Photographie TOUS les reperes et objets de la station active (pose relative
+ pose absolue + parent), imprime un tableau et sauve un snapshot JSON
etiquete. Le mode "compare" diffe deux snapshots pour localiser ce qui
bouge entre la sauvegarde du .rdk et sa reouverture (bug Human_Base
desaligne / sous-solides type 7 non persistes).

Usage (RoboDK ouvert, station chargee) :
    python debug_reperes.py apres_build          # snapshot etiquete
    python debug_reperes.py avant_save
    python debug_reperes.py apres_reouverture
    python debug_reperes.py compare avant_save apres_reouverture

Snapshots dans scripts\\_debug_reperes\\<label>.json (gitignore).
Protocole : rebuild -> 'apres_build' -> Save .rdk -> 'avant_save' ->
fermer/rouvrir (double-clic ET menu Ouvrir, pour comparer) ->
'apres_reouverture' -> compare.
"""
import json
import math
import sys
from datetime import datetime
from pathlib import Path

OUTDIR = Path(__file__).resolve().parent / "_debug_reperes"
TOL_MM = 0.5    # ecart de position signale (mm)
TOL_DEG = 0.1   # ecart d'orientation signale (deg)

TYPE_NAMES = {1: "station", 3: "frame", 5: "objet", 7: "courbe(type7)", 10: "programme"}


# --- geometrie sur matrices 4x4 (listes de listes, pas besoin de robodk) ---

def pos_of(rows):
    return [rows[0][3], rows[1][3], rows[2][3]]


def dist_mm(r1, r2):
    p1, p2 = pos_of(r1), pos_of(r2)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def angle_deg(r1, r2):
    # angle de la rotation R1^T * R2 : acos((trace-1)/2)
    tr = sum(r1[k][i] * r2[k][i] for i in range(3) for k in range(3))
    c = max(-1.0, min(1.0, (tr - 1.0) / 2.0))
    return math.degrees(math.acos(c))


# --- snapshot ---

def item_path(item, station):
    """Chemin Nom/Nom/... depuis la racine de la station (exclue)."""
    parts = []
    cur = item
    while cur.Valid() and cur.item != station.item:
        parts.append(cur.Name())
        try:
            cur = cur.Parent()
        except Exception:
            break
    return "/".join(reversed(parts))


def take_snapshot(label):
    from robolink import Robolink
    RDK = Robolink()
    station = RDK.ActiveStation()
    items = []
    for it in RDK.ItemList():
        t = it.Type()
        if t not in (3, 5, 7):
            continue
        try:
            parent = it.Parent().Name()
        except Exception:
            parent = "?"
        items.append({
            "path": item_path(it, station),
            "name": it.Name(),
            "type": t,
            "parent": parent,
            "pose_rel": it.Pose().rows,
            "pose_abs": it.PoseAbs().rows,
        })
    items.sort(key=lambda d: d["path"])

    snap = {
        "label": label,
        "date": datetime.now().isoformat(timespec="seconds"),
        "station": station.Name(),
        "items": items,
    }
    OUTDIR.mkdir(exist_ok=True)
    out = OUTDIR / f"{label}.json"
    out.write_text(json.dumps(snap, indent=1), encoding="utf-8")

    # prints : Human_Base d'abord, puis tableau complet
    print(f"=== SNAPSHOT '{label}' — station '{station.Name()}' — {len(items)} items ===")
    hb = next((d for d in items if d["name"] == "Human_Base"), None)
    if hb:
        p = pos_of(hb["pose_abs"])
        print(f"Human_Base ABS : ({p[0]:8.2f}, {p[1]:8.2f}, {p[2]:8.2f})  parent: {hb['parent']}")
    else:
        print("!! Human_Base INTROUVABLE dans la station")
    print(f"{'item':42s} {'typ':10s} {'pos relative (mm)':>28s} {'pos absolue (mm)':>28s}")
    for d in items:
        pr, pa = pos_of(d["pose_rel"]), pos_of(d["pose_abs"])
        ind = "  " * d["path"].count("/")
        nm = (ind + d["name"])[:42]
        print(f"{nm:42s} {TYPE_NAMES.get(d['type'], str(d['type'])):10s} "
              f"({pr[0]:7.1f},{pr[1]:7.1f},{pr[2]:7.1f})  "
              f"({pa[0]:7.1f},{pa[1]:7.1f},{pa[2]:7.1f})")
    print(f"OK — snapshot sauve : {out}")


# --- compare ---

def load(label):
    f = OUTDIR / f"{label}.json"
    if not f.exists():
        sys.exit(f"ERREUR : snapshot '{label}' introuvable ({f})")
    return json.loads(f.read_text(encoding="utf-8"))


def compare(label_a, label_b):
    A, B = load(label_a), load(label_b)
    ia = {d["path"]: d for d in A["items"]}
    ib = {d["path"]: d for d in B["items"]}
    print(f"=== COMPARE '{label_a}' ({A['date']}) -> '{label_b}' ({B['date']}) ===")
    print(f"Stations : '{A['station']}' -> '{B['station']}'")

    missing = sorted(set(ia) - set(ib))
    added = sorted(set(ib) - set(ia))
    for p in missing:
        print(f"  DISPARU  : {p}")
    for p in added:
        print(f"  NOUVEAU  : {p}")

    diffs = []
    for p in sorted(set(ia) & set(ib)):
        da, db = ia[p], ib[p]
        for kind in ("rel", "abs"):
            ra, rb = da[f"pose_{kind}"], db[f"pose_{kind}"]
            dt, dr = dist_mm(ra, rb), angle_deg(ra, rb)
            if dt > TOL_MM or dr > TOL_DEG:
                diffs.append((dt, dr, p, kind, da["type"]))
    if not diffs:
        print(f"AUCUN ecart > {TOL_MM} mm / {TOL_DEG} deg sur "
              f"{len(set(ia) & set(ib))} items communs — poses persistees.")
        return
    diffs.sort(reverse=True)
    print(f"\n{len(diffs)} ECARTS (tri par amplitude) :")
    print(f"{'item':50s} {'pose':4s} {'typ':10s} {'d_pos mm':>10s} {'d_rot deg':>10s}")
    for dt, dr, p, kind, t in diffs:
        print(f"{p[:50]:50s} {kind:4s} {TYPE_NAMES.get(t, str(t)):10s} {dt:10.2f} {dr:10.3f}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "compare":
        compare(args[1], args[2])
    elif len(args) == 1 and args[0] != "compare":
        take_snapshot(args[0])
    else:
        print(__doc__)
        sys.exit(1)
