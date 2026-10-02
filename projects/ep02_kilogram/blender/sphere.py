# The Avogadro sphere: a mirror-polished silicon-28 ball, studio product lighting.
# Run: blender -b -P sphere.py -- <out_prefix> [still|anim] [samples]
import bpy, math, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import common as C

OUT, MODE, SAMPLES = C.args()
FRAMES = int(os.environ.get("FRAMES", "120"))
sc = C.setup(SAMPLES, FRAMES, bg=(0.004, 0.005, 0.007))

silicon = C.principled("Si28", **{"Base Color": (0.55, 0.57, 0.60, 1), "Metallic": 1.0, "Roughness": 0.035})
deck = C.principled("Deck", **{"Base Color": (0.01, 0.011, 0.013, 1), "Roughness": 0.12, "Metallic": 0.3})

bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
C.add(bpy.context.object, deck)

R = 0.0468                                   # 93.6 mm across
bpy.ops.mesh.primitive_uv_sphere_add(radius=R, location=(0, 0, R), segments=256, ring_count=128)
ball = C.add(bpy.context.object, silicon, smooth=True)

# a low cradle ring so it doesn't look like it floats
bpy.ops.mesh.primitive_torus_add(major_radius=R * 0.62, minor_radius=0.004, location=(0, 0, 0.004))
C.add(bpy.context.object, C.principled("Cradle", **{"Base Color": (0.02, 0.02, 0.022, 1), "Metallic": 0.8, "Roughness": 0.35}), smooth=True)


def softbox(loc, rot, energy, w, h, color=(1, 1, 1)):
    """Rectangular light that also shows up as a highlight in the mirror surface."""
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=[math.radians(r) for r in rot])
    L = bpy.context.object
    L.data.shape = "RECTANGLE"
    L.data.size, L.data.size_y = w, h
    L.data.energy, L.data.color = energy, color
    return L


softbox((-0.34, -0.30, 0.40), (52, 0, -42), 160, 0.55, 0.28)          # key, long highlight
softbox((0.42, 0.20, 0.34), (62, 0, 118), 90, 0.45, 0.22, (0.6, 0.72, 1.0))   # cool rim
softbox((0.10, -0.55, 0.06), (88, 0, 8), 25, 0.9, 0.10, (1.0, 0.85, 0.65))    # warm slash near the floor
C.bokeh_leds(14, seed=5, x=(-1.2, 1.2), y=(0.9, 1.6), z=(0.02, 0.5), strength=8)

cam, tgt = C.camera(85, 3.2, (0, 0, R))
C.key_path(cam, [(1, (-0.20, -0.42, 0.10)), (FRAMES, (-0.12, -0.44, 0.13))])
C.key_path(ball, [(1, (0, 0, 0)), (FRAMES, (0, 0, math.radians(18)))], "rotation_euler")

C.render(sc, OUT, MODE)
