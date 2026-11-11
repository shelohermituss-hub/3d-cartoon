"""Measure a frame the same way ANALYSIS.md section 4 measured the references.

mean luma (0-255), dark share (luma < 40), bright share (luma > 215), k-means palette (k = 8, seed 7)
on a 48 px wide thumbnail, plus share of 'saturated accent' pixels. The caption band (y 1290 - 1410)
is excluded so the caption does not count as scenery.

Usage: python measure.py IMG [IMG ...]
"""
import sys
import numpy as np
from PIL import Image


def kmeans(x, k=8, seed=7, it=30):
    rng = np.random.default_rng(seed)
    c = x[rng.choice(len(x), k, replace=False)]
    for _ in range(it):
        lab = ((x[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        c = np.array([x[lab == i].mean(0) if (lab == i).any() else c[i] for i in range(k)])
    return c, lab


def measure(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(float)
    a = np.concatenate([a[:1290], a[1410:]]) if a.shape[0] == 1920 else a
    luma = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    small = np.asarray(Image.fromarray(a.astype(np.uint8)).resize((48, int(48 * a.shape[0] / a.shape[1])))).reshape(-1, 3).astype(float)
    c, lab = kmeans(small)
    share = np.bincount(lab, minlength=8) / len(lab)
    order = share.argsort()[::-1]
    print(f'## {path}')
    print(f'mean luma {luma.mean():.0f}  dark<40 {100 * (luma < 40).mean():.1f} %  bright>215 {100 * (luma > 215).mean():.1f} %  '
          f'saturated (S>0.5, V>90) {100 * ((sat > 0.5) & (mx > 90)).mean():.1f} %')
    for i in order:
        r, g, b = c[i]
        print(f'  #{int(r):02x}{int(g):02x}{int(b):02x}  {100 * share[i]:.1f} %')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        measure(p)
