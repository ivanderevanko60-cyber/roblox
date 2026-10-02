# Earth from space with two glowing around-the-world flight paths (east: gold, west: blue) drawing on.
# Textures: NASA Blue Marble (day) + Black Marble 2012 (night lights), public domain.
# Run: blender -b -P globe.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "150"))
sc = C.setup(SAMPLES, FRAMES, bg=(0, 0, 0))
sc.view_settings.look = "AgX - High Contrast"

# --- starfield world ------------------------------------------------------------------------------
wn = sc.world.node_tree
bg = wn.nodes["Background"]
vor = wn.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 420
ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
ramp.color_ramp.elements[1].position = 0.035
ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
wn.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
mulw = wn.nodes.new("ShaderNodeMath"); mulw.operation = "MULTIPLY"; mulw.inputs[1].default_value = 0.6
wn.links.new(ramp.outputs["Color"], mulw.inputs[0])
wn.links.new(mulw.outputs[0], bg.inputs["Strength"])
bg.inputs["Color"].default_value = (1, 1, 1, 1)

# --- Earth ------------------------------------------------------------------------------------------
R = 1.0
bpy.ops.mesh.primitive_uv_sphere_add(radius=R, segments=192, ring_count=96)
earth = bpy.context.object
for p in earth.data.polygons:
    p.use_smooth = True
m = bpy.data.materials.new("Earth")
m.use_nodes = True
n = m.node_tree
pb = n.nodes["Principled BSDF"]
day = n.nodes.new("ShaderNodeTexImage"); day.image = bpy.data.images.load(os.path.join(HERE, "tex", "earth_day.jpg"))
night = n.nodes.new("ShaderNodeTexImage"); night.image = bpy.data.images.load(os.path.join(HERE, "tex", "earth_night.jpg"))
n.links.new(day.outputs["Color"], pb.inputs["Base Color"])
pb.inputs["Roughness"].default_value = 0.65
pb.inputs["Specular IOR Level"].default_value = 0.35
# night lights only where the sun doesn't reach: mask = clamp(-(N . sun_dir) * 4)
geo = n.nodes.new("ShaderNodeNewGeometry")
SUN_DIR = (0.85, -0.35, 0.25)
dot = n.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"
dot.inputs[1].default_value = SUN_DIR
n.links.new(geo.outputs["Normal"], dot.inputs[0])
neg = n.nodes.new("ShaderNodeMath"); neg.operation = "MULTIPLY"; neg.inputs[1].default_value = -4.0
n.links.new(dot.outputs["Value"], neg.inputs[0])
cl = n.nodes.new("ShaderNodeClamp")
n.links.new(neg.outputs[0], cl.inputs["Value"])
lights = n.nodes.new("ShaderNodeMath"); lights.operation = "MULTIPLY"; lights.inputs[1].default_value = 3.0
n.links.new(cl.outputs[0], lights.inputs[0])
n.links.new(night.outputs["Color"], pb.inputs["Emission Color"])
n.links.new(lights.outputs[0], pb.inputs["Emission Strength"])
earth.data.materials.append(m)

# --- atmosphere: thin scattering shell + rim glow -------------------------------------------------
bpy.ops.mesh.primitive_uv_sphere_add(radius=R * 1.025, segments=128, ring_count=64)
atm = bpy.context.object
for p in atm.data.polygons:
    p.use_smooth = True
am = bpy.data.materials.new("Atmos")
am.use_nodes = True
an = am.node_tree
an.nodes.remove(an.nodes["Principled BSDF"])
em = an.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.25, 0.5, 1.0, 1)
lw = an.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.12
pw = an.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 3.0
an.links.new(lw.outputs["Facing"], pw.inputs[0])
st = an.nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = 2.2
an.links.new(pw.outputs[0], st.inputs[0])
an.links.new(st.outputs[0], em.inputs["Strength"])
tr = an.nodes.new("ShaderNodeBsdfTransparent")
add = an.nodes.new("ShaderNodeAddShader")
an.links.new(em.outputs[0], add.inputs[0]); an.links.new(tr.outputs[0], add.inputs[1])
an.links.new(add.outputs[0], an.nodes["Material Output"].inputs["Surface"])
atm.data.materials.append(am)
atm.visible_shadow = False

# --- flight paths: mid-latitude loops around the planet, drawn over time ---------------------------
def route(lat_deg, color, start, end, reverse):
    lat = math.radians(lat_deg)
    bpy.ops.curve.primitive_bezier_circle_add(radius=R * 1.012 * math.cos(lat), location=(0, 0, R * 1.012 * math.sin(lat)))
    c = bpy.context.object
    c.data.resolution_u = 64
    c.data.bevel_depth = 0.0022
    c.data.bevel_resolution = 2
    if reverse:
        c.scale = (1, -1, 1)
    c.parent = earth
    mat, emn = C.emission("Route", color, 5.0)
    c.data.materials.append(mat)
    c.data.bevel_factor_end = 0.0
    c.data.keyframe_insert("bevel_factor_end", frame=start)
    c.data.bevel_factor_end = 1.0
    c.data.keyframe_insert("bevel_factor_end", frame=end)
    return c

earth.rotation_euler = (0, 0, 0)
route(39, (1.0, 0.55, 0.12), 10, 110, False)   # eastbound (gold)
route(33, (0.2, 0.55, 1.0), 40, 140, True)     # westbound (blue)
earth.animation_data_clear()
ROT0 = math.radians(float(os.environ.get("EARTH_ROT", "0")))
C.key_path(earth, [(1, (math.radians(-10), 0, ROT0)), (FRAMES, (math.radians(-10), 0, ROT0 + math.radians(25)))], "rotation_euler")

# --- sun + camera ----------------------------------------------------------------------------------
bpy.ops.object.light_add(type="SUN")
sun = bpy.context.object
sun.data.energy = 4.5
sun.data.angle = math.radians(0.6)
import mathutils
sun.rotation_euler = (-mathutils.Vector(SUN_DIR)).to_track_quat("-Z", "Y").to_euler()

cam, tgt = C.camera(62, 8.0, (0, 0, 0), focus=False)
C.key_path(cam, [(1, (1.6, -4.6, 2.2)), (FRAMES, (0.9, -4.6, 2.4))])
C.key_path(tgt, [(1, (0.0, 0, 0.1)), (FRAMES, (0.0, 0, 0.1))])

C.render(sc, OUT, MODE, still_frame=120)
