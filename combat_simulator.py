from actor import Actor
import utility
import config


class CombatSimulator:
    def __init__(
        self, attacker: Actor, target: Actor, total_rounds=config.TOTAL_ROUNDS
    ):
        self.total_rounds = total_rounds
        self.remaining_rounds = total_rounds
        self.dmg_made = 0.0
        self.dmg_taken = 0.0
        self.total_cost = 0.0
        self.total_fatigue = 0.0

        self.attacker = attacker
        self.target = target

    def simulate_combat(self):
        while self.remaining_rounds > 0:
            self.dmg_made += self.dmg_calculation(self.attacker, self.target)
            self.dmg_taken += self.dmg_calculation(self.target, self.attacker)

            self.total_cost += self.cost_calculation(self.attacker)
            self.total_fatigue += self.fatigue_calculation(self.attacker)

            self.remaining_rounds -= 1

    def dmg_calculation(self, attacker: Actor, target: Actor) -> float:
        attacker_status = attacker.get_character_status()
        target_status = target.get_character_status()

        skill = attacker.get_character_skill()
        skill_params = skill.get_params()

        base_attack = attacker_status.get("base_attack", 0)
        base_hit = attacker_status.get("base_hit_rate", 0)
        base_crit = attacker_status.get("base_critical_rate", 0)
        base_crit_mult = attacker_status.get("base_critical_multiplier", 0)

        target_defense = target_status.get("base_defense", 0)
        target_dodge = target_status.get("base_dodge", 0)
        target_anti_crit = target_status.get("base_anti_critical", 0)

        skill_damage = skill_params.get("skill_damage", 0)
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

    def cost_calculation(self, attacker: Actor) -> float:
        skill = attacker.get_character_skill()
        skill_params = skill.aggregated_params

        raw_cost = skill_params.get("skill_cost", 0)
        reduction_ratio = skill_params.get("skill_cost_reduction_ratio", 0)

        reduction_ratio = max(0, min(reduction_ratio, 100))
        final_cost = raw_cost * (1 - reduction_ratio / 100)

        return final_cost

    def fatigue_calculation(self, attacker: Actor) -> float:
        skill = attacker.get_character_skill()
        skill_params = skill.aggregated_params

        raw_fatigue = skill_params.get("skill_fatigue", 0)
        reduction_ratio = skill_params.get("skill_fatigue_reduction_ratio", 0)

        reduction_ratio = max(0, min(reduction_ratio, 100))
        final_fatigue = raw_fatigue * (1 - reduction_ratio / 100)

        return final_fatigue

    def report_dmg(self):
        print(f"total dmg made: {self.dmg_made}")
        print(f"total dmg taken: {self.dmg_taken}")
        print(f"total cost: {self.total_cost}")
        print(f"total fatigue: {self.total_fatigue}")
        print(f"avg dmg made per round: {self.dmg_made / self.total_rounds}")
        print(f"avg cost per round: {self.total_cost / self.total_rounds}")
        print(f"avg fatigue per round: {self.total_fatigue / self.total_rounds}")
        print(f"{self.attacker.get_character_skill().get_params()}")
        print(f"{self.attacker.get_character_skill().get_entries()}")


# cs = CombatSimulator()
# cs.simulate_combat()
# cs.report_dmg()
