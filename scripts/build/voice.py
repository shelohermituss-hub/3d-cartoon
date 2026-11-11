"""Narration with Kokoro-82M (Apache-2.0, ONNX, CPU) - French voice ff_siwis.

Usage: python voice.py SCRIPT.txt OUT.wav [speed]
Pauses longer than 0.12 s are shortened (the references have no breaths, no pause of 0.2 s).
"""
import os, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
V = os.path.join(ROOT, 'assets', 'voice')


def tighten(x, sr, thr=0.012, keep=0.08):
    """Shorten every silence to `keep` seconds."""
    win = int(0.01 * sr)
    env = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same'))
    loud = env > thr
    out, i, n = [], 0, len(x)
    keep_n = int(keep * sr)
    while i < n:
        if loud[i]:
            j = i
            while j < n and loud[j]:
                j += 1
            out.append(x[i:j]); i = j
        else:
            j = i
            while j < n and not loud[j]:
                j += 1
            seg = x[i:j]
            if len(seg) > keep_n:
                h = keep_n // 2
                seg = np.concatenate([seg[:h], seg[-h:]])
            out.append(seg); i = j
    return np.concatenate(out)


if __name__ == '__main__':
    text = open(sys.argv[1], encoding='utf-8').read().strip()
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.2
    k = Kokoro(os.path.join(V, 'model.onnx'), os.path.join(V, 'voices.npz'))
    audio, sr = k.create(text, voice='ff_siwis', speed=speed, lang='fr-fr')
    audio = tighten(np.asarray(audio, np.float32), sr)
    sf.write(sys.argv[2], audio, sr)
    print(f'{len(audio) / sr:.2f} s at {sr} Hz, speed {speed}')
