import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
const [file, tag] = process.argv.slice(2);
const W=36,H=64,N=W*H*3;
// crop out caption zone (bottom-middle 60-80%) -> blank rows 40..52 of 64
const raw=spawnSync('ffmpeg',['-v','error','-i',file,'-vf',`scale=${W}:${H}:flags=area`,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],{maxBuffer:1<<30}).stdout;
const F=raw.length/N, d=[0];
for(let f=1;f<F;f++){let s=0;for(let y=0;y<H;y++){ if(y>=38&&y<=52) continue; for(let x=0;x<W*3;x++){const i=y*W*3+x; s+=Math.abs(raw[f*N+i]-raw[(f-1)*N+i]);}} d.push(s/((H-15)*W*3)/255);}
fs.writeFileSync(`${process.env.S}/diff_${tag}.json`,JSON.stringify(d));
const med=a=>{const s=[...a].sort((x,y)=>x-y);return s[s.length>>1]};
const cuts=[];
for(let f=2;f<F-1;f++){const w=[...d.slice(Math.max(1,f-10),f),...d.slice(f+1,f+11)];const m=Math.max(med(w),0.004);
 if(d[f]>=0.05 && d[f]>=4*m && d[f]>=d[f-1] && d[f]>=d[f+1]) cuts.push({t:+(f/30).toFixed(2),d:+d[f].toFixed(3)});}
console.log(tag,F,'frames');console.log(JSON.stringify(cuts.map(c=>c.t)));
const starts=[0,...cuts.map(c=>c.t)],len=F/30,lens=starts.map((s,i)=>+((starts[i+1]??len)-s).toFixed(2));
const q=(v,p)=>{const s=[...v].sort((a,b)=>a-b),x=(s.length-1)*p,lo=Math.floor(x);return +(s[lo]+(s[Math.ceil(x)]-s[lo])*(x-lo)).toFixed(2)};
console.log(JSON.stringify({shots:lens.length,cutsPerMin:+(cuts.length/(len/60)).toFixed(1),median:q(lens,.5),p10:q(lens,.1),p90:q(lens,.9),mean:+(len/lens.length).toFixed(2),lens}));
