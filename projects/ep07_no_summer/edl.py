"""Edit decision list for EP07 — "The Year Summer Never Came".

Shot spec: "name[@start][!r]" — a clip in footage/clips, an entry in SOURCES, or "black".
Stock footage only; every clip is used once. No black screens: titles and section cards sit on footage.
"""

SOURCES = {}
MULTI_USE = {"black"}
CARDS_ON_FOOTAGE = True
GAP = 0.28

TICKS = ()
FAST_LINES = (0, 1, 2, 3, 4)
BOOMS = (0, 5, 8, 11, 17, 36)  # snow in June · the volcano · biggest eruption · it went up · frost every month · one in six

CHANNEL = "THE LAST DIGIT"

SECTIONS = {
    6: "I  ·  THE LOUDEST SOUND",
    12: "II  ·  A VEIL AROUND THE EARTH",
    17: "III  ·  EIGHTEEN HUNDRED AND FROZE TO DEATH",
    23: "IV  ·  TWO MONSTERS",
    28: "V  ·  THE SKY IN THE PAINTINGS",
    31: "VI  ·  NOBODY KNEW",
    34: "VII  ·  THE LAST DIGIT",
}

EDL = {
    0: (["snow_leaves", "snow_blossom", "snow_field"], ("small", "New England  ·  June 1816")),
    1: (["frost_leaf", "frozen_grass", "snow_furrows"], None),
    2: (["storm_sky", "flood_fields", "mud_road", "dark_field"], None),
    3: (["lake_storm", "rain_window", "candle_write", "ink_pot", "lightning"], None),
    4: (["globe_hand", "earth_clouds"], None),
    5: (["eruption", "ash_column"], ("title", "THE YEAR SUMMER NEVER CAME")),
    6: (["island", "cone"], ("small", "Mount Tambora  ·  April 1815")),
    7: (["tall_ship", "sail_ship", "smoke_column"], ("big", "2,000+ km")),
    8: (["lava_fountain", "lava_flow"], None),
    9: (["grey_slope", "ash_field", "lava_ridge"], None),
    10: (["fissure"], None),
    11: (["plume"], None),
    12: (["crater_clouds", "above_clouds", "plane_window"], ("big", "~60 million tonnes")),
    13: (["high_clouds", "earth_limb", "earth_turn"], None),
    14: (["sun_haze", "sun_white"], None),
    15: (["misty_sun", "field_cold"], ("big", "−0.5 °C")),
    16: (["hands_soil"], None),
    17: (["frost_thistle", "corn", "snow_field_2"], None),
    18: (["farmhouse_snow"], ("lower", "“Eighteen hundred and froze to death”")),
    19: (["carriage", "carriage_road"], None),
    20: (["wheat_storm", "bread", "grain_hands", "pot_fire"], ("big", "wheat price ×2")),
    21: (["rice", "rain_grey"], None),
    22: (["horses_sil", "horse_mouth", "spokes", "old_bicycle"], ("small", "Karl Drais  ·  1817")),
    23: (["villa_lake", "window_green"], ("small", "Lake Geneva  ·  June 1816")),
    24: (["candles", "fireplace", "candles_rug"], None),
    25: (["period_write", "dark_corridor", "letter_write"], None),
    26: (["sun_grey", "clouds_bw"], None),
    27: (["storm_bw", "lightning_far"], None),
    28: (["sunset_dark"], None),
    29: (["orange_sky", "sunset_red"], None),
    30: (["gallery", "old_painting", "palette"], None),
    31: (["book_spines", "old_books"], None),
    32: (["old_pages", "grey_clouds"], ("small", "William Humphreys  ·  1920")),
    33: (["erupt_plume", "lava_smoke", "forest_smoke"], ("lower", "Mount Pinatubo  ·  1991  ·  about −0.5 °C for two years")),
    34: (["small_plume", "earth_turn_2"], None),
    35: (["dice"], None),
    36: (["dice_fall"], ("big", "1 in 6")),
    37: (["red_sun"], ("title", CHANNEL)),
}
