"""Cantilever screen of the modeled 8x1x3mm capture-rack tooth.

Uses calculated MEAN arrest force, not peak impact force. Assumed steel stiffness
and yield bands are sensitivities, not a supplier rating or actual engagement.
"""

from pathlib import Path
import json, hashlib

H = Path(__file__).resolve().parent
O = H / "release"
d = json.loads((O / "LOAD_FAULT_REPORT.json").read_text())
rows = []
for i, c in enumerate(d["cases"]):
    for a in c["power_off_capture"]:
        F = a["mean_arrest_force_N"]
        b = 8.0
        t = 1.0
        height = 3.0
        E = 200000.0
        stress = 6 * F * height / (b * t * t)
        rows.append(
            {
                "load_case": i,
                "response_s": a["response_s"],
                "compliance_mm": a["compliance_mm"],
                "mean_force_N": F,
                "nominal_root_bending_MPa": stress,
                "rectangular_section_shear_MPa": 1.5 * F / (b * t),
                "linear_tip_deflection_mm": 4 * F * height**3 / (E * b * t**3),
                "exceeds_assumed_yield": {str(y): stress > y for y in [250, 500, 1000]},
            }
        )
result = {
    "boundary": "Unengaged current pawl; this sizes the required tooth, not an actual retained load path. Mean arrest force underestimates unknown peak contact force. Sharp roots, stress concentration, pawl impact, fatigue and engaged contact absent.",
    "geometry_mm": {"width": 8, "root_thickness": 1, "contact_height": 3},
    "E_assumed_MPa": 200000,
    "yield_bands_MPa": [250, 500, 1000],
    "cases": rows,
    "max_mean_force_N": max(x["mean_force_N"] for x in rows),
    "max_nominal_bending_MPa": max(x["nominal_root_bending_MPa"] for x in rows),
    "counts_above_assumed_yield": {
        str(y): sum(x["exceeds_assumed_yield"][str(y)] for x in rows)
        for y in [250, 500, 1000]
    },
    "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "load_report_sha256": hashlib.sha256(
        (O / "LOAD_FAULT_REPORT.json").read_bytes()
    ).hexdigest(),
}
assert len(rows) == 972 and result["counts_above_assumed_yield"]["1000"] > 0
(O / "ARREST_TOOTH.json").write_text(json.dumps(result, indent=2) + "\n")
print(
    len(rows),
    "mean-load cases; max nominal tooth bending",
    result["max_nominal_bending_MPa"],
    "MPa; failures retained",
)
