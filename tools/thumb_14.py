# Blender: 3D hero number "14" for the NYC restaurant thumbnail.
# Run: blender -b -P tools/thumb_14.py -- <out.png>
import bpy, sys, math

out = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

try:
    scene.render.engine = "BLENDER_EEVEE"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"
ee = scene.eevee
for attr, val in (("taa_render_samples", 64), ("use_raytracing", True)):
    if hasattr(ee, attr):
        setattr(ee, attr, val)

# World: near-black with a cold tint
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.004, 0.006, 0.012, 1)
bg.inputs[1].default_value = 1.0

def mat(name, color, emit=0.0, rough=0.25, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*color, 1)
        p.inputs["Emission Strength"].default_value = emit
    return m

FONT = "C:/Windows/Fonts/ariblk.ttf"

def text(body, size, loc, material, extrude=0.18, rot_z=0.0):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, rot_z))
    t = bpy.context.object
    t.data.body = body
    t.data.font = bpy.data.fonts.load(FONT, check_existing=True)
    t.data.size = size
    t.data.extrude = extrude
    t.data.bevel_depth = 0.02
    t.data.bevel_resolution = 3
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.materials.append(material)
    return t

# Floor: glossy dark, catches reflections
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -1.05))
bpy.context.object.data.materials.append(mat("Floor", (0.01, 0.01, 0.015), rough=0.12))

# Hero "14": glowing red, slightly turned
text("14", 3.0, (1.55, 0, 0.3), mat("Red", (0.9, 0.02, 0.02), emit=1.2, rough=0.3), extrude=0.35, rot_z=math.radians(-14))

# Lights: red rim from behind, cool key from the left
bpy.ops.object.light_add(type="AREA", location=(1.5, 3.5, 2.5))
rim = bpy.context.object
rim.data.energy, rim.data.size, rim.data.color = 1500, 4, (1.0, 0.2, 0.15)
rim.rotation_euler = (math.radians(-60), 0, math.radians(180))
bpy.ops.object.light_add(type="AREA", location=(-4, -4, 3))
key = bpy.context.object
key.data.energy, key.data.size, key.data.color = 900, 5, (0.6, 0.75, 1.0)
key.rotation_euler = (math.radians(55), 0, math.radians(-45))

# Camera: low angle, shallow depth of field
bpy.ops.object.camera_add(location=(-0.6, -9.5, 0.35), rotation=(math.radians(88), 0, math.radians(-4)))
cam = bpy.context.object
cam.data.lens = 50
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 9.3
cam.data.dof.aperture_fstop = 2.2
scene.camera = cam

scene.render.filepath = out
bpy.ops.render.render(write_still=True)
