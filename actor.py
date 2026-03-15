from utility import load_json
from models import Skill


def load_charater_base_modifier(path="character_basic_modifier.json"):
    return load_json(path)


class Actor:
    def __init__(self, skill: Skill, base_character_status, id=0):
        self.skill = skill
        self.id = id
        self.character_status = base_character_status.copy()

    def get_character_status(self):
        return self.character_status

    def get_character_skill(self):
        return self.skill
