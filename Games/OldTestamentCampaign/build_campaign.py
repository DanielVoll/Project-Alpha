"""
Chronicles of Israel – Campaign Builder  (v2)
Generates all 12 .aoe2scenario files for the Old Testament campaign.

Changes v2:
  - ScenarioVariant.ROR set on every scenario (uses Pompeii/RoR civ list)
  - Proper RoR civilization IDs (Egyptian=1, Hittite=6, Phoenician=7, etc.)
  - Objective panel with checkboxes via header + sub-objective triggers
  - Timer(5) guard on every lose trigger to prevent instant-death on load
  - Per-scenario terrain decoration (trees, rocks, vegetation)

Run with:  py build_campaign.py
"""

import os, sys
os.environ["PYTHONIOENCODING"] = "utf-8"
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.scenario_variant import ScenarioVariant
from common import *


def new_scenario(map_size=MAP_MEDIUM):
    s = AoE2DEScenario.from_default()
    s.variant = ScenarioVariant.ROR
    s.map_manager.map_size = map_size
    return s


def save(s, filename):
    path = os.path.join(SCENARIO_OUT, filename)
    s.write_to_file(path)
    print(f"  Saved: {path}")


def setup_player(pm, pid, civ, name, food=400, wood=400, gold=200, stone=200,
                 human=False):
    p = pm.players[pid]
    p.civilization = civ
    p.tribe_name = name
    p.food = food
    p.wood = wood
    p.gold = gold
    p.stone = stone
    if human:
        p.human = 1


def set_diplomacy(pm, pid_a, pid_b, stance_ab, stance_ba):
    pm.players[pid_a].set_player_diplomacy(pid_b, stance_ab)
    pm.players[pid_b].set_player_diplomacy(pid_a, stance_ba)


