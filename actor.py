from skill_builder import generate_skill
import json

with open("character_basic_modifier.json", "r") as file:
    BASE_CHARACTER_STATUS = json.load(file)


class Actor:
    def __init__(self, id=0):
        self.skill = generate_skill()
        self.id = id

        self.character_status = BASE_CHARACTER_STATUS.copy()

    def get_character_status(self):
        return self.character_status
    
    def get_character_skill(self):
        return self.skill