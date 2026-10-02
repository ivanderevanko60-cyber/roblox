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
if SCENE == "rings":
    stars()
    e = earth(1.0, clouds=True, atmosphere=True)
    e.rotation_euler = (math.radians(15), 0, math.radians(-100))
    # cut a wedge out of the planet; the cut faces take the cutter's "rings" material
    bpy.ops.mesh.primitive_cube_add(size=2.2, location=(1.1, -1.1, 1.1))
    cutter = bpy.context.object
    cutter.rotation_euler = (0, 0, math.radians(10))
    rm = bpy.data.materials.new("Rings"); rm.use_nodes = True
    rn = rm.node_tree; rpb = rn.nodes["Principled BSDF"]
    tc = rn.nodes.new("ShaderNodeTexCoord")
    ln = node(rn, "ShaderNodeVectorMath"); ln.operation = "LENGTH"
    rn.links.new(tc.outputs["Object"], ln.inputs[0])
    # wobble the rings a little so they look grown, not machined
    nz = node(rn, "ShaderNodeTexNoise", Scale=6.0, Detail=4.0)
    rn.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    wob = node(rn, "ShaderNodeMath"); wob.operation = "MULTIPLY_ADD"
    wob.inputs[1].default_value = 0.03
    rn.links.new(nz.outputs["Fac"], wob.inputs[0]); rn.links.new(ln.outputs["Value"], wob.inputs[2])
    freq = node(rn, "ShaderNodeMath"); freq.operation = "MULTIPLY"; freq.inputs[1].default_value = 110
    rn.links.new(wob.outputs[0], freq.inputs[0])
    sine = node(rn, "ShaderNodeMath"); sine.operation = "SINE"; rn.links.new(freq.outputs[0], sine.inputs[0])
    ringc = rn.nodes.new("ShaderNodeValToRGB")
    ringc.color_ramp.elements[0].color = (0.16, 0.07, 0.025, 1); ringc.color_ramp.elements[1].color = (0.62, 0.36, 0.17, 1)
    ringc.color_ramp.elements[0].position = 0.08; ringc.color_ramp.elements[1].position = 0.32     # thin dark growth lines
    sn = node(rn, "ShaderNodeMapRange"); sn.inputs["From Min"].default_value = -1
    rn.links.new(sine.outputs[0], sn.inputs["Value"]); rn.links.new(sn.outputs["Result"], ringc.inputs["Fac"])
    # the core glows: blackbody emission fading out with radius
    core = node(rn, "ShaderNodeMapRange"); core.inputs["From Min"].default_value = 0.06; core.inputs["From Max"].default_value = 0.22
    core.inputs["To Min"].default_value = 1.0; core.inputs["To Max"].default_value = 0.0
    rn.links.new(ln.outputs["Value"], core.inputs["Value"])
    bb = node(rn, "ShaderNodeBlackbody", Temperature=2200)
    cmix = rn.nodes.new("ShaderNodeMix"); cmix.data_type = "RGBA"
    rn.links.new(core.outputs["Result"], cmix.inputs["Factor"])
    rn.links.new(ringc.outputs["Color"], cmix.inputs["A"]); rn.links.new(bb.outputs["Color"], cmix.inputs["B"])
    rn.links.new(cmix.outputs["Result"], rpb.inputs["Base Color"])
    emi = node(rn, "ShaderNodeMath"); emi.operation = "MULTIPLY"; emi.inputs[1].default_value = 14
    rn.links.new(core.outputs["Result"], emi.inputs[0])
    rn.links.new(bb.outputs["Color"], rpb.inputs["Emission Color"]); rn.links.new(emi.outputs[0], rpb.inputs["Emission Strength"])
    rpb.inputs["Roughness"].default_value = 0.55
    cutter.data.materials.append(rm)
    for obj in [e] + list(e.children):
        b = obj.modifiers.new("cut", "BOOLEAN"); b.operation = "DIFFERENCE"; b.object = cutter; b.solver = "EXACT"
        if hasattr(b, "material_mode"):
            b.material_mode = "TRANSFER"
    cutter.hide_render = True; cutter.display_type = "WIRE"
    sun((60, 0, -35), 5.5)
    C.area((3.5, -2.5, 1.5), (70, 0, 55), 250, 3, (0.9, 0.95, 1.0))
    cam, tgt = C.camera(50, 8, (0, 0, 0), focus=False)
    cam.location = (2.0, -4.0, 1.25)
    if os.environ.get("ALPHA"):                                        # planet alone; stars and text go on in 2D
        sc.render.film_transparent = True

