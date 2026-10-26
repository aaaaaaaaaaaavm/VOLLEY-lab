"""Single-process bounded higher-target screen of unchanged ACR1 equations/inputs."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('frozen_shot',H/'capture/analysis/coupled_shot.py')
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
def main():
    sled,dry,xs,ks,R,pins=model.inputs();rows=[]
    jobs=[(v,a,20e-6,20e-6) for v in [10,15,30,50,100] for a in [False,True]]
    jobs += [(v,a,L,20e-6) for v in [10,15] for a in [False,True] for L in [3e-6,100e-6]]
    jobs += [(v,a,20e-6,5e-6) for v in [10,15] for a in [False,True]]
    out=H/'cases';out.mkdir(exist_ok=True)
    for v,adverse,L,dt in jobs:
        start=time.monotonic()
        r=model.simulate(v,sled,dry,xs,ks,R,adverse=adverse,L=L,dt=dt,trace=L==20e-6 and dt==5e-6)
        ident=f"u{v}_{'adverse' if adverse else 'nominal'}_L{L*1e6:g}uH_dt{dt*1e6:g}us"
        r['case_id']=ident;r['solver_elapsed_s']=time.monotonic()-start
        (out/(ident+'.json')).write_text(json.dumps(r,indent=2)+'\n')
        rows.append({k:val for k,val in r.items() if k!='trace'})
        print(json.dumps({k:r[k] for k in ['case_id','status','all_declared_checks_pass','stop_position_m','peak_phase_current_A','solver_elapsed_s']}),flush=True)
    result=dict(study='HV-ACR1-REJECTION-SCREEN-01',configuration='Unchanged VOLLEY-G5-ACR1, evaluated outside published supported commands for rejection assessment only',
        source_sha256=hashlib.sha256((H/'capture/analysis/coupled_shot.py').read_bytes()).hexdigest(),input_sha256=pins,
        sled_mass_kg=sled,payload_kg=4,dry_CAD_kg=dry,
        cases=rows,current_supported_command_points_m_s=[1,2,3],source_ratings_modified=False,
        limitations=['Average dq/source model only; not transistor-resolved switching or measured hardware.',
          'Failure at higher target is not a new achieved speed/rating.',
          'Finite-field coefficients are reused within unchanged1.3m drive/210mm arrest geometry; no long-rail force field is simulated.'])
    (H/'HIGH_TARGET_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Completed22actualunchanged-modelcases',flush=True)
if __name__=='__main__':main()
