"""Edit decision list for EP01. One entry per VO line (index = line in vo lines.json).

Shot spec: "name[@start][!r]"  — name is a file in footage/clips (no ext),
  or "nasa" (footage/nasa/earth_views_2021.mp4), "atom" (renders/atom_anim.mp4), "black".
  @start = in-point in seconds, !r = reversed.
Overlay: (kind, text) with kind in title | section | lower | big | small.
"""

SOURCES = {
    "nasa": "footage/nasa/earth_views_2021.mp4",
    "atom": "renders/atom_anim.mp4",
}

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
    1: (["open_watch_a", "open_watch_b"], None),
    2: (["atom", "lab_blue"], None),
    3: (["mtn_summit_station", "plane_takeoff", "stairs_a", "lab_face"], None),
    4: (["light_rays", "black"], ("title", TITLE)),
    5: (["nasa@95", "earth_limb_day"], None),
    6: (["earth_limb_night", "milky_way_a"], None),
    7: (["clouds_fly_a", "clouds_fly_b"], None),
    8: (["city_night_a"], None),
    9: (["mtn_snow_ridge", "mtn_summit_station", "mtn_peak_above_clouds"], ("lower", "Mount Washington, New Hampshire  ·  1,917 m")),
    10: (["boston_aerial", "boston_skyline"], ("lower", "Cambridge, Massachusetts  ·  sea level")),
    11: (["mtn_clouds", "clouds_fly_b"], ("big", "568  →  27 ?")),
    12: (["black"], ("big", "412")),
    13: (["mtn_peak_above_clouds@4"], None),
    14: (["milky_way_b", "earth_limb_night@8", "mtn_clouds@6"], None),
    15: (["open_face"], None),
    16: (["plane_taxi_window", "airport_night_a"], None),
    17: (["airport_night_b"], ("lower", "October 1971")),
    18: (["cabin_empty"], None),
    19: (["plane_sky", "clouds_fly_a@6", "plane_window_night"], None),
    20: (["dc_capitol_dusk"], ("lower", "U.S. Naval Observatory  ·  Washington, D.C.")),
    21: (["nasa@600", "plane_takeoff@20", "clouds_fly_b@8"], None),
    22: (["plane_landing_night"], None),
    23: (["plane_night_tarmac"], ("big", "EAST  −59 ns      WEST  +273 ns")),
    24: (["dc_capitol_night"], ("small", "predicted:  −40 ns  ·  +275 ns")),
    25: (["nasa@1330"], None),
    26: (["nasa@1080", "car_gps_night", "city_night_a@8"], None),
    27: (["plane_sky@2"], None),
    28: (["boulder_forest", "mtn_snow_ridge@2"], ("lower", "NIST  ·  Boulder, Colorado  ·  2010")),
    29: (["lab_blue@3", "lab_face@8"], None),
    30: (["lab_face@3"], None),
    31: (["stairs_a@3", "stairs_b"], ("big", "33 cm")),
    32: (["open_watch_a@8"], None),
    33: (["hands_old_a", "hands_old_b"], None),
    34: (["stairs_run_a", "stairs_run_b", "bed_wake_a", "bed_wake_b"], None),
    35: (["runner_sunrise", "runner_feet"], None),
    36: (["open_feet_b"], None),
    37: (["pencil_dark"], None),
    38: (["lab_face@6", "lab_blue@6"], ("lower", "JILA  ·  Boulder, Colorado  ·  2022")),
    39: (["atom"], None),
    40: (["atom!r", "light_rays@4", "lab_blue@9"], None),
    41: (["pencil_dark@3"], ("big", "≈ 1 mm")),
    42: (["light_rays@2"], None),
    43: (["atom!r"], None),
    44: (["milky_way_a@6", "nasa@1000", "milky_way_b@5"], ("big", "10⁻¹⁹")),
    45: (["atom"], None),
    46: (["open_watch_b@6"], None),
    47: (["milky_way_b@2"], None),
    48: (["city_night_b", "nasa@1250"], None),
    49: (["mtn_peak_above_clouds", "plane_sky", "stairs_a", "pencil_dark@1"], None),
    50: (["atom!r"], None),
    51: (["open_feet_a@6"], None),
    52: (["open_face@4", "black"], ("title", CHANNEL)),
}
