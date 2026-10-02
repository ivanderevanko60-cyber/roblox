# Kelvin's picture: a young Earth as a ball of molten rock, a dark crust spreading over it as it cools.
# Run: blender -b -P molten.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "150"))
sc = C.setup(SAMPLES, FRAMES, bg=(0, 0, 0))

bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=256, ring_count=128)
ball = bpy.context.object
for p in ball.data.polygons:
    p.use_smooth = True

m = bpy.data.materials.new("Molten"); m.use_nodes = True
n = m.node_tree; out = n.nodes["Material Output"]; pb = n.nodes["Principled BSDF"]
tc = n.nodes.new("ShaderNodeTexCoord")
warp = n.nodes.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 2.0; warp.inputs["Detail"].default_value = 6
n.links.new(tc.outputs["Object"], warp.inputs["Vector"])
wmix = n.nodes.new("ShaderNodeMix"); wmix.data_type = "VECTOR"; wmix.inputs["Factor"].default_value = 0.35
n.links.new(tc.outputs["Object"], wmix.inputs["A"]); n.links.new(warp.outputs["Color"], wmix.inputs["B"])
nz = n.nodes.new("ShaderNodeTexVoronoi"); nz.feature = "DISTANCE_TO_EDGE"; nz.inputs["Scale"].default_value = 7
n.links.new(wmix.outputs["Result"], nz.inputs["Vector"])
# crust threshold rises over time: glowing cracks shrink as the planet cools
thr = n.nodes.new("ShaderNodeValue"); thr.label = "cool"
cmp = n.nodes.new("ShaderNodeMapRange"); cmp.clamp = True
n.links.new(nz.outputs["Distance"], cmp.inputs["Value"])
n.links.new(thr.outputs[0], cmp.inputs["From Min"])
add = n.nodes.new("ShaderNodeMath"); add.operation = "ADD"; add.inputs[1].default_value = 0.02
n.links.new(thr.outputs[0], add.inputs[0]); n.links.new(add.outputs[0], cmp.inputs["From Max"])
inv = n.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
n.links.new(cmp.outputs["Result"], inv.inputs[1])                   # 1 = hot crack, 0 = crust
pb.inputs["Base Color"].default_value = (0.02, 0.018, 0.017, 1); pb.inputs["Roughness"].default_value = 0.85
lava = n.nodes.new("ShaderNodeBlackbody"); lava.inputs["Temperature"].default_value = 1250
em = n.nodes.new("ShaderNodeEmission"); n.links.new(lava.outputs[0], em.inputs["Color"])
es = n.nodes.new("ShaderNodeMath"); es.operation = "MULTIPLY"; es.inputs[1].default_value = 9
n.links.new(inv.outputs[0], es.inputs[0]); n.links.new(es.outputs[0], em.inputs["Strength"])
mixs = n.nodes.new("ShaderNodeAddShader")
n.links.new(pb.outputs[0], mixs.inputs[0]); n.links.new(em.outputs[0], mixs.inputs[1])
n.links.new(mixs.outputs[0], out.inputs["Surface"])
bump = n.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.5
n.links.new(cmp.outputs["Result"], bump.inputs["Height"]); n.links.new(bump.outputs["Normal"], pb.inputs["Normal"])
ball.data.materials.append(m)
thr.outputs[0].default_value = 0.10; thr.outputs[0].keyframe_insert("default_value", frame=1)
thr.outputs[0].default_value = 0.012; thr.outputs[0].keyframe_insert("default_value", frame=FRAMES)
C.key_path(ball, [(1, (0, 0, 0)), (FRAMES, (0, 0, math.radians(22)))], "rotation_euler")

bpy.ops.object.light_add(type="SUN"); s = bpy.context.object
s.data.energy = 3.0; s.rotation_euler = (math.radians(70), 0, math.radians(-60))

cam, tgt = C.camera(60, 8, (0.25, 0, 0), focus=False)
C.key_path(cam, [(1, (1.2, -4.4, 0.6)), (FRAMES, (1.0, -3.9, 0.45))])

C.render(sc, OUT, MODE)
