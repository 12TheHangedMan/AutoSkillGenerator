from utility import generate_float_levels, generate_levels
from procedure import Procedure
import json
import random
import config


def generate_entry(space, key):
    param = space[key]
    levels = generate_levels(param["min"], param["max"], param["step"])
    value = random.choice(levels)
    return key, value


def aggregate_entries(entries):
    result = {}
    for key, value in entries:
        clean_key = key.replace("_range", "")
        result[clean_key] = result.get(clean_key, 0) + value
    return result


def generate_parameters(num_slots: int):
    with open("skill_modifier_space.json", "r") as file:
        skill_modifier_space = json.load(file)

    entries = []

    # all skills require cost and fatigue
    required_keys = ["cost_range", "fatigue_range"]
    optional_keys = [k for k in skill_modifier_space.keys() if k not in required_keys]

    for key in required_keys:
        entries.append(generate_entry(skill_modifier_space, key))

    remaining_slots = num_slots - len(required_keys)
    for _ in range(remaining_slots):
        key = random.choice(optional_keys)
        entries.append(generate_entry(skill_modifier_space, key))

    result = aggregate_entries(entries)
    return result, entries