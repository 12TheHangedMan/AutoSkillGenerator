import random
from models import Entry
from utility import generate_levels, split_into_tiers
import config


# gene generator
def generate_entry(modifier_space: dict, entry_type=None, tier=None) -> Entry:
    if entry_type is None or entry_type not in modifier_space:
        entry_type = random.choice(list(modifier_space.keys()))

    if entry_type == config.EMPTY_PADDING:
        return Entry(entry_type=entry_type, tier=1, value=0)

    property = modifier_space[entry_type]
    min, max, step = property["min"], property["max"], property["step"]
    enrty_value_space: list = generate_levels(min, max, step)
    tier_list = split_into_tiers(enrty_value_space, config.TOTAL_TIERS)

    # default to random tier if not specified
    if tier is None:
        tier = random.randint(1, config.TOTAL_TIERS)

    value = random.choice(tier_list[tier - 1])

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
