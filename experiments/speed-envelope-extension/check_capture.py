"""Read-only captured-envelope check. Does not rerun models or write baseline files."""
from pathlib import Path
import csv,hashlib,importlib.util,json,math,sys
H=Path(__file__).resolve().parent;C=H.parent/'higher-speed-envelope/capture'
sys.dont_write_bytecode=True
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvrows(name):return list(csv.DictReader((H/name).open()))
def main():
    manifest=load(H/'MANIFEST.json')
    for name,r in manifest['files'].items():
        p=H/name;assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],name
    pins=load(H/'SOURCE_PINS.json');source=C/'analysis/coupled_shot.py'
    assert sha(source)==pins['model_sha256']=='560088cb2a05e270b621700df4de1598cb209237b726bd5569e639c5a0f38155'
    assert sha(C/'analysis/COUPLED_SHOT.json')==pins['baseline_sha256']
    spec=importlib.util.spec_from_file_location('check_frozen_source',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert m.inputs()[-1]==pins['input_sha256']
    rs=load(H/'CASES.json')['cases'];s=load(H/'RESULTS.json');d=load(H/'SCAN_DEFINITION.json')
    assert len(rs)==s['records']==106 and s['accepted_reuses']==18 and s['new_unique_computations']==88
    assert len({(r['target_m_s'],r['adverse'],r['inductance_H'],r['dt_s']) for r in rs})==len(rs)
    baseline=load(C/'analysis/COUPLED_SHOT.json')['cases']
    for r in rs:
        assert r['all_declared_checks_pass']==all(r['checks'].values())
        assert r['modeled_launch_arrest_gates_pass']==r['all_declared_checks_pass']
        assert not r['powered_return_reset_simulated'] and not r['full_exit_clearance_verified'] and r['operational_low_speed_floor_m_s'] is None
        if r['reused_accepted_capture']:
            old=next(x for x in baseline if x['target_m_s']==r['target_m_s'] and x['adverse']==r['adverse'] and x['inductance_H']==r['inductance_H'] and x['dt_s']==r['dt_s'])
            assert all(r[k]==v for k,v in old.items() if k!='trace')
    for a in [False,True]:
        for v in d['coarse_command_points_m_s']:
            assert any(r['target_m_s']==v and r['adverse']==a and r['inductance_H']==20e-6 and r['dt_s']==20e-6 for r in rs)
    assert s['dt_refinements']==17 and all(r['same_gate_result'] for r in load(H/'NUMERICAL_CHECKS.json')['refinements'])
    assert s['max_independent_motor_work_residual_J']<1e-6
    assert s['max_refined_release_speed_change_m_s']<.0001
    assert len(s['trace_files'])==2 and len(list(H.glob('*_trace.csv')))==2
    assert s['operational_lower_floor_m_s'] is None and not s['full_clearance_feeder_interlock_or_return_reset_proved']
    for row in s['upper_brackets']:
        assert math.isclose(row['next_sampled_fail_m_s']-row['last_sampled_pass_m_s'],.05,abs_tol=1e-9)
        L=row['L_uH']*1e-6
        for v,passed in [(row['last_sampled_pass_m_s'],True),(row['next_sampled_fail_m_s'],False)]:
            r=next(x for x in rs if x['target_m_s']==v and x['adverse']==row['adverse'] and math.isclose(x['inductance_H'],L,abs_tol=1e-14) and x['dt_s']==5e-6)
            assert r['all_declared_checks_pass']==passed
    for point in s['common_upper_confirmations']:
        for L in [3e-6,20e-6,100e-6]:
            assert next(r for r in rs if r['target_m_s']==point['common_sampled_upper_command_m_s'] and r['adverse']==point['adverse'] and r['inductance_H']==L and r['dt_s']==5e-6)['all_declared_checks_pass']
    mass=csvrows('MASS_INVENTORY.csv')
    for r in mass:
        expected=500+float(r['common_nonmoving_device_allocation_kg'])+48+int(r['adapter_inventory_count'])*float(r['adapter_kg'])
        assert math.isclose(expected,float(r['initial12payload_total_kg']),abs_tol=1e-9)
        assert r['manufactured_mass_measured']=='False'
    assert len(csvrows('GEOMETRY_REQUIREMENTS.csv'))==80 and len(csvrows('RANKED_REQUIREMENTS.csv'))==60
    assert load(H/'NEXT_COUPLED_CANDIDATES.json')['neither_completed']
    assert all(r['status'].startswith('pending') for r in load(H/'NEXT_COUPLED_CANDIDATES.json')['candidates'])
    inventory=load(H/'FIGURE_SOURCE_INVENTORY.json')
    assert sha(H/inventory['generator'])==inventory['generator_sha256']
    for name,digest in inventory['outputs'].items():assert sha(H/name)==digest
    for name,digest in inventory.get('additional_generators',{}).items():assert sha(H/name)==digest
    for name in ['SAMPLED_ENVELOPE.svg','GEOMETRY_AND_INVENTORY.svg','ENVELOPE_HERO.svg']:
        assert all(not line.endswith((' ','\t')) for line in (H/name).read_text().splitlines()),name
    hero=load(H/'HERO_DATA.json');assert hero['no_resimulation']
    assert hero['results_sha256']==sha(H/'RESULTS.json')
    assert [(r['last_common_sampled_pass_m_s'],r['next_limiting_sampled_fail_m_s']) for r in hero['rows']]==[(4.6,4.65),(3.7,3.75)]
    assert sha(source)==pins['model_sha256'] and m.inputs()[-1]==pins['input_sha256']
    print('PASS:106 unique records,18 accepted reuses,17 stable timestep refinements,six0.05m/s upper brackets,exact common upper points at all3 inductances,two traces,unchanged source/input pins,80geometry/60ranking requirements,two coupled candidates pending. Operational lower floor/reset/clearance unverified.')
if __name__=='__main__':main()
