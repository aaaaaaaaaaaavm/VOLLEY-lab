"""Independent STEP readback and orthographic edge extraction (FreeCAD/OCC)."""

from pathlib import Path
import json, hashlib
import FreeCAD as App
import Part

H = Path(__file__).resolve().parent
O = H / "release"
rows = []
for p in sorted(O.glob("*_3U.step")):
    shape = Part.Shape()
    shape.read(str(p))
    assert shape.isValid(), p
    bb = shape.BoundBox
    edges = []
    for edge in shape.Edges:
        points = edge.discretize(
            Number=2 if edge.Curve.__class__.__name__ == "Line" else 18
        )
        edges.append([[v.x, v.y, v.z] for v in points])
    rows.append(
        {
            "candidate": p.stem[:-3],
            "step": p.name,
            "step_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "valid": True,
            "solids": len(shape.Solids),
            "bounds_mm": [bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax],
            "edges": edges,
        }
    )
(O / "STEP_VIEWS.json").write_text(json.dumps(rows, separators=(",", ":")) + "\n")
print(
    "Independent STEP readback and orthographic geometry:",
    len(rows),
    "valid assemblies",
)
