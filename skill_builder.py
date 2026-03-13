from models import Skill
from entry_generator import load_modifier_space, generate_entries
from entry_validator import validate_entries
import config


def build_skill(entries):
    return Skill(entries=entries)


def generate_skill(total_slots=None):
    if total_slots is None:
        total_slots = config.TOTAL_SLOTS

    modifier_space = load_modifier_space()

    while True:
        entries = generate_entries(modifier_space, total_slots)

        if validate_entries(entries):
            return build_skill(entries)