"""Character kit for "3D Cartoon Shorts (NEW)" (docs/STYLE_NEW.md, sections 1, 2 and 5).

One character = one JSON description file (characters/*.json). This module turns a description +
a face (eyes / brows / mouth or an expr preset) + a view (front / 3q) + a light (from the set, as data)
into a transparent PNG. Deterministic: same inputs -> same pixels (no randomness, no state).

Units: 1 unit = the head's width (D px on the canvas). Builds, legLen, armLen are in units.

  python charkit.py sheet characters/theo.json OUT.png     # front + 3/4, several faces, flat + shaded
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw

# ------------------------------------------------------------------ constants
SS = int(os.environ.get('CHAR_SS', '3'))   # supersampling
D = 400                     # head width on the canvas (px) = 1 unit
CW, CH = 1100, 1700         # canvas
INK = '#1a1c2e'
HEAD = '#f6f4f1'
OW = 0.045                  # outline width, in units (thick ink)
LIMB = 0.068                # limb width, in units

BUILDS = {  # width, height (units) - values of the engine (section 1)
    'slim': (0.64, 0.90), 'medium': (0.80, 0.92), 'stout': (0.96, 0.95), 'egg': (0.94, 0.98),
    'pill': (0.87, 1.00), 'curvy': (0.82, 0.94), 'kid': (0.64, 0.56)}
DEFAULTS = {'shirt': '#e9e6df', 'trousers': '#2e3142', 'hair': '#3b2a22', 'hat': '#4a4f63', 'eyes': INK}

EXPR = {  # presets: eyes, brows, mouth
    'neutral': ('open', 'on', 'rest'), 'fear': ('wide', 'worried', 'tight'), 'terror': ('wide', 'up', 'wide'),
    'dread': ('half', 'worried', 'flat'), 'gulp': ('wide', 'worried', 'gulp'), 'confused': ('open', 'quizzical', 'smirk'),
    'relief': ('arc', 'up', 'smile'), 'hope': ('open', 'worried', 'smile'), 'dawning': ('wide', 'up', 'o'),
    'horror': ('pinpoint', 'up', 'wide'), 'stare': ('stare', 'off', 'flat'), 'blank': ('open', 'on', 'flat'),
    'smug': ('smug', 'down', 'smirk'), 'angry': ('angry', 'knit', 'grid'), 'happy': ('arc', 'on', 'crescent'),
    'sad': ('sad', 'worried', 'frown'), 'shout': ('wide', 'up', 'D'), 'pain': ('wince', 'knit', 'grid')}


def col(v, default):
    """6-digit hex or the default (a wrong value falls back, section 1)."""
    if isinstance(v, str) and len(v) == 7 and v[0] == '#':
        try:
            int(v[1:], 16)
            return v
        except ValueError:
            pass
    return default


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def darker(h, k=0.75):
    r, g, b = rgb(h)
    return '#%02x%02x%02x' % (int(r * k), int(g * k), int(b * k))


# ------------------------------------------------------------------ drawing helpers (canvas px -> supersampled)
class Pen:
    def __init__(self):
        self.img = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        # region masks for the shading pass
        self.masks = {k: Image.new('L', (CW * SS, CH * SS), 0) for k in ('head', 'torso', 'legs', 'hat')}
        self.md = {k: ImageDraw.Draw(v) for k, v in self.masks.items()}

    @staticmethod
    def P(pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, fill, ow=OW, mask=None, ink=True):
        P = self.P(pts)
        if fill:
            self.d.polygon(P, fill=fill)
        if ink and ow:
            self.d.line(P + [P[0], P[1]], fill=INK, width=max(1, int(ow * D * SS)), joint='curve')
        if mask:
            self.md[mask].polygon(P, fill=255)

    def line(self, pts, w, fill=INK, cap=True, mask=None):
        P = self.P(pts)
        W = max(1, int(w * D * SS))
        self.d.line(P, fill=fill, width=W, joint='curve')
        if mask:
            self.md[mask].line(P, fill=255, width=W, joint='curve')
        if cap:
            r = W / 2
            for p in (P[0], P[-1]):
                self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)
                if mask:
                    self.md[mask].ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)

    def ellipse(self, cx, cy, rx, ry, fill, ow=0.0, outline=INK, mask=None):
        box = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        self.d.ellipse(box, fill=fill, outline=outline if ow else None, width=int(ow * D * SS) if ow else 0)
        if mask:
            self.md[mask].ellipse(box, fill=255)

    def chord(self, cx, cy, rx, ry, a0, a1, fill):
        self.d.chord([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], a0, a1, fill=fill)

    def arc(self, cx, cy, rx, ry, a0, a1, w):
        self.d.arc([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], a0, a1, fill=INK,
                   width=max(1, int(w * D * SS)))


def bez(p0, p1, p2, n=28):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def superellipse(cx, cy, rx, ry, e=2.2, n=160, y0=None, y1=None):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = cx + math.copysign(abs(c) ** (2 / e), c) * rx
        y = cy + math.copysign(abs(s) ** (2 / e), s) * ry
        pts.append((x, y))
    return pts


def egg(cx, top, bot, w, kind):
    """Torso outline. Widest low for egg/stout/curvy, straight for pill/slim."""
    h = bot - top
    pts = []
    n = 90
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)   # s>0 lower half
        if kind == 'pill':
            e = 3.2
        elif kind in ('slim', 'kid'):
            e = 2.6
        else:
            e = 2.3
        x = math.copysign(abs(c) ** (2 / e), c)
        y = math.copysign(abs(s) ** (2 / e), s)
        k = 1.0 if kind == 'pill' else (0.84 + 0.16 * (y + 1) / 2)   # narrower at the top
        if kind == 'curvy':
            k *= 1 - 0.10 * math.exp(-((y + 0.15) / 0.25) ** 2)        # a waist
        pts.append((cx + x * w / 2 * k, top + h / 2 + y * h / 2))
    return pts


# ------------------------------------------------------------------ the character
class Character:
    def __init__(self, desc):
        self.d = desc
        b = desc.get('torso', {}).get('body', {}).get('build', 'medium')
        self.build = b if b in BUILDS else 'medium'
        self.tw, self.th = BUILDS[self.build]
        lim = desc.get('limbs', {})
        kid = self.build == 'kid'
        self.leg = float(lim.get('legLen', 0.72 if kid else 1.3))
        self.arm = float(lim.get('armLen', 0.62 if kid else 0.95))
        self.face = desc.get('face', {})

    # layout in canvas px, feet at the bottom
    def layout(self):
        cx = CW / 2
        foot = CH - 30
        hip = foot - self.leg * D
        tb = hip + 0.06 * D
        tt = tb - self.th * D
        hh = 0.94 * D
        hcy = tt + 0.10 * D - hh / 2
        return cx, foot, hip, tb, tt, hcy, hh

    def draw(self, face=None, view='front', light=None, pose='rest'):
        """pose: a name ('rest', 'carry', ...) or a dict: arms, legs ('stand'|'walk'|'run'|'tuck'), phase (0-1 per
        full stride cycle), dir (+1 = moving to picture right), fx (['speed', 'sweat']), lean (degrees, + = back)."""
        P = {'arms': pose, 'legs': 'stand', 'phase': 0.0, 'dir': 1, 'fx': [], 'lean': 0.0}
        if isinstance(pose, dict):
            P.update(pose)
        self.P = P
        pen = Pen()
        cx, foot, hip, tb, tt, hcy, hh = self.layout()
        fx = 0.16 * D if view == '3q' else 0.0          # face / chest details shift in 3/4
        squeeze = 0.9 if view == '3q' else 1.0
        tw = self.tw * D * squeeze
        out = self.d.get('outfit', {})
        layers = out.get('layers', [])
        base_col = col(layers[0].get('color'), DEFAULTS['shirt']) if layers else DEFAULTS['shirt']
        trousers = col(out.get('trousers'), DEFAULTS['trousers'])

        # back hair (behind head): bob / long / ponytail / pigtails
        hair = self.d.get('hair', {}) or {}
        hstyle = hair.get('style', 'short')
        hcol = col(hair.get('color'), DEFAULTS['hair'])
        hat = (self.d.get('hat') or {}).get('kind', 'none')
        if hat != 'none' and hstyle not in ('bald', 'bald_sides', 'receding'):
            hstyle = 'short'                                # under a hat: short hair
        if hstyle in ('bob', 'long'):
            bot = hcy + (0.18 if hstyle == 'bob' else 0.75) * D
            pts = superellipse(cx, hcy - 0.03 * D, 0.56 * D, 0.52 * D, 2.4)
            pts = [(x, min(y, bot)) if y > hcy else (x, y) for x, y in pts]
            if hstyle == 'long':
                pts = [(x, y + (0.55 * D if y > hcy - 0.02 * D else 0)) for x, y in pts]
            pen.poly(pts, hcol, mask='head')
        if hstyle == 'ponytail':
            pen.poly(bez((cx + 0.40 * D, hcy - 0.25 * D), (cx + 0.75 * D, hcy), (cx + 0.55 * D, hcy + 0.45 * D))
                     + bez((cx + 0.45 * D, hcy + 0.40 * D), (cx + 0.55 * D, hcy + 0.05 * D), (cx + 0.32 * D, hcy - 0.15 * D)),
                     hcol, mask='head')
        if hstyle == 'pigtails':
            for sx in (-1, 1):
                pen.ellipse(cx + sx * 0.56 * D, hcy + 0.12 * D, 0.13 * D, 0.2 * D, hcol, OW, mask='head')

        # skirt / coat tails behind the legs
        skirt = out.get('skirt')
        coat = next((l for l in layers if l.get('kind') == 'coat'), None)
        legs_visible_from = hip
        if coat:
            ccol = col(coat.get('color'), '#5a4a3a')
            y2 = hip + 0.45 * self.leg * D
            pen.poly([(cx - tw * 0.48, tb - 0.2 * D), (cx + tw * 0.48, tb - 0.2 * D), (cx + tw * 0.56, y2),
                      (cx + 0.03 * D, y2), (cx, y2 - 0.05 * D), (cx - 0.03 * D, y2), (cx - tw * 0.56, y2)], ccol, mask='torso')

        # legs: ink sticks from the hips (stand / walk / run / tuck), section 3 'Marche'
        self.legs(pen, cx, hip, foot)
        if skirt:
            length = skirt.get('length', 'knee')
            y2 = hip + (0.5 if length == 'knee' else 0.92) * self.leg * D
            flare = 0.62 if skirt.get('shape', 'flared') == 'flared' else 0.5
            scol = col(skirt.get('color'), '#7a3b4a')
            pts = [(cx - tw * 0.42, tb - 0.15 * D)] + bez((cx - tw * flare, (tb + y2) / 2), (cx - tw * flare * 1.05, y2), (cx, y2 + 0.04 * D), 12)
            pts = [(cx - tw * 0.42, tb - 0.15 * D), (cx - tw * flare, y2), (cx, y2 + 0.03 * D), (cx + tw * flare, y2), (cx + tw * 0.42, tb - 0.15 * D)]
            pen.poly(pts, scol, mask='torso')

        # back arm
        self.arm_stroke(pen, cx, tt, tw, +1, P['arms'])

        # torso: base garment
        T = egg(cx, tt, tb, tw, self.build)
        pen.poly(T, base_col, mask='torso')
        # trousers band at the pelvis (clipped to the torso shape)
        band_top = tb - 0.20 * self.th * D
        band = [(x, max(y, band_top)) for x, y in T if y > band_top - 1]
        if not skirt:
            pen.poly([(x, y) for x, y in T if y >= band_top] + [(min(x for x, _ in T), band_top)], trousers, ow=0, ink=False)
            pen.poly(T, None)                               # redraw outline over the band
        self.garments(pen, layers, cx + fx * 0.6, tt, tb, tw, T, band_top)

        # front arm
        self.arm_stroke(pen, cx, tt, tw, -1, P['arms'])

        # head
        H = superellipse(cx, hcy, 0.5 * D, hh / 2, 2.15)
        pen.poly(H, HEAD, mask='head')
        self.hair_front(pen, hstyle, hcol, cx, hcy, hh, fx)
        self.facial_hair(pen, cx + fx, hcy)
        self.draw_face(pen, face or 'neutral', cx + fx, hcy, view)
        self.glasses(pen, cx + fx, hcy)
        self.hat(pen, hat, cx, hcy, hh, fx)
        self.effects(pen, cx, hcy, hh)

        img = pen.img
        if light:
            img = shade(img, {k: v for k, v in pen.masks.items()}, light, (cx, hcy, tt, tb, hip))
        img = img.resize((CW, CH), Image.LANCZOS)
        if P['lean']:
            img = img.rotate(P['lean'] * P['dir'], resample=Image.BICUBIC, center=(cx, foot))
        return img

    # ---------------------------------------------------------------- legs
    def legs(self, pen, cx, hip, foot):
        P = self.P
        spread = 0.20 if self.build != 'kid' else 0.14
        k = self.leg / 1.3
        ph = 2 * math.pi * P['phase']
        dr = P['dir']
        for i, sx in enumerate((-1, 1)):
            hx, hy = cx + sx * 0.10 * D, hip - 0.04 * D
            if P['legs'] in ('walk', 'run'):
                a = math.sin(ph + (math.pi if i else 0.0))            # -1..1: back .. front
                amp, lift = (0.30, 0.10) if P['legs'] == 'walk' else (0.55, 0.26)
                fxp = cx + sx * 0.05 * D + dr * a * amp * k * D
                fy = foot - max(0.0, math.cos(ph + (math.pi if i else 0.0))) * lift * k * D
                knee = ((hx + fxp) / 2 + dr * (0.10 if P['legs'] == 'run' else 0.04) * D, (hy + fy) / 2)
                pts = bez((hx, hy), knee, (fxp, fy))
            elif P['legs'] == 'tuck':                                # jump: knees up and out
                fy = foot - 0.30 * k * D
                pts = bez((hx, hy), (hx + sx * 0.30 * D, (hy + fy) / 2), (hx + sx * 0.10 * D, fy))
            else:
                pts = bez((hx, hy), (cx + sx * 0.14 * D, (hip + foot) / 2), (cx + sx * spread * D, foot))
            pen.line(pts, LIMB, mask='legs')

    # ---------------------------------------------------------------- flat 2D effects (section 6 of ANALYSIS: speed lines, sweat)
    def effects(self, pen, cx, hcy, hh):
        fx = self.P.get('fx') or []
        if 'speed' in fx:
            for j in range(8):
                a = math.radians(-160 + j * 20)          # a fan above and around the head
                r0, r1 = 0.66 * D, (0.95 + 0.08 * (j % 2)) * D
                p0 = (cx + math.cos(a) * r0, hcy + math.sin(a) * r0 * 0.95)
                p1 = (cx + math.cos(a) * r1, hcy + math.sin(a) * r1 * 0.95)
                pen.line([p0, p1], 0.05)
                pen.line([p0, p1], 0.022, fill='#ffffff')
        if 'sweat' in fx:
            for (dx, dy, s) in ((0.52, -0.18, 1.0), (-0.56, -0.05, 0.8)):
                x, y = cx + dx * D, hcy + dy * D
                r = 0.06 * D * s
                drop = [(x, y - 2.2 * r)] + [(x + math.cos(a) * r, y + math.sin(a) * r)
                                            for a in [math.radians(v) for v in range(-30, 211, 15)]]
                pen.poly(drop, '#bfe4ff', OW * 0.45)
                pen.ellipse(x - r * 0.3, y - r * 0.2, r * 0.22, r * 0.22, '#ffffff')

    # ---------------------------------------------------------------- arms
    def arm_stroke(self, pen, cx, tt, tw, side, pose):
        """side +1 = picture-right arm (drawn behind the torso), -1 = picture-left (in front)."""
        sx = cx + side * (tw * 0.40)
        sy = tt + 0.14 * D
        L = self.arm * D
        P = self.P
        ph = 2 * math.pi * P.get('phase', 0.0)

        def hand(x, y):
            pen.ellipse(x, y, 0.075 * D, 0.075 * D, HEAD, OW * 0.65)

        if pose == 'akimbo':
            pen.line([(sx, sy), (sx + side * 0.32 * D, sy + 0.32 * D), (sx + side * 0.05 * D, sy + 0.62 * D)], LIMB)
            return
        if pose == 'wave' and side == -1:
            pts = bez((sx, sy), (sx - 0.45 * D, sy - 0.05 * D), (sx - 0.35 * D, sy - 0.6 * D))
            pen.line(pts, LIMB); hand(*pts[-1]); return
        if pose == 'carry':          # both hands on the sides of a box held at chest height
            end = (cx + side * 0.50 * D, sy + 0.42 * D)
            pts = bez((sx, sy), (sx + side * 0.30 * D, sy + 0.30 * D), end)
            pen.line(pts, LIMB); hand(*end); return
        if pose == 'down':           # put_down: arms reach low and forward
            end = (cx + side * 0.46 * D, sy + L * 1.05)
            pts = bez((sx, sy), (sx + side * 0.32 * D, sy + L * 0.5), end)
            pen.line(pts, LIMB); hand(*end); return
        if pose == 'up':             # shock: arms thrown up
            end = (cx + side * 0.78 * D, sy - 0.55 * D)
            pts = bez((sx, sy), (sx + side * 0.55 * D, sy + 0.05 * D), end)
            pen.line(pts, LIMB); hand(*end); return
        if pose in ('swing', 'run'):  # arms swing opposite to the legs
            a = math.sin(ph + (0.0 if side < 0 else math.pi))
            amp = 0.18 if pose == 'swing' else 0.34
            if pose == 'run':
                end = (sx + side * 0.10 * D + P['dir'] * a * amp * D, sy + L * 0.55)
                elbow = (sx + side * 0.28 * D - P['dir'] * a * 0.1 * D, sy + L * 0.42)
            else:
                end = (sx + side * 0.13 * D + P['dir'] * a * amp * D, sy + L)
                elbow = (sx + side * 0.22 * D, sy + L * 0.5)
            pen.line(bez((sx, sy), elbow, end), LIMB); hand(*end); return
        end = (sx + side * 0.13 * D, sy + L)
        pen.line(bez((sx, sy), (sx + side * 0.22 * D, sy + L * 0.5), end), LIMB)
        hand(*end)

    # ---------------------------------------------------------------- clothes
    def garments(self, pen, layers, cx, tt, tb, tw, T, band_top):
        h = tb - tt
        neck_y = tt + 0.04 * D
        for i, l in enumerate(layers):
            k = l.get('kind')
            c = col(l.get('color'), '#6b6f80')
            pattern = l.get('pattern')
            if i == 0 and k in ('shirt', 'blouse'):
                # collar: two small triangles
                for sx in (-1, 1):
                    pen.poly([(cx, neck_y + 0.02 * D), (cx + sx * 0.16 * D, neck_y - 0.02 * D), (cx + sx * 0.10 * D, neck_y + 0.12 * D)], c, OW * 0.5)
            if k == 'sweater' and i > 0:
                pen.poly(T, c)
                pen.line([(cx - tw * 0.45, band_top - 0.04 * D), (cx + tw * 0.45, band_top - 0.04 * D)], 0.016)
            if k == 'vest':
                pts = [(x, y) for x, y in T if y < band_top + 0.02 * D]
                pen.poly(pts, c, OW * 0.6)
                pen.poly([(cx, neck_y), (cx - 0.10 * D, neck_y), (cx, tt + h * 0.45), (cx + 0.10 * D, neck_y)], col(layers[0].get('color'), DEFAULTS['shirt']), OW * 0.4)
            if k in ('jacket', 'coat', 'cardigan'):
                for sx in (-1, 1):
                    half = [(x, y) for x, y in T if (x - cx) * sx >= 0.06 * D]
                    half.sort(key=lambda p: p[1])
                    edge = cx + sx * 0.06 * D
                    pts = [(edge, tt + 0.02 * D)] + sorted(half, key=lambda p: (p[1] if sx > 0 else p[1]))
                    pts = [(edge, tt + 0.02 * D)] + [p for p in half if p[1] <= tb] + [(edge, tb)]
                    pts = [pts[0]] + sorted(pts[1:-1], key=lambda p: p[1]) + [pts[-1]]
                    pen.poly(pts, c, OW * 0.6)
                    # lapel
                    pen.line([(edge, neck_y + 0.03 * D), (cx + sx * 0.17 * D, tt + 0.20 * D), (edge, tt + h * 0.42)], 0.016, cap=False)
            if k in ('jacket', 'coat') and pattern == 'tweed':
                pass
            if k == 'tie':
                pen.poly([(cx - 0.035 * D, neck_y + 0.04 * D), (cx + 0.035 * D, neck_y + 0.04 * D), (cx + 0.06 * D, tt + h * 0.58),
                          (cx, tt + h * 0.66), (cx - 0.06 * D, tt + h * 0.58)], c, OW * 0.5)
                if pattern == 'stripes':
                    for j in range(3):
                        y = tt + h * (0.25 + 0.12 * j)
                        pen.line([(cx - 0.04 * D, y), (cx + 0.04 * D, y + 0.03 * D)], 0.012, fill=darker(c, 0.6), cap=False)
            if k == 'bowtie':
                for sx in (-1, 1):
                    pen.poly([(cx, neck_y + 0.06 * D), (cx + sx * 0.11 * D, neck_y + 0.0 * D), (cx + sx * 0.11 * D, neck_y + 0.12 * D)], c, OW * 0.5)
                pen.ellipse(cx, neck_y + 0.06 * D, 0.03 * D, 0.03 * D, c, OW * 0.4)
            if k == 'scarf':
                pen.poly(superellipse(cx, neck_y + 0.03 * D, tw * 0.42, 0.075 * D, 3), c, OW * 0.55)
                pen.poly([(cx + 0.06 * D, neck_y + 0.06 * D), (cx + 0.17 * D, neck_y + 0.06 * D), (cx + 0.19 * D, tt + h * 0.55),
                          (cx + 0.08 * D, tt + h * 0.57)], c, OW * 0.55)
                if pattern == 'tartan':
                    for j in range(3):
                        y = neck_y + 0.15 * D + j * 0.09 * D
                        pen.line([(cx + 0.08 * D, y), (cx + 0.18 * D, y)], 0.012, fill=darker(c, 0.65), cap=False)
            if k == 'belt':
                pen.poly([(cx - tw * 0.47, band_top - 0.035 * D), (cx + tw * 0.47, band_top - 0.035 * D),
                          (cx + tw * 0.47, band_top + 0.02 * D), (cx - tw * 0.47, band_top + 0.02 * D)], c, OW * 0.4)
                pen.poly([(cx - 0.04 * D, band_top - 0.045 * D), (cx + 0.04 * D, band_top - 0.045 * D),
                          (cx + 0.04 * D, band_top + 0.03 * D), (cx - 0.04 * D, band_top + 0.03 * D)], '#c9a54a', OW * 0.35)
            if k == 'buttons':
                for j in range(3):
                    pen.ellipse(cx, tt + h * (0.32 + 0.16 * j), 0.018 * D, 0.018 * D, c)
            if k == 'placket':
                pen.line([(cx, neck_y + 0.08 * D), (cx, band_top - 0.04 * D)], 0.012, cap=False)
            if k == 'pocket':
                px = cx - tw * 0.26
                pen.poly([(px - 0.07 * D, tt + h * 0.30), (px + 0.07 * D, tt + h * 0.30), (px + 0.07 * D, tt + h * 0.44),
                          (px - 0.07 * D, tt + h * 0.44)], c, OW * 0.35)
            if k == 'suspenders':
                for sx in (-1, 1):
                    pen.poly([(cx + sx * 0.12 * D, tt + 0.02 * D), (cx + sx * 0.17 * D, tt + 0.02 * D), (cx + sx * 0.17 * D, band_top),
                              (cx + sx * 0.12 * D, band_top)], c, OW * 0.35)
            if k == 'apron':
                pen.poly([(cx - tw * 0.32, tt + h * 0.30), (cx + tw * 0.32, tt + h * 0.30), (cx + tw * 0.38, tb + 0.25 * D),
                          (cx - tw * 0.38, tb + 0.25 * D)], c, OW * 0.5)
                pen.line([(cx - tw * 0.30, tt + h * 0.30), (cx - 0.08 * D, neck_y)], 0.015, cap=False)
                pen.line([(cx + tw * 0.30, tt + h * 0.30), (cx + 0.08 * D, neck_y)], 0.015, cap=False)
            if k == 'bag_strap':     # role accessory: shoulder bag
                pen.poly([(cx - tw * 0.40, tt + 0.03 * D), (cx - tw * 0.30, tt), (cx + tw * 0.48, tb - 0.30 * D),
                          (cx + tw * 0.40, tb - 0.24 * D)], c, OW * 0.4)
                pen.poly([(cx + tw * 0.32, tb - 0.36 * D), (cx + tw * 0.72, tb - 0.36 * D), (cx + tw * 0.74, tb - 0.04 * D),
                          (cx + tw * 0.30, tb - 0.04 * D)], c, OW * 0.6)
                pen.line([(cx + tw * 0.31, tb - 0.26 * D), (cx + tw * 0.73, tb - 0.26 * D)], 0.014, cap=False)
            if pattern == 'dots' and k in ('shirt', 'blouse', 'sweater'):
                for j in range(12):
                    px = cx + ((j * 37) % 7 - 3) * tw * 0.11
                    py = tt + h * (0.25 + (j * 53 % 9) * 0.06)
                    pen.ellipse(px, py, 0.015 * D, 0.015 * D, darker(c, 0.8))
            if pattern == 'stripes' and k in ('shirt', 'sweater'):
                for j in range(4):
                    y = tt + h * (0.32 + 0.12 * j)
                    pen.line([(cx - tw * 0.42, y), (cx + tw * 0.42, y)], 0.02, fill=darker(c, 0.82), cap=False)

    # ---------------------------------------------------------------- hair, hats, face parts
    def hair_front(self, pen, style, c, cx, hcy, hh, fx):
        top = hcy - hh / 2
        if style in ('bald',):
            return
        if style in ('bald_sides', 'receding'):
            big = superellipse(cx, hcy, 0.53 * D, hh / 2 + 0.03 * D, 2.15, 240)
            for a0, a1 in ((math.radians(195), math.radians(232)), (math.radians(308), math.radians(345))):
                seg = []
                for x, y in big:
                    a = math.atan2(y - hcy, x - cx) % (2 * math.pi)
                    if a0 <= a <= a1:
                        seg.append((a, x, y))
                seg.sort()
                outer = [(x, y) for _, x, y in seg]
                inner = [(cx + (x - cx) * 0.80, hcy + (y - hcy) * 0.86) for x, y in reversed(outer)]
                pen.poly(outer + inner, c, OW * 0.5, mask='head')
            if style == 'receding':
                pen.poly(superellipse(cx - 0.04 * D, top + 0.07 * D, 0.13 * D, 0.045 * D, 2.2), c, OW * 0.5, mask='head')
            return
        # a cap of hair = the top of the head, slightly larger, cut by a hairline
        line_y = hcy - (0.20 if style not in ('messy', 'spiky', 'curly') else 0.16) * D
        big = superellipse(cx, hcy, 0.53 * D, hh / 2 + 0.03 * D, 2.15, 200)
        cap = [p for p in big if p[1] < line_y]
        cap.sort(key=lambda p: math.atan2(p[1] - hcy, p[0] - cx))
        if style == 'side_part':
            cap = cap + [(cx - 0.40 * D + fx, line_y + 0.06 * D)]
        if style in ('bob', 'long'):
            cap = cap + [(cx + 0.30 * D, line_y), (cx - 0.20 * D + fx, line_y + 0.10 * D)]
        pen.poly(cap, c, mask='head')
        if style == 'side_part':
            pen.line([(cx - 0.18 * D + fx, top + 0.02 * D), (cx - 0.14 * D + fx, line_y - 0.02 * D)], 0.014, cap=False)
        if style == 'curly':
            for j in range(9):
                a = math.pi * (1.05 + 0.9 * j / 8)
                pen.ellipse(cx + math.cos(a) * 0.48 * D, hcy + math.sin(a) * (hh / 2) * 0.98, 0.09 * D, 0.09 * D, c, OW * 0.5)
        if style in ('spiky', 'messy'):
            n = 7 if style == 'spiky' else 5
            for j in range(n):
                a = math.pi * (1.1 + 0.8 * j / (n - 1))
                bx, by = cx + math.cos(a) * 0.46 * D, hcy + math.sin(a) * hh / 2
                tip = (cx + math.cos(a) * 0.62 * D, hcy + math.sin(a) * hh * 0.66)
                pen.poly([(bx - 0.06 * D, by + 0.02 * D), tip, (bx + 0.06 * D, by + 0.02 * D)], c, OW * 0.5)
        if style == 'bun':
            pen.ellipse(cx, top - 0.06 * D, 0.13 * D, 0.11 * D, c, OW * 0.6)

    def hat(self, pen, kind, cx, hcy, hh, fx):
        if kind == 'none':
            return
        c = col((self.d.get('hat') or {}).get('color'), DEFAULTS['hat'])
        top = hcy - hh / 2
        if kind == 'beanie':
            band = hcy - 0.20 * D
            big = superellipse(cx, hcy + 0.01 * D, 0.535 * D, hh / 2 + 0.04 * D, 2.15, 200)
            cap = sorted([p for p in big if p[1] < band], key=lambda p: math.atan2(p[1] - hcy, p[0] - cx))
            pen.poly(cap, c, mask='hat')
            pen.line([(cx - 0.50 * D, band - 0.07 * D), (cx + 0.50 * D, band - 0.07 * D)], 0.016, cap=False)
            if (self.d.get('hat') or {}).get('pompom', True):
                pen.ellipse(cx, top - 0.05 * D, 0.075 * D, 0.07 * D, c, OW * 0.6, mask='hat')
        elif kind == 'ballcap':
            big = superellipse(cx, hcy, 0.53 * D, hh / 2 + 0.03 * D, 2.15, 200)
            cap = sorted([p for p in big if p[1] < hcy - 0.17 * D], key=lambda p: math.atan2(p[1] - hcy, p[0] - cx))
            pen.poly(cap, c, mask='hat')
            pen.poly(superellipse(cx + 0.30 * D + fx * 0.5, hcy - 0.18 * D, 0.30 * D, 0.05 * D, 2.0), darker(c, 0.85), OW * 0.6, mask='hat')
        elif kind in ('flatcap', 'officer'):
            pen.poly([(cx - 0.52 * D, hcy - 0.16 * D), (cx - 0.46 * D, top - 0.04 * D), (cx + 0.40 * D, top - 0.08 * D),
                      (cx + 0.56 * D, hcy - 0.20 * D)], c, mask='hat')
            pen.poly(superellipse(cx + 0.18 * D, hcy - 0.16 * D, 0.36 * D, 0.045 * D, 2), INK if kind == 'officer' else darker(c), OW * 0.5, mask='hat')
        elif kind in ('bowler', 'tophat'):
            hgt = 0.30 if kind == 'bowler' else 0.62
            if kind == 'bowler':
                dome = superellipse(cx, hcy - 0.30 * D, 0.40 * D, 0.30 * D, 2.0)
                dome = [p for p in dome if p[1] < hcy - 0.18 * D]
                dome.sort(key=lambda p: math.atan2(p[1] - (hcy - 0.3 * D), p[0] - cx))
                pen.poly(dome, c, mask='hat')
            else:
                pen.poly([(cx - 0.34 * D, hcy - 0.20 * D), (cx - 0.31 * D, top - hgt * D * 0.5), (cx + 0.31 * D, top - hgt * D * 0.5),
                          (cx + 0.34 * D, hcy - 0.20 * D)], c, mask='hat')
            pen.poly(superellipse(cx, hcy - 0.19 * D, 0.56 * D, 0.05 * D, 2), c, OW * 0.6, mask='hat')
        elif kind == 'headband':
            pen.poly([(cx - 0.50 * D, hcy - 0.26 * D), (cx + 0.50 * D, hcy - 0.26 * D), (cx + 0.50 * D, hcy - 0.18 * D),
                      (cx - 0.50 * D, hcy - 0.18 * D)], c, OW * 0.5, mask='hat')
        elif kind in ('headscarf', 'chef', 'strawhat'):
            pen.poly(superellipse(cx, top + 0.02 * D, 0.52 * D, 0.22 * D, 2.2), c, mask='hat')

    def eye_xy(self, cx, hcy):
        f = self.face
        gap = 0.21 * D * max(0.85, min(1.15, float(f.get('eyeGap', 1.0))))
        ey = hcy + 0.02 * D + max(-0.06, min(0.06, float(f.get('eyeHeight', 0.0)))) * D
        return gap, ey

    def draw_face(self, pen, face, cx, hcy, view):
        if isinstance(face, str):
            eyes, brows, mouth = EXPR.get(face, EXPR['neutral'])
        else:
            eyes, brows, mouth = face.get('eyes', 'open'), face.get('brows', 'on'), face.get('mouth', 'rest')
        f = self.face
        es = max(0.9, min(1.1, float(f.get('eyeSize', 1.0))))
        bt = max(1.0, min(1.5, float(f.get('browThick', 1.3))))
        mw = max(0.8, min(1.2, float(f.get('mouthWidth', 1.0))))
        ecol = col(f.get('eyeColor'), INK)
        gap, ey = self.eye_xy(cx, hcy)
        if view == '3q':
            gap *= 0.82
        r = 0.042 * D * es
        for sx in (-1, 1):
            x = cx + sx * gap
            if eyes == 'open':
                pen.ellipse(x, ey, r * 0.85, r * 1.05, ecol)
            elif eyes in ('look_l', 'look_r'):
                dx = (-1 if eyes == 'look_l' else 1) * r * 0.45
                pen.ellipse(x + dx, ey, r * 0.85, r * 1.05, ecol)
            elif eyes == 'smug':
                pen.chord(x, ey, r * 1.3, r * 1.1, 0, 180, ecol)
                pen.line([(x - r * 1.5, ey), (x + r * 1.5, ey)], 0.02, cap=False)
            elif eyes == 'half':
                pen.chord(x, ey - r * 0.2, r * 1.15, r * 1.15, 0, 180, ecol)
                pen.line([(x - r * 1.4, ey - r * 0.2), (x + r * 1.4, ey - r * 0.2)], 0.018, cap=False)
            elif eyes == 'blink':
                pen.line([(x - r * 1.3, ey), (x + r * 1.3, ey)], 0.02)
            elif eyes == 'arc':
                pen.arc(x, ey + r * 0.6, r * 1.3, r * 1.2, 200, 340, 0.022)
            elif eyes in ('wide', 'stare', 'pinpoint'):
                R = r * (1.9 if eyes != 'stare' else 1.6)
                pen.ellipse(x, ey, R, R, HEAD, 0.02)
                p = {'wide': 0.45, 'stare': 0.7, 'pinpoint': 0.22}[eyes]
                pen.ellipse(x, ey, r * p * 1.4, r * p * 1.4, ecol)
            elif eyes == 'wince':
                pen.line([(x - sx * r * 1.4, ey - r * 1.1), (x + sx * r * 1.2, ey), (x - sx * r * 1.4, ey + r * 1.1)], 0.02)
            elif eyes in ('angry', 'sad'):
                pen.ellipse(x, ey + r * 0.2, r * 0.9, r * 1.0, ecol)
                inner = -sx if eyes == 'angry' else sx
                # a lid that cuts the eye: lower on the inner side (angry) or outer side (sad)
                ya = ey - r * (0.1 if inner < 0 else 1.2)
                yb = ey - r * (1.2 if inner < 0 else 0.1)
                pen.poly([(x - r * 1.5, ya), (x + r * 1.5, yb), (x + r * 1.5, ey - r * 2.2), (x - r * 1.5, ey - r * 2.2)], HEAD, 0, ink=False)
                pen.line([(x - r * 1.5, ya), (x + r * 1.5, yb)], 0.02, cap=False)
        # brows
        by = ey - 0.13 * D
        w = 0.026 * bt
        bl = 0.10 * D
        for sx in (-1, 1):
            x = cx + sx * gap
            if brows == 'off':
                continue
            if brows == 'on':
                pts = [(x - bl, by), (x + bl, by - 0.005 * D)]
            elif brows == 'up':
                pts = bez((x - bl, by - 0.05 * D), (x, by - 0.10 * D), (x + bl, by - 0.05 * D), 10)
            elif brows == 'down':
                pts = [(x - bl, by + 0.035 * D), (x + bl, by + 0.035 * D)]
            elif brows == 'knit':      # inner ends down
                pts = [(x - sx * bl, by + 0.05 * D), (x + sx * bl, by - 0.03 * D)]
            elif brows == 'worried':   # inner ends up
                pts = [(x - sx * bl, by - 0.06 * D), (x + sx * bl, by + 0.02 * D)]
            elif brows == 'quizzical':
                pts = bez((x - bl, by - (0.07 if sx > 0 else 0) * D), (x, by - (0.11 if sx > 0 else 0.01) * D), (x + bl, by - (0.06 if sx > 0 else 0) * D), 10)
            else:
                pts = [(x - bl, by), (x + bl, by)]
            pen.line(pts, w)
        # mouth
        my = hcy + 0.24 * D
        m = 0.07 * D * mw
        if mouth == 'rest':
            pen.ellipse(cx, my, m * 0.55, m * 0.18, INK)
        elif mouth == 'smile':
            pen.arc(cx, my - m * 0.5, m, m * 0.7, 20, 160, 0.02)
        elif mouth == 'frown':
            pen.arc(cx, my + m * 0.6, m, m * 0.6, 200, 340, 0.02)
        elif mouth == 'smirk':
            pen.line(bez((cx - m * 0.8, my + m * 0.05), (cx + m * 0.2, my + m * 0.2), (cx + m, my - m * 0.25), 10), 0.02)
        elif mouth in ('D', 'Dtongue'):
            pen.chord(cx, my - m * 0.6, m * 1.1, m * 1.3, 0, 180, INK)
            if mouth == 'Dtongue':
                pen.chord(cx + m * 0.1, my + m * 0.55, m * 0.55, m * 0.35, 180, 360, '#c8505a')
        elif mouth == 'crescent':
            pen.chord(cx, my - m * 0.7, m * 1.5, m * 1.25, 0, 180, INK)
        elif mouth == 'grid':
            pen.poly([(cx - m, my - m * 0.35), (cx + m, my - m * 0.35), (cx + m, my + m * 0.35), (cx - m, my + m * 0.35)], HEAD, 0.016)
            pen.line([(cx - m, my), (cx + m, my)], 0.01, cap=False)
            for j in (-0.5, 0, 0.5):
                pen.line([(cx + j * m, my - m * 0.35), (cx + j * m, my + m * 0.35)], 0.01, cap=False)
        elif mouth == 'o':
            pen.ellipse(cx, my + m * 0.1, m * 0.4, m * 0.5, INK)
        elif mouth == 'wide':
            pen.ellipse(cx, my + m * 0.4, m * 0.95, m * 1.25, INK)
            pen.chord(cx, my + m * 1.15, m * 0.55, m * 0.35, 180, 360, '#c8505a')
        elif mouth == 'flat':
            pen.line([(cx - m * 0.7, my), (cx + m * 0.7, my)], 0.018, cap=False)
        elif mouth == 'tight':
            pen.line([(cx - m * 0.35, my), (cx + m * 0.35, my)], 0.03)
        elif mouth == 'gulp':
            pts = [(cx - m * 0.8 + i * m * 0.2, my + (0.12 * m if i % 2 else -0.12 * m)) for i in range(9)]
            pen.line(pts, 0.016)

    def glasses(self, pen, cx, hcy):
        g = self.d.get('glasses')
        if not g:
            return
        kind = g.get('kind', 'round')
        gap, ey = self.eye_xy(cx, hcy)
        R = 0.10 * D
        fill = INK if kind == 'sun' else None
        for sx in (-1, 1):
            x = cx + sx * gap
            if kind in ('round', 'oval', 'sun'):
                pen.ellipse(x, ey, R, R * (0.8 if kind == 'oval' else 1.0), fill, 0.016)
            elif kind in ('square', 'half'):
                y0 = ey - (0.0 if kind == 'half' else R * 0.8)
                pen.poly([(x - R, y0), (x + R, y0), (x + R, ey + R * 0.8), (x - R, ey + R * 0.8)], None, 0.016)
            elif kind == 'cateye':
                pen.poly([(x - R * 1.1, ey - R), (x + R, ey - R * 0.6), (x + R * 0.8, ey + R * 0.7), (x - R * 0.8, ey + R * 0.7)], None, 0.016)
        pen.line([(cx - gap + R, ey), (cx + gap - R, ey)], 0.014, cap=False)

    def facial_hair(self, pen, cx, hcy):
        fh = self.d.get('facialHair')
        if not fh:
            return
        kind = fh.get('kind')
        c = col(fh.get('color'), col((self.d.get('hair') or {}).get('color'), DEFAULTS['hair']))
        my = hcy + 0.24 * D
        if kind in ('full', 'mutton'):
            pts = superellipse(cx, hcy + 0.25 * D, 0.40 * D, 0.21 * D, 2.2)
            pts = [p for p in pts if p[1] > hcy + 0.15 * D]
            pts.sort(key=lambda p: p[0])
            pen.poly(pts, c, OW * 0.5)
            pen.ellipse(cx, my, 0.07 * D, 0.03 * D, HEAD)
        elif kind == 'goatee':
            pen.poly(superellipse(cx, my + 0.08 * D, 0.08 * D, 0.06 * D, 2.2), c, OW * 0.5)
        elif kind == 'stubble':
            for j in range(18):
                a = math.pi * (0.15 + 0.7 * (j % 9) / 8)
                rr = 0.30 * D + (j // 9) * 0.05 * D
                pen.ellipse(cx + math.cos(a) * rr, hcy + 0.05 * D + math.sin(a) * rr * 0.75, 0.007 * D, 0.007 * D, c)
        if kind in ('moustache', 'walrus', 'handlebar', 'full'):
            w = {'moustache': 0.11, 'walrus': 0.16, 'handlebar': 0.13, 'full': 0.11}[kind] * D
            pen.poly([(cx - w, my - 0.03 * D), (cx, my - 0.07 * D), (cx + w, my - 0.03 * D), (cx, my - 0.01 * D)], c, OW * 0.4)
            if kind == 'handlebar':
                for sx in (-1, 1):
                    pen.line(bez((cx + sx * w, my - 0.03 * D), (cx + sx * (w + 0.05 * D), my - 0.02 * D), (cx + sx * (w + 0.04 * D), my - 0.09 * D), 8), 0.014)


# ------------------------------------------------------------------ 2.5D shading (section 5)
def shade(img, masks, L, geo):
    """Light the flat drawing like the set lights it.

    L: dict with  dir (x right, y up, z toward camera; the key light's direction FROM the character TO the light),
    key '#hex' (warm), shadow '#hex' (cool), floor (0-1, minimum light so faces never go muddy),
    rim (0-1), hardness (edge width, 0.02 = crisp), legs (multiplier), headShadow (0-1).
    Ink pixels are never shaded; hats shade with the head but get no rim.
    """
    cx, hcy, tt, tb, hip = [v * SS for v in geo]
    a = np.asarray(img).astype(np.float32) / 255.0
    rgbA, alpha = a[..., :3], a[..., 3:]
    h, w = alpha.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    lx, ly, lz = L.get('dir', (-0.5, 0.6, 0.6))
    n = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / n, ly / n, lz / n
    hard = L.get('hardness', 0.03)
    floor = L.get('floor', 0.35)
    key = np.array(rgb(L.get('key', '#ffe2c0')), np.float32) / 255
    shd = np.array(rgb(L.get('shadow', '#6c74a8')), np.float32) / 255
    ink = np.array(rgb(INK), np.float32) / 255
    is_ink = (np.abs(rgbA - ink).sum(-1) < 0.12)[..., None]

    def toon(ndl, keyc=None):
        t = np.clip((ndl + hard) / (2 * hard), 0, 1)          # crisp drawn edge
        lightc = (key if keyc is None else keyc)[None, None, :]
        shadowc = floor + (1 - floor) * shd[None, None, :]
        return t[..., None] * lightc + (1 - t[..., None]) * shadowc, t

    out = rgbA.copy()
    R = 0.5 * D * SS
    # head + hat: a sphere on its disc
    for name, rim_ok in (('head', True), ('hat', False)):
        m = np.asarray(masks[name], np.float32)[..., None] / 255
        if m.max() == 0:
            continue
        nx = (xs - cx) / R
        ny = -(ys - hcy) / (0.47 * D * SS)
        rr = np.clip(nx * nx + ny * ny, 0, 1)
        nz = np.sqrt(1 - rr)
        ndl = nx * lx + ny * ly + nz * lz
        f, t = toon(ndl, 0.8 + 0.2 * key)                   # faces stay paper-white on the lit side
        sh = out * f
        if rim_ok and L.get('rim', 0) > 0:
            rim = np.clip((rr - 0.80) / 0.15, 0, 1) * (1 - t) * L['rim']          # thin rim on the dark side
            sh = sh + rim[..., None] * key[None, None, :] * 0.6
        out = np.where((m > 0.5) & ~is_ink, sh, out)
    # torso: a cylinder, + the head's drawn shadow on the chest
    head_m = (np.asarray(masks['head']) > 127) | (np.asarray(masks['hat']) > 127)
    m = np.asarray(masks['torso'], np.float32)[..., None] / 255 * (~head_m)[..., None]
    tw = max(1.0, (np.asarray(masks['torso']).max(0) > 0).sum() / 2)
    nx = np.clip((xs - cx) / tw, -1, 1)
    nz = np.sqrt(1 - nx * nx)
    ndl = nx * lx + nz * max(lz, 0.2) + 0.25 * ly
    f, t = toon(ndl)
    hs = L.get('headShadow', 0.5)
    sx_off = -lx * 0.12 * D * SS
    in_hs = ((xs - cx - sx_off) / (0.42 * D * SS)) ** 2 + ((ys - tt - 0.02 * D * SS) / (0.16 * D * SS)) ** 2 < 1
    f = np.where(in_hs[..., None] & (ly > 0), f * (1 - hs) + hs * (floor + (1 - floor) * shd), f)
    out = np.where((m > 0.5) & ~is_ink, out * f, out)
    # legs: ink sticks, already the darkest value of the drawing (section 5 'jambes plus sombres')
    out = np.clip(out, 0, 1)
    res = np.concatenate([out, alpha], -1)
    return Image.fromarray((res * 255).astype(np.uint8), 'RGBA')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def sheet(desc_path, out_path):
    """Check sheet (section 1 'Vérification'): front + 3/4, faces, flat and shaded."""
    ch = Character(load(desc_path))
    light = {'dir': (-0.6, 0.5, 0.65), 'key': '#ffe0bc', 'shadow': '#7a7fb8', 'floor': 0.42, 'rim': 0.6,
             'hardness': 0.03, 'legs': 0.85, 'headShadow': 0.45}
    cells = [ch.draw('neutral', 'front'), ch.draw('neutral', '3q'), ch.draw('neutral', 'front', light),
             ch.draw('neutral', '3q', light)]
    faces = ['fear', 'relief', 'confused', 'horror', 'smug', 'angry', 'shout', 'dread']
    heads = []
    for e in faces:
        im = ch.draw(e, 'front', light)
        cx, foot, hip, tb, tt, hcy, hh = ch.layout()
        heads.append(im.crop((int(cx - 0.75 * D), int(hcy - 0.8 * D), int(cx + 0.75 * D), int(hcy + 0.7 * D))))
    W = Image.new('RGB', (4 * 550, 850 + 2 * 300), (128, 146, 160))
    for i, c in enumerate(cells):
        c2 = c.resize((550, 850))
        W.paste(c2, (i * 550, 0), c2)
    for i, hd in enumerate(heads):
        hd = hd.resize((275, 275))
        W.paste(hd, ((i % 8) * 275, 860 + (i // 8) * 300), hd)
    W.save(out_path)


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        sheet(sys.argv[2], sys.argv[3])
