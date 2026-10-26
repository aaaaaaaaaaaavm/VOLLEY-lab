"""Summarize actual new-design computations and produce one-message source-linked figures."""
from pathlib import Path
import csv,hashlib,json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from coupled_design import simulate
H=Path(__file__).resolve().parent
def load(name):return json.loads((H/name).read_text())
def dump(name,x):(H/name).write_text(json.dumps(x,indent=2)+'\n')
def save(fig,name):
    for suffix in ['png','pdf','svg']:fig.savefig(H/(name+'.'+suffix),dpi=150,bbox_inches='tight')
    f=H/(name+'.svg');f.write_text(''.join(s.rstrip()+'\n' for s in f.read_text().splitlines()));plt.close(fig)
def main():
    primary=load('COUPLED_RESULTS.json');rows=primary['cases'];refined=[];comparisons=[]
    for name in ['R10','F10']:
        d=load(name+'_DESIGN.json');mass=load(name+'_MASS.json');field=load(name+'_REFINED_FIELD.json')
        fine=dict(d);fine['finite_field_stations']=field['stations']
        for adverse in [False,True]:
            result=simulate(fine,mass,adverse,5e-6);result.pop('trace');result['id']=name+('_adverse' if adverse else '_nominal')+'_refinedfield_dt5us'
            refined.append(result)
            base=next(r for r in rows if r['configuration']==d['configuration'] and r['adverse']==adverse and r['dt_s']==5e-6)
            comparisons.append(dict(configuration=d['configuration'],adverse=adverse,
                primary_gates_pass=base['all_model_gates_pass'],refined_field_gates_pass=result['all_model_gates_pass'],
                primary_release_m_s=base['release']['relative_speed_m_s'],refined_release_m_s=result['release']['relative_speed_m_s'],
                release_change_m_s=result['release']['relative_speed_m_s']-base['release']['relative_speed_m_s'],
                final_position_change_mm=1000*(result['final_position_m']-base['final_position_m']),
                source_draw_change_J=result['source_draw_J']-base['source_draw_J'],
                failed_refined_gates=[k for k,v in result['checks'].items() if not v]))
            print(result['id'],result['status'],result['all_model_gates_pass'],result['release']['relative_speed_m_s'],flush=True)
    dump('REFINED_COUPLED_RESULTS.json',dict(cases=refined,comparisons=comparisons,
        refinement='Actual transverse-return quadrature1→3,critical0.05m field stations and5µs motion;not old-map scaling.'))
    step=[]
    for r in rows:
        if r['dt_s']!=5e-6:continue
        coarse=next(x for x in rows if x['configuration']==r['configuration'] and x['adverse']==r['adverse'] and x['dt_s']==20e-6)
        step.append(dict(configuration=r['configuration'],adverse=r['adverse'],same_gate_result=coarse['checks']==r['checks'],
            release_change_m_s=r['release']['relative_speed_m_s']-coarse['release']['relative_speed_m_s'],
            terminal_position_change_mm=1000*(r['final_position_m']-coarse['final_position_m'])))
    dump('NUMERICAL_CHECKS.json',dict(timestep_comparisons=step,field_comparisons=comparisons,
        max_independent_mechanical_work_residual_J=max(abs(r['independent_mechanical_residual_J']) for r in rows+refined),
        max_total_energy_residual_J=max(abs(r['total_energy_residual_J']) for r in rows+refined),
        actual_new_geometry_and_source_models=True,whole_mechanism_qualification=False))
    compact=[]
    for r in rows+refined:
        compact.append(dict(case=r['id'],configuration=r['configuration'],adverse=r['adverse'],dt_us=r['dt_s']*1e6,
            status=r['status'],departure_relative_m_s=r['release']['relative_speed_m_s'],
            final_position_m=r['final_position_m'],final_relative_speed_m_s=r['final_relative_speed_m_s'],
            source_draw_J=r['source_draw_J'],peak_phase_current_A=r['peak_phase_current_A'],peak_hot_device_current_A=r['peak_hot_device_current_A'],
            peak_switch_V=r['peak_switch_V'],winding_adiabatic_rise_C=r['thermal']['winding_adiabatic_rise_C'],
            model_gates_pass=r['all_model_gates_pass'],failed_gates=';'.join(k for k,v in r['checks'].items() if not v)))
    with (H/'RESULTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(compact[0]),lineterminator='\n');w.writeheader();w.writerows(compact)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    colors={'R10':'#087f81','F10':'#b56b12'}
    fig,ax=plt.subplots(figsize=(9,4.8))
    for name in ['R10','F10']:
        f=load(name+'_REFINED_FIELD.json');s=f['stations'];ax.plot([r['displacement_m'] for r in s],[r['N_per_peak_A'] for r in s],lw=2.5,color=colors[name],label=name+(' · 534 finite belts' if name=='R10' else ' · 372 finite belts'))
    ax.axvline(2.5,color='.5',ls='--',lw=1);ax.set(xlabel='Displacement from home [m]',ylabel='Force coefficient [N / peak phase A]',title='Finite winding geometry sets the force map',ylim=(0,1.55));ax.legend();ax.grid(alpha=.2);save(fig,'FINITE_FORCE')
    fig,ax=plt.subplots(figsize=(9,4.8));r=next(r for r in rows if r['id']=='R10_nominal_dt5us');data=np.genfromtxt(H/(r['id']+'_history.csv'),delimiter=',',names=True)
    ax.plot(data['t_s'],data['relative_v_m_s'],lw=2.5,color=colors['R10']);rel=r['release'];ax.scatter([rel['time_s']],[rel['relative_speed_m_s']],s=60,color='#b56b12');ax.annotate('Payload release',(rel['time_s'],rel['relative_speed_m_s']),xytext=(12,-35),textcoords='offset points')
    ax.set(xlabel='Time [s]',ylabel='Carrier relative speed [m/s]',title='R10 accelerates, releases and arrests');ax.grid(alpha=.2);save(fig,'R10_VELOCITY')
    fig,ax=plt.subplots(figsize=(9,4.8));fine=[r for r in rows if r['dt_s']==5e-6]
    labels=[r['configuration'].split('-')[0]+('\nadverse' if r['adverse'] else '\nnominal') for r in fine]
    bars=ax.bar(labels,[r['source_draw_J']/1000 for r in fine],color=[colors[r['configuration'].split('-')[0]] for r in fine])
    for bar,r in zip(bars,fine):ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.06,f"{r['source_draw_J']/1000:.3f}",ha='center',fontsize=14)
    ax.set(ylabel='Net bank energy drawn [kJ]',title='The new source and moving mass change shot energy',ylim=(0,5));ax.text(.01,.96,'F10 adverse misses the unchanged speed gate.',transform=ax.transAxes,va='top',fontsize=11,color='.35');save(fig,'SHOT_ENERGY')
    fig,ax=plt.subplots(figsize=(9,4.5))
    for y in [6,-14]:ax.add_patch(Rectangle((-45,y),90,8,facecolor='#8ca1ad',edgecolor='#344955'))
    ax.add_patch(Rectangle((-45,-3),90,6,facecolor='#bc7439',edgecolor='#805020'))
    for y in [3,-5]:ax.add_patch(Rectangle((-45,y),90,2,facecolor='#8a9c70'))
    ax.annotate('',xy=(58,-6),xytext=(58,6),arrowprops=dict(arrowstyle='<->'));ax.text(60,0,'12 mm\nmagnet gap',va='center')
    ax.annotate('',xy=(-45,-21),xytext=(45,-21),arrowprops=dict(arrowstyle='<->'));ax.text(0,-25,'90 mm active depth',ha='center')
    ax.text(0,20,'42 × 8 mm blocks per side = 336 mm moving array',ha='center',fontsize=13)
    ax.text(0,0,'6 mm copper',ha='center',va='center',fontsize=13,color='white')
    ax.set(xlim=(-65,105),ylim=(-32,26),aspect='equal',title='Declared magnetic cross-section; schematic dimensions');ax.axis('off');save(fig,'MAGNETIC_SECTION')
    checks=load('NUMERICAL_CHECKS.json');report='# R10 and F10: actual ten-metre-per-second design computations\n\n'
    report+='Two new finite windings and explicit mass/source configurations were computed for one-shot averaged circuit/motion analysis. The accepted ACR1 command points remain 1, 2 and 3 m/s.\n\n'
    report+='![New finite geometry force map](FINITE_FORCE.png)\n\n'
    report+='| Case,5 µs | Relative departure | Source draw | Declared circuit/motion gates |\n|---|---:|---:|---|\n'
    for r in fine:report+=f"|{r['configuration']} {'adverse' if r['adverse'] else 'nominal'}|{r['release']['relative_speed_m_s']:.6f} m/s|{r['source_draw_J']:.2f} J|{'pass' if r['all_model_gates_pass'] else 'FAIL: '+','.join(k for k,v in r['checks'].items() if not v)}|\n"
    report+='\n## New geometry and components\n\n'
    report+='R10 uses 534 finite belts,2.5 m powered travel and1.3 m active arrest. Home aft is200 mm,release2700 mm,arrest4000 mm;the new4750 mm rail allows the reused carrier envelope plus margin. The declared cam opens over2645–2695 mm and holds through4000 mm. F10 uses372 finite belts,2.5 m powered travel and a3400 mm guide exit plane;its attached430 mm shoe/payload clears when its aft reference reaches that plane.\n\n'
    report+='The 84 moving magnet blocks retain the source geometry and3.6288 kg computed mass. F10 adds1 kg allocated GFRP/aluminum support,fasteners,retention and liners to each modified payload;all12 shoes are carried. This allocation is not a substantiated structural design or verified fit in the legacy storage/feeder. R10 reuses the13.127806 kg carrier once. Old track/stator/support/cam masses are removed and replaced by explicitly dimensioned copper,rail,backbone,plate,crossmember and cam quantities in the mass ledgers. CAD-derived,computed-volume and allocated masses are identified.\n\n'
    for name in ['R10','F10']:
        d=load(name+'_DESIGN.json');m=load(name+'_MASS.json');L=d['inductance'][-1]['balanced_effective_inductance_eigenvalues_H']
        report+=f"**{name}:** device initial dry{m['device_initial_dry_kg']:.6f} kg;loaded initial host+device+48 kg payload{m['initial_combined_kg']:.6f} kg. Copper{sum(p['copper_volume_m3'] for p in d['phases'])*8960:.6f} kg;phase20°C resistances "+', '.join(f"{p['resistance20C_ohm']*1000:.3f}" for p in d['phases'])+f" mΩ. Refined balanced partial-element inductance{min(L)*1e6:.3f}–{max(L)*1e6:.3f} µH. Source32S{m['source_bank']['parallel']}P,{m['source_bank']['cells']} original Eaton reference cells,{m['source_bank']['bare_cell_mass_kg']:.2f} kg bare.\n\n"
    report+='Charge remains86.4 V. The original600 A mean phase,92 A hot-device and200 V switch gates are unchanged. R10 adds parallel cells;it does not raise cell voltage or individual-device ratings. The same three-half-bridge/ten-parallel-device topology and original loss/parasitic assumptions are retained. Resistance comes from actual new finite conductor segment lengths/sections and temperature-dependent copper,with an explicit2 mΩ joint allowance. Balanced L is computed from the declared new phase paths at20/10 mm panels;it is a partial-element estimate,not full AC/FEM characterization.\n\n'
    report+='## What changed in physics and control\n\n'
    report+='Finite Lorentz integration uses the actual new belt positions,84 cuboids,active copper volumes and return geometry. No old k(x) is tiled or stretched,and no external actuator force fit is transferred. The primary return cross-section quadrature is1 point per transverse axis;the refined map uses3,plus additional0.05 m handoff/exit stations. Independently higher-order5×5×9 active/7-point return anchor checks are retained. Exact finite-source query caching identifies only equal physical coordinates (1 pm quantization);it does not impose periodic source fields.\n\n'
    report+='R10 includes finite host reaction,payload detachment at zero rear normal reaction,active current-limited arrest and magnetic energy. STOPPED is first low-speed turnaround,not powered return/reset. F10 carries payload and shoe together through a declared open guide and source-current decay,with explicit friction feed-forward for the passive exit coast. The controller uses allocated case friction;an actual friction estimator is not demonstrated. The adverse R1 speed miss is preserved. No R2 tuning or11–13 m/s upper-speed result is claimed.\n\n'
    report+='![R10 one-shot velocity](R10_VELOCITY.png)\n\n## Refinement and conservation\n\n'
    for r in comparisons:report+=f"{r['configuration']} {'adverse' if r['adverse'] else 'nominal'}: refined map departure{r['refined_release_m_s']:.6f} m/s,change{r['release_change_m_s']:+.7f} m/s;model gates{'pass' if r['refined_field_gates_pass'] else 'FAIL '+','.join(r['failed_refined_gates'])}.\n\n"
    report+=f"Four20→5 µs motion pairs and actual refined-field reruns are archived. Independent reduced-mass kinetic work+friction agrees with signed motor work to{checks['max_independent_mechanical_work_residual_J']:.3g} J;maximum complete electrical energy residual is{checks['max_total_energy_residual_J']:.4f} J. Source draw,all losses,remaining magnetic energy and failure gates are retained. Numerical agreement is not measured accuracy.\n\n"
    report+='## One-shot thermal and practical decision\n\n'
    for r in fine:report+=f"{r['configuration']} {'adverse' if r['adverse'] else 'nominal'}: copper adiabatic rise{r['thermal']['winding_adiabatic_rise_C']:.4f} K from its allocated50/100°C initial state;inverter loss{r['thermal']['inverter_loss_J']:.2f} J;bank ESR rise spans"+', '.join(f'{v:.4f}' for v in r['thermal']['bank_ESR_adiabatic_rise_for_cp700to1200_C'])+' K for the explicitly assumed700–1200 J/kg/K cell heat capacity.\n\n'
    report+='The winding loss heats its computed copper mass and feeds resistance back during the shot. Cell heat capacity is an assumption,not catalog data. Inverter transient junction temperature,actual case/sink temperatures,insulation/material limits,skin/proximity/eddy losses,repeated duty and TVAC acceptance remain unresolved. The small calculated bulk rises do not qualify the circuit.\n\n![Net source energy](SHOT_ENERGY.png)\n\nR10 is the stronger present computational candidate:it passes the enumerated10 m/s model gates with the longer arrest and larger bank. F10 reduces one-shot energy but carries12 attached adapters and requires new payload/storage/exit/abort interfaces;its adverse R1 speed miss remains outside the original±0.005 m/s gate. Neither case closes new CAD clearances,structural strength,fault containment,EMC,payload magnetic compatibility,return/reset,or physical/source qualification.\n\n'
    report+='![Declared cross-section](MAGNETIC_SECTION.png)\n\n## Reproduce\n\nRun `build_design.py` with Magpylib5.2.3/NumPy2.4.6;`configure_mass.py`;`run_cases.py`;`refine_maps.py`;`finish_report.py`;then `check_capture.py`. The refinement uses two CPU processes. The neutral SVGs retain editable text;PDF uses Type42 fonts. `provenance/` contains byte-identical original sources and inputs;`COUPLED_SOURCE_CHANGE.diff` exposes the new integration. All paths resolve relative to this folder. No third-party binary or PDF is redistributed.\n'
    (H/'README.md').write_text(report)
    print('PASS:actual primary and refined-field coupledcases,standalone one-messagefigures,thermal/loss/energy ledgers and report.',flush=True)
if __name__=='__main__':main()
