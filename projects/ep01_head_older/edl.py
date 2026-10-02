"""Edit decision list for EP01. One entry per VO line (index = line in vo lines.json).

Shot spec: "name[@start][!r]"  — name is a file in footage/clips (no ext),
  or "nasa" (footage/nasa/earth_views_2021.mp4), "atom" (renders/atom_anim.mp4), "black".
  @start = in-point in seconds, !r = reversed.
Overlay: (kind, text) with kind in title | section | lower | big | small.
"""

SOURCES = {
    "nasa": "footage/nasa/earth_views_2021.mp4",   # long compilation: distinct in-points are distinct shots
    "atom": "renders/atom_anim.mp4",
    "atom_macro": "renders/atom_macro.mp4",
    "atom_orbit": "renders/atom_orbit.mp4",
    "lattice": "renders/lattice.mp4",
    "two_clocks": "renders/two_clocks.mp4",
    "globe_routes": "renders/globe_routes.mp4",
    # archive photographs of the real hardware (NIST/JILA, public domain, credited in the description)
    "nist_trap": "footage/archive/nist_al_clock.jpg",
    "jila_blue": "footage/archive/jila_sr_blue.jpg",
}

TICKS = (17, 30, 32, 42)      # lines carrying the clock motif
BOOMS = (12, 23, 32, 43, 52)  # lines with a reveal to hit
MULTI_USE = {"nasa", "black"}   # everything else may appear only once

TITLE = "YOUR HEAD IS OLDER THAN YOUR FEET"
CHANNEL = "THE LAST GOOD NUMBER"

# section name -> title card shown before the section's first line
SECTIONS = {
    5: "I  ·  THE MOUNTAIN",
    17: "II  ·  THE AIRPLANES",
    28: "III  ·  TWO STAIR STEPS",
    38: "IV  ·  ONE MILLIMETER",
}

EDL = {
    0: (["open_feet_a"], None),
    1: (["open_watch_a", "hourglass"], None),
    2: (["atom", "lab_blue"], None),
    3: (["climber_peak", "plane_takeoff", "stairs_a", "prism_cube"], None),
    4: (["light_rays", "black"], ("title", TITLE)),
    5: (["nasa@95", "aurora_a"], None),
    6: (["dust_bokeh", "embers"], None),
    7: (["clouds_fly_a", "clouds_fly_b", "aurora_b"], None),
    8: (["city_night_a"], None),
    9: (["mtn_snow_ridge", "hikers_snow", "mtn_summit_station"], ("lower", "Mount Washington, New Hampshire  ·  1,917 m")),
    10: (["boston_aerial", "boston_skyline"], ("lower", "Cambridge, Massachusetts  ·  sea level")),
    11: (["mtn_clouds", "forest_descent_a", "pocket_watch"], ("big", "568  →  27 ?")),
    12: (["black"], ("big", "412")),
    13: (["mtn_peak_above_clouds@4"], None),
    14: (["milky_way_a", "particle_waves", "star_trails_a", "light_trails"], None),
    15: (["open_face"], None),
    16: (["plane_taxi_window", "airport_night_a"], None),
    17: (["airport_night_b", "departures"], ("lower", "October 1971")),
    18: (["cabin_empty"], None),
    19: (["plane_sky", "globe_routes", "plane_window_night"], None),
    20: (["dc_capitol_dusk"], ("lower", "U.S. Naval Observatory  ·  Washington, D.C.")),
    21: (["nasa@600", "jet_engine", "clouds_valley", "star_trails_b"], None),
    22: (["plane_landing_night"], None),
    23: (["plane_night_tarmac"], ("big", "EAST  −59 ns      WEST  +273 ns")),
    24: (["dc_capitol_night"], ("small", "predicted:  −40 ns  ·  +275 ns")),
    25: (["nasa@1330", "plane_sea_sunset"], None),
    26: (["nasa@1080", "earth_limb_night", "car_gps_night", "phone_map"], None),
    27: (["plane_window_sunset"], None),
    28: (["boulder_forest", "snow_valley"], ("lower", "NIST  ·  Boulder, Colorado  ·  2010")),
    29: (["nist_trap", "lab_face", "clockwork_a"], None),
    30: (["two_clocks"], None),
    31: (["stairs_b", "spiral_stairs"], ("big", "33 cm")),
    32: (["pendulum_a"], None),
    33: (["hands_old_a", "hands_old_b"], None),
    34: (["stairs_run_a", "stairs_run_b", "bed_wake_a", "bed_wake_b"], None),
    35: (["runner_sunrise", "runner_feet", "walk_night_a"], None),
    36: (["open_feet_b"], None),
    37: (["ruler"], None),
    38: (["jila_blue", "microscope_b", "blue_bokeh"], ("lower", "JILA  ·  Boulder, Colorado  ·  2022")),
    39: (["atom_orbit"], None),
    40: (["atom_macro", "lattice", "pancakes"], None),
    41: (["sand_dark"], ("big", "≈ 1 mm")),
    42: (["metronome"], None),
    43: (["clockwork_b"], None),
    44: (["nebula_a", "nasa@1000", "nebula_b"], ("big", "10⁻¹⁹")),
    45: (["ink_blue", "prism_arc"], None),
    46: (["open_watch_b"], None),
    47: (["stars_trees"], None),
    48: (["city_night_b", "nasa@1250", "city_night_c"], None),
    49: (["sunrise_clouds_a", "earth_coast", "stairs_above", "sparkler"], None),
    50: (["sunrise_clouds_b"], None),
    51: (["legs_dark"], None),
    52: (["face_dark", "black"], ("title", CHANNEL)),
}
