# A zircon crystal with its atoms visible inside: uranium (green) slowly turning into lead (grey-blue).
# Run: blender -b -P zircon.py -- <out_prefix> [still|anim] [samples]
import bpy, bmesh, math, os, random, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "150"))
sc = C.setup(SAMPLES, FRAMES, bg=(0.003, 0.003, 0.004))

# --- crystal: square prism with pyramidal ends (the zircon habit) ------------------------------
W, H, P = 0.22, 0.62, 0.2           # half-width, prism height, pyramid height
me = bpy.data.meshes.new("Zircon"); bm = bmesh.new()
sq = [(W, W), (-W, W), (-W, -W), (W, -W)]
bot = [bm.verts.new((x, y, 0)) for x, y in sq]
top = [bm.verts.new((x, y, H)) for x, y in sq]
tip_b = bm.verts.new((0, 0, -P)); tip_t = bm.verts.new((0, 0, H + P))
for i in range(4):
    j = (i + 1) % 4
    bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.faces.new((top[i], top[j], tip_t))
    bm.faces.new((bot[j], bot[i], tip_b))
bm.to_mesh(me); bm.free()
xtal = bpy.data.objects.new("Zircon", me); sc.collection.objects.link(xtal)
xtal.location = (0, 0, 0.12 + P); xtal.rotation_euler = (math.radians(8), math.radians(-14), math.radians(20))
bev = xtal.modifiers.new("bev", "BEVEL"); bev.width = 0.006; bev.segments = 3
glass = C.principled("ZirconGlass", **{"Base Color": (1.0, 0.55, 0.30, 1), "Transmission Weight": 1.0, "IOR": 1.95,
                                       "Roughness": 0.04})
xtal.data.materials.append(glass)
C.key_path(xtal, [(1, xtal.rotation_euler[:]), (FRAMES, (math.radians(8), math.radians(-14), math.radians(62)))], "rotation_euler")

# --- atoms inside: each one flips from uranium-green to lead-grey at its own moment -------------
random.seed(7)
atom = bpy.data.materials.new("Atom"); atom.use_nodes = True
an = atom.node_tree; an.nodes.remove(an.nodes["Principled BSDF"])
attr = an.nodes.new("ShaderNodeAttribute"); attr.attribute_type = "OBJECT"; attr.attribute_name = "decay"
mix = an.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
mix.inputs["A"].default_value = (0.25, 1.0, 0.35, 1)       # uranium
mix.inputs["B"].default_value = (0.55, 0.62, 0.78, 1)      # lead
an.links.new(attr.outputs["Fac"], mix.inputs["Factor"])
strength = an.nodes.new("ShaderNodeMapRange"); strength.inputs["To Min"].default_value = 3.5; strength.inputs["To Max"].default_value = 1.0
an.links.new(attr.outputs["Fac"], strength.inputs["Value"])
em = an.nodes.new("ShaderNodeEmission")
an.links.new(mix.outputs["Result"], em.inputs["Color"]); an.links.new(strength.outputs["Result"], em.inputs["Strength"])
an.links.new(em.outputs[0], an.nodes["Material Output"].inputs["Surface"])
for k in range(45):
    x, y, z = random.uniform(-0.8, 0.8) * W, random.uniform(-0.8, 0.8) * W, random.uniform(0.05, 0.95) * H
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.008, segments=12, ring_count=8, location=(x, y, z))
    a = bpy.context.object; a.parent = xtal; a.data.materials.append(atom)
    a["decay"] = 0.0
    t = random.uniform(0.15, 0.95) * FRAMES
    a.keyframe_insert('["decay"]', frame=max(1, int(t) - 4))
    a["decay"] = 1.0 if random.random() < 0.55 else 0.0          # about half have decayed by the end
    a.keyframe_insert('["decay"]', frame=int(t))

# --- base: dark slate with a soft reflection ------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
C.add(bpy.context.object, C.principled("Slate", **{"Base Color": (0.01, 0.01, 0.011, 1), "Roughness": 0.3}))

C.area((-1.8, -1.2, 1.8), (50, 0, -55), 180, 1.2, (1.0, 0.85, 0.7))
C.area((0.8, 2.0, 1.2), (-65, 0, 160), 300, 0.6, (0.6, 0.8, 1.0))
C.area((0, 0, 2.4), (0, 0, 0), 40, 2.5, (1, 1, 1))

cam, tgt = C.camera(90, 5.6, (0, 0, 0.55))
C.key_path(cam, [(1, (0.5, -5.2, 1.3)), (FRAMES, (0.25, -4.5, 1.1))])

C.render(sc, OUT, MODE)
