#!/usr/bin/env python3
"""Team Unicorn destination-aware integer-stepping toy model v0.3.
Model assumptions clearly artificial; NOT a derivation of primality or physical gait.
Plain Python 3 standard-library only; deterministic, exhaustive over specified catalog.
"""
from itertools import combinations_with_replacement
from math import sqrt
from collections import Counter, defaultdict
import csv,json,os,random,statistics

PRIMES=(2,3,5,7,11,13)
DESTINATIONS=range(2,101)
COORD_COSTS={'light':0.06,'medium':0.14,'heavy':0.24}
FINISH_COST=0.35
FINE_COST=0.62
MAX_DISTANCE=100
BIRTH_COEFF=0.07
BIRTH_COUNT=0.10
PULSE_BASE=0.10
PULSE_SQRT_COEFF=0.045
IDLE_COEFF=0.015
SYSTEM_COEFF=0.015


def is_prime(n):
    if n<2:return False
    return all(n%d for d in range(2,int(sqrt(n))+1))

def factors(n):
    k=n; result=[]
    for p in range(2,n+1):
        if p*p>k:break
        if k%p==0:
            e=0
            while k%p==0:k//=p;e+=1
            result.append([p,e])
    if k>1:result.append([k,1])
    return result


def make_actions(design, gamma):
    k=len(design)
    actions=[{'distance':1,'time':FINE_COST+SYSTEM_COEFF*(k-1),'label':'+1 fine','legs':[],'fine':True}]
    for mask in range(1,1<<k):
        indices=[j for j in range(k) if mask & (1<<j)]
        r=len(indices)
        step=sum(design[j] for j in indices)
        time=(max(PULSE_BASE+PULSE_SQRT_COEFF*sqrt(design[j]) for j in indices)
              +gamma*(r-1)**2+IDLE_COEFF*(k-r)+SYSTEM_COEFF*(k-1))
        actions.append({'distance':step,'time':time,'label':'+'.join(str(design[j]) for j in indices), 'legs':indices,'fine':False})
    return actions


def calc_design(design, gamma):
    actions=make_actions(design,gamma)
    dp=[0.]+[float('inf')]*MAX_DISTANCE
    steps=[0]+[10**9]*MAX_DISTANCE
    prev=[None]*(MAX_DISTANCE+1)
    # minimum duration to reach exactly position d, sequential pulses, dynamic program.
    for d in range(1,MAX_DISTANCE+1):
        for ai, a in enumerate(actions):
            if a['distance']<=d:
                candidate=dp[d-a['distance']]+a['time']
                counts=steps[d-a['distance']]+1
                if candidate < dp[d]-1e-11 or (abs(candidate-dp[d])<1e-11 and counts<steps[d]):
                    dp[d]=candidate; steps[d]=counts; prev[d]=(d-a['distance'],ai)
    birth=BIRTH_COEFF*sum(sqrt(p) for p in design)+BIRTH_COUNT*len(design)**2
    return {'design':list(design),'actions':actions,'dp':dp,'steps':steps,'prev':prev,'birth':birth}


def trace(sim, distance):
    arr=[]; d=distance
    while d:
        pr=sim['prev'][d]
        assert pr is not None
        start, ai=pr
        a=sim['actions'][ai]
        arr.append({'from':start,'to':d,'jump':a['distance'],'duration':round(a['time'],6),'legs':a['legs'],'label':a['label'],'fine':a['fine']})
        d=start
    return list(reversed(arr))


def optimize_regime(gamma, objective='roundtrip', availability='preloaded'):
    designs=[calc_design(c,gamma) for k in range(1,5) for c in combinations_with_replacement(PRIMES,k)]
    def score(c, n):
        m=n-1
        return c['birth']+c['dp'][m]+FINISH_COST+(c['dp'][n] if objective=='roundtrip' else 0)
    baseline=min(designs,key=lambda c:sum(score(c,n) for n in DESTINATIONS))
    out=[]
    for n in DESTINATIONS:
        available=[c for c in designs if availability=='preloaded' or max(c['design'])<=max(2,n-1)]
        winner=min(available,key=lambda c:score(c,n))
        best_one=min((c for c in available if len(c['design'])==1),key=lambda c:score(c,n))
        m=n-1
        path=trace(winner,m)
        back=trace(winner,n) if objective=='roundtrip' else []
        out.append({'unicorn':n, 'destination':n, 'previous_rock':m, 'is_prime_target':is_prime(n),
                    'target_factors':factors(n),'predecessor_factors':factors(m),
                    'legs':winner['design'],'k':len(winner['design']),'birth':round(winner['birth'],5),
                    'outbound':round(winner['dp'][m],5),'final_plus_one':FINISH_COST,
                    'return':round(winner['dp'][n],5) if objective=='roundtrip' else 0,
                    'total':round(score(winner,n),5),'gait_steps':len(path),
                    'max_stride':max((a['jump'] for a in path),default=0),
                    'fine_steps':sum(a['fine'] for a in path),
                    'path':path,'return_path':back,
                    'fixed_design_total':round(score(baseline,n),5),
                    'gain_vs_fixed':round(score(baseline,n)-score(winner,n),5),
                    'best_single_legs':best_one['design'], 'best_single_total':round(score(best_one,n),5),
                    'gain_vs_single':round(score(best_one,n)-score(winner,n),5)})
    stats={'n':len(out),'catalog_designs':len(designs),'mean_total':round(statistics.mean(r['total'] for r in out),4),
          'mean_fixed':round(statistics.mean(r['fixed_design_total'] for r in out),4),
          'total_gain_pct':round(100*sum(r['gain_vs_fixed'] for r in out)/sum(r['fixed_design_total'] for r in out),3),
          'single_gain_pct':round(100*sum(r['gain_vs_single'] for r in out)/sum(r['best_single_total'] for r in out),3),
          'mean_by_prime':{kind:round(statistics.mean(r['total'] for r in out if r['is_prime_target']==b),3) for kind,b in [('prime',True),('composite',False)]},
          'k_counts':dict(sorted(Counter(r['k'] for r in out).items())),
          'fixed_legs':baseline['design'], 'prime_destinations':sum(r['is_prime_target'] for r in out)}
    return {'gamma':gamma,'objective':objective,'availability':availability,'stats':stats,'results':out}


