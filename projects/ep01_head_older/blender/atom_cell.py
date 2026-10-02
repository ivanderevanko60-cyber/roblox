# Photoreal hero shot: strontium atom cloud glowing inside a glass vacuum cell on an optical table.
# Run: blender -b -P atom_cell.py -- <out_prefix> [still|anim] [samples]
import bpy, sys, math

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
MODE = argv[1] if len(argv) > 1 else "still"
SAMPLES = int(argv[2]) if len(argv) > 2 else 128

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.use_adaptive_sampling = True
sc.cycles.max_bounces = 8
sc.cycles.transmission_bounces = 8
sc.cycles.volume_bounces = 1
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.fps = 30
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.use_motion_blur = False

world = bpy.data.worlds.new("W")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.002, 0.003, 0.005, 1)


def principled(name, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    for k, v in kw.items():
        p.inputs[k].default_value = v
    return m, p


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


# --- Optical table: dark anodised steel with a 25 mm hole grid ---------------------------------
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 0))
table = bpy.context.object
tm, tp = principled("Table", **{"Base Color": (0.035, 0.037, 0.04, 1), "Metallic": 0.9, "Roughness": 0.38})
nt = tm.node_tree
tc = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping")
mp.inputs["Scale"].default_value = (40, 40, 40)          # 1 unit = 1 m -> 25 mm pitch
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
# distance to cell centre
vfr = nt.nodes.new("ShaderNodeVectorMath"); vfr.operation = "FRACTION"
nt.links.new(mp.outputs["Vector"], vfr.inputs[0])
sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"
sub.inputs[1].default_value = (0.5, 0.5, 0.0)
nt.links.new(vfr.outputs[0], sub.inputs[0])
nt.links.new(sub.outputs[0], sep.inputs[0])
cmb = nt.nodes.new("ShaderNodeCombineXYZ")
nt.links.new(sep.outputs["X"], cmb.inputs["X"])
nt.links.new(sep.outputs["Y"], cmb.inputs["Y"])
ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
nt.links.new(cmb.outputs[0], ln.inputs[0])
hole = nt.nodes.new("ShaderNodeMapRange")
hole.inputs["From Min"].default_value = 0.13
hole.inputs["From Max"].default_value = 0.16
nt.links.new(ln.outputs["Value"], hole.inputs["Value"])
mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"
mixc.inputs["A"].default_value = (0.0, 0.0, 0.0, 1)
mixc.inputs["B"].default_value = (0.035, 0.037, 0.04, 1)
nt.links.new(hole.outputs["Result"], mixc.inputs["Factor"])
nt.links.new(mixc.outputs["Result"], tp.inputs["Base Color"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.6
nt.links.new(hole.outputs["Result"], bump.inputs["Height"])
# fine surface noise for realism
nz = nt.nodes.new("ShaderNodeTexNoise")
nz.inputs["Scale"].default_value = 900
rr = nt.nodes.new("ShaderNodeMapRange")
rr.inputs["To Min"].default_value = 0.3
rr.inputs["To Max"].default_value = 0.5
nt.links.new(nz.outputs["Fac"], rr.inputs["Value"])
nt.links.new(rr.outputs["Result"], tp.inputs["Roughness"])
nt.links.new(bump.outputs["Normal"], tp.inputs["Normal"])
assign(table, tm)

steel, sp = principled("Steel", **{"Base Color": (0.62, 0.62, 0.63, 1), "Metallic": 1.0, "Roughness": 0.22, "Anisotropic": 0.6})
black_al, _ = principled("BlackAl", **{"Base Color": (0.02, 0.02, 0.022, 1), "Metallic": 0.7, "Roughness": 0.45})
glass, _ = principled("Glass", **{"Base Color": (0.95, 0.97, 1.0, 1), "Roughness": 0.0, "IOR": 1.46, "Transmission Weight": 1.0})
mirror, _ = principled("Mirror", **{"Base Color": (0.95, 0.9, 0.85, 1), "Metallic": 1.0, "Roughness": 0.02})
copper, _ = principled("Copper", **{"Base Color": (0.95, 0.55, 0.35, 1), "Metallic": 1.0, "Roughness": 0.3})

# --- Glass cell (hollow quartz cuboid) with steel flange tube -----------------------------------
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.16))
cell = bpy.context.object
cell.scale = (0.05, 0.05, 0.05)
bpy.ops.object.transform_apply(scale=True)
sol = cell.modifiers.new("shell", "SOLIDIFY"); sol.thickness = 0.004
bev = cell.modifiers.new("bevel", "BEVEL"); bev.width = 0.0015; bev.segments = 3
assign(cell, glass)

bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.22, location=(0.145, 0, 0.16), rotation=(0, math.radians(90), 0), vertices=64)
assign(smooth(bpy.context.object), steel)
for x in (0.04, 0.255):  # conflat flanges
    bpy.ops.mesh.primitive_cylinder_add(radius=0.052, depth=0.016, location=(x, 0, 0.16), rotation=(0, math.radians(90), 0), vertices=96)
    assign(smooth(bpy.context.object), steel)
    for k in range(8):  # bolts
        a = k / 8 * 2 * math.pi
        bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.03, location=(x, 0.043 * math.cos(a), 0.16 + 0.043 * math.sin(a)), rotation=(0, math.radians(90), 0), vertices=6)
        assign(bpy.context.object, steel)
