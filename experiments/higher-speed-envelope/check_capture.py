"""Read-only verification of source identity,rejected trajectories,bounds and refinement."""
from pathlib import Path
import hashlib,importlib.util,json,math,sys
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=load(H/'MANIFEST.json')
    for name,m in manifest['files'].items():
        p=H/name;assert p.stat().st_size==m['bytes'] and sha(p)==m['sha256'],name
    pins=load(H/'SOURCE_IDENTITIES.json')
    assert not pins['source_code_changed']
    for r in pins['sources']:assert sha(H/r['capture_path'])==r['sha256'],r['capture_path']
    source=H/'capture/analysis/coupled_shot.py'
    spec=importlib.util.spec_from_file_location('captured_model_check',source);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    sled,dry,xs,ks,R,inputs=model.inputs();results=load(H/'HIGH_TARGET_RESULTS.json')
    assert results['source_sha256']==sha(source) and results['input_sha256']==inputs
    assert len(results['cases'])==22 and not results['source_ratings_modified']
    for r in results['cases']:
        raw=load(H/'cases'/(r['case_id']+'.json'))
        assert all(raw[k]==v for k,v in r.items())
        assert r['status']=='ARREST_STROKE_EXCEEDED' and not r['all_declared_checks_pass']
        assert not r['checks']['stopped_inside_210mm'] and not r['checks']['release_speed']
        assert r['stop_position_m']>1.511 and r['stop_velocity_m_s']>0
        assert r['target_m_s'] in [10,15,30,50,100]
    check=load(H/'INVARIANT_AND_REFINEMENT_CHECKS.json')
    assert check['passed'] and len(check['refinements'])==4
    assert max(abs(r['independent_mechanical_work_residual_J']) for r in check['invariants'])<1e-6
    assert all(r['same_rejection_status'] for r in check['refinements'])
    assert max(abs(r['release_speed_change_m_s']) for r in check['refinements'])<.001
    b=load(H/'BUDGET_BOUNDS.json')
    assert math.isclose(b['accelerated_mass_kg'],sled+4,abs_tol=1e-12)
    assert math.isclose(b['nominal_usable_bank_energy_86p4_to60V_J'],.5*6.25*(86.4**2-60**2),abs_tol=1e-9)
    assert b['optimistic_arrest_speed_ceiling_at600A_no_losses_m_s']<10
    shoes=load(H/'HYPOTHETICAL_FLYAWAY_SHOES.json')
    assert shoes['current_moving_magnet_count']==84 and math.isclose(shoes['current_CAD_moving_magnet_mass_kg'],3.6288,abs_tol=1e-10)
    assert len(shoes['rows'])==20
    for r in shoes['rows']:
        assert math.isclose(r['same_available_work_mass_only_speed_ratio'],math.sqrt((sled+4)/(r['assumed_adapter_kg']+4)),rel_tol=1e-12)
        assert r['total_adapter_inventory_kg']==12*r['assumed_adapter_kg']
        assert not r['shoe_mass_substantiated'] and not r['current_force_map_transferred'] and not r['discarded_free_adapter_debris_assumed']
    baseline=load(H/'capture/analysis/COUPLED_SHOT.json')
    assert baseline['source_sha256']==sha(source)
    assert all(r['all_declared_checks_pass'] for r in baseline['cases'] if r['target_m_s'] in [1,2,3])
    print(f"PASS:{len(manifest['files'])} file identities;unchanged accepted source/maps;22 actual rejected cases;4 timestep refinements;independent work balance;20 hypothetical shoe bounds;current1/2/3 baseline preserved.")
if __name__=='__main__':main()
