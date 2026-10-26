"""Actual one-shot computations of new R10/F10 finite-field designs."""
from pathlib import Path
import hashlib,json,sys
from coupled_design import simulate
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def main():
    rows=[]
    for name in ['R10','F10']:
        d=json.loads((H/(name+'_DESIGN.json')).read_text());mass=json.loads((H/(name+'_MASS.json')).read_text())
        for adverse in [False,True]:
            for dt in [20e-6,5e-6]:
                r=simulate(d,mass,adverse,dt);trace=r.pop('trace')
                r['id']=f"{name}_{'adverse' if adverse else 'nominal'}_dt{dt*1e6:g}us";rows.append(r)
                if dt==5e-6:
                    with (H/(r['id']+'_history.csv')).open('w') as f:
                        f.write('t_s,x_m,relative_v_m_s,phase_current_A,bank_V\n')
                        for line in trace:f.write(','.join(str(v) for v in line)+'\n')
                print(r['id'],r['status'],r['all_model_gates_pass'],r['release'],r['checks'],flush=True)
    (H/'COUPLED_RESULTS.json').write_text(json.dumps(dict(study='TEN-METRE-PER-SECOND-DESIGNS-R1',model_sha256=hashlib.sha256((H/'coupled_design.py').read_bytes()).hexdigest(),
        cases=rows,scope='Mean-dq source/finite-host one-shot design computations;not full mechanism/return/hardware acceptance.'),indent=2)+'\n')
if __name__=='__main__':main()
