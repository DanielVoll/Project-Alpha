"""
Shared constants and helper utilities for the Chronicles of Israel campaign.
"""

import os
import random

# ── Output directory ────────────────────────────────────────────────────────
MOD_ROOT = (
    r"C:\Users\Leseh\Games\Age of Empires 2 DE"
    r"\76561198062540201\modes\Pompeii"
)
SCENARIO_OUT = os.path.join(MOD_ROOT, "resources", "_common", "scenario")

# ── Return of Rome (Pompeii) civilization IDs ────────────────────────────────
# These IDs come from modes/Pompeii/resources/_common/dat/civilizations.json
# They are interpreted correctly when the scenario variant is set to ROR.
CIV_GAIA      = 0
CIV_EGYPT     = 1   # Egyptian
CIV_GREEK     = 2   # Greek
CIV_BABYLON   = 3   # Babylonian
CIV_ASSYRIA   = 4   # Assyrian
CIV_MINOAN    = 5   # Minoan
CIV_CANAAN    = 6   # Hittite  — Canaanite city-states
CIV_ISRAEL    = 7   # Phoenician — Semitic Levantine, closest to ancient Israel
CIV_MIDIAN    = 8   # Sumerian  — Mesopotamian/desert raiders (Midian, Amalek)
CIV_PERSIA    = 9   # Persian
CIV_ROMAN     = 13  # Roman
CIV_PALMYRAN  = 15  # Palmyran  — Levantine desert people
CIV_SELEUCID  = 16  # Macedonian — Philistines / Seleucid Empire
CIV_TYRE      = 7   # Phoenician (Solomon's trading partner)

# ── Standard unit IDs ────────────────────────────────────────────────────────
U_MILITIA           = 74
U_ARCHER            = 4
U_SLINGER           = 185
U_SPEARMAN          = 93
U_HOPLITE           = 2110
U_ELITE_HOPLITE     = 2111
U_WAR_CHARIOT       = 2150
U_ELITE_WAR_CHARIOT = 2151
U_SCOUT_CAVALRY     = 448
U_KNIGHT            = 38
U_LONG_SWORDSMAN    = 77
U_CAMEL_RIDER       = 329
U_VILLAGER          = 83
U_KING              = 434
U_MONK              = 125
U_PRIEST            = 1023

# ── Building IDs ─────────────────────────────────────────────────────────────
B_TOWN_CENTER    = 109
B_BARRACKS       = 12
B_ARCHERY_RANGE  = 87
B_STABLE         = 101
B_MARKET         = 84
B_MONASTERY      = 104
B_CASTLE         = 82
B_WONDER         = 276
B_WATCH_TOWER    = 79
B_STONE_WALL     = 117
B_FORTIFIED_WALL = 155
B_PALISADE_WALL  = 72
B_GATE           = 487

# ── Terrain IDs ──────────────────────────────────────────────────────────────
T_GRASS       = 0
T_SHALLOW     = 1
T_DIRT3       = 3
T_SHALLOWS    = 4
T_DIRT1       = 6
T_GRASS3      = 9
T_DIRT2       = 11
T_GRASS2      = 12
T_FOREST_PALM = 13
T_DESERT      = 14
T_WATER_DEEP  = 22
T_WATER_MED   = 23
T_ROAD        = 24
T_ROCK        = 40
T_DESERT_CRACK= 45
T_FOREST_ACA  = 50
T_GRASS_DRY   = 100
T_FOREST_MED  = 88

