# Io slipping into Jupiter's shadow — the observation that proved light has a speed.
# Texture: Cassini cylindrical map of Jupiter (NASA/JPL/Space Science Institute, public domain).
# Run: blender -b -P jupiter_io.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "120"))
sc = C.setup(SAMPLES, FRAMES, bg=(0, 0, 0))
sc.view_settings.look = "AgX - High Contrast"

# --- starfield --------------------------------------------------------------------------------
wn = sc.world.node_tree
bg = wn.nodes["Background"]
vor = wn.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 520
ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
ramp.color_ramp.elements[1].position = 0.03; ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
wn.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
mul = wn.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 0.5
wn.links.new(ramp.outputs["Color"], mul.inputs[0])
wn.links.new(mul.outputs[0], bg.inputs["Strength"])
bg.inputs["Color"].default_value = (1, 1, 1, 1)

# --- Jupiter ----------------------------------------------------------------------------------
RJ = 1.0
bpy.ops.mesh.primitive_uv_sphere_add(radius=RJ, segments=256, ring_count=128, location=(0, 0, 0))
jup = bpy.context.object
jup.scale = (1, 1, 0.935)                      # Jupiter is visibly oblate
for p in jup.data.polygons:
    p.use_smooth = True
m = bpy.data.materials.new("Jupiter")
m.use_nodes = True
n = m.node_tree
pb = n.nodes["Principled BSDF"]
tex = n.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(os.path.join(HERE, "tex", "jupiter.jpg"))
n.links.new(tex.outputs["Color"], pb.inputs["Base Color"])
pb.inputs["Roughness"].default_value = 0.9
pb.inputs["Specular IOR Level"].default_value = 0.1
jup.data.materials.append(m)
C.key_path(jup, [(1, (0, 0, 0)), (FRAMES, (0, 0, math.radians(4)))], "rotation_euler")

# --- Io: small, sulphur-yellow, on an orbit that carries it behind the planet -------------------
RIO = 0.045                                      # slightly enlarged so it reads on screen
bpy.ops.mesh.primitive_uv_sphere_add(radius=RIO, segments=64, ring_count=32)
io = bpy.context.object
for p in io.data.polygons:
    p.use_smooth = True
im = bpy.data.materials.new("Io")
im.use_nodes = True
inn = im.node_tree
ipb = inn.nodes["Principled BSDF"]
nz = inn.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9
ramp2 = inn.nodes.new("ShaderNodeValToRGB")
ramp2.color_ramp.elements[0].color = (0.82, 0.62, 0.20, 1)
ramp2.color_ramp.elements[1].color = (0.95, 0.88, 0.55, 1)
inn.links.new(nz.outputs["Fac"], ramp2.inputs["Fac"])
inn.links.new(ramp2.outputs["Color"], ipb.inputs["Base Color"])
ipb.inputs["Roughness"].default_value = 0.95
io.data.materials.append(im)
# orbit: comes from the right, passes behind Jupiter into the shadow
C.key_path(io, [(1, (1.62, -0.95, 0.05)), (FRAMES, (1.18, -0.30, 0.05))])

# --- sun: hard light from the left, so the right side of Jupiter carries the shadow -------------
bpy.ops.object.light_add(type="SUN")
sun = bpy.context.object
sun.data.energy = 6.0
sun.data.angle = math.radians(0.1)
sun.rotation_euler = (math.radians(88), 0, math.radians(58))

cam, tgt = C.camera(70, 8.0, (0.35, 0, 0), focus=False)
C.key_path(cam, [(1, (2.0, -4.6, 0.75)), (FRAMES, (1.75, -4.5, 0.62))])

C.render(sc, OUT, MODE)
