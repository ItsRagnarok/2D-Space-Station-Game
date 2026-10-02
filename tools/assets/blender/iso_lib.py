# blender -b -P iso_lib.py -- outdir [id ...|all]   Isometric (2:1-style) asset kit for the botany + station sheets.
import bpy, sys, math, random, bmesh
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]; OUT = args[0]; WANT = args[1:]
PXU = 85.0                                   # render px per world unit (ortho scale 12 @ 1024 px) -> same scale for every asset
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48; sc.cycles.use_denoising = False
    sc.view_settings.view_transform = 'Standard'; sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGBA'
    sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs[1].default_value = 0.0
    return sc
def hexc(h): h = h.lstrip('#'); return tuple(pow(int(h[i:i + 2], 16) / 255, 2.2) for i in (0, 2, 4))
def mat(col, metal=0.3, rough=0.55, emit=None, es=0.0, alpha=1.0):
    m = bpy.data.materials.new('m'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*hexc(col), 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*hexc(emit), 1); b.inputs['Emission Strength'].default_value = es
    if alpha < 1: b.inputs['Alpha'].default_value = alpha
    return m
def glow(c, s=4): return mat(c, 0, 0.3, c, s)
GUN = lambda: mat('#2b2e39', 0.7, 0.45); GUN2 = lambda: mat('#454a59', 0.7, 0.4); STEEL = lambda: mat('#7c8292', 0.65, 0.4); STEEL2 = lambda: mat('#a3a9b8', 0.6, 0.4)
GOLD = lambda: mat('#cf9420', 0.75, 0.38); DARK = lambda: mat('#0f1118', 0.5, 0.6); SOIL = lambda: mat('#16120f', 0.1, 0.9); ROCK = lambda: mat('#242227', 0.2, 0.8)
def box(loc, size, m, bev=0.04, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.scale = [s / 2 for s in size]; bpy.ops.object.transform_apply(scale=True)
    if bev: md = o.modifiers.new('b', 'BEVEL'); md.width = bev; md.segments = 2
    o.data.materials.append(m); return o
def cyl(loc, r, h, m, rot=(0, 0, 0), v=28, r2=None):
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(location=loc, radius=r, depth=h, vertices=v, rotation=rot)
    else: bpy.ops.mesh.primitive_cone_add(location=loc, radius1=r, radius2=r2, depth=h, vertices=v, rotation=rot)
    o = bpy.context.object; o.data.materials.append(m); return o
def sph(loc, radii, m, seg=20, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc, radius=1, segments=seg, ring_count=seg // 2, rotation=rot); o = bpy.context.object; o.scale = radii if hasattr(radii, '__len__') else (radii,) * 3
    o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def tube(p0, p1, r0, r1, m, v=10):
    a = Vector(p0); b = Vector(p1); d = b - a; L = d.length
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r0, radius2=r1, depth=L, location=(a + b) / 2); o = bpy.context.object
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def leaf(base, az, el, L, W, m, th=0.05, curl=0.0):
    """flattened ellipsoid pointing along (az, el) from base"""
    d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))); c = Vector(base) + d * (L / 2)
    bpy.ops.mesh.primitive_uv_sphere_add(location=c, radius=1, segments=16, ring_count=8); o = bpy.context.object; o.scale = (L / 2, W / 2, th)
    o.rotation_euler = d.to_track_quat('X', 'Z').to_euler(); o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def arc_pts(base, height, bend, n=7, az=0.0, wob=0.0):
    pts = []
    for i in range(n + 1):
        t = i / n; x = bend * (t ** 1.8) * math.cos(az); y = bend * (t ** 1.8) * math.sin(az); pts.append((base[0] + x + wob * math.sin(t * 6 + az), base[1] + y, base[2] + height * t))
    return pts
def stalk(pts, r0, r1, m):
    n = len(pts) - 1
    for i in range(n): tube(pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n, m)
def rocks(cx, cy, r=0.8, n=7, z=0.0):
    for i in range(n):
        a = i * 6.28 / n; sph((cx + math.cos(a) * r * 0.7, cy + math.sin(a) * r * 0.7, z + 0.08), (random.uniform(.16, .26), random.uniform(.14, .22), random.uniform(.1, .16)), ROCK(), 10)
