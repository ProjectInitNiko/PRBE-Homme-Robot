"""
Viewer URDF basé sur iDynTree.

Usage :
    conda run -n hmgenv --no-capture-output python view_urdf.py <chemin_vers_fichier.urdf>

Contrôles :
    - clic gauche + glisser : rotation
    - clic droit + glisser : translation
    - molette : zoom
    - fermer la fenêtre : quitter
"""

import sys
from pathlib import Path
import idyntree.bindings as iDynTree


def view(urdf_path: Path) -> None:
    if not urdf_path.exists():
        sys.exit(f"[ERR] URDF introuvable : {urdf_path}")

    loader = iDynTree.ModelLoader()
    if not loader.loadModelFromFile(str(urdf_path)):
        sys.exit(f"[ERR] Échec chargement modèle depuis {urdf_path}")

    model = loader.model()
    print(f"[INFO] Modèle chargé : {urdf_path.name}")
    print(f"[INFO] Links : {model.getNrOfLinks()}")
    print(f"[INFO] Joints (total) : {model.getNrOfJoints()}")
    print(f"[INFO] DDL (revolute/prismatic) : {model.getNrOfDOFs()}")

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
    joint_positions = [0.0] * model.getNrOfDOFs()

    viz.modelViz("Model").setPositions(base_transform, joint_positions)

    print("[INFO] Fenêtre ouverte. Ferme-la pour quitter.")
    while viz.run():
        viz.draw()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage : python {Path(__file__).name} <fichier.urdf>")
    view(Path(sys.argv[1]).resolve())
