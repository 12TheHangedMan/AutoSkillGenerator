from models import Skill
from entry_generator import generate_entries
from entry_validator import validate_entries
import config
import json


def load_modifier_space(path="skill_modifier_space.json"):
    with open(path, "r") as f:
        return json.load(f)


MODIFIER_SPACE = load_modifier_space()
SKILL_ID_COUNTER = 0


def new_skill_id():
    global SKILL_ID_COUNTER
    SKILL_ID_COUNTER += 1
    return SKILL_ID_COUNTER


def build_skill(entries):
    return Skill(skill_id=new_skill_id(), entries=entries)


def generate_skill(total_slots=None):
    if total_slots is None:
        total_slots = config.TOTAL_SLOTS

    modifier_space = MODIFIER_SPACE

    while True:
        entries = generate_entries(modifier_space, total_slots)

        if validate_entries(entries):
            return build_skill(entries)
