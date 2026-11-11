import { spawnSync } from 'node:child_process'; import fs from 'node:fs';
const [file,tag]=process.argv.slice(2);
// caption band y 1250..1450 full res, x 0..1080 ; downscale by 2 -> 540x100, gray
const W=540,H=100;
const raw=spawnSync('ffmpeg',['-v','error','-i',file,'-vf','crop=1080:200:0:1250,scale=540:100:flags=area,format=gray','-f','rawvideo','pipe:1'],{maxBuffer:1<<30}).stdout;
const F=raw.length/(W*H);
// white mask: >=245 ; text interior pure white
const mask=f=>{const m=new Uint8Array(W*H);for(let i=0;i<W*H;i++)m[i]=raw[f*W*H+i]>=248?1:0;return m;};
let prev=null,prevCnt=0;const rows=[];let lastBB=null;
const ev=[];const bbs=[];
for(let f=0;f<F;f++){const m=mask(f);let cnt=0,x0=W,x1=-1,y0=H,y1=-1;
 for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(m[y*W+x]){cnt++;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}
 let diff=0;if(prev){for(let i=0;i<W*H;i++)diff+=m[i]^prev[i];}
 bbs.push(cnt>150?{x0:x0*2,x1:x1*2,y0:y0*2+1250,y1:y1*2+1250,cnt}:null);
 ev.push({f,cnt,diff});prev=m;}
// caption on-frames
const on=bbs.map(b=>!!b);const onShare=on.filter(Boolean).length/F;
// word change events: diff large vs cnt, with cnt>150 after, rising edges and big diffs
const ch=[];for(let f=1;f<F;f++){const e=ev[f];if(e.cnt>150&&e.diff>0.5*Math.max(e.cnt,ev[f-1].cnt)&&(ch.length===0||f/30-ch.at(-1)>0.12))ch.push(+(f/30).toFixed(2));}
const dur=F/30;const gaps=ch.slice(1).map((t,i)=>t-ch[i]).sort((a,b)=>a-b);
const med=gaps[gaps.length>>1];
const valid=bbs.filter(Boolean);const avg=k=>Math.round(valid.reduce((a,b)=>a+b[k],0)/valid.length);
const widths=valid.map(b=>b.x1-b.x0).sort((a,b)=>a-b);
console.log(tag,JSON.stringify({frames:F,captionOnShare:+onShare.toFixed(3),captionChanges:ch.length,perMin:+(ch.length/(dur/60)).toFixed(0),medianGapS:med,gapP10:gaps[Math.floor(gaps.length*.1)],gapP90:gaps[Math.floor(gaps.length*.9)],avgY0:avg('y0'),avgY1:avg('y1'),avgCenterX:Math.round(valid.reduce((a,b)=>a+(b.x0+b.x1)/2,0)/valid.length),widthMed:widths[widths.length>>1],widthMax:widths.at(-1)}));
fs.writeFileSync(`${process.env.S}/capchg_${tag}.json`,JSON.stringify(ch));
