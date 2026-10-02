"""Edit decision list for EP06 — "The Sun Already Tried to Switch Off the Internet".

Shot spec: "name[@start][!r]" — a clip in footage/clips, an entry in SOURCES, or "black".
Stock footage (Pexels) + NASA SDO/SOHO/KSC footage cut into separate shots; every shot is used once.
No black screens: titles and section cards sit on footage.
"""

SOURCES = {}
MULTI_USE = {"black"}
CARDS_ON_FOOTAGE = True
GAP = 0.28

TICKS = ()
FAST_LINES = (0, 1, 2, 3, 4)
BOOMS = (0, 3, 13, 21, 26, 28)  # the sky at 1 am · the Sun hits · the field shakes · Quebec · the 2012 cloud · the miss

CHANNEL = "THE LAST DIGIT"

SECTIONS = {
    6: "I  ·  TWO BEADS OF LIGHT",
    13: "II  ·  THE NIGHT THE SKY CAUGHT FIRE",
    20: "III  ·  WHAT A STORM DOES NOW",
    26: "IV  ·  THE MISS",
    31: "V  ·  THE WATCHERS",
    35: "VI  ·  THE LAST DIGIT",
}

EDL = {
    0: (["mtn_trails", "bonfire", "fire_people"], ("small", "Rocky Mountains  ·  2 September 1859")),
    1: (["aur_pink", "aur_redgreen"], None),
    2: (["sparks_grind", "poles_sil", "spark_weld", "paper_burn", "paper_burn2"], None),
    3: (["y_prom", "y_eruption", "a_red"], ("big", "1859")),
    4: (["x_limberupt", "earth_limb_sun"], None),
    5: (["earth_night_sun", "grid_city", "y_fulldisk"], ("title", "THE STORM THAT ALREADY HAPPENED")),
    6: (["quill_candle", "telescope_dusk", "y_reddisc"], None),
    7: (["sun_disc", "y_sunspots", "pencil_sketch"], None),
    8: (["m_goldflare", "y_goldflare", "s_purple"], ("small", "11:18 a.m.  ·  1 September 1859")),
    9: (["corridor_long", "door_green", "clock_black"], None),
    10: (["y_violet", "t_purple"], None),
    11: (["y_prom2", "soho_red", "particles_orange"], None),
    12: (["wind_streaks", "earth_rot", "clock_red"], ("big", "17.6 hours")),
    13: (["mag_model", "filings"], None),
    14: (["palms_stars", "aur_harbor", "palm_tall"], None),
    15: (["aur_harbor2", "reading_window", "newspaper_hands"], None),
    16: (["wires_dusk"], None),
    17: (["poles_sunset", "pylon_sun", "wires_fog", "plasma_globe"], None),
    18: (["morse_hands", "typewriter", "letter_read", "aur_curtain"], ("lower", "Boston – Portland  ·  2 hours on auroral current")),
    19: (["substation", "earth_airglow", "grid_dark"], None),
    20: (["x_redclose", "y_redbright"], None),
    21: (["snowcity", "cooling_towers", "blackout_bw", "blackout2"], ("lower", "Québec  ·  13 March 1989  ·  6 million without power")),
    22: (["sea_grey", "ship_bow", "sea_storm"], ("small", "4 August 1972")),
    23: (["f9pad", "launch_wide", "ascent", "burn"], ("big", "38 of 49")),
    24: (["tractor_top", "tractor_red", "car_screen", "tractor_field"], ("small", "May 2024")),
    25: (["y_gold_curtain", "a_disk"], None),
    26: (["y_redflare", "x_fulldisk"], ("small", "23 July 2012")),
    27: (["probe", "a_gold", "soho_blue"], None),
    28: (["earth_small", "stars_dark"], ("big", "≈ 1 week")),
    29: (["dark_street", "candle", "street_empty", "candle2"], ("big", "up to $2 trillion")),
    30: (["substation_aerial", "transformer", "steel_plant"], None),
    31: (["observatory", "radio_dish"], None),
    32: (["belts_sat", "x_teal_close", "y_teal"], None),
    33: (["orbit_view", "earth_clouds", "radio_heather"], ("big", "15–60 min")),
    34: (["payload", "airplane_wing", "switch_panel"], None),
    35: (["y_redlimb2", "twist"], None),
    36: (["aur_green", "aur_mtn"], None),
    37: (["aur_trees", "aur_harbor3"], None),
    38: (["y_goldloops", "a_gold2"], ("title", CHANNEL)),
}
