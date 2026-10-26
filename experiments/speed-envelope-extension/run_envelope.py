"""Portable sampled launch/arrest envelope of unchanged pinned ACR1 equations.

Reads the sibling higher-speed-envelope capture; writes only this new folder.
STOPPED means first low-speed turnaround, never full reset/clearance acceptance.
"""
from pathlib import Path
import hashlib,importlib.util,json,math,sys,time
import numpy as np
H=Path(__file__).resolve().parent
CAPTURE=H.parent/'higher-speed-envelope/capture'
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,x):(H/name).write_text(json.dumps(x,indent=2)+'\n')
def main():
    source=CAPTURE/'analysis/coupled_shot.py';before=sha(source)
    assert before=='560088cb2a05e270b621700df4de1598cb209237b726bd5569e639c5a0f38155'
    spec=importlib.util.spec_from_file_location('frozen_envelope_source',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    sled,dry,xs,ks,R,pins=m.inputs()
    baseline=json.loads((CAPTURE/'analysis/COUPLED_SHOT.json').read_text())
    assert baseline['source_sha256']==before and baseline['inputs_sha256']==pins
    dump('SOURCE_PINS.json',dict(model_relative_path='../higher-speed-envelope/capture/analysis/coupled_shot.py',
        model_sha256=before,baseline_relative_path='../higher-speed-envelope/capture/analysis/COUPLED_SHOT.json',
        baseline_sha256=sha(CAPTURE/'analysis/COUPLED_SHOT.json'),input_sha256=pins,
        source_changed=False,runner_changes='Target/inductance/timestep arguments only; no source limits or controller optimization.'))
    rows=json.loads((H/'CASES.json').read_text())['cases'] if (H/'CASES.json').exists() else []
    def get(v,adverse,L=20e-6,dt=20e-6,stage='coarse',trace=False):
        v=round(float(v),8)
        prior=next((r for r in rows if r['target_m_s']==v and r['adverse']==adverse and r['inductance_H']==L and r['dt_s']==dt),None)
        if prior:return prior
        reused=next((r for r in baseline['cases'] if abs(r['target_m_s']-v)<1e-10 and r['adverse']==adverse and r['inductance_H']==L and r['dt_s']==dt),None)
        began=time.monotonic()
        raw=dict(reused) if reused is not None and not trace else m.simulate(v,sled,dry,xs,ks,R,adverse=adverse,L=L,dt=dt,trace=trace)
        records=raw.pop('trace',[])
        if not trace:records=[]
        ident=f"u{v:g}_{'adverse' if adverse else 'nominal'}_L{L*1e6:g}uH_dt{dt*1e6:g}us"
        raw.update(case_id=ident,stage=stage,reused_accepted_capture=reused is not None and not trace,
            exit_only_speed_gate_pass=raw['checks']['release_speed'],modeled_launch_arrest_gates_pass=raw['all_declared_checks_pass'],
            powered_return_reset_simulated=False,full_exit_clearance_verified=False,operational_low_speed_floor_m_s=None,
            elapsed_computation_s=time.monotonic()-began)
        if records:
            tracepath=H/(ident+'_trace.csv')
            with tracepath.open('w') as f:
                f.write('t_s,x_m,relative_v_m_s,phase_current_A,cap_V,terminal_V,bank_A,phase\n')
                for record in records:f.write(','.join(str(x) for x in record)+'\n')
            raw['trace_file']=tracepath.name
        rows.append(raw)
        dump('CASES.json',dict(study='ACR1-SAMPLED-LAUNCH-ARREST-ENVELOPE-01',cases=rows))
        print(json.dumps(dict(case=ident,stage=stage,status=raw['status'],gates=raw['all_declared_checks_pass'],
            actual_release_m_s=None if raw['release'] is None else raw['release']['relative_speed_m_s'],elapsed_s=raw['elapsed_computation_s'])),flush=True)
        return raw
    coarse=sorted(set([round(x,8) for x in np.arange(.1,4.70001,.25)]+[1.,2.,3.,4.7]))
    for adverse in [False,True]:
        for v in coarse:get(v,adverse)
    transitions=[]
    for adverse in [False,True]:
        rr=[get(v,adverse) for v in coarse]
        for a,b in zip(rr,rr[1:]):
            if a['all_declared_checks_pass']!=b['all_declared_checks_pass']:
                transitions.append(dict(adverse=adverse,left=a['target_m_s'],right=b['target_m_s']))
                for v in np.arange(math.ceil(a['target_m_s']/.05-1e-9)*.05,b['target_m_s']+.00001,.05):
                    get(v,adverse,stage='edge_0p05')
    decisions=[]
    for adverse in [False,True]:
        rr=sorted([r for r in rows if r['adverse']==adverse and r['inductance_H']==20e-6 and r['dt_s']==20e-6],key=lambda r:r['target_m_s'])
        passes=[r for r in rr if r['all_declared_checks_pass']]
        if not passes:continue
        low,high=passes[0],passes[-1]
        brackets=[]
        lower=[r for r in rr if r['target_m_s']<low['target_m_s']]
        upper=[r for r in rr if r['target_m_s']>high['target_m_s']]
        if lower:brackets += [lower[-1]['target_m_s'],low['target_m_s']]
        if upper:brackets += [high['target_m_s'],upper[0]['target_m_s']]
        for v in sorted(set(brackets)):
            refined=get(v,adverse,dt=5e-6,stage='decisive_dt5',trace=v==high['target_m_s'])
            decisions.append(dict(adverse=adverse,target_m_s=v,fine_case=refined['case_id']))
        # Two upper passing-edge histories only; avoid long low-speed trace files.
        existing=next((r for r in rows if r['target_m_s']==high['target_m_s'] and r['adverse']==adverse and r['inductance_H']==20e-6 and r['dt_s']==5e-6),None)
        if existing and 'trace_file' not in existing:
            traced=m.simulate(high['target_m_s'],sled,dry,xs,ks,R,adverse=adverse,L=20e-6,dt=5e-6,trace=True)
            tracepath=H/(existing['case_id']+'_trace.csv')
            with tracepath.open('w') as f:
                f.write('t_s,x_m,relative_v_m_s,phase_current_A,cap_V,terminal_V,bank_A,phase\n')
                for record in traced['trace']:f.write(','.join(str(x) for x in record)+'\n')
            assert traced['checks']==existing['checks']
            existing['trace_file']=tracepath.name
        for L in [3e-6,100e-6]:
            for v in sorted(set([1.,2.,3.,high['target_m_s']]+([upper[0]['target_m_s']] if upper else []))):
                get(v,adverse,L=L,stage='inductance_sensitivity')
            tested=sorted([r for r in rows if r['adverse']==adverse and r['inductance_H']==L and r['dt_s']==20e-6],key=lambda r:r['target_m_s'])
            good=max(r['target_m_s'] for r in tested if r['all_declared_checks_pass'])
            bads=[r['target_m_s'] for r in tested if not r['all_declared_checks_pass'] and r['target_m_s']>good]
            if bads:
                bad=min(bads)
                while bad-good>.050001:
                    mid=round(round((good+bad)/2/.05)*.05,8)
                    if mid<=good:mid=round(good+.05,8)
                    if mid>=bad:break
                    row=get(mid,adverse,L=L,stage='inductance_upper_edge_0p05')
                    if row['all_declared_checks_pass']:good=mid
                    else:bad=mid
                for v in [good,bad]:
                    refined=get(v,adverse,L=L,dt=5e-6,stage='inductance_decisive_dt5')
                    decisions.append(dict(adverse=adverse,target_m_s=v,inductance_H=L,fine_case=refined['case_id']))
    # Confirm the exact common upper point across all three inductances at5µs.
    common=[]
    for adverse in [False,True]:
        high=min(max(r['target_m_s'] for r in rows if r['adverse']==adverse and r['inductance_H']==L and r['dt_s']==20e-6 and r['all_declared_checks_pass']) for L in [3e-6,20e-6,100e-6])
        for L in [3e-6,20e-6,100e-6]:
            get(high,adverse,L=L,stage='exact_common_upper_reference')
            fine=get(high,adverse,L=L,dt=5e-6,stage='exact_common_upper_dt5')
            assert fine['all_declared_checks_pass']
        common.append(dict(adverse=adverse,common_sampled_upper_command_m_s=high,all3_inductances_pass_at5us=True))
    dump('CASES.json',dict(study='ACR1-SAMPLED-LAUNCH-ARREST-ENVELOPE-01',cases=rows))
    dump('SCAN_DEFINITION.json',dict(coarse_command_points_m_s=coarse,coarse_dt_s=20e-6,nominal_adverse=True,
        coarse_inductance_H=20e-6,edge_spacing_m_s=.05,transitions=transitions,decisive_refinements=decisions,
        source_limits_changed=False,kinetic_model_only=True,lower_operational_floor_m_s=None,common_upper_confirmations=common,
        note='Passing sampled launch/arrest gates is not contact/clearance/interlock or powered return/reset acceptance.'))
    assert sha(source)==before and m.inputs()[-1]==pins
    print('COMPLETE',len(rows),'unique cached/reused/actual case records; source immutable.',flush=True)
if __name__=='__main__':main()
