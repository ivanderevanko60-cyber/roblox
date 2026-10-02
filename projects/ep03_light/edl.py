"""Edit decision list for EP03 — "How Do We Know the Speed of Light?".

Shot spec: "name[@start][!r]" — a clip in footage/clips, an entry in SOURCES, or "black".
Every source is used once; the three hero renders may return at a different in-point.
"""

SOURCES = {
    "jupiter": "renders/jupiter_io.mp4",
    "fizeau": "renders/fizeau.mp4",
    "mirror": "renders/mirror.mp4",
    "kg_cylinder": "../ep02_kilogram/renders/cylinder_wide.mp4",   # callback to EP02
}
MULTI_USE = {"black", "jupiter", "fizeau", "mirror"}

TICKS = ()
FAST_LINES = (0, 1, 2, 3)   # the cold open cuts every ~1.5 s
BOOMS = (0, 8, 21, 27)      # the exact number · "the light is late" · Michelson's answer · the definition

TITLE = "HOW WE LEARNED THE SPEED OF LIGHT"
CHANNEL = "THE LAST DIGIT"

SECTIONS = {
    5: "I  ·  THE MOON THAT RAN LATE",
    12: "II  ·  A WHEEL WITH 720 TEETH",
    19: "III  ·  TWO MOUNTAINS",
    23: "IV  ·  THE LASER",
    27: "V  ·  THE DECISION",
}

EDL = {
    0: (["sun_close", "sun_leaves", "light_grid"], ("big", "299 792 458 m/s")),
    1: (["earth_sun", "sun_water", "tape_measure", "gauge_digital"], ("small", "Sun to Earth  ·  8 min 20 s")),
    2: (["forest_beams", "bulb", "scanlines"], None),
    3: (["jupiter@1", "fizeau@1", "la_hills", "mirror@1"], None),
    4: (["black"], ("title", TITLE)),
    5: (["lanterns", "hills_sunset", "lanterns_b"], None),
    6: (["old_map", "ship_mast", "compass_hand"], None),
    7: (["jupiter@0", "pocket_watch"], ("small", "Io  ·  one orbit every 42.5 hours")),
    8: (["star_glint", "typewriter"], ("lower", "Ole Rømer  ·  Paris, 1676")),
    9: (["earth_spin", "jupiter@2"], ("big", "≈ 22 minutes")),
    10: (["milky_dust", "desk_papers"], ("big", "≈ 227 000 km/s")),
    11: (["dusk_sky", "star_streaks", "sunbeams"], None),
    12: (["paris_sky", "paris_bw"], None),
    13: (["montmartre", "paris_roofs", "fizeau@0"], ("lower", "Hippolyte Fizeau  ·  Paris, 1849")),
    14: (["fizeau@2", "watch_gears"], None),
    15: (["fizeau@3", "candle", "torch"], ("big", "≈ 313 000 km/s")),
    16: (["paris_night", "paris_avenue"], None),
    17: (["mirror@0", "drops_color", "prism_hands"], ("lower", "Léon Foucault  ·  1862")),
    18: (["prism_face", "watch_open"], ("big", "298 000 km/s")),
    19: (["valley_road", "desert_plain", "green_hills"], ("lower", "Mount Wilson to Mount San Antonio  ·  1926")),
    20: (["mirror@2", "valley_alps", "hills_cloud"], ("small", "8 faces  ·  528 turns per second")),
    21: (["observatory", "domes"], ("big", "299 796 ± 1 km/s")),
    22: (["ruler_hand", "ruler_yellow"], None),
    23: (["instrument", "fiber_warm"], None),
    24: (["laser_show", "waves_blue"], ("big", "c = λ × f")),
    25: (["fiber_green", "map_hands", "city_street"], ("big", "299 792 456.2 ± 1.1 m/s")),
    26: (["waves_neon", "valley_green"], None),
    27: (["conference", "hills_storm"], ("big", "c = 299 792 458 m/s")),
    28: (["forest_path", "earth_net"], None),
    29: (["city_lights", "sunrise_clouds"], None),
    30: (["kg_cylinder@2", "ship_sea"], None),
    31: (["sunset_sea", "jupiter@3", "mirror@3"], None),
    32: (["black"], ("title", CHANNEL)),
}