# pedestal under the chamber
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.11, location=(0.2, 0, 0.055), vertices=48)
assign(smooth(bpy.context.object), black_al)

# --- MOT coils (copper rings) above and below the cell -------------------------------------------
for z in (0.225, 0.095):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.009, location=(0, 0, z), major_segments=96, minor_segments=24)
    assign(smooth(bpy.context.object), copper)

# --- Atom cloud: blue volumetric glow (Sr 461 nm) ------------------------------------------------
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(0, 0, 0.16), segments=48, ring_count=24)
cloud = bpy.context.object
cloud.scale = (1.0, 1.0, 0.75)
cm = bpy.data.materials.new("Cloud")
cm.use_nodes = True
cn = cm.node_tree
cn.nodes.remove(cn.nodes["Principled BSDF"])
vol = cn.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Density"].default_value = 0.0
vol.inputs["Emission Color"].default_value = (0.02, 0.15, 1.0, 1)
grad = cn.nodes.new("ShaderNodeTexGradient"); grad.gradient_type = "SPHERICAL"
nz2 = cn.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 6
mul = cn.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
pw = cn.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 3.0
gain = cn.nodes.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.inputs[1].default_value = float(__import__("os").environ.get("CLOUD_GAIN", "8000"))
tco = cn.nodes.new("ShaderNodeTexCoord")
centre = cn.nodes.new("ShaderNodeVectorMath"); centre.operation = "SUBTRACT"
centre.inputs[1].default_value = (0.5, 0.5, 0.5)
cn.links.new(tco.outputs["Generated"], centre.inputs[0])
twice = cn.nodes.new("ShaderNodeVectorMath"); twice.operation = "SCALE"
twice.inputs["Scale"].default_value = 2.0
cn.links.new(centre.outputs[0], twice.inputs[0])
cn.links.new(twice.outputs[0], grad.inputs["Vector"])
cn.links.new(tco.outputs["Object"], nz2.inputs["Vector"])
cn.links.new(grad.outputs["Fac"], pw.inputs[0])
cn.links.new(pw.outputs[0], mul.inputs[0])
cn.links.new(nz2.outputs["Fac"], mul.inputs[1])
cn.links.new(mul.outputs[0], gain.inputs[0])
cn.links.new(gain.outputs[0], vol.inputs["Emission Strength"])
cn.links.new(vol.outputs[0], cn.nodes["Material Output"].inputs["Volume"])
clear = cn.nodes.new("ShaderNodeBsdfTransparent")
cn.links.new(clear.outputs[0], cn.nodes["Material Output"].inputs["Surface"])
assign(cloud, cm)
# faint point light so the glow spills onto glass and coils
bpy.ops.object.light_add(type="POINT", location=(0, 0, 0.16))
pl = bpy.context.object
pl.data.energy, pl.data.color, pl.data.shadow_soft_size = 1.5, (0.2, 0.4, 1.0), 0.01
pl.visible_camera = False
pl.visible_glossy = False
pl.visible_transmission = False


def beam(p0, p1, color, strength, radius=0.0005):
    """Thin emissive cylinder between two points (laser beam made visible, as if through haze)."""
    import mathutils
    a, b = mathutils.Vector(p0), mathutils.Vector(p1)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=d.length, location=(a + b) / 2, vertices=16)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    m = bpy.data.materials.new("Beam")
    m.use_nodes = True
    n = m.node_tree
    n.nodes.remove(n.nodes["Principled BSDF"])
    em = n.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    tr = n.nodes.new("ShaderNodeBsdfTransparent")
    mix = n.nodes.new("ShaderNodeMixShader")
    lw = n.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    n.links.new(lw.outputs["Facing"], mix.inputs["Fac"])
    n.links.new(em.outputs[0], mix.inputs[1])
    n.links.new(tr.outputs[0], mix.inputs[2])
    n.links.new(mix.outputs[0], n.nodes["Material Output"].inputs["Surface"])
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


def mirror_mount(pos, face_deg):
    x, y = pos
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.13, location=(x, y, 0.065), vertices=32)
    assign(smooth(bpy.context.object), steel)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.16), rotation=(0, 0, math.radians(face_deg)))
    body = bpy.context.object
    body.scale = (0.012, 0.04, 0.04)
    bev = body.modifiers.new("b", "BEVEL"); bev.width = 0.002; bev.segments = 2
    assign(body, black_al)
    r = math.radians(face_deg)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0127, depth=0.006,
                                        location=(x - 0.008 * math.cos(r), y - 0.008 * math.sin(r), 0.16),
                                        rotation=(0, math.radians(90), r), vertices=64)
    assign(smooth(bpy.context.object), mirror)


