"""Actual return-cross-section quadrature and critical-station refinement of new finite geometry."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,time
import numpy as np
from build_design import F,ChunkedField
H=Path(__file__).resolve().parent
class MemoizedField:
    """Cache identical finite-source query points,not force coefficients or periodic tiles."""
    def __init__(self,field):self.field=field;self.cache={}
    def getB(self,points):
        unique,inverse=np.unique(np.round(np.asarray(points),12),axis=0,return_inverse=True)
        keys=[tuple(p) for p in unique];missing=[i for i,k in enumerate(keys) if k not in self.cache]
        for start in range(0,len(missing),768):
            ix=missing[start:start+768];values=self.field.getB(unique[ix])
            for i,value in zip(ix,values):self.cache[keys[i]]=value
        return np.asarray([self.cache[k] for k in keys])[inverse]
def worker(name):
    d=json.loads((H/(name+'_DESIGN.json')).read_text());p=d['parameters'];field=MemoizedField(F.make_field(p))
    points=[r['displacement_m'] for r in d['finite_field_stations']]
    points += [1.25,2.45,2.55]+([3.75] if name=='R10' else [2.65,2.75,2.85,2.95,3.05,3.15])
    rows=[];start=time.monotonic()
    for x in sorted(set(points)):
        active=F.active_coefficients(field,p,x,(3,3,5));returns=F.return_coefficients(field,p,x,5,3)
        rows.append(dict(displacement_m=x,N_per_peak_A=F.amplitude(active+returns),active_phase_coeff_N_per_A=active.tolist(),return_phase_coeff_N_per_A=returns.tolist()))
        print(name,'refined',x,rows[-1]['N_per_peak_A'],flush=True)
    result=dict(configuration=d['configuration'],stations=rows,active_quadrature=[3,3,5],return_line_quadrature=5,return_cross_quadrature=3,
        station_refinement='Additional0.05m midpoint stations around drive/exit/arrest handoffs plus1.25m;unchanged0.1m interior grid.',
        independent_higher_order_anchors=d['field_refinement'],wall_seconds=time.monotonic()-start,
        same_geometry_as_primary=True,old_k_tiling_or_scaling=False,
        numerical_cache='Identical finite84magnet-source field query coordinates,rounded1e-12m;no period identification,no spatial cutoff,no force-map tiling.')
    (H/(name+'_REFINED_FIELD.json')).write_text(json.dumps(result,indent=2)+'\n');return name
def main():
    with ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(worker,['R10','F10']))
if __name__=='__main__':main()
