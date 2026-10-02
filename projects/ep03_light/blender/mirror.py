# Michelson's rotating octagonal mirror: the beam leaves one face and must return to the next.
# Run: blender -b -P mirror.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "120"))
sc = C.setup(SAMPLES, FRAMES, bg=(0.003, 0.003, 0.005))
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.45

mirror = C.principled("Mirror", **{"Base Color": (0.95, 0.95, 0.96, 1), "Metallic": 1.0, "Roughness": 0.08})
steel = C.principled("Steel", **{"Base Color": (0.5, 0.51, 0.53, 1), "Metallic": 1.0, "Roughness": 0.3})
black = C.principled("BlackAl", **{"Base Color": (0.015, 0.015, 0.018, 1), "Metallic": 0.6, "Roughness": 0.4})

bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
C.add(bpy.context.object, C.principled("Bench", **{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.3}))

# the octagon itself, on a spindle
oct_ = bpy.data.objects.new("Octagon", None)
sc.collection.objects.link(oct_)
oct_.location = (0, 0, 0.20)
bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.05, vertices=8, location=(0, 0, 0))  # parented to the spindle, which is already at 0.20
body = bpy.context.object
bev = body.modifiers.new("b", "BEVEL"); bev.width = 0.0015; bev.segments = 2
C.add(body, mirror).parent = oct_
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.20, location=(0, 0, 0.10), vertices=32)
C.add(bpy.context.object, steel, smooth=True)
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.014, location=(0, 0, 0.007), vertices=64)
C.add(bpy.context.object, black, smooth=True)
C.key_path(oct_, [(1, (0, 0, 0)), (FRAMES, (0, 0, math.radians(300)))], "rotation_euler")

# incoming beam and the reflected leg heading out across the valley
C.beam((-1.7, -0.22, 0.20), (-0.02, -0.06, 0.20), (0.95, 0.96, 1.0), 6, radius=0.0016)
C.beam((0.02, -0.05, 0.20), (1.9, 0.55, 0.205), (0.95, 0.96, 1.0), 4, radius=0.0016)

# distant mirror mount and a foreground post for depth
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.0, 0.58, 0.22))
far = bpy.context.object; far.scale = (0.02, 0.16, 0.16); far.rotation_euler = (0, 0, math.radians(-16))
C.add(far, mirror)
bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.4, location=(-0.62, -0.75, 0.2), vertices=24)
C.add(bpy.context.object, steel, smooth=True)

# a bright panel above, so the mirror faces have something to catch
bpy.ops.mesh.primitive_plane_add(size=0.9, location=(-0.25, -0.35, 0.95), rotation=(math.radians(25), 0, 0))
C.add(bpy.context.object, C.emission("Panel", (1.0, 0.97, 0.92), 16)[0])
bpy.ops.mesh.primitive_plane_add(size=1.2, location=(-1.1, -0.5, 0.45), rotation=(0, math.radians(70), 0))
C.add(bpy.context.object, C.emission("Panel2", (0.85, 0.92, 1.0), 9)[0])
C.area((-0.6, -0.9, 0.9), (42, 0, -30), 110, 0.7, (1.0, 0.95, 0.9))
C.area((0.9, 0.8, 0.6), (-52, 0, 210), 55, 0.5, (0.55, 0.7, 1.0))
C.bokeh_leds(14, seed=4, x=(-1.4, 1.8), y=(1.3, 2.2), z=(0.05, 0.7), strength=10)

cam, tgt = C.camera(55, 3.0, (0.0, 0, 0.21))
C.key_path(cam, [(1, (-0.50, -1.15, 0.42)), (FRAMES, (-0.34, -1.02, 0.37))])

C.render(sc, OUT, MODE)
