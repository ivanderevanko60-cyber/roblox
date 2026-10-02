# Two identical optical clocks on a table; the right one rises by 33 cm and then ticks faster.
# Run: blender -b -P two_clocks.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "150"))
sc = C.setup(SAMPLES, FRAMES)
C.optical_table(14.0)

steel = C.principled("Steel", **{"Base Color": (0.62, 0.62, 0.63, 1), "Metallic": 1.0, "Roughness": 0.22, "Anisotropic": 0.5})
black = C.principled("BlackAl", **{"Base Color": (0.02, 0.02, 0.022, 1), "Metallic": 0.7, "Roughness": 0.45})
glass = C.principled("Glass", **{"Base Color": (0.95, 0.97, 1.0, 1), "Roughness": 0.0, "IOR": 1.46, "Transmission Weight": 1.0})

RISE_END = 70
LIFT = 0.33


def clock(x, rises, rate_before, rate_after, name):
    parent = bpy.data.objects.new(name, None)
    sc.collection.objects.link(parent)
    base_h = 0.14
    # telescoping post: fixed outer sleeve + inner rod that slides up
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=base_h, location=(x, 0, base_h / 2), vertices=48)
    C.add(bpy.context.object, black, smooth=True)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.01, location=(x, 0, 0.005), vertices=64)
    C.add(bpy.context.object, steel, smooth=True)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0105, depth=LIFT + 0.02, location=(x, 0, base_h - (LIFT + 0.02) / 2), vertices=48)
    rod = C.add(bpy.context.object, steel, smooth=True)
    rod.parent = parent
    # head: mounting plate + glass cell + ion glow
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, base_h + 0.015))
    plate = bpy.context.object; plate.scale = (0.06, 0.06, 0.01)
    C.add(plate, black).parent = parent
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, base_h + 0.05))
    cell = bpy.context.object; cell.scale = (0.05, 0.05, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    m = cell.modifiers.new("s", "SOLIDIFY"); m.thickness = 0.003
    m = cell.modifiers.new("b", "BEVEL"); m.width = 0.0012; m.segments = 2
    C.add(cell, glass).parent = parent
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(x, 0, base_h + 0.05), segments=32, ring_count=16)
    ion = bpy.context.object
    mat, gain = C.glow_volume(name + "Ion", (0.15, 0.4, 1.0), 12000)
    C.add(ion, mat).parent = parent
    beam = C.beam((x - 0.2, 0, base_h + 0.05), (x + 0.2, 0, base_h + 0.05), (0.05, 0.25, 1.0), 1.2, radius=0.0004)
    beam.parent = parent
    if rises:
        C.key_path(parent, [(1, (0, 0, 0)), (12, (0, 0, 0)), (RISE_END, (0, 0, LIFT))])
    for f in range(1, FRAMES + 1):
        rate = rate_before if f < RISE_END else rate_after
        # phase accumulates so the pulse speeds up smoothly
        clock.phase[name] = clock.phase.get(name, 0.0) + rate
        pulse = max(0.0, math.sin(clock.phase[name])) ** 6
        gain.default_value = 3000 + 20000 * pulse
        gain.keyframe_insert("default_value", frame=f)


clock.phase = {}
clock(-0.16, False, 0.28, 0.28, "Low")
clock(0.16, True, 0.28, 0.40, "High")

C.bokeh_leds(30, seed=11, x=(-2.5, 2.5), y=(2.6, 3.6), z=(0.05, 1.3), strength=9)
wall = C.principled("Wall", **{"Base Color": (0.012, 0.013, 0.016, 1), "Roughness": 0.6})

C.area((0.5, -1.2, 1.3), (45, 0, 20), 160, 1.2, (0.75, 0.85, 1.0))
C.area((-0.4, 1.0, 0.9), (-60, 0, 200), 90, 1.0, (1.0, 0.72, 0.5))
C.area((0.8, 2.6, 0.9), (-60, 0, 170), 25, 0.8, (0.35, 0.45, 0.8))
C.area((1.2, 0.0, 0.4), (90, 0, 90), 12, 0.5, (0.8, 0.85, 1.0))
# out-of-focus foreground optics for depth
for fx, fz in ((-0.55, 0.12), (0.62, 0.2)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=fz * 2, location=(fx, -1.3, fz), vertices=32)
    C.add(bpy.context.object, steel, smooth=True)

THUMB = os.environ.get("THUMB")
cam, tgt = C.camera(95 if THUMB else 70, 2.4 if THUMB else 2.0, (0, 0, 0.30))
if THUMB:
    C.key_path(cam, [(1, (0.16, -3.1, 0.52)), (FRAMES, (0.16, -3.1, 0.52))])
    C.key_path(tgt, [(1, (0.0, 0, 0.44)), (FRAMES, (0.0, 0, 0.44))])
else:
    C.key_path(cam, [(1, (0.35, -3.2, 0.40)), (FRAMES, (0.0, -2.95, 0.46))])
if not THUMB:
    C.key_path(tgt, [(1, (0, 0, 0.22)), (RISE_END, (0.03, 0, 0.30)), (FRAMES, (0.02, 0, 0.30))])

C.render(sc, OUT, MODE, still_frame=110)