elif SCENE == "hourglass":
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.004, 0.006, 1)
    # glass: a lathed profile (two bulbs and a narrow neck)
    prof = [(0.04, 0), (0.55, 0.05), (0.78, 0.35), (0.72, 0.75), (0.35, 1.05), (0.07, 1.22), (0.06, 1.3),
            (0.07, 1.38), (0.35, 1.55), (0.72, 1.85), (0.78, 2.25), (0.55, 2.55), (0.04, 2.6)]
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    for a, b in zip(vs, vs[1:]):
        bm.edges.new((a, b))
    me = bpy.data.meshes.new("Glass"); bm.to_mesh(me); bm.free()
    glass = bpy.data.objects.new("Glass", me); sc.collection.objects.link(glass)
    scr = glass.modifiers.new("lathe", "SCREW"); scr.steps = 128; scr.render_steps = 128; scr.use_merge_vertices = True
    sol = glass.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.02
    sub = glass.modifiers.new("smooth", "SUBSURF"); sub.levels = sub.render_levels = 2
    glass.location = (0, 0, -1.3)
    gm = C.principled("GlassMat", **{"Base Color": (1, 1, 1, 1), "Transmission Weight": 1.0, "IOR": 1.5, "Roughness": 0.0})
    glass.data.materials.append(gm)
    for p in glass.data.polygons:
        p.use_smooth = True
    # the Earth in the top bulb
    e = earth(0.46, loc=(0, 0, 0.62), clouds=True, atmosphere=False)
    e.rotation_euler = (math.radians(20), 0, math.radians(-60))
    # molten rock piling up in the bottom bulb, and the thin stream
    bpy.ops.mesh.primitive_cone_add(radius1=0.72, depth=0.55, location=(0, 0, -1.02), vertices=96)
    pile = bpy.context.object
    lav = bpy.data.materials.new("Lava"); lav.use_nodes = True
    ln_ = lav.node_tree; lpb = ln_.nodes["Principled BSDF"]
    nz = node(ln_, "ShaderNodeTexNoise", Scale=9.0, Detail=10.0)
    ramp = ln_.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.02, 0.01, 0.008, 1)
    ramp.color_ramp.elements[1].position = 0.62; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    ln_.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    bb = node(ln_, "ShaderNodeBlackbody", Temperature=1500)
    lpb.inputs["Base Color"].default_value = (0.03, 0.02, 0.02, 1)
    ln_.links.new(bb.outputs["Color"], lpb.inputs["Emission Color"])
    es = node(ln_, "ShaderNodeMath"); es.operation = "MULTIPLY"; es.inputs[1].default_value = 5
    ln_.links.new(ramp.outputs["Color"], es.inputs[0]); ln_.links.new(es.outputs[0], lpb.inputs["Emission Strength"])
    pile.data.materials.append(lav)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=1.0, location=(0, 0, -0.35), vertices=24)
    stream = bpy.context.object
    stream.data.materials.append(C.emission("Stream", (1.0, 0.45, 0.12), 8)[0])
    # wooden caps
    for z in (-1.33, 1.33):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=0.08, location=(0, 0, z), vertices=96)
        C.add(bpy.context.object, C.principled("Wood", **{"Base Color": (0.12, 0.06, 0.03, 1), "Roughness": 0.45}), smooth=True)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=2.66, location=(0.88 * math.cos(a), 0.88 * math.sin(a), 0), vertices=24)
        C.add(bpy.context.object, C.principled("Wood2", **{"Base Color": (0.12, 0.06, 0.03, 1), "Roughness": 0.45}), smooth=True)
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -1.37))
    C.add(bpy.context.object, C.principled("Floor", **{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.25}))
    C.area((-2.5, -2.0, 2.2), (55, 0, -50), 500, 2.0, (0.75, 0.85, 1.0))
    C.area((2.6, 1.8, 1.6), (-65, 0, 130), 700, 1.2, (1.0, 0.75, 0.5))
    C.area((0, 3, 0.5), (-90, 0, 180), 300, 4, (0.5, 0.6, 1.0))
    C.area((-2.2, 1.8, 0.4), (-80, 0, -140), 900, 0.6, (1.0, 0.8, 0.6))     # rim lights draw the glass edges
    C.area((2.2, 1.8, 0.4), (-80, 0, 140), 900, 0.6, (0.6, 0.8, 1.0))
    cam, tgt = C.camera(50, 8, (-0.9, 0, 0), focus=False)
    cam.location = (-0.9, -8.6, 0.6)

