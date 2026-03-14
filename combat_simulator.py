from actor import Actor
import utility
import config


class CombatSimulator:
    def __init__(self, total_rounds=config.TOTAL_ROUNDS):
        self.remaining_rounds = total_rounds
        self.dummy = Actor()
        self.test_unit = Actor()
        self.dmg_made = 0
        self.dmg_taken = 0

    def simulate_combat(self):
        while self.remaining_rounds > 0:
            self.dmg_made += self.dmg_calculation(self.test_unit, self.dummy)
            self.dmg_taken += self.dmg_calculation(self.dummy, self.test_unit)

            self.remaining_rounds -= 1

    def dmg_calculation(self, attacker: Actor, target: Actor):
        attacker_status = attacker.get_character_status()
        target_status = target.get_character_status()

        skill = attacker.get_character_skill()
        skill_params = skill.aggregated_params

        base_attack = attacker_status.get("base_attack", 0)
        base_hit = attacker_status.get("base_hit_rate", 0)
        base_crit = attacker_status.get("base_critical_rate", 0)
        base_crit_mult = attacker_status.get("base_critical_multiplier", 0)

        target_defense = target_status.get("base_defense", 0)
        target_dodge = target_status.get("base_dodge", 0)
        target_anti_crit = target_status.get("base_anti_critical", 0)

        skill_damage = skill_params.get("damage", 0)
        skill_hit = skill_params.get("skill_hit_rate", 0)
        skill_crit = skill_params.get("skill_critical_chance", 0)
        skill_crit_mult = skill_params.get("skill_critical_multiplication", 0)
        skill_attack_mult = skill_params.get("skill_attack_multiplication", 0)
        skill_ignore_def = skill_params.get("ignore_defence", 0)

        attack = base_attack + skill_damage
        hit = base_hit + skill_hit
        crit = base_crit + skill_crit
        crit_mult = base_crit_mult + skill_crit_mult

        effective_defense = max(0, target_defense - skill_ignore_def)

        dmg_ratio = utility.damage_ratio_calculation(attack, effective_defense)
        hit_ratio = utility.damage_ratio_calculation(hit, target_dodge)
        crit_ratio = utility.damage_ratio_calculation(crit, target_anti_crit)

        attack_multiplier = 1 + skill_attack_mult / 100
        crit_multiplier = 1 + crit_mult / 100

        expected_damage = (
            attack
            * dmg_ratio
            * hit_ratio
            * attack_multiplier
            * (1 + crit_ratio * (crit_multiplier - 1))
        )

        return expected_damage

    def report_dmg(self):
        print(f"total dmg made: {self.dmg_made}")
        print(f"total dmg taken: {self.dmg_taken}")


cs = CombatSimulator()
cs.simulate_combat()
cs.report_dmg()
