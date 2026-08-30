"""Run my VLAB-X001 reduced-order quadrant gas-bearing screen."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "parameters.json"
ARTIFACTS = HERE / "artifacts"
G0 = 9.81


@dataclass(frozen=True)
class PadGeometry:
    area_m2: float
    width_m: float
    clearance_m: float
    exit_length_m: float
    restrictor_diameter_m: float


def load_parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def inherited_target(parameters: dict, name: str) -> dict:
    target = dict(parameters["targets"][name])
    parent = target.pop("inherits", None)
    if parent:
        merged = inherited_target(parameters, parent)
        merged.update(target)
        target = merged
    return target


def viscosity(physics: dict, temperature_k: float) -> float:
    # Sutherland scaling anchored to the frozen 300 K value; this is a gas-property correction,
    # not a fitted bearing parameter.
    mu0 = physics["dynamic_viscosity_pa_s_at_300k"]
    sutherland_k = 111.0
    return mu0 * (temperature_k / 300.0) ** 1.5 * (300.0 + sutherland_k) / (temperature_k + sutherland_k)


def mean_free_path(physics: dict, pressure_pa: float, temperature_k: float) -> float:
    kb = 1.380649e-23
    diameter = physics["molecular_collision_diameter_m"]
    return kb * temperature_k / (math.sqrt(2.0) * math.pi * diameter**2 * max(pressure_pa, 1e-30))


def pad_geometry(target: dict) -> PadGeometry:
    if target["guide_type"] == "round":
        width = target["pocket_arc_fraction_of_quadrant"] * math.pi * target["bore_diameter_m"] / 4.0
        length = target["pocket_axial_length_m"]
    else:
        width = target["pocket_width_m"]
        length = target["pocket_axial_length_m"]
    return PadGeometry(
        area_m2=width * length,
        width_m=width,
        clearance_m=target["nominal_clearance_m"],
        exit_length_m=target["film_exit_length_m"],
        restrictor_diameter_m=target["restrictor_diameter_m"],
    )


def orifice_mass_flow(physics: dict, supply_pa: float, pocket_pa: float, temperature_k: float,
                      area_multiplier: float = 1.0) -> float:
    if supply_pa <= pocket_pa:
        return 0.0
    gamma = physics["heat_capacity_ratio"]
    gas_r = physics["specific_gas_constant_j_kg_k"]
    cd = physics["orifice_discharge_coefficient"]
    ratio = max(pocket_pa / supply_pa, 0.0)
    critical = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
    if ratio <= critical:
        flow_function = math.sqrt(gamma) * (2.0 / (gamma + 1.0)) ** (
            (gamma + 1.0) / (2.0 * (gamma - 1.0))
        )
    else:
        term = 2.0 * gamma / (gamma - 1.0) * (
            ratio ** (2.0 / gamma) - ratio ** ((gamma + 1.0) / gamma)
        )
        flow_function = math.sqrt(max(term, 0.0))
    diameter = current_pad_geometry.restrictor_diameter_m
    area = math.pi * diameter**2 / 4.0 * area_multiplier
    return cd * area * supply_pa / math.sqrt(gas_r * temperature_k) * flow_function


def film_mass_flow(physics: dict, pocket_pa: float, gap_m: float, temperature_k: float) -> float:
    ambient = physics["ambient_pressure_pa"]
    gas_r = physics["specific_gas_constant_j_kg_k"]
    mu = viscosity(physics, temperature_k)
    exits = physics["film_exit_count_per_pocket"]
    coefficient = (
        exits * current_pad_geometry.width_m * max(gap_m, 1e-12) ** 3
        / (24.0 * mu * gas_r * temperature_k * current_pad_geometry.exit_length_m)
    )
    return coefficient * max(pocket_pa**2 - ambient**2, 0.0)


current_pad_geometry: PadGeometry


def pocket_state(physics: dict, supply_pa: float, gap_m: float, temperature_k: float,
                 fault: str | None = None) -> tuple[float, float, float]:
    """Return pocket pressure, mass flow, and relative mass-balance residual."""
    ambient = physics["ambient_pressure_pa"]
    if supply_pa <= ambient:
        return ambient, 0.0, 0.0
    if fault == "stuck_open":
        pressure = supply_pa
        return pressure, film_mass_flow(physics, pressure, gap_m, temperature_k), 0.0
    if fault == "stuck_closed":
        return ambient, 0.0, 0.0
    area_multiplier = 1.1 if fault == "inlet_area_plus_10pct" else 1.0

    # Most of this screen is on the choked branch. There the inlet flow is constant and the
    # parallel-plate outlet is C*(p^2-pa^2), so the pressure root is exact in closed form. The
    # first implementation sent even this branch through Brent millions of times; it was stopped
    # before producing an artifact. I retain Brent only where the closed-form candidate crosses
    # the critical pressure ratio.
    gamma = physics["heat_capacity_ratio"]
    critical = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
    choked_inlet = orifice_mass_flow(physics, supply_pa, ambient, temperature_k, area_multiplier)
    unit_outlet = film_mass_flow(physics, math.sqrt(ambient**2 + 1.0), gap_m, temperature_k)
    candidate = math.sqrt(ambient**2 + choked_inlet / max(unit_outlet, 1e-300))
    if candidate / supply_pa <= critical:
        outlet = film_mass_flow(physics, candidate, gap_m, temperature_k)
        relative = abs(choked_inlet - outlet) / max(choked_inlet, outlet, 1e-30)
        return candidate, 0.5 * (choked_inlet + outlet), relative

    def residual(pressure: float) -> float:
        return orifice_mass_flow(physics, supply_pa, pressure, temperature_k, area_multiplier) - film_mass_flow(
            physics, pressure, gap_m, temperature_k
        )

    pressure = brentq(residual, ambient, supply_pa, rtol=1e-12, xtol=1e-8)
    inlet = orifice_mass_flow(physics, supply_pa, pressure, temperature_k, area_multiplier)
    outlet = film_mass_flow(physics, pressure, gap_m, temperature_k)
    relative = abs(inlet - outlet) / max(inlet, outlet, 1e-30)
    return pressure, 0.5 * (inlet + outlet), relative


def guide(target: dict, x_m: float, amplitude_m: float, phase: float) -> tuple[float, float, float, float]:
    # Each axis receives amplitude/sqrt(2), so the declared amplitude is a radial envelope rather
    # than being applied twice on a diagonal.
    amp = amplitude_m / math.sqrt(2.0)
    wave = 2.0 * math.pi / target["guide_spatial_period_m"]
    y = amp * math.sin(wave * x_m + phase)
    z = amp * math.sin(wave * x_m + phase + 0.5 * math.pi)
    yp = amp * wave * math.cos(wave * x_m + phase)
    zp = amp * wave * math.cos(wave * x_m + phase + 0.5 * math.pi)
    return y, z, yp, zp


def bearing_loads(parameters: dict, target: dict, x_m: float, state: np.ndarray, supply_pa: float,
                  temperature_k: float, amplitude_m: float, phase: float,
                  cg_offset_m: float, fault: str | None = None) -> dict:
    global current_pad_geometry
    current_pad_geometry = pad_geometry(target)
    _time, _velocity, _gas, y, _vy, z, _vz, theta_y, _wy, theta_z, _wz, _used = state
    station_half = target["station_separation_m"] / 2.0
    gy = cg_offset_m / math.sqrt(2.0)
    gz = -cg_offset_m / math.sqrt(2.0)
    fy = fz = moment_y = moment_z = total_flow = 0.0
    min_gap = float("inf")
    max_pressure = parameters["physics"]["ambient_pressure_pa"]
    min_pressure = supply_pa
    max_residual = 0.0
    pocket_records = []
    affected = "front_positive_y"
    for station_name, station in (("front", station_half), ("rear", -station_half)):
        yc, zc, _ys, _zs = guide(target, x_m + station, amplitude_m, phase)
        axis_y = (y - gy) + station * theta_z
        axis_z = (z - gz) - station * theta_y
        dy, dz = axis_y - yc, axis_z - zc
        local = {}
        for face, gap in (
            ("positive_y", current_pad_geometry.clearance_m - dy),
            ("negative_y", current_pad_geometry.clearance_m + dy),
            ("positive_z", current_pad_geometry.clearance_m - dz),
            ("negative_z", current_pad_geometry.clearance_m + dz),
        ):
            pocket_name = f"{station_name}_{face}"
            applied_fault = fault if pocket_name == affected else None
            pressure, flow, residual = pocket_state(
                parameters["physics"], supply_pa, max(gap, 1e-12), temperature_k, applied_fault
            )
            force = (pressure - parameters["physics"]["ambient_pressure_pa"]) * current_pad_geometry.area_m2
            local[face] = force
            total_flow += flow
            min_gap = min(min_gap, gap)
            max_pressure = max(max_pressure, pressure)
            min_pressure = min(min_pressure, pressure)
            max_residual = max(max_residual, residual)
            pocket_records.append((pocket_name, pressure, gap, flow))
        station_fy = local["negative_y"] - local["positive_y"]
        station_fz = local["negative_z"] - local["positive_z"]
        fy += station_fy
        fz += station_fz
        moment_y += -station * station_fz
        moment_z += station * station_fy
    return {
        "force_y_n": fy,
        "force_z_n": fz,
        "moment_y_nm": moment_y,
        "moment_z_nm": moment_z,
        "mass_flow_kg_s": total_flow,
        "minimum_gap_m": min_gap,
        "minimum_pressure_pa": min_pressure,
        "maximum_pressure_pa": max_pressure,
        "maximum_mass_residual_fraction": max_residual,
        "pockets": pocket_records,
    }


def axial_baseline(target: dict) -> tuple[float, float]:
    mass = target["moving_mass_kg"]
    if target["axial_model"].startswith("closed_adiabatic"):
        p0 = target["initial_supply_pressure_pa"]
        v0 = target["initial_chamber_volume_m3"]
        area = target["piston_area_m2"]
        gamma = 1.4
        v1 = v0 + area * target["stroke_m"]
        work = p0 * v0**gamma * (v1 ** (1.0 - gamma) - v0 ** (1.0 - gamma)) / (1.0 - gamma)
        work -= target["axial_friction_n"] * target["stroke_m"]
        velocity = math.sqrt(max(2.0 * work / mass, 0.0))
        acceleration = (p0 * area - target["axial_friction_n"]) / mass
    else:
        acceleration = target["mean_supply_pressure_pa"] * target["piston_area_m2"] / mass
        velocity = math.sqrt(2.0 * acceleration * target["stroke_m"])
    return velocity, acceleration / G0


def simulate_case(parameters: dict, name: str, target: dict, temperature_k: float,
                  amplitude_m: float, phase: float, cg_offset_m: float, centroid_error_m: float,
                  max_step_m: float, fault: str | None = None) -> dict:
    physics = parameters["physics"]
    global current_pad_geometry
    current_pad_geometry = pad_geometry(target)
    baseline_velocity, baseline_accel_g = axial_baseline(target)
    mass_body = target["moving_mass_kg"]
    inertia = target["transverse_inertia_kg_m2"] + mass_body * cg_offset_m**2
    gy = cg_offset_m / math.sqrt(2.0)
    gz = -cg_offset_m / math.sqrt(2.0)
    x0 = 1e-7
    if target["axial_model"].startswith("closed_adiabatic"):
        supply0 = target["initial_supply_pressure_pa"]
        accel0 = (supply0 * target["piston_area_m2"] - target["axial_friction_n"]) / mass_body
        gas0 = supply0 * target["initial_chamber_volume_m3"] / (
            physics["specific_gas_constant_j_kg_k"] * temperature_k
        )
    else:
        supply0 = target["mean_supply_pressure_pa"]
        accel0 = supply0 * target["piston_area_m2"] / mass_body
        gas0 = target["baseline_gas_allowance_kg"]
    velocity0 = math.sqrt(max(2.0 * accel0 * x0, 1e-12))
    y0, z0, yp0, zp0 = guide(target, x0, amplitude_m, phase)
    state0 = np.array([
        velocity0 / max(accel0, 1e-12), velocity0, gas0,
        y0 + gy, yp0 * velocity0, z0 + gz, zp0 * velocity0,
        -zp0, 0.0, yp0, 0.0, 0.0,
    ])
    peak = {
        "acceleration_g": 0.0,
        "pressure_pa": 0.0,
        "mass_residual": 0.0,
        "minimum_gap_m": float("inf"),
    }

    def rhs(x_m: float, state: np.ndarray) -> np.ndarray:
        velocity = max(state[1], 1e-8)
        if target["axial_model"].startswith("closed_adiabatic"):
            chamber_volume = target["initial_chamber_volume_m3"] + target["piston_area_m2"] * x_m
            density_ratio = (max(state[2], 1e-12) / gas0) * target["initial_chamber_volume_m3"] / chamber_volume
            supply = target["initial_supply_pressure_pa"] * max(density_ratio, 1e-12) ** physics["heat_capacity_ratio"]
            local_temperature = temperature_k * max(density_ratio, 1e-12) ** (physics["heat_capacity_ratio"] - 1.0)
            axial_force = supply * target["piston_area_m2"] - target["axial_friction_n"]
        else:
            supply = target["mean_supply_pressure_pa"]
            local_temperature = temperature_k
            axial_force = supply * target["piston_area_m2"]
        loads = bearing_loads(
            parameters, target, x_m, state, supply, local_temperature, amplitude_m, phase,
            cg_offset_m, fault
        )
        axial_accel = axial_force / mass_body
        force_error_y = centroid_error_m / math.sqrt(2.0)
        force_error_z = -centroid_error_m / math.sqrt(2.0)
        moment_y = loads["moment_y_nm"] + force_error_z * axial_force
        moment_z = loads["moment_z_nm"] - force_error_y * axial_force
        peak["acceleration_g"] = max(peak["acceleration_g"], axial_accel / G0)
        peak["pressure_pa"] = max(peak["pressure_pa"], loads["maximum_pressure_pa"])
        peak["mass_residual"] = max(peak["mass_residual"], loads["maximum_mass_residual_fraction"])
        peak["minimum_gap_m"] = min(peak["minimum_gap_m"], loads["minimum_gap_m"])
        derivative = np.zeros(12)
        derivative[0] = 1.0 / velocity
        derivative[1] = axial_accel / velocity
        derivative[2] = -loads["mass_flow_kg_s"] / velocity if target["axial_model"].startswith("closed_adiabatic") else 0.0
        derivative[3] = state[4] / velocity
        derivative[4] = loads["force_y_n"] / (mass_body * velocity)
        derivative[5] = state[6] / velocity
        derivative[6] = loads["force_z_n"] / (mass_body * velocity)
        derivative[7] = state[8] / velocity
        derivative[8] = moment_y / (inertia * velocity)
        derivative[9] = state[10] / velocity
        derivative[10] = moment_z / (inertia * velocity)
        derivative[11] = loads["mass_flow_kg_s"] / velocity
        return derivative

    def gap_event(x_m: float, state: np.ndarray) -> float:
        if target["axial_model"].startswith("closed_adiabatic"):
            chamber_volume = target["initial_chamber_volume_m3"] + target["piston_area_m2"] * x_m
            density_ratio = (max(state[2], 1e-12) / gas0) * target["initial_chamber_volume_m3"] / chamber_volume
            supply = target["initial_supply_pressure_pa"] * max(density_ratio, 1e-12) ** physics["heat_capacity_ratio"]
            local_temperature = temperature_k * max(density_ratio, 1e-12) ** (physics["heat_capacity_ratio"] - 1.0)
        else:
            supply, local_temperature = target["mean_supply_pressure_pa"], temperature_k
        return bearing_loads(
            parameters, target, x_m, state, supply, local_temperature, amplitude_m, phase,
            cg_offset_m, fault
        )["minimum_gap_m"]

    gap_event.terminal = True
    gap_event.direction = -1
    solution = solve_ivp(
        rhs, (x0, target["stroke_m"]), state0, method="DOP853",
        rtol=parameters["solver"]["relative_ivp_tolerance"],
        atol=parameters["solver"]["absolute_ivp_tolerance"], max_step=max_step_m,
        events=gap_event,
    )
    final = solution.y[:, -1]
    completed = bool(solution.success and solution.t[-1] >= target["stroke_m"] * (1.0 - 1e-9))
    rates = {
        "pitch_deg_s": math.degrees(final[8]),
        "yaw_deg_s": math.degrees(final[10]),
        "roll_deg_s": 0.0,
    }
    active_velocity = float(final[1])
    if target["axial_model"].startswith("closed_adiabatic"):
        total_gas = target["baseline_gas_allowance_kg"]
    else:
        total_gas = target["baseline_gas_allowance_kg"] + float(final[11])
    return {
        "target": name,
        "temperature_k": temperature_k,
        "guide_amplitude_m": amplitude_m,
        "guide_phase_rad": phase,
        "cg_offset_m": cg_offset_m,
        "force_centroid_error_from_cg_m": centroid_error_m,
        "fault": fault or "none",
        "completed": completed,
        "termination_x_m": float(solution.t[-1]),
        "solver_success": bool(solution.success),
        "solver_message": solution.message,
        "function_evaluations": int(solution.nfev),
        "baseline_exit_velocity_m_s": baseline_velocity,
        "active_exit_velocity_m_s": active_velocity,
        "exit_velocity_change_fraction": abs(active_velocity - baseline_velocity) / max(baseline_velocity, 1e-30),
        "baseline_peak_acceleration_g": baseline_accel_g,
        "active_peak_acceleration_g": peak["acceleration_g"],
        "bearing_gas_mass_kg": float(final[11]),
        "total_gas_mass_kg": total_gas,
        "gas_fraction_of_baseline": total_gas / target["baseline_gas_allowance_kg"],
        "minimum_gap_m": peak["minimum_gap_m"],
        "maximum_pocket_pressure_pa": peak["pressure_pa"],
        "maximum_mass_residual_fraction": peak["mass_residual"],
        "exit_rates_deg_s": rates,
        "maximum_abs_exit_rate_deg_s": max(abs(value) for value in rates.values()),
    }


def response_map(parameters: dict, name: str, target: dict) -> list[dict]:
    global current_pad_geometry
    current_pad_geometry = pad_geometry(target)
    temperature = max(target["temperature_k"])
    supply = target.get("initial_supply_pressure_pa", target.get("mean_supply_pressure_pa"))
    clearance = current_pad_geometry.clearance_m
    records = []
    state = np.zeros(12)
    for fraction in parameters["solver"]["response_offset_fraction_of_clearance"]:
        state[3] = fraction * clearance
        loads = bearing_loads(parameters, target, 0.0, state, supply, temperature, 0.0, 0.0, 0.0)
        records.append({
            "target": name,
            "offset_fraction": fraction,
            "offset_m": fraction * clearance,
            "force_y_n": loads["force_y_n"],
            "restoring": loads["force_y_n"] * fraction < 0.0,
            "minimum_gap_m": loads["minimum_gap_m"],
            "maximum_pressure_pa": loads["maximum_pressure_pa"],
            "mass_flow_kg_s": loads["mass_flow_kg_s"],
            "maximum_mass_residual_fraction": loads["maximum_mass_residual_fraction"],
        })
    return records


def fault_disposition(case: dict, parameters: dict, target_name: str) -> str:
    accel_limit = (
        parameters["bands"]["maximum_volley_longitudinal_acceleration_g"]
        if target_name.startswith("volley") else parameters["bands"]["maximum_bolley_longitudinal_acceleration_g"]
    )
    if not case["completed"] or case["gas_fraction_of_baseline"] > parameters["bands"]["maximum_total_gas_fraction_of_baseline"]:
        return "REJECTED"
    if case["maximum_abs_exit_rate_deg_s"] > parameters["bands"]["maximum_exit_rate_deg_s_per_axis"]:
        return "REJECTED"
    if case["active_peak_acceleration_g"] > accel_limit:
        return "REJECTED"
    if case["exit_velocity_change_fraction"] > parameters["bands"]["maximum_axial_exit_velocity_change_fraction"]:
        return "DEGRADED"
    return "SAFE"


def run(parameters: dict) -> dict:
    all_response = []
    all_cases = []
    convergence = []
    faults = []
    target_names = ("volley_reference", "bolley_reference", "bolley_qualification")
    max_step = parameters["solver"]["maximum_axial_step_m"]
    for name in target_names:
        print(f"running {name}", flush=True)
        target = inherited_target(parameters, name)
        all_response.extend(response_map(parameters, name, target))
        amplitudes = target["guide_centreline_amplitude_m"]
        temperatures = target["temperature_k"]
        cg_offsets = target["transverse_cg_offset_m"]
        errors = target["axial_force_centroid_error_from_cg_m"]
        for temperature, amplitude, phase, cg_offset, error in itertools.product(
            temperatures, amplitudes, (0.0, 0.5 * math.pi), cg_offsets, errors
        ):
            all_cases.append(simulate_case(
                parameters, name, target, temperature, amplitude, phase, cg_offset, error, max_step
            ))
        controlling_inputs = (
            min(temperatures), max(amplitudes), 0.5 * math.pi, max(cg_offsets), max(errors)
        )
        coarse = simulate_case(parameters, name, target, *controlling_inputs, max_step)
        fine = simulate_case(
            parameters, name, target, *controlling_inputs,
            max_step * parameters["solver"]["convergence_step_multiplier"]
        )
        quantities = [coarse["active_exit_velocity_m_s"], coarse["exit_rates_deg_s"]["pitch_deg_s"], coarse["exit_rates_deg_s"]["yaw_deg_s"]]
        fine_quantities = [fine["active_exit_velocity_m_s"], fine["exit_rates_deg_s"]["pitch_deg_s"], fine["exit_rates_deg_s"]["yaw_deg_s"]]
        changes = [abs(a - b) / max(abs(b), 1e-9) for a, b in zip(quantities, fine_quantities)]
        convergence.append({
            "target": name,
            "coarse_step_m": max_step,
            "fine_step_m": max_step * parameters["solver"]["convergence_step_multiplier"],
            "maximum_relative_change": max(changes),
            "coarse": coarse,
            "fine": fine,
        })
        for fault in parameters["bands"]["faults_requiring_disposition"]:
            case = simulate_case(parameters, name, target, *controlling_inputs, max_step, fault=fault)
            case["disposition"] = fault_disposition(case, parameters, name)
            faults.append(case)

    target_summaries = {}
    for name in target_names:
        target = inherited_target(parameters, name)
        cases = [case for case in all_cases if case["target"] == name]
        responses = [record for record in all_response if record["target"] == name]
        pocket_pressure = max(record["maximum_pressure_pa"] for record in responses)
        min_pocket_pressure = min(
            parameters["physics"]["ambient_pressure_pa"] + 1e-30,
            pocket_pressure,
        )
        target_summaries[name] = {
            "case_count": len(cases),
            "restoring_points": sum(record["restoring"] for record in responses),
            "response_points": len(responses),
            "completed_cases": sum(case["completed"] for case in cases),
            "maximum_gas_fraction_of_baseline": max(case["gas_fraction_of_baseline"] for case in cases),
            "maximum_exit_velocity_change_fraction": max(case["exit_velocity_change_fraction"] for case in cases),
            "maximum_longitudinal_acceleration_g": max(case["active_peak_acceleration_g"] for case in cases),
            "maximum_abs_exit_rate_deg_s": max(case["maximum_abs_exit_rate_deg_s"] for case in cases),
            "minimum_gap_m": min(case["minimum_gap_m"] for case in cases),
            "maximum_pocket_pressure_pa": max(case["maximum_pocket_pressure_pa"] for case in cases),
            "maximum_mass_residual_fraction": max(case["maximum_mass_residual_fraction"] for case in cases),
            "pocket_knudsen_at_response_peak": mean_free_path(
                parameters["physics"], max(pocket_pressure, 1.0), max(target["temperature_k"])
            ) / target["nominal_clearance_m"],
            "outlet_knudsen_at_ambient": mean_free_path(
                parameters["physics"], parameters["physics"]["ambient_pressure_pa"], max(target["temperature_k"])
            ) / target["nominal_clearance_m"],
        }

    all_nominal_complete = all(s["completed_cases"] == s["case_count"] for s in target_summaries.values())
    pressure_valid = all(
        case["maximum_pocket_pressure_pa"] <= inherited_target(parameters, case["target"]).get(
            "initial_supply_pressure_pa", inherited_target(parameters, case["target"]).get("mean_supply_pressure_pa")
        ) * (1.0 + 1e-9)
        for case in all_cases
    )
    checks = [
        {"band": 1, "name": "restoring force sign", "pass": all(r["restoring"] for r in all_response)},
        {"band": 2, "name": "centred stability and no film closure", "pass": all_nominal_complete},
        {"band": 3, "name": "absolute pressure bounds", "pass": pressure_valid},
        {"band": 4, "name": "total gas <= 110% of baseline", "pass": all(s["maximum_gas_fraction_of_baseline"] <= parameters["bands"]["maximum_total_gas_fraction_of_baseline"] for s in target_summaries.values())},
        {"band": 5, "name": "axial exit change <= 0.5%", "pass": all(s["maximum_exit_velocity_change_fraction"] <= parameters["bands"]["maximum_axial_exit_velocity_change_fraction"] for s in target_summaries.values())},
        {"band": 6, "name": "longitudinal acceleration limits", "pass": target_summaries["volley_reference"]["maximum_longitudinal_acceleration_g"] <= parameters["bands"]["maximum_volley_longitudinal_acceleration_g"] and all(target_summaries[n]["maximum_longitudinal_acceleration_g"] <= parameters["bands"]["maximum_bolley_longitudinal_acceleration_g"] for n in ("bolley_reference", "bolley_qualification"))},
        {"band": 7, "name": "exit rates <= 2 deg/s per axis", "pass": all(s["maximum_abs_exit_rate_deg_s"] <= parameters["bands"]["maximum_exit_rate_deg_s_per_axis"] for s in target_summaries.values())},
        {"band": 8, "name": "all single faults disposed", "pass": len(faults) == len(target_names) * len(parameters["bands"]["faults_requiring_disposition"]) and all(case.get("disposition") in {"SAFE", "DEGRADED", "REJECTED"} for case in faults)},
        {"band": 9, "name": "continuum validity reported", "pass": all("pocket_knudsen_at_response_peak" in s and "outlet_knudsen_at_ambient" in s for s in target_summaries.values())},
        {"band": 10, "name": "plume, contamination and charging remain open", "pass": all(item in parameters["bands"]["limitations_required_open"] for item in ("plume", "contamination", "electrostatic_charging"))},
    ]
    reproduction = {}
    for name in target_names:
        target = inherited_target(parameters, name)
        calculated, _accel = axial_baseline(target)
        reproduction[name] = {
            "declared_m_s": target["baseline_exit_velocity_m_s"],
            "calculated_m_s": calculated,
            "relative_error": abs(calculated - target["baseline_exit_velocity_m_s"]) / target["baseline_exit_velocity_m_s"],
            "pass": abs(calculated - target["baseline_exit_velocity_m_s"]) / target["baseline_exit_velocity_m_s"] <= 0.01,
        }
    numerical_checks = {
        "baseline_reproduction": all(item["pass"] for item in reproduction.values()),
        "step_convergence": all(item["maximum_relative_change"] <= parameters["solver"]["maximum_convergence_change_fraction"] for item in convergence),
        "pressure_mass_balance": all(s["maximum_mass_residual_fraction"] <= parameters["solver"]["maximum_pressure_mass_residual_fraction"] for s in target_summaries.values()),
    }
    return {
        "schema": "volley-lab.quadrant-bearing-result/1",
        "controlled_input": "experiments/VLAB-X001/parameters.json",
        "evidence_class": "reduced-order compressible-flow and rigid-body model; no test evidence",
        "checks": checks,
        "pass_count": sum(item["pass"] for item in checks),
        "check_count": len(checks),
        "screen_pass": all(item["pass"] for item in checks) and all(numerical_checks.values()),
        "reproduction": reproduction,
        "numerical_checks": numerical_checks,
        "target_summaries": target_summaries,
        "response_map": all_response,
        "nominal_cases": all_cases,
        "convergence": convergence,
        "fault_cases": faults,
        "limitations": parameters["declared_limitations"],
    }


def render_figures(result: dict) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    colors = {"volley_reference": "#3155c6", "bolley_reference": "#d14e96", "bolley_qualification": "#8f3fc0"}
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for name, color in colors.items():
        records = [r for r in result["response_map"] if r["target"] == name]
        ax.plot([100 * r["offset_fraction"] for r in records], [r["force_y_n"] for r in records], "o-", label=name.replace("_", " "), color=color)
    ax.axhline(0.0, color="#333333", linewidth=0.8)
    ax.axvline(0.0, color="#333333", linewidth=0.8)
    ax.set_xlabel("signed offset (% of nominal clearance)")
    ax.set_ylabel("net restoring-axis force (N)")
    ax.set_title("VLAB-X001 quasi-static restoring response")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ARTIFACTS / "response_map.svg")
    plt.close(fig)

    names = list(colors)
    rates = [result["target_summaries"][n]["maximum_abs_exit_rate_deg_s"] for n in names]
    gaps = [1e6 * result["target_summaries"][n]["minimum_gap_m"] for n in names]
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.8))
    axes[0].bar([n.replace("_", "\n") for n in names], rates, color=[colors[n] for n in names])
    axes[0].axhline(2.0, color="#b71935", linestyle="--", label="2 deg/s band")
    axes[0].set_ylabel("worst absolute exit rate (deg/s)")
    axes[0].legend()
    axes[1].bar([n.replace("_", "\n") for n in names], gaps, color=[colors[n] for n in names])
    axes[1].axhline(0.0, color="#b71935", linestyle="--")
    axes[1].set_ylabel("minimum film gap (µm)")
    fig.suptitle("VLAB-X001 dynamic envelope")
    fig.tight_layout()
    fig.savefig(ARTIFACTS / "dynamic_envelope.svg")
    plt.close(fig)


def render_report(result: dict) -> str:
    verdict = "PASS" if result["screen_pass"] else "REJECT"
    lines = [
        "# VLAB-X001 quadrant-bearing result",
        "",
        "> **Generated by `quadrant_bearing.py`. Do not hand-edit.**  ",
        "> **Evidence class:** reduced-order compressible-flow and rigid-body model; nothing is measured.",
        "",
        f"## My disposition: {verdict}",
        "",
        f"The frozen mechanism screen passes **{result['pass_count']} of {result['check_count']} bands**.",
        "",
        "## Target envelope",
        "",
        "| Target | Completed corners | Gas / baseline | Exit-speed change | Peak axial g | Worst exit rate | Minimum gap |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, summary in result["target_summaries"].items():
        lines.append(
            f"| {name.replace('_', ' ')} | {summary['completed_cases']}/{summary['case_count']} | "
            f"{100*summary['maximum_gas_fraction_of_baseline']:.3f}% | "
            f"{100*summary['maximum_exit_velocity_change_fraction']:.4f}% | "
            f"{summary['maximum_longitudinal_acceleration_g']:.3f} | "
            f"{summary['maximum_abs_exit_rate_deg_s']:.3f} deg/s | "
            f"{1e6*summary['minimum_gap_m']:.3f} µm |"
        )
    lines.extend(["", "## Frozen bands", "", "| Band | Check | Result |", "|---:|---|---:|"])
    for check in result["checks"]:
        lines.append(f"| {check['band']} | {check['name']} | **{'PASS' if check['pass'] else 'FAIL'}** |")
    lines.extend(["", "## Numerical checks", ""])
    for key, value in result["numerical_checks"].items():
        lines.append(f"- {key.replace('_', ' ')}: **{'PASS' if value else 'FAIL'}**")
    lines.extend(["", "## Single-channel faults", "", "| Target | Fault | Disposition | Completion | Exit rate | Gas / baseline |", "|---|---|---:|---:|---:|---:|"])
    for case in result["fault_cases"]:
        lines.append(
            f"| {case['target'].replace('_', ' ')} | {case['fault']} | **{case['disposition']}** | "
            f"{'yes' if case['completed'] else 'no'} | {case['maximum_abs_exit_rate_deg_s']:.3f} deg/s | "
            f"{100*case['gas_fraction_of_baseline']:.3f}% |"
        )
    lines.extend([
        "", "## Continuum warning", "",
        "The pocket Knudsen numbers and the vacuum-boundary values are retained in the JSON. The",
        "pocket core may be continuum-like while the last part of the outlet film is not. This screen",
        "does not turn that boundary into a validated leakage prediction.",
        "", "## What remains open", "",
    ])
    lines.extend(f"- {item}" for item in result["limitations"])
    lines.extend([
        "", "![Quasi-static response](artifacts/response_map.svg)", "",
        "![Dynamic envelope](artifacts/dynamic_envelope.svg)", "",
        "The complete corner, convergence, pressure-residual and fault records are in",
        "[`artifacts/result.json`](artifacts/result.json).",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the controlled JSON, report and figures")
    args = parser.parse_args()
    parameters = load_parameters()
    result = run(parameters)
    print(json.dumps({
        "screen_pass": result["screen_pass"],
        "pass_count": result["pass_count"],
        "check_count": result["check_count"],
        "numerical_checks": result["numerical_checks"],
        "target_summaries": result["target_summaries"],
    }, indent=2))
    if args.write:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        (ARTIFACTS / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        render_figures(result)
        (HERE / "RESULT.md").write_text(render_report(result), encoding="utf-8")


if __name__ == "__main__":
    main()
