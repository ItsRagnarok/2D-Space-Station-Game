"""Render a sci-fi console in a fixed 3/4 orthographic view (headless Blender).

Usage: blender -b -P blender/render_console.py -- out/console_raw.png
"""
import bpy, math, sys

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "out/console_raw.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(name, color, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.7
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m

def box(name, loc, size, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(material)
    return o

metal = mat("metal", (0.12, 0.14, 0.2))
dark = mat("dark", (0.07, 0.08, 0.1))
amber = mat("amber", (1.0, 0.5, 0.05), emit=2.5)
screen = mat("screen", (0.1, 1.0, 0.45), emit=1.6)

box("base", (0, 0, 0.5), (3.0, 1.6, 1.0), metal)
box("plate", (0, 0, 1.05), (3.2, 1.8, 0.1), dark)
box("slope", (0, 0.1, 1.45), (2.6, 1.0, 0.7), metal, rot=(math.radians(-25), 0, 0))
box("screen", (0, -0.28, 1.62), (2.2, 0.05, 0.45), screen, rot=(math.radians(-25), 0, 0))
box("strip1", (-1.1, -0.82, 0.55), (0.5, 0.04, 0.12), amber)
box("strip2", (0.0, -0.82, 0.55), (0.9, 0.04, 0.12), amber)
box("strip3", (1.1, -0.82, 0.55), (0.5, 0.04, 0.12), amber)

bpy.ops.object.light_add(type="SUN", location=(3, -4, 6))
sun = bpy.context.object
sun.data.energy = 2.2
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))

bpy.ops.object.camera_add(location=(0, -9, 7.5))
cam = bpy.context.object
cam.data.type = "ORTHO"
cam.data.ortho_scale = 5.2
cam.rotation_euler = (math.radians(52), 0, 0)  # 3/4 view, axis-aligned
scene.camera = cam

scene.world = bpy.data.worlds.new("w")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.06, 0.1, 1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
scene.view_settings.view_transform = "Standard"  # AgX washes colors out
scene.view_settings.look = "None"

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.resolution_x = 384
scene.render.resolution_y = 384
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("RENDERED", out)
