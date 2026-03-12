from collections import Counter
import config


def validate_entries(entries):
    counter = Counter(entry.entry_type for entry in entries)

    for required_type in config.REQUIRED_ENTRY_TYPES:
        if counter[required_type] < 1:
            return False

    for entry_type, min_count in config.MIN_TYPE_COUNTS.items():
        if counter[entry_type] < min_count:
            return False

    for entry_type, max_count in config.MAX_TYPE_COUNTS.items():
        if counter[entry_type] > max_count:
            return False

    non_damage_count = sum(
        count
        for entry_type, count in counter.items()
        if entry_type not in ["damage_range", "cost_range", "fatigue_range"]
    )

    if non_damage_count < config.MIN_NON_DAMAGE_COUNT:
        return False

    if non_damage_count > config.MAX_NON_DAMAGE_COUNT:
        return False

    return True
