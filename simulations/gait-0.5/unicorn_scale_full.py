"""Scale unchanged Fourier Gait Lab 0.4 for integer destination N<=1_000_000.
Uses proved deterministic screening on periodic-time bounds to avoid 2.9 billion evaluations.

WARNING: Completely hypothetical sinusoidal leg drive; NO prime-specific gait is modelled.
"""
import itertools, math, time, json, csv, gzip, collections, zipfile
from pathlib import Path
import numpy as np
OUT=Path('/mnt/data/unicorn_fourier_scale_05'); OUT.mkdir(exist_ok=True)
MAX_N=1_000_000
SAMPLES=720
TS=np.linspace(0.,1.,SAMPLES+1)
FREQS=(1,2,3,4,5,6);PHASES=(0.,math.pi/2,math.pi,3*math.pi/2)
MODES=list(itertools.product(FREQS,range(4)))
A=np.stack([np.maximum(0,np.sin(2*np.pi*f*TS+PHASES[q])) for f,q in MODES])
CANDS=[]
for k in (1,2,3):
 for comb in itertools.combinations_with_replacement(range(24),k):
  act=A[list(comb)];s=act.sum(axis=0);pair=(s*s-(act*act).sum(axis=0))/2
  v=10*s/(np.sqrt(k)*(1+.3*pair))
  cum=np.r_[0,np.cumsum((v[:-1]+v[1:])/(2*SAMPLES))]
  CANDS.append({'id':len(CANDS),'k':k,'legs':[list(MODES[z]) for z in comb], 'modes':comb,'birth':.43*k*k+.028*sum(MODES[z][0]**2 for z in comb),'timefactor':1+.055*k*(k-1),'advance':cum[-1],'cum':cum})
assert len(CANDS)==2924

def inv_many(d,c):
 d=np.asarray(d,dtype=np.float64); adv=c['advance']; cum=c['cum']
 cycles=np.floor(d/adv)
 rem=d-cycles*adv
 nearzero=rem<1e-11
 nearfull=(adv-rem)<1e-10
 idx=np.clip(np.searchsorted(cum,rem,side='left'),1,SAMPLES)
 left=cum[idx-1];diff=cum[idx]-left
 phase=np.where(diff<1e-14,idx/SAMPLES,((idx-1)+(rem-left)/np.where(diff>1e-14,diff,1))/(SAMPLES))
 phase=np.where(nearzero,0,phase)
 phase=np.where(nearfull,1,phase)
 return cycles+phase

def time_many(n,c):
 forward=inv_many(n-1,c);back=inv_many(n,c)
 return c['birth']+c['timefactor']*(forward+back)+.35

start=time.perf_counter(); best_asymptotic=min(CANDS,key=lambda c:c['timefactor']/c['advance'])
rate0=best_asymptotic['timefactor']/best_asymptotic['advance']
for c in CANDS:
 if c is best_asymptotic:
  c['search_upto']=MAX_N
  continue
 delta=c['timefactor']/c['advance']-rate0
 if delta<=1e-12:
  c['search_upto']=MAX_N
 else:
  # Bounds of the inverse of a 1-second periodic cumulative travel curve:
  # |inv(d) - d/adv| <= 1 s. Hence for any n, C_c >= B_c+F_c*((2*n-1)/adv_c-2)+final.
  # C_ref <= B_ref+F_ref*((2*n-1)/adv_ref+2)+final.
  # Once LB_c > UB_ref, this candidate provably cannot win at that n or later.
  root=.5+(2*(c['timefactor']+best_asymptotic['timefactor'])-(c['birth']-best_asymptotic['birth']))/(2*delta)
  c['search_upto']=min(MAX_N,max(1,int(math.ceil(root))+2))
ns=np.arange(2,MAX_N+1,dtype=np.float64)
wscore=np.full(MAX_N-1,np.inf,dtype=np.float64)
wid=np.full(MAX_N-1,-1,dtype=np.int16)
tested=0
for c in CANDS:
 stop=c['search_upto']
 if stop<2: continue
 subset=ns[:stop-1];tested+=len(subset)
 scores=time_many(subset,c)
 changes=scores<wscore[:len(subset)]
 wscore[:len(subset)][changes]=scores[changes]
 wid[:len(subset)][changes]=c['id']
