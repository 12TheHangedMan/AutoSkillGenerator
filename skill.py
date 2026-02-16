class Skill:
    def __init__(self):
        # global unique id
        self.skill_id = 0

        self.skill_skeleton = 0

        # sword, barehand, polearm
        self.skill_type = 0

        # active/passive
        self.skill_class = 0

        # === cost class ===
        # mana cost
        self.skill_cost = 0

        # replace cd
        self.skill_fatigue = 0

        # === attack class ===
        self.skill_attack = 0

        self.skill_ignore_defense = 0

        # === defense class ===
        self.skill_damage_reduction_ratio = 0

        self.skill_damage_reduction_flat = 0

        # === attack buff class ===
        self.skill_critical_chance = 0

        self.skill_critical_multiplication = 0

        # === recover class ===
        self.skill_healing = 0

        self.skill_vampiric_ratio = 0

        # === control class ===
        # self.skill_stun_rounds = 0

        # decrease target attack
        # self.skill_weaken = 0, 0
