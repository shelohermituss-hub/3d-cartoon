"""Build the 'alley at dusk' set from Poly Haven CC0 assets, place the flat character, render one still.

Run:  python scene_alley.py OUT.png [scale] [samples]
  scale   1.0 = 1080 x 1920, 0.5 = 540 x 960 (for quick tests)
"""
import bpy
bpy.app.version  # initialise Blender before other imports
import math, os, random, sys
from mathutils import Vector, Euler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PH = os.path.join(ROOT, 'assets', 'polyhaven')
CHAR = os.path.join(ROOT, 'assets', 'characters')
args = [a for a in sys.argv[1:]]
OUT = args[0] if args else os.path.join(ROOT, 'renders', 'still.png')
SCALE = float(args[1]) if len(args) > 1 else 1.0
SAMPLES = int(args[2]) if len(args) > 2 else 32
random.seed(4)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def hexrgb(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, a)


def gltf(aid):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(PH, aid, f'{aid}_1k.gltf'))
    return [o for o in bpy.data.objects if o not in before]


def library(aid):
    """Import an asset into a hidden collection; return {name: object}."""
    objs = gltf(aid)
    col = bpy.data.collections.new('lib_' + aid)
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        col.objects.link(o)
    return {o.name.split('.')[0]: o for o in objs if o.type == 'MESH'}


def place(src, loc, rot_z=0.0, scale=1.0, offset=(0, 0, 0)):
    """Linked copy of a library mesh. offset moves the piece's own origin first (kit layouts)."""
    o = bpy.data.objects.new(src.name + '_i', src.data)
    scene.collection.objects.link(o)
    m = Euler((0, 0, rot_z)).to_matrix().to_4x4()
    o.matrix_world = (
        __import__('mathutils').Matrix.Translation(Vector(loc)) @ m @
        __import__('mathutils').Matrix.Scale(scale, 4) @
        __import__('mathutils').Matrix.Translation(Vector(offset)) @ src.matrix_world)
    return o


# ---------------------------------------------------------------- facade kit
FAC = library('modular_urban_apartments_facade')
# bay = (wall piece, window/door piece); both are moved so the wall's lower-left corner is the origin.
BAY_X0 = {}
for n, o in FAC.items():
    if n.startswith('wall_'):
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        BAY_X0[n] = (min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))

GROUND_BAYS = [('wall_standard_standard_01', None), ('wall_door_centered_small_01', 'door_centered_small_01'),
               ('wall_door_centered_large_01', 'door_centered_large_01')]
UPPER_BAYS = [('wall_window_centered_large_01', 'window_centered_large_01'),
              ('wall_window_centered_small_01', 'window_centered_small_01'),
              ('wall_window_centered_double_01', 'window_centered_double_01'),
              ('wall_window_offset_small_01', 'window_offset_small_01')]
STOREY = 3.5
WARM_GLASS = None


def lit_glass(obj, on):
    """Window glass: warm #f0c060 glow when lit, dark blue reflection otherwise."""
    global WARM_GLASS
    if not on:
        return
    if WARM_GLASS is None:
        m = bpy.data.materials.new('window_warm')
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes['Principled BSDF']
        bsdf.inputs['Base Color'].default_value = hexrgb('#f0c060')
        bsdf.inputs['Emission Color'].default_value = hexrgb('#f0c060')
        bsdf.inputs['Emission Strength'].default_value = 6.0
        WARM_GLASS = m
    obj.data = obj.data.copy()
    for i, slot in enumerate(obj.data.materials):
        if slot and 'glass' in slot.name:
            obj.data.materials[i] = WARM_GLASS


