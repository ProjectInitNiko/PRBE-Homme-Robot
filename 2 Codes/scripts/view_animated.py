"""
Viewer URDF animé (iDynTree) — fait bouger les DDL du mannequin.

Chaque degré de liberté oscille dans ses limites articulaires (sinus, phases
décalées) → on voit les articulations gardées bouger et les segments figés
rester rigides. Sert à valider visuellement le modèle réduit.

Usage (depuis le dossier examples/ pour que les meshes soient trouvés) :
    cd examples
    conda run -n hmgenv --no-capture-output python ../scripts/view_animated.py Niko_v2_PRBE.urdf

Contrôles : clic gauche = rotation, clic droit = translation, molette = zoom.
"""

import sys
import time
import math
from pathlib import Path
import idyntree.bindings as iDynTree


def joint_limits(model):
    """Retourne [(lo, hi)] par DDL, dans l'ordre des DDL du modèle."""
    ndof = model.getNrOfDOFs()
    lims = [(-0.5, 0.5)] * ndof  # défaut si pas de limite déclarée
    for i in range(model.getNrOfJoints()):
        j = model.getJoint(i)
        n = j.getNrOfDOFs()
        if n == 0:
            continue
        off = j.getDOFsOffset()
        for d in range(n):
            try:
                if j.hasPosLimits():
                    lims[off + d] = (j.getMinPosLimit(d), j.getMaxPosLimit(d))
            except Exception:  # noqa: BLE001
                pass
    return lims


def view(urdf_path: Path) -> None:
    if not urdf_path.exists():
        sys.exit(f"[ERR] URDF introuvable : {urdf_path}")

    loader = iDynTree.ModelLoader()
    if not loader.loadModelFromFile(str(urdf_path)):
        sys.exit(f"[ERR] Échec chargement modèle depuis {urdf_path}")

    model = loader.model()
    ndof = model.getNrOfDOFs()
    lims = joint_limits(model)
    print(f"[INFO] Modèle : {urdf_path.name} | Links {model.getNrOfLinks()} | DDL {ndof}")
    print("[INFO] Animation des DDL en cours. Ferme la fenêtre pour quitter.")

    viz = iDynTree.Visualizer()
    opt = iDynTree.VisualizerOptions()
    opt.winWidth = 1500
    opt.winHeight = 1000
    viz.init(opt)

    env = viz.enviroment()
    env.setElementVisibility("floor_grid", True)
    env.setElementVisibility("world_frame", True)
    viz.setColorPalette("meshcat")

    cam = viz.camera()
    cam.setPosition(iDynTree.Position(2, 1, 2.5))
    cam.animator().enableMouseControl(True)

    viz.addModel(model, "Model")

    rot = iDynTree.Rotation()
    rot.fromQuaternion(iDynTree.Vector4([1, 0, 0, 0]))
    base_transform = iDynTree.Transform(rot, iDynTree.Position([0, 0, 0]))

    freq = 0.25  # Hz — lent pour bien voir
    t0 = time.time()
    while viz.run():
        t = time.time() - t0
        q = [0.0] * ndof
        for k in range(ndof):
            lo, hi = lims[k]
            mid = 0.5 * (lo + hi)
            amp = 0.5 * (hi - lo) * 0.85  # marge pour rester dans les limites
            phase = 2.0 * math.pi * k / max(ndof, 1)
            q[k] = mid + amp * math.sin(2.0 * math.pi * freq * t + phase)
        viz.modelViz("Model").setPositions(base_transform, q)
        viz.draw()
        time.sleep(0.01)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage : python {Path(__file__).name} <fichier.urdf>")
    view(Path(sys.argv[1]).resolve())
