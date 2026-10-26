"""Analyze sampled source-model gates and separate hypothetical mass/length budgets."""
from pathlib import Path
import csv,hashlib,json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;C=H.parent/'higher-speed-envelope/capture'
def load(p):return json.loads(p.read_text())
def dump(name,x):(H/name).write_text(json.dumps(x,indent=2)+'\n')
def table(name,rows):
    with (H/name).open('w',newline='') as f:
        fields=list(dict.fromkeys(k for r in rows for k in r));w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()})
def main():
    rows=load(H/'CASES.json')['cases'];definition=load(H/'SCAN_DEFINITION.json');pins=load(H/'SOURCE_PINS.json')
    compact=[];refinement=[];mechanical=[];upper=[]
    for r in rows:
        release=r['release'];host=r['reference_rest_host_kg'];sled=r['moving_sled_kg'];mu=(sled+4)*host/(host+sled+4);mub=sled*host/(host+sled)
        if release:
            work=.5*(mu-mub)*release['relative_speed_m_s']**2+.5*mub*r['stop_velocity_m_s']**2+r['mechanical_friction_dissipation_J']
            difference=r['energy_ledger']['mechanical_J']-work
            assert abs(difference)<1e-6
            mechanical.append(dict(case=r['case_id'],independent_motor_work_residual_J=difference))
        compact.append(dict(case=r['case_id'],command_m_s=r['target_m_s'],adverse=r['adverse'],L_uH=r['inductance_H']*1e6,dt_us=r['dt_s']*1e6,
            modeled_rear_contact_release_relative_m_s=None if release is None else release['relative_speed_m_s'],
            payload_inertial_kick_m_s=None if release is None else release['payload_inertial_delta_v_m_s'],
            source_status=r['status'],terminal_position_m=r['stop_position_m'],terminal_relative_speed_m_s=r['stop_velocity_m_s'],
            release_speed_gate_pass=r['checks']['release_speed'],launch_arrest_gates_pass=r['all_declared_checks_pass'],
            powered_return_reset_simulated=False,full_exit_clearance_verified=False,operational_lower_floor_m_s=None,
            energy_balance_gate=r['checks']['energy_balance'],energy_residual_J=r['energy_residual_J'],
            peak_phase_current_A=r['peak_phase_current_A'],cap_draw_J=r['cap_draw_J'],
            failed_gates=[k for k,v in r['checks'].items() if not v],reused_accepted_capture=r['reused_accepted_capture']))
        if r['dt_s']==5e-6:
            coarse=next(x for x in rows if x['target_m_s']==r['target_m_s'] and x['adverse']==r['adverse'] and x['inductance_H']==r['inductance_H'] and x['dt_s']==20e-6)
            refinement.append(dict(command_m_s=r['target_m_s'],adverse=r['adverse'],L_uH=r['inductance_H']*1e6,
                coarse_gates_pass=coarse['all_declared_checks_pass'],fine_gates_pass=r['all_declared_checks_pass'],
                same_gate_result=coarse['all_declared_checks_pass']==r['all_declared_checks_pass'],
                terminal_position_change_mm=1000*(r['stop_position_m']-coarse['stop_position_m']),
                release_speed_change_m_s=None if r['release'] is None else r['release']['relative_speed_m_s']-coarse['release']['relative_speed_m_s'],
                cap_draw_change_J=r['cap_draw_J']-coarse['cap_draw_J']))
    ranges=[]
    for adverse in [False,True]:
        rr=sorted([r for r in rows if r['adverse']==adverse and r['inductance_H']==20e-6 and r['dt_s']==20e-6],key=lambda r:r['target_m_s'])
        passing=[r for r in rr if r['all_declared_checks_pass']]
        ranges.append(dict(adverse=adverse,inductance_uH=20,sampled_min_command_gate_pass_m_s=passing[0]['target_m_s'],
            sampled_max_command_gate_pass_m_s=passing[-1]['target_m_s'],lower_operational_floor_m_s=None,
            interpolation_validated=False,return_reset_or_feeder_safe_claim=False))
        for L in [3e-6,20e-6,100e-6]:
            sampled=sorted([r for r in rows if r['adverse']==adverse and r['inductance_H']==L and r['dt_s']==20e-6],key=lambda r:r['target_m_s'])
            passes=[r for r in sampled if r['all_declared_checks_pass']];high=passes[-1]['target_m_s']
            later=[r for r in sampled if r['target_m_s']>high and not r['all_declared_checks_pass']]
            upper.append(dict(adverse=adverse,L_uH=L*1e6,last_sampled_pass_m_s=high,next_sampled_fail_m_s=later[0]['target_m_s'],
                bracket_width_m_s=later[0]['target_m_s']-high,
                lower_inductance_boundary_fully_scanned=L==20e-6,
                conditional_scope='Sampled source-model launch/arrest gates only;no continuous or operational envelope qualification.'))
    assert all(x['same_gate_result'] for x in refinement)
    table('SAMPLED_CASES.csv',compact);table('UPPER_BOUNDARIES.csv',upper);table('TIMESTEP_REFINEMENT.csv',refinement)
    # Common baseline nonmoving hardware is held fixed only for explicit mass accounting.
    home=load(C/'cad/release/VOLLEY_G5_ACR1_home.json');sled=rows[0]['moving_sled_kg']
    dry=sum(r['mass_kg'] for r in home['BOM'] if r['subsystem']!='payload')+7
    magnets=[r for r in home['BOM'] if r['subsystem'].startswith('sled') and 'magnet' in str(r).lower()]
    floor=sum(r['mass_kg'] for r in magnets);assert len(magnets)==84 and math.isclose(floor,3.6288,abs_tol=1e-10)
    fixed=dry-sled
    variants=[('RETAINED_CURRENT',sled,False,'Current complete moving sled/pallet.'),
        ('FLYAWAY_MAGNET_FLOOR',floor,True,'84 current magnets only;nonbuildable lower bound,zero support/attachment allocation.'),
        ('FLYAWAY_MAGNET_PLUS_1KG',floor+1,True,'3.6288kg magnets plus1kg explicitly hypothetical support/retention allocation;not substantiated achievable mass.'),
        ('FLYAWAY_FULL_SLED',sled,True,'Complete13.127805767kg sled remains attached to payload;no moving-mass launch-energy saving.')]
    inventory=[];geometry=[];ranking=[]
    lengths=[1.3,2.5,5.,10.];g0=9.80665
    for name,adapter,fly,note in variants:
        count=12 if fly else 1;initial=500+fixed+48+count*adapter
        outbound=4+adapter;rest=initial-outbound
        mu=outbound*rest/initial
        massrow=dict(variant=name,adapter_kg=adapter,payload_kg=4,moving_assembly_kg=outbound,
            adapter_inventory_count=count,adapter_inventory_kg=count*adapter,
            common_nonmoving_device_allocation_kg=fixed,initial12payload_total_kg=initial,
            reference_rest_host_first_event_kg=rest,first_event_accelerated_reduced_mass_kg=mu,
            successful_departure_requires_retained_sled_arrest=not fly,
            ideal_same_work_mass_only_speed_ratio=math.sqrt((sled+4)/outbound),
            full_installed_architecture_validated=False,manufactured_mass_measured=False,
            mass_basis='Current CAD-computed carrier' if name=='RETAINED_CURRENT' else 'Explicit hypothetical allocation or magnet-only lower bound',
            assumption=note)
        inventory.append(massrow)
        for speed in [10,15,30,50,100]:
            launch=.5*mu*speed**2
            mu_brake=sled*rest/(sled+rest) if not fly else None
            arrest=None if fly else .5*mu_brake*speed**2
            for length in lengths:
                a=speed**2/(2*length)
                geometry.append(dict(variant=name,target_relative_m_s=speed,drive_length_m=length,
                    ideal_relative_acceleration_g=a/g0,ideal_relative_acceleration_time_s=2*length/speed,
                    first_event_relative_launch_kinetic_work_J=launch,ideal_mean_drive_force_N=mu*a,
                    kinematic_within5g=a<=5*g0,kinematic_within10g=a<=10*g0,kinematic_within25g=a<=25*g0,
                    matched_arrest_length_m=None if fly else length,
                    ideal_mean_arrest_force_N=None if fly else arrest/length,
                    first_event_relative_arrest_kinetic_work_J=arrest,
                    current_force_map_transferred=False,actual_coupled_new_configuration_run=False))
            for g in [5,10,25]:
                necessary=speed**2/(2*g*g0);candidate=next((l for l in lengths if l>=necessary),None)
                ranking.append(dict(variant=name,target_relative_m_s=speed,relative_acceleration_cap_g=g,
                    necessary_drive_length_m=necessary,first_listed_drive_length_meeting_g_m=candidate,
                    necessary_retained_sled_arrest_length_m=None if fly else necessary,
                    first_listed_arrest_length_meeting_g_m=None if fly else candidate,
                    source_force_thermal_interface_feasibility_established=False,
                    priority='10m/s first;15m/s next;30+requires larger architecture and source changes',
                    status='kinematic requirement only;new coupled configuration pending'))
    table('MASS_INVENTORY.csv',inventory);table('GEOMETRY_REQUIREMENTS.csv',geometry);table('RANKED_REQUIREMENTS.csv',ranking)
    dump('ANALYTICAL_ASSUMPTIONS.json',dict(current_magnet_count=84,current_computed_magnet_floor_kg=floor,
        common_mass_boundary='500kg wet bus + fixed current nonmoving device allocation +48kg payloads + one reusable carrier OR12attached adapters. This explicit inventory does not validate packaging or unchanged nonmoving structure.',
        instantaneous_host_boundary='First-event finite-host reduced masses use the above fully declared mass inventory. No12release mission or actual new host simulation is performed.',
        acceleration_caps='5/10/25g refer to relative rail-frame kinematics,not approved payload acceleration limits.',
        current_field_force_map_transferred=False,force_source_coupled_geometry_validation=False,
        low_mass_shoe_constraint='0.25/0.5/1kg cannot retain the current3.6288kg moving magnet set;those earlier sensitivities need a new topology.',
        shoe_retention='Adapters remain attached to modified payloads;no free adapter debris credited.',
        abort_scope='Removing successful-departure arrest does not remove partial-launch,stuck-payload or ambiguous-release containment requirements.'))
    candidates=[dict(id='R10',priority=1,target_m_s=10,architecture='Retained carrier',drive_length_m=2.5,arrest_length_m=1.3,
        status='pending_new_coupled_geometry',reason='New finite field,resistance/inductance,source,arrest,loads,thermal,custody and mass inputs required;no unchanged-map extrapolation.'),
        dict(id='F10',priority=2,target_m_s=10,architecture='Attached flyaway shoe',assumed_shoe_kg=floor+1,
        shoe_mass_allocation='3.6288kg current magnets+1kg unsubstantiated structural/retention allocation',drive_length_m=2.5,
        status='pending_geometry_mass_interface_then_coupled_model',reason='Mass/guide/attachment/storage/exit/abort and full first-event/campaign recoil require a selected geometry;no current force-map transfer.')]
    dump('NEXT_COUPLED_CANDIDATES.json',dict(candidates=candidates,neither_completed=True,no_further_study_run=True))
    summary=dict(study='ACR1-SAMPLED-LAUNCH-ARREST-ENVELOPE-01',records=len(rows),accepted_reuses=sum(r['reused_accepted_capture'] for r in rows),
        new_unique_computations=sum(not r['reused_accepted_capture'] for r in rows),dt_refinements=len(refinement),
        trace_files=[r['trace_file'] for r in rows if 'trace_file' in r],ranges_20uH=ranges,upper_brackets=upper,
        common_upper_confirmations=definition['common_upper_confirmations'],
        max_refined_release_speed_change_m_s=max(abs(r['release_speed_change_m_s']) for r in refinement),
        max_refined_terminal_position_change_mm=max(abs(r['terminal_position_change_mm']) for r in refinement),
        max_independent_motor_work_residual_J=max(abs(r['independent_motor_work_residual_J']) for r in mechanical),
        source_limits_changed=False,controller_optimized=False,operational_lower_floor_m_s=None,
        full_clearance_feeder_interlock_or_return_reset_proved=False,
        repeated_thermal_or_structural_acceptance_at_new_commands=False,
        native_contact_at_new_commands_verified=False,published_current_points_m_s=[1,2,3])
    dump('RESULTS.json',summary);dump('NUMERICAL_CHECKS.json',dict(passed=True,mechanical_work=mechanical,refinements=refinement))
    # Neutral, publication-sized figures; markers denote model checks only.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2,'svg.fonttype':'none','pdf.fonttype':42})
    colors={False:'#087f81',True:'#b56b12'}
    fig,axes=plt.subplots(1,3,figsize=(15,4.8),layout='constrained')
    for adverse in [False,True]:
        rr=sorted([r for r in rows if r['adverse']==adverse and r['inductance_H']==20e-6 and r['dt_s']==20e-6],key=lambda r:r['target_m_s'])
        col=colors[adverse];label='Adverse' if adverse else 'Nominal'
        for passed,marker in [(True,'o'),(False,'x')]:
            selected=[r for r in rr if r['all_declared_checks_pass']==passed and r['release'] is not None]
            axes[0].scatter([r['target_m_s'] for r in selected],[r['release']['relative_speed_m_s'] for r in selected],color=col,marker=marker,s=28,label=label+(' gates pass' if passed else ' gates fail'))
        missing=[r for r in rr if r['release'] is None]
        if missing:axes[0].scatter([r['target_m_s'] for r in missing],[-.13]*len(missing),color=col,marker='v',s=28,label=label+' no release event')
        focus=[r for r in rr if r['target_m_s']>=2.5]
        axes[1].plot([r['target_m_s'] for r in focus],[r['stop_position_m'] for r in focus],'-o',ms=3,color=col,label=label)
    axes[0].plot([0,4.8],[0,4.8],'--',color='.5',lw=1);axes[0].set(xlabel='Requested command [m/s]',ylabel='Modeled contact-release relative speed [m/s]',title='A  20 µH: sampled launch/arrest gates',xlim=(0,4.85),ylim=(-.25,4.85));axes[0].legend(fontsize=8)
    axes[1].axhline(1.51,color='#a54444',ls='--',label='210 mm arrest end');axes[1].set(xlabel='Requested command [m/s]',ylabel='Terminal carrier position [m]',title='B  Upper-region arrest position zoom',ylim=(1.501,1.513),xlim=(2.5,4.8));axes[1].legend(fontsize=8)
    labels=[]
    for i,r in enumerate(upper):
        axes[2].plot([r['last_sampled_pass_m_s'],r['next_sampled_fail_m_s']],[i,i],color=colors[r['adverse']],lw=2)
        axes[2].scatter([r['last_sampled_pass_m_s']],[i],color=colors[r['adverse']],marker='o',s=30)
        axes[2].scatter([r['next_sampled_fail_m_s']],[i],color=colors[r['adverse']],marker='x',s=36)
        labels.append(('Adv' if r['adverse'] else 'Nom')+f" {r['L_uH']:g} µH")
    axes[2].set(yticks=range(len(upper)),yticklabels=labels,xlabel='Last pass ○ / next fail × [m/s]',title='C  Upper brackets, confirmed at 5 µs',xlim=(3.5,4.85));axes[2].invert_yaxis()
    fig.suptitle('Frozen ACR1: modeled release/arrest response and upper command brackets',fontsize=14,weight='bold')
    fig.savefig(H/'SAMPLED_ENVELOPE.png',dpi=180);fig.savefig(H/'SAMPLED_ENVELOPE.pdf');fig.savefig(H/'SAMPLED_ENVELOPE.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.4),layout='constrained');v=np.linspace(10,100,200)
    for g,col in [(5,'#087f81'),(10,'#b56b12'),(25,'#6c679c')]:axes[0].plot(v,v*v/(2*g*g0),label=f'{g} g relative cap',color=col)
    for length in lengths:axes[0].axhline(length,color='.6',lw=.7,ls=':')
    axes[0].set(xlabel='Target relative speed [m/s]',ylabel='Minimum kinematic drive/arrest distance [m]',yscale='log',title='A  Geometry requirement; force not established');axes[0].legend(fontsize=8)
    values=[r['adapter_inventory_kg'] for r in inventory];names=['Reusable\ncarrier','Flyaway\nmagnet floor','Flyaway\nmagnet + 1 kg','Flyaway\nfull sled']
    axes[1].bar(names,values,color=['#087f81','#b56b12','#a48a5b','#8b9198'])
    for i,value in enumerate(values):axes[1].text(i,value+3,f'{value:.2f}',ha='center',fontsize=9)
    axes[1].set(ylabel='Launch-member inventory for 12 payloads [kg]',title='B  One reusable carrier versus 12 attached shoes')
    fig.suptitle('Hypothetical geometry/mass requirements: no new force-map or source validation',fontsize=13,weight='bold')
    fig.savefig(H/'GEOMETRY_AND_INVENTORY.png',dpi=180);fig.savefig(H/'GEOMETRY_AND_INVENTORY.pdf');fig.savefig(H/'GEOMETRY_AND_INVENTORY.svg');plt.close(fig)
    for name in ['SAMPLED_ENVELOPE.svg','GEOMETRY_AND_INVENTORY.svg']:
        svg=H/name
        svg.write_text(''.join(line.rstrip()+'\n' for line in svg.read_text().splitlines()))
    # Exact scope and results are prose; no full-cycle or hardware extension is inferred.
    report=f'''# Sampled speed and architecture requirements

This bounded study evaluates the unchanged pinned ACR1 averaged source model. It contains **{len(rows)} unique records: {summary['new_unique_computations']} newly computed cases and {summary['accepted_reuses']} accepted-case reuses**. The specified 0.1–4.7 m/s coarse scan uses 0.25 m/s increments plus exact 1/2/3 command points and the 4.7 endpoint, nominal/adverse at 20 µH/20 µs. Observed transitions are resolved at 0.05 m/s, with targeted 3/100 µH upper-bracket bisections and **{len(refinement)} 5 µs checks**. Only two upper-edge histories are retained. No source, voltage, current, control or acceptance limit was changed or optimized.

[Sampled source-model gates](SAMPLED_ENVELOPE.svg) · [Separate geometry and inventory requirements](GEOMETRY_AND_INVENTORY.svg). Editable SVG text and Type42-font PDF exports accompany each PNG.

## What the sampled gates say

At **20 µH**, nominal sampled commands pass the source model's launch/arrest checks from **0.10 through 4.65 m/s**; 4.70 fails arrest. Adverse sampled commands pass from **0.70 through 3.75 m/s**; 0.65 fails the release-speed tolerance and 3.80 fails the arrest-position gate. The 5 µs checks retain those pass/fail results. These are sampled computational results; interpolation between commands is not experimentally validated.

| Condition | L (µH) | Last sampled upper pass | Next sampled fail |
|---|---:|---:|---:|
'''
    for r in upper:report+=f"|{'Adverse' if r['adverse'] else 'Nominal'}|{r['L_uH']:g}|{r['last_sampled_pass_m_s']:.2f} m/s|{r['next_sampled_fail_m_s']:.2f} m/s|\n"
    report+=f'''
Inductance sensitivity matters: the adverse 20 µH upper value must not be transferred to 3/100 µH. Their upper sampled pass is 3.70 m/s, with 3.75 failing. The common upper sampled commands are **4.60 m/s nominal and 3.70 m/s adverse**, each explicitly checked at 5 µs at all three inductances. The complete lower-speed scan was performed only at 20 µH; 3/100 µH share the original 1/2/3 evidence plus targeted upper samples. No continuous all-inductance interval is established.

`STOPPED` in the inherited code means the **first low-speed turnaround**. It does not simulate powered return/reset, full payload exit clearance, contact/interlock proof, custody completion or a safe feeder cycle. A STOPPED case can still exceed the allowed position: the adverse 3.80 m/s result illustrates this. SAMPLED_CASES exposes the source status and every failed gate separately.

The requested command is separate from the modeled rear-contact release speed and payload inertial kick. The model's release event is not a verified complete payload exit. Its cam-open check is a position proxy, not a fresh geometry/interlock demonstration. The **operational lower-speed floor is unset**: low-speed clearance, stiction/contact uncertainty, timing and interlocks are not established by a kinetic-model pass. Current published ACR1 command points remain **1, 2 and 3 m/s**; this study supplies additional research evidence, not a hardware rating.

The averaged source calculation retains its fixed nominal/adverse resistance and component allocations. It does not establish new repeated-duty winding/source temperatures, structural/tolerance life, six-degree-of-freedom contact/exit behavior or EMC acceptance at the additional commands. Those broader gates remain necessary before any operational or article-speed extension.

## Numerical checks

All {len(refinement)} coarse/fine decisions agree. Maximum 20→5 µs contact-release speed change is {summary['max_refined_release_speed_change_m_s']:.8g} m/s; terminal-position change is {summary['max_refined_terminal_position_change_mm']:.6g} mm. Independent reduced-mass kinetic work plus friction agrees with signed motor work to {summary['max_independent_motor_work_residual_J']:.3g} J. Original declared total-energy and component gates are retained as returned by the model; failed cases stay visible. Source and input hashes match the sibling accepted capture.

## Separate architecture requirements

The analytical sweep covers 1.3/2.5/5/10 m drive and retained-sled arrest lengths, 5/10/25 g **relative-motion** caps, and 10/15/30/50/100 m/s targets. GEOMETRY_REQUIREMENTS contains 80 variant/speed/length rows; RANKED_REQUIREMENTS contains 60 variant/speed/g rows. Passing a kinematic distance condition does not establish force, source, thermal, structural or payload acceptance. No current force map is transferred to any changed geometry.

Every mass variant is explicit. The common nonmoving allocation is {fixed:.6f} kg, including the current 7 kg power/control allowance once; the notional bus is 500 kg wet and the manifest remains 12×4 kg. A reusable current carrier occurs once; flyaway adapters occur twelve times. First-event reduced masses and host inventory are recomputed from those assumptions, with no claimed 12-release simulation.

| Variant | Adapter mass | Number carried | Adapter inventory | Initial combined mass |
|---|---:|---:|---:|---:|
'''
    for r in inventory:report+=f"|{r['variant']}|{r['adapter_kg']:.6f} kg|{r['adapter_inventory_count']}|{r['adapter_inventory_kg']:.6f} kg|{r['initial12payload_total_kg']:.6f} kg|\n"
    report+='''
The 3.6288 kg floor comprises 84 current moving magnets only. It has no guide, support or attachment allowance and is not a buildable shoe. The magnet-plus-1 kg variant has a fully stated mass allocation, but its 1 kg structural/retention allowance is unsubstantiated. Full-sled flyaway removes successful-departure arrest but retains the same moving mass and requires twelve complete members. Its release dynamics, payload interface and mass budget are a different architecture. Attached adapters are not credited as free debris; partial-launch and stuck-payload containment remain required.

Individual moving-mass energy savings can coexist with a larger total adapter inventory. Even the magnet-only flyaway floor carries 43.5456 kg of magnets over twelve payloads versus one current 13.1278 kg moving carrier. A 0.25/0.5/1 kg shoe cannot retain the present magnet set and needs a different electromagnetic topology. Complete installed mass, payload magnetic acceptance and mission advantage remain unproved.

## What remains pending

Ten metres per second is the first new design target; fifteen follows before 30+. The two candidate records R10 (2.5 m drive/1.3 m retained arrest) and F10 (2.5 m drive, attached magnet-plus-1 kg shoe) are **pending coupled work**, not completed designs. Their dimensions are requirement hypotheses. New finite fields, resistance/inductance, source/braking or exit control, actual structural mass, geometry/custody, thermal and payload/host interfaces are required. This deliverable stops at the verified frozen-model scan and analytical requirements; it does not replace those missing studies with extrapolated force curves.

## Reproduce

Run `python3 run_envelope.py`, `MPLCONFIGDIR=/tmp/volley-env-mpl python3 analyze.py`, then `python3 check_capture.py`. The driver caches exact parameter cases and reuses matching accepted records. The immutable source is `../higher-speed-envelope/capture/analysis/coupled_shot.py`; SOURCE_PINS records its exact identity and input hashes. Only this new folder is written. Accepted files, repositories outside this new folder and current academic outputs are untouched. No commit or push is performed.
'''
    (H/'README.md').write_text(report)
    from make_hero import update
    update()
    print('PASS:',len(rows),'records;',len(refinement),'refinements;80 geometry requirements;60 ranked requirements;two coupled candidates pending.')
if __name__=='__main__':main()
