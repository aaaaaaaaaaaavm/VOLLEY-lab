"""Native CAD material-only CG/inertia and connectivity review in the stowed pose."""

from pathlib import Path
import json, hashlib, itertools
import FreeCAD as App

H = Path(__file__).resolve().parent
O = H / "release"
d = json.loads((O / "CAD_REPORT.json").read_text())
out = []
for r in d["reports"]:
    p = O / (r["candidate"] + "_" + r["payload_class"] + ".FCStd")
    doc = App.openDocument(str(p))
    items = []
    for obj, row in zip(doc.Objects, r["parts"]):
        assert obj.Label == row["part"].replace("-", "m").replace(".", "_"), (
            obj.Label,
            row["part"],
        )
        if row["modeled_mass_kg"] <= 0:
            continue
        m = row["modeled_mass_kg"]
        density = m / obj.Shape.Volume
        for solid in obj.Shape.Solids:
            c = solid.CenterOfMass
            items.append((solid, row, [c.x, c.y, c.z], solid.Volume * density, density))
    mass = sum(x[3] for x in items)
    cg = [sum(x[2][j] * x[3] for x in items) / mass for j in range(3)]
    I = [[0.0] * 3 for _ in range(3)]
    for obj, row, c, m, rho in items:
        mat = obj.MatrixOfInertia
        v = [c[j] - cg[j] for j in range(3)]
        diag = sum(z * z for z in v)
        for i in range(3):
            for j in range(3):
                I[i][j] += (
                    getattr(mat, "A" + str(i + 1) + str(j + 1)) * rho
                    + m * ((diag if i == j else 0) - v[i] * v[j])
                ) * 1e-6
    bb = doc.Objects[0].Shape.BoundBox
    for obj in doc.Objects[1:]:
        bb.add(obj.Shape.BoundBox)
    # Detect missing nominal contact between modeled drive chain pieces. A zero
    # distance is necessary, not sufficient, for a mechanically adequate joint.
    names = {row["part"]: (obj, row) for obj, row in zip(doc.Objects, r["parts"])}
    pairs = []
    for a, b in [
        ("Driven_fork_frame", "Tr8_nut_blank"),
        ("Driven_fork_frame", "Guide_bearing_-34"),
        ("Driven_fork_frame", "Guide_bearing_-62"),
        ("Spring_applied_pawl", "Power_off_capture_rack"),
    ]:
        if a in names and b in names:
            dist = names[a][0].Shape.distToShape(names[b][0].Shape)[0]
            pairs.append(
                {
                    "a": a,
                    "b": b,
                    "minimum_distance_mm": dist,
                    "status": (
                        "MISSING_MODELED_CONNECTION"
                        if dist > 1e-5
                        else "GEOMETRIC_CONTACT_ONLY_NOT_JOINT_PROOF"
                    ),
                }
            )
    out.append(
        {
            "candidate": r["candidate"],
            "class": r["payload_class"],
            "mass_material_only_kg": mass,
            "CG_mm": cg,
            "inertia_about_CG_kg_m2": I,
            "bounds_mm": [bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax],
            "bounding_box_volume_litre": bb.XLength * bb.YLength * bb.ZLength / 1e6,
            "drive_chain_connections": pairs,
            "fork_frame_connected_solids": len(
                names["Driven_fork_frame"][0].Shape.Solids
            ),
            "FCStd_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
    )
    App.closeDocument(doc.Name)
(O / "METROLOGY.json").write_text(
    json.dumps(
        {
            "boundary": "Modeled material only; payload, uncatalogued actuator/sensors, fasteners/harness/interface omitted. This is not installed CG/inertia. Drum includes four cells; others one; raw masses are not a fair system ranking.",
            "cases": out,
        },
        indent=2,
    )
    + "\n"
)
print("14 material CG/inertia/bounds and drive-chain connectivity records")
