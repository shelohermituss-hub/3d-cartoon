"""Test film, 10 s: "Théo et le colis". Every frame is a pure function of t (docs/STYLE_NEW.md section 0).

Blender (bpy) script. Builds the alley set once (scripts/build/scene_alley.py), then for each frame:
character drawing (charkit, shaded by the set's light), character position, props, camera -> render.

  python film.py OUTDIR [--scale 0.5] [--samples 4] [--lines 1] [--part 0 --parts 3] [--frames a-b]
"""
import bpy
bpy.app.version
import json, math, os, runpy, sys
from mathutils import Vector, Euler, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
FPS, DUR = 30, 10.0
NF = int(FPS * DUR)
VO = 0.40                     # the narration starts 0.4 s into the film

# ------------------------------------------------------------------ arguments
a = sys.argv[1:]
OUT = a[0]


def opt(name, default):
    return type(default)(a[a.index(name) + 1]) if name in a else default


SCALE, SAMPLES, LINES = opt('--scale', 0.5), opt('--samples', 4), opt('--lines', 1)
PART, PARTS = opt('--part', 0), opt('--parts', 1)
FR = opt('--frames', '')
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ build the set once
os.environ['SCENE_BUILD_ONLY'] = '1'
sys.argv = ['scene', '/dev/null', str(SCALE), str(SAMPLES)]
G = runpy.run_path(os.path.join(ROOT, 'scripts', 'build', 'scene_alley.py'), run_name='scene')
scene, cam, charkit, hero, place, P = G['scene'], G['cam'], G['charkit'], G['hero'], G['place'], G['P']
UNIT, CARD_H, FEET, sun_dir = G['UNIT'], G['CARD_H'], G['FEET'], G['sun_dir']
card = bpy.data.objects['character']
shadow_card = bpy.data.objects['character_shadow']
char_img = bpy.data.materials['char_flat'].node_tree.nodes['Image Texture'].image
ee = scene.eevee
ee.use_raytracing = False                       # speed: no screen-space reflections
bpy.data.objects['haze'].hide_render = True     # speed: haze is done in post
scene.render.use_freestyle = bool(LINES)
scene.view_layers[0].use_freestyle = bool(LINES)

# hydrant: moved against the left wall, out of the camera paths; the still's hard-coded character spot is driven per frame below
for o in bpy.data.objects:
    if o.name.startswith('fire_hydrant'):
        o.location.x -= 1.05; o.location.y += 0.9
words = json.load(open(os.path.join(HERE, 'words.json'), encoding='utf-8'))
W = {i: (w['t0'] + VO, w['t1'] + VO) for i, w in enumerate(words)}

# ------------------------------------------------------------------ props: the parcel and the dumpster lid
box = place(P['cardboard_box_01']['cardboard_box_01'], (0, 0, 0), 0.0)
BOX_S = 0.72                         # 0.27 x 0.37 x 0.25 m
box.name = 'parcel'
lid = next(o for o in bpy.data.objects if o.name.startswith('Object_82_i'))
bb = [lid.matrix_world @ Vector(c) for c in lid.bound_box]
lx0, lx1 = min(v.x for v in bb), max(v.x for v in bb)
ly0, ly1 = min(v.y for v in bb), max(v.y for v in bb)
lz1 = max(v.z for v in bb)
hinge = bpy.data.objects.new('lid_hinge', None)
scene.collection.objects.link(hinge)
hinge.location = ((lx0 + lx1) / 2, ly1, lz1 - 0.03)        # back top edge
bpy.context.view_layer.update()
lid.parent = hinge
lid.matrix_parent_inverse = hinge.matrix_world.inverted()

# ------------------------------------------------------------------ helpers (all pure functions of t)
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def vlerp(a, b, x):
    return Vector(a).lerp(Vector(b), x)


def noise(t, seed):
    """Smooth deterministic wobble in -1..1 (sum of sines, no random state)."""
    return (math.sin(t * 7.3 + seed) * 0.5 + math.sin(t * 13.1 + seed * 2.1) * 0.3 + math.sin(t * 23.7 + seed * 3.7) * 0.2)


P0 = Vector((-1.30, 6.00, 0.0))      # where Théo stands at the start
P1 = Vector((0.00, 5.45, 0.0))       # in front of the dumpster
BOX_GROUND = Vector((0.55, 5.30, 0.0))
RUN_END = Vector((-1.0, 0.4, 0.0))      # runs toward the camera (face visible), exits left
HEAD_Z = (charkit.CH - 30 - hero.layout()[5]) / charkit.D * UNIT     # head centre above the feet (m)
HAND_Z = 0.714                       # hands in the 'carry' pose (m above the feet)

