"""Assemble the engineering review from captured CAD, solver and load records."""

from pathlib import Path
import json, csv, hashlib, shutil
import numpy as np

H = Path(__file__).resolve().parent
O = H / "release"
root = H.parents[1]
load = lambda n: json.loads((O / n).read_text())
cad = load("CAD_REPORT.json")
met = load("METROLOGY.json")
loads = load("LOAD_FAULT_REPORT.json")
fea = load("fea/RESULTS.json")
# Keep the pre-existing ordinal trade as hypotheses. Numerical CAD results cannot
# justify measured reliability scores or comparable installed-system mass.
with (root / "docs/GEN6_FEEDER_TRADE_INPUTS.csv").open() as f:
    old = list(csv.DictReader(f))
w = np.array([0.35, 0.25, 0.20, 0.10, 0.10])
trade = []
for row in old:
    values = np.array(
        [
            float(row[k])
            for k in [
                "fault_safety",
                "fit_mass",
                "positioning",
                "cycle_power",
                "manufacturability",
            ]
        ]
    )
    trade.append(
        {
            "candidate": row["candidate"],
            "hypothesis_score": float(values @ w),
            "lower_one_point": float(np.clip(values - 1, 1, 5) @ w),
            "upper_one_point": float(np.clip(values + 1, 1, 5) @ w),
            "eligible_for_baseline": False,
            "reason": "Same-boundary installed hardware, full-cycle load/contact/fault evidence incomplete",
        }
    )
(O / "TRADE.json").write_text(
    json.dumps(
        {
            "weights": dict(
                zip(["safety", "fit_mass", "position", "cycle_power", "manufacture"], w)
            ),
            "interpretation": "Ordinal hypotheses retained from 12 Oct, not measured reliability or validated performance; all feasible-set gates remain open; no final selection",
            "candidates": trade,
        },
        indent=2,
    )
    + "\n"
)
# BOM includes every modeled part; purchased envelopes remain visible zero/unrated.
with (O / "BOM.csv").open("w") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "candidate",
            "class",
            "part",
            "material",
            "role",
            "volume_mm3",
            "modeled_material_kg",
            "boundary",
        ]
    )
    for r in cad["reports"]:
        for p in r["parts"]:
            writer.writerow(
                [
                    r["candidate"],
                    r["payload_class"],
                    p["part"],
                    p["material"],
                    p["role"],
                    p["volume_mm3"],
                    p["modeled_mass_kg"],
                    (
                        "Envelope/payload excluded"
                        if p["material"] in ["payload", "envelope"]
                        else "Material only; no installed rating"
                    ),
                ]
            )
