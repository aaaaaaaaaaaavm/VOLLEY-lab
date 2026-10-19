"""Verify captured feeder evidence integrity; does not execute native CAD/FEA."""

from pathlib import Path
import json, hashlib, math

H = Path(__file__).resolve().parent
O = H / "release"
load = lambda p: json.loads((O / p).read_text())
P = json.loads((H / "requirements.json").read_text())
d = load("CAD_REPORT.json")
m = load("METROLOGY.json")
masses = {}
for name, sha in d["artifact_sha256"].items():
    assert hashlib.sha256((O / name).read_bytes()).hexdigest() == sha, name
assert d["revision"] == P["revision"]
assert len(d["reports"]) == len(m["cases"]) == 14
for r in d["reports"]:
    assert r["source_revision"] == P["revision"]
    assert len(r["motion_stations"]) == 15
    assert not any(p["intersections"] for p in r["motion_stations"]), (
        r["candidate"],
        r["payload_class"],
        "unresolved nominal intersections",
    )
    assert not r["continuous_translational_payload_sweep"]["unresolved_penetrations"]
    mass = sum(p["modeled_mass_kg"] for p in r["parts"])
    assert math.isclose(mass, r["modeled_material_kg"], abs_tol=1e-10)
    masses[r["candidate"], r["payload_class"]] = mass
for r in m["cases"]:
    assert math.isclose(
        masses[r["candidate"], r["class"]], r["mass_material_only_kg"], abs_tol=1e-9
    )
    assert r["fork_frame_connected_solids"] == 1
    I = r["inertia_about_CG_kg_m2"]
    assert all(I[i][i] > 0 for i in range(3))
    assert all(abs(I[i][j] - I[j][i]) < 1e-10 for i in range(3) for j in range(3))
l = load("LOAD_FAULT_REPORT.json")
assert l["revision"] == P["revision"]
assert (
    len(l["cases"]) == 108
    and len(l["tolerances"]) == 12
    and len(l["fault_cases"]) == 36
)
assert any(not x["spring"]["force_floor_sufficient"] for x in l["cases"])
assert any(not x["screen_pass"] for x in l["tolerances"])
assert all(not x["continue_other_cells"] for x in l["fault_cases"])
f = load("fea/RESULTS.json")
assert len(f["cases"]) == 6
for r in f["cases"]:
    assert abs(r["force_N"] - 6 * 25 * 9.80665) < 1e-8
    for ext, key in [(".inp", "input_sha256"), (".dat", "dat_sha256")]:
        assert (
            hashlib.sha256((O / "fea" / (r["case"] + ext)).read_bytes()).hexdigest()
            == r[key]
        )
for r in load("TRADE.json")["candidates"]:
    assert r["eligible_for_baseline"] is False
tooth = load("ARREST_TOOTH.json")
assert len(tooth["cases"]) == 972 and tooth["counts_above_assumed_yield"]["1000"] > 0
manifest = json.loads((H / "MANIFEST.json").read_text())
for name, sha in manifest["files"].items():
    assert hashlib.sha256((H / name).read_bytes()).hexdigest() == sha, name
print(
    "PASS: 14 native captures,210 nominal stations,14 bounded payload sweeps; material properties,108 load/12 tolerance/36 conditional fault cases,6 native fixture cases and exact file hashes. No hardware/full-cycle/selection pass."
)
