"""Edit decision list for EP04 — "How Do We Know How Old the Earth Is?".

Shot spec: "name[@start][!r]" — a clip in footage/clips, an entry in SOURCES, or "black".
Stock footage only this time; every clip is used once.
"""

SOURCES = {}
MULTI_USE = {"black"}

TICKS = ()
FAST_LINES = (0, 1, 2, 3)   # the cold open cuts every ~2 s
BOOMS = (0, 13, 20, 27)     # the number · the clock that never changes · 4.55 billion · the end of leaded petrol

TITLE = "HOW OLD IS THE EARTH?"
CHANNEL = "THE LAST DIGIT"

SECTIONS = {
    5: "I  ·  TOO YOUNG",
    11: "II  ·  A CLOCK INSIDE THE ROCK",
    16: "III  ·  THE POISONED LABORATORY",
    22: "IV  ·  WHERE THE LEAD CAME FROM",
    28: "V  ·  THE NUMBER",
}

EDL = {
    0: (["earth_clouds", "lava_crust", "volcano_fire", "lava_flow", "nebula"], ("big", "4.54 billion years")),
    1: (["rock_hand", "exhaust_smoke", "hands_dirty", "dust_road", "smog_city"], None),
    2: (["clean_work", "lab_suit", "traffic_jam", "smog_towers"], None),
    3: (["city_sunrise"], None),
    4: (["black"], ("title", TITLE)),
    5: (["candle_book", "book_pages", "candle_desk"], None),
    6: (["steam_vents", "molten_flow", "volcano_night"], ("lower", "William Thomson, later Lord Kelvin  ·  1862")),
    7: (["hourglass_hands", "book_hands"], ("big", "20 – 40 million years")),
    8: (["canyon_grand", "rock_layers", "river_gorge", "canyon_mesa"], None),
    9: (["waves_soft", "salt_pour", "delta_sunset", "salt_macro"], ("big", "≈ 90 million years")),
    10: (["hourglass", "river_rock"], None),
    11: (["uv_tube", "glass_colour", "microscope_b", "particles_dark"], ("lower", "Henri Becquerel  ·  1896")),
    12: (["steam_desert", "crystal_single", "gems_blue"], None),
    13: (["crystal_pile", "lead_melt", "molten_pour"], ("big", "U-238 half-life  ·  4.47 billion years")),
    14: (["pipette", "glass_cyl", "microscope"], None),
    15: (["cliff_white", "rock_red", "outback_river", "desert_hill"], ("lower", "Bertram Boltwood  ·  1907")),
    16: (["waves_dark", "ground_drill"], None),
    17: (["milky_way", "lab_vintage"], ("lower", "Clair Patterson  ·  Chicago, 1948")),
    18: (["smoke_white", "lab_bottles", "glass_wash", "hands_sample"], None),
    19: (["clean_gown", "acid_wash", "lab_machine"], None),
    20: (["crater_wide", "crater_aerial", "earth_turn"], ("big", "4.55 ± 0.07 billion years")),
    21: (["sky_clouds", "delta_green"], ("big", "4.54 billion years")),
    22: (["street_fog", "street_night"], None),
    23: (["ice_sea", "ice_drill", "snow", "ice_shelf"], ("small", "Greenland ice  ·  lead through time")),
    24: (["car_vintage", "car_red", "exhaust_car"], ("lower", "Tetraethyl lead  ·  1923")),
    25: (["typewriter_hands", "print_press", "papers_desk", "building"], None),
    26: (["traffic_rain", "blood_tube", "sky_cumulus", "kids_slide"], ("small", "US blood lead  ·  down by more than three quarters")),
    27: (["highway_sun", "pump_night"], ("big", "2021")),
    28: (["nebula_b", "outback_red"], ("big", "4.567 billion years")),
    29: (["rock_macro", "stars_trees"], ("big", "4.54 ± 0.05 billion years")),
    30: (["highway_aerial", "city_skyline"], None),
    31: (["black"], ("title", CHANNEL)),
}