# Explicit issue dispositions based on actual checked geometry, not declarations.
issues = [
    {
        "id": "FDR-I01",
        "issue": "Previous common side caps intersected side walls",
        "cause": "Separate overlapping proxy solids",
        "correction": "Fused one-piece L sections and gate slots",
        "verification": "Current exact B-rep stations and payload sweep",
        "state": "CORRECTED_WITHIN_STATED_GEOMETRY_CHECK",
    },
    {
        "id": "FDR-I02",
        "issue": "Receiver gate crossed fork at handoff",
        "cause": "Closing gate while fork remained advanced",
        "correction": "Seated snapshot retracts fork before receiver barrier closes",
        "verification": "Snapshot checked only; transition not verified",
        "state": "FULL_HANDOFF_TRANSITION_OPEN",
    },
    {
        "id": "FDR-I03",
        "issue": "Disconnected crosshead/link/rear fork",
        "cause": "46/9 mm gaps in prior FDR04 drive chain",
        "correction": "One connected overhead fork frame and nut-mount bridge in FDR08",
        "verification": "Native connected-solid assertion; current intersections; joint/contact ratings still open",
        "state": "FORK_AND_BEARING_HOUSING_CONNECTED_JOINT_RATINGS_OPEN",
    },
    {
        "id": "FDR-I04",
        "issue": "Power-off pawl engagement not represented",
        "cause": "1 mm gap from capture teeth in prior topology",
        "correction": "No assumed engagement; spring-applied capture is a requirement",
        "verification": "Counterexample remains when sole restraint is lost",
        "state": "OPEN_SAFETY_CRITICAL",
    },
    {
        "id": "FDR-I05",
        "issue": "0.5 degree adverse tolerance stack loses side gap",
        "cause": "Angular displacement over 200mm plus thermal/manufacturing allowance",
        "correction": "Require tighter datum alignment or redesign gap; 0.1 degree band screened",
        "verification": "12 parametric stacks; not measured fit",
        "state": "OPEN_UNTIL_INTERFACE_AND_DEFLECTION_DEFINED",
    },
    {
        "id": "FDR-I06",
        "issue": "Spring force insufficient at end of travel",
        "cause": "15N modeled end force below20/50N resistance cases",
        "correction": "Reject this spring sizing for those bands; re-size with governor/material fatigue checks",
        "verification": "108 analytical cases and wire geometry identity",
        "state": "FAILED_CASE_RETAINED",
    },
    {
        "id": "FDR-I07",
        "issue": "Unrated drive and receiver parts",
        "cause": "No sourceable actuator, brake, latch, sensor, coupling, mounts or payload ICD selected",
        "correction": "Use computed demands as component procurement requirements",
        "verification": "Zero-envelope mass shown explicitly in BOM",
        "state": "OPEN_NO_BUILD_RELEASE",
    },
    {
        "id": "FDR-I08",
        "issue": "Common-cycle and indexing evidence incomplete",
        "cause": "Stations do not cover full gate/fork/capture return motion, drum indexing or sequential scissor collapse",
        "correction": "Keep all seven as research candidates; no baseline lock",
        "verification": "Bounded sweep explicitly excludes nonlinear motion",
        "state": "OPEN",
    },
    {
        "id": "FDR-I09",
        "issue": "Fixture FEA is not assembly FEA",
        "cause": "Clamped edges omit real joints, bearings and host",
        "correction": "Retain mesh trends and no strength/qualification pass",
        "verification": "Six native CalculiX inputs/DAT/FRD/logs",
        "state": "BOUNDED_FIXTURE_RESULT_ONLY",
    },
    {
        "id": "FDR-I10",
        "issue": "Raw material mass is not equal-boundary installed mass",
        "cause": "Drum has four cells, other models one; unknown actuators omitted",
        "correction": "No raw-mass winner; four/twelve bookkeeping remains lower-bound material only",
        "verification": "Material CG/inertia/BOM identity",
        "state": "OPEN_SYSTEM_COMPARISON",
    },
]
(O / "ISSUES.json").write_text(json.dumps(issues, indent=2) + "\n")
# FMEA is qualitative: no fabricated occurrence/detection probabilities or RPN.
fmea = []
for mechanism, fault, consequence, control in [
    (
        "All",
        "Gate opens before fork capture",
        "Uncontained payload",
        "Independent positive barrier; two dissimilar seat/closed indications",
    ),
    (
        "All",
        "Shared path obstructed",
        "Remaining cells cannot deploy safely",
        "Fail locked; verify physical safe path before supervised continuation",
    ),
    (
        "Lead screw",
        "Nut jam/backdrive",
        "Stalled or uncontrolled transfer",
        "Torque limit, positive independent brake/capture; do not rely on friction self-lock",
    ),
    (
        "Spring",
        "Governor/gate fails",
        "Overspeed, double feed, end-stroke stall",
        "Two barriers, captured follower, governed energy dissipation",
    ),
    (
        "Rack",
        "Pawl bounce/tooth fracture",
        "Lost index or reverse travel",
        "Independent holdback, tooth proof and partial-stroke detection",
    ),
    (
        "Drum",
        "Index lock absent or stalls",
        "All payloads/common window unavailable",
        "Independent cell locks, hard index detent, swept-index proof",
    ),
    (
        "Pantograph",
        "Near-flat linkage/joint play",
        "High force, lateral motion, jam",
        "Angle stop, joint/preload budget, individual platform locks",
    ),
    (
        "Telescopic",
        "Stage order or stop fails",
        "Separation/binding",
        "Positive anti-separation stops, keyed overlap, stage position sensing",
    ),
    (
        "Belt",
        "Belt breaks/slips or creeps",
        "Position lost/uncontrolled carriage",
        "Independent capture rack, tension monitor, verified return path",
    ),
]:
    fmea.append(
        {
            "mechanism": mechanism,
            "fault": fault,
            "effect": consequence,
            "required_control": control,
            "verification": "Not physically demonstrated; component-specific design required",
            "probability": None,
        }
    )