# Two horizontal MOT beams crossing at the cloud, bounced by mirrors
M1, M2 = (-0.32, 0.0), (0.0, -0.32)
mirror_mount(M1, 0)
mirror_mount(M2, 90)
mirror_mount((-0.32, -0.32), 45)
BLUE = (0.05, 0.25, 1.0)
beam((-0.32, 0, 0.16), (0.32, 0, 0.16), BLUE, 3)
beam((0, -0.32, 0.16), (0, 0.32, 0.16), BLUE, 3)
beam((-0.32, -0.32, 0.16), (-0.32, 0, 0.16), BLUE, 3)
beam((-0.32, -0.32, 0.16), (0, -0.32, 0.16), BLUE, 3)
# red lattice laser, vertical-ish, the "clock" laser
RED = (1.0, 0.05, 0.02)
beam((0.0, 0.0, 0.0), (0.0, 0.0, 0.5), RED, 5, radius=0.0004)

# Background clutter for bokeh: more posts and tiny indicator LEDs far behind
import random
random.seed(3)
for i in range(14):
    x, y = random.uniform(-1.0, 0.9), random.uniform(0.35, 1.3)
    h = random.uniform(0.08, 0.3)
    bpy.ops.mesh.primitive_cylinder_add(radius=random.uniform(0.006, 0.03), depth=h, location=(x, y, h / 2), vertices=24)
    assign(smooth(bpy.context.object), random.choice([steel, black_al]))
for i in range(22):
    x, y, z = random.uniform(-1.2, 1.2), random.uniform(0.8, 1.4), random.uniform(0.05, 0.6)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.004, location=(x, y, z), segments=8, ring_count=6)
    col = random.choice([(1, 0.25, 0.05), (0.1, 1, 0.2), (0.2, 0.5, 1), (1, 0.8, 0.4)])
    lm = bpy.data.materials.new("LED")
    lm.use_nodes = True
    lmn = lm.node_tree
    lmn.nodes.remove(lmn.nodes["Principled BSDF"])
    e = lmn.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*col, 1)
    e.inputs["Strength"].default_value = 40
    lmn.links.new(e.outputs[0], lmn.nodes["Material Output"].inputs["Surface"])
    assign(bpy.context.object, lm)

# --- Lights ------------------------------------------------------------------------------------
def area(loc, rot, energy, size, color):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=[math.radians(r) for r in rot])
    L = bpy.context.object
    L.data.energy, L.data.size, L.data.color = energy, size, color
    return L

area((0.2, -0.6, 0.9), (35, 0, 15), 40, 0.8, (0.75, 0.85, 1.0))     # soft cool key
area((-0.2, 0.9, 0.5), (-65, 0, 190), 25, 0.5, (1.0, 0.75, 0.55))    # warm back rim
area((0.9, 0.2, 0.25), (90, 0, 95), 6, 0.3, (0.8, 0.85, 1.0))       # side kicker for steel

# --- Camera: low, close, shallow DOF, slow push-in -----------------------------------------------
bpy.ops.object.camera_add()
cam = bpy.context.object
cam.data.lens = 70
cam.data.sensor_width = 36
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 2.8
target = bpy.data.objects.new("Target", None)
sc.collection.objects.link(target)
target.location = (0.01, 0, 0.16)
cam.data.dof.focus_object = target
tr = cam.constraints.new("TRACK_TO")
tr.target = target
tr.track_axis = "TRACK_NEGATIVE_Z"
tr.up_axis = "UP_Y"
sc.camera = cam

import os
CAM = os.environ.get("CAM", "push")
FRAMES = int(os.environ.get("FRAMES", "120"))
sc.frame_start, sc.frame_end = 1, FRAMES
if CAM == "orbit":  # high angle, slow arc around the cell
    cam.data.lens = 50
    for f, deg in ((1, -125), (FRAMES // 2, -95), (FRAMES, -65)):
        a = math.radians(deg)
        cam.location = (0.6 * math.cos(a), 0.6 * math.sin(a), 0.62)
        cam.keyframe_insert("location", frame=f)
elif CAM == "macro":  # tight on the glowing cloud, lateral slide
    cam.data.lens = 105
    cam.data.dof.aperture_fstop = 2.0
    cam.location = (-0.30, -0.36, 0.215)
    cam.keyframe_insert("location", frame=1)
    cam.location = (-0.18, -0.42, 0.195)
    cam.keyframe_insert("location", frame=FRAMES)
else:
    cam.location = (-0.62, -0.95, 0.42)
    cam.keyframe_insert("location", frame=1)
    cam.location = (-0.48, -0.74, 0.34)
    cam.keyframe_insert("location", frame=FRAMES)
for fc in cam.animation_data.action.fcurves if hasattr(cam.animation_data.action, "fcurves") else []:
    for kp in fc.keyframe_points:
        kp.interpolation = "SINE"

sc.render.image_settings.file_format = "PNG"
if MODE == "still":
    sc.frame_set(60)
    sc.render.filepath = OUT + ".png"
    bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = OUT + "_"
    bpy.ops.render.render(animation=True)