def facade(origin, rot_z, bays, storeys, lit_ratio=0.35):
    """Build a facade `bays` wide (3 m each) and `storeys` high, starting at origin, running along local +X."""
    rot = Euler((0, 0, rot_z)).to_matrix()
    for b in range(bays):
        for s_ in range(storeys):
            wall_n, item_n = random.choice(GROUND_BAYS if s_ == 0 else UPPER_BAYS)
            x0, y0, z0 = BAY_X0[wall_n]
            loc = Vector(origin) + rot @ Vector((b * 3.0, 0, s_ * STOREY))
            place(FAC[wall_n], loc, rot_z, offset=(-x0, -y0, -z0))
            if item_n:
                it = place(FAC[item_n], loc, rot_z, offset=(-x0, -y0, -z0))
                lit_glass(it, s_ > 0 and random.random() < lit_ratio)
            # band between storeys
            if s_ > 0:
                dn = 'dado_standard_standard_01'
                o = FAC[dn]
                bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
                place(o, loc + Vector((0, 0, -0.5)), rot_z,
                      offset=(-min(v.x for v in bb), -max(v.y for v in bb), -min(v.z for v in bb)))
        # base and crown
        for dn, z in (('base_standard_01', 0.0), ('crown_standard_standard_01', storeys * STOREY - 0.5)):
            o = FAC[dn]
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            loc = Vector(origin) + rot @ Vector((b * 3.0, 0, z))
            place(o, loc, rot_z, offset=(-min(v.x for v in bb), -max(v.y for v in bb), -min(v.z for v in bb)))
        # piers between bays fill the 1 m gap
        o = FAC['wall_pier_standard_01']
    return


# Alley runs along +Y. Left wall faces +X, right wall faces -X, end wall faces -Y.
facade((-3.0, 40.0, 0), -math.pi / 2, 14, 5, 0.3)
facade((-3.0, 46.0, 0), -math.pi / 2, 2, 2, 0.3)       # left wall, running from y=40 toward -y
facade((3.0, -2.0, 0), math.pi / 2, 14, 5, 0.3)         # right wall, running from y=-2 toward +y
facade((-12.0, 52.0, 0), 0.0, 8, 3, 0.5)                # low far building: the low sun passes over it

# ---------------------------------------------------------------- props (mid-ground layer)
P = {}
for aid in ('rollershutter_door', 'metal_trash_can', 'street_lamp_01', 'exterior_aircon_unit', 'fire_hydrant',
            'utility_box_01', 'cardboard_box_01', 'modular_fire_escape', 'water_manhole_cover', 'concrete_road_barrier'):
    P[aid] = library(aid)


def recolor(obj, hexcol, keep_texture=0.25):
    """Give an asset one flat saturated colour (the scene's accent), keeping a little of its texture."""
    obj.data = obj.data.copy()
    for i, mat in enumerate(obj.data.materials):
        m = mat.copy()
        m['accent'] = 1
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        link = bsdf.inputs['Base Color'].links
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = keep_texture
        mix.inputs[6].default_value = hexrgb(hexcol)
        if link:
            nt.links.new(link[0].from_socket, mix.inputs[7])
        else:
            mix.inputs[7].default_value = (1, 1, 1, 1)
        nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
        obj.data.materials[i] = m


# accent: a blue roller shutter (#3c56a6) on the right wall, two of them side by side
for y in (7.0, 8.2):
    o = place(P['rollershutter_door']['rollershutter_door'], (2.98, y, 0), math.pi / 2)
    recolor(o, '#3c56a6', 0.35)
place(P['metal_trash_can']['metal_trash_can'], (1.9, 5.2, 0), 0.4, offset=(-0.5, 0, 0))
place(P['metal_trash_can']['metal_trash_can_rust'], (2.3, 10.5, 0), -0.3, offset=(0.5, 0, 0))
place(P['cardboard_box_01']['cardboard_box_01'], (2.2, 4.3, 0), 0.6)
place(P['cardboard_box_01']['cardboard_box_01'], (2.35, 4.6, 0.34), 1.2)
place(P['utility_box_01']['utility_box_01_box'], (-2.7, 6.0, 0), -math.pi / 2)
place(P['exterior_aircon_unit']['exterior_aircon_unit'], (2.8, 12.0, 4.2), math.pi / 2, offset=(0.5, 0, 0))
place(P['exterior_aircon_unit']['exterior_aircon_unit_rusted'], (-2.8, 15.0, 7.7), -math.pi / 2, offset=(-0.5, 0, 0))
place(P['water_manhole_cover']['water_manhole_cover_frame'], (0.3, 7.5, 0.0))
place(P['water_manhole_cover']['water_manhole_cover'], (0.3, 7.5, 0.0))
place(P['concrete_road_barrier']['concrete_road_barrier'], (-1.4, 18.0, 0), 0.15)
hyd = place(P['fire_hydrant']['fire_hydrant_aged'], (-1.06, 4.4, 0), 0.5, offset=(-0.3, 0, 0))
recolor(hyd, '#3d4842', 0.3)
for k in ('fire_hydrant_cap_01_aged', 'fire_hydrant_cap_02_aged', 'fire_hydrant_cap_03_aged', 'fire_hydrant_chain_aged'):
    recolor(place(P['fire_hydrant'][k], (-1.06, 4.4, 0), 0.5, offset=(-0.3, 0, 0)), '#3d4842', 0.3)
