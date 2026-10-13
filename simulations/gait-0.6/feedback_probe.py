#!/usr/bin/env python3
"""Gait 0.6 — local phase-feedback vs open-loop after unexpected phase kicks.
Deliberately toy oscillators: NOT locomotion physics, prime-number evidence, or real time.
"""
import math,csv,json
from pathlib import Path
OUT=Path(__file__).parent
DT=0.0025; V0=10.; OVERLAP=0.30; MAX_CONTROL=3.0
KICKS=[(0.75,[0.,math.pi/2,-math.pi/2]),(3.0,[0.,-math.pi/2,math.pi/3]),(7.0,[0.,math.pi/3,-math.pi/2])]

def sim(k=2, horizon=10.,gain=1.5, disturbance=True, f=1., target=None, collect=False):
    steps=round(horizon/DT); th=[2*math.pi*i/k for i in range(k)]
    x=0.; effort=0.; max_phase_error=0.; track=[]; triggered=set(); prev_x=0.;hit_time=None
    for j in range(steps):
        now=j*DT
        if disturbance:
            for q,(when,kick) in enumerate(KICKS):
                if q not in triggered and now+DT*.5>=when:
                    th=[z+kick[i] for i,z in enumerate(th)];triggered.add(q)
        a=[max(0., math.sin(z)) for z in th]
        pair=sum(a[i]*a[q] for i in range(k) for q in range(i+1,k))
        vel=V0*sum(a)/(math.sqrt(k)*(1.+OVERLAP*pair))
        prev_x=x; x+=vel*DT
        if target is not None and hit_time is None and x>=target:
            hit_time=now+DT*((target-prev_x)/(x-prev_x)) if x>prev_x else now+DT
        us=[0.]*k
        for i in range(1,k):
            error=(th[i]-th[0]-2*math.pi*i/k+math.pi)%(2*math.pi)-math.pi
            max_phase_error=max(max_phase_error,abs(error))
            us[i]=max(-MAX_CONTROL,min(MAX_CONTROL,-gain*math.sin(error)))
        effort+=sum(u*u for u in us)*DT
        for i in range(k): th[i]+=(2*math.pi*f+us[i])*DT
        if collect and j%40==0:track.append([round(now+DT,4),round(x,6),round(vel,6),round(max_phase_error,4)])
    errors=[((th[i]-th[0]-2*math.pi*i/k+math.pi)%(2*math.pi)-math.pi) for i in range(1,k)]
    return dict(k=k,horizon=horizon,gain=gain,perturbed=disturbance,distance=x,control_effort=effort,phase_error_rms=(sum(e*e for e in errors)/len(errors))**.5 if errors else 0,hit_time=hit_time,track=track)

rows=[]
for k in [1,2,3]:
 for horizon in [1.,5.,10.]:
  ref=sim(k,horizon,0.,False)
  fixed=sim(k,horizon,0.,True)
  for gain in [0.,0.6,1.5,3.0]:
   z=sim(k,horizon,gain,True)
   rows.append({key:round(val,8) if isinstance(val,float) else val for key,val in dict(k=k,T=horizon,gain=gain,ideal_distance=ref['distance'],actual_distance=z['distance'],fixed_perturbed_distance=fixed['distance'],distance_gain_over_fixed=z['distance']-fixed['distance'],percent_vs_fixed=100*(z['distance']/fixed['distance']-1) if fixed['distance'] else 0,control_effort=z['control_effort'],endpoint_phase_error_rad=z['phase_error_rms']).items()})
with (OUT/'results.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(OUT/'parameters.json').write_text(json.dumps({'dt':DT,'velocity':'10*sum(max(0,sin(theta_i)))/(sqrt(k)*(1+0.30*sum pairwise active_i*active_j))','oscillator':'theta_i derivative =2pi f + control_i, f=1 Hz','controller':'control_0=0, control_i=clip(-K sin(wrapped(theta_i-theta_0-2pi*i/k)),-3,+3) rad/s','kicks':KICKS,'control_effort':'integral sum_i control_i^2 dt; not subtracted from distance','assumptions':'phase kicks unexpected at 0.75s,3s,7s; each phase sensor internal; reference controls can observe current phases; no motion physics; no primes embedded; no distance feedback'},indent=2))
print('k T ideal fixed feedback(K=1.5) gain_pct effort err_rms')
for k in [1,2,3]:
 for T in [1,5,10]:
  p=next(z for z in rows if z['k']==k and z['T']==T and z['gain']==1.5)
  print(k,T,*(round(p[x],4) for x in ['ideal_distance','fixed_perturbed_distance','actual_distance','percent_vs_fixed','control_effort','endpoint_phase_error_rad']))
for k in [2,3]:
 for n in [5,15,30]:
  z0=sim(k,12,0,True,target=n-1);z1=sim(k,12,1.5,True,target=n-1)
  print('arrival k',k,'dest',n,'fixed',z0['hit_time'],'adapt',z1['hit_time'])