def add_lose_trigger(tm, message):
    """Lose trigger with a 5-second timer guard to prevent instant-death on load."""
    t = tm.add_trigger("Defeat – Hero Slain")
    t.enabled = True
    t.new_condition.timer(timer=5)
    t.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t.new_effect.display_instructions(
        display_time=10, message=message, instruction_panel_position=0,
    )
    return t


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 1 – LET MY PEOPLE GO  (The Exodus)
# ═══════════════════════════════════════════════════════════════════════════════
def build_s01():
    print("Building S01: Let My People Go…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    # ── Terrain ─────────────────────────────────────────────────────────────
    fill_terrain(mm, T_DESERT)
    draw_river(mm, T_WATER_MED, 55, 0, 55, 119, width=8)
    fill_terrain(mm, T_GRASS, 47, 0, 63, 119)
    fill_terrain(mm, T_GRASS_DRY, 80, 0, 119, 70)
    fill_terrain(mm, T_ROAD, 5, 40, 45, 80)
    fill_terrain(mm, T_DESERT_CRACK, 90, 80, 119, 119)

    # Decoration
    scatter(um,  47,  0,  63, 119, TREE_PALM,                   30, seed=1)   # Nile palms
    scatter(um,  64, 10, 119,  80, [TREE_ACACIA, TREE_DEAD],    25, seed=2)   # desert acacias
    scatter(um,  70, 85, 119, 119, [CACTUS, ROCK_SM],           20, seed=3)   # deep desert
    scatter(um,   0,  0,  45, 119, [ROCK_SM, ROCK_MED],         15, seed=4)   # western rocks
    scatter(um,  47, 85,  70, 119, [BUSH_A, PLANT_SHRUB],       12, seed=5)   # southern banks

    # ── Players ─────────────────────────────────────────────────────────────
    setup_player(pm, P1, CIV_ISRAEL, "Israel",
                 food=300, wood=200, gold=100, stone=0, human=True)
    setup_player(pm, P2, CIV_EGYPT, "Egypt",
                 food=800, wood=600, gold=500, stone=400)
    setup_player(pm, P3, CIV_EGYPT, "Pharaoh's Guard",
                 food=600, wood=400, gold=300, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY,  DIPL_ALLY)

    # ── Units ───────────────────────────────────────────────────────────────
    moses = um.add_unit(P1, U_KING,     x=65, y=60)
    um.add_unit(P1, U_VILLAGER,  x=66, y=58)
    um.add_unit(P1, U_VILLAGER,  x=67, y=60)
    um.add_unit(P1, U_VILLAGER,  x=65, y=62)
    um.add_unit(P1, U_VILLAGER,  x=68, y=59)
    um.add_unit(P1, U_MILITIA,   x=64, y=57)
    um.add_unit(P1, U_MILITIA,   x=64, y=63)
    um.add_unit(P1, U_ARCHER,    x=70, y=58)
    um.add_unit(P1, U_ARCHER,    x=70, y=62)
    um.add_unit(P1, B_BARRACKS,  x=72, y=60)

    for x in range(15, 45, 6):
        um.add_unit(P2, U_WAR_CHARIOT, x=x, y=45)
        um.add_unit(P2, U_WAR_CHARIOT, x=x, y=75)
    um.add_unit(P2, B_TOWN_CENTER, x=20, y=60)
    um.add_unit(P2, B_CASTLE,      x=10, y=50)
    um.add_unit(P2, B_WATCH_TOWER, x=35, y=45)
    um.add_unit(P2, B_WATCH_TOWER, x=35, y=75)

    escape_tc = um.add_unit(P1, B_TOWN_CENTER, x=110, y=60)

    # ── Triggers ────────────────────────────────────────────────────────────
    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>Let My People Go</b>\n\n"
            "Egypt, 1446 BC. For four hundred years the children of Israel "
            "have laboured under Pharaoh's whip. The Lord has spoken to Moses "
            "from the burning bush: lead His people out of bondage.\n\n"
            "The plagues have broken Egypt's pride. Pharaoh has relented — "
            "but his heart will harden. Lead your people east across the Nile "
            "and into the Sinai before his chariots give chase."
        ),
    )

    sub_ids = setup_objectives(tm, "Let My People Go", [
        ("Lead Moses east to the encampment",
         "Move Moses (the King unit) to the camp on the eastern edge of the map."),
        ("Protect Moses",
         "Moses must survive — if he falls, the Exodus fails."),
    ])

    t_pursue = tm.add_trigger("Pharaoh Pursues")
    t_pursue.enabled = True
    t_pursue.new_condition.objects_in_area(
        quantity=1, source_player=P1, object_list=U_KING,
        area_x1=85, area_y1=40, area_x2=119, area_y2=80,
    )
    t_pursue.new_effect.display_instructions(
        display_time=13, instruction_panel_position=0,
        message=(
            "Pharaoh's heart has hardened! His chariots pour out in pursuit. "
            "Move quickly — reach the encampment before they surround you!"
        ),
    )
    for cx, cy in [(60, 50), (60, 60), (60, 70)]:
        t_pursue.new_effect.create_object(
            object_list_unit_id=U_WAR_CHARIOT, source_player=P3,
            location_x=cx, location_y=cy,
        )
    t_pursue.new_effect.deactivate_trigger(trigger_id=t_pursue.trigger_id)

    t_win = tm.add_trigger("Victory – Reached Sinai")
    t_win.enabled = True
    t_win.new_condition.objects_in_area(
        quantity=1, source_player=P1, object_list=U_KING,
        area_x1=100, area_y1=50, area_x2=119, area_y2=70,
    )
    t_win.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="Moses leads the children of Israel out of Egypt. The first step of a long journey has begun.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Moses has fallen. Without their leader, the Israelites are enslaved again.")

    s.message_manager.instructions = "Lead Moses (King unit) east to the encampment. Protect him at all costs."
    s.message_manager.victory = "Israel is free! The Exodus from Egypt begins."
    s.message_manager.loss = "Moses has been slain. The Exodus has failed."
    save(s, "ot_01_exodus.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 2 – THE WALLS OF JERICHO
# ═══════════════════════════════════════════════════════════════════════════════
def build_s02():
    print("Building S02: The Walls of Jericho…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_GRASS, 40, 30, 90, 90)
    draw_river(mm, T_SHALLOW, 0, 60, 35, 60, width=4)
    fill_terrain(mm, T_DESERT, 0, 0, 30, 119)
    fill_terrain(mm, T_ROCK, 85, 0, 119, 50)
    set_elevation_area(mm, 2, 85, 0, 119, 60)
    fill_terrain(mm, T_ROAD, 52, 48, 72, 68)

    # Decoration
    scatter(um, 35, 25, 85, 90, [TREE_OLIVE, PLANT_SHRUB],  30, seed=10)  # Canaan valley
    scatter(um, 85,  0, 119, 60, [TREE_CYPRESS, ROCK_SM],   20, seed=11)  # eastern hills
    scatter(um,  0,  0,  35, 119, [ROCK_MED, ROCK_SM],      15, seed=12)  # desert rocks
    scatter(um, 47, 45,  53, 70, [ROCK_LIME],                8, seed=13)  # Jericho limestone

    setup_player(pm, P1, CIV_ISRAEL,  "Israel",
                 food=500, wood=400, gold=200, stone=100, human=True)
    setup_player(pm, P2, CIV_CANAAN,  "Jericho",
                 food=700, wood=500, gold=400, stone=600)
    setup_player(pm, P3, CIV_CANAAN,  "Canaan",
                 food=400, wood=300, gold=200, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY,  DIPL_ALLY)

    joshua = um.add_unit(P1, U_KING,        x=20, y=60)
    um.add_unit(P1, B_TOWN_CENTER,           x=15, y=58)
    um.add_unit(P1, B_BARRACKS,              x=12, y=65)
    um.add_unit(P1, U_PRIEST,                x=16, y=60)
    for i in range(8):
        um.add_unit(P1, U_MILITIA,  x=18+i, y=62)
        um.add_unit(P1, U_ARCHER,   x=18+i, y=56)
    um.add_unit(P1, U_SPEARMAN, x=22, y=60)
    um.add_unit(P1, U_SPEARMAN, x=24, y=60)

    jericho_tc = um.add_unit(P2, B_TOWN_CENTER, x=62, y=58)
    um.add_unit(P2, B_CASTLE,       x=55, y=50)
    um.add_unit(P2, B_WATCH_TOWER,  x=50, y=50)
    um.add_unit(P2, B_WATCH_TOWER,  x=75, y=50)
    um.add_unit(P2, B_WATCH_TOWER,  x=50, y=70)
    um.add_unit(P2, B_WATCH_TOWER,  x=75, y=70)
    for x in range(50, 76):
        um.add_unit(P2, B_STONE_WALL, x=x, y=48)
        um.add_unit(P2, B_STONE_WALL, x=x, y=70)
    for y in range(48, 71):
        um.add_unit(P2, B_STONE_WALL, x=50, y=y)
        um.add_unit(P2, B_STONE_WALL, x=75, y=y)
    for i in range(6):
        um.add_unit(P2, U_HOPLITE, x=55+i*3, y=52)
        um.add_unit(P2, U_ARCHER,  x=55+i*3, y=66)
    um.add_unit(P2, U_WAR_CHARIOT, x=62, y=60)
    um.add_unit(P2, U_WAR_CHARIOT, x=58, y=60)

    um.add_unit(P3, B_TOWN_CENTER, x=100, y=55)
    for i in range(5):
        um.add_unit(P3, U_MILITIA, x=95, y=52+i*3)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>The Walls of Jericho</b>\n\n"
            "1406 BC. After forty years in the wilderness, Joshua leads Israel "
            "across the Jordan into the Promised Land. Jericho's walls are said "
            "to be unbreakable.\n\n"
            "God commands: march around the city once each day for six days, "
            "then seven times on the seventh. When the priests blow the ram's "
            "horns, the walls shall fall."
        ),
    )

    sub_ids = setup_objectives(tm, "The Walls of Jericho", [
        ("Destroy Jericho's Town Center",    "Breach the walls and destroy the heart of the city."),
        ("Protect Joshua",                   "If Joshua falls, all is lost."),
        ("Defeat the Canaanite relief force","Repel any army that marches to Jericho's aid."),
    ])

    for day in range(1, 8):
        td = tm.add_trigger(f"Day {day}")
        td.enabled = (day == 1)
        td.new_condition.timer(timer=day * 90)
        if day < 7:
            td.new_effect.display_instructions(
                display_time=8, instruction_panel_position=0,
                message=f"Day {day}: Israel marches around Jericho in silence. The defenders watch in confusion.",
            )
            td.new_effect.deactivate_trigger(trigger_id=td.trigger_id)
        else:
            td.new_effect.display_instructions(
                display_time=13, instruction_panel_position=0,
                message=(
                    "On the seventh day the trumpets blare and the people shout! "
                    "The walls of Jericho tremble. CHARGE!"
                ),
            )
            td.new_effect.damage_object(
                object_list_unit_id=B_STONE_WALL, source_player=P2,
                area_x1=48, area_y1=46, area_x2=77, area_y2=72, quantity=500,
            )
            td.new_effect.deactivate_trigger(trigger_id=td.trigger_id)

    t_win = tm.add_trigger("Victory – Jericho Falls")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=jericho_tc.reference_id)
    t_win.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="Jericho has fallen! The first great victory in the Promised Land belongs to Israel.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Joshua has fallen. Without their commander, Israel retreats across the Jordan.")
    s.message_manager.instructions = "Destroy Jericho's Town Center. Wait for the Day 7 shout to weaken the walls first."
    s.message_manager.victory = "Jericho has fallen! The conquest of Canaan begins."
    s.message_manager.loss = "Joshua has been slain. The assault on Jericho fails."
    save(s, "ot_02_jericho.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 3 – THE PROMISED LAND
# ═══════════════════════════════════════════════════════════════════════════════
def build_s03():
    print("Building S03: The Promised Land…")
    s = new_scenario(MAP_LARGE)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS)
    fill_terrain(mm, T_GRASS_DRY, 0, 0, 50, 60)
    fill_terrain(mm, T_DESERT, 110, 0, 143, 143)
    draw_river(mm, T_SHALLOW, 0, 72, 30, 72, width=5)
    fill_terrain(mm, T_FOREST_MED, 60, 100, 90, 143)
    set_elevation_area(mm, 2, 55, 50, 90, 90)

    # Decoration
    scatter(um,  0, 30, 55, 70, [TREE_OLIVE, BUSH_A],          25, seed=20)
    scatter(um, 55, 50, 90, 90, [TREE_CYPRESS, ROCK_LIME],     20, seed=21)
    scatter(um, 60,100, 90,143, [TREE_OAK, PLANT_SHRUB],       20, seed=22)
    scatter(um,110,  0,143,143, [TREE_DEAD, CACTUS, ROCK_SM],  20, seed=23)
    scatter(um,  0,  0, 50, 30, [ROCK_MED, ROCK_SM, BUSH_A],   15, seed=24)

    setup_player(pm, P1, CIV_ISRAEL, "Israel",
                 food=600, wood=500, gold=300, stone=200, human=True)
    setup_player(pm, P2, CIV_CANAAN, "Hazor",
                 food=700, wood=500, gold=400, stone=300)
    setup_player(pm, P3, CIV_CANAAN, "Lachish",
                 food=600, wood=400, gold=300, stone=200)
    setup_player(pm, P4, CIV_EGYPT,  "Jerusalem",
                 food=800, wood=500, gold=500, stone=400)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P4, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY,  DIPL_ALLY)
    set_diplomacy(pm, P2, P4, DIPL_ALLY,  DIPL_ALLY)
    set_diplomacy(pm, P3, P4, DIPL_ALLY,  DIPL_ALLY)

    um.add_unit(P1, B_TOWN_CENTER, x=15, y=72)
    um.add_unit(P1, B_BARRACKS,    x=12, y=78)
    um.add_unit(P1, U_KING,        x=17, y=72)
    for i in range(6): um.add_unit(P1, U_MILITIA,  x=10+i*2, y=68)
    for i in range(4): um.add_unit(P1, U_ARCHER,   x=10+i*2, y=76)
    for i in range(3): um.add_unit(P1, U_VILLAGER, x=20+i,   y=74)

    hazor_tc = um.add_unit(P2, B_TOWN_CENTER, x=70, y=25)
    um.add_unit(P2, B_CASTLE,      x=65, y=20)
    um.add_unit(P2, B_WATCH_TOWER, x=80, y=20)
    for i in range(6): um.add_unit(P2, U_WAR_CHARIOT, x=72+i*2, y=30)
    for i in range(5): um.add_unit(P2, U_HOPLITE,     x=68+i*2, y=32)

    lachish_tc = um.add_unit(P3, B_TOWN_CENTER, x=40, y=110)
    um.add_unit(P3, B_CASTLE, x=35, y=105)
    for i in range(5): um.add_unit(P3, U_MILITIA, x=38+i*2, y=108)
    for i in range(4): um.add_unit(P3, U_ARCHER,  x=38+i*2, y=115)

    jer_tc = um.add_unit(P4, B_TOWN_CENTER, x=95, y=72)
    um.add_unit(P4, B_CASTLE,      x=90, y=65)
    um.add_unit(P4, B_CASTLE,      x=90, y=80)
    um.add_unit(P4, B_WATCH_TOWER, x=100, y=65)
    um.add_unit(P4, B_WATCH_TOWER, x=100, y=80)
    for i in range(8): um.add_unit(P4, U_HOPLITE,     x=93+i*2, y=72)
    for i in range(4): um.add_unit(P4, U_WAR_CHARIOT, x=93+i*2, y=68)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20, instruction_panel_position=0,
        message=(
            "<b>The Promised Land</b>\n\n"
            "The conquest of Canaan has begun. Three kingdoms stand in Israel's "
            "way: Hazor in the north, Lachish in the south-west, and Jerusalem "
            "in the hills. Destroy them all before they unite against you."
        ),
    )

    sub_ids = setup_objectives(tm, "The Promised Land", [
        ("Destroy Hazor",    "Defeat the northern Canaanite coalition."),
        ("Destroy Lachish",  "Break the southern Canaanite stronghold."),
        ("Destroy Jerusalem","Capture the fortress city of the Jebusites."),
        ("Protect Joshua",   "The commander must survive."),
    ])

    for tc, city, msg, sid in [
        (hazor_tc,   "Hazor",    "Hazor burns! The north is open.",      sub_ids[0]),
        (lachish_tc, "Lachish",  "Lachish falls! The south road is free.",sub_ids[1]),
        (jer_tc,     "Jerusalem","Jerusalem taken! The hills are Israel's.",sub_ids[2]),
    ]:
        t = tm.add_trigger(f"{city} Falls")
        t.enabled = True
        t.new_condition.destroy_object(unit_object=tc.reference_id)
        t.new_effect.display_instructions(display_time=10, message=msg, instruction_panel_position=0)
        t.new_effect.deactivate_trigger(trigger_id=sid)
        t.new_effect.deactivate_trigger(trigger_id=t.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=hazor_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=lachish_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=jer_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="The Promised Land is Israel's! The twelve tribes claim their inheritance.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Joshua has fallen. The conquest of Canaan has stalled.")
    s.message_manager.instructions = "Destroy the Town Centers of Hazor, Lachish, and Jerusalem."
    s.message_manager.victory = "All of Canaan bows before Israel!"
    s.message_manager.loss = "Joshua is dead. The conquest fails."
    save(s, "ot_03_promised_land.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 4 – DEBORAH'S SWORD
# ═══════════════════════════════════════════════════════════════════════════════
def build_s04():
    print("Building S04: Deborah's Sword…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS)
    fill_terrain(mm, T_GRASS_DRY, 0,  0, 119, 30)
    fill_terrain(mm, T_GRASS_DRY, 0, 90, 119, 119)
    set_elevation_area(mm, 3, 0, 0, 20, 119)
    set_elevation_area(mm, 2, 100, 0, 119, 119)
    draw_river(mm, T_SHALLOW, 30, 50, 90, 70, width=3)

    # Decoration
    scatter(um, 100,  0, 119, 119, [TREE_CYPRESS, ROCK_SM],  20, seed=30)  # Mt Tabor
    scatter(um,   0,  0,  20, 119, [TREE_OAK, ROCK_MED],     15, seed=31)  # western hills
    scatter(um,  20, 32,  95,  48, [BUSH_A, PLANT_SHRUB],    25, seed=32)  # valley floor
    scatter(um,  20, 72,  95,  88, [BUSH_A, PLANT_SHRUB],    20, seed=33)
    scatter(um,  28, 48,  92,  72, [TREE_ACACIA, BUSH_A],    15, seed=34)  # Kishon banks

    setup_player(pm, P1, CIV_ISRAEL, "Israel",
                 food=400, wood=300, gold=200, stone=0, human=True)
    setup_player(pm, P2, CIV_CANAAN, "Sisera's Army",
                 food=900, wood=600, gold=400, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)

    deborah = um.add_unit(P1, U_KING,    x=105, y=60)
    um.add_unit(P1, B_BARRACKS,           x=108, y=60)
    for i in range(10): um.add_unit(P1, U_MILITIA,  x=100, y=50+i*3)
    for i in range(6):  um.add_unit(P1, U_ARCHER,   x=102, y=52+i*3)
    for i in range(4):  um.add_unit(P1, U_SPEARMAN, x=98,  y=54+i*3)

    sisera_flag = um.add_unit(P2, B_TOWN_CENTER, x=30, y=60)
    for row in range(4):
        for col in range(8):
            um.add_unit(P2, U_WAR_CHARIOT, x=20+col*6, y=45+row*10)
    for i in range(12): um.add_unit(P2, U_HOPLITE, x=15+i*3, y=70)
    for i in range(8):  um.add_unit(P2, U_ARCHER,  x=15+i*4, y=40)
    um.add_unit(P2, B_CASTLE,      x=15, y=60)
    um.add_unit(P2, B_WATCH_TOWER, x=25, y=45)
    um.add_unit(P2, B_WATCH_TOWER, x=25, y=75)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>Deborah's Sword</b>\n\n"
            "1125 BC. For twenty years Canaanite king Jabin has oppressed Israel "
            "with nine hundred iron chariots under Sisera. The prophetess Deborah "
            "summons Barak from Mount Tabor: 'Go! The Lord gives Sisera into your "
            "hands today!'\n\nA storm is coming. The Kishon river will flood and "
            "bog down the chariots. Strike from the high ground!"
        ),
    )

    sub_ids = setup_objectives(tm, "Deborah's Sword", [
        ("Destroy Sisera's camp (Town Center)", "Break the Canaanite host in the valley below."),
        ("Protect Deborah",                     "The prophetess must survive to lead Israel."),
    ])

    t_storm = tm.add_trigger("The Storm Breaks")
    t_storm.enabled = True
    t_storm.new_condition.timer(timer=120)
    t_storm.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message=(
            "The heavens open! Rain floods the Kishon. Sisera's iron chariots "
            "are mired in mud — their advantage is lost. CHARGE!"
        ),
    )
    t_storm.new_effect.damage_object(
        object_list_unit_id=U_WAR_CHARIOT, source_player=P2,
        area_x1=0, area_y1=0, area_x2=119, area_y2=119, quantity=60,
    )
    t_storm.new_effect.deactivate_trigger(trigger_id=t_storm.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=sisera_flag.reference_id)
    t_win.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="Sisera's army is routed! The iron chariot host lies broken in the mud of the Kishon.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Deborah has fallen. Sisera's grip on Israel tightens.")
    s.message_manager.instructions = "Charge down from Mount Tabor. Wait for the storm, then destroy Sisera's camp."
    s.message_manager.victory = "Sisera is broken! Israel breathes free."
    s.message_manager.loss = "The prophetess has fallen."
    save(s, "ot_04_deborah.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 5 – GIDEON'S 300
# ═══════════════════════════════════════════════════════════════════════════════
def build_s05():
    print("Building S05: Gideon's 300…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_DESERT, 0, 70, 119, 119)
    fill_terrain(mm, T_GRASS, 30, 20, 90, 70)
    set_elevation_area(mm, 3, 0, 0, 20, 60)
    draw_river(mm, T_SHALLOW, 40, 0, 40, 80, width=3)

    # Decoration
    scatter(um,  0,  0,  20,  60, [TREE_CYPRESS, ROCK_MED],  18, seed=40)  # Gideon's hill
    scatter(um, 30, 20,  90,  70, [BUSH_A, PLANT_SHRUB],     25, seed=41)  # Harod valley
    scatter(um,  0, 70, 119, 119, [CACTUS, TREE_DEAD, ROCK_SM], 22, seed=42)
    scatter(um, 36,  0,  44,  80, [TREE_ACACIA],              8, seed=43)  # spring banks

    setup_player(pm, P1, CIV_ISRAEL,  "Gideon",
                 food=200, wood=100, gold=100, stone=0, human=True)
    setup_player(pm, P2, CIV_MIDIAN,  "Midian",
                 food=1200, wood=800, gold=600, stone=0)
    setup_player(pm, P3, CIV_PALMYRAN,"Amalek",
                 food=600, wood=400, gold=300, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY,  DIPL_ALLY)

    gideon = um.add_unit(P1, U_KING, x=10, y=30)
    for i in range(8):  um.add_unit(P1, U_MILITIA, x=8+i*2,  y=25)
    for i in range(7):  um.add_unit(P1, U_ARCHER,  x=8+i*2,  y=32)
    for i in range(5):  um.add_unit(P1, U_SLINGER, x=10+i*2, y=38)

    midian_tc = um.add_unit(P2, B_TOWN_CENTER, x=70, y=50)
    um.add_unit(P2, B_CASTLE, x=65, y=45)
    amalek_tc = um.add_unit(P3, B_TOWN_CENTER, x=90, y=70)
    for col in range(10):
        for row in range(5):
            um.add_unit(P2, U_MILITIA,     x=50+col*5, y=30+row*6)
    for i in range(8):  um.add_unit(P2, U_WAR_CHARIOT, x=55+i*4, y=55)
    for i in range(6):  um.add_unit(P3, U_MILITIA,     x=88+i,   y=68)
    for i in range(4):  um.add_unit(P3, U_ARCHER,      x=88+i,   y=74)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>Gideon's 300</b>\n\n"
            "1169 BC. The Midianites strip Israel bare. God chooses Gideon — "
            "the least of his family. The army is reduced from 32,000 to 300, "
            "keeping only those who lap water like dogs.\n\n"
            "By night, armed with torches and ram's horns, the 300 will descend "
            "on the Midianite camp and shatter it with confusion."
        ),
    )

    sub_ids = setup_objectives(tm, "Gideon's 300", [
        ("Destroy the Midianite camp",  "Break the main enemy Town Center in the valley."),
        ("Destroy the Amalekite camp",  "Eliminate the allied Amalekite force."),
        ("Protect Gideon",              "The chosen leader must survive."),
    ])

    t_night = tm.add_trigger("Night Raid – Confusion")
    t_night.enabled = True
    t_night.new_condition.timer(timer=90)
    t_night.new_effect.display_instructions(
        display_time=13, instruction_panel_position=0,
        message=(
            "The trumpets blare, the torches blaze: 'A sword for the Lord and "
            "for Gideon!' The Midianites wake in blind panic — they attack each "
            "other in the darkness!"
        ),
    )
    t_night.new_effect.change_diplomacy(
        source_player=P2, target_player=P3, diplomacy=DIPL_ENEMY,
    )
    t_night.new_effect.change_diplomacy(
        source_player=P3, target_player=P2, diplomacy=DIPL_ENEMY,
    )
    t_night.new_effect.deactivate_trigger(trigger_id=t_night.trigger_id)

    t_midian_done = tm.add_trigger("Midian Falls")
    t_midian_done.enabled = True
    t_midian_done.new_condition.destroy_object(unit_object=midian_tc.reference_id)
    t_midian_done.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_midian_done.new_effect.deactivate_trigger(trigger_id=t_midian_done.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=midian_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=amalek_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="Midian flees across the Jordan! With 300 men and the hand of God, Gideon has delivered Israel.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Gideon has fallen. Midian's yoke remains on Israel.")
    s.message_manager.instructions = "Wait 90 seconds for the night raid trigger — then strike both camps."
    s.message_manager.victory = "Midian is routed by 300 faithful men!"
    s.message_manager.loss = "Gideon has been slain."
    save(s, "ot_05_gideon.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 6 – THE FIRST KING  (Saul)
# ═══════════════════════════════════════════════════════════════════════════════
def build_s06():
    print("Building S06: The First King…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_GRASS, 30, 40, 90, 90)
    fill_terrain(mm, T_DESERT, 90, 0, 119, 119)
    set_elevation_area(mm, 2, 0, 0, 30, 60)
    draw_river(mm, T_SHALLOW, 0, 75, 60, 75, width=3)

    # Decoration
    scatter(um,  0,  0,  30,  60, [TREE_CYPRESS, ROCK_MED],  18, seed=50)
    scatter(um, 30, 40,  90,  90, [TREE_OLIVE, BUSH_A],      25, seed=51)
    scatter(um, 90,  0, 119, 119, [TREE_DEAD, CACTUS],       18, seed=52)
    scatter(um,  0, 70,  60,  80, [TREE_ACACIA, PLANT_SHRUB], 10, seed=53)

    setup_player(pm, P1, CIV_ISRAEL,   "King Saul",
                 food=500, wood=400, gold=300, stone=100, human=True)
    setup_player(pm, P2, CIV_SELEUCID, "Philistia",
                 food=900, wood=600, gold=500, stone=200)
    setup_player(pm, P3, CIV_MIDIAN,   "Amalek",
                 food=500, wood=300, gold=200, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY,   DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY,   DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_NEUTRAL, DIPL_NEUTRAL)

    saul = um.add_unit(P1, U_KING,        x=20, y=50)
    um.add_unit(P1, B_TOWN_CENTER,         x=18, y=48)
    um.add_unit(P1, B_BARRACKS,            x=15, y=55)
    for i in range(8): um.add_unit(P1, U_MILITIA,  x=15+i*2, y=44)
    for i in range(6): um.add_unit(P1, U_SPEARMAN, x=15+i*2, y=52)
    for i in range(4): um.add_unit(P1, U_ARCHER,   x=15+i*3, y=58)
    for i in range(3): um.add_unit(P1, U_VILLAGER, x=22+i,   y=50)

    phil_tc = um.add_unit(P2, B_TOWN_CENTER, x=90, y=60)
    um.add_unit(P2, B_CASTLE, x=85, y=55)
    um.add_unit(P2, B_CASTLE, x=85, y=65)
    for i in range(8): um.add_unit(P2, U_HOPLITE,     x=80+i*2, y=60)
    for i in range(5): um.add_unit(P2, U_WAR_CHARIOT, x=78+i*3, y=55)
    for i in range(4): um.add_unit(P2, U_ARCHER,      x=80+i*2, y=66)

    amalek_tc = um.add_unit(P3, B_TOWN_CENTER, x=60, y=105)
    for i in range(6): um.add_unit(P3, U_MILITIA, x=55+i*2, y=100)
    for i in range(4): um.add_unit(P3, U_ARCHER,  x=55+i*2, y=108)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20, instruction_panel_position=0,
        message=(
            "<b>The First King</b>\n\n"
            "1051 BC. The elders of Israel demand a king. Samuel anoints Saul "
            "of Benjamin — tall, head-and-shoulders above every man.\n\n"
            "But a king must prove himself. The Philistines press from the coast "
            "with iron weapons. The Amalekites raid from the south. "
            "Unite the tribes and drive back both threats."
        ),
    )

    sub_ids = setup_objectives(tm, "The First King", [
        ("Destroy the Philistine stronghold", "Break the Philistine Town Center on the coast."),
        ("Destroy the Amalekite camp",        "Eliminate the raiders from the south."),
        ("Protect King Saul",                 "The first king of Israel must survive."),
    ])

    t_phil = tm.add_trigger("Philistia Falls")
    t_phil.enabled = True
    t_phil.new_condition.destroy_object(unit_object=phil_tc.reference_id)
    t_phil.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_phil.new_effect.deactivate_trigger(trigger_id=t_phil.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=phil_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=amalek_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="The kingdom is secured! Saul reigns over a united Israel. But the shadow of David already falls.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Saul has fallen. Israel has no king.")
    s.message_manager.instructions = "Defeat both the Philistines and Amalekites. Build up your forces first."
    s.message_manager.victory = "Saul establishes the first kingdom of Israel!"
    s.message_manager.loss = "The first king of Israel is no more."
    save(s, "ot_06_first_king.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 7 – THE SHEPHERD KING  (David)
# ═══════════════════════════════════════════════════════════════════════════════
def build_s07():
    print("Building S07: The Shepherd King…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_GRASS, 40, 30, 90, 90)
    set_elevation_area(mm, 3, 55, 50, 75, 70)
    fill_terrain(mm, T_ROAD, 55, 50, 75, 70)
    draw_river(mm, T_SHALLOW, 0, 60, 40, 60, width=4)
    fill_terrain(mm, T_DESERT, 95, 0, 119, 119)

    # Decoration
    scatter(um, 40, 30, 90, 90, [TREE_OLIVE, PLANT_SHRUB],  28, seed=60)
    scatter(um, 53, 48, 77, 72, [ROCK_LIME, ROCK_SM],       15, seed=61)  # Jerusalem stone
    scatter(um, 55, 49, 76, 72, [TREE_CYPRESS],              6, seed=62)
    scatter(um, 95,  0,119,119, [TREE_DEAD, CACTUS, ROCK_SM], 18, seed=63)
    scatter(um,  0, 56, 42, 64, [TREE_ACACIA, BUSH_A],      10, seed=64)

    setup_player(pm, P1, CIV_ISRAEL,   "King David",
                 food=600, wood=500, gold=400, stone=200, human=True)
    setup_player(pm, P2, CIV_SELEUCID, "Philistia",
                 food=800, wood=600, gold=500, stone=300)
    setup_player(pm, P3, CIV_CANAAN,   "Jebusite Jerusalem",
                 food=600, wood=400, gold=400, stone=500)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY,   DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY,   DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_NEUTRAL, DIPL_NEUTRAL)

    david = um.add_unit(P1, U_KING,        x=15, y=60)
    um.add_unit(P1, B_TOWN_CENTER,          x=13, y=58)
    um.add_unit(P1, B_BARRACKS,             x=10, y=64)
    um.add_unit(P1, B_ARCHERY_RANGE,        x=10, y=54)
    for i in range(10): um.add_unit(P1, U_MILITIA,  x=10+i*2, y=55)
    for i in range(6):  um.add_unit(P1, U_ARCHER,   x=10+i*2, y=63)
    for i in range(4):  um.add_unit(P1, U_SPEARMAN, x=10+i*2, y=67)
    for i in range(4):  um.add_unit(P1, U_VILLAGER, x=18+i,   y=60)

    phil_tc = um.add_unit(P2, B_TOWN_CENTER, x=100, y=40)
    um.add_unit(P2, B_CASTLE, x=95, y=35)
    for i in range(8): um.add_unit(P2, U_HOPLITE,     x=90+i*2, y=45)
    for i in range(5): um.add_unit(P2, U_WAR_CHARIOT, x=90+i*3, y=38)

    jer_tc = um.add_unit(P3, B_TOWN_CENTER, x=63, y=60)
    um.add_unit(P3, B_CASTLE,      x=57, y=55)
    um.add_unit(P3, B_WATCH_TOWER, x=72, y=55)
    um.add_unit(P3, B_WATCH_TOWER, x=72, y=65)
    for x in range(55, 76):
        um.add_unit(P3, B_STONE_WALL, x=x, y=52)
        um.add_unit(P3, B_STONE_WALL, x=x, y=70)
    for y in range(52, 71):
        um.add_unit(P3, B_STONE_WALL, x=55, y=y)
        um.add_unit(P3, B_STONE_WALL, x=75, y=y)
    for i in range(8): um.add_unit(P3, U_HOPLITE, x=60+i, y=58)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20, instruction_panel_position=0,
        message=(
            "<b>The Shepherd King</b>\n\n"
            "1010 BC. After years in the wilderness, David is anointed king at "
            "Hebron. All Israel rallies to him.\n\n"
            "Two tasks stand before the new king: drive out the Philistines, and "
            "capture the Jebusite fortress of Jerusalem — to make it the eternal "
            "capital of his kingdom."
        ),
    )

    sub_ids = setup_objectives(tm, "The Shepherd King", [
        ("Defeat the Philistines",   "Destroy the Philistine Town Center on the coast."),
        ("Capture Jerusalem",        "Destroy the Jebusite Town Center on the hill."),
        ("Protect King David",       "The shepherd king must survive."),
    ])

    t_jer = tm.add_trigger("Jerusalem Captured")
    t_jer.enabled = True
    t_jer.new_condition.destroy_object(unit_object=jer_tc.reference_id)
    t_jer.new_effect.deactivate_trigger(trigger_id=sub_ids[1])
    t_jer.new_effect.display_instructions(
        display_time=10, instruction_panel_position=0,
        message="Jerusalem is taken! David makes it the City of David, capital of a united Israel.",
    )
    t_jer.new_effect.deactivate_trigger(trigger_id=t_jer.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=phil_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=jer_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="David reigns from Jerusalem over all Israel and Judah. A man after God's own heart.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "David has fallen in battle.")
    s.message_manager.instructions = "Destroy both Town Centers. Build up at Hebron before assaulting Jerusalem."
    s.message_manager.victory = "Jerusalem is the City of David! Israel is united."
    s.message_manager.loss = "The shepherd king has fallen."
    save(s, "ot_07_shepherd_king.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 8 – SOLOMON'S TEMPLE
# ═══════════════════════════════════════════════════════════════════════════════
def build_s08():
    print("Building S08: Solomon's Temple…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_GRASS, 20, 20, 100, 100)
    fill_terrain(mm, T_ROAD, 50, 48, 72, 72)
    set_elevation_area(mm, 3, 48, 46, 74, 74)
    fill_terrain(mm, T_DESERT, 0, 0, 20, 119)
    fill_terrain(mm, T_WATER_MED, 90, 0, 119, 50)
    draw_river(mm, T_SHALLOW, 90, 0, 90, 60, width=4)

    # Decoration
    scatter(um, 20, 20, 95,100, [TREE_OLIVE, TREE_CYPRESS],  30, seed=70)  # gardens
    scatter(um, 88,  0,119, 55, [TREE_PALM, PLANT_SHRUB],    15, seed=71)  # Tyre coast
    scatter(um, 48, 44, 76, 76, [ROCK_LIME],                 10, seed=72)  # Temple Mount
    scatter(um,  0,  0,  22,119, [TREE_DEAD, ROCK_SM],       12, seed=73)  # western desert

    setup_player(pm, P1, CIV_ISRAEL, "King Solomon",
                 food=800, wood=600, gold=500, stone=500, human=True)
    setup_player(pm, P2, CIV_TYRE,   "Tyre (Ally)",
                 food=500, wood=800, gold=400, stone=200)
    set_diplomacy(pm, P1, P2, DIPL_ALLY, DIPL_ALLY)

    um.add_unit(P1, B_TOWN_CENTER, x=60, y=60)
    um.add_unit(P1, B_MARKET,      x=55, y=70)
    um.add_unit(P1, B_BARRACKS,    x=55, y=50)
    um.add_unit(P1, U_KING,        x=62, y=60)
    for i in range(6): um.add_unit(P1, U_VILLAGER, x=64+i, y=60)
    for i in range(4): um.add_unit(P1, U_VILLAGER, x=64+i, y=55)
    um.add_unit(P2, B_TOWN_CENTER, x=100, y=25)
    um.add_unit(P2, B_MARKET,      x=105, y=30)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>Solomon's Temple</b>\n\n"
            "970 BC. Solomon inherits a kingdom at peace and a divine commission: "
            "build the Temple that his father's wars would not allow.\n\n"
            "Hiram, King of Tyre, sends cedar wood and craftsmen. The project "
            "will take seven years.\n\n"
            "Gather resources and build the Temple (Wonder) before the deadline. "
            "Tyre will send tribute shipments to help."
        ),
    )

    sub_ids = setup_objectives(tm, "Solomon's Temple", [
        ("Build the Temple (Wonder)", "Construct a Wonder on the Temple Mount before time runs out."),
        ("Protect King Solomon",      "Solomon must oversee the construction."),
    ])

    for i, delay in enumerate([60, 150, 240, 360]):
        tt = tm.add_trigger(f"Tyre Tribute {i+1}")
        tt.enabled = True
        tt.new_condition.timer(timer=delay)
        tt.new_effect.tribute(
            quantity=200, tribute_list=1, source_player=P2, target_player=P1,
        )
        tt.new_effect.tribute(
            quantity=150, tribute_list=3, source_player=P2, target_player=P1,
        )
        tt.new_effect.display_instructions(
            display_time=6, instruction_panel_position=0,
            message="A Tyrian caravan arrives bearing cedar and stone for the Temple.",
        )
        tt.new_effect.deactivate_trigger(trigger_id=tt.trigger_id)

    t_warn = tm.add_trigger("Deadline Warning")
    t_warn.enabled = True
    t_warn.new_condition.timer(timer=420)
    t_warn.new_effect.display_instructions(
        display_time=10, instruction_panel_position=0,
        message="Seven years have nearly passed. If the Temple is not raised soon, the moment will be lost!",
    )
    t_warn.new_effect.deactivate_trigger(trigger_id=t_warn.trigger_id)

    t_win = tm.add_trigger("Victory – Temple Complete")
    t_win.enabled = True
    t_win.new_condition.own_objects(quantity=1, source_player=P1, object_list=B_WONDER)
    t_win.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_win.new_effect.display_instructions(
        display_time=15, instruction_panel_position=0,
        message=(
            "The Temple is complete! The Ark of the Covenant is carried into "
            "the Holy of Holies. The glory of the Lord fills the Temple."
        ),
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Solomon has fallen. The Temple was never built.")
    s.message_manager.instructions = "Build a Wonder (the Temple) before the 14-minute deadline. Accept Tyre's tributes."
    s.message_manager.victory = "The Temple stands! Solomon's golden age begins."
    s.message_manager.loss = "The Temple was never built."
    save(s, "ot_08_solomon.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 9 – A KINGDOM DIVIDED
# ═══════════════════════════════════════════════════════════════════════════════
def build_s09():
    print("Building S09: A Kingdom Divided…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_GRASS, 30, 20, 90, 90)
    draw_river(mm, T_SHALLOW, 55, 0, 55, 119, width=4)
    fill_terrain(mm, T_DESERT, 95, 0, 119, 119)
    set_elevation_area(mm, 2, 40, 40, 70, 80)

    # Decoration
    scatter(um, 30, 20, 90, 90, [TREE_OLIVE, TREE_CYPRESS, BUSH_A], 30, seed=80)
    scatter(um, 52,  0,  58,119, [TREE_ACACIA, PLANT_SHRUB],        12, seed=81)
    scatter(um, 95,  0,119,119, [TREE_DEAD, CACTUS, ROCK_SM],       18, seed=82)
    scatter(um, 38, 38, 72, 82, [ROCK_LIME, ROCK_SM],               15, seed=83)

    setup_player(pm, P1, CIV_ISRAEL, "Judah",
                 food=500, wood=400, gold=300, stone=200, human=True)
    setup_player(pm, P2, CIV_ISRAEL, "Israel (North)",
                 food=600, wood=400, gold=300, stone=100)
    setup_player(pm, P3, CIV_EGYPT,  "Egypt (Shishak)",
                 food=800, wood=500, gold=600, stone=200)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY,  DIPL_ALLY)

    rehoboam = um.add_unit(P1, U_KING,        x=50, y=80)
    um.add_unit(P1, B_TOWN_CENTER,             x=48, y=78)
    um.add_unit(P1, B_CASTLE,                  x=43, y=75)
    um.add_unit(P1, B_WATCH_TOWER,             x=55, y=75)
    for y in range(73, 89):
        um.add_unit(P1, B_STONE_WALL, x=43, y=y)
        um.add_unit(P1, B_STONE_WALL, x=58, y=y)
    for i in range(8): um.add_unit(P1, U_HOPLITE,  x=44+i*2, y=76)
    for i in range(5): um.add_unit(P1, U_ARCHER,   x=44+i*2, y=82)
    for i in range(3): um.add_unit(P1, U_VILLAGER, x=50+i,   y=80)

    jeroboam_tc = um.add_unit(P2, B_TOWN_CENTER, x=50, y=35)
    um.add_unit(P2, B_CASTLE, x=45, y=30)
    for i in range(8): um.add_unit(P2, U_MILITIA,     x=45+i*2, y=40)
    for i in range(5): um.add_unit(P2, U_ARCHER,      x=45+i*2, y=35)
    for i in range(3): um.add_unit(P2, U_WAR_CHARIOT, x=48+i*2, y=30)

    shishak_tc = um.add_unit(P3, B_TOWN_CENTER, x=105, y=60)
    for i in range(10): um.add_unit(P3, U_WAR_CHARIOT, x=100+i, y=55)
    for i in range(8):  um.add_unit(P3, U_HOPLITE,     x=98+i*2, y=62)
    for i in range(6):  um.add_unit(P3, U_ARCHER,      x=98+i*2, y=68)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>A Kingdom Divided</b>\n\n"
            "930 BC. Solomon is dead. His son Rehoboam threatens heavier taxes — "
            "ten tribes revolt under Jeroboam, forming the northern Kingdom of "
            "Israel. Only Judah and Benjamin remain loyal.\n\n"
            "Now Shishak of Egypt invades from the east. "
            "Rehoboam must defend Jerusalem from enemies on two fronts."
        ),
    )

    sub_ids = setup_objectives(tm, "A Kingdom Divided", [
        ("Destroy the northern Israel (Town Center)", "Repel Jeroboam's rebellion from the north."),
        ("Destroy Shishak's Egyptian army",           "Drive back the Egyptian invasion from the east."),
        ("Protect Rehoboam",                          "The king of Judah must survive."),
    ])

    for tc, name, sid in [
        (jeroboam_tc, "North Israel", sub_ids[0]),
        (shishak_tc,  "Shishak",      sub_ids[1]),
    ]:
        t = tm.add_trigger(f"{name} Defeated")
        t.enabled = True
        t.new_condition.destroy_object(unit_object=tc.reference_id)
        t.new_effect.deactivate_trigger(trigger_id=sid)
        t.new_effect.deactivate_trigger(trigger_id=t.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=jeroboam_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=shishak_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="Jerusalem stands! Though the kingdom is forever split, Judah endures — the line of David continues.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Rehoboam has fallen. Jerusalem is lost.")
    s.message_manager.instructions = "Defend Jerusalem from north and east. Destroy both enemy Town Centers."
    s.message_manager.victory = "Judah survives the division and foreign invasion."
    s.message_manager.loss = "The house of David falls."
    save(s, "ot_09_divided.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 10 – HEZEKIAH'S WALL
# ═══════════════════════════════════════════════════════════════════════════════
def build_s10():
    print("Building S10: Hezekiah's Wall…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_DESERT, 70, 0, 119, 119)
    fill_terrain(mm, T_ROAD, 30, 40, 60, 80)
    set_elevation_area(mm, 4, 25, 38, 65, 82)
    fill_terrain(mm, T_GRASS, 0, 0, 70, 119)

    # Decoration
    scatter(um, 25, 36, 67, 84, [ROCK_LIME, ROCK_SM],           20, seed=90)  # Jerusalem walls
    scatter(um, 25, 36, 67, 84, [TREE_CYPRESS],                  8, seed=91)
    scatter(um,  0,  0,  25,119, [TREE_OLIVE, BUSH_A],           18, seed=92)
    scatter(um, 67,  0,119,119, [TREE_DEAD, CACTUS, ROCK_MED],   20, seed=93)

    setup_player(pm, P1, CIV_ISRAEL,  "Judah",
                 food=600, wood=500, gold=400, stone=600, human=True)
    setup_player(pm, P2, CIV_ASSYRIA, "Assyria",
                 food=1500, wood=800, gold=700, stone=300)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)

    hezekiah = um.add_unit(P1, U_KING, x=42, y=60)
    um.add_unit(P1, B_TOWN_CENTER,      x=40, y=58)
    um.add_unit(P1, B_CASTLE,           x=35, y=52)
    um.add_unit(P1, B_CASTLE,           x=50, y=52)
    um.add_unit(P1, B_MONASTERY,        x=42, y=65)
    for x in range(28, 62):
        um.add_unit(P1, B_FORTIFIED_WALL, x=x, y=40)
        um.add_unit(P1, B_FORTIFIED_WALL, x=x, y=78)
    for y in range(40, 79):
        um.add_unit(P1, B_FORTIFIED_WALL, x=28, y=y)
        um.add_unit(P1, B_FORTIFIED_WALL, x=61, y=y)
    for i in range(12): um.add_unit(P1, U_HOPLITE,  x=30+i*2, y=44)
    for i in range(8):  um.add_unit(P1, U_ARCHER,   x=30+i*3, y=50)
    for i in range(6):  um.add_unit(P1, U_SLINGER,  x=30+i*3, y=74)
    for i in range(3):  um.add_unit(P1, U_VILLAGER, x=42+i,   y=60)

    sennacherib_tc = um.add_unit(P2, B_TOWN_CENTER, x=95, y=60)
    um.add_unit(P2, B_CASTLE, x=90, y=50)
    um.add_unit(P2, B_CASTLE, x=90, y=70)
    for i in range(15): um.add_unit(P2, U_HOPLITE,     x=70+i*2, y=50)
    for i in range(15): um.add_unit(P2, U_HOPLITE,     x=70+i*2, y=70)
    for i in range(10): um.add_unit(P2, U_WAR_CHARIOT, x=75+i*3, y=60)
    for i in range(10): um.add_unit(P2, U_ARCHER,      x=72+i*2, y=45)
    for i in range(10): um.add_unit(P2, U_ARCHER,      x=72+i*2, y=75)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>Hezekiah's Wall</b>\n\n"
            "701 BC. Sennacherib of Assyria has destroyed the northern kingdom. "
            "Now 185,000 soldiers surround Jerusalem. His envoy mocks: "
            "'Has any god delivered his nation from my hand?'\n\n"
            "Hezekiah strengthens the walls and prays. "
            "Hold Jerusalem for ten minutes — then God will act."
        ),
    )

    sub_ids = setup_objectives(tm, "Hezekiah's Wall", [
        ("Hold Jerusalem for 10 minutes",     "Defend the walls until the Angel of the Lord strikes."),
        ("Destroy the Assyrian camp",         "After the Angel strikes, finish what remains."),
        ("Protect Hezekiah",                  "The king must survive."),
    ])

    t_angel = tm.add_trigger("The Angel of the Lord")
    t_angel.enabled = True
    t_angel.new_condition.timer(timer=600)
    t_angel.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_angel.new_effect.display_instructions(
        display_time=15, instruction_panel_position=0,
        message=(
            "In the night the Angel of the Lord strikes 185,000 men in the "
            "Assyrian camp. When morning comes there are only corpses. "
            "Sennacherib breaks camp and withdraws to Nineveh."
        ),
    )
    for uid in [U_HOPLITE, U_WAR_CHARIOT, U_ARCHER]:
        t_angel.new_effect.kill_object(
            object_list_unit_id=uid, source_player=P2,
            area_x1=0, area_y1=0, area_x2=119, area_y2=119,
            max_units_affected=150,
        )
    t_angel.new_effect.deactivate_trigger(trigger_id=t_angel.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=sennacherib_tc.reference_id)
    t_win.new_effect.deactivate_trigger(trigger_id=sub_ids[1])
    t_win.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="The siege is broken! Jerusalem alone survives. Hezekiah's faith has saved the city.",
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Hezekiah has fallen. Jerusalem is taken by Assyria.")
    s.message_manager.instructions = "Survive 10 minutes. Then the Angel strikes — destroy the remnant to win."
    s.message_manager.victory = "God delivers Jerusalem from Sennacherib!"
    s.message_manager.loss = "The walls of Jerusalem have fallen to Assyria."
    save(s, "ot_10_hezekiah.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 11 – THE FALL OF JERUSALEM
# ═══════════════════════════════════════════════════════════════════════════════
def build_s11():
    print("Building S11: The Fall of Jerusalem…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_DESERT, 80, 0, 119, 119)
    fill_terrain(mm, T_ROAD, 20, 40, 60, 80)
    set_elevation_area(mm, 3, 18, 38, 62, 82)
    fill_terrain(mm, T_GRASS, 0, 0, 80, 119)

    # Decoration
    scatter(um, 18, 36, 64, 84, [ROCK_LIME, ROCK_SM],           18, seed=100)
    scatter(um,  0, 10,  18,119, [TREE_OLIVE, TREE_CYPRESS],    15, seed=101)
    scatter(um,  0, 90,  75,119, [BUSH_A, PLANT_SHRUB],         15, seed=102)  # escape route
    scatter(um, 80,  0,119,119, [TREE_DEAD, CACTUS, ROCK_MED],  18, seed=103)

    setup_player(pm, P1, CIV_ISRAEL,  "Judah",
                 food=400, wood=300, gold=200, stone=300, human=True)
    setup_player(pm, P2, CIV_BABYLON, "Babylon",
                 food=2000, wood=1000, gold=800, stone=400)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)

    zedekiah = um.add_unit(P1, U_KING,     x=38, y=60)
    um.add_unit(P1, B_TOWN_CENTER,          x=36, y=58)
    um.add_unit(P1, B_CASTLE,               x=30, y=52)
    um.add_unit(P1, B_MONASTERY,            x=40, y=65)
    for x in range(22, 56):
        um.add_unit(P1, B_STONE_WALL, x=x, y=40)
        um.add_unit(P1, B_STONE_WALL, x=x, y=78)
    for y in range(40, 79):
        um.add_unit(P1, B_STONE_WALL, x=22, y=y)
        um.add_unit(P1, B_STONE_WALL, x=55, y=y)
    for i in range(8): um.add_unit(P1, U_HOPLITE,  x=25+i*2, y=44)
    for i in range(6): um.add_unit(P1, U_ARCHER,   x=25+i*3, y=72)
    for i in range(2): um.add_unit(P1, U_VILLAGER, x=38+i,   y=60)
    ark = um.add_unit(P1, U_MONK, x=40, y=60)

    nebuc_tc = um.add_unit(P2, B_TOWN_CENTER, x=100, y=60)
    um.add_unit(P2, B_CASTLE, x=95, y=50)
    um.add_unit(P2, B_CASTLE, x=95, y=70)
    for i in range(20): um.add_unit(P2, U_HOPLITE,     x=65+i*2, y=50)
    for i in range(20): um.add_unit(P2, U_HOPLITE,     x=65+i*2, y=70)
    for i in range(12): um.add_unit(P2, U_WAR_CHARIOT, x=70+i*3, y=60)
    for i in range(12): um.add_unit(P2, U_ARCHER,      x=67+i*2, y=44)
    for i in range(12): um.add_unit(P2, U_ARCHER,      x=67+i*2, y=76)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "<b>The Fall of Jerusalem</b>\n\n"
            "586 BC. Nebuchadnezzar has besieged Jerusalem for eighteen months. "
            "The city starves. Jeremiah weeps: 'Is it nothing to you, all who "
            "pass by? Behold and see if there is any sorrow like my sorrow.'\n\n"
            "The walls cannot hold forever. Escape south with the Ark (the Monk) "
            "before Babylon completes its conquest."
        ),
    )

    sub_ids = setup_objectives(tm, "The Fall of Jerusalem", [
        ("Escort the Ark to the southern edge", "Move the Monk carrying the sacred scrolls to safety."),
        ("Survive the Babylonian assault",       "Hold as long as possible before the walls fall."),
    ])

    t_breach = tm.add_trigger("Walls Breached")
    t_breach.enabled = True
    t_breach.new_condition.timer(timer=300)
    t_breach.new_effect.display_instructions(
        display_time=12, instruction_panel_position=0,
        message="The wall is breached! Babylonian soldiers pour in. The Temple is burning. Escape with the scrolls!",
    )
    t_breach.new_effect.kill_object(
        object_list_unit_id=B_STONE_WALL, source_player=P1,
        area_x1=0, area_y1=0, area_x2=119, area_y2=119,
        max_units_affected=30,
    )
    for _ in range(5):
        t_breach.new_effect.create_object(
            object_list_unit_id=U_HOPLITE, source_player=P2,
            location_x=30, location_y=60,
        )
    t_breach.new_effect.deactivate_trigger(trigger_id=sub_ids[1])
    t_breach.new_effect.deactivate_trigger(trigger_id=t_breach.trigger_id)

    t_win = tm.add_trigger("Victory – The Ark Escapes")
    t_win.enabled = True
    t_win.new_condition.objects_in_area(
        quantity=1, source_player=P1, object_list=U_MONK,
        area_x1=0, area_y1=100, area_x2=70, area_y2=119,
    )
    t_win.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_win.new_effect.display_instructions(
        display_time=15, instruction_panel_position=0,
        message=(
            "Jerusalem has fallen. The Temple lies in ashes. But the sacred "
            "scrolls and the remnant of Israel escape into exile. "
            "By the rivers of Babylon they will weep — but they will return."
        ),
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose_ark = tm.add_trigger("Defeat – Ark Lost")
    t_lose_ark.enabled = True
    t_lose_ark.new_condition.timer(timer=5)
    t_lose_ark.new_condition.own_fewer_objects(
        quantity=1, source_player=P1, object_list=U_MONK,
    )
    t_lose_ark.new_effect.display_instructions(
        display_time=10, instruction_panel_position=0,
        message="The sacred scrolls are lost to Babylon. The covenant is forgotten.",
    )

    s.message_manager.instructions = "Get the Monk (Ark) to the southern edge. The city will fall — focus on escape."
    s.message_manager.victory = "The sacred remnant escapes into Babylon. Israel will return."
    s.message_manager.loss = "The last light of Jerusalem is extinguished."
    save(s, "ot_11_fall.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 12 – JUDAS MACCABEUS
# ═══════════════════════════════════════════════════════════════════════════════
def build_s12():
    print("Building S12: Judas Maccabeus…")
    s = new_scenario(MAP_LARGE)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_GRASS, 0, 30, 80, 110)
    fill_terrain(mm, T_ROCK, 0, 0, 50, 30)
    set_elevation_area(mm, 3, 0, 0, 50, 30)
    fill_terrain(mm, T_ROAD, 70, 55, 90, 75)
    set_elevation_area(mm, 2, 65, 50, 95, 80)
    fill_terrain(mm, T_DESERT, 100, 0, 143, 143)

    # Decoration — Judean hills guerrilla start
    scatter(um,  0,  0,  50,  30, [TREE_OAK, TREE_CYPRESS, ROCK_MED], 30, seed=110)
    scatter(um,  0, 30,  80, 110, [TREE_OLIVE, BUSH_A, PLANT_SHRUB],  35, seed=111)
    scatter(um, 65, 48,  95,  82, [ROCK_LIME, TREE_CYPRESS],          18, seed=112)  # Temple hill
    scatter(um,100,  0, 143, 143, [TREE_DEAD, CACTUS, ROCK_SM],       22, seed=113)

    setup_player(pm, P1, CIV_ISRAEL,   "Maccabees",
                 food=300, wood=200, gold=100, stone=0, human=True)
    setup_player(pm, P2, CIV_SELEUCID, "Seleucid Empire",
                 food=2000, wood=1200, gold=900, stone=500)
    setup_player(pm, P3, CIV_SELEUCID, "Seleucid Garrison",
                 food=600, wood=400, gold=300, stone=200)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY,  DIPL_ALLY)

    judas = um.add_unit(P1, U_KING,    x=20, y=15)
    um.add_unit(P1, B_BARRACKS,         x=18, y=12)
    for i in range(5): um.add_unit(P1, U_MILITIA,  x=15+i*2, y=10)
    for i in range(5): um.add_unit(P1, U_ARCHER,   x=15+i*2, y=18)
    for i in range(3): um.add_unit(P1, U_SLINGER,  x=18+i*2, y=24)

    seleucid_tc = um.add_unit(P2, B_TOWN_CENTER, x=120, y=70)
    um.add_unit(P2, B_CASTLE, x=115, y=60)
    um.add_unit(P2, B_CASTLE, x=115, y=80)
    for i in range(15): um.add_unit(P2, U_ELITE_HOPLITE,     x=100+i*2, y=60)
    for i in range(15): um.add_unit(P2, U_ELITE_HOPLITE,     x=100+i*2, y=80)
    for i in range(10): um.add_unit(P2, U_ELITE_WAR_CHARIOT, x=105+i*2, y=70)
    for i in range(8):  um.add_unit(P2, U_ARCHER,            x=102+i*2, y=55)

    garrison_tc = um.add_unit(P3, B_TOWN_CENTER, x=78, y=62)
    um.add_unit(P3, B_CASTLE,       x=72, y=58)
    um.add_unit(P3, B_WATCH_TOWER,  x=88, y=58)
    um.add_unit(P3, B_WATCH_TOWER,  x=88, y=70)
    um.add_unit(P3, B_MONASTERY,    x=80, y=65)
    for i in range(8): um.add_unit(P3, U_ELITE_HOPLITE, x=73+i*2, y=65)
    for i in range(5): um.add_unit(P3, U_ARCHER,        x=73+i*2, y=60)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=25, instruction_panel_position=0,
        message=(
            "<b>Judas Maccabeus</b>\n\n"
            "167 BC. Antiochus IV has desecrated the Temple and banned the Torah. "
            "Mattathias the priest refuses to comply — and strikes down a Seleucid "
            "officer. The revolt begins. His son Judas 'The Hammer' leads a band "
            "of faithful warriors from the Judean hills.\n\n"
            "Against all odds, the few must defeat the many. "
            "Liberate Jerusalem. Rededicate the Temple. "
            "The miracle of Hanukkah awaits."
        ),
    )

    sub_ids = setup_objectives(tm, "Judas Maccabeus", [
        ("Defeat the Seleucid garrison",        "Destroy the garrison Town Center holding the Temple."),
        ("Build the Temple (Wonder)",           "Rededicate the Temple — construct a Wonder on the Temple Mount."),
        ("Survive the Seleucid counter-attack", "Antiochus will send his full army. Hold them off."),
        ("Protect Judas Maccabeus",             "The Hammer must lead Israel to freedom."),
    ])

    t_phase2 = tm.add_trigger("Phase 2 - Rededicate the Temple")
    t_phase2.enabled = True
    t_phase2.new_condition.destroy_object(unit_object=garrison_tc.reference_id)
    t_phase2.new_effect.deactivate_trigger(trigger_id=sub_ids[0])
    t_phase2.new_effect.display_instructions(
        display_time=15, instruction_panel_position=0,
        message=(
            "The garrison is broken! Jerusalem is free — but the full Seleucid "
            "army is marching. Build the Temple (Wonder) before they arrive!"
        ),
    )
    t_phase2.new_effect.modify_resource(
        quantity=1000, tribute_list=3, source_player=P1, operation=1,
    )
    t_phase2.new_effect.modify_resource(
        quantity=800, tribute_list=1, source_player=P1, operation=1,
    )
    t_phase2.new_effect.deactivate_trigger(trigger_id=t_phase2.trigger_id)

    t_counter = tm.add_trigger("Seleucid Counter-Attack")
    t_counter.enabled = True
    t_counter.new_condition.timer(timer=180)
    t_counter.new_effect.display_instructions(
        display_time=10, instruction_panel_position=0,
        message="Lysias leads the Seleucid host! The full army marches on Jerusalem — defend the Temple!",
    )
    for _ in range(5):
        t_counter.new_effect.create_object(
            object_list_unit_id=U_ELITE_HOPLITE, source_player=P2,
            location_x=100, location_y=70,
        )
    t_counter.new_effect.deactivate_trigger(trigger_id=t_counter.trigger_id)

    t_win = tm.add_trigger("Victory – Hanukkah")
    t_win.enabled = True
    t_win.new_condition.own_objects(quantity=1, source_player=P1, object_list=B_WONDER)
    t_win.new_effect.deactivate_trigger(trigger_id=sub_ids[1])
    t_win.new_effect.display_instructions(
        display_time=22, instruction_panel_position=0,
        message=(
            "The Temple is rededicated! The Maccabees find one small jar of "
            "consecrated oil — enough for one day, yet it burns for eight. "
            "This is Hanukkah: the Festival of Lights.\n\n"
            "Judas Maccabeus has done what no one thought possible. "
            "Against the greatest empire of the age, the few have defeated "
            "the many. Israel is free. The flame is never extinguished."
        ),
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    add_lose_trigger(tm, "Judas Maccabeus has fallen. Without the Hammer, the revolt collapses.")
    s.message_manager.instructions = "Destroy the Garrison TC, then build a Wonder on the Temple Mount. Judas must survive."
    s.message_manager.victory = "The Festival of Lights! Israel reclaims the Temple."
    s.message_manager.loss = "The Hammer has fallen. The flame goes out."
    save(s, "ot_12_maccabeus.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# CAMPAIGN & MOD JSON
# ═══════════════════════════════════════════════════════════════════════════════
def write_campaign_json():
    import json
    data = {
        "Name": "Chronicles of Israel",
        "Difficulty": 1,
        "Scenarios": [
            {"Name": "Let My People Go",     "Filename": "ot_01_exodus.aoe2scenario"},
            {"Name": "The Walls of Jericho", "Filename": "ot_02_jericho.aoe2scenario"},
            {"Name": "The Promised Land",    "Filename": "ot_03_promised_land.aoe2scenario"},
            {"Name": "Deborah's Sword",      "Filename": "ot_04_deborah.aoe2scenario"},
            {"Name": "Gideon's 300",         "Filename": "ot_05_gideon.aoe2scenario"},
            {"Name": "The First King",       "Filename": "ot_06_first_king.aoe2scenario"},
            {"Name": "The Shepherd King",    "Filename": "ot_07_shepherd_king.aoe2scenario"},
            {"Name": "Solomon's Temple",     "Filename": "ot_08_solomon.aoe2scenario"},
            {"Name": "A Kingdom Divided",    "Filename": "ot_09_divided.aoe2scenario"},
            {"Name": "Hezekiah's Wall",      "Filename": "ot_10_hezekiah.aoe2scenario"},
            {"Name": "The Fall of Jerusalem","Filename": "ot_11_fall.aoe2scenario"},
            {"Name": "Judas Maccabeus",      "Filename": "ot_12_maccabeus.aoe2scenario"},
        ],
    }
    path = os.path.join(
        MOD_ROOT, "resources", "_common", "campaign", "chronicles_of_israel.json"
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved: {path}")


def write_mod_json():
    import json
    data = {
        "Author": "DanielVoll",
        "CacheStatus": 0,
        "Description": (
            "A 12-scenario Return of Rome campaign covering Old Testament Jewish "
            "history — from the Exodus to the Maccabean Revolt. Play as Moses, "
            "Joshua, Deborah, Gideon, Saul, David, Solomon, Hezekiah, and Judas Maccabeus."
        ),
        "Title": "Chronicles of Israel",
    }
    path = os.path.join(MOD_ROOT, "mod.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("Chronicles of Israel – Campaign Builder v2")
    print("=" * 60)

    builders = [
        build_s01, build_s02, build_s03, build_s04,
        build_s05, build_s06, build_s07, build_s08,
        build_s09, build_s10, build_s11, build_s12,
    ]
    for i, fn in enumerate(builders, 1):
        try:
            fn()
        except Exception as e:
            print(f"  ERROR in scenario {i}: {e}")
            import traceback; traceback.print_exc()

    write_campaign_json()
    write_mod_json()

    print()
    print("Done! Scenarios written to:")
    print(f"  {SCENARIO_OUT}")
    print()
    print("Play in AoE2DE: Single Player > Custom Scenarios")
    print("NOTE: Load scenarios in 'Return of Rome' mode for correct civs.")
