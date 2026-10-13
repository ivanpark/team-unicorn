
'use strict';
const EPS=1e-9, BASE_D=[5,2,3,7,11,13], BASE_F=[7,1,1,1,1,1];
const $=id=>document.getElementById(id);
function isPrime(n){if(!Number.isSafeInteger(n)||n<2)return false;if(n%2===0)return n===2;for(let d=3;d*d<=n;d+=2)if(n%d===0)return false;return true;}
function factors(n){if(n<1)return '—';if(n===1)return '1';const out=[];let d=2;while(d*d<=n){let a=0;while(n%d===0){a++;n/=d;}if(a)out.push(a===1?String(d):`${d}^${a}`);d=d===2?3:d+2;}if(n>1)out.push(String(n));return out.join(' × ');}
function makeLegs(k,ds,fs,phaseMode){return ds.slice(0,k).map((d,i)=>({stride:d,frequency:fs[i],phase:i===0||phaseMode==='aligned'?1:i/k}));}
function schedule(legs,T,cost,controller){
 const ev=[];
 legs.forEach((l,i)=>{for(let j=0;;j++){const r=(j+l.phase)/l.frequency;if(r>T+EPS)break;ev.push({leg:i+1,request:j+1,release:r,stride:l.stride});if(ev.length>100000)throw Error('이벤트가 너무 많습니다. 빈도를 줄여주세요.');}});
 ev.sort((a,b)=>Math.abs(a.release-b.release)>EPS?a.release-b.release:a.leg-b.leg||a.request-b.request);
 const h=cost*(legs.length-1),free=Array(controller==='shared'?1:legs.length).fill(0);
 for(const e of ev){const lane=controller==='shared'?0:e.leg-1;e.start=Math.max(e.release,free[lane]);e.finish=e.start+h;e.wait=e.start-e.release;e.service=h;free[lane]=e.finish;}
 return ev;
}
function snapshot(legs,ev,T,cost,controller){
 const req=ev.filter(e=>e.release<=T+EPS),done=req.filter(e=>e.finish<=T+EPS);
 const D=done.reduce((s,e)=>s+e.stride,0),prev=done.filter(e=>e.finish<=Math.max(0,T-1)+EPS).reduce((s,e)=>s+e.stride,0);
 const h=cost*(legs.length-1);const load=controller==='shared'?h*legs.reduce((s,l)=>s+l.frequency,0):Math.max(...legs.map(l=>h*l.frequency));
 return {time:T,distance:D,prime:isPrime(D),factors:factors(D),speed:D/T,lastSecond:D-prev,requested:req.length,completed:done.length,pending:req.length-done.length,ideal:req.reduce((s,e)=>s+e.stride,0),load,moves:legs.map((_,i)=>done.filter(e=>e.leg===i+1).length)};
}
function run(k,ds,fs,phase,cost,controller){const legs=makeLegs(k,ds,fs,phase),events=schedule(legs,10,cost,controller);return {legs,events,snapshots:[1,5,10].map(T=>snapshot(legs,events,T,cost,controller))};}
function fmt(v,n=3){return Number(v.toFixed(n)).toLocaleString('ko-KR');}
let state=null;
function getConfig(){const ds=BASE_D.map((_,i)=>Number($('d'+i).value));const fs=BASE_F.map((_,i)=>Number($('f'+i).value));if(ds.some(d=>!Number.isInteger(d)||d<1||d>1000)||fs.some(f=>!Number.isFinite(f)||f<=0||f>100))throw Error('거리는 1~1000의 정수, 요청 횟수는 0보다 크고 100 이하로 입력하세요.');return {k:Number($('k').value),ds,fs,cost:Number($('cost').value)/1000,phase:$('phase').value,controller:$('controller').value};}
function render(){try{
 $('error').style.display='none';const c=getConfig();const result=run(c.k,c.ds,c.fs,c.phase,c.cost,c.controller);state={model:'Unicorn Gait Lab 0.2',assumptions:'Toy arithmetic + controller scheduling; not physical locomotion; default strides do not establish a prime-to-stride law.',config:c,result,comparison:[]};
 $('kLabel').textContent=c.k;$('costLabel').textContent=`${fmt(c.cost*1000)} ms`;
 BASE_D.forEach((_,i)=>{const row=$('leg'+i);row.className=i<c.k?'':'disabled';const ph=i===0||c.phase==='aligned'?1:i/c.k;$('p'+i).textContent=i<c.k?fmt(ph/c.fs[i],5):'비활성';});
 const rho=result.snapshots[0].load,h=c.cost*(c.k-1);
 $('load').innerHTML=`현재 요청 한 건의 관리시간 <strong>${fmt(h*1000)} ms</strong> · 관리자 부하 <strong>${fmt(rho)}</strong>. `+(rho>1+EPS?'요청량이 처리능력을 넘는다. 계속 실행하면 미처리 요청이 증가한다.':Math.abs(rho-1)<=EPS?'평균 처리능력을 모두 사용한다. 추가 지연을 흡수할 여유가 없다.':'평균 요청량은 처리능력 이하다. 그래도 관측 시점이나 동시 요청에 따른 대기가 남을 수 있다.');
 $('metrics').innerHTML=result.snapshots.map(s=>`<div class="metric"><div class="time">${s.time}초 누적</div><div class="value">${fmt(s.distance,0)} <span class="units">units</span></div><div><span class="tag ${s.prime?'prime':''}">${s.prime?'소수':s.distance<2?'소수 아님':'합성수'}</span></div><div class="small" style="margin-top:9px">${s.factors}<br>완료 횟수 [${s.moves.join(', ')}]<br>미완료 요청 ${s.pending}건</div></div>`).join('');
 $('summary').innerHTML=result.snapshots.map(s=>`<tr><td>${s.time}초</td><td>${s.ideal}</td><td><strong>${s.distance}</strong></td><td>${fmt(s.speed)}</td><td>${s.lastSecond}</td><td>${s.completed}</td><td>${s.pending}</td></tr>`).join('');
 let rows='';for(let k=1;k<=6;k++){const r=run(k,c.ds,c.fs,c.phase,c.cost,c.controller),ss=r.snapshots;state.comparison.push({k,snapshots:ss});rows+=`<tr class="${k===c.k?'selected':''}"><td>${k}개</td><td>${ss[0].distance}</td><td>${ss[1].distance}</td><td>${ss[2].distance}</td><td>${ss[2].pending}</td><td>${fmt(ss[2].load)}</td></tr>`;}$('comparison').innerHTML=rows;
 $('eventlog').innerHTML=result.events.slice(0,160).map(e=>`<tr><td>${e.leg} / ${e.request}</td><td>${fmt(e.release,5)}</td><td>${fmt(e.start,5)}</td><td>${fmt(e.finish,5)}</td><td>${fmt(e.wait,5)}</td><td>+${e.stride}</td><td>${e.finish<=10+EPS?'완료':'대기 / 처리 중'}</td></tr>`).join('');
 }catch(e){$('error').style.display='block';$('error').textContent=e.message;}}
function preset(k,cost){BASE_D.forEach((d,i)=>{$('d'+i).value=d;$('f'+i).value=BASE_F[i];});$('k').value=k;$('cost').value=cost;$('phase').value='staggered';$('controller').value='shared';render();}
function init(){
 $('legs').innerHTML=BASE_D.map((d,i)=>`<tr id="leg${i}"><td>Leg ${i+1}</td><td><input aria-label="Leg ${i+1} 동작당 거리" id="d${i}" type="number" value="${d}" min="1" max="1000" step="1"></td><td><input aria-label="Leg ${i+1} 초당 요청" id="f${i}" type="number" value="${BASE_F[i]}" min="0.1" max="100" step="0.1"></td><td id="p${i}"></td></tr>`).join('');
 document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',render));$('original').addEventListener('click',()=>preset(1,0));$('two').addEventListener('click',()=>preset(2,0));$('six').addEventListener('click',()=>preset(6,30));$('download').addEventListener('click',()=>{if(!state)return;const blob=new Blob([JSON.stringify(state,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='unicorn_gait_lab_02_current.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});render();
}
if(typeof document!=='undefined')init();
if(typeof module!=='undefined')module.exports={run,isPrime,factors,makeLegs,schedule,snapshot};
