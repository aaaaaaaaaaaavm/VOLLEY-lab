"""Read-only source,geometry,circuit/motion conservation and refinement check;no Magpylib required."""
from pathlib import Path
import cmath,csv,hashlib,json,math
H=Path(__file__).resolve().parent
def load(n):return json.loads((H/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=load('MANIFEST.json')
    for n,r in manifest['files'].items():
        p=H/n;assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],n
    for r in load('SOURCE_PINS.json')['sources']:assert sha(H/r['capture_path'])==r['sha256']
    primary=load('COUPLED_RESULTS.json');refined=load('REFINED_COUPLED_RESULTS.json');rows=primary['cases']+refined['cases']
    assert primary['model_sha256']==sha(H/'coupled_design.py')==sha(H/'provenance/coupled_design_R1.py')
    assert len(primary['cases'])==8 and len(refined['cases'])==4
    for name,belts,rail in [('R10',534,4750),('F10',372,3400)]:
        d=load(name+'_DESIGN.json');m=load(name+'_MASS.json');f=load(name+'_REFINED_FIELD.json')
        p=d['parameters'];l=p['launch']
        assert p['magnetic']['stator_belts']==belts and l['powered_travel']==2500 and l['rail_length']==rail
        assert l['home_aft_x']==200 and l['drive_end_aft_x']==2700
        if name=='R10':assert l['release_aft_x']==2700 and l['arrest_aft_x']==4000 and l['cam_ramp_aft_x_mm']==[2645,2695] and l['cam_hold_through_aft_x_mm']==4000
        else:assert l['release_aft_x'] is None and l['full_free_exit_aft_x']==3400 and l['brake_travel']==0
        assert math.isclose(sum(r['kg'] for r in m['components']),m['device_initial_dry_kg'],abs_tol=1e-9)
        assert math.isclose(500+m['device_initial_dry_kg']+48,m['initial_combined_kg'],abs_tol=1e-9)
        assert math.isclose(m['first_shot_rest_host_kg']+m['moving_carrier_or_shoe_kg']+4,m['initial_combined_kg'],abs_tol=1e-9)
        assert m['source_bank']['cells']==(192 if name=='R10' else 64) and m['source_bank']['initial_V']==86.4
        for r in d['finite_field_stations']+f['stations']:
            coeff=[a+b for a,b in zip(r['active_phase_coeff_N_per_A'],r['return_phase_coeff_N_per_A'])]
            amp=abs(sum(c*cmath.exp(1j*phase) for c,phase in zip(coeff,[0,-2*math.pi/3,2*math.pi/3])))
            assert math.isclose(amp,r['N_per_peak_A'],rel_tol=1e-10,abs_tol=1e-12)
        for r in [r for r in rows if r['configuration']==d['configuration']]:
            assert r['all_model_gates_pass']==all(r['checks'].values())
            assert r['checks']['speed']==(abs(r['release']['relative_speed_m_s']-10)<=.005)
            C=m['source_bank']['adverse_F' if r['adverse'] else 'nominal_F']
            assert math.isclose(.5*C*(86.4**2-r['final_bank_V']**2),r['source_draw_J'],abs_tol=1e-8)
            residual=r['source_draw_J']-sum(r['energy_ledger'].values())-r['magnetic_energy_end_J']
            assert math.isclose(residual,r['total_energy_residual_J'],abs_tol=1e-9)
            assert abs(r['independent_mechanical_residual_J'])<1e-6
            assert r['peak_phase_current_A']<=600.1 and r['peak_hot_device_current_A']<=92 and r['peak_switch_V']<200 and r['peak_cell_V']<3
            assert not r['return_reset_simulated'] and not r['manufacturing_or_full_feeder_acceptance']
            if name=='R10':assert r['status']=='STOPPED' and r['final_position_m']<=3.8 and 200+r['release']['position_m']*1000>=2695 and r['all_model_gates_pass']
            elif r['adverse']:assert r['status']=='FREE_EXIT' and not r['checks']['speed'] and not r['all_model_gates_pass']
            else:assert r['status']=='FREE_EXIT' and r['all_model_gates_pass']
    check=load('NUMERICAL_CHECKS.json')
    assert all(r['same_gate_result'] for r in check['timestep_comparisons'])
    assert all(r['primary_gates_pass']==r['refined_field_gates_pass'] for r in check['field_comparisons'])
    for p in H.glob('*.svg'):assert '<text' in p.read_text() and all(not l.endswith((' ','\t')) for l in p.read_text().splitlines())
    for p in H.glob('*.csv'):assert b'\r\n' not in p.read_bytes()
    fig=load('FIGURE_SOURCE_INVENTORY.json')
    for n,h in fig['outputs'].items():assert sha(H/n)==h
    print('PASS:12 actual circuit/motion cases,clean derived geometry,new534/372belt finite maps,R/L/mass/source ledgers,independent energy work,timestep/field gate stability,editable SVG andLF CSV. R10bothpass;F10adverse speed miss preserved;no physical/full-cycle qualification.')
if __name__=='__main__':main()
