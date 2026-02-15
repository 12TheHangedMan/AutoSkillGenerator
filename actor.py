from skill import Skill

class Actor:
    def __init__(self, id, skeleton, constrains, skills:list[Skill]):
        self.skeleton = skeleton
        self.constrains = constrains
        self.skills = skills
        self.id = id

    def move(self, target):
        pass

    def log(self):
        pass

