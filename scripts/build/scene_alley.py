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
place(P['fire_hydrant']['fire_hydrant_aged'], (-1.75, 3.3, 0), 0.5, offset=(-0.3, 0, 0))
for k in ('fire_hydrant_cap_01_aged', 'fire_hydrant_cap_02_aged', 'fire_hydrant_cap_03_aged', 'fire_hydrant_chain_aged'):
    place(P['fire_hydrant'][k], (-1.75, 3.3, 0), 0.5, offset=(-0.3, 0, 0))
# fire escape on the left wall, its lowest platform at 3.5 m
for n, o in P['modular_fire_escape'].items():
    place(o, (-2.35, 11.0, 6.5), -math.pi / 2)
# street lamp on the left, its arm over the alley
lamp = place(P['street_lamp_01']['street_lamp_01'], (-2.5, 9.0, 0), -math.pi / 2)

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
    m.surface_render_method = 'BLENDED' if hasattr(m, 'surface_render_method') else None
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
cam.data.lens = 27
cam.data.sensor_fit = 'VERTICAL'
cam.data.sensor_height = 36
cam.location = (-1.35, 1.95, 1.4)
target = Vector((-0.45, 4.6, 0.98))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()

# ---------------------------------------------------------------- light: warm key + cool fill
# key: low golden sun from the far end of the alley, upper left -> lights the right wall tops, long shadows toward camera
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
scene.collection.objects.link(sun)
sun.data.color = hexrgb('#ffb47a')[:3]
sun.data.energy = 3.2
sun.data.angle = math.radians(2.5)
sun.rotation_euler = Euler((math.radians(-63), 0, math.radians(-5)))
sun_dir = sun.matrix_world.to_quaternion() @ Vector((0, 0, -1))   # direction light travels

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
cr.elements[1].position = 0.55; cr.elements[1].color = hexrgb('#352c3f')
e = cr.elements.new(0.12); e.color = hexrgb('#d99a8a')
e = cr.elements.new(0.3); e.color = hexrgb('#7d6390')
wn.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
bg = wn.nodes['Background']; bg.inputs['Strength'].default_value = 1.0
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

char = billboard(os.path.join(CHAR, 'courier_neutral.png'), (-0.55, 4.6, 0.0), 1.85, cam, sun_dir)

# ---------------------------------------------------------------- render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = int(1080 * SCALE)
scene.render.resolution_y = int(1920 * SCALE)
scene.render.resolution_percentage = 100
scene.render.fps = 30
ee = scene.eevee
ee.taa_render_samples = SAMPLES
for attr, val in (('use_raytracing', True), ('use_shadows', True), ('shadow_ray_count', 2), ('shadow_step_count', 8),
                  ('use_volumetric_shadows', True), ('volumetric_tile_size', '8')):
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
ls.linestyle.alpha = 0.8
ls.linestyle.thickness = 1.6 * SCALE
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
pv = vn.nodes.new('ShaderNodeVolumePrincipled'); pv.inputs['Density'].default_value = 0.012
pv.inputs['Color'].default_value = hexrgb('#b9a7c9')
vn.links.new(pv.outputs[0], vn.nodes['Material Output'].inputs['Volume'])
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 18, 8))
hz = bpy.context.active_object; hz.name = 'haze'; hz.scale = (6, 48, 16); hz.data.materials.append(vol)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
scene.render.filepath = OUT
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print('WROTE', OUT)
