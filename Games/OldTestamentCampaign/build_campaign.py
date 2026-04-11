"""
Chronicles of Israel – Campaign Builder
Generates all 12 .aoe2scenario files for the Old Testament campaign.

Run with:  py build_campaign.py
"""

import os, sys
os.environ["PYTHONIOENCODING"] = "utf-8"

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioParser.datasets.players import PlayerId
from common import *

# ─── silence emoji output on Windows ─────────────────────────────────────────
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def new_scenario(map_size=MAP_MEDIUM):
    s = AoE2DEScenario.from_default()
    s.map_manager.map_size = map_size
    return s


def save(s, filename):
    path = os.path.join(SCENARIO_OUT, filename)
    s.write_to_file(path)
    print(f"  Saved: {path}")


def setup_player(pm, pid, civ, name, food=400, wood=400, gold=200, stone=200,
                 active=True, human=False):
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


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 1 – LET MY PEOPLE GO  (The Exodus)
# ═══════════════════════════════════════════════════════════════════════════════
def build_s01():
    print("Building S01: Let My People Go…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    # ── Terrain: Egypt ──────────────────────────────────────────────────────
    fill_terrain(mm, T_DESERT)                        # base desert
    draw_river(mm, T_WATER_MED, 55, 0, 55, 119, width=8)   # Nile
    fill_terrain(mm, T_GRASS, 47, 0, 63, 119)         # fertile Nile banks
    fill_terrain(mm, T_DESERT, 0, 90, 119, 119)       # Sinai/border region
    fill_terrain(mm, T_GRASS_DRY, 80, 0, 119, 70)     # eastern desert scrub
    # Egyptian city structures in the west
    fill_terrain(mm, T_ROAD, 5, 40, 45, 80)           # city roads

    # ── Players ─────────────────────────────────────────────────────────────
    setup_player(pm, P1, CIV_ATHENIANS, "Israel",
                 food=300, wood=200, gold=100, stone=0, human=True)
    setup_player(pm, P2, CIV_ACHAEMENIDS, "Egypt",
                 food=800, wood=600, gold=500, stone=400)
    setup_player(pm, P3, CIV_ACHAEMENIDS, "Pharaoh's Guard",
                 food=600, wood=400, gold=300, stone=0)
    # P3 is always active by default

    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY, DIPL_ALLY)

    # ── Units ───────────────────────────────────────────────────────────────
    # P1 – Moses (King unit) + band of Israelites
    moses = um.add_unit(P1, U_KING,      x=65, y=60)
    um.add_unit(P1, U_VILLAGER,   x=66, y=58)
    um.add_unit(P1, U_VILLAGER,   x=67, y=60)
    um.add_unit(P1, U_VILLAGER,   x=65, y=62)
    um.add_unit(P1, U_VILLAGER,   x=68, y=59)
    um.add_unit(P1, U_MILITIA,    x=64, y=57)
    um.add_unit(P1, U_MILITIA,    x=64, y=63)
    um.add_unit(P1, U_ARCHER,     x=70, y=58)
    um.add_unit(P1, U_ARCHER,     x=70, y=62)

    # Starting building – a small shelter
    um.add_unit(P1, B_BARRACKS, x=72, y=60)

    # P2 – Egyptian city guard
    for x in range(15, 45, 6):
        um.add_unit(P2, U_WAR_CHARIOT,  x=x, y=45)
        um.add_unit(P2, U_WAR_CHARIOT,  x=x, y=75)
    um.add_unit(P2, B_TOWN_CENTER, x=20, y=60)
    um.add_unit(P2, B_CASTLE,      x=10, y=50)
    um.add_unit(P2, B_WATCH_TOWER, x=35, y=45)
    um.add_unit(P2, B_WATCH_TOWER, x=35, y=75)

    # P3 – Pursuing army (disabled at start, activated by trigger)
    guard1 = um.add_unit(P3, U_WAR_CHARIOT, x=50, y=55)
    guard2 = um.add_unit(P3, U_WAR_CHARIOT, x=50, y=60)
    guard3 = um.add_unit(P3, U_WAR_CHARIOT, x=50, y=65)
    for ref in [guard1, guard2, guard3]:
        pass  # will be frozen until trigger fires

    # Escape marker – eastern edge
    escape_tc = um.add_unit(P1, B_TOWN_CENTER, x=110, y=60)

    # ── Triggers ────────────────────────────────────────────────────────────

    # Intro text (fires on load)
    t_intro = tm.add_trigger("Intro Narration")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20,
        message=(
            "<b>Let My People Go</b>\n\n"
            "Egypt, 1446 BC. For four hundred years the children of Israel "
            "have laboured under Pharaoh's whip. The Lord has spoken to Moses "
            "from the burning bush: lead His people out of bondage.\n\n"
            "The plagues have broken Egypt's pride. Pharaoh has finally "
            "relented — but his heart will harden. You must lead your people "
            "east across the Nile and into the Sinai before his army gives chase."
        ),
        instruction_panel_position=0,
    )

    # Objective text
    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Escape Egypt"
    t_obj.description = (
        "Lead Moses and your people to the eastern encampment.\n"
        "Avoid or defeat Egyptian patrols along the way."
    )

    # Halfway story – Egypt pursues
    t_pursue = tm.add_trigger("Pharaoh Pursues")
    t_pursue.enabled = True
    t_pursue.new_condition.objects_in_area(
        quantity=1, source_player=P1,
        object_list=U_KING,
        area_x1=85, area_y1=40, area_x2=119, area_y2=80,
    )
    t_pursue.new_effect.display_instructions(
        display_time=15,
        message=(
            "Pharaoh's heart has hardened! His chariots pour out of the city "
            "in pursuit. Move quickly — reach the encampment before they surround you!"
        ),
        instruction_panel_position=0,
    )
    # Spawn pursuing chariots
    t_pursue.new_effect.create_object(
        object_list_unit_id=U_WAR_CHARIOT, source_player=P3,
        location_x=60, location_y=50,
    )
    t_pursue.new_effect.create_object(
        object_list_unit_id=U_WAR_CHARIOT, source_player=P3,
        location_x=60, location_y=60,
    )
    t_pursue.new_effect.create_object(
        object_list_unit_id=U_WAR_CHARIOT, source_player=P3,
        location_x=60, location_y=70,
    )
    t_pursue.new_effect.deactivate_trigger(trigger_id=t_pursue.trigger_id)

    # Win – Moses reaches the eastern encampment
    t_win = tm.add_trigger("Victory – Reached Sinai")
    t_win.enabled = True
    t_win.new_condition.objects_in_area(
        quantity=1, source_player=P1,
        object_list=U_KING,
        area_x1=100, area_y1=50, area_x2=119, area_y2=70,
    )
    t_win.new_effect.display_instructions(
        display_time=10,
        message=(
            "Moses leads the children of Israel out of Egypt. "
            "The first step of a long journey has begun."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    # Lose – Moses killed
    t_lose = tm.add_trigger("Defeat – Moses Slain")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(
        quantity=1, source_player=P1, object_list=U_KING,
    )
    t_lose.new_effect.display_instructions(
        display_time=10,
        message="Moses has fallen. Without their leader, the Israelites are enslaved again.",
        instruction_panel_position=0,
    )

    # ── Message manager ─────────────────────────────────────────────────────
    s.message_manager.instructions = (
        "Lead Moses (the King unit) east across the Nile to the encampment. "
        "Protect him at all costs — if he falls, all is lost."
    )
    s.message_manager.loss = "Moses has been slain. The Exodus has failed."
    s.message_manager.victory = "Israel is free! The Exodus from Egypt begins."
    s.message_manager.scouts = (
        "You begin east of the Nile with a small band of Israelites. "
        "Egyptian patrols guard the roads. Move Moses to the eastern encampment to win."
    )

    save(s, "ot_01_exodus.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 2 – THE WALLS OF JERICHO
# ═══════════════════════════════════════════════════════════════════════════════
def build_s02():
    print("Building S02: The Walls of Jericho…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    # ── Terrain ─────────────────────────────────────────────────────────────
    fill_terrain(mm, T_GRASS_DRY)                       # Canaan scrubland
    fill_terrain(mm, T_GRASS, 40, 30, 90, 90)           # fertile valley
    draw_river(mm, T_SHALLOW, 0, 60, 35, 60, width=4)   # Jordan River (west)
    fill_terrain(mm, T_DESERT, 0, 0, 30, 119)           # desert side (Sinai)
    fill_terrain(mm, T_ROCK, 85, 0, 119, 50)            # hills to east
    set_elevation_area(mm, 2, 85, 0, 119, 60)           # elevated eastern hills
    # Jericho city centre
    fill_terrain(mm, T_ROAD, 52, 48, 72, 68)

    # ── Players ─────────────────────────────────────────────────────────────
    setup_player(pm, P1, CIV_ATHENIANS, "Israel",
                 food=500, wood=400, gold=200, stone=100, human=True)
    setup_player(pm, P2, CIV_THRACIANS, "Jericho",
                 food=700, wood=500, gold=400, stone=600)
    setup_player(pm, P3, CIV_THRACIANS, "Canaan",
                 food=400, wood=300, gold=200, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY, DIPL_ALLY)

    # ── Units ───────────────────────────────────────────────────────────────
    # P1 – Israelite camp west of Jericho
    joshua = um.add_unit(P1, U_KING,    x=20, y=60)
    um.add_unit(P1, B_TOWN_CENTER,      x=15, y=58)
    um.add_unit(P1, B_BARRACKS,         x=12, y=65)
    for i in range(8):
        um.add_unit(P1, U_MILITIA,  x=18+i, y=62)
        um.add_unit(P1, U_ARCHER,   x=18+i, y=56)
    um.add_unit(P1, U_SPEARMAN, x=22, y=60)
    um.add_unit(P1, U_SPEARMAN, x=24, y=60)
    um.add_unit(P1, U_PRIEST,   x=16, y=60)   # Ark of the Covenant carrier

    # P2 – Jericho: walled city
    jericho_tc = um.add_unit(P2, B_TOWN_CENTER, x=62, y=58)
    um.add_unit(P2, B_CASTLE,       x=55, y=50)
    um.add_unit(P2, B_WATCH_TOWER,  x=50, y=50)
    um.add_unit(P2, B_WATCH_TOWER,  x=75, y=50)
    um.add_unit(P2, B_WATCH_TOWER,  x=50, y=70)
    um.add_unit(P2, B_WATCH_TOWER,  x=75, y=70)
    # Walls around Jericho
    for x in range(50, 76):
        um.add_unit(P2, B_STONE_WALL, x=x, y=48)
        um.add_unit(P2, B_STONE_WALL, x=x, y=70)
    for y in range(48, 71):
        um.add_unit(P2, B_STONE_WALL, x=50, y=y)
        um.add_unit(P2, B_STONE_WALL, x=75, y=y)
    for i in range(6):
        um.add_unit(P2, U_HOPLITE,    x=55+i*3, y=52)
        um.add_unit(P2, U_ARCHER,     x=55+i*3, y=66)
    um.add_unit(P2, U_WAR_CHARIOT, x=62, y=60)
    um.add_unit(P2, U_WAR_CHARIOT, x=58, y=60)

    # P3 – Canaanite relief force (activates later)
    um.add_unit(P3, B_TOWN_CENTER, x=100, y=55)
    for i in range(5):
        um.add_unit(P3, U_MILITIA, x=95, y=52+i*3)

    # ── Triggers ────────────────────────────────────────────────────────────
    t_intro = tm.add_trigger("Intro Narration")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20,
        message=(
            "<b>The Walls of Jericho</b>\n\n"
            "1406 BC. After forty years in the wilderness, Joshua leads Israel "
            "across the Jordan River into the Promised Land. The great walled "
            "city of Jericho stands in their path — its walls are said to be "
            "unbreakable.\n\n"
            "But God has spoken: march around the city once each day for six "
            "days, then seven times on the seventh day. When the priests blow "
            "the ram's horns, the walls shall fall."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Conquer Jericho"
    t_obj.description = (
        "Destroy the Town Center of Jericho to complete the conquest.\n"
        "Defeat the Canaanite relief army if they march to Jericho's aid."
    )

    # Day counter events
    for day in range(1, 7):
        td = tm.add_trigger(f"Day {day} Narration")
        td.enabled = (day == 1)
        td.new_condition.timer(timer=day * 90)  # 90 seconds per in-game "day"
        td.new_effect.display_instructions(
            display_time=8,
            message=f"Day {day}: The Israelites march around Jericho in silence. The defenders watch in confusion.",
            instruction_panel_position=0,
        )
        if day < 6:
            td.new_effect.deactivate_trigger(trigger_id=td.trigger_id)

    # Day 7 – walls weaken, Canaanite reinforcements arrive
    t_day7 = tm.add_trigger("Day 7 – The Shout")
    t_day7.enabled = True
    t_day7.new_condition.timer(timer=7 * 90)
    t_day7.new_effect.display_instructions(
        display_time=12,
        message=(
            "On the seventh day the priests blow the trumpets and the people shout! "
            "The walls of Jericho tremble. Now is the time to attack — CHARGE!"
        ),
        instruction_panel_position=0,
    )
    # Weaken the walls / defenders via damage
    t_day7.new_effect.damage_object(
        object_list_unit_id=B_STONE_WALL, source_player=P2,
        area_x1=48, area_y1=46, area_x2=77, area_y2=72,
        quantity=500,
    )
    t_day7.new_effect.deactivate_trigger(trigger_id=t_day7.trigger_id)

    # Win condition
    t_win = tm.add_trigger("Victory – Jericho Falls")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=jericho_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=10,
        message="Jericho has fallen! The first great victory in the Promised Land belongs to Israel.",
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    # Lose – Joshua killed
    t_lose = tm.add_trigger("Defeat – Joshua Slain")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(
        quantity=1, source_player=P1, object_list=U_KING,
    )
    t_lose.new_effect.display_instructions(
        display_time=10,
        message="Joshua has fallen. Without their commander, Israel retreats across the Jordan.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = (
        "Destroy Jericho's Town Center to win. Joshua (the King unit) must survive."
    )
    s.message_manager.victory = "Jericho has fallen! The conquest of Canaan begins."
    s.message_manager.loss = "Joshua has been slain. The assault on Jericho fails."

    save(s, "ot_02_jericho.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 3 – THE PROMISED LAND  (Conquest of Canaan)
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

    setup_player(pm, P1, CIV_ATHENIANS,  "Israel",
                 food=600, wood=500, gold=300, stone=200, human=True)
    setup_player(pm, P2, CIV_THRACIANS,  "Hazor",
                 food=700, wood=500, gold=400, stone=300)
    setup_player(pm, P3, CIV_THRACIANS,  "Lachish",
                 food=600, wood=400, gold=300, stone=200)
    setup_player(pm, P4, CIV_ACHAEMENIDS,"Jerusalem",
                 food=800, wood=500, gold=500, stone=400)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P4, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY, DIPL_ALLY)
    set_diplomacy(pm, P2, P4, DIPL_ALLY, DIPL_ALLY)
    set_diplomacy(pm, P3, P4, DIPL_ALLY, DIPL_ALLY)

    # P1 base
    um.add_unit(P1, B_TOWN_CENTER, x=15, y=72)
    um.add_unit(P1, B_BARRACKS,    x=12, y=78)
    um.add_unit(P1, U_KING,        x=17, y=72)
    for i in range(6): um.add_unit(P1, U_MILITIA,  x=10+i*2, y=68)
    for i in range(4): um.add_unit(P1, U_ARCHER,   x=10+i*2, y=76)
    for i in range(3): um.add_unit(P1, U_VILLAGER, x=20+i,   y=74)

    # Hazor (north)
    hazor_tc = um.add_unit(P2, B_TOWN_CENTER, x=70, y=25)
    um.add_unit(P2, B_CASTLE,      x=65, y=20)
    um.add_unit(P2, B_WATCH_TOWER, x=80, y=20)
    for i in range(6): um.add_unit(P2, U_WAR_CHARIOT, x=72+i*2, y=30)
    for i in range(5): um.add_unit(P2, U_HOPLITE,     x=68+i*2, y=32)

    # Lachish (south-west)
    lachish_tc = um.add_unit(P3, B_TOWN_CENTER, x=40, y=110)
    um.add_unit(P3, B_CASTLE,      x=35, y=105)
    for i in range(5): um.add_unit(P3, U_MILITIA,  x=38+i*2, y=108)
    for i in range(4): um.add_unit(P3, U_ARCHER,   x=38+i*2, y=115)

    # Jerusalem (centre-east – hardest)
    jer_tc = um.add_unit(P4, B_TOWN_CENTER, x=95, y=72)
    um.add_unit(P4, B_CASTLE,      x=90, y=65)
    um.add_unit(P4, B_CASTLE,      x=90, y=80)
    um.add_unit(P4, B_WATCH_TOWER, x=100, y=65)
    um.add_unit(P4, B_WATCH_TOWER, x=100, y=80)
    for i in range(8): um.add_unit(P4, U_HOPLITE,     x=93+i*2, y=72)
    for i in range(4): um.add_unit(P4, U_WAR_CHARIOT, x=93+i*2, y=68)

    # ── Triggers ────────────────────────────────────────────────────────────
    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20,
        message=(
            "<b>The Promised Land</b>\n\n"
            "The conquest of Canaan has begun. Three great city-kingdoms "
            "control the land: Hazor in the north, Lachish in the south-west, "
            "and the mighty Jerusalem at the heart of the hills.\n\n"
            "Joshua must lead Israel to destroy all three before they can "
            "unite and drive Israel back across the Jordan."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Conquer Canaan"
    t_obj.description = (
        "Destroy the Town Centers of Hazor, Lachish, and Jerusalem.\n"
        "Protect Joshua (the King unit) throughout the campaign."
    )

    # Track city captures with progress messages
    for tc, city, msg in [
        (hazor_tc, "Hazor", "Hazor burns! The northern Canaanite coalition is shattered."),
        (lachish_tc, "Lachish", "Lachish has fallen! The southern road lies open."),
        (jer_tc, "Jerusalem", "Jerusalem is taken! The hill country belongs to Israel."),
    ]:
        t = tm.add_trigger(f"{city} Falls")
        t.enabled = True
        t.new_condition.destroy_object(unit_object=tc.reference_id)
        t.new_effect.display_instructions(display_time=10, message=msg,
                                          instruction_panel_position=0)
        t.new_effect.deactivate_trigger(trigger_id=t.trigger_id)

    # Win: all three TCs destroyed
    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=hazor_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=lachish_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=jer_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12,
        message="The Promised Land is Israel's! The twelve tribes claim their inheritance.",
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=10,
        message="Joshua has fallen. The conquest of Canaan has stalled.",
        instruction_panel_position=0,
    )

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

    # Jezreel Valley – flat with hills on edges
    fill_terrain(mm, T_GRASS)
    fill_terrain(mm, T_GRASS_DRY, 0, 0, 119, 30)
    fill_terrain(mm, T_GRASS_DRY, 0, 90, 119, 119)
    set_elevation_area(mm, 3, 0, 0, 20, 119)     # western hills (Carmel)
    set_elevation_area(mm, 2, 100, 0, 119, 119)  # eastern hills (Tabor)
    draw_river(mm, T_SHALLOW, 30, 50, 90, 70, width=3)  # Kishon river

    setup_player(pm, P1, CIV_ATHENIANS,  "Israel",
                 food=400, wood=300, gold=200, stone=0, human=True)
    setup_player(pm, P2, CIV_THRACIANS,  "Sisera's Army",
                 food=900, wood=600, gold=400, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)

    # P1 – Barak's army on Mount Tabor (east hills)
    deborah = um.add_unit(P1, U_KING,    x=105, y=60)
    barak   = um.add_unit(P1, U_PRIEST,  x=103, y=62)
    um.add_unit(P1, B_BARRACKS, x=108, y=60)
    for i in range(10): um.add_unit(P1, U_MILITIA,  x=100, y=50+i*3)
    for i in range(6):  um.add_unit(P1, U_ARCHER,   x=102, y=52+i*3)
    for i in range(4):  um.add_unit(P1, U_SPEARMAN, x=98,  y=54+i*3)

    # P2 – Sisera: iron chariots flood the valley
    sisera_flag = um.add_unit(P2, B_TOWN_CENTER, x=30, y=60)
    for row in range(4):
        for col in range(8):
            um.add_unit(P2, U_WAR_CHARIOT,  x=20+col*6, y=45+row*10)
    for i in range(12): um.add_unit(P2, U_HOPLITE,  x=15+i*3, y=70)
    for i in range(8):  um.add_unit(P2, U_ARCHER,   x=15+i*4, y=40)
    um.add_unit(P2, B_CASTLE,      x=15, y=60)
    um.add_unit(P2, B_WATCH_TOWER, x=25, y=45)
    um.add_unit(P2, B_WATCH_TOWER, x=25, y=75)

    # ── Triggers ────────────────────────────────────────────────────────────
    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20,
        message=(
            "<b>Deborah's Sword</b>\n\n"
            "1125 BC. For twenty years the Canaanite king Jabin has "
            "oppressed Israel with nine hundred iron chariots under his "
            "commander Sisera. The prophetess Deborah summons Barak from "
            "Mount Tabor: 'Go! The Lord gives Sisera into your hands today!'\n\n"
            "A storm is coming. The river Kishon will flood and bog down "
            "Sisera's chariots. Strike now from the high ground!"
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Defeat Sisera"
    t_obj.description = "Destroy Sisera's camp (Town Center) in the valley below."

    # Storm event – river floods, chariots are weakened
    t_storm = tm.add_trigger("The Storm Breaks")
    t_storm.enabled = True
    t_storm.new_condition.timer(timer=120)
    t_storm.new_effect.display_instructions(
        display_time=10,
        message=(
            "The heavens open! Rain pours into the valley. The Kishon floods — "
            "Sisera's iron chariots are mired in mud. Their advantage is lost. CHARGE!"
        ),
        instruction_panel_position=0,
    )
    # Damage the chariots to simulate bogging
    t_storm.new_effect.damage_object(
        object_list_unit_id=U_WAR_CHARIOT, source_player=P2,
        area_x1=0, area_y1=0, area_x2=119, area_y2=119, quantity=60,
    )
    t_storm.new_effect.deactivate_trigger(trigger_id=t_storm.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=sisera_flag.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12,
        message=(
            "Sisera's army is routed! The iron chariot host lies broken in "
            "the mud of the Kishon. Israel is free from Canaanite oppression."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=10, message="Deborah has fallen. Sisera's grip on Israel tightens.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = "Charge down from Mount Tabor. Destroy Sisera's camp."
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
    set_elevation_area(mm, 3, 0, 0, 20, 60)   # Gideon's hill
    draw_river(mm, T_SHALLOW, 40, 0, 40, 80, width=3)  # Spring of Harod

    setup_player(pm, P1, CIV_ATHENIANS, "Gideon",
                 food=200, wood=100, gold=100, stone=0, human=True)
    setup_player(pm, P2, CIV_THRACIANS, "Midian",
                 food=1200, wood=800, gold=600, stone=0)
    setup_player(pm, P3, CIV_THRACIANS, "Amalek",
                 food=600, wood=400, gold=300, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY, DIPL_ALLY)

    # P1 – Gideon with exactly 300 men (represented as ~20 units)
    gideon = um.add_unit(P1, U_KING, x=10, y=30)
    for i in range(8):  um.add_unit(P1, U_MILITIA,  x=8+i*2,  y=25)
    for i in range(7):  um.add_unit(P1, U_ARCHER,   x=8+i*2,  y=32)
    for i in range(5):  um.add_unit(P1, U_SLINGER,  x=10+i*2, y=38)

    # P2/P3 – Vast Midianite camp
    midian_tc = um.add_unit(P2, B_TOWN_CENTER, x=70, y=50)
    um.add_unit(P2, B_CASTLE,  x=65, y=45)
    um.add_unit(P3, B_TOWN_CENTER, x=90, y=70)
    for col in range(10):
        for row in range(5):
            um.add_unit(P2, U_MILITIA,   x=50+col*5, y=30+row*6)
    for i in range(8):  um.add_unit(P2, U_WAR_CHARIOT, x=55+i*4, y=55)
    for i in range(6):  um.add_unit(P3, U_MILITIA,     x=88+i,   y=68)
    for i in range(4):  um.add_unit(P3, U_ARCHER,      x=88+i,   y=74)

    # ── Triggers ────────────────────────────────────────────────────────────
    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20,
        message=(
            "<b>Gideon's 300</b>\n\n"
            "1169 BC. The Midianites pour across the Jordan like locusts, "
            "stripping Israel bare. God chooses Gideon — the least of his "
            "family — to lead. But first, the army must be reduced.\n\n"
            "'You have too many men. Tell those who are afraid to go home.' "
            "Then: 'Still too many. Watch how they drink — keep only those "
            "who lap water like dogs.' Three hundred remain.\n\n"
            "By night, armed with torches and ram's horns, the 300 will "
            "descend on the Midianite camp and shatter it with confusion."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Rout Midian"
    t_obj.description = (
        "Destroy both Midianite camps (Town Centers).\n"
        "You are vastly outnumbered — use speed and cunning."
    )

    # Night raid – after 60 seconds the enemy turns on itself
    t_night = tm.add_trigger("Night Raid Confusion")
    t_night.enabled = True
    t_night.new_condition.timer(timer=90)
    t_night.new_effect.display_instructions(
        display_time=12,
        message=(
            "The trumpets blare, the torches blaze, the shout goes up: "
            "'A sword for the Lord and for Gideon!' The Midianites wake in "
            "blind panic — they attack each other in the darkness!"
        ),
        instruction_panel_position=0,
    )
    # Midian attacks Amalek (simulate friendly fire confusion)
    t_night.new_effect.change_diplomacy(
        source_player=P2, target_player=P3, diplomacy=DIPL_ENEMY
    )
    t_night.new_effect.change_diplomacy(
        source_player=P3, target_player=P2, diplomacy=DIPL_ENEMY
    )
    t_night.new_effect.deactivate_trigger(trigger_id=t_night.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=midian_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12,
        message=(
            "Midian flees across the Jordan! With 300 men and the hand of "
            "God, Gideon has delivered Israel. The land has rest for forty years."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=10, message="Gideon has fallen. Midian's yoke remains on Israel.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = "You are outnumbered 400 to 1. Wait for the night raid trigger, then strike both camps."
    s.message_manager.victory = "Midian is routed by 300 faithful men!"
    s.message_manager.loss = "Gideon has been slain."
    save(s, "ot_05_gideon.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 6 – THE FIRST KING
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

    setup_player(pm, P1, CIV_ATHENIANS,  "King Saul",
                 food=500, wood=400, gold=300, stone=100, human=True)
    setup_player(pm, P2, CIV_MACEDONIANS, "Philistia",
                 food=900, wood=600, gold=500, stone=200)
    setup_player(pm, P3, CIV_THRACIANS,   "Amalek",
                 food=500, wood=300, gold=200, stone=0)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_NEUTRAL, DIPL_NEUTRAL)

    # P1 – Saul's base at Gibeah
    saul = um.add_unit(P1, U_KING,        x=20, y=50)
    um.add_unit(P1, B_TOWN_CENTER,         x=18, y=48)
    um.add_unit(P1, B_BARRACKS,            x=15, y=55)
    for i in range(8):  um.add_unit(P1, U_MILITIA,      x=15+i*2, y=44)
    for i in range(6):  um.add_unit(P1, U_SPEARMAN,     x=15+i*2, y=52)
    for i in range(4):  um.add_unit(P1, U_ARCHER,       x=15+i*3, y=58)
    for i in range(3):  um.add_unit(P1, U_VILLAGER,     x=22+i,   y=50)

    # P2 – Philistine coastal city
    phil_tc = um.add_unit(P2, B_TOWN_CENTER, x=90, y=60)
    um.add_unit(P2, B_CASTLE,      x=85, y=55)
    um.add_unit(P2, B_CASTLE,      x=85, y=65)
    for i in range(8):  um.add_unit(P2, U_HOPLITE,     x=80+i*2, y=60)
    for i in range(5):  um.add_unit(P2, U_WAR_CHARIOT, x=78+i*3, y=55)
    for i in range(4):  um.add_unit(P2, U_ARCHER,      x=80+i*2, y=66)

    # P3 – Amalekite raiders (south)
    amalek_tc = um.add_unit(P3, B_TOWN_CENTER, x=60, y=105)
    for i in range(6):  um.add_unit(P3, U_MILITIA, x=55+i*2, y=100)
    for i in range(4):  um.add_unit(P3, U_ARCHER,  x=55+i*2, y=108)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20,
        message=(
            "<b>The First King</b>\n\n"
            "1051 BC. The elders of Israel demand a king 'like the other nations.' "
            "The prophet Samuel reluctantly anoints Saul of Benjamin — tall, "
            "handsome, head-and-shoulders above every man.\n\n"
            "But a king must prove himself. The Philistines press from the coast "
            "with iron weapons Israel cannot match. The Amalekites raid from the "
            "south. Unite the tribes and drive back both threats."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Establish the Kingdom"
    t_obj.description = (
        "Destroy the Philistine stronghold (Town Center) and the Amalekite camp.\n"
        "King Saul must survive."
    )

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=phil_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=amalek_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12,
        message=(
            "The kingdom is secured! Saul reigns over a united Israel. "
            "But the shadow of a young shepherd named David is already falling."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=10, message="Saul has fallen. Israel has no king.",
        instruction_panel_position=0,
    )

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
    set_elevation_area(mm, 3, 55, 50, 75, 70)  # Jerusalem hill
    fill_terrain(mm, T_ROAD, 55, 50, 75, 70)
    draw_river(mm, T_SHALLOW, 0, 60, 40, 60, width=4)
    fill_terrain(mm, T_DESERT, 95, 0, 119, 119)

    setup_player(pm, P1, CIV_ATHENIANS,  "King David",
                 food=600, wood=500, gold=400, stone=200, human=True)
    setup_player(pm, P2, CIV_MACEDONIANS, "Philistia",
                 food=800, wood=600, gold=500, stone=300)
    setup_player(pm, P3, CIV_THRACIANS,   "Jebusite Jerusalem",
                 food=600, wood=400, gold=400, stone=500)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_NEUTRAL, DIPL_NEUTRAL)

    # P1 – David at Hebron
    david = um.add_unit(P1, U_KING, x=15, y=60)
    um.add_unit(P1, B_TOWN_CENTER,   x=13, y=58)
    um.add_unit(P1, B_BARRACKS,      x=10, y=64)
    um.add_unit(P1, B_ARCHERY_RANGE, x=10, y=54)
    for i in range(10): um.add_unit(P1, U_MILITIA,  x=10+i*2, y=55)
    for i in range(6):  um.add_unit(P1, U_ARCHER,   x=10+i*2, y=63)
    for i in range(4):  um.add_unit(P1, U_SPEARMAN, x=10+i*2, y=67)
    for i in range(4):  um.add_unit(P1, U_VILLAGER, x=18+i,   y=60)

    # P2 – Philistines pushing east
    phil_tc = um.add_unit(P2, B_TOWN_CENTER, x=100, y=40)
    um.add_unit(P2, B_CASTLE,      x=95, y=35)
    for i in range(8):  um.add_unit(P2, U_HOPLITE,     x=90+i*2, y=45)
    for i in range(5):  um.add_unit(P2, U_WAR_CHARIOT, x=90+i*3, y=38)

    # P3 – Jebusites hold Jerusalem
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
    for i in range(8):  um.add_unit(P3, U_HOPLITE, x=60+i, y=58)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=20,
        message=(
            "<b>The Shepherd King</b>\n\n"
            "1010 BC. After years in the wilderness evading Saul's jealousy, "
            "David is anointed king at Hebron. All Israel rallies to him.\n\n"
            "Two tasks stand before the new king: drive the Philistines from "
            "the interior, and capture the Jebusite fortress of Jerusalem — "
            "the City of David, to become the eternal capital of his kingdom."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Unite the Kingdom"
    t_obj.description = (
        "Defeat the Philistines and capture Jerusalem (destroy both Town Centers).\n"
        "David must survive."
    )

    t_jer_falls = tm.add_trigger("Jerusalem Captured")
    t_jer_falls.enabled = True
    t_jer_falls.new_condition.destroy_object(unit_object=jer_tc.reference_id)
    t_jer_falls.new_effect.display_instructions(
        display_time=10,
        message="Jerusalem is taken! David makes it the City of David, capital of a united Israel.",
        instruction_panel_position=0,
    )
    t_jer_falls.new_effect.deactivate_trigger(trigger_id=t_jer_falls.trigger_id)

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=phil_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=jer_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12,
        message=(
            "David reigns from Jerusalem over all Israel and Judah. "
            "His kingdom stretches from Dan to Beersheba. "
            "A man after God's own heart."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=10, message="David has fallen in battle.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = "Destroy both Town Centers. Build up at Hebron before assaulting Jerusalem."
    s.message_manager.victory = "Jerusalem is the City of David! Israel is united."
    s.message_manager.loss = "The shepherd king has fallen."
    save(s, "ot_07_shepherd_king.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 8 – SOLOMON'S TEMPLE  (Builder scenario)
# ═══════════════════════════════════════════════════════════════════════════════
def build_s08():
    print("Building S08: Solomon's Temple…")
    s = new_scenario(MAP_MEDIUM)
    mm, um, tm, pm = s.map_manager, s.unit_manager, s.trigger_manager, s.player_manager

    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_GRASS, 20, 20, 100, 100)
    fill_terrain(mm, T_ROAD, 50, 48, 72, 72)  # Temple Mount platform
    set_elevation_area(mm, 3, 48, 46, 74, 74)
    fill_terrain(mm, T_DESERT, 0, 0, 20, 119)
    fill_terrain(mm, T_WATER_MED, 90, 0, 119, 50)   # Mediterranean (Tyre trade)
    draw_river(mm, T_SHALLOW, 90, 0, 90, 60, width=4)

    setup_player(pm, P1, CIV_ATHENIANS, "King Solomon",
                 food=800, wood=600, gold=500, stone=500, human=True)
    setup_player(pm, P2, CIV_ATHENIANS, "Tyre (Ally)",
                 food=500, wood=800, gold=400, stone=200, active=True)
    # Tyre is ally – sends tribute over time
    set_diplomacy(pm, P1, P2, DIPL_ALLY, DIPL_ALLY)

    # P1 – Jerusalem
    um.add_unit(P1, B_TOWN_CENTER, x=60, y=60)
    um.add_unit(P1, B_MARKET,      x=55, y=70)
    um.add_unit(P1, B_BARRACKS,    x=55, y=50)
    um.add_unit(P1, U_KING,        x=62, y=60)
    for i in range(6): um.add_unit(P1, U_VILLAGER, x=64+i, y=60)
    for i in range(4): um.add_unit(P1, U_VILLAGER, x=64+i, y=55)

    # P2 – Tyre (ally port on the coast)
    um.add_unit(P2, B_TOWN_CENTER, x=100, y=25)
    um.add_unit(P2, B_MARKET,      x=105, y=30)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22,
        message=(
            "<b>Solomon's Temple</b>\n\n"
            "970 BC. David is gone. His son Solomon inherits a kingdom at "
            "peace, vast wealth, and a divine commission: build the Temple "
            "in Jerusalem that his father's wars would not allow.\n\n"
            "Hiram, King of Tyre, sends cedar wood and craftsmen. "
            "Thirty thousand men are conscripted to work in Lebanon. "
            "The project will take seven years.\n\n"
            "Gather resources and build the Temple (Wonder) before the "
            "time limit expires. A rival power grows in the east — do not "
            "wait too long."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Build the Temple"
    t_obj.description = "Construct a Wonder on the Temple Mount before time runs out."

    # Tyre tribute: periodically sends resources
    for i, delay in enumerate([60, 150, 240, 360]):
        tt = tm.add_trigger(f"Tyre Tribute {i+1}")
        tt.enabled = True
        tt.new_condition.timer(timer=delay)
        tt.new_effect.tribute(
            quantity=200, tribute_list=1,    # wood
            source_player=P2, target_player=P1,
        )
        tt.new_effect.tribute(
            quantity=150, tribute_list=3,    # stone
            source_player=P2, target_player=P1,
        )
        tt.new_effect.display_instructions(
            display_time=6,
            message=f"A Tyrian caravan arrives bearing cedar and stone for the Temple.",
            instruction_panel_position=0,
        )
        tt.new_effect.deactivate_trigger(trigger_id=tt.trigger_id)

    # Deadline warning
    t_warn = tm.add_trigger("Deadline Warning")
    t_warn.enabled = True
    t_warn.new_condition.timer(timer=420)
    t_warn.new_effect.display_instructions(
        display_time=10,
        message="Seven years have nearly passed. If the Temple is not raised soon, the moment will be lost!",
        instruction_panel_position=0,
    )
    t_warn.new_effect.deactivate_trigger(trigger_id=t_warn.trigger_id)

    # Win: Wonder built
    t_win = tm.add_trigger("Victory – Temple Complete")
    t_win.enabled = True
    t_win.new_condition.own_objects(
        quantity=1, source_player=P1, object_list=B_WONDER,
    )
    t_win.new_effect.display_instructions(
        display_time=15,
        message=(
            "The Temple is complete! The Ark of the Covenant is carried "
            "into the Holy of Holies. The glory of the Lord fills the Temple. "
            "Solomon's prayer rises: 'May your eyes be open toward this Temple night and day.'"
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    # Lose: time runs out (14 minutes ≈ 840s)
    t_time_lose = tm.add_trigger("Time's Up")
    t_time_lose.enabled = True
    t_time_lose.new_condition.timer(timer=840)
    t_time_lose.new_condition.own_fewer_objects(
        quantity=1, source_player=P1, object_list=B_WONDER,
    )
    t_time_lose.new_effect.display_instructions(
        display_time=10,
        message="The moment has passed. Solomon's glory fades without the Temple.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = "Build a Wonder (the Temple) before the 14-minute deadline. Use Tyre's tribute shipments wisely."
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
    draw_river(mm, T_SHALLOW, 55, 0, 55, 119, width=4)  # the divide
    fill_terrain(mm, T_DESERT, 95, 0, 119, 119)
    set_elevation_area(mm, 2, 40, 40, 70, 80)

    setup_player(pm, P1, CIV_ATHENIANS,  "Judah",
                 food=500, wood=400, gold=300, stone=200, human=True)
    setup_player(pm, P2, CIV_ATHENIANS,  "Israel (North)",
                 food=600, wood=400, gold=300, stone=100)
    setup_player(pm, P3, CIV_ACHAEMENIDS,"Egypt (Shishak)",
                 food=800, wood=500, gold=600, stone=200)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY, DIPL_ALLY)  # Jeroboam sheltered in Egypt

    # P1 – Judah/Jerusalem (south)
    rehoboam = um.add_unit(P1, U_KING,       x=50, y=80)
    um.add_unit(P1, B_TOWN_CENTER,            x=48, y=78)
    um.add_unit(P1, B_CASTLE,                 x=43, y=75)
    um.add_unit(P1, B_WATCH_TOWER,            x=55, y=75)
    for y in range(73, 89):
        um.add_unit(P1, B_STONE_WALL, x=43, y=y)
        um.add_unit(P1, B_STONE_WALL, x=58, y=y)
    for i in range(8):  um.add_unit(P1, U_HOPLITE,  x=44+i*2, y=76)
    for i in range(5):  um.add_unit(P1, U_ARCHER,   x=44+i*2, y=82)
    for i in range(3):  um.add_unit(P1, U_VILLAGER, x=50+i,   y=80)

    # P2 – Israel/Jeroboam (north)
    jeroboam_tc = um.add_unit(P2, B_TOWN_CENTER, x=50, y=35)
    um.add_unit(P2, B_CASTLE,      x=45, y=30)
    for i in range(8): um.add_unit(P2, U_MILITIA,  x=45+i*2, y=40)
    for i in range(5): um.add_unit(P2, U_ARCHER,   x=45+i*2, y=35)
    for i in range(3): um.add_unit(P2, U_WAR_CHARIOT, x=48+i*2, y=30)

    # P3 – Shishak's Egyptian invasion (east)
    shishak_tc = um.add_unit(P3, B_TOWN_CENTER, x=105, y=60)
    for i in range(10): um.add_unit(P3, U_WAR_CHARIOT, x=100+i, y=55)
    for i in range(8):  um.add_unit(P3, U_HOPLITE,     x=98+i*2, y=62)
    for i in range(6):  um.add_unit(P3, U_ARCHER,      x=98+i*2, y=68)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22,
        message=(
            "<b>A Kingdom Divided</b>\n\n"
            "930 BC. Solomon is dead. His son Rehoboam threatens heavier "
            "taxes — ten tribes revolt under Jeroboam, forming the northern "
            "Kingdom of Israel. Only Judah and Benjamin remain loyal.\n\n"
            "Now Shishak of Egypt invades, drawn by the chaos. Israel and "
            "Egypt press on Jerusalem from north and east. "
            "Rehoboam must defend the holy city with what he has left."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Defend Jerusalem"
    t_obj.description = (
        "Survive the invasions from Israel (north) and Egypt (east).\n"
        "Destroy both enemy Town Centers. Rehoboam must survive."
    )

    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=jeroboam_tc.reference_id)
    t_win.new_condition.destroy_object(unit_object=shishak_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12,
        message=(
            "Jerusalem stands! Though the kingdom is forever split, "
            "Judah endures — the line of David continues."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=10, message="Rehoboam has fallen. Jerusalem is lost.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = "Defend Jerusalem against enemies from two directions. Destroy both Town Centers."
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

    # Jerusalem as a fortified hill city
    fill_terrain(mm, T_GRASS_DRY)
    fill_terrain(mm, T_DESERT, 70, 0, 119, 119)
    fill_terrain(mm, T_ROAD, 30, 40, 60, 80)
    set_elevation_area(mm, 4, 25, 38, 65, 82)  # Jerusalem on the hill
    fill_terrain(mm, T_GRASS, 0, 0, 70, 119)

    setup_player(pm, P1, CIV_ATHENIANS,  "Judah",
                 food=600, wood=500, gold=400, stone=600, human=True)
    setup_player(pm, P2, CIV_ACHAEMENIDS,"Assyria",
                 food=1500, wood=800, gold=700, stone=300)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)

    # P1 – Hezekiah's Jerusalem, heavily fortified
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

    # P2 – Sennacherib's vast Assyrian host
    sennacherib_tc = um.add_unit(P2, B_TOWN_CENTER, x=95, y=60)
    um.add_unit(P2, B_CASTLE,  x=90, y=50)
    um.add_unit(P2, B_CASTLE,  x=90, y=70)
    for i in range(15): um.add_unit(P2, U_HOPLITE,     x=70+i*2, y=50)
    for i in range(15): um.add_unit(P2, U_HOPLITE,     x=70+i*2, y=70)
    for i in range(10): um.add_unit(P2, U_WAR_CHARIOT, x=75+i*3, y=60)
    for i in range(10): um.add_unit(P2, U_ARCHER,      x=72+i*2, y=45)
    for i in range(10): um.add_unit(P2, U_ARCHER,      x=72+i*2, y=75)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22,
        message=(
            "<b>Hezekiah's Wall</b>\n\n"
            "701 BC. Sennacherib, King of Assyria, has already destroyed "
            "the northern kingdom of Israel. Now 185,000 Assyrian soldiers "
            "surround Jerusalem. His envoy mocks: 'Do not let your God deceive "
            "you. Has any god delivered his nation from my hand?'\n\n"
            "Hezekiah strengthens the walls, blocks the water supply outside "
            "the city, and prays. Hold Jerusalem until the hand of God moves."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Hold Jerusalem"
    t_obj.description = (
        "Defend Jerusalem's walls for 10 minutes.\n"
        "Then the Angel of the Lord will strike the Assyrian camp."
    )

    # The Angel strikes – after 10 minutes, Assyrian army is devastated
    t_angel = tm.add_trigger("The Angel of the Lord")
    t_angel.enabled = True
    t_angel.new_condition.timer(timer=600)
    t_angel.new_effect.display_instructions(
        display_time=15,
        message=(
            "In the night the Angel of the Lord goes out and strikes 185,000 "
            "men in the Assyrian camp. When morning comes, there are only corpses. "
            "Sennacherib breaks camp and withdraws to Nineveh."
        ),
        instruction_panel_position=0,
    )
    # Kill a massive portion of the Assyrian army
    t_angel.new_effect.kill_object(
        object_list_unit_id=U_HOPLITE, source_player=P2,
        area_x1=0, area_y1=0, area_x2=119, area_y2=119,
        max_units_affected=200,
    )
    t_angel.new_effect.kill_object(
        object_list_unit_id=U_WAR_CHARIOT, source_player=P2,
        area_x1=0, area_y1=0, area_x2=119, area_y2=119,
        max_units_affected=50,
    )
    t_angel.new_effect.kill_object(
        object_list_unit_id=U_ARCHER, source_player=P2,
        area_x1=0, area_y1=0, area_x2=119, area_y2=119,
        max_units_affected=100,
    )
    t_angel.new_effect.deactivate_trigger(trigger_id=t_angel.trigger_id)

    # Win – after angel strikes, finish off remainder
    t_win = tm.add_trigger("Victory")
    t_win.enabled = True
    t_win.new_condition.destroy_object(unit_object=sennacherib_tc.reference_id)
    t_win.new_effect.display_instructions(
        display_time=12,
        message=(
            "The Assyrian siege is broken! Jerusalem alone among all the "
            "cities of Judah survives. Hezekiah's faith has saved the city."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=10, message="Hezekiah has fallen. Jerusalem is taken by Assyria.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = "Survive 10 minutes. After the Angel strikes, destroy the Assyrian camp to win."
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

    setup_player(pm, P1, CIV_ATHENIANS,  "Judah",
                 food=400, wood=300, gold=200, stone=300, human=True)
    setup_player(pm, P2, CIV_ACHAEMENIDS,"Babylon",
                 food=2000, wood=1000, gold=800, stone=400)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)

    # P1 – weakened Jerusalem
    zedekiah = um.add_unit(P1, U_KING, x=38, y=60)
    um.add_unit(P1, B_TOWN_CENTER,      x=36, y=58)
    um.add_unit(P1, B_CASTLE,           x=30, y=52)
    um.add_unit(P1, B_MONASTERY,        x=40, y=65)   # Temple
    for x in range(22, 56):
        um.add_unit(P1, B_STONE_WALL, x=x, y=40)
        um.add_unit(P1, B_STONE_WALL, x=x, y=78)
    for y in range(40, 79):
        um.add_unit(P1, B_STONE_WALL, x=22, y=y)
        um.add_unit(P1, B_STONE_WALL, x=55, y=y)
    for i in range(8): um.add_unit(P1, U_HOPLITE,  x=25+i*2, y=44)
    for i in range(6): um.add_unit(P1, U_ARCHER,   x=25+i*3, y=72)
    for i in range(2): um.add_unit(P1, U_VILLAGER, x=38+i,   y=60)
    # Sacred relic (Ark) – must escape
    ark = um.add_unit(P1, U_MONK, x=40, y=60)

    # P2 – Nebuchadnezzar's massive siege force
    nebuc_tc = um.add_unit(P2, B_TOWN_CENTER, x=100, y=60)
    um.add_unit(P2, B_CASTLE,  x=95, y=50)
    um.add_unit(P2, B_CASTLE,  x=95, y=70)
    for i in range(20): um.add_unit(P2, U_HOPLITE,     x=65+i*2, y=50)
    for i in range(20): um.add_unit(P2, U_HOPLITE,     x=65+i*2, y=70)
    for i in range(12): um.add_unit(P2, U_WAR_CHARIOT, x=70+i*3, y=60)
    for i in range(12): um.add_unit(P2, U_ARCHER,      x=67+i*2, y=44)
    for i in range(12): um.add_unit(P2, U_ARCHER,      x=67+i*2, y=76)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=22,
        message=(
            "<b>The Fall of Jerusalem</b>\n\n"
            "586 BC. Nebuchadnezzar of Babylon has besieged Jerusalem for "
            "eighteen months. The city starves. The prophet Jeremiah weeps: "
            "'Is it nothing to you, all who pass by? Behold and see if there "
            "is any sorrow like my sorrow.'\n\n"
            "The walls cannot hold forever. Your task: survive the siege "
            "as long as possible, then escape south with the Ark of the "
            "Covenant (the Monk) before Babylon completes its conquest."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Save the Ark"
    t_obj.description = (
        "Escort the Monk (carrying the sacred scrolls) to the southern edge of the map.\n"
        "Survive as long as you can — but the city will fall."
    )

    # Walls breached after 5 minutes
    t_breach = tm.add_trigger("Walls Breached")
    t_breach.enabled = True
    t_breach.new_condition.timer(timer=300)
    t_breach.new_effect.display_instructions(
        display_time=12,
        message=(
            "The wall is breached! Babylonian soldiers pour into the city. "
            "The Temple is burning. Escape now with the sacred scrolls!"
        ),
        instruction_panel_position=0,
    )
    t_breach.new_effect.kill_object(
        object_list_unit_id=B_STONE_WALL, source_player=P1,
        area_x1=0, area_y1=0, area_x2=119, area_y2=119,
        max_units_affected=30,
    )
    # Send Babylonians flooding in
    for _ in range(5):
        t_breach.new_effect.create_object(
            object_list_unit_id=U_HOPLITE, source_player=P2,
            location_x=30, location_y=60,
        )
    t_breach.new_effect.deactivate_trigger(trigger_id=t_breach.trigger_id)

    # Win – Monk escapes south
    t_win = tm.add_trigger("Victory – The Ark Escapes")
    t_win.enabled = True
    t_win.new_condition.objects_in_area(
        quantity=1, source_player=P1,
        object_list=U_MONK,
        area_x1=0, area_y1=100, area_x2=70, area_y2=119,
    )
    t_win.new_effect.display_instructions(
        display_time=15,
        message=(
            "Jerusalem has fallen. The Temple lies in ashes. "
            "But the sacred scrolls and the remnant of Israel escape into exile. "
            "By the rivers of Babylon they will weep — but they will return."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat – All Lost")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_MONK)
    t_lose.new_effect.display_instructions(
        display_time=10,
        message="The sacred scrolls are lost to Babylon. The covenant is forgotten.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = "Get the Monk to the southern edge of the map. Survive the siege until you can escape."
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
    set_elevation_area(mm, 3, 0, 0, 50, 30)   # Judean hills guerrilla start
    fill_terrain(mm, T_ROAD, 70, 55, 90, 75)  # Temple Mount (occupied)
    set_elevation_area(mm, 2, 65, 50, 95, 80)
    fill_terrain(mm, T_DESERT, 100, 0, 143, 143)

    setup_player(pm, P1, CIV_ATHENIANS,  "Maccabees",
                 food=300, wood=200, gold=100, stone=0, human=True)
    setup_player(pm, P2, CIV_MACEDONIANS,"Seleucid Empire",
                 food=2000, wood=1200, gold=900, stone=500)
    setup_player(pm, P3, CIV_MACEDONIANS,"Seleucid Garrison",
                 food=600, wood=400, gold=300, stone=200)
    set_diplomacy(pm, P1, P2, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P1, P3, DIPL_ENEMY, DIPL_ENEMY)
    set_diplomacy(pm, P2, P3, DIPL_ALLY, DIPL_ALLY)

    # P1 – Maccabees in the hill country: small guerrilla force
    judas = um.add_unit(P1, U_KING,     x=20, y=15)
    um.add_unit(P1, B_BARRACKS,          x=18, y=12)
    for i in range(5):  um.add_unit(P1, U_MILITIA,  x=15+i*2, y=10)
    for i in range(5):  um.add_unit(P1, U_ARCHER,   x=15+i*2, y=18)
    for i in range(3):  um.add_unit(P1, U_SLINGER,  x=18+i*2, y=24)

    # P2 – Seleucid main army (east)
    seleucid_tc = um.add_unit(P2, B_TOWN_CENTER, x=120, y=70)
    um.add_unit(P2, B_CASTLE,  x=115, y=60)
    um.add_unit(P2, B_CASTLE,  x=115, y=80)
    for i in range(15): um.add_unit(P2, U_ELITE_HOPLITE,     x=100+i*2, y=60)
    for i in range(15): um.add_unit(P2, U_ELITE_HOPLITE,     x=100+i*2, y=80)
    for i in range(10): um.add_unit(P2, U_ELITE_WAR_CHARIOT, x=105+i*2, y=70)
    for i in range(8):  um.add_unit(P2, U_ARCHER,            x=102+i*2, y=55)

    # P3 – Garrison holding the Temple
    garrison_tc = um.add_unit(P3, B_TOWN_CENTER,  x=78, y=62)
    um.add_unit(P3, B_CASTLE,       x=72, y=58)
    um.add_unit(P3, B_WATCH_TOWER,  x=88, y=58)
    um.add_unit(P3, B_WATCH_TOWER,  x=88, y=70)
    desecrated_temple = um.add_unit(P3, B_MONASTERY, x=80, y=65)  # desecrated Temple
    for i in range(8): um.add_unit(P3, U_ELITE_HOPLITE, x=73+i*2, y=65)
    for i in range(5): um.add_unit(P3, U_ARCHER,        x=73+i*2, y=60)

    t_intro = tm.add_trigger("Intro")
    t_intro.enabled = True
    t_intro.execute_on_load = True
    t_intro.new_effect.display_instructions(
        display_time=25,
        message=(
            "<b>Judas Maccabeus</b>\n\n"
            "167 BC. Antiochus IV Epiphanes of the Seleucid Empire has "
            "desecrated the Temple in Jerusalem, banned the Torah, and ordered "
            "Jews to worship Greek gods on pain of death.\n\n"
            "Mattathias the priest refuses — and strikes down a Seleucid "
            "officer. The revolt begins. His son Judas Maccabeus ('The Hammer') "
            "leads a band of faithful warriors from the hills of Judea.\n\n"
            "Against all odds, the few must defeat the many. "
            "Liberate Jerusalem. Rededicate the Temple. "
            "The miracle of Hanukkah awaits."
        ),
        instruction_panel_position=0,
    )

    t_obj = tm.add_trigger("Objective")
    t_obj.enabled = True
    t_obj.execute_on_load = True
    t_obj.display_as_objective = True
    t_obj.short_description = "Liberate Jerusalem"
    t_obj.description = (
        "1. Defeat the Seleucid garrison (destroy Garrison Town Center).\n"
        "2. Build a Wonder on the Temple Mount to rededicate the Temple.\n"
        "3. Judas Maccabeus must survive."
    )

    # Phase 2: after garrison is destroyed, build the Temple
    t_phase2 = tm.add_trigger("Phase 2 - Rededicate the Temple")
    t_phase2.enabled = True
    t_phase2.new_condition.destroy_object(unit_object=garrison_tc.reference_id)
    t_phase2.new_effect.display_instructions(
        display_time=15,
        message=(
            "The garrison is broken! Jerusalem is free - but for how long? "
            "Antiochus will send his full army. You must rededicate the Temple "
            "before the Seleucid host arrives. Build the Temple (Wonder) now!"
        ),
        instruction_panel_position=0,
    )
    # Give the player resources for the Temple
    t_phase2.new_effect.modify_resource(
        quantity=1000, tribute_list=3,   # stone, operation add
        source_player=P1, operation=1,
    )
    t_phase2.new_effect.modify_resource(
        quantity=800, tribute_list=1,    # wood, operation add
        source_player=P1, operation=1,
    )
    t_phase2.new_effect.deactivate_trigger(trigger_id=t_phase2.trigger_id)

    # Seleucid counter-attack after 3 minutes
    t_counter = tm.add_trigger("Seleucid Counter-Attack")
    t_counter.enabled = True
    t_counter.new_condition.timer(timer=180)
    t_counter.new_effect.display_instructions(
        display_time=10,
        message="Lysias leads the Seleucid host! The full army marches on Jerusalem — defend the Temple!",
        instruction_panel_position=0,
    )
    for _ in range(5):
        t_counter.new_effect.create_object(
            object_list_unit_id=U_ELITE_HOPLITE, source_player=P2,
            location_x=100, location_y=70,
        )
    t_counter.new_effect.deactivate_trigger(trigger_id=t_counter.trigger_id)

    # Win: Temple Wonder built
    t_win = tm.add_trigger("Victory – Hanukkah")
    t_win.enabled = True
    t_win.new_condition.own_objects(
        quantity=1, source_player=P1, object_list=B_WONDER,
    )
    t_win.new_effect.display_instructions(
        display_time=20,
        message=(
            "The Temple is rededicated! The Maccabees find one small jar of "
            "consecrated oil — enough for one day, yet it burns for eight. "
            "This is Hanukkah: the Festival of Lights.\n\n"
            "Judas Maccabeus has done what no one thought possible. "
            "Against the greatest empire of the age, the few have defeated "
            "the many. Israel is free. The flame is never extinguished."
        ),
        instruction_panel_position=0,
    )
    t_win.new_effect.declare_victory(source_player=P1, enabled=1)

    t_lose = tm.add_trigger("Defeat")
    t_lose.enabled = True
    t_lose.new_condition.own_fewer_objects(quantity=1, source_player=P1, object_list=U_KING)
    t_lose.new_effect.display_instructions(
        display_time=12,
        message="Judas Maccabeus has fallen. Without the Hammer, the revolt collapses.",
        instruction_panel_position=0,
    )

    s.message_manager.instructions = (
        "Start in the Judean hills. Destroy the Garrison Town Center, "
        "then build a Wonder on the Temple Mount. Judas must survive."
    )
    s.message_manager.victory = "The Festival of Lights! Israel reclaims the Temple."
    s.message_manager.loss = "The Hammer has fallen. The flame goes out."
    save(s, "ot_12_maccabeus.aoe2scenario")


# ═══════════════════════════════════════════════════════════════════════════════
# CAMPAIGN JSON  (campaign menu metadata)
# ═══════════════════════════════════════════════════════════════════════════════
def write_campaign_json():
    import json
    campaign_data = {
        "Name": "Chronicles of Israel",
        "Difficulty": 1,
        "Scenarios": [
            {"Name": "Let My People Go",    "Filename": "ot_01_exodus.aoe2scenario"},
            {"Name": "The Walls of Jericho","Filename": "ot_02_jericho.aoe2scenario"},
            {"Name": "The Promised Land",   "Filename": "ot_03_promised_land.aoe2scenario"},
            {"Name": "Deborah's Sword",     "Filename": "ot_04_deborah.aoe2scenario"},
            {"Name": "Gideon's 300",        "Filename": "ot_05_gideon.aoe2scenario"},
            {"Name": "The First King",      "Filename": "ot_06_first_king.aoe2scenario"},
            {"Name": "The Shepherd King",   "Filename": "ot_07_shepherd_king.aoe2scenario"},
            {"Name": "Solomon's Temple",    "Filename": "ot_08_solomon.aoe2scenario"},
            {"Name": "A Kingdom Divided",   "Filename": "ot_09_divided.aoe2scenario"},
            {"Name": "Hezekiah's Wall",     "Filename": "ot_10_hezekiah.aoe2scenario"},
            {"Name": "The Fall of Jerusalem","Filename": "ot_11_fall.aoe2scenario"},
            {"Name": "Judas Maccabeus",     "Filename": "ot_12_maccabeus.aoe2scenario"},
        ]
    }
    path = os.path.join(MOD_ROOT, "resources", "_common", "campaign", "chronicles_of_israel.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(campaign_data, f, indent=2)
    print(f"  Saved: {path}")


def write_mod_json():
    import json
    mod_data = {
        "Author": "DanielVoll",
        "CacheStatus": 0,
        "Description": (
            "A 12-scenario campaign covering Old Testament Jewish history — "
            "from the Exodus out of Egypt to the Maccabean Revolt. "
            "Play as Moses, Joshua, Deborah, Gideon, Saul, David, Solomon, "
            "Hezekiah, and Judas Maccabeus."
        ),
        "Title": "Chronicles of Israel"
    }
    path = os.path.join(MOD_ROOT, "mod.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mod_data, f, indent=2)
    print(f"  Saved: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("Chronicles of Israel – Campaign Builder")
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
    print("Done! All scenarios written to:")
    print(f"  {SCENARIO_OUT}")
    print()
    print("To play:")
    print("  1. Launch Age of Empires II: Definitive Edition")
    print("  2. Go to Mods (in-game) – the mod 'Chronicles of Israel' should appear")
    print("  3. Enable it and restart the game")
    print("  4. Access scenarios via Single Player > Custom Scenarios")
