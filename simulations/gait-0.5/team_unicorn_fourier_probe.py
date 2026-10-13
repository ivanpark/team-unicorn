"""Team Unicorn exploratory Fourier gait probe; no prime-labelled stride or p-length assumption.
Toy stance rectifier with bounded per-leg effort and coordination cost; NOT physics.
Reproducible Python 3 + NumPy. Also Fourier character divisibility test.
"""
import numpy as np, math, itertools, csv, collections, json
from pathlib import Path
root=Path('/mnt/data'); N=720; ts=np.linspace(0.,1.,N+1); freqs=(1,2,3,4,5,6); phases=(0.,math.pi/2,math.pi,3*math.pi/2)
modes=list(itertools.product(freqs,range(len(phases))))
legs=np.stack([np.maximum(np.sin(2*math.pi*f*ts+phases[pi]),0.) for f,pi in modes],axis=0)
# Parameters selected BEFORE evaluating prime distribution; equal effort normalisation
V0=10.; OVERLAP=0.30; BIRTH_K=0.43; FREQ_PENALTY=0.028; COORD_K=0.055; FINAL=0.35
ns=np.arange(2,101)
rows=[]; winners={int(n):(1e6,None) for n in ns}
all_cands=0
for k in (1,2,3):
 for comb in itertools.combinations_with_replacement(range(len(modes)), k):
  all_cands+=1
  selected=legs[np.array(comb)]; summed=selected.sum(axis=0)
  pairwise=(summed*summed-(selected*selected).sum(axis=0))/2
  # Fixed effort scale, concurrent positive stance pulses, phase crowding penalty
  velo=V0*summed/(math.sqrt(k)*(1.+OVERLAP*pairwise))
  increments=(velo[:-1]+velo[1:])/(2*N)
  cum=np.r_[0.,np.cumsum(increments)]
  advance=float(cum[-1])
  if advance<1e-8:continue
  def inv(target):
   cycles=int(np.floor(target/advance))
   rem=target-cycles*advance
   if rem<1e-11:return float(cycles)
   if advance-rem<1e-10:return float(cycles+1)
   j=int(np.searchsorted(cum,rem,side='left'))
   j=max(1,min(N,j))
   if cum[j]-cum[j-1]<1e-14:tm=j/N
   else:tm=((j-1)+(rem-cum[j-1])/(cum[j]-cum[j-1]))/N
   return cycles+tm
  costbirth=BIRTH_K*k*k + FREQ_PENALTY*sum(modes[i][0]**2 for i in comb)
  effective_time_factor=1+COORD_K*k*(k-1)
  for n in ns:
   forward=inv(float(n-1)); ret=inv(float(n));
   score=costbirth+effective_time_factor*(forward+ret)+FINAL
   if score<winners[int(n)][0]:
    winners[int(n)]=(score,{'destination':int(n),'k':k,'freqs':[modes[i][0] for i in comb],'phase_quarters':[modes[i][1] for i in comb], 'one_second_distance':round(advance,6),'birth_cost':round(costbirth,6),'outbound_time':round(forward,6),'return_time':round(ret,6),'score':round(score,6)})
for n,(cost,r) in winners.items():
 r['prime_destination']=n>=2 and all(n%i for i in range(2,math.isqrt(n)+1));rows.append(r)
# Fourier character sieve: divisibility via cyclic Fourier phase sum for *all* q, including composites
sieve=[]
for n in range(2,101):
 hits=[]
 for q in range(2,math.isqrt(n)+1):
  # Numeric Fourier roots of unity orthogonality
  val=sum(complex(math.cos(2*math.pi*j*n/q),math.sin(2*math.pi*j*n/q)) for j in range(q))/q
  phase_hit=abs(val-1)<1e-9
  mod_hit=n%q==0
  assert phase_hit==mod_hit,(n,q,val)
  if phase_hit:hits.append(q)
 prime=(len(hits)==0)
 assert prime==winners[n][1]['prime_destination']
 sieve.append({'integer':n,'prime':prime,'divisibility_frequencies':hits})
with open(root/'Team_Unicorn_Fourier_probe_results.csv','w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=['destination','prime_destination','k','freqs','phase_quarters','one_second_distance','outbound_time','return_time','birth_cost','score']);w.writeheader();w.writerows(rows)
with open(root/'Team_Unicorn_Fourier_probe.json','w',encoding='utf-8') as f:json.dump({'assumptions':{'velocity':'v(t)=10*sum_i max(0,sin(2pi*f_i*t+phi_i))/(sqrt(k)*(1+0.30*sum_{i<j}a_i a_j))','birth':'0.43*k^2+0.028*sum_i f_i^2','coordination':'travel time multiplied by 1+0.055*k*(k-1)','final_add':'0.35 seconds','frequencies':freqs,'phases':phases,'leg_count':[1,2,3],'each_prime_label_does_not_enter_motion':'yes, so prime structure cannot be inferred from gait optimization alone'},'candidate_count':all_cands,'results':rows,'fourier_sieve':sieve},f,ensure_ascii=False,indent=2)
co=collections.Counter(r['k'] for r in rows); pairs=collections.Counter(tuple(r['freqs']) for r in rows)
primefreqs=[f for r in rows for f in r['freqs']]
print('candidates',all_cands,'kcounts',co,'freqs',collections.Counter(primefreqs),'most designs',pairs.most_common(12))
print('selected targets')
for n in (2,3,5,7,11,13,17,25,29,37,50,64,73,97,100):print(winners[n][1])
print('sieve 99/99 exact, classifications primes',sum(x['prime'] for x in sieve))
