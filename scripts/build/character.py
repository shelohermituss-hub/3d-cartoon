"""Draw the flat 'Cartoon Short' character as a transparent PNG (one image per expression).

The character is drawn, never rendered: white egg head, dot eyes, ink outline, flat torso,
noodle limbs. Role identity = torso colour + one accessory.

Usage: python character.py OUT_DIR
Writes <role>_<expression>.png at 1000 x 1900 (drawn 4x larger, then reduced for clean edges).
"""
import math, os, sys
from PIL import Image, ImageDraw

SS = 4                     # supersampling
W, H = 1000, 1900          # final canvas
INK = (26, 28, 46, 255)    # #1a1c2e outline
HEAD = (246, 243, 240, 255)  # off-white paper head, between #e8e1df and #ffffff

ROLES = {
    # role: torso, accessory colour, hat colour
    'courier': dict(torso=(92, 107, 86, 255), strap=(110, 74, 50, 255), hat=(181, 86, 45, 255)),
}


def s(v):
    return int(round(v * SS))


def egg(cx, cy, w, h, n=180):
    """Egg outline: a bit wider at the top than at the bottom."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = math.cos(t)
        y = math.sin(t)
        k = 1.0 - 0.07 * y          # y>0 is lower half (image coords): narrower
        pts.append((s(cx + x * w / 2 * k), s(cy + y * h / 2)))
    return pts


def stroke(d, pts, width, fill=INK):
    pts = [(s(x), s(y)) for x, y in pts]
    d.line(pts, fill=fill, width=s(width), joint='curve')
    r = s(width) / 2
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def bezier(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


def outlined_polygon(d, pts, fill, ow):
    pts_s = [(s(x), s(y)) for x, y in pts]
    d.polygon(pts_s, fill=fill)
    d.line(pts_s + [pts_s[0]], fill=INK, width=s(ow), joint='curve')


def rounded_trapezoid(cx, top, bottom, wtop, wbot, r, n=10):
    """Torso: wider at the shoulders, rounded corners."""
    corners = [(cx - wtop / 2, top), (cx + wtop / 2, top), (cx + wbot / 2, bottom), (cx - wbot / 2, bottom)]
    pts = []
    for i, c in enumerate(corners):
        prev = corners[i - 1]
        nxt = corners[(i + 1) % 4]
        def toward(a, b, dist):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            return (a[0] + dx / L * dist, a[1] + dy / L * dist)
        a = toward(c, prev, r)
        b = toward(c, nxt, r)
        pts += bezier(a, c, b, n)
    return pts


def draw(role='courier', expr='neutral'):
    R = ROLES[role]
    img = Image.new('RGBA', (s(W), s(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 500
    head_cy, head_w, head_h = 330, 370, 410
    torso_top, torso_bot = 535, 1000
    hip_y = torso_bot - 20
    foot_y = H - 30
    limb = 26          # noodle limb width on the canvas (about 12 px on screen in a medium shot)
    ow = 13            # outline width on the canvas (about 6 px on screen)

    # legs (behind torso)
    stroke(d, bezier((cx - 55, hip_y), (cx - 75, (hip_y + foot_y) / 2), (cx - 70, foot_y)), limb)
    stroke(d, bezier((cx + 55, hip_y), (cx + 80, (hip_y + foot_y) / 2), (cx + 78, foot_y)), limb)
    # feet: tiny ink tips
    for fx in (cx - 70, cx + 78):
        d.ellipse([s(fx - 30), s(foot_y - 14), s(fx + 26), s(foot_y + 14)], fill=INK)

    # back arm (right side of picture), hanging
    stroke(d, bezier((cx + 135, torso_top + 70), (cx + 210, torso_top + 330), (cx + 190, torso_top + 560)), limb)
    d.ellipse([s(cx + 190 - 24), s(torso_top + 560 - 24), s(cx + 190 + 24), s(torso_top + 560 + 24)], fill=INK)

    # torso
    torso = rounded_trapezoid(cx, torso_top, torso_bot, 300, 250, 70)
    outlined_polygon(d, torso, R['torso'], ow)
    # zip line down the jacket
    stroke(d, [(cx, torso_top + 60), (cx, torso_bot - 30)], 6, (40, 46, 40, 255))

    # accessory: shoulder bag strap across the chest + bag at the hip
    strap = [(cx - 120, torso_top + 20), (cx - 85, torso_top + 5), (cx + 140, torso_bot - 120), (cx + 110, torso_bot - 95)]
    outlined_polygon(d, strap, R['strap'], 8)
    bag = rounded_trapezoid(cx + 150, torso_bot - 170, torso_bot - 10, 170, 190, 30)
    outlined_polygon(d, bag, R['strap'], ow)
    stroke(d, [(cx + 70, torso_bot - 110), (cx + 232, torso_bot - 110)], 7)

    # front arm (left side of picture), bent, hand near the strap
    stroke(d, bezier((cx - 135, torso_top + 70), (cx - 230, torso_top + 300), (cx - 110, torso_top + 360)), limb)
    d.ellipse([s(cx - 110 - 24), s(torso_top + 360 - 24), s(cx - 110 + 24), s(torso_top + 360 + 24)], fill=INK)

    # head
    head = egg(cx, head_cy, head_w, head_h)
    d.polygon(head, fill=HEAD)
    d.line(head + [head[0]], fill=INK, width=s(ow), joint='curve')

    # hat: knitted beanie = the top of the head shape, a bit larger, as one flat shape
    top = head_cy - head_h / 2
    band_y = head_cy - 45
    big = egg(cx, head_cy, head_w + 22, head_h + 22)
    hat = [p for p in big if p[1] < s(band_y)]
    hat.sort(key=lambda p: math.atan2(p[1] - s(head_cy), p[0] - s(cx)))
    hat = [(x / SS, y / SS) for x, y in hat]
    outlined_polygon(d, hat, R['hat'], ow)
    stroke(d, [(cx - head_w / 2 + 2, band_y - 22), (cx + head_w / 2 - 2, band_y - 22)], 8)
    d.ellipse([s(cx - 34), s(top - 60), s(cx + 34), s(top + 8)], fill=R['hat'], outline=INK, width=s(ow))

    # face
    ey = head_cy + 50
    if expr == 'neutral':
        for ex in (cx - 62, cx + 62):
            d.ellipse([s(ex - 16), s(ey - 18), s(ex + 16), s(ey + 18)], fill=INK)
        stroke(d, [(cx - 92, ey - 52), (cx - 38, ey - 48)], 9)          # brows: one flat,
        stroke(d, [(cx + 36, ey - 46), (cx + 92, ey - 58)], 9)          # one slightly raised (wary)
        stroke(d, [(cx - 22, ey + 82), (cx + 18, ey + 78)], 8)          # small mouth line
    elif expr == 'shock':
        for ex in (cx - 62, cx + 62):
            d.ellipse([s(ex - 26), s(ey - 26), s(ex + 26), s(ey + 26)], fill=HEAD, outline=INK, width=s(7))
            d.ellipse([s(ex - 8), s(ey - 8), s(ex + 8), s(ey + 8)], fill=INK)
        stroke(d, [(cx - 92, ey - 70), (cx - 36, ey - 80)], 9)
        stroke(d, [(cx + 36, ey - 80), (cx + 92, ey - 70)], 9)
        d.ellipse([s(cx - 26), s(ey + 60), s(cx + 26), s(ey + 120)], fill=INK)

    return img.resize((W, H), Image.LANCZOS)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for role in ROLES:
        for expr in ('neutral', 'shock'):
            p = os.path.join(out, f'{role}_{expr}.png')
            draw(role, expr).save(p)
            print(p)
