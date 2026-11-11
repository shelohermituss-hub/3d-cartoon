import fs from 'node:fs';
const [tag,thr]=[process.argv[2],+process.argv[3]];
const d=JSON.parse(fs.readFileSync(`${process.env.S}/diff_${tag}.json`));
const F=d.length, K=6;
const w=d.map((_,f)=>{let s=0;for(let k=0;k<K;k++)s+=d[Math.min(F-1,f+k)];return s;});
const out=[];
for(let f=1;f<F-K;f++){ if(w[f]>=thr && w[f]>=w[f-1] && w[f]>w[f+1]){ if(!out.length||f/30-out.at(-1)>0.5) out.push(+(f/30).toFixed(2)); else if(w[f]>w[Math.round(out.at(-1)*30)]) out[out.length-1]=+(f/30).toFixed(2);} }
const len=F/30, st=[0,...out], lens=st.map((s,i)=>+((st[i+1]??len)-s).toFixed(2));
const q=(v,p)=>{const s=[...v].sort((a,b)=>a-b),x=(s.length-1)*p,lo=Math.floor(x);return +(s[lo]+(s[Math.ceil(x)]-s[lo])*(x-lo)).toFixed(2)};
console.log(tag,'cuts',JSON.stringify(out));
console.log(JSON.stringify({shots:lens.length,cutsPerMin:+(out.length/(len/60)).toFixed(1),median:q(lens,.5),p10:q(lens,.1),p90:q(lens,.9),mean:+(len/lens.length).toFixed(2)}));
const s=[...d].sort((a,b)=>a-b);console.log('diff p50',s[s.length>>1].toFixed(4),'p90',s[Math.floor(F*.9)].toFixed(4),'p99',s[Math.floor(F*.99)].toFixed(4));