# key times (film seconds), from the words
T_BOUGE = W[12][0]                   # "bouge."
T_WALK0, T_WALK1 = W[13][0], W[13][0] + 0.60
T_PUT0, T_PUT1 = T_WALK1 + 0.03, T_WALK1 + 0.33
T_RATTLE = W[21][0]                  # "benne"
T_OPEN = W[22][0]                    # "s'ouvre"
T_SHOCK = T_OPEN + 0.04
T_JUMP = T_SHOCK + 2 / FPS
T_RUN = W[26][0] + 0.06              # "Depuis,"

# shots: (start, end, name). Cuts land 0.06 s before the clause's first word; a 3-frame dissolve into the last shot.
CUTS = [0.0, W[5][0] - 0.06, W[10][0] - 0.06, W[13][0] - 0.06, W[20][0] - 0.06, W[26][0] - 0.06, DUR]
SHOTS = ['close', 'macro', 'medium', 'wide', 'lowmed', 'widecalm']
DISSOLVE_INTO = {'widecalm': 3}      # frames of cross-dissolve at the start of these shots


def shot_at(t):
    for i in range(len(SHOTS)):
        if CUTS[i] <= t < CUTS[i + 1]:
            return i
    return len(SHOTS) - 1


def theo_pos(t):
    if t < T_WALK0:
        p = P0.copy()
    elif t < T_WALK1:
        p = vlerp(P0, P1, (t - T_WALK0) / (T_WALK1 - T_WALK0))
        p.z = 0.025 * abs(math.sin(math.pi * (t - T_WALK0) * FPS / 9))     # body rises at each 9-frame step
    elif t < T_RUN:
        p = P1.copy()
    else:
        x = clamp((t - T_RUN) / 1.65)
        p = vlerp(P1, RUN_END, x)
        p.z = 0.06 * abs(math.sin(math.pi * (t - T_RUN) * FPS / 6))
    # shock jump: up 0.3 x height fast, down in 0.4 s, stops dead
    if T_JUMP <= t < T_JUMP + 0.42:
        u = (t - T_JUMP) / 0.42
        p.z += 0.48 * (1 - (2 * u - 1) ** 2)
    return p


def theo_look(t):
    """Face, pose and 2D effects for the drawing at time t. Faces change instantly, at most every 8 frames."""
    face = {'eyes': 'smug', 'brows': 'down', 'mouth': 'smirk'}
    if 0.90 <= t < 0.90 + 2 / FPS:
        face = {'eyes': 'blink', 'brows': 'down', 'mouth': 'smirk'}
    if t >= CUTS[1] + 4 / FPS:
        face = {'eyes': 'open', 'brows': 'on', 'mouth': 'rest'}
    if t >= T_BOUGE + 0.04:
        face = 'fear'
    if t >= CUTS[3] + 4 / FPS:
        face = 'dread'
    if t >= T_SHOCK:
        face = 'terror'
    if t >= T_RUN:
        face = {'eyes': 'wide', 'brows': 'worried', 'mouth': 'wide'}
    pose = {'arms': 'carry', 'legs': 'stand', 'phase': 0.0, 'dir': 1, 'fx': [], 'lean': 0.0}
    if T_BOUGE + 0.10 <= t < T_WALK0:            # react: lean back, ~10 frames, then still
        pose['lean'] = 6.0 * ease((t - T_BOUGE - 0.10) / 0.33)
    if T_WALK0 <= t < T_WALK1:
        pose.update(legs='walk', phase=(t - T_WALK0) * FPS / 18.0)
    if T_PUT0 <= t < T_PUT1 + 0.25:
        pose['arms'] = 'down'
    elif t >= T_PUT1 + 0.25:
        pose['arms'] = 'rest'
    if T_JUMP <= t < T_JUMP + 0.42:
        pose['arms'] = 'up'
        pose['legs'] = 'tuck' if 0.06 < (t - T_JUMP) < 0.36 else 'stand'
    if T_SHOCK + 1 / FPS <= t < T_SHOCK + 6 / FPS:
        pose['fx'] = ['speed', 'sweat']
    elif t >= T_SHOCK + 6 / FPS:
        pose['fx'] = ['sweat']
    if T_JUMP + 0.42 <= t < T_RUN:
        pose['arms'] = 'up'                      # held still after landing
    if t >= T_RUN:
        pose.update(arms='run', legs='run', phase=(t - T_RUN) * FPS / 12.0, dir=-1)
    return face, pose