(O / "FMEA.json").write_text(json.dumps(fmea, indent=2) + "\n")
lines = [
    "---",
    'title: "VOLLEY Gen6 — feeder engineering review"',
    'date: "19 October 2026 · FDR-08"',
    "geometry: margin=18mm",
    "fontsize: 10pt",
    "mainfont: DejaVu Sans",
    "---",
    "",
    "# Review disposition",
    "",
    "This is a computational candidate-design review, not a finished feeder, manufacturing release or qualified deployer. All seven mechanisms remain unselected. Gen5 is unchanged. The review provides actual native CAD/STEP, exact geometric checks, analytical load cases, native fixture FEA, fault requirements and retained negative findings. A collision-free pose is not proof that a mechanism can transmit load, complete a cycle or contain a payload after a fault.",
    "",
    "# Configuration and interfaces",
    "",
    "Dedicated 1U (113.5 × 100 × 100 mm) and 3U (340.5 × 100 × 100 mm) passive payload surrogates transfer 200 mm laterally. Nominal payload masses are 1.33/4 kg; adverse cases use 2/6 kg. Dimensions and 5/10/25 g loads are provisional sensitivity inputs, not provider-approved limits. X is the launch direction; Y is feed; Z is normal. Receiver, upper clearances and overhead gate actuation require host accommodation. Ordinary passive CubeSat compatibility has not been demonstrated.",
    "",
    "The common topology uses a storage gate, front/rear captive transfer members, guides, receiving gate/clamps and an independent arrest requirement. The native Part solids are editable from the Python builder and individually inspectable in FCStd. Thread, gear, pivot, coupling, bolt, harness and purchased internals are incomplete. The pantograph is a transfer linkage example, not the previously proposed independently collapsing multi-level magazine. The drum models a four-cell rotor; its indexing motion is not validated.",
    "",
    "# CAD evidence",
    "",
    "Fourteen native assemblies and 28 STEP files cover seven candidates × two sizes, with additional mid-transfer and seated 3U snapshots. The exact positive-volume intersection threshold is 0.0001 mm³. Nine feed stations, one stowed pose and five gate heights give 210 inspections. The rectangular payload sweep is exact only for the stipulated straight translation against fixed feed-state geometry; it does not certify nonlinear mechanisms or handoff. Zero-volume touching surfaces do not establish a joint.",
    "",
    "| Candidate / class | Material [kg] | Positive-volume pairs across poses | Payload-sweep penetrations |",
    "|:--|--:|--:|--:|",
]
for r in cad["reports"]:
    cc = sum(len(x["intersections"]) for x in r["motion_stations"])
    sw = len(r["continuous_translational_payload_sweep"]["unresolved_penetrations"])
    lines.append(
        f"| {r['candidate']} / {r['payload_class']} | {r['modeled_material_kg']:.3f} | {cc} | {sw} |"
    )
