"""Native CalculiX 2.23 screen of the candidate storage-floor plate.

A declared clamped-short-edge fixture, not the actual host mounting or assembled
feeder. Linear elastic 69 GPa / nu .33 aluminium assumption. C3D8I mesh refinement.
Usage: CCX=/path/to/ccx python fea_floor.py
"""

from pathlib import Path
import os, json, subprocess, math, hashlib

H = Path(__file__).resolve().parent
O = H / "release/fea"
O.mkdir(exist_ok=True, parents=True)


def run(label, length, nx, ny, nz=2):
    # SI throughout; geometry agrees with the floor blank before mounting details.
    L = (length + 24) / 1000
    B = 0.110
    h = 0.006
    force = 6 * 25 * 9.80665
    E = 69e9
    nodes = {}
    n = 0
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                n += 1
                nodes[i, j, k] = n
    name = f"{label}_{nx}x{ny}x{nz}"
    p = O / name
    lines = [
        "*HEADING",
        name + "; assumed clamped-edge floor, 6kg x 25g; not assembly qualification",
        "*NODE",
    ]
    for (i, j, k), n in nodes.items():
        lines.append(f"{n},{L*i/nx:.12g},{B*j/ny:.12g},{h*k/nz:.12g}")
    lines += ["*ELEMENT,TYPE=C3D8I,ELSET=PLATE"]
    e = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                e += 1
                nn = [
                    nodes[i, j, k],
                    nodes[i + 1, j, k],
                    nodes[i + 1, j + 1, k],
                    nodes[i, j + 1, k],
                    nodes[i, j, k + 1],
                    nodes[i + 1, j, k + 1],
                    nodes[i + 1, j + 1, k + 1],
                    nodes[i, j + 1, k + 1],
                ]
                lines.append(str(e) + "," + ",".join(map(str, nn)))
    fixed = [n for (i, j, k), n in nodes.items() if i in [0, nx]]
    lines += ["*NSET,NSET=FIXED"]
    for k in range(0, len(fixed), 16):
        lines.append(",".join(map(str, fixed[k : k + 16])))
    lines += [
        "*NSET,NSET=ALLNODES,GENERATE",
        f"1,{len(nodes)},1",
        "*MATERIAL,NAME=AL_ASSUMED",
        "*ELASTIC",
        "69000000000,0.33",
        "*SOLID SECTION,ELSET=PLATE,MATERIAL=AL_ASSUMED",
        "*BOUNDARY",
        "FIXED,1,3",
        "*STEP",
        "*STATIC",
        "*CLOAD",
    ]
    applied = 0
    for (i, j, k), n in nodes.items():
        if k != nz:
            continue
        f = (
            -force
            / nx
            / ny
            * (0.5 if i in [0, nx] else 1)
            * (0.5 if j in [0, ny] else 1)
        )
        applied += f
        lines.append(f"{n},3,{f:.12g}")
    assert abs(applied + force) < 1e-9
    lines += [
        "*NODE PRINT,NSET=ALLNODES",
        "U",
        "*EL PRINT,ELSET=PLATE",
        "S",
        "*NODE FILE",
        "U",
        "*EL FILE",
        "S",
        "*END STEP",
    ]
    p.with_suffix(".inp").write_text("\n".join(lines) + "\n")
    ccx = os.environ.get("CCX", "ccx")
    x = subprocess.run([ccx, "-i", name], cwd=O, capture_output=True, text=True)
    p.with_suffix(".log").write_text(x.stdout + x.stderr)
    if x.returncode or not p.with_suffix(".dat").exists():
        raise RuntimeError(name + ": " + x.stdout[-600:] + x.stderr[-500:])
    mode = None
    U = []
    stress = []
    for line in p.with_suffix(".dat").read_text().splitlines():
        if "displacements" in line:
            mode = "U"
            continue
        if "stresses" in line:
            mode = "S"
            continue
        v = line.split()
        if mode == "U" and len(v) == 4:
            try:
                U.append([int(v[0])] + [float(a) for a in v[1:]])
            except ValueError:
                pass
        if mode == "S" and len(v) >= 8:
            try:
                xx, yy, zz, xy, xz, yz = map(float, v[2:8])
                vm = math.sqrt(
                    0.5 * ((xx - yy) ** 2 + (yy - zz) ** 2 + (zz - xx) ** 2)
                    + 3 * (xy * xy + xz * xz + yz * yz)
                )
                stress.append(vm)
            except ValueError:
                pass
    assert U and stress, name
    max_u = max(abs(x[3]) for x in U)
    beam = force * L**3 / (384 * E * (B * h**3 / 12))
    return {
        "case": name,
        "geometry_m": {"length": L, "width": B, "thickness": h},
        "nodes": len(nodes),
        "elements": e,
        "force_N": force,
        "max_abs_uz_m": max_u,
        "max_von_mises_Pa": max(stress),
        "fixed_fixed_Euler_beam_deflection_m": beam,
        "beam_comparison_boundary": "1-D beam approximation; 3-D plate Poisson/edge effects differ",
        "dat_sha256": hashlib.sha256(p.with_suffix(".dat").read_bytes()).hexdigest(),
        "input_sha256": hashlib.sha256(p.with_suffix(".inp").read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    rows = []
    for label, length in [("1U", 113.5), ("3U", 340.5)]:
        for nx, ny in [(12, 6), (24, 12), (48, 24)]:
            d = run(label, length, nx, ny)
            rows.append(d)
            print(d["case"], d["max_abs_uz_m"], d["max_von_mises_Pa"], flush=True)
    for label in ["1U", "3U"]:
        r = [x for x in rows if x["case"].startswith(label)]
        r[-1]["deflection_refinement_relative"] = (
            abs(r[-1]["max_abs_uz_m"] - r[-2]["max_abs_uz_m"]) / r[-1]["max_abs_uz_m"]
        )
    (O / "RESULTS.json").write_text(
        json.dumps(
            {
                "solver": "CalculiX 2.23",
                "evidence": "Native linear elastic fixture screen, not assembled feeder/launch qualification",
                "material": "Assumed aluminium E69GPa nu0.33; no selected alloy/temperature allowable",
                "load": "6kg x25g uniform normal force on top, both short edges fully clamped",
                "cases": rows,
                "limitations": [
                    "Actual mounts, bolt holes, guides, contacts, gate and load paths absent",
                    "Peak support stresses can depend on idealized constraints; no assembly pass from this screen",
                    "No fatigue, vibration, thermal stress, nonlinear contact or measured correlation",
                ],
            },
            indent=2,
        )
        + "\n"
    )
