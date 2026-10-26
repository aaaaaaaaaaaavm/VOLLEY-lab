"""Budget bounds, external-measurement applicability and report for frozen high-target rejections."""
from pathlib import Path
import csv,hashlib,json,math,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def dump(name,x):(H/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def table(name,rows):
    with (H/name).open('w',newline='') as f:
        keys=list(dict.fromkeys(k for r in rows for k in r));w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()})
def main():
    source=load(H/'HIGH_TARGET_RESULTS.json');rows=source['cases'];sled=source['sled_mass_kg'];payload=4.;moving=sled+payload
    host=rows[0]['reference_rest_host_kg'];total=host+moving
    home=load(H/'capture/cad/release/VOLLEY_G5_ACR1_home.json')
    magnets=[r for r in home['BOM'] if r['subsystem'].startswith('sled') and 'magnet' in str(r).lower()]
    magnet_mass=sum(r['mass_kg'] for r in magnets);assert len(magnets)==84 and math.isclose(magnet_mass,3.6288,abs_tol=1e-10)
    mu=moving*host/total;mub=sled*host/(host+sled)
    f=load(H/'capture/analysis/FINITE_MOTOR.json')['stations'];b=load(H/'capture/analysis/ARREST_FORCE_MAP.json')['stations']
    launch_integral=float(np.trapezoid([r['with_return_N_per_A'] for r in f],[r['displacement_m'] for r in f]))
    brake_integral=float(np.trapezoid([r['N_per_peak_A'] for r in b],[r['displacement_m'] for r in b]))
    maxk=max(r['with_return_N_per_A'] for r in f);mink=min(r['with_return_N_per_A'] for r in f)
    nominal_usable=.5*6.25*(86.4**2-60**2);adverse_usable=nominal_usable*.9*.7
    constraints=[];long=[];refine=[];invariants=[];compact=[]
    for speed in [10,15,30,50,100]:
        wa=.5*mu*speed**2;wb=.5*mub*speed**2
        child=host/total*speed
        constraints.append(dict(target_relative_m_s=speed,moving_sled_plus_payload_kg=moving,
            accelerated_reduced_mass_kg=mu,braking_reduced_mass_kg=mub,
            assembly_kinetic_energy_fixed_lab_J=.5*moving*speed**2,finite_host_relative_launch_work_J=wa,
            sled_kinetic_energy_fixed_lab_J=.5*sled*speed**2,finite_host_relative_arrest_work_J=wb,
            mean_launch_force_in_1p3m_N=wa/1.3+5,
            mean_arrest_force_in_210mm_N=wb/.21,
            optimistic_constant_phase_current_launch_A=(wa+5*1.3)/launch_integral,
            optimistic_constant_phase_current_arrest_A=wb/brake_integral,
            ideal_acceleration_duration_s=2*1.3/speed,ideal_average_acceleration_m_s2=speed**2/(2*1.3),
            ideal_relative_acceleration_g=speed**2/(2*1.3*9.80665),
            ideal_payload_inertial_axial_acceleration_g=host/total*speed**2/(2*1.3*9.80665),
            mean_mechanical_launch_power_for_constant_acceleration_W=wa/(2*1.3/speed),
            optimistic_back_EMF_q_voltage_V=maxk*speed/1.5,
            minimum_bank_voltage_for_back_EMF_no_losses_V=math.sqrt(3)/.95*maxk*speed/1.5,
            payload_inertial_delta_v_m_s_if_target_reached=child,
            host_recoil_before_arrest_m_s_if_target_reached=-moving/total*speed,
            final_retained_host_recoil_m_s_if_arrest_completed=-payload*child/(total-payload),
            angular_impulse_at_0p1m_offset_Nm_s=.1*payload*child,
            optimistic_drive_length_600A_best_coefficient_m=wa/(600*maxk),
            optimistic_arrest_length_600A_best_coefficient_m=wb/(600*maxk),
            source_nominal_usable_to60V_J=nominal_usable,source_adverse_usable_to60V_J=adverse_usable))
        for length in [2,5,10]:
            long.append(dict(hypothetical_revision=f'HYP-L{length}m',drive_length_m=length,target_relative_m_s=speed,
                assumed_same_reduced_mass_kg=mu,mean_launch_force_N=wa/length+5,
                constant_phase_current_static_bound_A=(wa/length+5)/mink,
                ideal_acceleration_m_s2=speed**2/(2*length),ideal_acceleration_time_s=2*length/speed,
                launch_kinetic_work_J=wa,arrest_still210mm_required_static_phase_current_A=wb/brake_integral,
                validity='Arithmetic requirement for a DIFFERENT hypothetical rail. Same k is an unvalidated optimistic transfer assumption; added mass/field/end effects/harness/thermal/control must be recomputed.'))
    for r in rows:
        release=r['release'];mechanical=None
        if release:
            mechanical=.5*(mu-mub)*release['relative_speed_m_s']**2+.5*mub*r['stop_velocity_m_s']**2+r['mechanical_friction_dissipation_J']
            diff=r['energy_ledger']['mechanical_J']-mechanical
            assert abs(diff)<1e-6
            invariants.append(dict(case=r['case_id'],independent_mechanical_work_residual_J=diff,
                same_declared_energy_balance=r['checks']['energy_balance'],declared_gates_pass=r['all_declared_checks_pass']))
        compact.append(dict(case=r['case_id'],target_m_s=r['target_m_s'],adverse=r['adverse'],L_uH=r['inductance_H']*1e6,dt_us=r['dt_s']*1e6,
            actual_release_relative_m_s=None if not release else release['relative_speed_m_s'],
            actual_payload_inertial_kick_m_s=None if not release else release['payload_inertial_delta_v_m_s'],
            status=r['status'],boundary_exit_position_m=r['stop_position_m'],velocity_at_boundary_exit_m_s=r['stop_velocity_m_s'],
            source_draw_until_boundary_exit_J=r['cap_draw_J'],cap_voltage_at_boundary_exit_V=r['cap_end_V'],
            peak_phase_current_A=r['peak_phase_current_A'],peak_device_current_A=r['peak_device_current_A'],allocated_peak_Vds_V=r['allocated_peak_Vds_V'],
            modeled_peak_payload_normal_N=r['peak_payload_normal_reaction_N'],energy_residual_J=r['energy_residual_J'],
            max_actual_modulation_ratio=r['actual_modulation_peak'],all_declared_checks_pass=r['all_declared_checks_pass'],
            failed_gates=[k for k,v in r['checks'].items() if not v]))
    for fine in [r for r in rows if r['dt_s']==5e-6]:
        coarse=next(r for r in rows if r['target_m_s']==fine['target_m_s'] and r['adverse']==fine['adverse'] and r['inductance_H']==fine['inductance_H'] and r['dt_s']==20e-6)
        refine.append(dict(target_m_s=fine['target_m_s'],adverse=fine['adverse'],L_uH=20,coarse_dt_us=20,fine_dt_us=5,
            coarse_status=coarse['status'],fine_status=fine['status'],same_rejection_status=coarse['status']==fine['status'],
            release_speed_change_m_s=fine['release']['relative_speed_m_s']-coarse['release']['relative_speed_m_s'],
            boundary_exit_position_change_mm=1000*(fine['stop_position_m']-coarse['stop_position_m']),
            boundary_exit_speed_change_m_s=fine['stop_velocity_m_s']-coarse['stop_velocity_m_s'],
            cap_draw_change_J=fine['cap_draw_J']-coarse['cap_draw_J'],peak_current_change_A=fine['peak_phase_current_A']-coarse['peak_phase_current_A']))
    assert len(rows)==22 and not any(r['all_declared_checks_pass'] for r in rows)
    assert len(refine)==4 and all(r['same_rejection_status'] for r in refine)
    table('MODEL_CASES.csv',compact);table('CONSTRAINTS.csv',constraints);table('HYPOTHETICAL_LONG_RAILS.csv',long);table('TIMESTEP_REFINEMENT.csv',refine)
    bounds=dict(moving_sled_kg=sled,payload_kg=4,accelerated_mass_kg=moving,reference_rest_host_kg=host,total_initial_kg=total,
        accelerated_reduced_mass_kg=mu,braking_reduced_mass_kg=mub,
        launch_work_coefficient_J_per_A=launch_integral,arrest_work_coefficient_J_per_A=brake_integral,
        optimistic_arrest_work_at600A_J=600*brake_integral,
        optimistic_drive_speed_ceiling_at600A_no_losses_m_s=math.sqrt(2*600*launch_integral/mu),
        optimistic_arrest_speed_ceiling_at600A_no_losses_m_s=math.sqrt(2*600*brake_integral/mub),
        nominal_usable_bank_energy_86p4_to60V_J=nominal_usable,adverse_usable_bank_energy_86p4_to60V_J=adverse_usable,
        nominal_initial_positive_source_power_budget_W=.8*86.4**2/(4*.176),adverse_initial_positive_source_power_budget_W=.8*86.4**2/(4*.352),
        optimistic_initial_q_voltage_ceiling_no_ESR_V=.95*86.4/math.sqrt(3),
        optimistic_no_load_back_EMF_speed_ceiling_m_s=(.95*86.4/math.sqrt(3))/(maxk/1.5),
        caveat='These are necessary optimistic bounds of current field map, not achievable operating points or new rated speeds.')
    dump('BUDGET_BOUNDS.json',bounds);dump('INVARIANT_AND_REFINEMENT_CHECKS.json',dict(passed=True,invariants=invariants,refinements=refine,
        all22_cases_rejected=True,original_acceptance_gates_unchanged=True,original_source_unchanged=True))
    shoe=[]
    for adapter in [.25,.5,1.,sled]:
        for speed in [10,15,30,50,100]:
            shoe.append(dict(variant='HYP-full-sled-flyaway' if adapter==sled else f'HYP-attached-shoe-{adapter:g}kg',
                assumed_adapter_kg=adapter,payload_kg=4,outbound_payload_plus_adapter_kg=4+adapter,
                target_relative_m_s=speed,fixed_lab_kinetic_work_J=.5*(4+adapter)*speed**2,
                current_reusable_mover_fixed_lab_kinetic_work_J=.5*moving*speed**2,
                same_available_work_mass_only_speed_ratio=math.sqrt(moving/(4+adapter)),
                attached_adapter_count_per12payload_campaign=12,total_adapter_inventory_kg=12*adapter,
                current_reusable_sled_inventory_count=1,current_reusable_sled_inventory_kg=sled,
                powered_sled_arrest_required_after_successful_shoe_departure=False,
                discarded_free_adapter_debris_assumed=False,
                shoe_mass_substantiated=False,current_force_map_transferred=False,
                caveat='Gen6/Labs analytic trade only. Adapter stays attached to satellite; no achievable adapter mass,force,source speed or complete installed-system advantage is demonstrated.'))
    table('HYPOTHETICAL_FLYAWAY_SHOES.csv',shoe)
    dump('HYPOTHETICAL_FLYAWAY_SHOES.json',dict(scope='Hypothetical attached flyaway launch shoes; current ACR1 unchanged',
        current_moving_magnet_count=len(magnets),current_CAD_moving_magnet_mass_kg=magnet_mass,
        current_array_blocks_per_side=42,current_blocks_per_magnetic_period=6,
        current_geometry_mass_constraint='0.25/0.5/1kg hypothetical shoes cannot retain the present3.6288kg magnet set even before guides/retention/support. Current force map cannot transfer.',
        ratio_equation='sqrt((13.127805767068676+4)/(4+m_shoe)) at equal ideal fixed-lab work,neglecting all losses and geometry changes',
        finite_host_note='This requested mass-only ratio is not a finite-host coupled solution. Actual mass history/recoil/source/field must be recomputed for selected new geometry.',
        assumptions=['0.25/0.5/1kg are sensitivity values with no substantiated achievable design.',
                     'Full-sled flyaway retains17.1278kg outbound moving assembly;removes arrest but has no launch-kinetic-energy mass saving.',
                     'Twelve adapters are required for twelve deployments,versus one current reusable carrier.',
                     'Each adapter remains positively attached to its payload;no free adapter debris is credited.',
                     'Source field modules,rails,interface and abort/partial-exit containment must be redesigned;no blind current-force scaling.'],
        rows=shoe))
    # Genuine published measurements are paraphrased; no new data or calibration fit is invented.
    reading=load(H/'literature/READING_RECEIPT.json');pdfhash=reading['sha256']
    assert pdfhash=='c996e1768abfcbb85f97155acbe3871a4b69246079dcbb0b9b80abdb39782b9f'
    assert next(s for s in load(H/'literature/SOURCE_CARDS_REUSED.json')['sources'] if s['id']=='Z22')['sha256']==pdfhash
    benchmark=[dict(id='Z22_FIELD',doi='10.3390/rs14174205',url='https://www.mdpi.com/2072-4292/14/17/4205',location='§5.1,p12,Fig16',
        actual_measurement='Gauss-meter/XYZ-stage airgap field; reported average ejection-unit gap-center flux about0.424T,conveying drive about0.23T.',
        applicable_check='Reconstruct published double-magnetic-circuit geometry/materials/gap; compare field-vs-position before dynamic calibration.',
        mismatch='Yoked double magnetic circuit is not ACR1 air-core Halbach:six blocks per period,42 per side,12mm modeled magnet-face gap. Published gap/material/coverage dimensions must be recovered;no universal flux correction transfers.',
        model_validation_completed_here=False),
      dict(id='Z22_FORCE',doi='10.3390/rs14174205',location='§5.2,pp13–14,Fig20',
        actual_measurement='Ejection force/current/coil-position measured on laboratory launcher; theory exceeds measured force at larger current density.',
        applicable_check='Independent force-current-position benchmark at the published geometry,including armature reaction. Digitize traceable curve points/uncertainty before claiming reproduction.',
        mismatch='ACR1 freezes magnet field and imposes mean three-phase current up to600A. Published voice-coil topology,current density,turns,gap and saturation are different; no high-current scaling factor is inferred.',
        model_validation_completed_here=False),
      dict(id='Z22_RELEASE',doi='10.3390/rs14174205',location='§5.4,pp17–18,Fig27',
        actual_measurement='Fixed-frame counterweighted gravity-compensation release;1kg dummy0.67–1.42m/s;3kg dummy0.40–0.85m/s;currents0.5–2.5A;high-speed camera.',
        derived_payload_kinetic_energy_1kg_J=[.5*.67**2,.5*1.42**2],derived_payload_kinetic_energy_3kg_J=[.5*3*.4**2,.5*3*.85**2],
        author_reported_model_difference='Below11% in their test conditions;collision losses and armature reaction omitted.',
        applicable_check='Work-energy/dynamic benchmark only after reconstructing force,stroke,mass,counterweight/friction and current waveform; distinguishes model discrepancy from shot dispersion.',
        mismatch='1/3kg low-speed fixed-frame tests do not contain13.1278kg retained sled,finite host,captive arrest,ACR1 source/PWM or10–100m/s operation. The11% figure is not ACR1 uncertainty.',
        model_validation_completed_here=False),
      dict(id='Z25_TRANSPORT',doi='10.3390/aerospace12060466',location='Existing full-text review §5;not newly reread in this task',
        actual_measurement='Gravity-assisted aligned/offset transport tests reported about0.20/0.246s.',
        applicable_check='Separate custody/contact/transfer benchmark;not an ejection-speed or high-speed current-source validation.',
        mismatch='Grooves/iron patches and gravity assistance differ from ACR1 passive generic payload interface.',model_validation_completed_here=False)]
    dump('EXPERIMENTAL_BENCHMARK_CARDS.json',dict(review_date_utc='2026-10-26',primary_Z22_pdf_sha256=pdfhash,
        actual_this_task_reading='Reread selected existing public-publisher PDF passages:pp3–8(topology/model),pp9–14(field/force),pp17–18(release).No complete new full-text review claimed.',
        cards=benchmark,excluded_as_experimental_validation=[
          dict(doi='10.1155/ijae/3000765',reason='Feng2025 higher-speed induction-launch results are simulation,not measured hardware.'),
          dict(doi='10.1541/ieejias.143.570',reason='Yamaguchi2023 finite-end-effect theory is2D;hardware demonstration future work.'),
          dict(doi='10.1109/TIE.2021.3134060',reason='Existing primary metadata/abstract only;closed full text;no quantitative benchmark imported.')],
        external_experiments_physically_validate_VOLLEY=False,no_external_contacts=True,no_paywall_bypass=True))
    # Exportable scientific figure: all current-model cases retain rejection semantics.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.22,'savefig.facecolor':'white'})
    fig,axes=plt.subplots(2,2,figsize=(13,8.5),layout='constrained');teal='#087f81';amber='#b56b12'
    ax=axes[0,0]
    for adverse,col,label in [(False,teal,'Nominal, 20 µH'),(True,amber,'Adverse, 20 µH')]:
        rr=[r for r in rows if r['adverse']==adverse and r['inductance_H']==20e-6 and r['dt_s']==20e-6]
        ax.plot([r['target_m_s'] for r in rr],[r['release']['relative_speed_m_s'] for r in rr],marker='x',lw=2,color=col,label=label)
    ax.plot([0,100],[0,100],'--',color='.55',label='Requested = achieved')
    ax.set(xlabel='Requested relative speed [m/s]',ylabel='Release speed before failed arrest [m/s]',title='A  Unchanged 1.3 m drive + 210 mm arrest: all rejected',ylim=(0,105));ax.legend(fontsize=9,loc='upper left')
    speeds=[r['target_relative_m_s'] for r in constraints]
    ax=axes[0,1];ax.plot(speeds,[r['finite_host_relative_launch_work_J'] for r in constraints],'-o',color=teal,label='Relative launch kinetic work')
    ax.plot(speeds,[r['finite_host_relative_arrest_work_J'] for r in constraints],'-s',color=amber,label='Relative sled arrest kinetic work')
    ax.axhline(nominal_usable,color='.3',ls='--',label='Bank usable to 60 V, nominal')
    ax.axhline(600*brake_integral,color='#a23b3b',ls=':',label='Ideal 600 A current-map arrest work')
    ax.set(xlabel='Target relative speed [m/s]',ylabel='Energy/work [J]',yscale='log',title='B  Kinetic requirements; losses must be added');ax.legend(fontsize=9)
    ax=axes[1,0];ax.plot(speeds,[r['optimistic_constant_phase_current_launch_A'] for r in constraints],'-o',color=teal,label='Drive: constant-current work bound')
    ax.plot(speeds,[r['optimistic_constant_phase_current_arrest_A'] for r in constraints],'-s',color=amber,label='Arrest: constant-current work bound')
    ax.axhline(600,color='#a23b3b',ls='--',label='Current reference clamp 600 A')
    ax.set(xlabel='Target relative speed [m/s]',ylabel='Peak-phase-current convention [A]',yscale='log',title='C  Same field-map requirements; not feasible ratings');ax.legend(fontsize=9)
    ax=axes[1,1]
    for length,col in [(2,'#236c9a'),(5,'#7c5a9b'),(10,'#6c7838')]:
        rr=[r for r in long if r['drive_length_m']==length]
        ax.plot(speeds,[r['constant_phase_current_static_bound_A'] for r in rr],'-o',color=col,label=f'HYP-L{length} m: new rail')
    ax.axhline(600,color='#a23b3b',ls='--',label='600 A reference')
    ax.set(xlabel='Target relative speed [m/s]',ylabel='Hypothetical static drive-current bound [A]',yscale='log',title='D  Changed rails: budget only; field/mass not validated');ax.legend(fontsize=9)
    fig.suptitle('Higher-speed design constraints — same ACR1 source, geometry and acceptance gates',fontsize=15,weight='bold')
    fig.savefig(H/'HIGH_VELOCITY_SCREEN.png',dpi=180);fig.savefig(H/'HIGH_VELOCITY_SCREEN.pdf');plt.close(fig)
    fine=[r for r in rows if r['dt_s']==5e-6]
    report=f'''# Higher-speed assessment:bounded first screen

**HV-ACR1-REJECTION-SCREEN-01 ·26October2026.** The unchanged source/geometry was actually run at requested10,15,30,50 and100m/s. All22target/inductance/adverse/timestep cases fail the original accepted gates. Current modeled command points remain1,2 and3m/s. No higher achieved or hardware-rated operating point is established.

## What was executed

Unchanged coupled_shot.py was imported from a private byte-identical capture. Its finite magnetic/brake maps,computed phase resistance,CAD mass and all source/inverter/current/voltage/arrest checks were preserved. The runner calls the existing function with new target arguments only:all five targets at20µH/20µs,nominal and adverse;10/15m/s at3/100µH;and four decisive10/15m/s nominal/adverse20µH refinements at5µs. Twenty-two cases took a single CPU process;no finite-field map,accepted source output or geometry was regenerated. Exact accepted copies and pins accompany this packet.

| Target | Condition |5µs release (m/s)|Speed at >1.511m abort (m/s)|Draw until abort (J)|
|---:|---|---:|---:|---:|
'''
    for r in fine:report+=f"|{r['target_m_s']:g}|{'adverse' if r['adverse'] else 'nominal'}|{r['release']['relative_speed_m_s']:.6f}|{r['stop_velocity_m_s']:.6f}|{r['cap_draw_J']:.3f}|\n"
    report+=f'''
Every listed case is **ARREST_STROKE_EXCEEDED**,with release-speed failure as well. The physical arrest end is1.510m;the inherited numerical abort guard is1.511m. The reported nonzero speed is at that abort,not a completed stop. Requested30/50/100m/s trajectories saturate toward roughly the same current/source-limited release regime;their requested value is not their achieved release speed. Individual failed gates,including adverse modulation and some100µH current overshoot,remain in MODEL_CASES and full case JSON.

## Why the current device rejects these requests

The accelerated assembly is **{moving:.9f}kg={sled:.9f}kg retained sled/pallet+4kg payload**. The finite retained-host reduced masses are{mu:.9f}kg during acceleration and{mub:.9f}kg during arrest. Momentum and energy accounting use those masses;fixed-lab kinetic energies are also tabulated separately.

Integrating the actual current brake map across210mm gives{brake_integral:.9f}J per peak phase ampere. Even an instantaneous,loss-free,constant600A brake supplies at most**{600*brake_integral:.3f}J** of relative work,corresponding to an optimistic **{bounds['optimistic_arrest_speed_ceiling_at600A_no_losses_m_s']:.3f}m/s** ceiling. That is a necessary bound,not an achievable rating. At10m/s the sled alone requires{constraints[0]['finite_host_relative_arrest_work_J']:.2f}J relative arrest work and{constraints[0]['mean_arrest_force_in_210mm_N']:.1f}N mean force. The field-map work bound would require{constraints[0]['optimistic_constant_phase_current_arrest_A']:.0f}A before current ramp/source/regeneration constraints. Longer acceleration alone cannot fix the retained210mm arrest region.

The same600A idealized drive-work bound reaches only{bounds['optimistic_drive_speed_ceiling_at600A_no_losses_m_s']:.3f}m/s within1.3m,ignoring all losses and source voltage. Nominal energy usable between86.4V and the60V stop gate is{nominal_usable:.1f}J;the adverse capacitance case gives{adverse_usable:.1f}J. The initial positive source-power budgets are{bounds['nominal_initial_positive_source_power_budget_W']:.1f}/{bounds['adverse_initial_positive_source_power_budget_W']:.1f}W and decrease with bank voltage. Those are distinct from stored energy. A no-ESR/no-load q-voltage bound is{bounds['optimistic_initial_q_voltage_ceiling_no_ESR_V']:.2f}V;100m/s back-EMF alone requires about{constraints[-1]['optimistic_back_EMF_q_voltage_V']:.2f}V before resistance/inductance/control margin. Current ratings and voltage cannot be relaxed to make a case pass.

CONSTRAINTS includes launch/arrest energy,acceleration/load,mean force,phase-current work bounds,source voltage/power,transient/final host recoil and angular impulse for a declared0.1m offset. Counter-torque,actual mounting offset/inertia and source thermal/contact/actuator limits still require a selected new configuration. Draw-until-abort is not a complete-shot efficiency or a full brake-heat measurement.

## Next design targets

1. **10m/s first:**a separately identified design with adequate drive voltage/current/power and a much longer or different arrest system. Even an unrealistically constant best-case600A force needs at least{constraints[0]['optimistic_drive_length_600A_best_coefficient_m']:.3f}m drive and{constraints[0]['optimistic_arrest_length_600A_best_coefficient_m']:.3f}m arrest. Add margin,mass and finite-field/end/custody/source/thermal analyses;these are lower bounds,not a proposed accepted layout.
2. **15m/s second:**its ideal lower bounds rise to{constraints[1]['optimistic_drive_length_600A_best_coefficient_m']:.3f}m drive/{constraints[1]['optimistic_arrest_length_600A_best_coefficient_m']:.3f}m arrest. It needs a new power/controller/mechanism and coupled re-evaluation. Qualifying10m/s would not automatically qualify15m/s.
3. **30m/s and above later:**quadratic launch/arrest energy and load growth changes the architecture.50/100m/s launch kinetic work alone exceeds the present usable bank boundary before losses;100m/s also exceeds its ideal back-EMF voltage headroom. Do not transfer the historical16.029m/s periodic result or induction-launch simulation into a current rating.

HYP-L2m,HYP-L5m andHYP-L10m are explicitly **different hypothetical revisions**,shown only as static requirement arithmetic. The unchanged local k(x) does not validate a longer winding,commutation,end coverage,inductance,added structural mass,cooling or arrest system. No long-rail source simulation or linear-force extrapolation is claimed validated.

## Published experiments:what can support model applicability

The actual existing20-page Zhao2022 publisher PDF was hash-verified,and selected topology/model,field/force and release passages were reread(pp3–14,17–18). Its measured gap-center field is about0.424T in the ejection unit;field-position curves and force-current/coil-position tests are genuine benchmark observables. The counterweighted1kg/3kg tests reach0.67–1.42/0.40–0.85m/s at0.5–2.5A. Derived payload kinetic-energy ranges are0.22445–1.0082J and0.24–1.08375J. These are measured data ranges under the source's conditions,not ACR1 measurements.

Those experiments can substantiate a reconstruction of the **published** force/field/work-energy model at its own geometry and currents. They do not physically validate VOLLEY or directly substantiate10/15/30/50/100m/s. Its yoked,double-magnetic-circuit voice coil differs from the finite air-core Halbach topology:ACR1 has six blocks per48mm magnetic period and42 blocks per side,with12mm magnet-face spacing in the field model. That magnetic gap is not a mechanical running-clearance rating. Gap,turns/material properties,current density,armature reaction,contact/friction and speed must be matched or bounded. The authors explicitly note increasing high-current force overprediction from omitted armature reaction,and release differences below11% from their model under their tests. That11% is neither a measured dispersion nor an ACR1 uncertainty allowance. No digitized-curve fit or quantitative external-model reproduction was performed here.

EXPERIMENTAL_BENCHMARK_CARDS identifies measured field/force/release observables and the exact next reconstruction/uncertainty steps. The2025 gravity-assisted transport experiments are a separate contact/custody benchmark. Feng's230–321m/s induction-launch results are simulation;Yamaguchi's relevant end-effect work is2D theory with hardware future work;the closed voice-coil paper remains metadata-only. None is relabeled measured support for this rail. No new paywall bypass,provider contact or invented full-text reading occurred.

## Numerical checks and reproducibility

Four20→5µs pairs retain the same rejection. Maximum release-speed change is{max(abs(r['release_speed_change_m_s']) for r in refine):.8f}m/s;abort-position change{max(abs(r['boundary_exit_position_change_mm']) for r in refine):.6f}mm. Independent reduced-mass kinetic-energy plus friction agrees with signed motor work to{max(abs(r['independent_mechanical_work_residual_J']) for r in invariants):.3g}J. Original declared total-energy checks are retained;failed physical/design gates are not overridden by numerical convergence.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 run_screen.py
python3 analyze_screen.py
python3 check_capture.py
```

The field map and accepted original outputs are inputs,not rerun scripts. finite_motor.py is captured unchanged for provenance. The runner changes only arguments and output location. No accepted source/PDF,repository,Sheet orDrive file was modified. High-target trajectories and hypothetical designs belong in **Labs/research**;Main may link a bounded rejection summary,source-backed constraints and current1/2/3m/s status. New10–15m/s operating claims require the separately designed coupled configuration,appropriate model benchmarks,convergence,uncertainty and targeted physical measurements. External experiments can support applicable equations;VOLLEY-specific experimental validation still requires relevant article measurements.
'''
    report+='''
## Separate Gen6/Labs trade: attached flyaway launch shoe

A shoe that remains attached to a modified CubeSat can remove the successful-departure sled-arrest/return requirement. It creates a different payload interface and outbound mass. The 0.25/0.5/1 kg shoe values below are unsubstantiated sensitivity assumptions, not feasible designs or achieved adapter masses. No current k(x), current waveform or force map is transferred to the redesigned magnetic/guide structure.

At the same ideal fixed-lab launch work, the moving-mass-only speed ratio is sqrt[(13.127805767+4)/(4+m_shoe)]. This relation omits changes in field, source, friction, geometry, finite-host mass and losses. It is not a predicted achieved release speed.

| Hypothetical shoe | Outbound payload+shoe | Same-work ideal mass-only ratio | Twelve adapters | Successful-departure arrest |
|---:|---:|---:|---:|---|
'''
    for adapter in [.25,.5,1.,sled]:
        report+=f'|{adapter:.6f} kg|{4+adapter:.6f} kg|{math.sqrt(moving/(4+adapter)):.6f}×|{12*adapter:.6f} kg|No retained sled to arrest|\n'
    report+='''
The full-sled flyaway row keeps the same 17.127806 kg moving assembly and a 1× ideal ratio: removing arrest supplies no launch-energy mass saving. It also needs twelve full launch members, versus one reusable 13.127806 kg sled today. The lightweight-shoe rows require twelve attached adapters; their inventory is 3/6/12 kg, but this limited comparison says nothing about complete installed-device mass or actual magnetic hardware feasibility. No adapter is assumed discarded as free debris.

The frozen CAD BOM provides a decisive compatibility check:84 moving magnet blocks already total3.6288kg under the current density/geometry model. The assumed0.25/0.5/1kg shoes cannot retain that magnet set,even before guide,structure and positive attachment mass. Those small sensitivities therefore require a materially redesigned electromagnetic geometry/topology;they are not achievable mass estimates for a trimmed current carrier. Six blocks describes one magnetic period,not the entire current array.

Removing arrest does not convert any rejected current-model trajectory into a qualified flyaway design. The current ten-metre-per-second cases already miss their requested speed before the arrest failure; changing release/custody and exit dynamics requires a new model. A flyaway configuration also carries the adapter's momentum away, changes host recoil and per-release mass history, and changes payload magnetic exposure, centre of gravity, structural attachment and later attitude/mission behavior.

Next gates are: define the actual minimum field/guide/interface assembly and substantiate its mass; retain the shoe positively on the payload; develop storage/transfer/rail-exit/partial-launch containment; calculate its new finite magnetic field and current/source/thermal response; propagate all twelve adapter inventories and recoils; and establish payload structural, magnetic, contamination and mission acceptance. A lighter shoe is a reasonable next architecture study, not a demonstration that a 0.25–1 kg launcher adapter is achievable.
'''
    report=report.replace('# Higher-speed assessment:bounded first screen','# Higher-speed design constraints')
    report=report.replace('26October2026','26 October 2026')
    report=report.replace('Zhao2022','[Zhao et al. (2022)](https://doi.org/10.3390/rs14174205)')
    report=re.sub(r'(?<=\d)(?=[A-Za-zµ])',' ',report)
    report=report.replace(',nominal',', nominal').replace(',adverse',', adverse')
    chunks=report.split('```')
    for i in range(0,len(chunks),2):
        urls=[]
        def stash(match):urls.append(match.group());return '@URL_'+str(len(urls)-1)+'@'
        chunk=re.sub(r'https?://[^\s]+',stash,chunks[i])
        chunk=re.sub(r'(?<=[a-z])(?=\d)',' ',chunk)
        chunk=re.sub(r'(?<=[,;:])(?=[A-Za-z0-9])',' ',chunk)
        chunk=chunk.replace('most**','most **')
        for j,url in enumerate(urls):chunk=chunk.replace('@URL_'+str(j)+'@',url)
        chunks[i]=chunk
    report='```'.join(chunks)
    (H/'REPORT.md').write_text(report)
    print('PASS:22rejected trajectories,4refinements,5constraint rows,15hypotheticalrail budgets,measured-literature applicability cards and scientificfigure/report.')
if __name__=='__main__':main()
