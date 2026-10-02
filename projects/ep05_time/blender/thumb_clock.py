# Thumbnail hero stills for EP04 — one visual idea per frame, lit as one scene.
#   SCENE=rings     the Earth cut open like a tree trunk: count the rings to know its age
#   SCENE=hourglass the Earth inside an hourglass, molten rock running out below
#   SCENE=lead      liquid lead poured over the Earth
# Run: blender -b -P thumb_scenes.py -- <out_prefix> still <samples>
import bpy, bmesh, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, MODE, SAMPLES = C.args()
SCENE = os.environ.get("SCENE", "rings")
sc = C.setup(SAMPLES, 1, bg=(0.0, 0.0, 0.0))
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.view_settings.look = "AgX - High Contrast"
sc.cycles.max_bounces = 12
sc.cycles.transmission_bounces = 12


def node(nt, kind, **inputs):
    n = nt.nodes.new(kind)
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


def earth(radius=1.0, loc=(0, 0, 0), clouds=True, atmosphere=True):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=192, ring_count=96, location=loc)
    e = bpy.context.object
    for p in e.data.polygons:
        p.use_smooth = True
    m = bpy.data.materials.new("Earth"); m.use_nodes = True
    nt = m.node_tree; pb = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(os.path.join(HERE, "tex", "earth5k.jpg"))
    nt.links.new(tex.outputs["Color"], pb.inputs["Base Color"])
    # oceans shinier than land: blue channel dominance as a cheap water mask
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(tex.outputs["Color"], sep.inputs[0])
    sub = node(nt, "ShaderNodeMath"); sub.operation = "SUBTRACT"
    nt.links.new(sep.outputs[2], sub.inputs[0]); nt.links.new(sep.outputs[0], sub.inputs[1])
    rr = node(nt, "ShaderNodeMapRange"); rr.inputs["From Min"].default_value = 0.02; rr.inputs["From Max"].default_value = 0.12
    rr.inputs["To Min"].default_value = 0.75; rr.inputs["To Max"].default_value = 0.25
    nt.links.new(sub.outputs[0], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], pb.inputs["Roughness"])
    e.data.materials.append(m)
    if clouds:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius * 1.008, segments=192, ring_count=96, location=loc)
        c = bpy.context.object
        for p in c.data.polygons:
            p.use_smooth = True
        cm = bpy.data.materials.new("Clouds"); cm.use_nodes = True
        cn = cm.node_tree; cpb = cn.nodes["Principled BSDF"]
        ct = cn.nodes.new("ShaderNodeTexImage"); ct.image = bpy.data.images.load(os.path.join(HERE, "tex", "clouds.jpg"))
        cpb.inputs["Base Color"].default_value = (1, 1, 1, 1)
        cn.links.new(ct.outputs["Color"], cpb.inputs["Alpha"])
        c.data.materials.append(cm)
        c.parent = e; c.location = (0, 0, 0)
    if atmosphere:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius * 1.035, segments=128, ring_count=64, location=loc)
        a = bpy.context.object
        for p in a.data.polygons:
            p.use_smooth = True
        am = bpy.data.materials.new("Atmo"); am.use_nodes = True
        an = am.node_tree; an.nodes.remove(an.nodes["Principled BSDF"])
        lw = node(an, "ShaderNodeLayerWeight", Blend=0.12)
        em = node(an, "ShaderNodeEmission", Color=(0.25, 0.55, 1.0, 1), Strength=2.2)
        tr = an.nodes.new("ShaderNodeBsdfTransparent")
        mx = an.nodes.new("ShaderNodeMixShader")
        an.links.new(lw.outputs["Facing"], mx.inputs["Fac"])
        an.links.new(tr.outputs[0], mx.inputs[1]); an.links.new(em.outputs[0], mx.inputs[2])
        an.links.new(mx.outputs[0], an.nodes["Material Output"].inputs["Surface"])
        a.data.materials.append(am)
        a.parent = e; a.location = (0, 0, 0)
        a.visible_shadow = False
    return e


