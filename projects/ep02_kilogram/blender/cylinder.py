# Le Grand K: a polished Pt-Ir cylinder under nested glass bell jars, museum lighting.
# Run: blender -b -P cylinder.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "120"))
sc = C.setup(SAMPLES, FRAMES, bg=(0.004, 0.004, 0.006))
sc.cycles.transmission_bounces = 16
sc.cycles.max_bounces = 16

plinth = C.principled("Plinth", **{"Base Color": (0.006, 0.006, 0.008, 1), "Roughness": 0.22, "Metallic": 0.2})
pt_ir = C.principled("PtIr", **{"Base Color": (0.78, 0.77, 0.75, 1), "Metallic": 1.0, "Roughness": 0.07})
glass = C.principled("Glass", **{"Base Color": (0.97, 0.98, 1.0, 1), "Roughness": 0.01, "IOR": 1.52,
                                 "Transmission Weight": 1.0})

# polished dark stone plinth
bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.06, location=(0, 0, -0.03), vertices=128)
C.add(bpy.context.object, plinth, smooth=True)
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -0.06))
C.add(bpy.context.object, C.principled("Floor", **{"Base Color": (0.0015, 0.0015, 0.002, 1), "Roughness": 0.28}))

# the prototype: 39 x 39 mm cylinder with a slightly rounded edge
bpy.ops.mesh.primitive_cylinder_add(radius=0.0195, depth=0.039, location=(0, 0, 0.0195), vertices=256)
cyl = bpy.context.object
bev = cyl.modifiers.new("b", "BEVEL"); bev.width = 0.0012; bev.segments = 6
C.add(cyl, pt_ir, smooth=True)
for p in cyl.data.polygons:      # keep the flat faces flat, round only the barrel
    p.use_smooth = abs(p.normal.z) < 0.5

# three nested bell jars
for i, (r, hgt) in enumerate(((0.050, 0.115), (0.076, 0.155), (0.104, 0.200))):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=hgt, location=(0, 0, hgt / 2 - 0.001), vertices=160)
    jar = bpy.context.object
    bev = jar.modifiers.new("b", "BEVEL")      # heavy bevel turns the top into a dome shoulder
    bev.width = r * 0.22; bev.segments = 10; bev.limit_method = "ANGLE"
    sol = jar.modifiers.new("s", "SOLIDIFY"); sol.thickness = 0.0022
    C.add(jar, glass, smooth=True)

bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 1.1, 0.8), rotation=(math.radians(90), 0, 0))
C.add(bpy.context.object, C.principled("Backdrop", **{"Base Color": (0.02, 0.022, 0.028, 1), "Roughness": 0.9}))

# --- lighting: one big soft key, a cold rim, a warm floor bounce ---------------------------------
C.area((-0.50, -0.40, 0.95), (28, 0, -38), 150, 0.5, (1.0, 0.96, 0.92))
C.area((0.80, 0.60, 0.52), (-58, 0, 205), 70, 0.5, (0.55, 0.68, 1.0))
C.area((0.0, -1.0, 0.30), (70, 0, 0), 18, 0.8, (1.0, 0.80, 0.58))
# small light dedicated to the prototype itself, so the metal reads bright inside the glass
C.area((-0.10, -0.22, 0.30), (38, 0, -25), 12, 0.10, (1.0, 0.97, 0.93))

CLOSE = os.environ.get("CAM") == "close"
cam, tgt = C.camera(85 if CLOSE else 50, 2.8 if CLOSE else 4.0, (0, 0, 0.03 if CLOSE else 0.085))
if CLOSE:
    C.key_path(cam, [(1, (-0.16, -0.40, 0.085)), (FRAMES, (-0.11, -0.33, 0.068))])
    C.key_path(tgt, [(1, (0, 0, 0.026)), (FRAMES, (0, 0, 0.022))])
else:
    C.key_path(cam, [(1, (-0.34, -0.80, 0.26)), (FRAMES, (-0.27, -0.66, 0.22))])
    C.key_path(tgt, [(1, (0, 0, 0.095)), (FRAMES, (0, 0, 0.075))])

C.render(sc, OUT, MODE)
