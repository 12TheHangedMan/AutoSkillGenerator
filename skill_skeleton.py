import random


def generate_skill_skeleton(modifier_space: dict, skeleton_constraints: dict) -> list[str]:
    total_slots = skeleton_constraints["total_slots"]
    constraints = skeleton_constraints["constraints"]

    skeleton = []
    counts = {}

    constraint_map = {}
    for item in constraints:
        entry_type = item["entry_type"]
        min_count = item["min"]
        max_count = item["max"]

        if min_count > max_count:
            raise ValueError(f"{entry_type}: min > max")

        constraint_map[entry_type] = {"min": min_count, "max": max_count}

    candidate_entry_types = set(modifier_space.keys())

    # fill min
    for entry_type, rule in constraint_map.items():
        for _ in range(rule["min"]):
            skeleton.append(entry_type)
            counts[entry_type] = counts.get(entry_type, 0) + 1

        # remove types that already reach max
        if counts.get(entry_type, 0) >= rule["max"]:
            candidate_entry_types.discard(entry_type)



    # fill remaining slots
    remaining_slots = total_slots - len(skeleton)

    while remaining_slots:
        if not candidate_entry_types:
            raise ValueError("No candidate entry types available.")

        chosen = random.choice(list(candidate_entry_types))

        skeleton.append(chosen)
        counts[chosen] = counts.get(chosen, 0) + 1
        remaining_slots -= 1

        # remove types that already reach max
        if chosen in constraint_map and counts[chosen] >= constraint_map[chosen]["max"]:
            candidate_entry_types.discard(chosen)

    return skeleton