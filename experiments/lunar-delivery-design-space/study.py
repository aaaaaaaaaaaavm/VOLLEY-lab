"""Analytical patched-conic resource screen; no optimized transfer/flight claim."""
from pathlib import Path
import math,json,csv
P=Path(__file__).parent
MU_E=398600.4418; MU_M=4902.800066; RE=6378.137; RM=1737.4; D=384400.; G=9.80665

def calculate():
 r=RE+500;rp=RM+100;a=(r+D)/2
 vc=math.sqrt(MU_E/r);vp=math.sqrt(MU_E*(2/r-1/a));va=math.sqrt(MU_E*(2/D-1/a));vm=math.sqrt(MU_E/D)
 dv=(vp-vc)*1000;vinf=(vm-va)*1000;capture=(math.sqrt((vinf/1000)**2+2*MU_M/rp)-math.sqrt(MU_M/rp))*1000
 sled=13.127805767;payload=4.;host=500+149.55671970039353+7+44-sled
 alpha=host/(host+payload+sled);u=dv/alpha;mu=(payload+sled)*alpha
 rows=[]
 for speed in [1,3,10,15,30,50,100,1000,u]:
  kick=alpha*speed
  rows.append(dict(relative_exit_m_s=speed,payload_delta_v_m_s=kick,remaining_departure_burn_m_s=max(0,dv-kick),lunar_capture_burn_m_s=capture,ideal_relative_launch_work_J=.5*mu*speed**2,ideal_10g_drive_length_m=speed**2/(20*G),host_recoil_m_s=-(payload+sled)/(host+payload+sled)*speed))
 return dict(model='Coplanar tangential Earth two-body transfer and lunar patched-conic capture; ideal instantaneous burns',constants=dict(mu_earth_km3_s2=MU_E,mu_moon_km3_s2=MU_M,earth_equatorial_radius_km=RE,moon_reference_radius_km=RM,mean_distance_km=D),earth_parking_altitude_km=500,lunar_circular_altitude_km=100,departure_delta_v_m_s=dv,lunar_vinf_m_s=vinf,lunar_capture_delta_v_m_s=capture,transfer_time_days=math.pi*math.sqrt(a**3/MU_E)/86400,payload_only_departure_energy_J=.5*payload*dv**2,full_existing_sled_flyaway_relative_speed_required_m_s=u,reference_retained_host_kg=host,outbound_mass_kg=payload+sled,cases=rows,limitations=['Not a three-body trajectory, launch window, SSO plane-change solution or low-energy capture optimization.','No current rail is assumed capable of these requested speeds. Work and length are necessary ideal bounds.','Lunar capture is required in every row; no propulsion module mass, dry mass, supplier component or delivered capacity selected.','Full sled flyaway is a different payload interface and inventory, not the reusable Gen5 configuration.','Classical host propulsion and electromagnetic injection must ultimately be compared at matched installed hardware and delivered states.'])

def main():
 r=calculate();(P/'RESULTS.json').write_text(json.dumps(r,indent=2)+'\n')
 with (P/'CASES.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(r['cases'][0]),lineterminator="\n");w.writeheader();w.writerows(r['cases'])
 # Independent vis-viva energy checks and Keplerian endpoint integration.
 from scipy.integrate import solve_ivp
 rr=RE+500;aa=(rr+D)/2;vv=math.sqrt(MU_E*(2/rr-1/aa));T=math.pi*math.sqrt(aa**3/MU_E)
 def rhs(t,s):
  R=math.hypot(s[0],s[1]);return [s[2],s[3],-MU_E*s[0]/R**3,-MU_E*s[1]/R**3]
 y=solve_ivp(rhs,[0,T],[rr,0,0,vv],rtol=2e-12,atol=1e-10,method='DOP853').y[:,-1]
 e=abs(math.hypot(y[0],y[1])-D);assert e<.002
 checks=dict(integrator='SciPy DOP853',endpoint_radius_error_km=e,endpoint_speed_error_m_s=abs(math.hypot(y[2],y[3])-math.sqrt(MU_E*(2/D-1/aa)))*1000,scope='Independent numerical check of ideal Earth two-body leg only; not lunar encounter validation')
 (P/'CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({"svg.fonttype":"none","pdf.fonttype":42})
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
 fig,axs=plt.subplots(1,2,figsize=(10,4.2),layout='constrained')
 ss=[10,15,30,50,100,1000,r["full_existing_sled_flyaway_relative_speed_required_m_s"]]
 axs[0].loglog(ss,[s*s/(20*G) for s in ss],'-o',color='#146c80');axs[0].set(xlabel='Relative exit speed (m/s)',ylabel='Ideal powered travel at 10 g (m)',title='Stroke scales with speed squared')
 cs=r['cases'];axs[1].plot([c['relative_exit_m_s'] for c in cs],[c['remaining_departure_burn_m_s'] for c in cs],'-o',color='#146c80',label='Remaining Earth-departure burn');axs[1].axhline(r['lunar_capture_delta_v_m_s'],color='#a3642f',label='Separate ideal lunar capture');axs[1].set(xlabel='Relative exit speed (m/s)',ylabel='Propulsive velocity increment (m/s)',title='Arrival still needs capture');axs[1].legend(fontsize=8)
 fig.suptitle('Earth-to-lunar-orbit architecture bounds · 500 km to 100 km',fontsize=12)
 for ext in ['png','pdf','svg']:fig.savefig(P/('lunar_architecture_bounds.'+ext),dpi=180)
 svg=P/"lunar_architecture_bounds.svg";svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
 print(json.dumps({k:r[k] for k in ['departure_delta_v_m_s','lunar_capture_delta_v_m_s','transfer_time_days','full_existing_sled_flyaway_relative_speed_required_m_s']},indent=2))
if __name__=='__main__':main()
