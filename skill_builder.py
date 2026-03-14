from models import Skill
from entry_generator import generate_entries
from skill_skeleton import generate_skill_skeleton
import config
import json


def load_modifier_space(path="skill_modifier_space.json"):
    with open(path, "r") as f:
        return json.load(f)


def load_skeleton_constraints(path="skill_skeleton_constraints.json"):
    with open(path, "r") as f:
        return json.load(f)


MODIFIER_SPACE = load_modifier_space()
SKELETON_CONSTRAINTS = load_skeleton_constraints()
SKILL_ID_COUNTER = 0


def new_skill_id():
    global SKILL_ID_COUNTER
    SKILL_ID_COUNTER += 1
    return SKILL_ID_COUNTER


def build_skill(entries):
    return Skill(skill_id=new_skill_id(), entries=entries)


def generate_skill():
    skill_skeleton = generate_skill_skeleton(MODIFIER_SPACE, SKELETON_CONSTRAINTS)
    entries = generate_entries(MODIFIER_SPACE, skill_skeleton)

    return build_skill(entries)