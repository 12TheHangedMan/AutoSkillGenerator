import json
import random
from models import Entry
from utility import generate_levels, split_into_tiers
import config


def load_modifier_space(path="skill_modifier_space.json"):
    with open(path, "r") as f:
        return json.load(f)


def generate_entry(modifier_space, entry_type=None, tier=None, slot_id=0):
    if entry_type is None:
        entry_type = random.choice(list(modifier_space.keys()))

    param = modifier_space[entry_type]
    levels = generate_levels(param["min"], param["max"], param["step"])
    tiers = split_into_tiers(levels, config.TOTAL_TIERS)

    if tier is None:
        tier = random.randint(1, config.TOTAL_TIERS)

    tier_values = tiers[tier - 1]
    value = random.choice(tier_values)

    return Entry(
        entry_type=entry_type,
        tier=tier,
        value=int(value),
        slot_id=slot_id
    )


def generate_entries(modifier_space, total_slots):
    entries = []
    slot_id = 0

    # fill cost and fatigue
    for entry_type in config.REQUIRED_ENTRY_TYPES:
        entries.append(
            generate_entry(
                modifier_space=modifier_space,
                entry_type=entry_type,
                slot_id=slot_id
            )
        )
        slot_id += 1

    # fill the min active modifiers
    for _ in range(config.MIN_TYPE_COUNTS.get("damage_range", 0)):
        entries.append(
            generate_entry(
                modifier_space=modifier_space,
                entry_type="damage_range",
                slot_id=slot_id
            )
        )
        slot_id += 1

    # fill the passive modifiers
    optional_non_damage_types = [
        k for k in modifier_space.keys()
        if k not in ["damage_range", "cost_range", "fatigue_range"]
    ]

    for _ in range(config.MIN_NON_DAMAGE_COUNT):
        entry_type = random.choice(optional_non_damage_types)
        entries.append(
            generate_entry(
                modifier_space=modifier_space,
                entry_type=entry_type,
                slot_id=slot_id
            )
        )
        slot_id += 1

    # fill the rest slots
    optional_types = [
        k for k in modifier_space.keys()
        if k not in config.REQUIRED_ENTRY_TYPES
    ]

    remaining_slots = total_slots - len(entries)

    for _ in range(remaining_slots):
        entry_type = random.choice(optional_types)
        entries.append(
            generate_entry(
                modifier_space=modifier_space,
                entry_type=entry_type,
                slot_id=slot_id
            )
        )
        slot_id += 1

    return entries