# fire escape on the left wall, its lowest platform at 3.5 m
for n, o in P['modular_fire_escape'].items():
    place(o, (-2.35, 11.0, 6.5), -math.pi / 2)
# street lamp on the left, its arm over the alley
lamp = place(P['street_lamp_01']['street_lamp_01'], (-2.5, 9.0, 0), -math.pi / 2)

# ---------------------------------------------------------------- Sketchfab props (CC-BY, see CREDITS.md)
SF = os.path.join(ROOT, 'assets', 'sketchfab')


def sf_library(uid):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(SF, uid, 'scene.gltf'))
    objs = [o for o in bpy.data.objects if o not in before]
    col = bpy.data.collections.new('lib_' + uid)
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        col.objects.link(o)
    bpy.context.view_layer.update()
    return {o.name.split('.')[0]: o for o in objs if o.type == 'MESH'}


SP = sf_library('8013d8e6af4645d1a7c3d5b24054bfc8')
# accent: the big dumpster, repainted the scene's one vivid colour (#3c56a6), standing in the sun
for n in ('Object_80', 'Object_82'):
    o = place(SP[n], (1.75, 6.6, 0), math.pi / 2, offset=(-0.265, -3.725, 0))
    recolor(o, '#3c56a6' if n == 'Object_80' else '#2c3f80', 0.3)
for n, (x, y, r) in (('Object_58', (2.5, 5.2, 0.4)), ('Object_60', (2.2, 4.7, 1.2)), ('Object_66', (0.9, 7.3, 0.2))):
    o = SP[n]
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    cxy = ((min(v.x for v in bb) + max(v.x for v in bb)) / 2, (min(v.y for v in bb) + max(v.y for v in bb)) / 2)
    place(o, (x, y, 0), r, offset=(-cxy[0], -cxy[1], 0))
for n in ('Object_44', 'Object_48'):   # two bollards
    o = SP[n]
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    cxy = ((min(v.x for v in bb) + max(v.x for v in bb)) / 2, (min(v.y for v in bb) + max(v.y for v in bb)) / 2)
    place(o, (-2.55, 7.5 if n == 'Object_44' else 9.3, 0), 0, offset=(-cxy[0], -cxy[1], 0))

