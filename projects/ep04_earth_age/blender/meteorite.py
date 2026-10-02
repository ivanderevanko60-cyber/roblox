# A fragment of an iron-stony meteorite on a dark plinth — the rock Patterson read the age of the Earth from.
# Run: blender -b -P meteorite.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "150"))
sc = C.setup(SAMPLES, FRAMES, bg=(0.004, 0.004, 0.005))

# --- the rock: a subdivided icosphere pushed around by two noise layers + regmaglypt dimples --------
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.5, location=(0, 0, 0.3))
rock = bpy.context.object
import random as _r; _r.seed(11)
for v in rock.data.vertices:                      # chipped, angular silhouette before smoothing
    v.co *= _r.uniform(0.78, 1.18)
sub = rock.modifiers.new("sub", "SUBSURF"); sub.levels = sub.render_levels = 5
rock.scale = (1.15, 0.9, 0.62)
for name, kind, size, strength in (("big", "CLOUDS", 0.4, 0.08), ("dimples", "VORONOI", 0.16, -0.05), ("fine", "CLOUDS", 0.05, 0.012)):
    t = bpy.data.textures.new(name, kind)
    if kind == "VORONOI":
        t.distance_metric = "DISTANCE"; t.noise_scale = size
    else:
        t.noise_scale = size; t.noise_depth = 4
    d = rock.modifiers.new(name, "DISPLACE"); d.texture = t; d.strength = strength; d.texture_coords = "LOCAL"
for p in rock.data.polygons:
    p.use_smooth = True

m = bpy.data.materials.new("Crust"); m.use_nodes = True
n = m.node_tree; pb = n.nodes["Principled BSDF"]
tc = n.nodes.new("ShaderNodeTexCoord")
nz = n.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14; nz.inputs["Detail"].default_value = 12
n.links.new(tc.outputs["Object"], nz.inputs["Vector"])
ramp = n.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.5; ramp.color_ramp.elements[0].color = (0.010, 0.009, 0.008, 1)
ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = (0.05, 0.028, 0.014, 1)   # rusty fusion crust
n.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
n.links.new(ramp.outputs["Color"], pb.inputs["Base Color"])
# metal flecks: small voronoi cells become polished iron-nickel
vo = n.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 60
n.links.new(tc.outputs["Object"], vo.inputs["Vector"])
fl = n.nodes.new("ShaderNodeMath"); fl.operation = "LESS_THAN"; fl.inputs[1].default_value = 0.08
n.links.new(vo.outputs["Distance"], fl.inputs[0])
n.links.new(fl.outputs[0], pb.inputs["Metallic"])
rough = n.nodes.new("ShaderNodeMapRange"); rough.inputs["To Min"].default_value = 0.8; rough.inputs["To Max"].default_value = 0.22
n.links.new(fl.outputs[0], rough.inputs["Value"])
n.links.new(rough.outputs["Result"], pb.inputs["Roughness"])
bump = n.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6; bump.inputs["Distance"].default_value = 0.01
n.links.new(nz.outputs["Fac"], bump.inputs["Height"])
n.links.new(bump.outputs["Normal"], pb.inputs["Normal"])
rock.data.materials.append(m)
C.key_path(rock, [(1, (0, 0, 0)), (FRAMES, (0, 0, math.radians(40)))], "rotation_euler")

# --- plinth: matte black stone -----------------------------------------------------------------
bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=0.12, location=(0, 0, -0.06), vertices=128)
C.add(bpy.context.object, C.principled("Plinth", **{"Base Color": (0.012, 0.012, 0.013, 1), "Roughness": 0.45}), smooth=True)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.12))
C.add(bpy.context.object, C.principled("Floor", **{"Base Color": (0.004, 0.004, 0.004, 1), "Roughness": 0.9}))

# --- light: warm key from the left, cold rim from behind, faint fill ---------------------------
C.area((-2.2, -1.6, 2.0), (55, 0, -55), 260, 1.6, (1.0, 0.82, 0.62))
C.area((1.6, 2.4, 1.4), (-70, 0, 145), 420, 0.8, (0.62, 0.78, 1.0))
C.area((2.6, -2.0, 0.6), (80, 0, 50), 25, 3.0, (0.9, 0.9, 1.0))

cam, tgt = C.camera(85, 3.2, (0, 0, 0.33))
C.key_path(cam, [(1, (0.3, -5.6, 1.6)), (FRAMES, (0.1, -4.9, 1.25))])

C.render(sc, OUT, MODE)