lines += [
    "",
    "Mass is modeled material, excluding payload and all unrated actuator/sensor envelopes. Drum values include four cells while other values represent a single cell, so these numbers cannot rank installed systems. METROLOGY.json reports material-only CG, inertia and bounding boxes. BOM.csv retains every modeled part and omission. Four/twelve assemblies cannot be inferred by simply multiplying these values.",
    "",
    "# Drive and tolerance calculations",
    "",
    "Triangular motion uses v_max = 2s/T and a = 4s/T². Required output force is F = (m_payload + m_moving)a + R. The square-thread screw model uses lead angle λ, friction angle φ, torque F d_m tan(λ+φ)/2 and efficiency tan λ/tan(λ+φ). Bearings, preload, motor/inverter losses and acceleration of unmodeled mechanisms are omitted. The 2/5/10 s cases demand 6000/2400/1200 rpm for a 2 mm lead. A torque-only motor choice would be inadequate. The model is not an actual Tr8 trapezoidal thread rating.",
    "",
    "![Parameterized drive demand](release/figures/loads.png)",
    "",
    "108 common load cases retain force, energy, speed, torque, spring shear, scissor input and arrest sensitivities. The spring has 86.4 N/m stiffness, 32.28 N initial and 15 N end force, 4.728 J release energy and approximately 1032 MPa initial calculated wire shear. No fatigue/material allowable exists. It stalls the 20/50 N resistance screens even when a gross energy comparison appears sufficient. Scissor input rises as 3F cot θ at the 10° lower-angle assumption. Pawl delay/compliance estimates are travel and mean force, not measured peak contact loads.",
    "",
    "![Adverse fit screen](release/figures/tolerance.png)",
    "",
    "The fit stack subtracts two 0.15 mm manufacturing allowances, 200 tan θ and assumed differential thermal expansion from a 2 mm nominal side gap. The 0.1° band retains positive nominal gap; adverse 0.5° cases fail. Loaded deflection, real payload expansion, geometric tolerances and actual rail alignment require further analysis.",
    "",
    "# Native structural screen",
    "",
    "![CalculiX convergence](release/figures/fea_convergence.png)",
    "",
    "CalculiX 2.23 ran six C3D8I solid cases. The floor blank uses assumed E = 69 GPa and ν = 0.33, uniform 6 kg × 25 g load (1471 N), with both short edges fully fixed. This is an explicit fixture, not the real mounting interface. The finest 3U maximum normal displacement is approximately 1.308 mm; its last displacement change is approximately 1.58%. Peak support stress remains mesh-sensitive. No strength margin, allowable, assembly qualification or payload safety follows. Raw INP, DAT, FRD and solver logs are retained.",
    "",
    "# Fault containment and operating sequence",
    "",
    "The required sequence is storage locked → fork captures → storage gate opens → supervised transfer → receiver captures → fork releases/retracts → cell closes → shot enabled → carrier captured/home → reset. Every transition needs a positively retained payload and independently verified path. The CAD seated pose is not proof of that transition sequence. In particular, the front-barrier retraction, receiver capture and fork return need full kinematic/contact implementation.",
    "",
    "Thirty-six state/fault requirement records include power loss, stall, sensor disagreement, timeout, double feed and reset. Their containment statements assume the stipulated barrier actually holds. They do not prove that a modeled pawl is engaged. Other cells remain inhibited until supervised safe-path verification. FMEA.json records principal failure modes without invented probabilities. Single-barrier failure can defeat containment; this is a design requirement, not a demonstrated redundant mechanism.",
    "",
    "# Weighted trade and decision",
    "",
    "Safety 35%, packaging/mass 25%, positioning 20%, cycle/power 10%, manufacture 10%. The earlier ordinal 1–5 scores and ±1 intervals remain hypotheses. Quantitative CAD/load evidence is reported separately so that unmeasured reliability is not converted into false numerical confidence.",
    "",
    "| Candidate | Hypothesis /5 | ±1 interval | Baseline eligible |",
    "|:--|--:|:--|:--|",
]
for r in trade:
    lines.append(
        f"| {r['candidate']} | {r['hypothesis_score']:.3f} | {r['lower_one_point']:.3f}–{r['upper_one_point']:.3f} | No |"
    )
lines += [
    "",
    "The lead screw remains a useful reversible transfer reference; spring/two-gate remains the low-drive-energy challenger and pantograph the compact-linkage challenger. This is a study recommendation, not final selection. The score intervals overlap and none has complete same-boundary installed mass, source-rated drive, full-cycle clearance, loaded restraint/contact or fault proof. The evidence is insufficient to release a controlled feeder baseline. No alternative is falsely marked rejected. All remain preserved in Labs.",
    "",
    "# Corrective actions and verification",
    "",
    "| ID | Finding and disposition |",
    "|:--|:--|",
]
for r in issues:
    lines.append(
        f"| {r['id']} | {r['issue']}. {r['correction']}. **{r['state'].replace('_', ' ').lower()}**. {r['verification']}. |"
    )
lines += [
    "",
    "# Candidate geometry views",
    "",
    "These orthographic wireframes are generated from independent native STEP readback. They are not solver screenshots or hardware photographs. JPEG previews are accompanied by vector SVG/PDF. The assembly bounding boxes and datums are recorded in STEP_VIEWS.json. No manufacturing tolerance/finish approval is implied.",
]
for c in [
    "lead_screw",
    "spring_dual_gate",
    "rack_pawl",
    "indexed_drum",
    "pantograph",
    "telescopic",
    "belt_shuttle",
]:
    lines += [
        "",
        f'## {c.replace("_"," ").title()}',
        f"![{c} STEP geometry](release/figures/{c}_cad.png)",
    ]
