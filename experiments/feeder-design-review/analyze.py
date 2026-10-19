"""Common-boundary feeder loads, tolerance and finite-state fault cases.

Analytical/model checks only. No measured reliability or hardware qualification.
"""

from pathlib import Path
import math, json, itertools, hashlib

H = Path(__file__).resolve().parent
P = json.loads((H / "requirements.json").read_text())
O = H / "release"
O.mkdir(exist_ok=True)
G = 9.80665


def calculate():
    rows = []
    masses = sorted(
        set([x[k] for x in P["payloads"] for k in ["nominal_kg", "upper_study_kg"]])
    )
    for m, T, R, mv in itertools.product(
        masses,
        P["transfer_duration_s"],
        P["resistance_N"],
        P["moving_drive_allowance_kg"],
    ):
        s = P["stroke_mm"] / 1000
        v = 2 * s / T
        a = 4 * s / T**2
        M = m + mv
        F = M * a + R
        lead = P["screw_lead_mm"] / 1000
        dm = P["screw_mean_diameter_mm"] / 1000
        lam = math.atan(lead / (math.pi * dm))
        screw = []
        for mu in P["thread_friction"]:
            phi = math.atan(mu)
            torque = F * dm / 2 * math.tan(lam + phi)
            screw.append(
                {
                    "assumed_thread_mu": mu,
                    "raising_torque_N_m": torque,
                    "raising_efficiency": math.tan(lam) / math.tan(lam + phi),
                    "static_self_locking_ideal": phi > lam,
                }
            )
        k = P["spring_k_N_m"]
        f0 = P["spring_end_force_N"] + k * s
        E = P["spring_end_force_N"] * s + 0.5 * k * s * s
        work = R * s + 0.5 * M * v * v
        # Wahl correction for round-wire helical spring; fatigue/material limits not supplied.
        C = P["spring_mean_diameter_mm"] / P["spring_wire_diameter_mm"]
        wahl = (4 * C - 1) / (4 * C - 4) + 0.615 / C
        tau = (
            wahl
            * 8
            * f0
            * (P["spring_mean_diameter_mm"] / 1000)
            / (math.pi * (P["spring_wire_diameter_mm"] / 1000) ** 3)
        )
        fault = []
        for delay, compliance in itertools.product(
            P["power_loss_response_s"], P["arrest_compliance_mm"]
        ):
            drift = P["pawl_pitch_mm"] / 1000 + v * delay + 0.5 * a * delay**2
            energy = 0.5 * M * (v + a * delay) ** 2
            fault.append(
                {
                    "response_s": delay,
                    "compliance_mm": compliance,
                    "upper_travel_before_contact_mm": drift * 1000,
                    "mean_arrest_force_N": energy / (compliance / 1000) + R,
                    "not_established": "peak contact force, actual response or engagement reliability",
                }
            )
        rows.append(
            {
                "payload_kg": m,
                "moving_allowance_kg": mv,
                "duration_s": T,
                "resistance_N": R,
                "peak_speed_m_s": v,
                "acceleration_m_s2": a,
                "required_output_force_N": F,
                "positive_work_floor_J": work,
                "screw": screw,
                "screw_peak_rpm": 60 * v / lead,
                "spring": {
                    "initial_force_N": f0,
                    "end_force_N": P["spring_end_force_N"],
                    "released_J": E,
                    "force_floor_sufficient": P["spring_end_force_N"] >= F,
                    "energy_floor_sufficient": E >= work,
                    "initial_wire_shear_MPa": tau / 1e6,
                    "material_fatigue_allowable": None,
                    "governor_energy_J": max(0, E - work),
                },
                "pantograph_peak_input_N": P["pantograph_stages"]
                * F
                / math.tan(math.radians(P["pantograph_theta_min_deg"])),
                "rack_ideal_pinion_torque_N_m": F * 0.014,
                "belt_ideal_pulley_torque_N_m": F * 0.012,
                "power_off_capture": fault,
            }
        )
    tolerance = []
    for payload, angle, temp in itertools.product(
        P["payloads"], P["alignment_deg"], P["temperature_C"]
    ):
        # Conservative differential expansion against a dimensionally fixed payload boundary.
        thermal = (
            P["aluminium_cte_K"]
            * payload["length_mm"]
            * abs(temp - P["reference_temperature_C"])
        )
        manufacture = 2 * P["manufacturing_each_mm"]
        angular = P["stroke_mm"] * math.tan(math.radians(angle))
        res = P["side_clearance_mm"] - thermal - manufacture - angular
        tolerance.append(
            {
                "payload": payload["class"],
                "alignment_deg": angle,
                "temperature_C": temp,
                "manufacturing_stack_mm": manufacture,
                "angular_stack_mm": angular,
                "thermal_stack_mm": thermal,
                "remaining_gap_mm": res,
                "screen_pass": res > 0,
            }
        )
    retention = []
    for m, g in itertools.product(masses, P["launch_load_g"]):
        force = m * g * G
        area = 2 * math.pi * 4**2 / 4
        stress = force / area
        retention.append(
            {
                "payload_kg": m,
                "assumed_g": g,
                "force_N": force,
                "two_4mm_pins_shear_MPa": stress,
                "bearing_stress_3mm_ear_MPa": force / (2 * 4 * 3),
                "allowables": "Not selected; material/temperature/fatigue/load-path verification required",
            }
        )
    # Containment invariants refer to explicitly stipulated physical lock states.
    states = [
        ("stored", True, False, False),
        ("fork_capture", True, True, False),
        ("transfer", False, True, False),
        ("receiver_capture", False, True, True),
        ("fork_release", False, False, True),
        ("reset", True, False, True),
    ]
    faults = []
    for state, stored, fork, receiver in states:
        for failure in [
            "power_loss",
            "motor_stall",
            "sensor_disagreement",
            "command_timeout",
            "double_feed_request",
            "reset_request",
        ]:
            contained = stored or fork or receiver
            faults.append(
                {
                    "state": state,
                    "fault": failure,
                    "positive_barrier_required": (
                        "storage" if stored else "fork" if fork else "receiver"
                    ),
                    "inhibit_shot": True,
                    "automatic_retry": False,
                    "logical_containment_if_barrier_holds": contained,
                    "continue_other_cells": False,
                    "may_request_supervised_other_cell_after_path_proof": state
                    in ["stored", "reset"],
                    "path_verification_required": True,
                }
            )
    return {
        "revision": P["revision"],
        "model_boundary": "Analytical sizing and stipulated-barrier logic; not physical validation",
        "case_count": len(rows),
        "cases": rows,
        "tolerances": tolerance,
        "storage_restraint": retention,
        "fault_cases": faults,
        "spring_geometry": {
            "stowed_length_mm": 180,
            "extended_length_mm": 380,
            "required_free_length_mm": 380
            + 1000 * P["spring_end_force_N"] / P["spring_k_N_m"],
            "solid_length_mm": P["spring_active_turns"] * P["spring_wire_diameter_mm"],
            "k_from_wire_N_m": P["spring_shear_modulus_Pa"]
            * (P["spring_wire_diameter_mm"] / 1000) ** 4
            / (
                8
                * (P["spring_mean_diameter_mm"] / 1000) ** 3
                * P["spring_active_turns"]
            ),
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inputs_sha256": hashlib.sha256(
            (H / "requirements.json").read_bytes()
        ).hexdigest(),
    }


if __name__ == "__main__":
    d = calculate()
    assert d["case_count"] == 108
    assert all(x["logical_containment_if_barrier_holds"] for x in d["fault_cases"])
    assert all(x["screen_pass"] for x in d["tolerances"] if x["alignment_deg"] == 0.1)
    assert any(
        not x["screen_pass"] for x in d["tolerances"] if x["alignment_deg"] == 0.5
    )
    assert abs(d["spring_geometry"]["k_from_wire_N_m"] - P["spring_k_N_m"]) < 1e-10
    (O / "LOAD_FAULT_REPORT.json").write_text(json.dumps(d, indent=2) + "\n")
    print(
        "108 common load cases; 12 tolerance cases; 36 stipulated-barrier fault cases checked. Adverse 0.5-degree fits and spring force failures retained."
    )
