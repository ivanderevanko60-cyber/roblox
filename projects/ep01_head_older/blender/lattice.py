# "Stack of pancakes made of light": strontium atoms held in layers by a vertical laser lattice.
# Each layer pulses like a clock; higher layers tick slightly faster. Camera tilts bottom -> top.
# Run: blender -b -P lattice.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "120"))
sc = C.setup(SAMPLES, FRAMES)

LAYERS, GAP, R = 15, 0.006, 0.028
z0 = -GAP * (LAYERS - 1) / 2
for i in range(LAYERS):
    z = z0 + i * GAP
    bpy.ops.mesh.primitive_cylinder_add(radius=R * (1 - 0.35 * abs(i - LAYERS / 2) / LAYERS), depth=0.0022, location=(0, 0, z), vertices=48)
    disc = bpy.context.object
    h = i / (LAYERS - 1)
    col = (0.05 + 0.25 * h, 0.2 + 0.1 * h, 1.0 - 0.15 * h)   # cool blue at bottom -> lilac at top
    mat, gain = C.glow_volume(f"Layer{i}", col, 2500, radial_only=True)
    C.add(disc, mat)
    # ticking: base glow with a pulse whose rate rises with height (exaggerated for visibility)
    rate = 0.20 + 0.05 * h
    for f in range(1, FRAMES + 1, 2):
        pulse = 0.5 + 0.5 * math.sin(f * rate + i * 0.4)
        gain.default_value = 1200 + 3200 * pulse ** 3
        gain.keyframe_insert("default_value", frame=f)

# vertical red lattice beam + faint horizontal blue beams
C.beam((0, 0, -0.25), (0, 0, 0.25), (1.0, 0.05, 0.02), 6, radius=0.0006)
C.beam((-0.4, 0.0, -0.001), (0.4, 0.0, -0.001), (0.05, 0.25, 1.0), 0.8, radius=0.0003)

# glass cell walls (out of focus foreground/background)
glass = C.principled("Glass", **{"Base Color": (0.95, 0.97, 1.0, 1), "Roughness": 0.0, "IOR": 1.46, "Transmission Weight": 1.0})
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
cell = bpy.context.object
cell.scale = (0.09, 0.09, 0.12)
bpy.ops.object.transform_apply(scale=True)
m = cell.modifiers.new("s", "SOLIDIFY"); m.thickness = 0.004
m = cell.modifiers.new("b", "BEVEL"); m.width = 0.002; m.segments = 3
C.add(cell, glass)

steel = C.principled("Steel", **{"Base Color": (0.6, 0.6, 0.62, 1), "Metallic": 1.0, "Roughness": 0.25})
copper = C.principled("Copper", **{"Base Color": (0.95, 0.55, 0.35, 1), "Metallic": 1.0, "Roughness": 0.3})
for z in (0.09, -0.09):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.012, location=(0, 0, z), major_segments=96, minor_segments=24)
    C.add(bpy.context.object, copper, smooth=True)
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.02, location=(0, 0, -0.14), vertices=96)
C.add(bpy.context.object, steel, smooth=True)

C.bokeh_leds(24, seed=7, x=(-1.5, 1.5), y=(1.6, 2.6), z=(-0.5, 0.7), strength=12)
C.area((0.3, -0.5, 0.4), (50, 0, 30), 12, 0.6, (0.75, 0.85, 1.0))
C.area((-0.3, 0.6, 0.2), (-70, 0, 200), 10, 0.4, (1.0, 0.7, 0.5))

cam, tgt = C.camera(85, 2.8, (0, 0, z0))
cam.location = (-0.12, -0.42, -0.05)
C.key_path(tgt, [(1, (0, 0, z0 - 0.004)), (FRAMES, (0, 0, -z0 + 0.004))])
C.key_path(cam, [(1, (-0.22, -0.58, 0.10)), (FRAMES, (-0.12, -0.56, 0.20))])

C.render(sc, OUT, MODE)
