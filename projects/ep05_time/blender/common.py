"""Shared helpers for EP01 Blender scenes (Cycles, CPU)."""
import bpy, math, os, sys, random


def args():
    a = sys.argv[sys.argv.index("--") + 1:]
    return a[0], (a[1] if len(a) > 1 else "still"), int(a[2]) if len(a) > 2 else 32


def setup(samples, frames, bg=(0.002, 0.003, 0.005)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.max_bounces = 8
    sc.cycles.volume_bounces = 1
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = 30
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.frame_start, sc.frame_end = 1, frames
    if os.environ.get("PREVIEW"):
        sc.render.resolution_percentage = 40
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*bg, 1)
    return sc


def principled(name, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    for k, v in kw.items():
        p.inputs[k].default_value = v
    return m


def emission(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree
    n.nodes.remove(n.nodes["Principled BSDF"])
    e = n.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = strength
    n.links.new(e.outputs[0], n.nodes["Material Output"].inputs["Surface"])
    return m, e


def glow_volume(name, color, gain, radial_only=False):
    """Soft volumetric glow with falloff from the object's centre. Returns (material, gain socket)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree
    n.nodes.remove(n.nodes["Principled BSDF"])
    vol = n.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 0.0
    vol.inputs["Emission Color"].default_value = (*color, 1)
    tc = n.nodes.new("ShaderNodeTexCoord")
    c = n.nodes.new("ShaderNodeVectorMath"); c.operation = "SUBTRACT"
    c.inputs[1].default_value = (0.5, 0.5, 0.5)
    n.links.new(tc.outputs["Generated"], c.inputs[0])
    s = n.nodes.new("ShaderNodeVectorMath"); s.operation = "MULTIPLY"
    s.inputs[1].default_value = (2.0, 2.0, 0.0 if radial_only else 2.0)
    n.links.new(c.outputs[0], s.inputs[0])
    g = n.nodes.new("ShaderNodeTexGradient"); g.gradient_type = "SPHERICAL"
    n.links.new(s.outputs[0], g.inputs["Vector"])
    pw = n.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 3.0
    n.links.new(g.outputs["Fac"], pw.inputs[0])
    nz = n.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 5
    n.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mul = n.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    n.links.new(pw.outputs[0], mul.inputs[0]); n.links.new(nz.outputs["Fac"], mul.inputs[1])
    gn = n.nodes.new("ShaderNodeMath"); gn.operation = "MULTIPLY"; gn.inputs[1].default_value = gain
    n.links.new(mul.outputs[0], gn.inputs[0])
    n.links.new(gn.outputs[0], vol.inputs["Emission Strength"])
    n.links.new(vol.outputs[0], n.nodes["Material Output"].inputs["Volume"])
    tr = n.nodes.new("ShaderNodeBsdfTransparent")
    n.links.new(tr.outputs[0], n.nodes["Material Output"].inputs["Surface"])
    return m, gn.inputs[1]


def add(obj, mat, smooth=False):
    obj.data.materials.append(mat)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def beam(p0, p1, color, strength, radius=0.0005):
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


def area(loc, rot, energy, size, color):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=[math.radians(r) for r in rot])
    L = bpy.context.object
    L.data.energy, L.data.size, L.data.color = energy, size, color
    return L


def camera(lens, fstop, target_loc, focus=True):
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.lens = lens
    cam.data.sensor_width = 36
    tgt = bpy.data.objects.new("Target", None)
    bpy.context.scene.collection.objects.link(tgt)
    tgt.location = target_loc
    if focus:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_object = tgt
    tr = cam.constraints.new("TRACK_TO")
    tr.target = tgt
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam, tgt


def key_path(obj, points, attr="location"):
    for f, v in points:
        setattr(obj, attr, v)
        obj.keyframe_insert(attr, frame=f)


def bokeh_leds(n=20, seed=3, x=(-1.2, 1.2), y=(0.8, 1.5), z=(0.05, 0.7), strength=40):
    random.seed(seed)
    for _ in range(n):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.004, location=(random.uniform(*x), random.uniform(*y), random.uniform(*z)), segments=8, ring_count=6)
        col = random.choice([(1, 0.25, 0.05), (0.1, 1, 0.2), (0.2, 0.5, 1), (1, 0.8, 0.4)])
        add(bpy.context.object, emission("LED", col, strength)[0])


def render(sc, out, mode, still_frame=None):
    sc.render.image_settings.file_format = "PNG"
    if mode == "still":
        sc.frame_set(still_frame or (sc.frame_end // 2))
        sc.render.filepath = out + ".png"
        bpy.ops.render.render(write_still=True)
    else:
        sc.render.filepath = out + "_"
        bpy.ops.render.render(animation=True)


def optical_table(size=3.0):
    """Dark anodised steel breadboard with a 25 mm threaded-hole grid."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    table = bpy.context.object
    m = principled("Table", **{"Base Color": (0.035, 0.037, 0.04, 1), "Metallic": 0.9, "Roughness": 0.38})
    nt = m.node_tree
    tp = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (40, 40, 40)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    fr = nt.nodes.new("ShaderNodeVectorMath"); fr.operation = "FRACTION"
    nt.links.new(mp.outputs["Vector"], fr.inputs[0])
    sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (0.5, 0.5, 0.0)
    nt.links.new(fr.outputs[0], sub.inputs[0])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(sub.outputs[0], sep.inputs[0])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], cmb.inputs["X"]); nt.links.new(sep.outputs["Y"], cmb.inputs["Y"])
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    nt.links.new(cmb.outputs[0], ln.inputs[0])
    hole = nt.nodes.new("ShaderNodeMapRange")
    hole.inputs["From Min"].default_value = 0.13
    hole.inputs["From Max"].default_value = 0.16
    nt.links.new(ln.outputs["Value"], hole.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (0, 0, 0, 1)
    mix.inputs["B"].default_value = (0.035, 0.037, 0.04, 1)
    nt.links.new(hole.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], tp.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6
    nt.links.new(hole.outputs["Result"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], tp.inputs["Normal"])
    table.data.materials.append(m)
    return table
