#!/usr/bin/env python3
"""validate_dof.py — Charge un URDF avec iDynTree, compte les DDL et vérifie la
consistance physique (matrice de masse définie positive sur des poses aléatoires).

Usage : conda run -n hmgenv python scripts/validate_dof.py [modele.urdf]
Défaut : examples/Niko_v2_PRBE.urdf
"""
import sys
from pathlib import Path

import numpy as np
import idyntree.bindings as idt


def main():
    repo = Path(__file__).resolve().parent.parent
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "examples" / "Niko_v2_PRBE.urdf"

    loader = idt.ModelLoader()
    if not loader.loadModelFromFile(str(src)):
        sys.exit(f"ERREUR : iDynTree n'a pas pu charger {src}")
    model = loader.model()

    ndof = model.getNrOfDOFs()
    print(f"Modèle  : {src.name}")
    print(f"Links   : {model.getNrOfLinks()}")
    print(f"DDL     : {ndof}")
    print("Joints articulés :")
    for i in range(model.getNrOfJoints()):
        j = model.getJoint(i)
        if j.getNrOfDOFs() > 0:
            print(f"  - {model.getJointName(i)}")

    # Consistance dynamique : matrice de masse définie positive sur 100 poses.
    dyn = idt.KinDynComputations()
    dyn.loadRobotModel(model)
    dyn.setFloatingBase("Pelvis")
    grav = idt.Vector3()
    grav.zero()
    ok = True
    for _ in range(100):
        q = idt.JointPosDoubleArray(ndof)
        for k in range(ndof):
            q.setVal(k, np.random.uniform(-np.pi, np.pi))
        base = idt.Transform.Identity()
        dyn.setRobotState(base, q,
                          idt.Twist.Zero(), idt.JointDOFsDoubleArray(ndof),
                          grav)
        M = idt.MatrixDynSize(ndof + 6, ndof + 6)
        dyn.getFreeFloatingMassMatrix(M)
        eig = np.linalg.eigvalsh(M.toNumPy())
        if np.min(eig) <= 0:
            ok = False
            break
    print(f"\nMatrice de masse définie positive (100 poses) : {'OUI' if ok else 'NON'}")
    sys.exit(0 if (ndof == 22 and ok) else 1)


if __name__ == "__main__":
    main()
