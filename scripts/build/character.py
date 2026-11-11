"""Draw the flat 'Cartoon Short' character as a transparent PNG (one image per expression).

Drawing grammar taken from the references (ANALYSIS.md section 6 + frames/v2_20.5.png), not their characters:
- head: big egg, slightly wider than tall, about 1.6 x the torso width, no neck; flat off-white, never shaded
- torso: a narrow bean (no shoulders, rounded bottom), solid outfit colour; identity = colour + one accessory
- face: short thick brows, small dot eyes or lid bars, a tiny filled mouth
- limbs: thin ink noodles; legs about half the body height, starting close together; hands = small white circles
- one uniform dark-navy ink outline

Usage: python character.py OUT_DIR   ->  <role>_<expression>.png, 1000 x 2000
"""
import math, os, sys
from PIL import Image, ImageDraw

SS = 4
W, H = 1000, 2000
INK = (26, 28, 46, 255)        # #1a1c2e
HEAD = (246, 243, 240, 255)    # paper white

# Original roles for our own stories. Hat / hair are single flat shapes; accessory is the identity.
ROLES = {
    'courier': dict(torso=(88, 112, 84, 255), hat=(196, 92, 46, 255), strap=(118, 78, 50, 255)),
}

OW = 20       # outline on the canvas: about 7 px on screen in a medium shot (head ~190 px)
LIMB = 30     # limb width on the canvas: about 11 px on screen


def s(v):
    return int(round(v * SS))


def bez(p0, p1, p2, n=32):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def stroke(d, pts, width, fill=INK):
    P = [(s(x), s(y)) for x, y in pts]
    d.line(P, fill=fill, width=s(width), joint='curve')
    r = s(width) / 2
    for p in (P[0], P[-1]):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def shape(d, pts, fill, ow=OW):
    P = [(s(x), s(y)) for x, y in pts]
    d.polygon(P, fill=fill)
    d.line(P + [P[0], P[1]], fill=INK, width=s(ow), joint='curve')