def run():
    root=os.path.dirname(os.path.abspath(__file__))
    data={kind:{avail:{obj:optimize_regime(g,obj,avail) for obj in ('roundtrip','outbound')} for avail in ('preloaded','inherited')} for kind,g in COORD_COSTS.items()}
    output={'description':'Unicorn 2..100 destination-aware exhaustive design search, toy arithmetic gait, not physical locomotion',
            'parameter_values':{
                'allowed_leg_prime_labels':PRIMES,'leg_count_min':1,'leg_count_max':4,'repeated_prime_legs_allowed':True,
                'pulse_step':'sum of labels of simultaneously active leg subset; conjectural movement mapping',
                'pulse_seconds':f'max_i({PULSE_BASE}+{PULSE_SQRT_COEFF}*sqrt(p_i))+gamma*(r-1)^2+{IDLE_COEFF}*(k-r)+{SYSTEM_COEFF}*(k-1)',
                'fine_plus1_seconds':FINE_COST,'final_plus1_seconds':FINISH_COST,
                'birth_seconds':f'{BIRTH_COEFF}*sum(sqrt(p_i))+{BIRTH_COUNT}*k^2',
                'origin':0,'bridge_stone_at': 'unicorn n places stone n after reaching n-1 and final +1',
                'return': 'same design, reversing moves to cover distance n; informational proxy',
                'objective': 'birth + exact outbound time to n-1 + final +1 + exact return time of n (or outbound only)',
                'gamma_cases':COORD_COSTS, 'availability_options': {'preloaded':'prime parts 2..13 available to HQ from start','inherited':'only prime leg parts p<=n-1 at target n; special p=2 bootstrap at n=2'},
                'fixed_design_baseline':'best single multi-leg architecture across all n=2..100; gait still tailored per destination'},
            'regimes':data}
    with open(os.path.join(root,'results.json'),'w',encoding='utf8') as f:json.dump(output,f,ensure_ascii=False,separators=(',',':'))
    with open(os.path.join(root,'results.csv'),'w',newline='',encoding='utf-8-sig') as f:
        fields=['regime','availability','objective','unicorn','destination','previous_rock','is_prime_target','legs','k','birth','outbound','final_plus_one','return','total','gait_steps','fine_steps','fixed_design_total','gain_vs_fixed']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for mode,avs in data.items():
            for availability,objs in avs.items():
                for objective,r in objs.items():
                    for item in r['results']:
                        z={field:item.get(field,'') for field in fields};z.update({'regime':mode,'availability':availability,'objective':objective,'legs':'-'.join(map(str,item['legs']))})
                        w.writerow(z)
    for mode, avs in data.items():
      for availability, objs in avs.items():
        r=objs['roundtrip']
        print(mode,availability,'full',r['stats'])
        for n in [2,3,5,11,12,13,17,29,30,31,37,50,64,97,100]:
            a=r['results'][n-2];print(f'  {n:3} {str(a["legs"]):20} tot {a["total"]:7.3f} birth {a["birth"]:5.2f} travel {a["outbound"]:5.2f} return {a["return"]:5.2f} steps {a["gait_steps"]} vs 1leg {a["gain_vs_single"]:5.2f}')
    # checks: arithmetic, minimality, and exhaustive objective values for every candidate.
    rng=random.Random(450)
    for mode,gamma in COORD_COSTS.items():
        sims=[calc_design(c,gamma) for k in range(1,5) for c in combinations_with_replacement(PRIMES,k)]
        for availability in ('preloaded','inherited'):
          for objective in ('roundtrip','outbound'):
            for r in data[mode][availability][objective]['results']:
                assert sum(s['jump'] for s in r['path'])==r['destination']-1
                assert r['previous_rock']+1==r['destination']
                if objective=='roundtrip':assert sum(s['jump'] for s in r['return_path'])==r['destination']
                for path in (r['path'],r['return_path']):
                    pos=0
                    for step in path:assert step['from']==pos;pos=step['to']
                assert abs(sum(s['duration'] for s in r['path'])-r['outbound'])<0.0005
                n=r['destination']
                def sc(c):return c['birth']+c['dp'][n-1]+FINISH_COST+(c['dp'][n] if objective=='roundtrip' else 0)
                avail=[c for c in sims if availability=='preloaded' or max(c['design'])<=max(2,n-1)]
                assert abs(min(map(sc,avail))-r['total'])<1e-4,(mode,availability,objective,n)
    print('PASS exhaustive+path verification for 12 x 99 cases')
    return output

if __name__=='__main__':run()
