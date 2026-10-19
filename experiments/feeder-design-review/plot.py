"""Scientific plots and STEP-derived orthographic views; not GUI screenshots."""

from pathlib import Path
import json
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

H = Path(__file__).resolve().parent
O = H / "release"
F = O / "figures"
F.mkdir(exist_ok=True)
plt.style.use(H.parents[1] / "tools/scientific.mplstyle")


def save(fig, name):
    for ext in ["png", "svg", "pdf"]:
        p = F / (name + "." + ext)
        fig.savefig(p, bbox_inches="tight")
        if ext == "svg":
            p.write_text(
                "\n".join(l.rstrip() for l in p.read_text().splitlines()) + "\n"
            )
    plt.close(fig)


for r in json.loads((O / "STEP_VIEWS.json").read_text()):
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.5))
    for ax, axes, labels in [
        (axs[0], [0, 1], ["X / launch direction [mm]", "Y / feed direction [mm]"]),
        (axs[1], [1, 2], ["Y / feed direction [mm]", "Z [mm]"]),
    ]:
        seg = [[[p[axes[0]], p[axes[1]]] for p in edge] for edge in r["edges"]]
        ax.add_collection(
            LineCollection(seg, colors="#465865", linewidths=0.35, alpha=0.8)
        )
        ax.autoscale()
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(
        r["candidate"].replace("_", " ") + " · 3U nominal stowed geometry", fontsize=12
    )
    fig.text(
        0.02,
        0.01,
        "Independent FreeCAD/OCC STEP readback. Orthographic wireframe, not hardware or verified full-cycle motion.\nUnselected drive, sensors, contact/load paths and actual host interface remain open.",
        fontsize=8,
    )
    fig.subplots_adjust(bottom=0.24, wspace=0.35)
    save(fig, r["candidate"] + "_cad")
    # JPEG requested for CAD previews, with SVG/PDF retained for line-art use.
    from PIL import Image

    Image.open(F / (r["candidate"] + "_cad.png")).convert("RGB").save(
        F / (r["candidate"] + "_cad.jpg"), quality=94
    )
d = json.loads((O / "LOAD_FAULT_REPORT.json").read_text())
rows = [
    c
    for c in d["cases"]
    if c["payload_kg"] == 6
    and c["moving_allowance_kg"] == 0.5
    and c["resistance_N"] == 20
]
fig, axs = plt.subplots(1, 2, figsize=(8, 4))
axs[0].plot(
    [r["duration_s"] for r in rows],
    [r["required_output_force_N"] for r in rows],
    "o-",
    label="6 kg payload + 0.5 kg allowance",
)
axs[0].axhline(15, color="#d55e00", ls="--", label="Modeled spring end force")
axs[0].set(
    xlabel="Transfer duration [s]",
    ylabel="Output force [N]",
    title="Resistance and acceleration",
)
axs[0].legend(fontsize=8)
for r in rows:
    axs[1].plot(
        [x["assumed_thread_mu"] for x in r["screw"]],
        [x["raising_torque_N_m"] for x in r["screw"]],
        "o-",
        label=str(r["duration_s"]) + " s",
    )
axs[1].set(
    xlabel="Assumed thread friction coefficient",
    ylabel="Idealized raising torque [N m]",
    title="Tr8×2 screw screen",
)
axs[1].legend()
fig.subplots_adjust(bottom=0.25, wspace=0.4)
fig.text(
    0.02,
    0.01,
    "Parameterized loads and square-thread mechanics; no selected actuator, friction measurement or component rating.",
    fontsize=8,
)
save(fig, "loads")
fig, ax = plt.subplots(figsize=(7.1, 4))
groups = {}
for r in d["tolerances"]:
    if r["temperature_C"] != 80:
        continue
    groups[(r["payload"], r["alignment_deg"])] = r["remaining_gap_mm"]
labels = [f"{a}, {b}°" for a, b in groups]
vals = list(groups.values())
ax.bar(labels, vals, color=["#0072b2" if v > 0 else "#d55e00" for v in vals])
ax.axhline(0, color="black", lw=0.8)
ax.set(
    ylabel="Remaining nominal side gap [mm]",
    title="Adverse thermal/manufacturing/alignment stack",
)
fig.subplots_adjust(bottom=0.24)
fig.text(
    0.02,
    0.01,
    "80°C versus 20°C datum; differential expansion assumed. 0.5° case fails; no manufactured fit verified.",
    fontsize=8,
)
save(fig, "tolerance")
fea = json.loads((O / "fea/RESULTS.json").read_text())
fig, axs = plt.subplots(1, 2, figsize=(8, 4))
for label in ["1U", "3U"]:
    r = [x for x in fea["cases"] if x["case"].startswith(label)]
    axs[0].plot(
        [x["elements"] for x in r],
        [x["max_abs_uz_m"] * 1000 for x in r],
        "o-",
        label=label,
    )
    axs[1].plot(
        [x["elements"] for x in r],
        [x["max_von_mises_Pa"] / 1e6 for x in r],
        "o-",
        label=label,
    )
axs[0].set(xlabel="C3D8I elements", ylabel="Maximum normal displacement [mm]")
axs[1].set(xlabel="C3D8I elements", ylabel="Peak reported von Mises stress [MPa]")
axs[0].legend()
axs[1].legend()
fig.subplots_adjust(bottom=0.25, wspace=0.4)
fig.suptitle("Native CalculiX 2.23 · assumed clamped floor fixture")
fig.text(
    0.02,
    0.01,
    "6 kg × 25 g, E=69 GPa, ν=0.33. Peak support stress is not converged or an assembly allowable.\nActual mounts, joints and contact are absent; this is not launch qualification.",
    fontsize=8,
)
save(fig, "fea_convergence")
print("STEP-derived CAD JPEG/SVG/PDF and load/tolerance/native-FEA figures written")
