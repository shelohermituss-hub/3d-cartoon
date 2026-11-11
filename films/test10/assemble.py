"""Assemble the test film: frames (+ dissolves) -> 1080x1920 30 fps, post (glow, grade, vignette), captions, audio.

Sound effects are synthesised here from formulas (no third-party samples, so no rights question).
Mix: narration + effects + room tone, ffmpeg loudnorm to -14 LUFS integrated, true peak <= -1.5 dBFS, mono-like.

  python assemble.py FRAMES_DIR OUT.mp4
"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'build'))
import finish   # noqa: E402  (caption style + post filter chain)

FR, OUTV = sys.argv[1], sys.argv[2]
TL = json.load(open(os.path.join(FR, 'timeline.json')))
FPS, DUR, VO = TL['fps'], TL['dur'], TL['vo']
NF = int(FPS * DUR)
EV = TL['events']
SR = 48000

# ------------------------------------------------------------------ 1. frames: upscale, cross-dissolves
tmp = os.path.join(FR, 'full')
os.makedirs(tmp, exist_ok=True)
starts = {round(c * FPS): s for c, s in zip(TL['cuts'], TL['shots'])}
for f in range(NF):
    a = Image.open(os.path.join(FR, f'f{f:04d}.png')).convert('RGB')
    prev = os.path.join(FR, f'f{f:04d}_prev.png')
    if os.path.exists(prev):                     # dissolve: 2/3, 1/3, ... of the previous shot
        start = max(c for c in starts if c <= f)
        n = TL['dissolve'][starts[start]]
        w = (f - start + 1) / (n + 1)
        a = Image.blend(Image.open(prev).convert('RGB'), a, w)
    a.resize((1080, 1920), Image.LANCZOS).save(os.path.join(tmp, f'{f:04d}.png'))

# ------------------------------------------------------------------ 2. captions: 1-3 words, no gaps
words = json.load(open(os.path.join(HERE, 'words.json'), encoding='utf-8'))
chunks, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    end_punct = re.search(r'[.!?,:…]$', w['w'])
    nxt = words[i + 1]['w'] if i + 1 < len(words) else ''
    content = len(re.sub(r'[^\w]', '', w['w'])) >= 4          # chunk ends on a content word (ANALYSIS section 3)
    if end_punct or content or len(cur) == 2 or not nxt:
        chunks.append(cur); cur = []
cap = []
for j, c in enumerate(chunks):
    t0 = c[0]['t0'] + VO
    t1 = chunks[j + 1][0]['t0'] + VO if j + 1 < len(chunks) else DUR
    text = ' '.join(x['w'] for x in c).replace(' :', ' :').replace(' !', ' !')
    cap.append((t0 if j else 0.0, t1, text))       # first chunk from frame 0: no caption-less frame
ass = os.path.join(FR, 'captions.ass')
finish.write_ass(cap, ass)
print('captions:', [c[2] for c in cap])

# ------------------------------------------------------------------ 3. sound effects (synthesised)
n = int(DUR * SR)
fx = np.zeros(n, np.float32)
t = np.arange(n) / SR


def env_exp(dur, decay):
    k = np.arange(int(dur * SR)) / SR
    return np.exp(-k / decay)


def add(at, sig, gain):
    i = int(at * SR)
    j = min(n, i + len(sig))
    if i < n:
        fx[i:j] += gain * sig[:j - i]


def det_noise(m, seed):
    """Deterministic noise (fixed seed): same sound every run."""
    return np.random.default_rng(seed).standard_normal(m).astype(np.float32)


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x)).astype(np.float32)


def thud(seed, dur=0.12, lo=60, hi=500, decay=0.03):
    s = bandpass(det_noise(int(dur * SR), seed), lo, hi)
    return s / (np.abs(s).max() + 1e-9) * env_exp(dur, decay)


def metal(freqs, dur, decay, seed):
    k = np.arange(int(dur * SR)) / SR
    s = sum(math.exp(-i * 0.5) * np.sin(2 * np.pi * f * k + i) for i, f in enumerate(freqs))
    s = s / np.abs(s).max() * np.exp(-k / decay)
    return (s + 0.15 * thud(seed, dur, 200, 4000, decay * 0.2)).astype(np.float32)


# room tone of an alley: low brown noise
room = np.cumsum(det_noise(n, 1)) ; room -= np.convolve(room, np.ones(4800) / 4800, 'same')
fx += 0.015 * room / (np.abs(room).max() + 1e-9)
# the parcel shakes: cardboard taps at ~11 Hz
k = 0
tt = EV['bouge']
while tt < EV['walk0']:
    add(tt, thud(10 + k, 0.05, 300, 3000, 0.012), 0.35 * (0.6 + 0.4 * math.sin(k)))
    tt += 1 / 11 + 0.006 * math.sin(k * 1.7); k += 1
# footsteps (9-frame steps), put down
step = EV['walk0'] + 4 / FPS
while step < EV['walk1']:
    add(step, thud(40 + int(step * 100), 0.10, 50, 900, 0.03), 0.30); step += 9 / FPS
add(EV['put1'], thud(77, 0.16, 40, 700, 0.05), 0.45)
# lid rattles, then bangs open (whoosh + metal clang when it stops)
tt, k = EV['rattle'], 0
while tt < EV['open']:
    add(tt, metal([620, 930, 1410], 0.10, 0.03, 90 + k), 0.18); tt += 1 / 14; k += 1
sw = bandpass(det_noise(int(0.35 * SR), 5), 300, 2500) * np.sin(np.linspace(0, np.pi, int(0.35 * SR))) ** 2
add(EV['open'], sw / np.abs(sw).max(), 0.35)
add(EV['open'] + 0.36, metal([138, 231, 409, 688, 1033], 1.2, 0.35, 7), 0.9)
add(EV['open'] + 0.36, thud(8, 0.3, 40, 300, 0.08), 0.8)
# jump: rising whoosh; landing thud
m = int(0.3 * SR)
up = bandpass(det_noise(m, 9), 500, 4000) * np.linspace(0, 1, m) ** 2
add(EV['jump'], up / np.abs(up).max(), 0.3)
add(EV['jump'] + 0.42, thud(12, 0.12, 50, 600, 0.04), 0.5)
# running steps (6-frame steps), fading as he leaves
step, k = EV['run'] + 2 / FPS, 0
while step < EV['run'] + 1.5:
    add(step, thud(200 + k, 0.08, 60, 1200, 0.025), 0.35 * max(0.0, 1 - (step - EV['run']) / 1.6)); step += 6 / FPS; k += 1
fxw = os.path.join(FR, 'fx.wav')
import soundfile as sf  # noqa: E402
sf.write(fxw, fx, SR)

# ------------------------------------------------------------------ 4. mix + loudness
mix = os.path.join(FR, 'mix.wav')
pre = os.path.join(FR, 'pre.wav')
voice = os.path.join(HERE, 'voice_raw.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice, '-i', fxw, '-filter_complex',
                f'[0:a]aresample={SR},adelay={int(VO * 1000)},apad[v];[1:a]volume=0.8[f];'
                f'[v][f]amix=inputs=2:duration=shortest:normalize=0,atrim=0:{DUR},'
                'acompressor=threshold=-20dB:ratio=3:attack=5:release=80', '-ar', str(SR), '-ac', '1', pre], check=True)


def integrated(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])


# two steps: measure, then exact gain to -14 LUFS, then a limiter at -1.5 dBFS (true peak checked after)
gain = -14.0 - (integrated(pre) + 3.01)        # dual-mono stereo measures 3 dB louder than mono
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af',
                f'volume={gain:.2f}dB,alimiter=limit=0.80:level=false:attack=2:release=40,pan=stereo|c0=c0|c1=c0',
                '-ar', '48000', mix], check=True)
print('loudness after mix:', integrated(mix), 'LUFS')

# ------------------------------------------------------------------ 5. video: post chain + captions burned in
vf = finish.POST + f",ass={ass}:fontsdir={finish.FONTS},format=yuv420p"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(tmp, '%04d.png'), '-i', mix,
                '-vf', vf, '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUTV], check=True)
print('WROTE', OUTV)