def monitor(loc, w=0.7, h=0.5, face='-y', scr='#37e07a'):
    x, y, z = loc
    box((x, y, z), (w, 0.1, h), GOLD(), 0.02); box((x, y - 0.05, z), (w * 0.8, 0.06, h * 0.78), DARK(), 0.01); box((x, y - 0.075, z), (w * 0.66, 0.04, h * 0.6), glow(scr, 2.0), 0.005)
def gold_posts(cx, cy, z0, z1, w, d, t=0.16):
    for sx in (-1, 1):
        for sy in (-1, 1): box((cx + sx * (w / 2 - t / 2), cy + sy * (d / 2 - t / 2), (z0 + z1) / 2), (t, t, z1 - z0), GOLD(), 0.02)
def lights():
    bpy.ops.object.light_add(type='SUN'); l = bpy.context.object; l.data.energy = 4.2; l.data.color = (1, 0.95, 0.88); l.rotation_euler = (math.radians(48), 0, math.radians(30))
    bpy.ops.object.light_add(type='SUN'); l = bpy.context.object; l.data.energy = 1.5; l.data.color = (0.55, 0.65, 1.0); l.rotation_euler = (math.radians(62), 0, math.radians(-150))
def render(name, center=(0, 0, 1.0), elev=30, yaw=45, scale=12.0, res=1024):
    sc = bpy.context.scene; lights(); bpy.ops.object.camera_add(); cam = bpy.context.object; cam.data.type = 'ORTHO'; cam.data.ortho_scale = scale; sc.camera = cam
    d = 30; e = math.radians(elev); y = math.radians(yaw)
    cam.location = (center[0] + d * math.sin(y) * math.cos(e), center[1] - d * math.cos(y) * math.cos(e), center[2] + d * math.sin(e)); cam.rotation_euler = (math.radians(90 - elev), 0, y)
    sc.render.resolution_x = res; sc.render.resolution_y = res; sc.render.filepath = f'{OUT}/{name}.png'; bpy.ops.render.render(write_still=True)

# ---------------------------------------------------------------- plants ----------
def plant_blue_flower(x, y, z, h=1.0, seed=1, col='#2fb4ff'):
    random.seed(seed); pts = arc_pts((x, y, z), h, random.uniform(-0.2, 0.2), 4, random.uniform(0, 6.28)); stalk(pts, 0.035, 0.02, mat('#1a6aa0', 0, .5, '#1a8ad0', .6))
    tip = pts[-1]; sph(tip, (0.17, 0.17, 0.08), glow(col, 4)); sph((tip[0], tip[1], tip[2] + 0.04), 0.06, glow('#ffe86a', 5))
def plant_spiky(x, y, z, s=1.0, seed=1, col='#7a3ad8', tip='#c88aff'):
    random.seed(seed)
    for i in range(9):
        a = i * 0.7 + random.random() * 0.3; el = random.uniform(0.9, 1.35); L = random.uniform(0.35, 0.6) * s
        leaf((x, y, z), a, el, L, 0.13 * s, mat(col, 0, .5, col, .5), 0.03)
    sph((x, y, z + 0.35 * s), 0.08 * s, glow(tip, 4))
def grass(x, y, z, s=1.0, seed=1, col='#58c040'):
    random.seed(seed)
    for i in range(6): leaf((x, y, z), random.uniform(0, 6.28), random.uniform(0.9, 1.3), random.uniform(0.3, 0.5) * s, 0.07 * s, mat(col, 0, .6, col, .3), 0.02)