def box_matrix(t, theo, to_cam):
    """The parcel: carried in front of Théo, shaking on 'bouge', put down, then still on the ground."""
    carried = theo + to_cam * 0.14 + Vector((0, 0, HAND_Z - 0.12))
    rot = math.atan2(-to_cam.x, to_cam.y)
    if t < T_PUT0:
        pos, rx, ry = carried, 0.0, 0.0
        if T_BOUGE <= t < T_WALK0:               # it moves by itself
            k = 1.0 - 0.3 * ease((t - T_BOUGE) / 0.6)
            rx = math.radians(7) * k * math.sin(t * 2 * math.pi * 11)
            ry = math.radians(5) * k * math.sin(t * 2 * math.pi * 8 + 1)
            pos = pos + Vector((0, 0, 0.02 * abs(math.sin(t * 2 * math.pi * 9))))
    elif t < T_PUT1:
        u = ease((t - T_PUT0) / (T_PUT1 - T_PUT0))
        pos, rx, ry = vlerp(carried, BOX_GROUND, u), 0.0, 0.0
        rot = lerp(rot, 0.15, u)
    else:
        pos, rx, ry, rot = BOX_GROUND.copy(), 0.0, 0.0, 0.15
        if T_OPEN <= t < T_OPEN + 0.25:          # hops when the lid bangs open
            pos.z += 0.12 * math.sin(math.pi * (t - T_OPEN) / 0.25)
    return Matrix.Translation(pos) @ Euler((rx, ry, rot)).to_matrix().to_4x4() @ Matrix.Scale(BOX_S, 4)


def lid_angle(t):
    if t < T_RATTLE:
        return 0.0
    if t < T_OPEN:                               # rattles on "benne"
        return math.radians(4) * abs(math.sin((t - T_RATTLE) * 2 * math.pi * 7))
    u = (t - T_OPEN) / 0.40                      # swings open in 0.4 s with a 10 % overshoot, then stops dead
    if u < 1:
        return math.radians(118) * (1 - (1 - u) ** 3) * (1 + 0.10 * math.sin(math.pi * u))
    return math.radians(118)


def look_at(pos, target, fov_deg, roll_deg, shake=0.0, t=0.0):
    cam.location = pos
    q = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y')
    roll = math.radians(roll_deg)
    if shake:
        q = q @ Quaternion((1, 0, 0), math.radians(0.35 * shake * noise(t, 1.0))) @ Quaternion((0, 1, 0), math.radians(0.35 * shake * noise(t, 2.0)))
    cam.rotation_euler = (q @ Quaternion((0, 0, 1), roll)).to_euler()
    cam.data.lens = 18 / math.tan(math.radians(fov_deg / 2))