assert np.all(wid>=0)
print('swept',MAX_N-1,'targets',len(CANDS),'designs',tested,'candidate-target calculations','elapsed',round(time.perf_counter()-start,2),'seconds')
# Validate original 99 results without trusting only the compressed selector.
legacy=list(csv.DictReader(open('/mnt/data/Team_Unicorn_Fourier_probe_results.csv',encoding='utf-8-sig')))
issues=[]
for ix,old in enumerate(legacy):
 n=ix+2; sel=CANDS[int(wid[ix])]
 err=abs(wscore[ix]-float(old['score']))
 if err>2e-5 or sel['k']!=int(old['k']) or [x[0] for x in sel['legs']]!=json.loads(old['freqs']) or [x[1] for x in sel['legs']]!=json.loads(old['phase_quarters']):
  issues.append((n,err,sel['k'],sel['legs'],old['k'],old['freqs'],old['phase_quarters']))
print('legacy discrepancies',len(issues),'first',issues[:5]);assert not issues
# Strong independent subset cross-check for 300 random and handpicked targets against all 2924 candidates
rng=np.random.default_rng(20261013)
check_ns=np.unique(np.r_[np.arange(2,101),[101,997,1009,10000,10001,99991,100000,100001,999983,1000000],rng.integers(2,MAX_N+1,300)])
brute=np.full(len(check_ns),np.inf);brute_id=np.full(len(check_ns),-1)
for c in CANDS:
 scores=time_many(check_ns,c)
 changes=scores<brute
 brute[changes]=scores[changes]
 brute_id[changes]=c['id']
assert np.allclose(brute,wscore[check_ns-2],rtol=0,atol=5e-8)
assert np.array_equal(brute_id,wid[check_ns-2]);print('independent brute-force crosschecks',len(check_ns),'all matched')
# Reference baseline k=1 for all targets
base1=np.full(MAX_N-1,np.inf)
for c in CANDS[:24]:base1=np.minimum(base1,time_many(ns,c))
# Prime sieve for 2..1M (separate control, not a predictor in gait)
is_prime=np.ones(MAX_N+1,dtype=bool);is_prime[:2]=False
for p in range(2,math.isqrt(MAX_N)+1):
 if is_prime[p]:is_prime[p*p:MAX_N+1:p]=False
isprime=is_prime[2:]
assert isprime.sum()==78498
# Segment summary / winner change counts
changes=np.r_[0,np.nonzero(wid[1:]!=wid[:-1])[0]+1]
runs=[(int(i+2),int(changes[j+1]+1 if j+1<len(changes) else MAX_N),int(wid[i])) for j,i in enumerate(changes)]
count_all=collections.Counter(int(x) for x in wid)
kvals=np.array([c['k'] for c in CANDS],dtype=np.int8)
kout=kvals[wid]
print('k counts',collections.Counter(kout.tolist()),'unique winners',len(count_all),'number winner runs',len(runs));print('top designs',count_all.most_common(12));print('last 15 n',[(int(n),int(wid[n-2]),round(wscore[n-2],4)) for n in range(MAX_N-14,MAX_N+1)])
# Per 10K and per 100K, prime percentage and modal design, speed and savings
blocks=[]
for nstart in range(2,MAX_N+1,10_000):
 end=min(MAX_N,nstart+9999)
 z=slice(nstart-2,end-1)
 p=isprime[z];k=kout[z];t=wscore[z]
 cid=int(collections.Counter(wid[z].tolist()).most_common(1)[0][0])
 blocks.append({'start':nstart,'end':end,'primes':int(p.sum()),'prime_share':round(float(p.mean()),6),'leg_1':int((k==1).sum()),'leg_2':int((k==2).sum()),'leg_3':int((k==3).sum()),'most_common_design_id':cid,'mean_score':round(float(t.mean()),4),'mean_time_reduction_vs_1leg_pct':round(float(100*(1-t.sum()/base1[z].sum())),4)})