def b_tank_large():
    random.seed(1); L, W = 5.0, 2.3
    box((0, 0, 0.5), (L, W, 1.0), GUN2(), 0.06); box((0, -W / 2 - 0.02, 0.45), (L * 0.9, 0.06, 0.55), GUN(), 0.02)
    for k in range(3): box((-1.4 + k * 0.45, -W / 2 - 0.05, 0.62), (0.32, 0.04, 0.22), STEEL(), 0.01)
    box((-0.2, -W / 2 - 0.04, 0.2), (3.2, 0.05, 0.08), GOLD(), 0.01)
    gold_posts(0, 0, 0.0, 1.0, L, W, 0.2); monitor((1.55, -W / 2 - 0.04, 0.6), 0.9, 0.62); box((2.15, -W / 2 - 0.05, 0.55), (0.3, 0.06, 0.6), GOLD(), 0.02); box((2.15, -W / 2 - 0.09, 0.6), (0.16, 0.03, 0.36), glow('#ffb43a', 3), 0.005)
    # glass volume: dark back + soil + plants, then frame
    box((0, W / 2 - 0.1, 1.75), (L - 0.3, 0.12, 1.45), mat('#0a1230', 0.3, 0.4), 0.01); box((-L / 2 + 0.15, 0, 1.75), (0.12, W - 0.3, 1.45), mat('#0a1230', 0.3, 0.4), 0.01)
    box((0, 0, 1.05), (L - 0.3, W - 0.3, 0.12), SOIL(), 0.02)
    for i, x in enumerate((-1.7, -0.6, 0.55, 1.6)): plant_blue_flower(x, random.uniform(-0.3, 0.3), 1.1, random.uniform(0.9, 1.3), i)
    for x, y in ((-1.3, 0.3), (1.2, -0.2), (2.0, 0.35)): plant_spiky(x, y, 1.1, 1.1, int(x * 10))
    for x in (-2.1, -0.1, 0.9): grass(x, 0.4 * (1 if x > 0 else -1), 1.1, 1.0, int(x * 7 + 3))
    for sx in (-1, 1):
        for sy in (-1, 1): box((sx * (L / 2 - 0.1), sy * (W / 2 - 0.1), 1.75), (0.2, 0.2, 1.5), STEEL(), 0.03)
    box((0, -W / 2 + 0.05, 2.52), (L, 0.22, 0.12), STEEL(), 0.03); box((0, W / 2 - 0.05, 2.52), (L, 0.22, 0.12), STEEL(), 0.03)
    box((-L / 2 + 0.05, 0, 2.52), (0.22, W, 0.12), STEEL(), 0.03); box((L / 2 - 0.05, 0, 2.52), (0.22, W, 0.12), STEEL(), 0.03)
    box((0, 0, 2.62), (L - 0.1, W - 0.1, 0.22), STEEL2(), 0.05); box((0, 0, 2.76), (1.6, 0.7, 0.06), mat('#0c1a30', 0.8, 0.2, '#2a5a90', 0.6), 0.02)
    gold_posts(0, 0, 1.0, 2.6, L, W, 0.12)
    for x in (-1.2, 0, 1.2): box((x, -W / 2 + 0.07, 1.8), (0.05, 0.03, 1.2), mat('#9cc8ff', 0, 0.1, '#7ab0ff', 1.0), 0.005)
    render('b01_tank_large', center=(0, 0, 1.4))
def b_tube_green():
    random.seed(2); cyl((0, 0, 0.3), 1.0, 0.6, STEEL(), v=32); cyl((0, 0, 0.62), 1.05, 0.1, GOLD(), v=32); cyl((0, 0, 0.1), 1.1, 0.2, GUN(), v=32)
    for k in range(6): box((math.cos(k * 1.047) * 0.98, math.sin(k * 1.047) * 0.98, 0.3), (0.1, 0.1, 0.5), GOLD(), 0.01, rot=(0, 0, k * 1.047))
    monitor((0.2, -1.0, 0.32), 0.55, 0.38)
    cyl((0, 0, 1.75), 0.84, 2.2, mat('#35c64a', 0, 0.2, '#2ee04a', 0.9, 0.8), v=32)
    for i in range(7):
        a = i * 0.9; leaf((0, 0, 0.75), a, random.uniform(0.6, 1.2), random.uniform(0.7, 1.1), 0.28, mat('#1f7a28', 0, .5, '#1f8a2a', .4), 0.04)
    tube((0, 0, 0.75), (0.03, 0, 2.5), 0.05, 0.03, mat('#1f7a28'))
    cyl((0, 0, 2.95), 0.95, 0.4, STEEL(), v=32); cyl((0, 0, 3.2), 0.9, 0.16, GOLD(), v=32); cyl((0, 0, 3.32), 0.7, 0.1, GUN(), v=32)
    for k in range(10): box((math.cos(k * 0.628) * 0.8, math.sin(k * 0.628) * 0.8, 3.38), (0.18, 0.06, 0.04), GOLD(), 0.005, rot=(0, 0, k * 0.628))
    render('b02_tube_green', center=(0, 0, 1.7))