elif SCENE == "lead":
    stars(strength=0.4)
    e = earth(1.0, clouds=True, atmosphere=True)
    e.rotation_euler = (math.radians(12), 0, math.radians(-80))
    # a coat of lead that has run down from the top: metallic grey where a stretched noise says so
    m = e.data.materials[0]; nt = m.node_tree; pb = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (5.0, 5.0, 0.6)   # long vertical drips
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = node(nt, "ShaderNodeTexNoise", Scale=2.2, Detail=3.0)
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    lvl = node(nt, "ShaderNodeMath"); lvl.operation = "ADD"
    nt.links.new(sep.outputs["Z"], lvl.inputs[0])
    drip = node(nt, "ShaderNodeMath"); drip.operation = "MULTIPLY"; drip.inputs[1].default_value = 1.1
    nt.links.new(nz.outputs["Fac"], drip.inputs[0]); nt.links.new(drip.outputs[0], lvl.inputs[1])
    mask = node(nt, "ShaderNodeMapRange"); mask.inputs["From Min"].default_value = 0.72; mask.inputs["From Max"].default_value = 0.76
    nt.links.new(lvl.outputs[0], mask.inputs["Value"])
    old_col = pb.inputs["Base Color"].links[0].from_socket
    old_rough = pb.inputs["Roughness"].links[0].from_socket
    cm = nt.nodes.new("ShaderNodeMix"); cm.data_type = "RGBA"
    nt.links.new(mask.outputs["Result"], cm.inputs["Factor"]); nt.links.new(old_col, cm.inputs["A"])
    cm.inputs["B"].default_value = (0.55, 0.57, 0.62, 1)
    nt.links.new(cm.outputs["Result"], pb.inputs["Base Color"])
    nt.links.new(mask.outputs["Result"], pb.inputs["Metallic"])
    rmix = nt.nodes.new("ShaderNodeMix"); rmix.data_type = "FLOAT"
    nt.links.new(mask.outputs["Result"], rmix.inputs["Factor"]); nt.links.new(old_rough, rmix.inputs["A"])
    rmix.inputs["B"].default_value = 0.12
    nt.links.new(rmix.outputs["Result"], pb.inputs["Roughness"])
    # hide clouds under the metal
    for ch in e.children:
        if ch.data.materials and ch.data.materials[0].name.startswith("Clouds"):
            ch.hide_render = True
    # the pour: a slightly wavy stream of liquid metal from above
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=3.0, location=(0.05, 0, 2.45), vertices=48)
    st = bpy.context.object
    d = st.modifiers.new("wave", "DISPLACE"); t = bpy.data.textures.new("wv", "CLOUDS"); t.noise_scale = 0.3; d.texture = t; d.strength = 0.03
    sm = st.modifiers.new("sub", "SUBSURF"); sm.levels = sm.render_levels = 2
    C.add(st, C.principled("LiquidLead", **{"Base Color": (0.6, 0.62, 0.66, 1), "Metallic": 1.0, "Roughness": 0.08}), smooth=True)
    # a small studio environment so the metal has something to reflect
    C.area((-3, -2, 3), (50, 0, -55), 600, 4, (1.0, 0.9, 0.8))
    C.area((3, 1.5, 2), (-55, 0, 120), 500, 3, (0.6, 0.75, 1.0))
    sun((65, 0, -40), 4.0)
    cam, tgt = C.camera(50, 8, (0, 0, 0.35), focus=False)
    cam.location = (0.4, -5.2, 0.9)

C.render(sc, OUT, "still", still_frame=1)