def camera(t, i):
    """Dread Cuts: low camera looking up, slow push / orbit each shot, roll 2-5 deg changing side."""
    s0, s1 = CUTS[i], CUTS[i + 1]
    u = ease((t - s0) / (s1 - s0))
    name = SHOTS[i]
    th = theo_pos(t)
    head = Vector((th.x, th.y, HEAD_Z))
    if name == 'close':                          # head ~400 px, push in 10 %
        d = lerp(3.95, 3.55, u)
        look_at(head + Vector((-0.30, -d, -0.22)), Vector((th.x, th.y, 0.99)), 28, lerp(3.0, 2.0, u), 1.0, t)
        focus = d
    elif name == 'macro':                        # the parcel in his hands, orbit 12 deg
        boxc = th + Vector((0, -0.14, HAND_Z - 0.0))
        ang = math.radians(lerp(-16, -4, u))
        r = 0.95
        pos = boxc + Vector((math.sin(ang) * -r, -math.cos(ang) * r, -0.18))
        look_at(pos, boxc + Vector((0, 0, 0.02)), 34, -2.0, 1.0, t)
        focus = r
    elif name == 'medium':                       # head ~320 px, from the right, push 10 %
        d = lerp(4.2, 3.8, u)
        look_at(Vector((th.x + 1.15, th.y - d, 0.85)), Vector((th.x, th.y, 0.95)), 28, lerp(-3.0, -4.0, u), 1.0, t)
        focus = d
    elif name == 'wide':                         # ~200 px heads: the place, tracking the walker
        tgt = Vector((lerp(th.x, 0.9, 0.35), 5.7, 0.95))
        look_at(Vector((lerp(-1.75, -1.55, u), lerp(-1.7, -1.3, u), 1.0)), tgt, 30, 2.5, 1.0, t)
        focus = (tgt - cam.location).length
    elif name == 'lowmed':                       # low, Théo and the lid in frame; shake 2 on the shock
        sh = 1.0 + (2.0 * math.exp(-(t - T_SHOCK) * 3.0) if t >= T_SHOCK else 0.0)
        look_at(Vector((lerp(-1.05, -0.9, u), lerp(0.55, 0.95, u), 0.72)), Vector((0.55, 5.6, 1.18)), 32,
                lerp(-3.5, -2.5, u), sh, t)
        focus = (head - cam.location).length
    else:                                        # calm wide, slow pull-back
        look_at(Vector((lerp(-0.25, -0.32, u), lerp(-1.25, -1.75, u), 1.25)), Vector((0.35, 6.0, 0.95)), 30, 2.0, 1.0, t)
        focus = max(1.0, (theo_pos(t) + Vector((0, 0, 1.0)) - cam.location).length) if t < T_RUN + 1.65 else 7.0
    cam.data.dof.focus_distance = focus


def light_for_camera():
    to_light_c = cam.rotation_euler.to_quaternion().inverted() @ (-sun_dir)
    d = dict(G['LIGHT'])
    d['dir'] = tuple(round(v, 3) for v in to_light_c)
    return d


CACHE = {}


def set_character(t):
    face, pose = theo_look(t)
    th = theo_pos(t)
    to_cam = cam.location - th
    to_cam.z = 0
    to_cam.normalize()
    light = light_for_camera()
    key = json.dumps([face, pose, light], sort_keys=True, default=str)
    path = os.path.join(OUT, 'char', f'{abs(hash(key)) % 10 ** 12}.png')
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        hero.draw(face, 'front', light, pose).save(path)
    global char_img
    tex = bpy.data.materials['char_flat'].node_tree.nodes['Image Texture']
    old = tex.image
    tex.image = bpy.data.images.load(path)        # a fresh image each frame, the previous one is freed (no memory growth)
    if old is not None and old.users == 0:
        bpy.data.images.remove(old)
    char_img = tex.image
    card.location = (th.x, th.y, th.z - FEET)
    card.rotation_euler = (math.pi / 2, 0, math.atan2(-to_cam.x, to_cam.y) + math.pi)
    shadow_card.location = card.location
    box.matrix_world = box_matrix(t, th, to_cam)
    hinge.rotation_euler = (-lid_angle(t), 0, 0)


def render(t, i, path):
    camera(t, i)
    set_character(t)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------ frame loop (resumable, split across processes)
frames = range(NF)
if FR:
    f0, f1 = (int(x) for x in FR.split('-'))
    frames = range(f0, f1 + 1)
for f in frames:
    if f % PARTS != PART:
        continue
    t = f / FPS
    i = shot_at(t)
    path = os.path.join(OUT, f'f{f:04d}.png')
    if not os.path.exists(path):
        render(t, i, path)
    # cross-dissolve frames: also render the previous shot at the same t (the blend is done when assembling)
    k = f - round(CUTS[i] * FPS)
    if SHOTS[i] in DISSOLVE_INTO and 0 <= k < DISSOLVE_INTO[SHOTS[i]]:
        pathb = os.path.join(OUT, f'f{f:04d}_prev.png')
        if not os.path.exists(pathb):
            render(t, i - 1, pathb)
    print('frame', f, 'shot', SHOTS[i], flush=True)

# timeline for the assembly step
json.dump({'fps': FPS, 'dur': DUR, 'vo': VO, 'cuts': CUTS, 'shots': SHOTS, 'dissolve': DISSOLVE_INTO,
           'events': {'bouge': T_BOUGE, 'walk0': T_WALK0, 'walk1': T_WALK1, 'put1': T_PUT1, 'rattle': T_RATTLE,
                      'open': T_OPEN, 'jump': T_JUMP, 'run': T_RUN}},
          open(os.path.join(OUT, 'timeline.json'), 'w'), indent=1)
