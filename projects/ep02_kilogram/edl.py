"""Edit decision list for EP02 — "The Kilogram Was Losing Weight".

Shot spec: "name[@start][!r]" — a clip in footage/clips, an entry in SOURCES, or "black".
Every source is used once (the build refuses to render repeats).
"""

SOURCES = {
    "cyl_wide": "renders/cylinder_wide.mp4",
    "cyl_close": "renders/cylinder_close.mp4",
    "sphere3d": "renders/sphere.mp4",
    # archive photographs (NIST, public domain, credited in the description)
    "nist4": "footage/archive/nist4_kibble.jpg",
    "si_sphere": "footage/archive/si_sphere.png",
    "two_kg": "footage/archive/two_kilograms.jpg",
}
# the three hero renders may return as a callback, but only at a different in-point
MULTI_USE = {"black", "cyl_wide", "cyl_close", "sphere3d"}

TICKS = ()
BOOMS = (0, 2, 12, 31, 32)     # the disagreement · the 50 µg · the fixed constant · the new definition

TITLE = "THE KILOGRAM WAS LOSING WEIGHT"
CHANNEL = "THE LAST DIGIT"

SECTIONS = {
    5: "I  ·  THE METAL",
    11: "II  ·  THE DRIFT",
    18: "III  ·  WEIGHING WITH ELECTRICITY",
    25: "IV  ·  COUNTING ATOMS",
    30: "V  ·  THE VOTE",
}

EDL = {
    0: (["molten", "cyl_close@0", "sparks_table", "gauge_scale"], None),
    1: (["cyl_wide@0", "museum_cases", "clock_wind"], ("big", "1.000 000 000 kg")),
    2: (["balance_classic"], None),
    3: (["fingerprint", "droplets_glass", "tunnel_water"], None),
    4: (["paris_aerial", "black"], ("title", TITLE)),
    5: (["archive_shelves", "paris_roofs", "stairs_marble"], ("lower", "Sèvres, France  ·  1889")),
    6: (["hand_metal", "liquid_metal", "metal_spheres"], ("small", "90 % platinum  ·  10 % iridium")),
    7: (["old_lock", "lock_latch", "museum_hall"], None),
    8: (["two_kg", "cleanroom_a"], None),
    9: (["archive_cards", "scale_antique"], ("small", "compared roughly once every 40 years")),
    10: (["gloves_lab", "gloves_dish"], None),
    11: (["cleanroom_b", "balance_lab"], ("lower", "Third periodic verification  ·  1988–1992")),
    12: (["balance_powder", "watchmaker"], ("big", "+50 µg")),
    13: (["sand_light", "sand_fine", "dust_beam"], None),
    14: (["laser_particles", "jeweller"], None),
    15: (["ripples", "glass_dome", "library"], None),
    16: (["circuit_macro", "gears_gold", "racks_dark"], None),
    17: (["light_spikes", "ink_blue"], None),
    18: (["nist4", "machine_shop"], ("lower", "Kibble balance  ·  Bryan Kibble, 1975")),
    19: (["coil_spool", "coil_wires", "filings"], None),
    20: (["lathe", "precision_part"], None),
    21: (["magnifier", "lab_blue", "wave_lines"], None),
    22: (["corridor", "tunnel", "glassware"], ("lower", "NIST-4  ·  Gaithersburg, Maryland")),
    23: (["lathe_b", "microscope"], ("big", "13 ppb")),
    24: (["pool", "newton_cradle"], None),
    25: (["sphere3d"], None),
    26: (["crystals", "cleanroom_worker", "crucible"], ("small", "99.9995 % silicon-28")),
    27: (["si_sphere", "lens_optics"], ("big", "≈ 50 nm")),
    28: (["lattice", "caliper", "solder_board"], None),
    29: (["gauge_dial", "plasma"], None),
    30: (["council_room", "suits"], ("lower", "26th CGPM  ·  Versailles, 16 November 2018")),
    31: (["ink_orange", "lab_flasks", "clock_tower"], ("big", "h = 6.626 070 15 × 10⁻³⁴ J s")),
    32: (["cyl_wide@2", "chip_hand"], None),
    33: (["cyl_close@6", "stairs_arch"], None),
    34: (["observatory", "sphere3d@2"], None),
    35: (["black"], ("title", CHANNEL)),
}
