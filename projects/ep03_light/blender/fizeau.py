# Fizeau's toothed wheel: a beam of light chopped by a spinning brass wheel.
# Run: blender -b -P fizeau.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "120"))
sc = C.setup(SAMPLES, FRAMES, bg=(0.003, 0.003, 0.004))
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.6

brass = C.principled("Brass", **{"Base Color": (0.72, 0.52, 0.22, 1), "Metallic": 1.0, "Roughness": 0.28})
steel = C.principled("Steel", **{"Base Color": (0.55, 0.56, 0.58, 1), "Metallic": 1.0, "Roughness": 0.3})

# --- wheel: a brass disc with 72 teeth on the rim ------------------------------------------------
wheel = bpy.data.objects.new("Wheel", None)
sc.collection.objects.link(wheel)
wheel.location = (0, 0, 0.22)          # lift the wheel off the bench, onto its stand
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.22, location=(0, 0.045, 0.11), vertices=32)
C.add(bpy.context.object, steel, smooth=True)
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.012, location=(0, 0.045, 0.006), vertices=64)
C.add(bpy.context.object, steel, smooth=True)
bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.006, rotation=(math.radians(90), 0, 0), vertices=128)
C.add(bpy.context.object, brass, smooth=True).parent = wheel
bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.05, rotation=(math.radians(90), 0, 0), vertices=48)
C.add(bpy.context.object, steel, smooth=True).parent = wheel
TEETH = 72
for i in range(TEETH):
    a = i / TEETH * 2 * math.pi
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.185 * math.cos(a), 0, 0.185 * math.sin(a)),
                                    rotation=(0, -a, 0))
    t = bpy.context.object
    t.scale = (0.022, 0.006, 0.0062)
    C.add(t, brass).parent = wheel
C.key_path(wheel, [(1, (0, 0, 0)), (FRAMES, (0, math.radians(-220), 0))], "rotation_euler")

# --- the beam: comes from the left, passes the rim, continues into the dark -----------------------
C.beam((-1.6, 0, 0.405), (1.8, 0, 0.405), (1.0, 0.92, 0.72), 5, radius=0.0014)
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.09, location=(-0.55, 0, 0.405), rotation=(0, math.radians(90), 0), vertices=48)
C.add(bpy.context.object, steel, smooth=True)     # lamp housing the beam comes out of
bpy.ops.mesh.primitive_cylinder_add(radius=0.043, depth=0.004, location=(-0.505, 0, 0.405), rotation=(0, math.radians(90), 0), vertices=48)
C.add(bpy.context.object, C.emission("Lamp", (1.0, 0.9, 0.7), 22)[0], smooth=True)

# bench and a distant mirror mount
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, -0.02))
C.add(bpy.context.object, C.principled("Bench", **{"Base Color": (0.012, 0.012, 0.014, 1), "Roughness": 0.35}))
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.9, 0, 0.405))
mnt = bpy.context.object; mnt.scale = (0.02, 0.12, 0.12)
C.add(mnt, steel)

C.area((-0.5, -0.8, 0.7), (48, 0, -28), 90, 0.6, (1.0, 0.94, 0.86))
C.area((0.7, 0.7, 0.5), (-55, 0, 205), 45, 0.5, (0.6, 0.72, 1.0))
C.bokeh_leds(12, seed=9, x=(-1.0, 1.4), y=(1.2, 2.0), z=(0.05, 0.6), strength=10)

cam, tgt = C.camera(48, 3.6, (0.05, 0, 0.30))
C.key_path(cam, [(1, (-0.75, -1.95, 0.72)), (FRAMES, (-0.58, -1.75, 0.64))])

C.render(sc, OUT, MODE)
