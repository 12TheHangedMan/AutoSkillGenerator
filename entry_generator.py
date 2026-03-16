import random
from models import Entry
from utility import generate_levels, split_into_tiers
import config


# gene generator
def generate_entry(modifier_space: dict, entry_type=None, tier=None) -> Entry:
    if entry_type is None:
        entry_type = random.choice(list(modifier_space.keys()))

    param = modifier_space[entry_type]
    levels = generate_levels(param["min"], param["max"], param["step"])
    tiers = split_into_tiers(levels, config.TOTAL_TIERS)

    if tier is None:
        tier = random.randint(1, config.TOTAL_TIERS)

    tier_values = tiers[tier - 1]
    value = random.choice(tier_values)

    return Entry(entry_type=entry_type, tier=tier, value=int(value))


def generate_entries(modifier_space: dict, skeleton: list[str]) -> list[Entry]:
    entries = []

    for entry_type in skeleton:
        entries.append(
            generate_entry(
                modifier_space=modifier_space,
                entry_type=entry_type,
            )
        )

    return entries


def append_entries(entries: list[Entry], new_entry: Entry):
    return entries.append(new_entry)
