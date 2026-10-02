# blender -b -P ship_modules.py -- outdir
# Hero freighter built as three modules (cabin, mid hull, rear engines) with ONE shared camera, so renders overlay exactly.
import bpy, sys, math, random, bmesh
OUT = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 40; sc.cycles.use_denoising = False
sc.view_settings.view_transform = 'Standard'; sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGBA'
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs[1].default_value = 0.0
random.seed(21)
def hexc(h): h = h.lstrip('#'); return tuple(pow(int(h[i:i + 2], 16) / 255, 2.2) for i in (0, 2, 4))
def mat(col, metal=0.4, rough=0.55, emit=None, es=0.0):
    m = bpy.data.materials.new('m'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*(hexc(col) if isinstance(col, str) else col), 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*hexc(emit), 1); b.inputs['Emission Strength'].default_value = es
    return m
def glow(c, s=6): return mat(c, 0, 0.3, c, s)
PLATE = mat('#d9d9e6', 0.25, 0.6); PLATE2 = mat('#b3b3c6', 0.3, 0.6); GUN = mat('#1d1f28', 0.7, 0.45); GUN2 = mat('#343847', 0.75, 0.4); GUN3 = mat('#4a5062', 0.75, 0.35)
YEL = mat('#f4c20f', 0.15, 0.5); YEL2 = mat('#d98c10', 0.15, 0.5); STEELB = mat('#7a88a6', 0.5, 0.4); BLK = mat('#0b0b11', 0.3, 0.6); ORG = mat('#ff8a14', 0.2, 0.5)
AMB = glow('#ff8a14', 5); AMB2 = glow('#ffb43a', 4); RIM = glow('#2a8cff', 3.2); CORE = glow('#a8dcff', 5); GLASS = mat('#0b1826', 0.9, 0.1, '#123a60', 0.25)
MOD = {'cabin': [], 'mid': [], 'eng': []}; cur = ['mid']
def reg(o): MOD[cur[0]].append(o); return o
def box(loc, size, m, bev=0.05, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.scale = [s / 2 for s in size]; bpy.ops.object.transform_apply(scale=True)
    if bev: md = o.modifiers.new('b', 'BEVEL'); md.width = bev; md.segments = 3
    o.data.materials.append(m); return reg(o)
def cyl(loc, r, d, m, rot=(0, math.pi / 2, 0), v=28, r2=None):
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(location=loc, radius=r, depth=d, vertices=v, rotation=rot)
    else: bpy.ops.mesh.primitive_cone_add(location=loc, radius1=r, radius2=r2, depth=d, vertices=v, rotation=rot)
    o = bpy.context.object; o.data.materials.append(m); return reg(o)
def sph(loc, radii, m, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc, radius=1, segments=seg, ring_count=seg // 2); o = bpy.context.object; o.scale = radii; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return reg(o)
def wedge(loc, size, top, m, bev=0.04):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.scale = [s / 2 for s in size]; bpy.ops.object.transform_apply(scale=True)
    me = o.data; bm = bmesh.new(); bm.from_mesh(me)
    for v in bm.verts:
        if v.co.z > 0: v.co.x *= top[0]; v.co.y *= top[1]
    bm.to_mesh(me); bm.free()
    if bev: md = o.modifiers.new('b', 'BEVEL'); md.width = bev; md.segments = 2
    o.data.materials.append(m); return reg(o)
def prism(pts, y0, y1, m, bev=0.02):
    """extrude a side-view (x,z) polygon along Y from y0 to y1"""
    me = bpy.data.meshes.new('pr'); o = bpy.data.objects.new('pr', me); bpy.context.collection.objects.link(o)
    bm = bmesh.new(); a = [bm.verts.new((x, y0, z)) for x, z in pts]; b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(len(pts)): j = (i + 1) % len(pts); bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free(); me.materials.append(m)
    if bev: md = o.modifiers.new('b', 'BEVEL'); md.width = bev; md.segments = 2
    return reg(o)
def torus(loc, major, minor, m, rot, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot, major_segments=40, minor_segments=10); o = bpy.context.object; o.scale = scale; o.data.materials.append(m); return reg(o)
def window(x, y, z, w=0.3, h=0.3, face='-y'):
    """dark recessed square with amber light (like the reference's small windows)"""
    box((x, y, z), (w, 0.07, h), BLK, 0.01); box((x, y - 0.03, z), (w * 0.6, 0.05, h * 0.6), AMB, 0.005)
def slab(loc, size, m=PLATE, bev=0.07): return box(loc, size, m, bev)

# ================= ENGINES (rear) =================
cur[0] = 'eng'
def engine(cx, cy, cz, R, L, big=True):
    cyl((cx, cy, cz), R, L, GUN2)                                   # barrel
    for k in range(3): cyl((cx - L / 2 + 0.55 + k * 0.85, cy, cz), R * 1.04, 0.16, GUN3)           # three wide seam rings
    for k in range(4): cyl((cx + L / 2 - 0.85 + k * 0.18, cy, cz), R * 1.02, 0.1, GUN)             # ridged collar near the hull
    fx = cx - L / 2
    cyl((fx - 0.03, cy, cz), R * 1.06, 0.14, GUN3)                  # bezel
    cyl((fx - 0.12, cy, cz), R * 0.97, 0.05, RIM)                   # glowing rim
    cyl((fx - 0.17, cy, cz), R * 0.89, 0.05, mat('#06101e', 0.6, 0.4))
    cyl((fx - 0.22, cy, cz), R * 0.68, 0.05, glow('#1a4ee0', 2.6))
    cyl((fx - 0.26, cy, cz), R * 0.4, 0.05, CORE)
    for k in range(3):                                              # amber slots on the barrel side facing the camera
        box((cx + 0.2 + k * 0.5, cy - R * 1.01, cz + 0.12 - k * 0.04), (0.34, 0.05, 0.07), AMB, 0.005)
    box((cx + 0.9, cy - R * 1.0, cz - 0.35), (0.5, 0.05, 0.06), AMB2, 0.005)
engine(-2.85, -0.62, -0.18, 1.0, 2.7)
engine(-2.55, 1.05, 0.58, 0.8, 2.3)
# pylon between engines and hull
cyl((-1.1, 0.2, 0.35), 0.62, 0.9, GUN2, v=20); cyl((-1.1, 0.2, 0.35), 0.66, 0.1, GUN3, v=20)
box((-0.9, -0.55, 0.62), (0.5, 0.12, 0.4), PLATE2, 0.03); box((-0.9, -0.62, 0.62), (0.3, 0.06, 0.24), AMB, 0.01)
cyl((-2.0, -1.0, -1.1), 0.24, 1.0, GUN2, v=16); cyl((-2.55, -1.0, -1.1), 0.2, 0.1, RIM, v=16)   # little lower thruster

# ================= MID HULL =================
cur[0] = 'mid'
box((0.4, 0.05, 0.1), (4.3, 2.0, 1.7), GUN2, 0.05); box((0.3, -0.3, -1.0), (3.3, 1.9, 0.55), GUN2, 0.05)                    # dark core visible in the gaps
# top deck: two big plates + a smaller step
slab((-0.95, 0.2, 1.08), (1.55, 1.7, 0.32)); slab((0.75, 0.2, 1.08), (1.75, 1.7, 0.32)); slab((0.3, -0.72, 0.95), (3.2, 0.62, 0.28), PLATE2)
window(-1.0, -0.2, 1.24, 0.22, 0.22); box((-1.0, 0.3, 1.25), (0.2, 0.2, 0.05), BLK, 0.01); window(1.3, 0.1, 1.24, 0.28, 0.28)
# monitor frame
box((-0.55, -1.05, 0.55), (0.9, 0.14, 0.75), PLATE2, 0.05); box((-0.55, -1.13, 0.55), (0.66, 0.06, 0.52), GUN, 0.02); box((-0.55, -1.17, 0.55), (0.52, 0.04, 0.38), mat('#6a4a22', 0.2, 0.5, '#ff8a14', 1.6), 0.01)
# side plates (camera side), staggered
slab((-1.45, -1.06, 0.15), (0.9, 0.24, 1.35), PLATE, 0.07); slab((0.2, -1.1, 0.42), (1.6, 0.24, 0.95), PLATE, 0.07); slab((1.6, -1.08, 0.28), (1.1, 0.24, 1.1), PLATE, 0.07)
window(-1.45, -1.22, 0.3, 0.24, 0.24); window(0.0, -1.25, 0.6, 0.32, 0.32); window(0.75, -1.25, 0.5, 0.26, 0.26); window(1.6, -1.2, 0.5, 0.3, 0.3)
box((1.25, -1.25, 0.1), (0.18, 0.05, 0.18), BLK, 0.01); box((-0.4, -1.25, 0.15), (0.16, 0.05, 0.16), BLK, 0.01)
# lower long plate + dark window strip + hazard plate
slab((0.8, -1.1, -0.5), (3.0, 0.24, 0.5), PLATE, 0.07)
box((0.9, -1.1, -0.12), (2.4, 0.1, 0.22), GUN, 0.02)
for k in range(8): box((0.0 + k * 0.28, -1.17, -0.12), (0.1, 0.04, 0.14), AMB2 if k % 3 else AMB, 0.004)
slab((0.3, -1.3, -1.05), (2.8, 0.32, 0.42), PLATE, 0.05)
for k in range(11):
    box((-0.95 + k * 0.26, -1.48, -1.05), (0.12, 0.03, 0.34), ORG if k % 2 == 0 else BLK, 0.003, rot=(0, 0.7, 0))
box((0.9, -0.95, -1.28), (1.3, 0.9, 0.4), GUN2, 0.05); box((0.9, -1.4, -1.26), (1.0, 0.08, 0.28), mat('#ff9a1a', 0.1, 0.4, '#ff8a14', 3.0), 0.02)
# turret + gun, striped rod, hazard cylinder
cyl((2.0, 0.85, 1.28), 0.5, 0.6, GUN2, v=24, rot=(0, 0, 0)); cyl((2.0, 0.85, 1.62), 0.4, 0.14, GUN3, v=24, rot=(0, 0, 0))
for k in range(4): box((2.0 + 0.45 * math.cos(k * 1.57), 0.85 + 0.45 * math.sin(k * 1.57), 1.28), (0.14, 0.14, 0.2), YEL, 0.01)
cyl((2.75, 0.85, 1.55), 0.1, 1.0, PLATE2, v=12); cyl((3.28, 0.85, 1.55), 0.11, 0.2, mat('#d8242a', 0.2, 0.5, '#d8242a', 1.6), v=12)
cyl((-1.9, 0.9, 1.35), 0.26, 1.7, PLATE, v=20)
for k in range(5): cyl((-2.55 + k * 0.38, 0.9, 1.35), 0.275, 0.14, ORG, v=20)
for i in range(16): box((random.uniform(-1.5, 1.8), random.uniform(-0.6, 0.9), 1.27), (random.uniform(0.08, 0.26), random.uniform(0.08, 0.2), 0.05), random.choice([BLK, GUN2, PLATE2]), 0.004)

# ================= CABIN (head) =================
cur[0] = 'cabin'
# Cabin as seen from the side, like the reference: bands drawn as side-view polygons on the camera-facing face.
body = box((3.35, 0.0, -0.02), (2.1, 1.95, 1.3), YEL, 0.4); body.modifiers['b'].segments = 8
box((3.3, 0.05, 0.64), (1.25, 1.1, 0.05), GLASS, 0.02); box((3.3, 0.05, 0.665), (1.05, 0.9, 0.02), mat('#102a44', 0.8, 0.12, '#1c5088', 0.3), 0.01)
prism([(2.6, 0.28), (2.6, 0.9), (3.45, 0.86), (4.05, 0.62), (4.18, 0.34)], -1.0, -1.08, GLASS, 0.03)     # sloped dark canopy glass
prism([(2.75, 0.34), (2.75, 0.84), (3.4, 0.8), (3.95, 0.58), (4.05, 0.38)], -1.08, -1.1, mat('#102a44', 0.8, 0.12, '#1c5088', 0.3), 0.02)
for x0 in (3.0, 3.4, 3.8): prism([(x0, 0.34), (x0 + 0.06, 0.34), (x0 + 0.06, 0.86 - (x0 - 3.0) * 0.28), (x0, 0.88 - (x0 - 3.0) * 0.28)], -1.1, -1.14, YEL, 0.01)   # yellow ribs
prism([(2.6, 0.9), (3.45, 0.9), (4.05, 0.66), (4.2, 0.4), (4.1, 0.34), (3.98, 0.58), (3.4, 0.82), (2.6, 0.84)], -1.08, -1.16, YEL, 0.015)  # yellow frame along the top
prism([(2.6, -0.2), (2.6, 0.24), (4.32, 0.0)], -1.0, -1.16, STEELB, 0.02)                              # steel triangle pointing at the nose
prism([(2.6, -0.2), (4.32, 0.0), (4.1, -0.1), (2.6, -0.28)], -1.16, -1.2, mat('#c0cae0', 0.5, 0.3), 0.01)  # its lit edge
prism([(2.6, -0.62), (2.6, -0.24), (4.18, -0.08), (4.05, -0.52)], -1.0, -1.12, GUN3, 0.03)             # blue-grey lower panel
for k in range(4): prism([(3.0 + k * 0.28, -0.5), (3.14 + k * 0.28, -0.5), (3.2 + k * 0.28, -0.3), (3.06 + k * 0.28, -0.3)], -1.12, -1.15, YEL, 0.004)   # hazard scuffs
prism([(2.6, -0.62), (2.6, -0.22), (3.1, -0.4), (3.0, -0.66)], -1.0, -1.14, YEL, 0.02)                  # yellow triangle panel at the rear-bottom
box((2.45, 0.0, 0.1), (0.3, 2.0, 1.3), GUN3, 0.05)                                                      # bulkhead

# ================= parent everything, shorten X like the compact reference =================
bpy.ops.object.empty_add(location=(0, 0, 0)); em = bpy.context.object
for o in [o for o in bpy.data.objects if o.type == 'MESH']: o.parent = em
em.scale = (0.92, 1.0, 1.12)
bpy.ops.object.light_add(type='SUN'); l = bpy.context.object; l.data.energy = 4.4; l.data.color = (1, 0.94, 0.86); l.rotation_euler = (math.radians(50), 0, math.radians(35))
bpy.ops.object.light_add(type='SUN'); l = bpy.context.object; l.data.energy = 1.4; l.data.color = (0.5, 0.65, 1.0); l.rotation_euler = (math.radians(60), 0, math.radians(-140))
bpy.ops.object.camera_add(); cam = bpy.context.object; cam.data.type = 'ORTHO'; cam.data.ortho_scale = 12.2; sc.camera = cam
e = math.radians(31); y = math.radians(-11); c = (-0.1, 0, 0.1); d = 20
cam.location = (c[0] + d * math.sin(y) * math.cos(e), c[1] - d * math.cos(y) * math.cos(e), c[2] + d * math.sin(e)); cam.rotation_euler = (math.radians(90 - 31), 0, y)
sc.render.resolution_x = 1024; sc.render.resolution_y = 1024
def show(names):
    for k, objs in MOD.items():
        for o in objs: o.hide_render = k not in names
for name, names in (('all', ('cabin', 'mid', 'eng')), ('cabin', ('cabin',)), ('mid', ('mid',)), ('eng', ('eng',))):
    show(names); sc.render.filepath = f'{OUT}/ship_{name}.png'; bpy.ops.render.render(write_still=True); print('rendered', name, flush=True)
