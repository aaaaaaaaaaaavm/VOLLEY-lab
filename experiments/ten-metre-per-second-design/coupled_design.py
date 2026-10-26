"""New R10/F10 mean-dq/source/motion integration, derived explicitly from frozen ACR1.
New field maps,conductor R/L,mass and bank are inputs. No old k(x) transfer.
"""
import math
import numpy as np
def simulate(design,mass,adverse=False,dt=10e-6,field_factor=1.):
    fly=design['configuration'].startswith('F');target=10.;D=2.5;A=1.3
    carrier=mass['moving_carrier_or_shoe_kg'];payload=4.;host=mass['first_shot_rest_host_kg'];mu=(carrier+payload)*host/(host+carrier+payload);mub=carrier*host/(host+carrier)
    bank=mass['source_bank'];C=bank['adverse_F' if adverse else 'nominal_F'];Rs=bank['adverse_ESR_ohm' if adverse else 'nominal_ESR_ohm']
    R20=max(r['resistance20C_ohm'] for r in design['phases']);T0=100. if adverse else 50.
    L=max(design['inductance'][-1]['balanced_effective_inductance_eigenvalues_H'])*(2 if adverse else 1)
    cu_mass=sum(r['copper_volume_m3'] for r in design['phases'])*8960;cp=385.
    xs=np.array([r['displacement_m'] for r in design['finite_field_stations']]);ks=np.array([r['N_per_peak_A'] for r in design['finite_field_stations']])*field_factor
    bx=xs[xs>=D];bk=ks[xs>=D];rem=np.r_[np.cumsum(((bk[:-1]+bk[1:])/2*np.diff(bx))[::-1])[::-1],0]
    stop_target=D+A-.003;reserve=float(np.interp(stop_target,bx,rem)) if not fly else 0
    friction=10. if adverse else 5.;kfactor=.9 if adverse else 1.
    # Explicit exit-friction feed-forward. Actual/adverse friction is an allocated model input,not measured identification.
    drive_goal=math.sqrt(target**2+2*friction*(design['full_exit_displacement_m']-D)/mu) if fly else target
    x=v=current=t=0.;vc=86.4;last_bank=0.;phase='DRIVE';attached=True;release=None
    ledger={k:0. for k in ['mechanical_J','copper_J','inverter_J','bank_J','auxiliary_J']}
    winding_heat=friction_work=0.;peak_i=peak_device=peak_vds=peak_bank=peak_mod=0.;peak_cell=2.7
    peak_payload=peak_power=peak_inv=0.;status='TIME_LIMIT';trace=[];n=0;handoff=None
    for step in range(int(3/dt)):
        k=max(1e-12,float(np.interp(x,xs,ks)));actual_k=k*kfactor
        Rw=R20*(1+.00393*(T0-20+winding_heat/(cu_mass*cp)));R=Rw+.002
        if phase=='DRIVE':
            acceleration=max(0,min((drive_goal**2-v*v)/(2*max(D-x,.001)),3*drive_goal**2/(2*D)))
            ref=(mu*acceleration+friction)/k
        elif phase=='BRAKE':
            work=float(np.interp(x,bx,rem))-reserve;ref=-.5*mub*v*v/max(work,.0001)
        else:ref=0.
        ref=max(-600,min(600,ref));omega=2*math.pi*v/.048;ke=actual_k/1.5
        terminal_prev=max(40,vc-last_bank*Rs);vmax=.95*terminal_prev/math.sqrt(3)
        qroom=math.sqrt(max(0,vmax*vmax-(omega*L*current)**2))
        qrequest=R*current+ke*v+L*(ref-current)/.00025;vq=max(-qroom,min(qroom,qrequest))
        ripple=terminal_prev/(4*L*40000);ron=.0097*2/10
        def source_power(q):
            mid=current+(q-R*current-ke*v)/L*dt/2
            inv=1.5*ron*mid*mid+ron*ripple*ripple/4+2*terminal_prev*(abs(mid)+ripple/2)*.2e-6*40000+6
            return 1.5*q*mid+R*ripple*ripple/4+inv+50
        budget=.8*vc*vc/(4*Rs);regen_floor=92.8*(vc-92.8)/Rs;p_req=source_power(vq)
        if p_req>budget or p_req<regen_floor:
            lo,hi=0.,1.
            for _ in range(14):
                mid=(lo+hi)/2
                if regen_floor<=source_power(vq*mid)<=budget:lo=mid
                else:hi=mid
            vq*=lo
        di=(vq-R*current-ke*v)/L;imid=current+di*dt/2;motive=actual_k*imid
        force=motive-friction if v>1e-8 else motive+friction if v< -1e-8 else math.copysign(max(0,abs(motive)-friction),motive)
        effective=mu if attached else mub
        if attached:peak_payload=max(peak_payload,payload*max(force,0)/(carrier+payload))
        vn=v+force/effective*dt;xn=x+(v+vn)/2*dt
        pcu=1.5*R*imid*imid+R*ripple*ripple/4
        pinv=1.5*ron*imid*imid+ron*ripple*ripple/4+2*terminal_prev*(abs(imid)+ripple/2)*.2e-6*40000+6
        pdc=1.5*vq*imid+R*ripple*ripple/4+pinv+50;disc=vc*vc-4*Rs*pdc
        if disc<=0:status='SOURCE_POWER_LIMIT';break
        ibank=2*pdc/(vc+math.sqrt(disc));terminal=vc-ibank*Rs
        peak_mod=max(peak_mod,math.hypot(vq,omega*L*current)/(terminal/math.sqrt(3)))
        last_bank=ibank;ledger['mechanical_J']+=actual_k*imid*(xn-x)
        friction_work+=max(0,(motive-force)*(xn-x));ledger['copper_J']+=pcu*dt
        winding_heat+=pcu*Rw/R*dt;ledger['inverter_J']+=pinv*dt;ledger['bank_J']+=ibank*ibank*Rs*dt;ledger['auxiliary_J']+=50*dt
        vc-=ibank/C*dt;peak_cell=max(peak_cell,vc/32,terminal/32)
        current+=di*dt;x,v,t=xn,vn,t+dt
        peak_i=max(peak_i,abs(current));peak_bank=max(peak_bank,abs(ibank));peak_power=max(peak_power,pdc);peak_inv=max(peak_inv,pinv)
        peak_device=max(peak_device,(abs(current)+ripple/2)/10*1.25);peak_vds=max(peak_vds,terminal+(abs(current)+ripple/2)*30e-9/.2e-6)
        if n%200==0:trace.append([t,x,v,current,vc])
        n+=1
        if phase=='DRIVE' and x>=D:
            handoff=dict(time_s=t,position_m=x,speed_m_s=v);phase='EXIT' if fly else 'BRAKE'
        if not fly and phase=='BRAKE' and attached and force<=0:
            release=dict(time_s=t,position_m=x,relative_speed_m_s=v,payload_inertial_kick_m_s=host/(host+carrier+payload)*v,
                host_recoil_before_arrest_m_s=-(carrier+payload)/(host+carrier+payload)*v);attached=False
        if fly and x>=design['full_exit_displacement_m']:
            release=dict(time_s=t,position_m=x,relative_speed_m_s=v,payload_plus_attached_shoe_kg=carrier+payload,
                outbound_inertial_kick_m_s=host/(host+carrier+payload)*v,host_recoil_m_s=-(carrier+payload)/(host+carrier+payload)*v)
            status='FREE_EXIT';break
        if not fly and phase=='BRAKE' and not attached and v<=.005:status='STOPPED';break
        if not fly and x>D+A+.001:status='ARREST_STROKE_EXCEEDED';break
        if vc<60:status='LOW_SOURCE_VOLTAGE';break
    drawn=.5*C*(86.4**2-vc**2);field=.75*L*current*current;residual=drawn-sum(ledger.values())-field
    independent=.5*mu*v*v+friction_work if fly else (None if release is None else .5*(mu-mub)*release['relative_speed_m_s']**2+.5*mub*v*v+friction_work)
    thermal=dict(winding_initial_C=T0,winding_adiabatic_rise_C=winding_heat/(cu_mass*cp),winding_end_C=T0+winding_heat/(cu_mass*cp),
        copper_cp_assumed_J_kgK=cp,bank_ESR_adiabatic_rise_for_cp700to1200_C=[ledger['bank_J']/(bank['bare_cell_mass_kg']*1200),ledger['bank_J']/(bank['bare_cell_mass_kg']*700)],
        bank_cp_is_assumption_not_catalog_property=True,inverter_loss_J=ledger['inverter_J'],inverter_peak_total_loss_W=peak_inv,
        inverter_transient_junction_temperature_not_resolved=True,material_host_sink_and_repeated_duty_acceptance_unverified=True)
    checks=dict(departure=release is not None,speed=release is not None and abs(release['relative_speed_m_s']-target)<=.005,
        arrest_or_free_exit=status=='FREE_EXIT' if fly else status=='STOPPED' and x<=D+A,
        phase_current=peak_i<=600.1,hot_device_current=peak_device<=92,switch_voltage=peak_vds<200,
        cell_voltage=peak_cell<3,modulation=peak_mod<=1,energy_balance=abs(residual)<max(.5,.01*abs(drawn)))
    return dict(configuration=design['configuration'],adverse=adverse,dt_s=dt,field_factor=field_factor,target_exit_m_s=target,
        drive_goal_m_s=drive_goal,L_H=L,R20_ohm=R20,status=status,release=release,handoff=handoff,
        final_position_m=x,final_relative_speed_m_s=v,elapsed_s=t,source_draw_J=drawn,final_bank_V=vc,
        energy_ledger=ledger,magnetic_energy_end_J=field,total_energy_residual_J=residual,
        independent_mechanical_work_J=independent,independent_mechanical_residual_J=None if independent is None else ledger['mechanical_J']-independent,
        friction_heat_J=friction_work,peak_phase_current_A=peak_i,peak_hot_device_current_A=peak_device,peak_switch_V=peak_vds,
        peak_bank_current_A=peak_bank,peak_source_power_W=peak_power,peak_cell_V=peak_cell,max_modulation=peak_mod,
        peak_payload_axial_normal_N=peak_payload,thermal=thermal,checks=checks,all_model_gates_pass=all(checks.values()),
        trace=trace,return_reset_simulated=False,manufacturing_or_full_feeder_acceptance=False)