def b_planter_blue():
    random.seed(3); L, W = 2.9, 2.1
    box((0, 0, 0.55), (L, W, 1.1), GUN2(), 0.06); gold_posts(0, 0, 0.0, 1.1, L, W, 0.2); box((0, 0, 1.12), (L + 0.12, W + 0.12, 0.14), STEEL(), 0.03)
    box((0, 0, 1.18), (L - 0.3, W - 0.3, 0.08), SOIL(), 0.02); monitor((0.7, -W / 2 - 0.04, 0.55), 0.8, 0.58); box((-0.7, -W / 2 - 0.05, 0.6), (0.9, 0.05, 0.4), GUN(), 0.02)
    for i in range(9): plant_blue_flower(random.uniform(-1.0, 1.0), random.uniform(-0.6, 0.6), 1.2, random.uniform(0.9, 2.0), i + 20)
    for x, y in ((-0.9, 0.4), (0.8, 0.5), (0.1, -0.4), (-0.4, -0.2)): grass(x, y, 1.2, 1.2, int(x * 9))
    render('b03_planter_blue', center=(0, 0, 1.7))
def b_plant_purple_leaf():
    random.seed(4); rocks(0, 0, 1.0, 9)
    stalk(arc_pts((0, 0, 0.1), 1.6, 0.1, 5), 0.08, 0.04, mat('#2a1a6a', 0, .5, '#3a28a0', .4))
    for i in range(8):
        a = i * 0.85 + 0.2; el = random.uniform(0.35, 1.0); L = random.uniform(1.0, 1.6); z0 = 0.7 + (i % 4) * 0.35
        leaf((0, 0, z0), a, el, L, L * 0.62, mat('#4a28c8', 0, .5, '#5a30e0', .5), 0.05)
        leaf((0, 0, z0 + 0.02), a, el, L * 0.8, L * 0.42, mat('#8a58f0', 0, .5, '#9a68ff', .5), 0.06)
        ex = Vector((math.cos(el) * math.cos(a), math.cos(el) * math.sin(a), math.sin(el))) * L; sph((ex.x, ex.y, z0 + ex.z), 0.07, glow('#3a9cff', 5))
    render('b04_plant_purple', center=(0, 0, 1.6))
def b_plant_red_tentacle():
    random.seed(5); rocks(0, 0, 1.0, 9); redm = mat('#b01820', 0, .45, '#d02a2a', .6)
    for i in range(6):
        a = i * 1.05; arc = arc_pts((math.cos(a) * 0.3, math.sin(a) * 0.3, 0.1), random.uniform(1.6, 3.2), random.uniform(0.3, 1.2), 9, a, 0.15); stalk(arc, 0.1, 0.05, redm)
        sph(arc[-1], 0.2, glow('#ff8a1a', 5)); sph((arc[-1][0], arc[-1][1], arc[-1][2] + 0.05), 0.09, glow('#ffd84a', 6))
        if i % 2: sph(arc[len(arc) // 2], 0.13, glow('#ff7a1a', 4))
    render('b05_plant_red', center=(0, 0, 1.7))

BUILD = {'b01': b_tank_large, 'b02': b_tube_green, 'b03': b_planter_blue, 'b04': b_plant_purple_leaf, 'b05': b_plant_red_tentacle}
exec(open(__file__.replace('iso_lib.py', 'iso_lib_more.py')).read()) if __import__('os').path.exists(__file__.replace('iso_lib.py', 'iso_lib_more.py')) else None
for k, fn in BUILD.items():
    if WANT and WANT != ['all'] and not any(k.startswith(w) for w in WANT): continue
    reset(); fn(); print('rendered', k, flush=True)