# sample selected n (also interactive on webpage via winner runs), and overall
for n in (2,10,50,100,101,997,1009,10000,100000,100001,500000,999983,1000000):
 c=CANDS[int(wid[n-2])];print(n,'prime',is_prime[n],'k',c['k'],'legs',c['legs'],'1s',round(c['advance'],4),'score',round(float(wscore[n-2]),4),'base1',round(float(base1[n-2]),4))
# store condensed winner run list, design params and graph points for reproducible browser UI
# Need include c['cum'] only on demand in JS, not embed every 2924 arrays.
public_cands=[{'id':c['id'],'k':c['k'],'legs':c['legs'],'advance':round(float(c['advance']),12),'birth':round(float(c['birth']),12),'factor':c['timefactor']} for c in CANDS if c['id'] in count_all]
samples=[]
for n in sorted(set([2,3,5,7,11,17,25,37,50,97,100,101,997,1009,10000,10001,100000,100001,500000,999983,1000000])):
 c=CANDS[int(wid[n-2])];samples.append({'n':n,'prime':bool(is_prime[n]),'design_id':int(c['id']),'k':c['k'],'legs':c['legs'],'advance':round(float(c['advance']),6),'score':round(float(wscore[n-2]),6),'one_leg_time':round(float(base1[n-2]),6)})
# write csv 100k uncompressed, and full 1M compressed
header=['destination','prime_destination','gait_design_id','k','frequency_1','phase_q_1','frequency_2','phase_q_2','frequency_3','phase_q_3','distance_per_second','model_total_time','best_one_leg_time']
for maxout,file in [(100_000,OUT/'Team_Unicorn_Fourier_2-100000.csv'),(MAX_N,OUT/'Team_Unicorn_Fourier_2-1000000.csv.gz')]:
 z=open(file,'w',newline='',encoding='utf-8-sig') if maxout<MAX_N else gzip.open(file,'wt',newline='',encoding='utf-8')
 with z as f:
  w=csv.writer(f);w.writerow(header)
  for ix in range(maxout-1):
   c=CANDS[int(wid[ix])]; lg=c['legs']; flat=[]
   for i in range(3):flat.extend(lg[i] if i<len(lg) else ('',''))
   w.writerow([ix+2,int(isprime[ix]),c['id'],c['k'],*flat,round(float(c['advance']),9),round(float(wscore[ix]),6),round(float(base1[ix]),6)])
 print('csv',file,file.stat().st_size)
summary={'model':'unchanged Gait Lab 0.4, hypothetical velocity from rectified harmonics, k=1..3, 24 possible freq-phase modes, 2924 multiset designs','limit':MAX_N,'designs':len(CANDS),'evaluations_after_safe_pruning':tested,'naive_evaluations':(MAX_N-1)*len(CANDS),'baseline_validated_99':True,'full_search_crosscheck_targets':int(len(check_ns)),'optimized_leg_counts':dict(sorted(collections.Counter(kout.tolist()).items())),'prime_destinations':int(isprime.sum()),'distinct_design_winners':len(count_all),'design_runs':len(runs),'sampled_destinations':samples,'overall_total_time':float(wscore.sum()),'one_leg_total_time':float(base1.sum()),'overall_reduction_vs_one_leg_pct':100*(1-wscore.sum()/base1.sum()),'mean_time_opt':float(wscore.mean()),'prime_mean_legs':float(kout[isprime].mean()),'composite_mean_legs':float(kout[~isprime].mean()),'last_100k_counts':dict(sorted(collections.Counter(kout[-100000:].tolist()).items())),'blocks':blocks,'asymptotic_fastest_design':best_asymptotic['id'],'safe_bound_explanation':'Each candidate has 1-second periodic waveform, so |T_inverse(d)-d/advance| <= 1 second. Comparing a lower bound on candidate time to an upper bound on the asymptotically best candidate time gives a provably safe maximum search destination for each design. Full 2924-design brute-force re-evaluation agrees on independent random targets.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
(OUT/'winning_runs.json').write_text(json.dumps({'runs':runs,'winner_designs':public_cands},separators=(',',':')),encoding='utf-8')
with open(OUT/'bins_10000.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=blocks[0].keys());w.writeheader();w.writerows(blocks)
print('overall reduction',summary['overall_reduction_vs_one_leg_pct'],'saved results',OUT,'elapsed',round(time.perf_counter()-start,2),'s')