# ── Foliage / decoration unit IDs (placed as Gaia) ───────────────────────────
TREE_PALM    = 351   # palm forest — Nile banks, Egypt
TREE_ACACIA  = 1063  # acacia — desert edge, dry savannah
TREE_OLIVE   = 1349  # olive — Canaan, Israel highlands
TREE_CYPRESS = 1347  # cypress — hill country, Jerusalem
TREE_DEAD    = 1250  # dead tree — harsh desert
TREE_OAK     = 349   # oak forest — northern hills, Lebanon cedar
BUSH_A       = 302   # generic shrub
CACTUS       = 709   # cactus — deep desert
PLANT_SHRUB  = 1362  # green shrub — fertile areas
ROCK_SM      = 1048  # small rock formation
ROCK_MED     = 1049  # medium rock formation
ROCK_LG      = 1050  # large rock formation
ROCK_LIME    = 2009  # limestone — Jerusalem stone

# ── Player IDs ───────────────────────────────────────────────────────────────
P_GAIA = 0
P1     = 1
P2     = 2
P3     = 3
P4     = 4
P5     = 5

# ── Diplomacy values ─────────────────────────────────────────────────────────
DIPL_ALLY    = 0
DIPL_NEUTRAL = 3
DIPL_ENEMY   = 1

# ── Map sizes ─────────────────────────────────────────────────────────────────
MAP_SMALL  = 80
MAP_MEDIUM = 120
MAP_LARGE  = 144


# ═══════════════════════════════════════════════════════════════════════════════
# Map painting helpers
# ═══════════════════════════════════════════════════════════════════════════════

def fill_terrain(mm, terrain_id, x1=0, y1=0, x2=None, y2=None, elevation=0):
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
                    mm.get_tile(nx, ny).terrain_id = terrain_id


def set_elevation_area(mm, elev, x1, y1, x2, y2):
    size = mm.map_size
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if 0 <= x < size and 0 <= y < size:
                mm.get_tile(x, y).elevation = elev


def draw_circle(mm, terrain_id, cx, cy, radius, elevation=None):
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
# Foliage / decoration helper
# ═══════════════════════════════════════════════════════════════════════════════

def scatter(um, x1, y1, x2, y2, unit_ids, count, seed=42):
    """
    Scatter `count` decoration units randomly within (x1,y1)-(x2,y2).
    unit_ids: single ID or list of IDs to choose from randomly.
    Uses a fixed seed so output is deterministic across rebuilds.
    """
    if isinstance(unit_ids, int):
        unit_ids = [unit_ids]
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(x1, x2)
        y = rng.randint(y1, y2)
        uid = rng.choice(unit_ids)
        um.add_unit(P_GAIA, uid, x=float(x), y=float(y))


# ═══════════════════════════════════════════════════════════════════════════════
# Trigger helpers
# ═══════════════════════════════════════════════════════════════════════════════

def setup_objectives(tm, title, objectives):
    """
    Create the top-right objective panel with checkboxes.

    title: str — bold header (no checkbox)
    objectives: list of (short_description, long_description) tuples
    Returns list of sub-objective trigger IDs so callers can deactivate them
    when each task is completed.
    """
    header = tm.add_trigger(f"OBJ: {title}")
    header.enabled = True
    header.execute_on_load = True
    header.display_as_objective = True
    header.header = True
    header.short_description = title
    header.description_order = 0

    sub_ids = []
    for i, (short, full) in enumerate(objectives, 1):
        t = tm.add_trigger(f"OBJ {i}: {short}")
        t.enabled = True
        t.execute_on_load = True
        t.display_as_objective = True
        t.header = False
        t.short_description = short
        t.description = full
        t.description_order = i
        sub_ids.append(t.trigger_id)

    return sub_ids


def story_trigger(tm, name, message, timer=None, activate_next=None,
                  deactivate_self=True, start_enabled=True):
    t = tm.add_trigger(name)
    t.enabled = start_enabled
    t.looping = False
    if timer is not None:
        t.new_condition.timer(timer=timer)
    t.new_effect.display_instructions(
        display_time=15, message=message, instruction_panel_position=0,
    )
    if deactivate_self:
        t.new_effect.deactivate_trigger(trigger_id=t.trigger_id)
    if activate_next is not None:
        t.new_effect.activate_trigger(trigger_id=activate_next)
    return t
