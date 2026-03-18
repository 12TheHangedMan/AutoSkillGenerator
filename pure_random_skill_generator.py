from skill_builder import SkillBuilder
from entry_generator import generate_entry
from models import Entry
import random


def generate_pure_random_skill(
    modifier_space: dict, skeleton_constraints: dict, skill_builder: SkillBuilder
):
    min_skeleton = skill_builder.get_min_skeleton()
    extended_skeleton = extend_skeleton(
        modifier_space, skeleton_constraints, min_skeleton
    )
    entries = fill_skeleton(modifier_space, extended_skeleton)

    return skill_builder.build_skill(entries)


def extend_skeleton(
    modifier_space: dict, skeleton_constraints: dict, min_skeleton: list[str]
) -> list[str]:
    max_slots = skeleton_constraints["max_slots"]
    constraints = skeleton_constraints["constraints"]

    candidate_entry_types = set(modifier_space.keys())

    counts = {}
    for entry_type in min_skeleton:
        counts[entry_type] = counts.get(entry_type, 0) + 1

    extended_skeleton = list(min_skeleton)

    # remove the candidate entries that hit max
    for entry_type, rule in constraints.items():
        if counts.get(entry_type, 0) >= rule["max"]:
            candidate_entry_types.discard(entry_type)

    remaining_slots = max_slots - len(extended_skeleton)

    while remaining_slots:
        if not candidate_entry_types:
            raise ValueError("No candidate entry types available.")

        chosen = random.choice(list(candidate_entry_types))
        append_skeleton(extended_skeleton, chosen)
        counts[chosen] = counts.get(chosen, 0) + 1
        remaining_slots -= 1

        if chosen in constraints and counts[chosen] >= constraints[chosen]["max"]:
            candidate_entry_types.discard(chosen)

    return extended_skeleton


def append_skeleton(skeleton: list[str], new_entry_type: str):
    if skeleton is None or len(skeleton) == 0:
        raise ValueError("Empty list")
    skeleton.append(new_entry_type)


def fill_skeleton(modifier_space: dict, skeleton: list[str]) -> list[Entry]:
    entries = []

    for entry_type in skeleton:
        entries.append(
            generate_entry(
                modifier_space=modifier_space,
                entry_type=entry_type,
            )
        )

    return entries