# ---------------------------------------------------------------- ground
def ground_mat():
    m = bpy.data.materials.new('asphalt')
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.45, 0.45, 0.45)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    d = os.path.join(PH, 'asphalt_02')
    def tex(name, color=True):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(os.path.join(d, name))
        if not color:
            n.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
        return n
    dif = tex('asphalt_02_diff_1k.jpg')
    tint = nt.nodes.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.blend_type = 'MULTIPLY'
    tint.inputs['Factor'].default_value = 0.6; tint.inputs[7].default_value = hexrgb('#6a757d')
    nt.links.new(dif.outputs['Color'], tint.inputs[6])
    nt.links.new(tint.outputs[2], bsdf.inputs['Base Color'])
    rough = tex('asphalt_02_rough_1k.jpg', False)
    # a wet look: lower roughness so the lamps and windows reflect
    mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = 0.7
    nt.links.new(rough.outputs['Color'], mr.inputs[0]); nt.links.new(mr.outputs[0], bsdf.inputs['Roughness'])
    nor = tex('asphalt_02_nor_gl_1k.jpg', False)
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.35
    nt.links.new(nor.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    return m


bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 28, 0))
g = bpy.context.active_object
g.scale = (14, 70, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
g.data.materials.append(ground_mat())

# ---------------------------------------------------------------- character billboard
def billboard(img_path, foot, height, cam_obj, sun_dir):
    img = bpy.data.images.load(img_path)
    w, h = img.size
    width = height * w / h
    m = bpy.data.materials.new('char_flat')
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img; tx.interpolation = 'Cubic'
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.0
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(tx.outputs['Color'], em.inputs['Color'])
    nt.links.new(tx.outputs['Alpha'], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    m.surface_render_method = 'DITHERED'   # writes depth: the depth of field keeps the character sharp
    m.use_transparent_shadow = True

    def plane(name):
        bpy.ops.mesh.primitive_plane_add(size=1)
        p = bpy.context.active_object
        p.name = name
        # plane stands up, bottom edge at the origin
        p.data.transform(__import__('mathutils').Matrix.Translation((0, 0.5, 0)))
        p.rotation_euler = (math.pi / 2, 0, 0)
        p.scale = (width, height, 1)
        p.location = foot
        p.data.materials.append(m)
        return p

    # visible card: faces the camera (yaw only), casts no shadow
    card = plane('character')
    to_cam = cam_obj.location - Vector(foot)
    card.rotation_euler.z = math.atan2(to_cam.y, to_cam.x) - math.pi / 2 + math.pi
    card.rotation_euler.z = math.atan2(-to_cam.x, to_cam.y) + math.pi
    card.visible_shadow = False
    # shadow card: faces the sun, invisible to camera, casts the ground shadow in the light's direction
    sh = plane('character_shadow')
    sh.rotation_euler.z = math.atan2(-sun_dir.x, sun_dir.y)
    sh.visible_camera = False
    sh.visible_glossy = False
    sh.visible_diffuse = False
    return card


# ---------------------------------------------------------------- camera
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = 18 / math.tan(math.radians(14))   # 28 deg vertical field
cam.data.sensor_fit = 'VERTICAL'
cam.data.sensor_height = 36
cam.location = (-0.85, 1.75, 0.9)
target = Vector((-0.55, 6.0, 0.95))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
ROLL = math.radians(3.0)
cam.rotation_euler = (cam.rotation_euler.to_quaternion() @ __import__('mathutils').Quaternion((0, 0, 1), ROLL)).to_euler()

# ---------------------------------------------------------------- light: warm key + cool fill
# key: low golden sun from the far end of the alley, upper left -> lights the right wall tops, long shadows toward camera
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
scene.collection.objects.link(sun)
sun.data.color = hexrgb('#ffb47a')[:3]
sun.data.energy = 8.0
sun.data.angle = math.radians(0.6)
_e, _a = math.radians(26), math.radians(5)
sun.rotation_euler = Vector((-math.sin(_a) * math.cos(_e), math.cos(_a) * math.cos(_e), -math.sin(_e))).to_track_quat('-Z', 'Y').to_euler()
sun_dir = sun.rotation_euler.to_quaternion() @ Vector((0, 0, -1))   # direction light travels

# cool fill: the sky
world = bpy.data.worlds.new('dusk')
world.use_nodes = True
wn = world.node_tree
tc = wn.nodes.new('ShaderNodeTexCoord')
sep = wn.nodes.new('ShaderNodeSeparateXYZ')
nrm = wn.nodes.new('ShaderNodeVectorMath'); nrm.operation = 'NORMALIZE'
wn.links.new(tc.outputs['Generated'], nrm.inputs[0]); wn.links.new(nrm.outputs[0], sep.inputs[0])
ramp = wn.nodes.new('ShaderNodeValToRGB')
cr = ramp.color_ramp
cr.elements[0].position = 0.0; cr.elements[0].color = hexrgb('#e4ae85')
cr.elements[1].position = 0.9; cr.elements[1].color = hexrgb('#352c3f')
e = cr.elements.new(0.12); e.color = hexrgb('#d99a8a')
e = cr.elements.new(0.3); e.color = hexrgb('#7d6390')
wn.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
bg = wn.nodes['Background']; bg.inputs['Strength'].default_value = 0.22
wn.links.new(ramp.outputs['Color'], bg.inputs['Color'])
scene.world = world

# street lamp light, with a bright bulb for the halo
lamp_light = bpy.data.objects.new('lamp', bpy.data.lights.new('lamp', 'POINT'))
scene.collection.objects.link(lamp_light)
lamp_light.data.color = hexrgb('#ffc46a')[:3]
lamp_light.data.energy = 350
lamp_light.data.shadow_soft_size = 0.15
lamp_light.location = lamp.matrix_world @ Vector((0, 0, 0)) + Vector((1.45, 0, 3.55))
# warm spill from a shop doorway on the left, near the character
spill = bpy.data.objects.new('spill', bpy.data.lights.new('spill', 'AREA'))
scene.collection.objects.link(spill)
spill.data.color = hexrgb('#f0c060')[:3]; spill.data.energy = 120; spill.data.size = 1.5
spill.location = (-2.6, 3.4, 2.2); spill.rotation_euler = (0, math.radians(-80), 0)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charkit
UNIT = 0.42                                   # 1 unit = head width = 0.42 m
bpy.context.view_layer.update()
to_light_w = -sun_dir
to_light_c = cam.rotation_euler.to_quaternion().inverted() @ to_light_w    # camera space: x right, y up, z to camera
LIGHT = {'dir': tuple(to_light_c), 'key': '#ffd6ad', 'shadow': '#6a6fae', 'floor': 0.45, 'rim': 0.5,
         'hardness': 0.03, 'headShadow': 0.45}
hero = charkit.Character(charkit.load(os.path.join(ROOT, 'characters', 'theo.json')))
FACE = os.environ.get('FACE', 'fear')
os.makedirs(os.path.join(ROOT, 'renders', 'tmp'), exist_ok=True)
char_png = os.path.join(ROOT, 'renders', 'tmp', 'theo_shot.png')
hero.draw(FACE, 'front', LIGHT).save(char_png)
CARD_H = charkit.CH / charkit.D * UNIT
FEET = (charkit.CH - (hero.layout()[1])) / charkit.D * UNIT     # feet height above the card's bottom edge
char = billboard(char_png, (-0.55, 6.0, -FEET), CARD_H, cam, sun_dir)
# depth of field (section 6): focus on the character, the set behind softens, the character stays sharp
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (Vector((-0.55, 6.0, 1.0)) - cam.location).length
cam.data.dof.aperture_fstop = 5.6

# ---------------------------------------------------------------- toon shading of the set
# Cel-leaning look of the references: flat colour shapes, one clear shadow edge, cool shade / warm light,
# texture detail reduced to a "painted" hint. The flat character and the glowing windows are left alone.
import numpy as np
AVG = {}


def image_average(img):
    if img.name not in AVG:
        n = img.size[0] * img.size[1] * img.channels
        a = np.empty(n, dtype=np.float32)
        img.pixels.foreach_get(a)
        AVG[img.name] = tuple(a.reshape(-1, img.channels)[:, :3].mean(0)) + (1.0,)
    return AVG[img.name]


def toonify(m):
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if bsdf is None or out is None:
        return
    if bsdf.inputs['Emission Strength'].default_value > 0 and bsdf.inputs['Emission Color'].default_value[0] > 0.5:
        return
    bl = bsdf.inputs['Base Color'].links
    base = bl[0].from_socket if bl else None
    # flatten the texture: 50 % towards its own average colour
    flat = nt.nodes.new('ShaderNodeMix'); flat.data_type = 'RGBA'
    flat.inputs['Factor'].default_value = 0.0 if m.get('accent') else 0.5
    tex = next((n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name != 'Non-Color'), None)
    if base is not None:
        nt.links.new(base, flat.inputs[6])
        flat.inputs[7].default_value = image_average(tex.image) if tex else (0.5, 0.5, 0.5, 1)
    else:
        flat.inputs[6].default_value = bsdf.inputs['Base Color'].default_value
        flat.inputs[7].default_value = bsdf.inputs['Base Color'].default_value
    sat = nt.nodes.new('ShaderNodeHueSaturation'); sat.inputs['Saturation'].default_value = 1.2
    nt.links.new(flat.outputs[2], sat.inputs['Color'])
    # light received, as a colour
    dif = nt.nodes.new('ShaderNodeBsdfDiffuse'); dif.inputs['Color'].default_value = (1, 1, 1, 1)
    nl = bsdf.inputs['Normal'].links
    if nl:
        nt.links.new(nl[0].from_socket, dif.inputs['Normal'])
    s2r = nt.nodes.new('ShaderNodeShaderToRGB'); nt.links.new(dif.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(s2r.outputs['Color'], bw.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB'); r = ramp.color_ramp; r.interpolation = 'EASE'
    r.elements[0].position = 0.0; r.elements[0].color = (0.13, 0.12, 0.24, 1)     # deep cool shade
    r.elements[1].position = 0.9; r.elements[1].color = (1.25, 1.02, 0.80, 1)    # warm sunlight
    e = r.elements.new(0.18); e.color = (0.24, 0.21, 0.38, 1)                       # shade
    e = r.elements.new(0.42); e.color = (0.40, 0.34, 0.52, 1)                       # shadow edge starts
    e = r.elements.new(0.50); e.color = (1.0, 0.82, 0.66, 1)                        # ... and ends: a clear edge
    nt.links.new(bw.outputs[0], ramp.inputs['Fac'])
    m1 = nt.nodes.new('ShaderNodeMix'); m1.data_type = 'RGBA'; m1.blend_type = 'MULTIPLY'; m1.inputs['Factor'].default_value = 1
    nt.links.new(sat.outputs[0], m1.inputs[6]); nt.links.new(ramp.outputs['Color'], m1.inputs[7])
    # local coloured light (lamp, door spill, windows) on top
    m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'; m2.inputs['Factor'].default_value = 1
    nt.links.new(sat.outputs[0], m2.inputs[6]); nt.links.new(s2r.outputs['Color'], m2.inputs[7])
    add = nt.nodes.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['Factor'].default_value = 0.35
    nt.links.new(m1.outputs[2], add.inputs[6]); nt.links.new(m2.outputs[2], add.inputs[7])
    em = nt.nodes.new('ShaderNodeEmission'); nt.links.new(add.outputs[2], em.inputs['Color'])
    nt.links.new(em.outputs[0], out.inputs['Surface'])


SKIP = ('window_warm', 'char_flat', 'haze')
for m in bpy.data.materials:
    if m.node_tree and not m.name.startswith(SKIP):
        toonify(m)

# ---------------------------------------------------------------- render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = int(1080 * SCALE)
scene.render.resolution_y = int(1920 * SCALE)
scene.render.resolution_percentage = 100
scene.render.fps = 30
ee = scene.eevee
ee.taa_render_samples = SAMPLES
for attr, val in (('use_raytracing', True), ('use_shadows', True), ('shadow_ray_count', 2), ('shadow_step_count', 8),
                  ('use_volumetric_shadows', False), ('volumetric_tile_size', '8')):
    if hasattr(ee, attr):
        setattr(ee, attr, val)
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0.0

# toon outline on the set: Freestyle, about 2 px, a dark ink
scene.render.use_freestyle = True
scene.render.line_thickness_mode = 'ABSOLUTE'
scene.render.line_thickness = 1.6 * SCALE
vl = scene.view_layers[0]
vl.use_freestyle = True
ls = vl.freestyle_settings.linesets[0] if vl.freestyle_settings.linesets else vl.freestyle_settings.linesets.new('lines')
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new('ink')
ls.select_by_visibility = True
ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True
ls.linestyle.color = hexrgb('#1d1b2a')[:3]
ls.linestyle.alpha = 1.0
ls.linestyle.thickness = 2.2 * SCALE
# ink lines fade with distance so they never sit sharp on a blurred background
_am = ls.linestyle.alpha_modifiers.new('fade', 'DISTANCE_FROM_CAMERA')
_am.range_min = 6.0; _am.range_max = 18.0; _am.mapping = 'LINEAR'; _am.invert = True
# the character is drawn already: keep Freestyle off it
char_col = bpy.data.collections.new('flat'); scene.collection.children.link(char_col)
for o in bpy.data.objects:
    if o.name.startswith('character'):
        for c in o.users_collection:
            c.objects.unlink(o)
        char_col.objects.link(o)
ls.select_by_collection = True
ls.collection = char_col
ls.collection_negation = 'EXCLUSIVE'

# atmosphere: a thin haze so the lamp and the far end glow
vol = bpy.data.materials.new('haze'); vol.use_nodes = True
vn = vol.node_tree
vn.nodes.remove(vn.nodes['Principled BSDF'])
pv = vn.nodes.new('ShaderNodeVolumePrincipled'); pv.inputs['Density'].default_value = float(os.environ.get('HAZE', '0.004'))
pv.inputs['Color'].default_value = hexrgb('#b9a7c9')
vn.links.new(pv.outputs[0], vn.nodes['Material Output'].inputs['Volume'])
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 18, 8))
hz = bpy.context.active_object; hz.name = 'haze'; hz.scale = (6, 48, 16); hz.data.materials.append(vol)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
scene.render.filepath = OUT
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print('WROTE', OUT)