def egg(cx, cy, w, h, n=200, squash=0.06):
    """Rounded egg: a superellipse-ish oval, a little narrower at the chin."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, sn = math.cos(t), math.sin(t)
        e = 2.25   # >2 = a bit boxier than an ellipse, like the references' heads
        x = math.copysign(abs(c) ** (2 / e), c)
        y = math.copysign(abs(sn) ** (2 / e), sn)
        k = 1 - squash * max(y, 0)
        pts.append((cx + x * w / 2 * k, cy + y * h / 2))
    return pts


def bean(cx, top, bot, w_top, w_mid):
    """Torso: narrow at the top (under the head), widest low down, round bottom."""
    pts = []
    pts += bez((cx - w_top / 2, top), (cx - w_mid / 2 - 6, (top + bot) / 2), (cx - w_mid / 2 + 4, bot - 70), 20)
    pts += bez((cx - w_mid / 2 + 4, bot - 70), (cx - w_mid / 2 + 10, bot + 6), (cx, bot + 4), 16)[1:]
    pts += bez((cx, bot + 4), (cx + w_mid / 2 - 10, bot + 6), (cx + w_mid / 2 - 4, bot - 70), 16)[1:]
    pts += bez((cx + w_mid / 2 - 4, bot - 70), (cx + w_mid / 2 + 6, (top + bot) / 2), (cx + w_top / 2, top), 20)[1:]
    return pts


def hand(d, x, y, r=26):
    d.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)], fill=HEAD, outline=INK, width=s(OW * 0.7))


def draw(role='courier', expr='neutral'):
    R = ROLES[role]
    img = Image.new('RGBA', (s(W), s(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 500
    hw, hh = 560, 500                  # head wider than tall
    hcy = 330
    t_top, t_bot = hcy + hh / 2 - 60, 1060
    foot = H - 24

    # legs: start close together under the torso, long and straight-ish
    stroke(d, bez((cx - 44, t_bot - 30), (cx - 80, (t_bot + foot) / 2), (cx - 150, foot)), LIMB)
    stroke(d, bez((cx + 44, t_bot - 30), (cx + 84, (t_bot + foot) / 2), (cx + 155, foot)), LIMB)

    # back arm (picture right): hangs, hand at hip height
    stroke(d, bez((cx + 110, t_top + 90), (cx + 215, t_top + 300), (cx + 175, t_top + 470)), LIMB)
    hand(d, cx + 175, t_top + 470)

    # torso
    shape(d, bean(cx, t_top, t_bot, 250, 340), R['torso'])
    # accessory: shoulder-bag strap across the chest, bag at the hip (role identity)
    shape(d, [(cx - 118, t_top + 40), (cx - 86, t_top + 22), (cx + 168, t_bot - 150), (cx + 140, t_bot - 122)], R['strap'], OW * 0.5)
    bag = [(cx + 95, t_bot - 190), (cx + 255, t_bot - 190), (cx + 262, t_bot - 40), (cx + 88, t_bot - 40)]
    shape(d, bag, R['strap'])
    stroke(d, [(cx + 92, t_bot - 140), (cx + 258, t_bot - 140)], OW * 0.5)

    # front arm (picture left): bent, hand on the strap
    stroke(d, bez((cx - 110, t_top + 90), (cx - 235, t_top + 270), (cx - 95, t_top + 330)), LIMB)
    hand(d, cx - 95, t_top + 330)

    # head
    head = egg(cx, hcy, hw, hh)
    shape(d, head, HEAD)

    # hat: knitted beanie = the top of the head shape, slightly larger, one flat shape + a fold line
    band = hcy - 70
    big = egg(cx, hcy, hw + 26, hh + 26)
    cap = [p for p in big if p[1] < band]
    cap.sort(key=lambda p: math.atan2(p[1] - hcy, p[0] - cx))
    shape(d, cap, R['hat'])
    stroke(d, [(cx - hw / 2 + 4, band - 30), (cx + hw / 2 - 4, band - 30)], OW * 0.5)

    # face (brows thick and short, eyes small, mouth a tiny filled shape)
    ey = hcy + 20
    ex = 92
    if expr in ('neutral', 'tired'):
        stroke(d, [(cx - ex - 46, ey - 62), (cx - ex + 40, ey - 66)], 22)
        stroke(d, [(cx + ex - 40, ey - 64), (cx + ex + 46, ey - 70)], 22)
        if expr == 'neutral':
            for x in (cx - ex, cx + ex):
                d.ellipse([s(x - 17), s(ey - 20), s(x + 17), s(ey + 20)], fill=INK)
        else:   # lid bars: half-closed eyes
            for x in (cx - ex, cx + ex):
                d.chord([s(x - 30), s(ey - 22), s(x + 30), s(ey + 30)], 0, 180, fill=INK)
                stroke(d, [(x - 36, ey + 2), (x + 36, ey + 2)], 9)
        d.ellipse([s(cx - 28), s(ey + 92), s(cx + 28), s(ey + 112)], fill=INK)
    elif expr == 'shock':
        stroke(d, bez((cx - ex - 46, ey - 70), (cx - ex, ey - 100), (cx - ex + 40, ey - 84)), 20)
        stroke(d, bez((cx + ex - 40, ey - 84), (cx + ex, ey - 100), (cx + ex + 46, ey - 70)), 20)
        for x in (cx - ex, cx + ex):
            d.ellipse([s(x - 32), s(ey - 32), s(x + 32), s(ey + 32)], fill=HEAD, outline=INK, width=s(9))
            d.ellipse([s(x - 10), s(ey - 10), s(x + 10), s(ey + 10)], fill=INK)
        d.ellipse([s(cx - 34), s(ey + 70), s(cx + 34), s(ey + 150)], fill=INK)
    elif expr == 'happy':
        stroke(d, [(cx - ex - 46, ey - 74), (cx - ex + 40, ey - 80)], 20)
        stroke(d, [(cx + ex - 40, ey - 80), (cx + ex + 46, ey - 74)], 20)
        for x in (cx - ex, cx + ex):
            stroke(d, bez((x - 30, ey + 10), (x, ey - 34), (x + 30, ey + 10), 12), 11)
        d.chord([s(cx - 50), s(ey + 50), s(cx + 50), s(ey + 140)], 0, 180, fill=INK)

    return img.resize((W, H), Image.LANCZOS)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith('.png'):
            os.remove(os.path.join(out, f))
    for role in ROLES:
        for expr in ('neutral', 'tired', 'shock', 'happy'):
            p = os.path.join(out, f'{role}_{expr}.png')
            draw(role, expr).save(p)
            print(p)
