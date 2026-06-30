"""
Convertit les chemins meshes absolus d'un .urdf généré par HMG en chemins relatifs.

HMG met des chemins type :
    D:\\PRBE_Homme_Robot\\Docs Git\\human-model-generator\\code\\models\\humanModelTemplate\\meshes\\Pelvis.stl

Ce script les remplace par :
    ../external/human-model-generator/code/models/humanModelTemplate/meshes/Pelvis.stl

→ le .urdf de sortie est portable, à condition que le repo PRBE-Homme-Robot soit
cloné avec HMG dans external/. Le chemin relatif part de examples/<urdf>.

Usage :
    python fix_urdf_paths.py <input.urdf> <output.urdf>
"""

import re
import sys
from pathlib import Path

# Le chemin relatif final, depuis examples/<urdf> vers les meshes HMG dans external/
RELATIVE_MESH_DIR = "../external/human-model-generator/code/models/humanModelTemplate/meshes"

# Pattern : capture tout ce qui finit par /humanModelTemplate/meshes/<NomDuMesh>.stl
# Marche pour Windows (\\) et Unix (/)
MESH_PATH_RE = re.compile(
    r'filename="[^"]*?humanModelTemplate[\\/]+meshes[\\/]+([^"\\/]+\.stl)"',
    re.IGNORECASE,
)


def fix(input_urdf: Path, output_urdf: Path) -> None:
    if not input_urdf.exists():
        sys.exit(f"[ERR] URDF d'entrée introuvable : {input_urdf}")

    text = input_urdf.read_text(encoding="utf-8")
    original_count = len(MESH_PATH_RE.findall(text))

    new_text = MESH_PATH_RE.sub(
        lambda m: f'filename="{RELATIVE_MESH_DIR}/{m.group(1)}"',
        text,
    )

    output_urdf.parent.mkdir(parents=True, exist_ok=True)
    output_urdf.write_text(new_text, encoding="utf-8")

    print(f"[OK] {original_count} chemins meshes convertis en relatif")
    print(f"[OK] Écrit : {output_urdf}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Usage : python {Path(__file__).name} <input.urdf> <output.urdf>")
    fix(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