lines += [
    "",
    "# Research basis",
    "",
    "The prior concept/trade/load records are retained in docs/GEN6_FEEDER_CONCEPT_TRADE.md, GEN6_FEEDER_WEIGHTED_TRADE_2026_10_12.md and GEN6_FEEDER_LOAD_SCREEN.md. The seven concepts are engineering analogies; none inherits flight heritage merely from using screws, springs or a familiar indexer.",
    "",
    "Fusaro and Khonsari, *Liquid Lubrication for Space Applications*, NASA TM-105198 (1992), public NTRS record 19920022596, discusses vacuum/environmental effects, bearing anomalies, lubricant/material selection and life. Selected full-text passages were examined for mechanism implications; it does not supply VOLLEY friction or life data. https://ntrs.nasa.gov/citations/19920022596",
    "",
    "The *46th Aerospace Mechanisms Symposium Proceedings* (2022), NTRS 20220006415, includes *Engineering Design of a Thruster Pointing Mechanism (TPM-250) for Deep Space and IOS Nanosats*, pp.143–158. Its lead-screw/worm sizing explicitly accounts for efficiency/backlash and measured friction factors; these values are specific to its mechanism and are not transferred to VOLLEY. The GRASS rotation-mechanism paper (pp.159–172) highlights mounting-induced stress/alignment sensitivity. These findings support including tribology, installed mounting and backlash in the remaining verification. https://ntrs.nasa.gov/citations/20220006415",
    "",
    "The review is not ECSS/NASA compliance certification, an independent expert review or a claim of P-POD-class reliability. Acceptance is limited to the stated computational boundaries; no build release is granted.",
]
tooth = load("ARREST_TOOTH.json")
idx = lines.index("# Weighted trade and decision")
lines[idx:idx] = [
    "# Capture-tooth sizing failure",
    "",
    f"The modeled rack tooth is 8 mm wide, 1 mm thick at the root and 3 mm high. A rectangular cantilever sensitivity uses the calculated mean arrest forces, assumed steel E=200 GPa and 250/500/1000 MPa yield bands. Across 972 cases, maximum mean force is {tooth['max_mean_force_N']:.1f} N and nominal root bending is {tooth['max_nominal_bending_MPa']:.0f} MPa. Cases exceed even the 1000 MPa band. These are not material allowables or peak impact forces. The present pawl is not engaged; neither the tooth nor a positive retention path is accepted. Larger section, controlled stopping energy and real engagement/contact require redesign. ARREST_TOOTH.json retains every case.",
    "",
]
issues.append(
    {
        "id": "FDR-I11",
        "issue": "Capture tooth cannot support adverse mean-arrest screens",
        "cause": "1mm root section and short stopping compliance",
        "correction": "Re-size section and stopping compliance/energy; model engagement and joint load path",
        "verification": "972 cantilever sensitivity cases; no selected material or peak contact model",
        "state": "FAILED_SIZING_RETAINED",
    }
)
(O / "ISSUES.json").write_text(json.dumps(issues, indent=2) + "\n")
lines += [
    "",
    "# Genuine native application and result views",
    "",
    "The following FreeCAD image is the actual Python-hosted Qt/Coin application viewport of the stored native candidate. It is not a Blender render or fabricated application UI.",
    "",
    "![FreeCAD native candidate viewport](release/captures/FreeCAD_lead_screw_3U.png)",
    "",
    "The Gmsh native viewport below displays the actual CalculiX C3D8I input mesh and DAT displacement norm in metres, on undeformed geometry. It remains the assumed clamped-floor fixture; no actual mounting or assembly qualification follows.",
    "",
    "![Native CalculiX data in Gmsh4.14.1](release/fea/Gmsh_CalculiX_floor.png)",
]
lines += [
    "",
    "# Reproduction",
    "",
    "Install the versions in requirements-python.txt for numerical reports/plots. Native CAD uses FreeCAD1.0/OpenCascade7.8.1 and its system Python; run build.py, metrology.py and project_step.py in that environment. Run analyze.py, arrest_tooth.py, plot.py and review.py using the numerical environment. fea_floor.py requires the CalculiX2.23 executable in CCX and its native runtime dependencies; retained inputs/DAT/FRD/logs permit inspection without rerunning the solver. view_fea.py uses Gmsh4.14.1 to display those actual results. capture_native.py requires the FreeCAD Qt display. No native GUI capture is generated by Matplotlib. Compile this README to PDF with pandoc/XeLaTeX, using this directory as the resource path.",
]
(H / "README.md").write_text("\n".join(lines) + "\n")
print(
    "Engineering review, explicit issues/FMEA, material BOM and uncertainty-qualified trade assembled"
)
