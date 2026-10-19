"""Display the captured CalculiX INP mesh and DAT displacement in native Gmsh.

No synthetic solver UI or displacement values. Geometry is undeformed; the field
is the native nodal displacement norm in metres from the clamped-floor fixture.
Requires gmsh4.14.1 and a working X/OpenGL display, e.g. Xvfb software rendering.
"""

from pathlib import Path
import json, math, hashlib
import gmsh

H = Path(__file__).resolve().parent
O = H / "release/fea"
p = O / "3U_48x24x2"
nodes = []
coords = []
elements = []
connect = []
mode = None
for line in p.with_suffix(".inp").read_text().splitlines():
    if line.strip() == "*NODE":
        mode = "node"
        continue
    if line.startswith("*ELEMENT"):
        mode = "element"
        continue
    if line.startswith("*"):
        mode = None
        continue
    row = line.split(",")
    if mode == "node":
        nodes.append(int(row[0]))
        coords.extend(float(x) for x in row[1:4])
    if mode == "element":
        elements.append(int(row[0]))
        connect.extend(int(x) for x in row[1:9])
values = {}
mode = False
for line in p.with_suffix(".dat").read_text().splitlines():
    if "displacements" in line:
        mode = True
        continue
    if "stresses" in line:
        mode = False
    row = line.split()
    if mode and len(row) == 4:
        try:
            values[int(row[0])] = math.sqrt(sum(float(x) ** 2 for x in row[1:]))
        except ValueError:
            pass
assert len(values) == len(nodes)
gmsh.initialize()
gmsh.model.add("FDR_clamped_floor_fixture")
entity = gmsh.model.addDiscreteEntity(3)
gmsh.model.mesh.addNodes(3, entity, nodes, coords)
gmsh.model.mesh.addElementsByType(entity, 5, elements, connect)
v = gmsh.view.add("Displacement norm [m] — 6 kg x25 g clamped-floor fixture")
gmsh.view.addModelData(
    v,
    0,
    gmsh.model.getCurrent(),
    "NodeData",
    nodes,
    [[values[n]] for n in nodes],
    numComponents=1,
)
gmsh.option.setNumber("General.GraphicsWidth", 1400)
gmsh.option.setNumber("General.GraphicsHeight", 850)
gmsh.option.setColor("General.Color.Background", 255, 255, 255)
gmsh.option.setColor("General.Color.Foreground", 0, 0, 0)
gmsh.option.setColor("General.Color.Text", 0, 0, 0)
gmsh.option.setNumber("Mesh.VolumeFaces", 0)
gmsh.option.setNumber("Mesh.VolumeEdges", 1)
gmsh.option.setNumber("General.Axes", 3)
gmsh.option.setNumber("General.Trackball", 0)
gmsh.option.setNumber("General.RotationX", -55)
gmsh.option.setNumber("General.RotationY", 0)
gmsh.option.setNumber("General.RotationZ", -30)
gmsh.view.option.setNumber(v, "ShowScale", 1)
gmsh.view.option.setNumber(v, "IntervalsType", 3)
gmsh.view.option.setNumber(v, "NbIso", 20)
gmsh.view.option.setNumber(v, "Light", 0)
gmsh.view.option.setNumber(v, "ColormapNumber", 23)
gmsh.fltk.initialize()
gmsh.graphics.draw()
gmsh.write(str(O / "Gmsh_CalculiX_floor.png"))
gmsh.view.write(v, str(O / "Gmsh_CalculiX_floor.msh"))
gmsh.finalize()
(O / "VIEW_PROVENANCE.json").write_text(
    json.dumps(
        {
            "viewer": "Gmsh4.14.1 native OpenGL viewport export",
            "solver": "CalculiX2.23",
            "case": "3U_48x24x2",
            "geometry": "Undeformed actual C3D8I INP mesh; displacement norm from native DAT in metres",
            "limitations": "Assumed clamped edges and E69GPa/nu0.33 fixture; not actual assembly, converged peak stress, contact or qualification",
            "inputs": {
                p.with_suffix(s)
                .name: hashlib.sha256(p.with_suffix(s).read_bytes())
                .hexdigest()
                for s in [".inp", ".dat"]
            },
        },
        indent=2,
    )
    + "\n"
)
print("Native Gmsh viewport exported from actual CalculiX input/output")
