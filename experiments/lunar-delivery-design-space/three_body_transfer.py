"""Ideal coplanar circular-Moon transfer shooting; not epoch-specific ephemerides."""
from pathlib import Path
import math,json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
P=Path(__file__).parent; ME=398600.4418;MM=4902.800066;D=384400.;RE=6378.137;RM=1737.4;RP=RM+100;R0=RE+500;T=5*86400.;N=math.sqrt((ME+MM)/D**3)
def moon(t,phase):
 q=phase+N*t;return D*np.array([math.cos(q),math.sin(q)]),D*N*np.array([-math.sin(q),math.cos(q)])
def rhs(phase):
 def f(t,s):
  r=s[:2];m,_=moon(t,phase);d=m-r;a=-ME*r/np.linalg.norm(r)**3+MM*(d/np.linalg.norm(d)**3-m/D**3);return np.r_[s[2:],a]
 return f
def solve(phase,dv,method='DOP853',dense=False):return solve_ivp(rhs(phase),(0,T),[R0,0,0,math.sqrt(ME/R0)+dv],method=method,rtol=2e-11,atol=1e-10,dense_output=dense)
def objective(z):
 s=solve(*z).y[:,-1];m,v=moon(T,z[0]);r=s[:2]-m;u=s[2:]-v;return [(np.linalg.norm(r)-RP)/1000,np.dot(r,u)/np.linalg.norm(r)]
def main():
 # Multiple inexpensive geometry seeds; select converged positive-tangential arrival.
 candidates=[]
 for phase in [math.pi-N*T,math.pi-N*T-.02,math.pi-N*T+.02]:
  fit=least_squares(objective,[phase,3.06],bounds=([1.7,2.95],[2.3,3.3]),xtol=1e-10,ftol=1e-10,gtol=1e-10,max_nfev=70,diff_step=1e-5)
  if np.linalg.norm(objective(fit.x))<1e-5:candidates.append(fit.x)
 if not candidates:raise RuntimeError('No converged arrival; do not publish a successful encounter claim')
 phase,dv=min(candidates,key=lambda z:z[1]);sol=solve(phase,dv,dense=True);state=sol.y[:,-1];m,vm=moon(T,phase);r=state[:2]-m;v=state[2:]-vm;tangent=np.array([-r[1],r[0]])/np.linalg.norm(r)
 if np.dot(v,tangent)<0:tangent=-tangent
 impulse=math.sqrt(MM/RP)*tangent-v;captured=np.r_[state[:2],state[2:]+impulse]
 before_times=np.linspace(T-43200,T,21601);before_alt=[np.linalg.norm(sol.sol(t)[:2]-moon(t,phase)[0])-RM for t in before_times];assert min(before_alt)>99.9
 rprev=sol.sol(T-600);mp,vmp=moon(T-600,phase);assert np.dot(rprev[:2]-mp,rprev[2:]-vmp)<0
 after=solve_ivp(rhs(phase),(T,T+86400),captured,rtol=2e-11,atol=1e-10,method='DOP853',dense_output=True)
 times=np.linspace(T,T+86400,721);alt=[np.linalg.norm(after.sol(t)[:2]-moon(t,phase)[0])-RM for t in times]
 independent=solve(phase,dv,method='RK45').y[:,-1];err=np.linalg.norm(independent[:2]-state[:2]);assert err<.1
 out=dict(model='Geocentric restricted3body with circular prescribedMoon,indirect term,Earth+Moon pointgravity; noSun,J2,terrain,finiteburns or ephemeris/SSO-plane solution',parking_altitude_km=500,lunar_arrival_altitude_km=float(np.linalg.norm(r)-RM),arrival_radial_speed_m_s=float(np.dot(r,v)/np.linalg.norm(r)*1000),transfer_days=5,initial_moon_phase_rad=float(phase),departure_delta_v_m_s=float(dv*1000),capture_delta_v_m_s=float(np.linalg.norm(impulse)*1000),lunar_relative_arrival_speed_m_s=float(np.linalg.norm(v)*1000),post_capture_24h_sampled_altitude_km=[float(min(alt)),float(max(alt))],independent_integrator_position_difference_km=float(err),optimizer_residual=objective([phase,dv]),last_12h_minimum_sampled_lunar_altitude_km=float(min(before_alt)),prearrival_radial_velocity_negative=True,launch_hardware_speed_claim=False,physical_validation=False,limitation='One ideal coplanar trajectory with free lunar phase. No actual date/provider/SSO departure plane or long-term orbital lifetime is demonstrated. Capture impulse requires explicitly carried propulsion or a maneuvering carrier; no passive rail-only lunar capture claimed.')
 import csv
 with (P/'LUNAR_CAPTURE_HISTORY.csv').open('w') as fp:
  writer=csv.writer(fp,lineterminator='\n');writer.writerow(['hours_after_capture','lunar_altitude_km']);writer.writerows(zip((times-T)/3600,alt))
 (P/'THREE_BODY_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 plt.rcParams.update({'svg.fonttype':'none','pdf.fonttype':42,'font.family':'DejaVu Sans','font.size':10})
 fig,ax=plt.subplots(figsize=(7,5),layout='constrained');tt=np.linspace(0,T,1500);states=sol.sol(tt);ax.plot(states[0]/1000,states[1]/1000,color='#146c80',label='Computed spacecraft transfer');ms=np.array([moon(t,phase)[0] for t in tt]);ax.plot(ms[:,0]/1000,ms[:,1]/1000,'--',color='#888888',label='Moon over same five days');ax.scatter([0],[0],s=65,color='#333333',label='Earth');ax.scatter([m[0]/1000],[m[1]/1000],s=35,color='#a3642f',label='Lunar arrival');ax.set(xlabel='Geocentric X (1000 km)',ylabel='Geocentric Y (1000 km)',title='One computed five-day Earth–Moon transfer');ax.set_aspect('equal');ax.spines[['top','right']].set_visible(False);ax.legend(fontsize=8)
 for ext in ['png','pdf','svg']:fig.savefig(P/('three_body_transfer.'+ext),dpi=170)
 fig2,ax2=plt.subplots(figsize=(6.5,4),layout='constrained');ax2.plot((times-T)/3600,(np.array(alt)-100)*1000,color='#146c80');ax2.set(xlabel='Hours after capture',ylabel='Altitude difference from 100 km (m)',title='24-hour coast after the modeled capture impulse');ax2.spines[['top','right']].set_visible(False)
 for ext in ['png','pdf','svg']:fig2.savefig(P/('lunar_capture_coast.'+ext),dpi=170)
 p2=P/'lunar_capture_coast.svg';p2.write_text('\n'.join(s.rstrip() for s in p2.read_text().splitlines())+'\n')
 p=P/'three_body_transfer.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
