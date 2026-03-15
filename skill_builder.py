from models import Skill,Entry
from entry_generator import generate_entries
from skill_skeleton import generate_skill_skeleton
from utility import load_json


def load_modifier_space(path="skill_modifier_space.json"):
    return load_json(path)


def load_skeleton_constraints(path="skill_skeleton_constraints.json"):
    return load_json(path)


MODIFIER_SPACE = load_modifier_space()
SKELETON_CONSTRAINTS = load_skeleton_constraints()

# not starting from 0, saving space for manual input testing skills
SKILL_ID_COUNTER = 100


# skill id is for future extension when implying skill names, not a hard requirement in this experiment
def new_skill_id():
    global SKILL_ID_COUNTER
    SKILL_ID_COUNTER += 1
    return SKILL_ID_COUNTER


def build_skill(entries):
    return Skill(skill_id=new_skill_id(), entries=entries)


def generate_skill(modifier_space, skeleton_constraints):
    skill_skeleton = generate_skill_skeleton(modifier_space, skeleton_constraints)
    entries = generate_entries(modifier_space, skill_skeleton)

    return build_skill(entries)


def load_skill_from_dict(raw_skill_data):
    entries = [
        Entry(
            entry_type=raw_entry["entry_type"],
            tier=raw_entry["tier"],
            value=raw_entry["value"]
        )
        for raw_entry in raw_skill_data.get("entries", [])
    ]

    return Skill(
        skill_id=raw_skill_data.get("skill_id", 0),
        entries=entries,
    )