# blender -b -P freighter.py -- out.png  : freighter model, 3/4 top-down ortho render, transparent bg
import bpy, sys, math, random
random.seed(7)
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def mat(name, col, metal=0.6, rough=0.45, emit=None, es=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = es
    return m
HULL = mat('hull', (0.62, 0.64, 0.68)); HULL2 = mat('hull2', (0.38, 0.40, 0.45)); DARK = mat('dark', (0.07, 0.075, 0.09), 0.8, 0.5)
ORG = mat('org', (0.9, 0.38, 0.05), 0.3, 0.5, (1, 0.45, 0.05), 0.6); BLU = mat('blu', (0.1, 0.3, 1), 0, 0.2, (0.2, 0.5, 1), 14)
WIN = mat('win', (0.5, 0.9, 1), 0, 0.1, (0.4, 0.85, 1), 4)

def box(n, loc, sc_, m, bev=0.04):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = n; o.scale = [s / 2 for s in sc_]
    bpy.ops.object.transform_apply(scale=True)
    if bev:
        mod = o.modifiers.new('b', 'BEVEL'); mod.width = bev; mod.segments = 2
    o.data.materials.append(m); return o
def cyl(n, loc, r, d, m, rot=(0, math.pi / 2, 0), v=24):
    bpy.ops.mesh.primitive_cylinder_add(location=loc, radius=r, depth=d, vertices=v, rotation=rot); o = bpy.context.object; o.name = n
    o.data.materials.append(m); return o

# ship points along +X (nose). hull blocks
box('core', (0, 0, 0), (4.6, 1.9, 1.0), HULL)
box('deck', (0.2, 0, 0.62), (3.2, 1.5, 0.3), HULL2)
box('nose', (2.7, 0, -0.05), (1.5, 1.4, 0.8), HULL)
box('nose2', (3.5, 0, -0.1), (0.7, 0.9, 0.55), HULL2)
box('bridge', (2.0, 0, 0.9), (1.1, 0.9, 0.5), HULL2); box('glass', (2.55, 0, 0.95), (0.12, 0.7, 0.28), WIN)
for sy in (-1, 1):
    box('cargo', (-0.3, sy * 1.25, -0.1), (2.8, 0.75, 0.95), HULL2)
    for i in range(4): box('stripe', (-1.5 + i * 0.8, sy * 1.25, 0.42), (0.35, 0.6, 0.06), ORG, 0.01)
    box('wing', (-1.8, sy * 1.7, -0.3), (1.4, 0.5, 0.25), HULL)
    cyl('engine', (-2.5, sy * 0.85, 0.0), 0.62, 1.2, DARK); cyl('ring', (-2.15, sy * 0.85, 0.0), 0.7, 0.18, HULL)
    cyl('flame', (-3.15, sy * 0.85, 0.0), 0.48, 0.18, BLU)
    cyl('flame2', (-3.5, sy * 0.85, 0.0), 0.26, 0.5, BLU)
for i in range(7): box('pl', (-2 + i * 0.7, random.uniform(-0.5, 0.5), 0.8), (0.5, 0.4, 0.07), random.choice([HULL, HULL2, DARK]), 0.01)
box('mast', (0.2, 0.0, 1.1), (0.08, 0.08, 0.7), DARK)
box('dish', (0.2, 0.0, 1.5), (0.5, 0.5, 0.06), HULL)

# lights + camera
for loc, e, col in (((6, -4, 9), 3.2, (1, 0.93, 0.85)), ((-6, 5, 5), 1.4, (0.55, 0.65, 1)), ((-4, 0, -2), 90, (0.2, 0.4, 1))):
    bpy.ops.object.light_add(type='SUN' if e < 50 else 'POINT', location=loc); l = bpy.context.object
    l.data.energy = e if e < 50 else 3000; l.data.color = col
    if e < 50: l.rotation_euler = (math.radians(50), 0, math.radians(35))
bpy.ops.object.camera_add(location=(0, 0, 0)); cam = bpy.context.object; cam.data.type = 'ORTHO'; cam.data.ortho_scale = 9.2
# 3/4 view: ship nose toward lower-left on screen => rotate ship with camera yaw
cam.location = (-4.2, -9.0, 9.0); cam.rotation_euler = (math.radians(52), 0, math.radians(-26)); sc.camera = cam
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24; sc.cycles.use_denoising = False
sc.render.film_transparent = True; sc.render.resolution_x = 640; sc.render.resolution_y = 480
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs[1].default_value = 0.15
sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True)
