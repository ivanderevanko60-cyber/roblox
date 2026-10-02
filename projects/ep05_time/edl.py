"""Edit decision list for EP05 — "Nobody Knows What Time It Is".

Shot spec: "name[@start][!r]" — a clip in footage/clips, an entry in SOURCES, or "black".
Stock footage only; every clip is used once. No black screens: titles and section cards sit on footage.
"""

SOURCES = {}
MULTI_USE = {"black"}
CARDS_ON_FOOTAGE = True
GAP = 0.28                  # tight breath between lines (the voice's own pauses are already trimmed)

TICKS = (0, 20)
FAST_LINES = (0, 1, 2, 3, 4)
BOOMS = (0, 3, 16, 25, 29)  # the extra second · nobody knows · the planet wobbles · the twist · the strange part

CHANNEL = "THE LAST DIGIT"

SECTIONS = {
    6: "I  ·  EVERY TOWN HAD ITS OWN NOON",
    13: "II  ·  THE ATOM THAT NEVER GETS TIRED",
    19: "III  ·  THE SECOND THAT BREAKS COMPUTERS",
    26: "IV  ·  FOUR HUNDRED CLOCKS VOTE",
    31: "V  ·  CLOCKS IN THE SKY",
    35: "VI  ·  THE LAST DIGIT",
}

EDL = {
    0: (["fireworks", "numbers_color", "second_red"], ("big", "23:59:60")),
    1: (["server_blue", "glitch", "departures", "code_scroll"], None),
    2: (["second_pink", "clock_close"], None),
    3: (["city_night", "phone_face", "alarm_clocks"], None),
    4: (["iss_horizon", "paris_haze", "smartwatch"], None),
    5: (["earth_big", "city_lights"], ("title", "NOBODY KNOWS WHAT TIME IT IS")),
    6: (["sky_dawn", "tree_shadow"], None),
    7: (["cobbles", "old_facade"], None),
    8: (["prague_clock", "clock_big", "big_ben"], None),
    9: (["steam_train", "grand_central", "steam_train_b"], ("lower", "Greenwich time becomes the law  ·  1880")),
    10: (["globe", "sunset"], None),
    11: (["earth_crescent"], None),
    12: (["waves_rocks", "glacier", "lava"], None),
    13: (["stars_hill", "dust_dark"], None),
    14: (["microscope", "lab_white"], None),
    15: (["notebook", "instrument_hand"], ("lower", "Louis Essen  ·  National Physical Laboratory, 1955")),
    16: (["lava_b", "waves_coast"], None),
    17: (["domes", "dome_aerial", "pendulum_hand"], None),
    18: (["numbers_3d", "tower_white"], ("big", "9 192 631 770")),
    19: (["sun_noon", "city_noon"], None),
    20: (["downtown", "window_shadow", "calendar_mark"], ("big", "23:59:60")),
    21: (["servers", "code_green"], ("small", "30 June 2012")),
    22: (["phone_boy", "glitch_lines", "phone_dial"], None),
    23: (["corridor_dark", "city_dense", "dusk_towers"], None),
    24: (["hall_empty", "rail_shadows", "sky_clouds"], ("lower", "27th CGPM  ·  leap seconds end by 2035")),
    25: (["earth_small", "star_trails"], None),
    26: (["clock_shop", "alarm_clock", "alarm_black"], None),
    27: (["map_board", "paris_roofs", "phone_world"], None),
    28: (["clock_face", "platform", "departures_b"], ("big", "UTC")),
    29: (["calendar_oct", "hourglass_red"], None),
    30: (["smartwatch_b", "watch_man", "car_night_nav"], None),
    31: (["satellite_b", "phone_map"], None),
    32: (["earth_horizon", "earth_night_rim", "shuttle"], ("big", "+38 µs / day")),
    33: (["car_screen", "traffic_night", "phone_map_b"], ("big", "≈ 10 km")),
    34: (["rocket_smoke", "radio_dish"], None),
    35: (["bokeh_blue", "hourglass_bokeh"], None),
    36: (["stairs", "stairs_feet"], None),
    37: (["station_crowd", "watch_dark", "clock_winding"], None),
    38: (["clouds_dark", "black"], ("title", CHANNEL)),
}
