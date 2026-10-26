"""New finite winding designs and geometry-derived R/L estimates; no old force-map scaling."""
from pathlib import Path
import copy,hashlib,importlib.util,json,math,sys,time
import numpy as np
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,H/'provenance'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
F=module('original_finite_field','finite_motor.py');IND=module('original_partial_L','winding_inductance.py')
def dump(name,x):(H/name).write_text(json.dumps(x,indent=2)+'\n')
class ChunkedField:
    def __init__(self,field):self.field=field
    def getB(self,points):
        a=np.asarray(points);return np.concatenate([self.field.getB(a[i:i+768]) for i in range(0,len(a),768)])
def paths(p,end_x):
    # Original physical series-path topology, with explicit new terminal-bus position.
    m=p['magnetic'];out=[]
    for phase,offset,gap in [('A',0,-.0035),('B',2,.0035),('C',1,0)]:
        ix=list(range(offset,m['stator_belts'],3));nodes=[];areas=[]
        def append(q,area):
            if nodes and np.linalg.norm(np.array(q)-nodes[-1])<1e-12:return
            if nodes:areas.append(area)
            nodes.append(np.array(q,float))
        first=(m['stator_x_start']+8*ix[0]+3.5)/1000;sign=-1 if phase=='C' else 1
        startdepth=-sign*.045;route=-.075 if startdepth<0 else .115
        for q in [(.15,0,.14),(.15,gap,.14),(.15,gap,route),(first,gap,route),(first,gap,startdepth),(first,0,startdepth)]:append(q,21e-6)
        for j,i in enumerate(ix):
            s=sign*(1 if j%2==0 else -1);x=(m['stator_x_start']+8*i+3.5)/1000
            append((x,0,s*.045),42e-6)
            if j==len(ix)-1:break
            xn=(m['stator_x_start']+8*ix[j+1]+3.5)/1000
            for q in [(x,0,s*.0525),(x,gap,s*.0525),(x,gap,s*.0675),(xn,gap,s*.0675),(xn,gap,s*.0525),(xn,0,s*.0525),(xn,0,s*.045)]:append(q,21e-6)
        end=nodes[-1];route=-.075 if end[2]<0 else .115
        for q in [(end[0],gap,end[2]),(end[0],gap,route),(end_x,gap,route),(end_x,gap,.14),(end_x,0,.14)]:append(q,21e-6)
        out.append((phase,nodes,areas))
    return out
def evaluate(field,p,x,refined=False):
    active=F.active_coefficients(field,p,float(x),(5,5,9) if refined else (3,3,5))
    returns=F.return_coefficients(field,p,float(x),7 if refined else 5,3 if refined else 1)
    c=active+returns
    return dict(displacement_m=float(x),N_per_peak_A=F.amplitude(c),active_phase_coeff_N_per_A=active.tolist(),return_phase_coeff_N_per_A=returns.tolist())
def main():
    base=json.loads((H/'provenance/PARAMETERS.json').read_text());home=json.loads((H/'provenance/VOLLEY_G5_ACR1_home.json').read_text())
    sled=sum(r['mass_kg'] for r in home['BOM'] if r['subsystem'].startswith('sled'))
    field=ChunkedField(F.make_field(base));results=[]
    for name,n,end,stop,moving in [('R10',534,4.75,3.8,sled),('F10',372,3.4,3.2,4.6288)]:
        p=copy.deepcopy(base);p['configuration_id']=name+'-R1';p['magnetic']['stator_belts']=n
        p['magnetic']['stator_pitch_span']=n*8;p['launch']['powered_travel']=2500;p['launch']['brake_travel']=1300 if name=='R10' else 0
        curves=paths(p,end);wire=[]
        for phase,nodes,areas in curves:
            lengths=[float(np.linalg.norm(b-a)) for a,b in zip(nodes,nodes[1:])]
            wire.append(dict(phase=phase,resistance20C_ohm=sum(1.7e-8*l/A for l,A in zip(lengths,areas)),
                copper_volume_m3=sum(l*A for l,A in zip(lengths,areas)),path_length_m=sum(lengths),
                nodes_m=[q.tolist() for q in nodes],cross_sections_m2=areas))
        # Partial-element matrix and refinement from actual new finite conductor paths.
        induct=[IND.inductance(curves,.02),IND.inductance(curves,.01)]
        rows=[];began=time.monotonic()
        for x in sorted(set(np.round(np.arange(0,stop+.0001,.1),8).tolist()+[2.5,stop])):
            rows.append(evaluate(field,p,x));print(name,'field',x,rows[-1]['N_per_peak_A'],flush=True)
        refinement=[]
        for x in [0.,1.25,2.5,stop]:
            coarse=evaluate(field,p,x);fine=evaluate(field,p,x,True)
            refinement.append(dict(x_m=x,coarse_N_A=coarse['N_per_peak_A'],fine_N_A=fine['N_per_peak_A'],relative_change=abs(fine['N_per_peak_A']-coarse['N_per_peak_A'])/max(fine['N_per_peak_A'],1e-9)))
        launch=dict(home_aft_x=200,powered_travel=2500,drive_end_aft_x=2700,
            brake_travel=1300 if name=='R10' else 0,rail_length=end*1000,
            release_aft_x=2700 if name=='R10' else None,arrest_aft_x=4000 if name=='R10' else None,
            full_free_exit_aft_x=3400 if name=='F10' else None,
            cam_ramp_aft_x_mm=[2645,2695] if name=='R10' else None,cam_hold_through_aft_x_mm=4000 if name=='R10' else None)
        clean=dict(configuration_id=name+'-R1',units='mm',magnetic=p['magnetic'],launch=launch,
            schema_scope='New finite motor/guide coordinates only;not a copied old assembly or approved manufacturing model.')
        result=dict(configuration=name+'-R1',parameters=clean,drive_m=2.5,arrest_m=1.3 if name=='R10' else None,
            free_exit_global_guide_end_m=end if name=='F10' else None,full_exit_displacement_m=stop if name=='F10' else None,
            moving_carrier_or_shoe_kg=moving,payload_kg=4,source_bank=dict(series=32,parallel=6,cells=192,initial_V=86.4,
                nominal_F=18.75,nominal_ESR_ohm=.058666666666666666,adverse_F=11.8125,adverse_ESR_ohm=.11733333333333333,bare_cell_mass_kg=3.84),
            phases=wire,inductance=induct,finite_field_stations=rows,field_refinement=refinement,field_wall_seconds=time.monotonic()-began,
            scope='Actual new finite belt counts, conductor returns and terminal routing evaluated with analytic cuboid source;no previous k-map scaled/tiled. No hardware/AC-field validation.',
            current_limit_A=600,MOSFET_Vds_limit_V=200,current_per_hot_device_gate_A=92,
            field_chunking='Exact input partition into768point chunks to bound memory;no spatial cutoff.',
            L_estimate_scope='Regularized partial-element matrix of actual new conductor centrelines;not AC eddy-current validation.')
        dump(name+'_DESIGN.json',result);results.append(name)
    dump('DESIGN_INDEX.json',dict(configurations=results,source_field_generator_sha256=hashlib.sha256((H/'provenance/finite_motor.py').read_bytes()).hexdigest()))
if __name__=='__main__':main()
