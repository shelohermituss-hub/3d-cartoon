"""Word timings for the narration (faster-whisper, word_timestamps), mapped onto the known script words.

Usage: python words.py VOICE.wav SCRIPT.txt OUT.json
"""
import json, re, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

wav, script, out = sys.argv[1:4]
model = WhisperModel('small', device='cpu', compute_type='int8')
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.float32)
segs, _ = model.transcribe(audio, language='fr', word_timestamps=True, beam_size=5)
heard = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]
words = re.findall(r"[\w'’\-]+[\s]*[:!?.,…]*", open(script, encoding='utf-8').read())
words = [w.strip() for w in words]
print('script', len(words), 'heard', len(heard))
import unicodedata


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if c.isalnum())


# greedy alignment: glue heard pieces until they spell the script word ("celui" + "-ci" = "celui-ci")
res, j = [], 0
for w in words:
    target = norm(w)
    t0 = heard[j][0] if j < len(heard) else res[-1]['t1']
    acc, t1 = '', t0
    while j < len(heard) and len(acc) < len(target):
        acc += norm(heard[j][2]); t1 = heard[j][1]; j += 1
    if acc != target:
        print('  (approximate match)', w, '<-', acc)
    res.append({'w': w, 't0': round(t0, 3), 't1': round(t1, 3)})
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
for r in res:
    print(f"{r['t0']:6.2f} {r['t1']:6.2f} {r['w']}")
