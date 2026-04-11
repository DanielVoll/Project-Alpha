"""
Shared constants and helper utilities for the Chronicles of Israel campaign.
"""

import os
import math
import random

# ── Output directory ────────────────────────────────────────────────────────
MOD_ROOT = (
    r"C:\Users\Leseh\Games\Age of Empires 2 DE"
    r"\76561198062540201\mods\local\chronicles-of-israel"
)
SCENARIO_OUT = os.path.join(MOD_ROOT, "resources", "_common", "scenario")

# ── Civilization IDs ─────────────────────────────────────────────────────────
# Antiquity-era civs (from civilizations.json)
CIV_ACHAEMENIDS  = 46   # Persian empire feel → Egypt / Assyria / Babylon
CIV_ATHENIANS    = 47   # Greek city-state feel → Israel (player)
CIV_SPARTANS     = 48   # Warrior culture → Philistines / Amalekites
CIV_MACEDONIANS  = 54   # Alexander style → Seleucids / Philistines
CIV_THRACIANS    = 55   # Barbarian-ish → Canaanites / Midianites

# ── Standard unit IDs ────────────────────────────────────────────────────────
U_MILITIA           = 74
U_ARCHER            = 4
U_SLINGER           = 185
U_SPEARMAN          = 93
U_HOPLITE           = 2110
U_ELITE_HOPLITE     = 2111
U_WAR_CHARIOT       = 2150      # antiquity war chariot
U_ELITE_WAR_CHARIOT = 2151
U_SCOUT_CAVALRY     = 448
U_KNIGHT            = 38
U_LONG_SWORDSMAN    = 77
U_CAMEL_RIDER       = 329
U_VILLAGER          = 83
U_KING              = 434       # hero / leader unit
U_MONK              = 125
U_PRIEST            = 1023

# ── Building IDs ─────────────────────────────────────────────────────────────
B_TOWN_CENTER   = 109
B_BARRACKS      = 12
B_ARCHERY_RANGE = 87
B_STABLE        = 101
B_MARKET        = 84
B_MONASTERY     = 104
B_CASTLE        = 82
B_WONDER        = 276
B_WATCH_TOWER   = 79
B_STONE_WALL    = 117
B_PALISADE_WALL = 72
B_FORTIFIED_WALL= 155
B_GATE          = 487

# ── Terrain IDs ──────────────────────────────────────────────────────────────
T_GRASS         = 0
T_SHALLOW       = 1
T_DIRT3         = 3
T_SHALLOWS      = 4
T_DIRT1         = 6
T_GRASS3        = 9
T_DIRT2         = 11
T_GRASS2        = 12
T_FOREST_PALM   = 13
T_DESERT        = 14
T_WATER_DEEP    = 22
T_WATER_MED     = 23
T_ROAD          = 24
T_ROCK          = 40
T_DESERT_CRACK  = 45
T_FOREST_ACACIA = 50
T_GRASS_DRY     = 100
T_FOREST_MED    = 88   # Mediterranean forest (olive trees)

# ── Player IDs ───────────────────────────────────────────────────────────────
P_GAIA  = 0
P1      = 1    # Human player (Israelites)
P2      = 2    # Enemy / Ally 1
P3      = 3    # Enemy / Ally 2
P4      = 4    # Enemy / Ally 3
P5      = 5

# ── Diplomacy values ─────────────────────────────────────────────────────────
DIPL_ALLY   = 0
DIPL_NEUTRAL= 3
DIPL_ENEMY  = 1

# ── Map sizes ─────────────────────────────────────────────────────────────────
MAP_SMALL   = 80
MAP_MEDIUM  = 120
MAP_LARGE   = 144


# ═══════════════════════════════════════════════════════════════════════════════
# Map painting helpers
# ═══════════════════════════════════════════════════════════════════════════════

def fill_terrain(mm, terrain_id, x1=0, y1=0, x2=None, y2=None, elevation=0):
    """Fill a rectangular region with a terrain type."""
    size = mm.map_size
    x2 = x2 if x2 is not None else size - 1
    y2 = y2 if y2 is not None else size - 1
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if 0 <= x < size and 0 <= y < size:
                tile = mm.get_tile(x, y)
                tile.terrain_id = terrain_id
                if elevation:
                    tile.elevation = elevation


def draw_river(mm, terrain_id, x_start, y_start, x_end, y_end, width=3):
    """Draw a rough river between two points."""
    size = mm.map_size
    steps = max(abs(x_end - x_start), abs(y_end - y_start))
    if steps == 0:
        return
    for i in range(steps + 1):
        t = i / steps
        cx = int(x_start + (x_end - x_start) * t)
        cy = int(y_start + (y_end - y_start) * t)
        for dx in range(-width // 2, width // 2 + 1):
            for dy in range(-width // 2, width // 2 + 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < size and 0 <= ny < size:
                    tile = mm.get_tile(nx, ny)
                    tile.terrain_id = terrain_id


def set_elevation_area(mm, elev, x1, y1, x2, y2):
    """Set elevation for a region."""
    size = mm.map_size
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if 0 <= x < size and 0 <= y < size:
                mm.get_tile(x, y).elevation = elev


def draw_circle(mm, terrain_id, cx, cy, radius, elevation=None):
    """Fill a circular region."""
    size = mm.map_size
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius:
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size:
                    tile = mm.get_tile(x, y)
                    tile.terrain_id = terrain_id
                    if elevation is not None:
                        tile.elevation = elevation


# ═══════════════════════════════════════════════════════════════════════════════
# Trigger helpers
# ═══════════════════════════════════════════════════════════════════════════════

def story_trigger(tm, name, message, timer=None, activate_next=None,
                  deactivate_self=True, start_enabled=True):
    """
    Create a one-shot story / narration trigger.
    Returns the trigger.
    """
    t = tm.add_trigger(name)
    t.enabled = start_enabled
    t.looping = False

    if timer is not None:
        t.new_condition.timer(timer=timer)

    t.new_effect.display_instructions(
        display_time=15,
        message=message,
        instruction_panel_position=0,
    )

    if deactivate_self:
        t.new_effect.deactivate_trigger(trigger_id=t.trigger_id)

    if activate_next is not None:
        t.new_effect.activate_trigger(trigger_id=activate_next)

    return t


def objective_trigger(tm, name, message, looping=False, enabled=True):
    """Display an objective on screen."""
    t = tm.add_trigger(name)
    t.enabled = enabled
    t.looping = looping
    t.display_as_objective = True
    t.short_description = name
    t.description = message
    return t


def win_trigger(tm, name, player=P1):
    """Declare victory for player."""
    t = tm.add_trigger(name)
    t.enabled = True
    t.new_effect.declare_victory(source_player=player, enabled=1)
    return t
