from models import Skill


class Actor:
    def __init__(self, skill: Skill, base_character_status: dict, id=0):
        self.skill = skill
        self.id = id
        self.character_status = base_character_status.copy()

    def get_character_status(self):
        return self.character_status

    def get_character_skill(self):
        return self.skill