def stars(n=1400, seed=4, strength=0.6):
    wn = sc.world.node_tree; bg = wn.nodes["Background"]
    vor = node(wn, "ShaderNodeTexVoronoi", Scale=420)
    ramp = wn.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
    ramp.color_ramp.elements[1].position = 0.025; ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    wn.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    mul = node(wn, "ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = strength
    wn.links.new(ramp.outputs["Color"], mul.inputs[0]); wn.links.new(mul.outputs[0], bg.inputs["Strength"])
    bg.inputs["Color"].default_value = (1, 1, 1, 1)


def sun(rot, energy, color=(1, 0.96, 0.9)):
    bpy.ops.object.light_add(type="SUN"); s = bpy.context.object
    s.data.energy = energy; s.data.color = color; s.data.angle = math.radians(1.5)
    s.rotation_euler = [math.radians(r) for r in rot]
    return s


# =================================================================================================
# SCENE=clock: the Earth as a clock face — hands rising out of the North Pole, hour marks orbiting it
stars(strength=0.5)
e = earth(1.0, clouds=True, atmosphere=True)
e.rotation_euler = (math.radians(-62), 0, math.radians(20))       # tilt the north pole towards camera
brass = C.principled("Brass", **{"Base Color": (0.95, 0.72, 0.38, 1), "Metallic": 1.0, "Roughness": 0.22,
                                  "Emission Color": (1.0, 0.75, 0.4, 1), "Emission Strength": 1.2})
white = C.emission("Tick", (1.0, 0.92, 0.75), 6)[0]
# hands: long minute hand, short hour hand, thin red second hand, pinned at the pole
pole = (0, -0.46, 0.89)
import mathutils
axis = mathutils.Vector(pole).normalized()
def hand(length, width, angle, mat, lift):
    bpy.ops.mesh.primitive_cube_add(size=1)
    h = bpy.context.object
    h.scale = (width, length, 0.012)
    h.location = (0, length / 2, 0)
    bpy.ops.object.transform_apply(location=True, scale=True)
    piv = bpy.data.objects.new("pivot", None); sc.collection.objects.link(piv)
    h.parent = piv
    piv.location = axis * (1.0 + lift)
    piv.rotation_mode = "QUATERNION"
    piv.rotation_quaternion = axis.to_track_quat("Z", "Y") @ mathutils.Quaternion((0, 0, 1), math.radians(angle))
    h.data.materials.append(mat)
    return h
hand(0.95, 0.045, 25, brass, 0.03)
hand(0.62, 0.07, -70, brass, 0.05)
hand(1.05, 0.012, 150, C.principled("Red", **{"Base Color": (0.9, 0.05, 0.03, 1), "Roughness": 0.3}), 0.07)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=axis * 1.08)
C.add(bpy.context.object, brass, smooth=True)
# twelve glowing hour marks on a ring around the pole
for k in range(12):
    bpy.ops.mesh.primitive_cube_add(size=1)
    t = bpy.context.object
    t.scale = (0.03, 0.16 if k % 3 == 0 else 0.09, 0.01)
    bpy.ops.object.transform_apply(scale=True)
    piv = bpy.data.objects.new("tp", None); sc.collection.objects.link(piv)
    t.parent = piv; t.location = (0, 1.17, 0)
    piv.location = axis * 1.02
    piv.rotation_mode = "QUATERNION"
    piv.rotation_quaternion = axis.to_track_quat("Z", "Y") @ mathutils.Quaternion((0, 0, 1), math.radians(30 * k))
    t.data.materials.append(white)
sun((55, 0, -30), 5.0)
C.area((3, -2, 2), (60, 0, 55), 300, 3, (0.8, 0.9, 1.0))
cam, tgt = C.camera(50, 8, (0, 0, 0), focus=False)
cam.location = axis * 6.0 + mathutils.Vector((0.35, -0.25, -0.35))    # looking down the clock's axis, slightly off
if os.environ.get("ALPHA"):
    sc.render.film_transparent = True

C.render(sc, OUT, "still", still_frame=1)
