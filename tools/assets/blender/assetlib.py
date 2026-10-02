# blender -b -P assetlib.py -- outdir name [name ...]    (or "all")
# 3D asset library -> transparent ortho renders, later pixelised by forge/pixelize.py
import bpy, sys, math, random, bmesh
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
OUT = args[0]; WANT = args[1:]

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 28; sc.cycles.use_denoising = False
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGBA'
    sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs[1].default_value = 0.0
    return sc

def mat(col, metal=0.5, rough=0.5, emit=None, es=0.0):
    m = bpy.data.materials.new('m'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = es
    return m
def hexc(h): h = h.lstrip('#'); return tuple(pow(int(h[i:i + 2], 16) / 255, 2.2) for i in (0, 2, 4))
STEEL = lambda: mat(hexc('#8a909c'), 0.6, 0.45); STEEL2 = lambda: mat(hexc('#555b68'), 0.6, 0.5); DARK = lambda: mat(hexc('#14161c'), 0.7, 0.5)
ORANGE = lambda: mat(hexc('#d4660c'), 0.3, 0.5); WHITE = lambda: mat(hexc('#d9dde5'), 0.4, 0.4)
def glow(h, s=8): c = hexc(h); return mat(c, 0, 0.3, c, max(0.8, s * 0.35))

def box(loc, size, m, bev=0.03, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.scale = [s / 2 for s in size]
    bpy.ops.object.transform_apply(scale=True)
    if bev: md = o.modifiers.new('b', 'BEVEL'); md.width = bev; md.segments = 2
    o.data.materials.append(m); return o
def cyl(loc, r, d, m, rot=(0, 0, 0), v=24, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(location=loc, radius=r, depth=d, vertices=v, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(location=loc, radius1=r, radius2=r2, depth=d, vertices=v, rotation=rot)
    o = bpy.context.object; o.data.materials.append(m); return o
def sph(loc, r, m, scale=(1, 1, 1), seg=20):
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc, radius=r, segments=seg, ring_count=seg // 2); o = bpy.context.object; o.scale = scale
    o.data.materials.append(m); return o

def lights(key=3.2, rim=(0.5, 0.65, 1.0)):
    bpy.ops.object.light_add(type='SUN'); l = bpy.context.object; l.data.energy = key; l.data.color = (1, 0.93, 0.85); l.rotation_euler = (math.radians(50), 0, math.radians(35))
    bpy.ops.object.light_add(type='SUN'); l = bpy.context.object; l.data.energy = 1.2; l.data.color = rim; l.rotation_euler = (math.radians(60), 0, math.radians(-140))

def render(name, scale, elev=55, yaw=0, res=512, center=(0, 0, 0.4), key=3.2):
    sc = bpy.context.scene; lights(key)
    bpy.ops.object.camera_add(); cam = bpy.context.object; cam.data.type = 'ORTHO'; cam.data.ortho_scale = scale; sc.camera = cam
    d = 20; e = math.radians(elev); y = math.radians(yaw)
    cam.location = (center[0] + d * math.sin(y) * math.cos(e), center[1] - d * math.cos(y) * math.cos(e), center[2] + d * math.sin(e))
    cam.rotation_euler = (math.radians(90 - elev), 0, y)
    sc.render.resolution_x = res; sc.render.resolution_y = res; sc.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)

# ---------------- builders ----------------
def b_cabinet(accent='#ff9a2a', seed=1, tall=1.6):
    random.seed(seed); box((0, 0, tall / 2), (1.2, 0.9, tall), STEEL2())
    box((0, -0.43, tall / 2), (1.0, 0.06, tall - 0.2), DARK()); box((0, 0, tall + 0.04), (1.26, 0.96, 0.1), STEEL())
    for r in range(int(tall / 0.28)):
        for c in range(4):
            if random.random() < 0.6: box((-0.4 + c * 0.27, -0.48, 0.2 + r * 0.26), (0.14, 0.05, 0.09), glow(random.choice([accent, '#3fffe6', '#6cff6c', accent]), 7), 0.005)
    box((0, -0.48, tall - 0.12), (0.9, 0.04, 0.1), glow(accent, 5), 0.005)
    render('cabinet_%d' % seed, 3.6, elev=38, yaw=0, center=(0, 0, tall / 2))
def b_console(accent='#3fffe6', seed=1):
    box((0, 0, 0.35), (1.6, 0.9, 0.7), STEEL2()); box((0, 0.2, 0.85), (1.5, 0.12, 0.7), DARK(), rot=(math.radians(-18), 0, 0))
    box((0, 0.13, 0.86), (1.3, 0.05, 0.52), glow(accent, 5), 0.004, rot=(math.radians(-18), 0, 0))
    for i in range(7): box((-0.65 + i * 0.22, -0.3, 0.74), (0.14, 0.1, 0.04), glow(random.choice(['#ff9a2a', '#6cff6c', accent]), 6), 0.004)
    box((0, -0.05, 0.71), (1.62, 0.92, 0.04), STEEL())
    render('console_%d' % seed, 3.2, elev=42, center=(0, 0, 0.5))
def b_tank(accent='#ffb020', color='#4a8a5a'):
    cyl((0, 0, 0.7), 0.45, 1.4, mat(hexc(color), 0.5, 0.4)); sph((0, 0, 1.4), 0.45, mat(hexc(color), 0.5, 0.4), (1, 1, 0.45))
    for z in (0.3, 1.1): cyl((0, 0, z), 0.48, 0.1, STEEL())
    cyl((0, 0, 0.7), 0.465, 0.22, glow(accent, 3)); cyl((0, 0, 0.04), 0.5, 0.08, DARK())
    render('tank_' + color.strip('#'), 2.6, center=(0, 0, 0.8))
def b_crate(color='#d4660c', seed=1):
    random.seed(seed); m = mat(hexc(color), 0.3, 0.5); box((0, 0, 0.4), (0.9, 0.9, 0.8), m, 0.04)
    for sx in (-0.4, 0.4):
        for sy in (-0.4, 0.4): box((sx, sy, 0.4), (0.1, 0.1, 0.84), STEEL2(), 0.01)
    box((0, 0, 0.82), (0.95, 0.95, 0.06), STEEL2(), 0.01); box((0, -0.46, 0.4), (0.5, 0.03, 0.3), glow('#ffd84a', 2), 0.004)
    render('crate_%s' % color.strip('#'), 2.2, center=(0, 0, 0.4))
def b_generator(seed=1):
    box((0, 0, 0.5), (1.6, 1.0, 1.0), STEEL2()); cyl((0, -0.1, 1.15), 0.4, 0.5, STEEL(), rot=(0, math.pi / 2, 0)); box((0, -0.52, 0.55), (1.0, 0.04, 0.5), glow('#3fffe6', 6), 0.004)
    for i in range(3): cyl((-0.5 + i * 0.5, 0.2, 1.1), 0.12, 0.5, DARK()); box((-0.5 + i * 0.5, 0.2, 1.38), (0.2, 0.2, 0.05), glow('#ff9a2a', 4), 0.004)
    render('generator_%d' % seed, 3.6, elev=42, center=(0, 0, 0.6))
def b_locker():
    box((0, 0, 0.9), (0.9, 0.6, 1.8), STEEL2()); box((-0.22, -0.31, 0.95), (0.4, 0.03, 1.5), STEEL(), 0.005); box((0.22, -0.31, 0.95), (0.4, 0.03, 1.5), STEEL(), 0.005)
    box((0, -0.33, 1.6), (0.7, 0.03, 0.1), glow('#ff9a2a', 5), 0.003); render('locker', 3.2, elev=38, center=(0, 0, 0.9))
def b_reactor():
    box((0, 0, 0.1), (3.0, 3.0, 0.2), STEEL2(), 0.08)
    cyl((0, 0, 0.3), 1.3, 0.2, STEEL(), v=8); cyl((0, 0, 0.48), 1.05, 0.2, STEEL2(), v=8)
    cyl((0, 0, 1.75), 0.8, 2.6, mat(hexc('#c8f4ff'), 0, 0.05)); cyl((0, 0, 1.75), 0.62, 2.55, glow('#18d8f0', 16)); cyl((0, 0, 1.75), 0.26, 2.6, glow('#d8fffc', 22))
    for z in (0.75, 1.55, 2.4): cyl((0, 0, z), 0.92, 0.12, STEEL())
    cyl((0, 0, 3.12), 0.98, 0.22, STEEL(), v=8); cyl((0, 0, 3.28), 0.55, 0.14, glow('#18d8f0', 12))
    for sx, sy in ((-1.2, -1.2), (1.2, -1.2), (-1.2, 1.2), (1.2, 1.2)):
        cyl((sx, sy, 0.8), 0.18, 1.2, STEEL2()); box((sx, sy, 1.45), (0.3, 0.3, 0.1), glow('#ff9a2a', 12), 0.01)
    render('reactor_core', 5.4, elev=40, center=(0, 0, 1.6), res=640, key=4.0)
def b_crystal(color='#3fa0ff', seed=1, n=6):
    random.seed(seed); g = glow(color, 6); g2 = glow(color, 2.5)
    for i in range(n):
        a = random.uniform(0, 6.28); r = random.uniform(0.05, 0.4) if i else 0; h = random.uniform(0.5, 1.2) * (1.4 if i == 0 else 1); w = random.uniform(0.09, 0.17)
        x, y = math.cos(a) * r, math.sin(a) * r; tilt = random.uniform(-0.3, 0.3)
        o = cyl((x, y, h / 2), w, h * 0.7, g2 if i % 2 else g, v=6, rot=(tilt, random.uniform(-0.3, 0.3), 0))
        cyl((x + math.sin(tilt) * h * 0.1, y, h * 0.7 + h * 0.15), w * 0.001 + 0.01, h * 0.3, g, v=6, r2=w, rot=(tilt, 0, 0))
    render('crystal_%s_%d' % (color.strip('#'), seed), 1.9, center=(0, 0, 0.5))
def b_tentacle(color='#d03a8a', orb='#ff3ad0', seed=1):
    random.seed(seed); m = mat(hexc(color), 0, 0.45, hexc(color), 0.6); g = glow(orb, 10)
    for k in range(3):
        a = k * 2.1 + random.random(); x = y = 0.0; z = 0.0; rad = 0.2
        for i in range(14):
            t = i / 13; x += math.cos(a) * 0.07 * (1 - t * 0.2); y += math.sin(a) * 0.07; z += 0.12; a += random.uniform(-0.15, 0.25)
            sph((x, y, z), rad * (1 - t * 0.55), m, seg=12)
        sph((x, y, z + 0.12), 0.2, g, seg=14)
    render('tentacle_%d' % seed, 3.4, center=(0.3, 0, 0.9))
def b_rosette(color='#2fbf5a', tip='#b8ff4a', seed=1, n=9):
    random.seed(seed); m = mat(hexc(color), 0, 0.5, hexc(color), 0.5); g = glow(tip, 6)
    for i in range(n):
        a = i * 6.28 / n + random.uniform(-0.2, 0.2); L = random.uniform(0.5, 0.75)
        o = cyl((math.cos(a) * L * 0.4, math.sin(a) * L * 0.4, 0.22 + 0.1 * (i % 2)), 0.001 + 0.04, L, m, r2=0.1, rot=(math.sin(a) * 1.0, -math.cos(a) * 1.0, 0)); o.scale = (1.6, 1, 1)
    sph((0, 0, 0.3), 0.14, g, seg=12); render('rosette_%s_%d' % (color.strip('#'), seed), 2.2, center=(0, 0, 0.3))
def b_mushroom(color='#ff8a2a', seed=1):
    random.seed(seed); g = glow(color, 5); st = mat(hexc('#c9a97a'), 0, 0.8)
    for x, y, s in ((0, 0, 1), (0.35, 0.1, 0.65), (-0.3, 0.2, 0.5)):
        cyl((x, y, 0.25 * s), 0.07 * s, 0.5 * s, st); sph((x, y, 0.52 * s), 0.3 * s, g, (1, 1, 0.55), 16)
    render('mushroom_%s' % color.strip('#'), 1.6, center=(0, 0, 0.3))
def b_asteroid(seed=1, size=1.0, ore='#ff8a2a'):
    random.seed(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.0); o = bpy.context.object
    rock = mat(hexc(random.choice(['#6a625a', '#5a5660', '#76685a'])), 0.1, 0.95); veins = glow(ore, 3)
    o.data.materials.append(rock); o.data.materials.append(veins)
    tex = bpy.data.textures.new('c', 'CLOUDS'); tex.noise_scale = random.uniform(0.7, 1.2); tex.noise_depth = 3
    d = o.modifiers.new('d', 'DISPLACE'); d.texture = tex; d.strength = 0.65; d.mid_level = 0.45
    tex2 = bpy.data.textures.new('v', 'VORONOI'); tex2.noise_scale = 0.5; d2 = o.modifiers.new('d2', 'DISPLACE'); d2.texture = tex2; d2.strength = 0.12
    o.scale = (random.uniform(1, 1.3), random.uniform(0.8, 1.1), random.uniform(0.7, 1.0))
    bpy.ops.object.modifier_apply(modifier='d'); bpy.ops.object.modifier_apply(modifier='d2')
    for p in o.data.polygons:
        if random.random() < 0.025: p.material_index = 1
    bpy.ops.object.shade_flat(); render('asteroid_%d' % seed, 3.4, elev=40, center=(0, 0, 0), key=4.5)
def b_ship(name='freighter', body='#e9ecf2', trim='#e8761a', lamp=None, scale=1.0, yaw=-26, big=True):
    random.seed(3)
    HULL = mat(hexc(body), 0.45, 0.4); HULL2 = mat(hexc('#7b8190'), 0.6, 0.4); D = DARK(); O = mat(hexc(trim), 0.3, 0.45)
    FL = mat(hexc('#1a4cff'), 0, 0.3, hexc('#2a60ff'), 1.5); FL2 = mat(hexc('#6aa8ff'), 0, 0.3, hexc('#5a9cff'), 2.2)
    WIN = glow(lamp or '#7fe8ff', 6)
    k = 1.0 if big else 0.7
    # fuselage: stacked blocks tapering to the nose (+X)
    box((0, 0, 0), (4.4 * k, 1.7 * k, 0.95 * k), HULL)
    box((0.3 * k, 0, 0.55 * k), (3.2 * k, 1.35 * k, 0.28 * k), HULL2)
    box((2.5 * k, 0, -0.02), (1.4 * k, 1.35 * k, 0.8 * k), HULL, rot=(0, 0, 0))
    box((3.3 * k, 0, -0.1), (0.9 * k, 0.9 * k, 0.6 * k), HULL2)
    cyl((3.95 * k, 0, -0.1), 0.001 + 0.2 * k, 0.5 * k, HULL, rot=(0, math.pi / 2, 0), v=8, r2=0.42 * k)
    box((2.2 * k, 0, 0.82 * k), (1.1 * k, 0.9 * k, 0.45 * k), HULL2); box((2.72 * k, 0, 0.88 * k), (0.14 * k, 0.76 * k, 0.26 * k), WIN, 0.004)
    # side pods + wings
    for sy in (-1, 1):
        box((-0.2 * k, sy * 1.15 * k, -0.12), (2.7 * k, 0.7 * k, 0.8 * k), HULL)
        for i in range(4): box(((-1.3 + i * 0.75) * k, sy * 1.15 * k, 0.3 * k), (0.34 * k, 0.55 * k, 0.07), O, 0.01)
        box((-1.2 * k, sy * 1.75 * k, -0.28), (1.5 * k, 0.55 * k, 0.2), HULL2); box((0.6 * k, sy * 1.5 * k, -0.28), (0.9 * k, 0.4 * k, 0.16), HULL)
        ex = -2.4 * k
        cyl((ex, sy * 0.78 * k, 0), 0.6 * k, 1.3 * k, D, rot=(0, math.pi / 2, 0)); cyl((ex + 0.5 * k, sy * 0.78 * k, 0), 0.68 * k, 0.16, HULL2, rot=(0, math.pi / 2, 0))
        cyl((ex - 0.7 * k, sy * 0.78 * k, 0), 0.47 * k, 0.14, FL2, rot=(0, math.pi / 2, 0))
        cyl((ex - 1.45 * k, sy * 0.78 * k, 0), 0.47 * k, 1.5 * k, FL, rot=(0, math.pi / 2, 0), r2=0.04)   # cone flame
    # greebles
    for i in range(9): box(((-1.9 + i * 0.62) * k, random.uniform(-0.45, 0.45) * k, 0.72 * k), (0.4 * k, 0.3 * k, 0.07), random.choice([HULL, HULL2, D, O]), 0.01)
    box((0.3 * k, 0.5 * k, 0.95 * k), (0.07, 0.07, 0.6 * k), D); box((0.3 * k, 0.5 * k, 1.3 * k), (0.45 * k, 0.45 * k, 0.05), HULL)
    if lamp: cyl((4.2 * k, 0, -0.1), 0.14 * k, 0.2, glow(lamp, 25), rot=(0, math.pi / 2, 0))
    render('ship_' + name, 9.6 * scale, yaw=yaw, center=(0, 0, 0), res=640, key=5.2)

def b_incubator(color='#4aff6a', plant='#2fbf5a', seed=1):
    random.seed(seed); L = glow(color, 3.2); G = mat(hexc('#bfe8e0'), 0, 0.05)
    cyl((0, 0, 0.12), 0.5, 0.24, STEEL2()); cyl((0, 0, 1.55), 0.5, 0.2, STEEL2()); cyl((0, 0, 0.82), 0.4, 1.3, L); cyl((0, 0, 0.82), 0.44, 1.32, G)
    for z in (0.35, 1.3): cyl((0, 0, z), 0.47, 0.06, STEEL())
    for i in range(5):
        a = i * 1.25; cyl((math.cos(a) * 0.08, math.sin(a) * 0.08, 0.5 + i * 0.08), 0.001 + 0.03, 0.55, mat(hexc(plant), 0, 0.5, hexc(plant), 0.5), r2=0.1, rot=(math.sin(a) * 0.9, -math.cos(a) * 0.9, 0))
    box((0.42, -0.42, 0.18), (0.14, 0.06, 0.1), glow('#ff9a2a', 5), 0.004); render('incubator_%s' % color.strip('#'), 3.2, elev=42, center=(0, 0, 0.85))
def b_flower(color='#f0c020', seed=1):
    random.seed(seed); m = mat(hexc(color), 0, 0.5, hexc(color), 0.9); g = mat(hexc('#2fbf5a'), 0, 0.6)
    for i in range(6):
        a = i * 1.1; cyl((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.2), 0.001 + 0.03, 0.5, g, r2=0.07, rot=(math.sin(a) * 1.1, -math.cos(a) * 1.1, 0))
    for x, y, z in ((0, 0, 0.55), (0.28, 0.1, 0.45), (-0.25, 0.15, 0.4)): sph((x, y, z), 0.22, m, (1, 1, 0.5), 14)
    render('flower_%s' % color.strip('#'), 1.9, center=(0, 0, 0.35))

def b_ship_hero():
    random.seed(11)
    PL = mat(hexc('#d6d6e2'), 0.3, 0.6); PL2 = mat(hexc('#a8a8ba'), 0.35, 0.6); GM = mat(hexc('#23252f'), 0.7, 0.45); GM2 = mat(hexc('#3a3d4a'), 0.7, 0.4)
    YL = mat(hexc('#e9b61c'), 0.2, 0.5); OR = mat(hexc('#ff8a14'), 0.2, 0.5); WH = mat(hexc('#e8e8f0'), 0.3, 0.5); BK = mat(hexc('#0c0c12'), 0.3, 0.6)
    RING = glow('#27a0ff', 8); WIN = glow('#ff8a14', 9); GLASS = mat(hexc('#10141c'), 0.9, 0.12)
    # hull core + layered top plates
    box((0, 0, 0.1), (4.4, 2.1, 1.8), PL2, 0.05)
    for i, x in enumerate((-1.5, -0.1, 1.3)): box((x, 0.1, 0.9), (1.34, 1.85, 0.3), PL, 0.05)
    box((0.8, -0.55, 0.62), (2.8, 0.9, 0.35), PL, 0.05)
    # side wall plates with windows (camera side = -Y)
    for x in (-1.5, -0.2, 1.1): box((x, -1.06, 0.15), (1.2, 0.1, 0.9), PL, 0.04)
    for x in (-1.5, -0.2, 1.1):
        for k in range(random.randint(2, 4)): box((x + random.uniform(-0.45, 0.45), -1.14, random.uniform(-0.15, 0.45)), (0.12, 0.05, 0.12), WIN, 0.004)
        for k in range(3): box((x + random.uniform(-0.5, 0.5), -1.13, random.uniform(-0.2, 0.5)), (0.07, 0.04, 0.07), BK, 0.004)
    box((0.9, -1.1, -0.45), (2.2, 0.08, 0.28), GLASS, 0.01)
    for i in range(7): box((0.0 + i * 0.28, -1.15, -0.45), (0.09, 0.04, 0.12), WIN, 0.003)
    # lower cargo + hazard cylinder + orange belly box
    box((0.2, 0, -1.0), (3.8, 1.9, 0.5), GM2, 0.05)
    cyl((0.4, -1.12, -1.0), 0.32, 3.0, WH, rot=(0, math.pi / 2, 0), v=20)
    for i in range(9): cyl((-0.9 + i * 0.36, -1.12, -1.0), 0.335, 0.17, OR if i % 2 == 0 else YL, rot=(0, math.pi / 2, 0), v=20)
    box((0.9, -0.2, -1.4), (1.3, 1.0, 0.3), mat(hexc('#ff9a1a'), 0.1, 0.4, hexc('#ff8a14'), 3), 0.04)
    # nose: stepped yellow wedge + dark windscreen
    box((2.75, 0, -0.05), (1.0, 2.0, 1.5), YL, 0.07); box((3.3, 0, -0.1), (0.9, 1.6, 1.2), YL, 0.07); box((3.75, 0, -0.15), (0.7, 1.15, 0.85), YL, 0.07)
    box((3.1, -0.05, 0.7), (1.1, 1.3, 0.3), GLASS, 0.05); box((3.62, -0.9, 0.0), (0.5, 0.06, 0.5), GLASS, 0.03); box((2.3, 0, 0.3), (0.3, 1.9, 1.3), mat(hexc('#2a2d38'), 0.5, 0.5), 0.04)
    for k in range(3): box((3.0 + k * 0.4, -1.03 - 0.0, -0.5), (0.3, 0.05, 0.12), mat(hexc('#2a2418'), 0.3, 0.6), 0.004)
    # top turret + barrel with red tip
    cyl((1.7, 0.75, 1.2), 0.38, 0.45, GM, v=20); cyl((1.7, 0.75, 1.5), 0.3, 0.2, GM2, v=20)
    cyl((2.5, 0.75, 1.5), 0.1, 1.0, WH, rot=(0, math.pi / 2, 0), v=12); cyl((3.05, 0.75, 1.5), 0.11, 0.18, mat(hexc('#e0242a'), 0.2, 0.5, hexc('#e0242a'), 2), rot=(0, math.pi / 2, 0), v=12)
    # striped rod (upper rear)
    cyl((-1.7, 0.55, 1.35), 0.27, 2.6, WH, rot=(0, math.pi / 2, 0), v=20)
    for i in range(7): cyl((-2.7 + i * 0.37, 0.55, 1.35), 0.285, 0.15, OR, rot=(0, math.pi / 2, 0), v=20)
    # engines (near big, far smaller) with glowing rings
    cyl((-2.9, -0.55, -0.15), 0.98, 2.7, GM, rot=(0, math.pi / 2, 0), v=28)
    for dx in (-1.6, -0.9, -0.2, 0.5): cyl((-2.9 + dx + 0.6, -0.55, -0.15), 1.0, 0.1, GM2, rot=(0, math.pi / 2, 0), v=28)
    cyl((-4.28, -0.55, -0.15), 0.86, 0.12, GM2, rot=(0, math.pi / 2, 0), v=28); cyl((-4.36, -0.55, -0.15), 0.82, 0.05, RING, rot=(0, math.pi / 2, 0), v=28); cyl((-4.41, -0.55, -0.15), 0.66, 0.05, glow('#1646d8', 3), rot=(0, math.pi / 2, 0), v=28); cyl((-4.44, -0.55, -0.15), 0.24, 0.05, glow('#7ac4ff', 7), rot=(0, math.pi / 2, 0), v=28); cyl((-4.38, -0.55, -0.15), 0.34, 0.06, glow('#58b4ff', 14), rot=(0, math.pi / 2, 0), v=28)
    cyl((-2.7, 1.0, 0.55), 0.8, 2.4, GM, rot=(0, math.pi / 2, 0), v=28)
    for dx in (-1.2, -0.5, 0.2): cyl((-2.7 + dx + 0.5, 1.0, 0.55), 0.82, 0.09, GM2, rot=(0, math.pi / 2, 0), v=28)
    cyl((-3.95, 1.0, 0.55), 0.72, 0.1, GM2, rot=(0, math.pi / 2, 0), v=28); cyl((-4.03, 1.0, 0.55), 0.68, 0.05, RING, rot=(0, math.pi / 2, 0), v=28); cyl((-4.08, 1.0, 0.55), 0.54, 0.05, glow('#1646d8', 3), rot=(0, math.pi / 2, 0), v=28); cyl((-4.11, 1.0, 0.55), 0.2, 0.05, glow('#7ac4ff', 7), rot=(0, math.pi / 2, 0), v=28); cyl((-4.05, 1.0, 0.55), 0.28, 0.06, glow('#58b4ff', 14), rot=(0, math.pi / 2, 0), v=28)
    for x in (-1.5, -0.1, 1.3): box((x, -0.6, 1.05), (1.2, 0.5, 0.12), PL, 0.03)
    box((2.0, -0.35, 1.02), (0.6, 0.7, 0.16), PL2, 0.03); box((-1.0, -1.1, 0.75), (0.6, 0.06, 0.4), mat(hexc('#14213a'), 0.5, 0.3, hexc('#2a6aff'), 1.2), 0.01)
    for i in range(16): box((random.uniform(-1.9, 2.0), random.uniform(-1.0, 1.0), 1.12), (random.uniform(0.08, 0.3), random.uniform(0.08, 0.25), 0.06), random.choice([BK, WIN, GM2, PL2, OR]), 0.004)
    for i in range(10): box((random.uniform(-1.8, 1.8), -1.15, random.uniform(-0.3, 0.7)), (random.uniform(0.08, 0.2), 0.05, random.uniform(0.06, 0.16)), random.choice([BK, WIN, GM2]), 0.004)
    # small thruster + rear greebles
    cyl((-2.2, -1.1, -1.05), 0.24, 1.0, GM, rot=(0, math.pi / 2, 0), v=16); cyl((-2.75, -1.1, -1.05), 0.2, 0.1, RING, rot=(0, math.pi / 2, 0), v=16)
    for i in range(10): box((random.uniform(-1.8, 1.8), random.uniform(-0.8, 0.9), 1.08), (random.uniform(0.1, 0.22), random.uniform(0.1, 0.22), 0.05), random.choice([BK, WIN, GM2]), 0.004)
    bpy.ops.object.empty_add(location=(0, 0, 0)); em = bpy.context.object
    for o in [o for o in bpy.data.objects if o.type == 'MESH']: o.parent = em
    em.scale = (0.78, 1.0, 1.1)
    render('ship_hero', 10.4, elev=33, yaw=-26, center=(-0.2, 0, 0.2), res=1024, key=4.6)

BUILD = {
 'cabinets': lambda: None,
}
JOBS = []
for s in (1, 2, 3): JOBS.append(('cabinet_%d' % s, (lambda s=s: b_cabinet(['#ff9a2a', '#3fffe6', '#ffd84a'][s - 1], s, [1.7, 1.4, 2.0][s - 1]))))
for s in (1, 2): JOBS.append(('console_%d' % s, (lambda s=s: b_console(['#3fffe6', '#6cff6c'][s - 1], s))))
JOBS += [('tank_green', lambda: b_tank('#ffb020', '#4a8a5a')), ('tank_blue', lambda: b_tank('#3fffe6', '#3a6aa8')),
         ('crate_orange', lambda: b_crate('#d4660c', 1)), ('crate_steel', lambda: b_crate('#7a8090', 2)),
         ('generator', lambda: b_generator(1)), ('locker', b_locker), ('reactor_core', b_reactor)]
for i, c in enumerate(('#3fa0ff', '#b44cff', '#3fff9a')):
    for s in (1, 2): JOBS.append(('crystal_%s_%d' % (c.strip('#'), s), (lambda c=c, s=s: b_crystal(c, s))))
for s in (1, 2): JOBS.append(('tentacle_%d' % s, (lambda s=s: b_tentacle(seed=s))))
for c, t in (('#2fbf5a', '#b8ff4a'), ('#1a8a8a', '#3fffe6')): JOBS.append(('rosette_%s_1' % c.strip('#'), (lambda c=c, t=t: b_rosette(c, t, 1))))
for c, p_ in (('#4aff6a', '#2fbf5a'), ('#ffd84a', '#c9a020'), ('#3fe8ff', '#1a8a8a')): JOBS.append(('incubator_%s' % c.strip('#'), (lambda c=c, p_=p_: b_incubator(c, p_))))
for c in ('#f0c020', '#c04cff', '#ff6a3a'): JOBS.append(('flower_%s' % c.strip('#'), (lambda c=c: b_flower(c))))
JOBS += [('rosette_8a3ad0_1', lambda: b_rosette('#8a3ad0', '#e08aff', 1)), ('rosette_2fbf5a_2', lambda: b_rosette('#2fbf5a', '#b8ff4a', 2, 11))]
JOBS += [('mushroom_ff8a2a', lambda: b_mushroom('#ff8a2a')), ('mushroom_3fffe6', lambda: b_mushroom('#3fffe6'))]
for s in range(1, 9): JOBS.append(('asteroid_%d' % s, (lambda s=s: b_asteroid(s))))
JOBS += [('ship_hero', b_ship_hero), ('ship_freighter', lambda: b_ship('freighter')), ('ship_explorer', lambda: b_ship('explorer', '#f4f6fa', '#f08a1a', '#7dff7d', 0.75, -30, False))]

for name, fn in JOBS:
    if WANT and WANT != ['all'] and not any(name.startswith(w) for w in WANT): continue
    reset(); fn(); print('rendered', name, flush=True)
