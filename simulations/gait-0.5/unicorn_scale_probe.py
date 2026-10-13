import numpy as np, math,itertools,collections,time
start=time.time(); N=720; ts=np.linspace(0,1,N+1);freqs=(1,2,3,4,5,6);phases=(0,math.pi/2,math.pi,3*math.pi/2);modes=list(itertools.product(freqs,range(4)))
legs=np.stack([np.maximum(np.sin(2*math.pi*f*ts+phases[pi]),0.) for f,pi in modes]); designs=[]
for k in (1,2,3):
 for comb in itertools.combinations_with_replacement(range(24),k):
  sel=legs[list(comb)]; summed=sel.sum(axis=0); pairwise=(summed*summed-(sel*sel).sum(axis=0))/2
  vel=10*summed/(math.sqrt(k)*(1+.3*pairwise)); cum=np.r_[0,np.cumsum((vel[1:]+vel[:-1])/(2*N))];adv=cum[-1]
  B=.43*k*k+.028*sum(modes[i][0]**2 for i in comb); F=1+.055*k*(k-1)
  designs.append((comb,adv,B,F,cum))
best=min(range(len(designs)),key=lambda i: designs[i][3]/designs[i][1]); ref=designs[best]; slope=ref[3]/ref[1]; print('generated',len(designs),'in',round(time.time()-start,3),'s'); print('maxrate design',best,'comb',ref[0],'leg modes',[modes[i] for i in ref[0]],'adv',ref[1],'B',ref[2],'F',ref[3],'slope',slope)
thresholds=[];tiemodes=[]; rank=[]
for i,d in enumerate(designs):
 if i==best: continue
 dm=d[3]/d[1]-slope
 if dm < 1e-12:
  tiemodes.append((i,dm,d[0])); end=1_000_000
 else:
  x=.5+(2*(d[3]+ref[3])-(d[2]-ref[2]))/(2*dm)
  end=max(1,int(math.ceil(x))+2)
 thresholds.append((i,end,dm))
print('ties',len(tiemodes),tiemodes[:25]);print('total scored candidate x n  up to 1M',sum(min(1_000_000,e) for _,e,_ in thresholds)+1_000_000)
print('n_end percentiles',np.quantile([x[1] for x in thresholds],[0,.25,.5,.75,.9,.95,.99,.999,1]));print('largest thresholds',sorted(thresholds,key=lambda x:-x[1])[:20]);print('runtime',round(time.time()-start,2))
