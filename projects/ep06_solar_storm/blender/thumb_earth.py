# Thumbnail hero still for EP06: the Earth lit hard from the left (the Sun's side), a glowing aurora
# curtain around the north pole. Rendered on transparent film and composited with real SDO footage in PIL.
# Run: blender -b -P thumb_earth.py -- <out_prefix> still <samples>
import bpy, math, os, sys, mathutils
EP05 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ep05_time", "blender")
sys.path.append(EP05)
src = open(os.path.join(EP05, "thumb_clock.py"), encoding="utf8").read().split("# =====")[0]
exec(compile(src, "thumb_clock_helpers", "exec"))
HERE = EP05                       # textures live with EP05's Blender scenes

e = earth(1.0, clouds=True, atmosphere=True)
POLE = mathutils.Vector((0.30, -0.62, 0.72)).normalized()   # north pole tipped towards the camera, a little to the night side
e.rotation_mode = 'QUATERNION'
e.rotation_quaternion = POLE.to_track_quat('Z', 'Y') @ mathutils.Quaternion((0, 0, 1), math.radians(float(os.environ.get('SPIN', '0'))))
bpy.context.view_layer.update()
# the atmosphere shell glows by itself in the shared helper; keep it a thin rim so the night side stays dark
for n in bpy.data.materials['Atmo'].node_tree.nodes:
    if n.type == 'EMISSION':
        n.inputs['Strength'].default_value = 0.7
    if n.type == 'LAYER_WEIGHT':
        n.inputs['Blend'].default_value = 0.05
axis = (e.matrix_world.to_3x3() @ mathutils.Vector((0, 0, 1))).normalized()

def curtain(r, h, lift, strength):
    """Open cylinder around the pole; emission fades from green at the base to red at the top."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=r, depth=h, end_fill_type="NOTHING")
    c = bpy.context.object
    for p in c.data.polygons:
        p.use_smooth = True
    m = bpy.data.materials.new("Aurora"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.1, 1.0, 0.35, 1)
    cr.elements[1].position = 1.0; cr.elements[1].color = (0.9, 0.08, 0.35, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    fade = nt.nodes.new("ShaderNodeMath"); fade.operation = "POWER"; fade.inputs[1].default_value = 2.6
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(sep.outputs["Z"], inv.inputs[1]); nt.links.new(inv.outputs[0], fade.inputs[0])
    # vertical rays: noise stretched along the curtain
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 18; noise.inputs["Detail"].default_value = 6
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (6, 6, 0.3)
    nt.links.new(tc.outputs["Generated"], mp.inputs[0]); nt.links.new(mp.outputs[0], noise.inputs["Vector"])
    rays = nt.nodes.new("ShaderNodeMapRange"); rays.inputs["From Min"].default_value = 0.42; rays.inputs["From Max"].default_value = 0.68
    nt.links.new(noise.outputs["Fac"], rays.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    nt.links.new(fade.outputs[0], mul.inputs[0]); nt.links.new(rays.outputs["Result"], mul.inputs[1])
    st = nt.nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = strength
    nt.links.new(mul.outputs[0], st.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(ramp.outputs["Color"], em.inputs["Color"]); nt.links.new(st.outputs[0], em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(em.outputs[0], add.inputs[0]); nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    c.data.materials.append(m)
    c.visible_shadow = False
    c.rotation_mode = "QUATERNION"
    c.rotation_quaternion = axis.to_track_quat("Z", "Y")
    c.location = axis * (math.sqrt(max(0.0, 1.0 - r * r)) + lift + h / 2)
    return c

curtain(0.42, 0.20, 0.0, 3.2)
curtain(0.46, 0.34, 0.03, 1.4)
sun((0, -80, 0), 7.0)                     # hard light from the left: the Sun's side of the Earth
cam, tgt = C.camera(50, 8, (0, 0, 0), focus=False)
cam.location = (0, -7.2, 0.9)
sc.render.film_transparent = True
C.render(sc, OUT, "still", still_frame=1)
