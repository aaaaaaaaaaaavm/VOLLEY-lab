#!/usr/bin/env python3
"""Comparable actuator-load sensitivities; not a mechanism downselect or qualification."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'analysis/inputs/gen6_feeder_load_screen.json'
OUTPUT = ROOT / 'analysis/results/gen6_feeder_load_screen.json'
REPORT = ROOT / 'docs/GEN6_FEEDER_LOAD_SCREEN.md'
FIGURE = ROOT / 'figures/gen6_feeder_load_screen.svg'


def motion(stroke, duration):
    if stroke <= 0 or duration <= 0:
        raise ValueError('stroke and duration must be positive')
    return {'peak_velocity_m_s': 2 * stroke / duration,
            'acceleration_m_s2': 4 * stroke / duration**2}


def pantograph(stroke, stages, minimum_deg, maximum_deg, output_force):
    low, high = map(math.radians, (minimum_deg, maximum_deg))
    if not 0 < low < high < math.pi / 2 or stages < 1:
        raise ValueError('non-singular increasing angles and positive stages required')
    # y=2*n*L*sin(theta), b=2*L*cos(theta).
    # Ideal virtual work gives |F_b/F_y|=n*cot(theta).
    half_link = stroke / (2 * stages * (math.sin(high) - math.sin(low)))
    return {'minimum_angle_deg': minimum_deg, 'half_link_length_m': half_link,
            'initial_height_m': 2 * stages * half_link * math.sin(low),
            'final_height_m': 2 * stages * half_link * math.sin(high),
            'initial_base_width_m': 2 * half_link * math.cos(low),
            'base_actuator_stroke_m': 2 * half_link * (math.cos(low) - math.cos(high)),
            'peak_ideal_input_force_N': stages * output_force / math.tan(low),
            'peak_force_multiplier': stages / math.tan(low)}


def build():
    p = json.loads(INPUT.read_text())
    cases = []
    for mass, duration, resistance in itertools.product(p['payload_masses_kg'], p['feed_durations_s'], p['opposing_force_scenarios_N']):
        kinematics = motion(p['transfer_stroke_m'], duration)
        force = mass * kinematics['acceleration_m_s2'] + resistance
        springs = []
        for stiffness in p['spring_stiffness_scenarios_N_m']:
            # Floor at weakest extension; spring unloads along the feed direction.
            energy = force * p['transfer_stroke_m'] + .5 * stiffness * p['transfer_stroke_m']**2
            springs.append({'stiffness_N_m': stiffness, 'minimum_force_floor_N': force,
                            'initial_force_N': force + stiffness * p['transfer_stroke_m'],
                            'released_energy_J': energy,
                            'lossless_undamped_payload_speed_bound_m_s': math.sqrt(2 * energy / mass)})
        cases.append({'payload_kg': mass, 'duration_s': duration, 'opposing_force_N': resistance,
                      **kinematics, 'peak_required_output_force_N': force,
                      'positive_mechanical_work_lower_bound_J': resistance * p['transfer_stroke_m'] + .5 * mass * kinematics['peak_velocity_m_s']**2,
                      'screw': [{'assumed_efficiency': efficiency,
                                 'torque_N_m': force * p['screw_lead_m'] / (2 * math.pi * efficiency),
                                 'peak_rpm': 60 * kinematics['peak_velocity_m_s'] / p['screw_lead_m']}
                                for efficiency in p['screw_efficiency_scenarios']],
                      'spring': springs,
                      'pantograph': [pantograph(p['transfer_stroke_m'], p['pantograph_stages'], angle, p['pantograph_max_angle_deg'], force)
                                     for angle in p['pantograph_min_angles_deg']]})
    lead_angle = math.atan(p['screw_lead_m'] / (math.pi * p['screw_mean_diameter_m']))
    return {'revision': p['revision'], 'evidence_class': p['evidence_class'],
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'inputs_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
            'case_count': len(cases), 'cases': cases,
            'square_thread_static_backdrive_screen': {
                'lead_angle_deg': math.degrees(lead_angle),
                'friction_threshold': math.tan(lead_angle),
                'scenarios': [{'assumed_friction': mu, 'ideal_self_locking': mu > math.tan(lead_angle)} for mu in p['thread_friction_scenarios']]},
            'retention_loads': [{'payload_kg': m, 'assumed_g': g, 'payload_inertia_force_N': m * 9.80665 * g}
                                for m, g in itertools.product(p['payload_masses_kg'], p['retention_acceleration_scenarios_g'])]}


def report(d):
    selected = [c for c in d['cases'] if c['payload_kg'] == 4 and c['duration_s'] == 5]
    lines = ['# Gen6 feeder: comparable load and energy screen', '',
             '**Analytical sensitivity study; no selected mechanism, rated component or verified CAD.**', '',
             'The reference is a 200 mm lateral one-way feed. The 1.33/4 kg cases match the mixed-size mission surrogates; 6 kg is a sensitivity only. Duration is active transfer time, not total deployment cadence. The three architectures share payload, travel, duration and opposing-force scenarios. None has a measured friction or mass advantage.', '',
             '[Inputs and provenance](../analysis/inputs/gen6_feeder_load_screen.json) · [source](../analysis/gen6_feeder_load_screen.py) · [full results](../analysis/results/gen6_feeder_load_screen.json)', '',
             '![Feeder actuator and restraint sensitivity](../figures/gen6_feeder_load_screen.svg)', '',
             '## Common boundary and equations', '',
             'An ideal symmetric triangular velocity profile gives peak speed `2s/T` and acceleration magnitude `4s/T²`. Peak output force is `m*4s/T² + R`, with R an assumed opposing-force scenario. This omits moving pusher/link mass, stiffness, shock and jerk. Positive mechanical-work floor is `R*s + m*v_peak²/2`; electrical input must also cover actuator, drivetrain and control losses. The actuator must support braking and holding as well as forward thrust.', '',
             'A screw requires idealized torque `F*lead/(2*pi*eta)` and peak speed `60*v_peak/lead`. Efficiency is assumed independently of the friction screen; these scenarios are not a mutually consistent component model. An 8 mm mean diameter and 2 mm lead give a 4.55-degree lead angle. The square-thread static self-locking condition is `mu > lead/(pi*d)`. It fails for mu=0.03 and narrowly passes for 0.08; dynamic vibration and lubrication can change it. **Do not use assumed screw friction as the power-off restraint.**', '',
             'For a three-stage ideal scissor with output `y=2*n*L*sin(theta)` and base width `b=2*L*cos(theta)`, virtual work gives input-force magnitude `n*F*cot(theta)`. The 5/10/20-degree starts are each resized to provide the same 200 mm output travel by 70 degrees. They are alternative geometries, not one fixed linkage. This is a horizontally actuated output-axis proxy; the proposed sequential-collapse magazine still needs independent latches and a final transfer mechanism.', '',
             'A spring is sized so its weakest force covers the peak force screen. With stiffness k, initial force is `F_min+k*s` and released energy is `F_min*s+k*s²/2`. The lossless undamped speed is an upper bound if all released spring energy reaches the payload; it is not the speed of a controlled transfer. Damping, a captured carriage, end stops and two independently contained barriers remain necessary.', '',
             '## Four-kilogram, five-second comparison', '',
             '| Assumed resistance N | Required output N | Screw torque at eta=0.4 N m | Three-stage scissor input at 10 degrees N | Spring released energy at k=50 N/m J |',
             '|---:|---:|---:|---:|---:|']
    for c in selected:
        lines.append(f"| {c['opposing_force_N']:.0f} | {c['peak_required_output_force_N']:.3f} | {c['screw'][1]['torque_N_m']:.5f} | {c['pantograph'][1]['peak_ideal_input_force_N']:.2f} | {c['spring'][1]['released_energy_J']:.3f} |")
    lines += ['', 'At five seconds the peak feed speed is 0.08 m/s and the 2 mm screw reaches 240 rpm. A 10-degree, three-stage scissor multiplies output force by 17.01; a 5-degree start multiplies it by 34.29. Near-flat force is a real trade penalty even when stowed height improves.', '',
              '## Retention is a separate load case', '',
              'A 4 kg payload produces 196.13/392.27/980.67 N under the provisional 5/10/25 g sensitivity bands, before safety factors, eccentricity, preload, dynamic amplification or other masses. These are not provider requirements. A feed axis sized for a few tens of newtons cannot be presumed to provide launch retention. Gates, locks and host structure need a separate load path and assessment.', '',
              '## Selection boundary', '',
              f"The {d['case_count']} common cases replace no subjective fit, reliability or mass scores. No downselect follows. Same-boundary mechanism CAD/STEP, link and bearing loads, screw buckling, interface contact, tolerance/thermal deflection, actuator ratings, complete installed BOM and positive power-off/fault containment remain unverified. No rejected concept is removed from the archive.", '',
              'Run `python3 analysis/gen6_feeder_load_screen.py --check` and `python3 -m unittest discover -s tests -v`. Tests check displacement, virtual-work force, energy and expected sensitivity counts; they verify the implementation, not a physical mechanism.', '']
    return '\n'.join(lines)


def figure(d):
    # Compact, deterministic SVG; all plotted coordinates are calculated.
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">',
           '<rect width="1200" height="560" fill="#07111b"/>',
           '<g font-family="sans-serif" fill="#e8f0f7">',
           '<text x="45" y="50" font-size="26">Feeder loads: the actuator and the restraint do different jobs</text>',
           '<text x="45" y="82" font-size="16" fill="#8fa7ba">200 mm transfer · ideal three-stage scissor · declared sensitivity scenarios</text>',
           '<text x="60" y="130" font-size="18">Scissor input force / output force</text>']
    for i, angle in enumerate((5,10,20)):
        value = 3 / math.tan(math.radians(angle)); y=165+i*80
        out += [f'<text x="60" y="{y+19}" font-size="16">{angle}°</text>',
                f'<rect x="115" y="{y}" width="{value*10}" height="30" fill="#38d6e8"/>',
                f'<text x="{125+value*10:.1f}" y="{y+22}" font-size="16">{value:.2f}×</text>']
    out += ['<text x="650" y="130" font-size="18">4 kg payload restraint force [N]</text>']
    for i,g in enumerate((5,10,25)):
        value=4*9.80665*g; y=165+i*80
        out += [f'<text x="650" y="{y+19}" font-size="16">{g} g</text>',
                f'<rect x="715" y="{y}" width="{value*.32}" height="30" fill="#ffb454"/>',
                f'<text x="{725+value*.32:.1f}" y="{y+22}" font-size="16">{value:.1f}</text>']
    out += ['<text x="45" y="445" font-size="18">Near-flat scissor geometry raises drive loads; screw friction does not establish safe holding.</text>',
            '<text x="45" y="480" font-size="18">Feed force, payload restraint and launch acceleration require separate load paths.</text>',
            '<text x="45" y="525" font-size="16" fill="#8fa7ba">ANALYTICAL REQUIREMENTS SCREEN · NO CAD CLEARANCE, HARDWARE OR RELIABILITY PASS</text></g></svg>\n']
    return '\n'.join(out)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    d=build(); generated={OUTPUT:json.dumps(d,indent=2,sort_keys=True)+'\n', REPORT:report(d), FIGURE:figure(d)}
    if args.check:
        stale=[str(p.relative_to(ROOT)) for p,body in generated.items() if not p.exists() or p.read_text()!=body]
        if stale: raise SystemExit('stale output: '+', '.join(stale))
        print(f"PASS: {d['case_count']} feeder scenarios and exact generated outputs")
    else:
        for p,body in generated.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(body)

if __name__=='__main__': main()
