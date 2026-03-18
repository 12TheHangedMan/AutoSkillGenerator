import config
import utility
from models import Skill, aggregate_entries


class SkillSimulator:
    def __init__(
        self,
        attacker_status: dict,
        target_status: dict,
        total_rounds: int = config.TOTAL_ROUNDS,
    ):
        self.attacker_status = attacker_status.copy()
        self.target_status = target_status.copy()
        self.total_rounds = total_rounds

    def simulate_skill(self, attacker_skill: Skill, target_skill: Skill) -> dict:
        result = self.simulate_with_entries(
            attacker_status=self.attacker_status,
            target_status=self.target_status,
            attacker_entries=attacker_skill.get_entries(),
            target_entries=target_skill.get_entries(),
        )

        return result

    def calculate_dmg(
        self,
        attacker_status: dict,
        target_status: dict,
        aggregated_attacker_entries: dict[str, int],
    ) -> float:
        base_attack = attacker_status.get("base_attack", 0)
        base_hit_rate = attacker_status.get("base_hit_rate", 0)
        base_critical_rate = attacker_status.get("base_critical_rate", 0)
        base_critical_multiplier = attacker_status.get("base_critical_multiplier", 0)

        target_defense = target_status.get("base_defense", 0)
        target_dodge_rate = target_status.get("base_dodge", 0)
        target_anti_critical = target_status.get("base_anti_critical", 0)

        skill_attack_multiplier = aggregated_attacker_entries.get(
            "skill_attack_multiplication", 0
        )
        attack = base_attack * (1 + skill_attack_multiplier / 100)

        skill_hit_rate = aggregated_attacker_entries.get("skill_hit_rate", 0)
        hit_rate = base_hit_rate + skill_hit_rate

        skill_critical_rate = aggregated_attacker_entries.get(
            "skill_critical_chance", 0
        )
        critical_rate = base_critical_rate + skill_critical_rate

        skill_critical_multiplier = aggregated_attacker_entries.get(
            "skill_critical_multiplication", 0
        )
        critical_multiplier = base_critical_multiplier + skill_critical_multiplier

        skill_ignore_defense = aggregated_attacker_entries.get(
            "skill_ignore_defense", 0
        )
        defense = max(0, target_defense - skill_ignore_defense)

        skill_damage = aggregated_attacker_entries.get("skill_damage", 0)

        dmg_ratio = utility.calculate_damage_ratio(attack, defense)
        hit_ratio = utility.calculate_hit_ratio(hit_rate, target_dodge_rate)
        crit_chance = utility.calculate_critical_ratio(
            critical_rate, target_anti_critical
        )

        crit_multiply_ratio = critical_multiplier / 100

        expected_damage = (
            skill_damage
            * dmg_ratio
            * hit_ratio
            * (1 + crit_chance * crit_multiply_ratio)
        )

        return expected_damage

    def calculate_cost(self, aggregated_attacker_entries: dict[str, int]) -> float:
        raw_cost = aggregated_attacker_entries.get("skill_cost", 0)
        reduction_ratio = aggregated_attacker_entries.get(
            "skill_cost_reduction_ratio", 0
        )

        cost_reduction_ratio = max(0, min(reduction_ratio, 100))
        return raw_cost * (1 - cost_reduction_ratio / 100)

    def calculate_fatigue(self, aggregated_attacker_entries: dict[str, int]) -> float:
        raw_fatigue = aggregated_attacker_entries.get("skill_fatigue", 0)
        reduction_ratio = aggregated_attacker_entries.get(
            "skill_fatigue_reduction_ratio", 0
        )

        fatigue_reduction_ratio = max(0, min(reduction_ratio, 100))
        return raw_fatigue * (1 - fatigue_reduction_ratio / 100)

    def simulate_with_entries(
        self,
        attacker_status: dict,
        target_status: dict,
        attacker_entries: list,
        target_entries: list,
        total_rounds: int = -1,
    ) -> dict:
        dmg_made = 0.0
        dmg_taken = 0.0
        total_cost = 0.0
        total_fatigue = 0.0

        aggregated_attacker_entries = aggregate_entries(attacker_entries)
        aggregated_target_entries = aggregate_entries(target_entries)

        if total_rounds <= 0:
            total_rounds = config.TOTAL_ROUNDS

        for _ in range(total_rounds):
            dmg_made += self.calculate_dmg(
                attacker_status=attacker_status,
                target_status=target_status,
                aggregated_attacker_entries=aggregated_attacker_entries,
            )

            dmg_taken += self.calculate_dmg(
                attacker_status=target_status,
                target_status=attacker_status,
                aggregated_attacker_entries=aggregated_target_entries,
            )

            total_cost += self.calculate_cost(aggregated_attacker_entries)
            total_fatigue += self.calculate_fatigue(aggregated_attacker_entries)

        return {
            "total_dmg_made": dmg_made,
            "total_dmg_taken": dmg_taken,
            "total_cost": total_cost,
            "total_fatigue": total_fatigue,
            "dmg_made_per_round": dmg_made / total_rounds,
            "cost_per_round": total_cost / total_rounds,
            "fatigue_per_round": total_fatigue / total_rounds,
        }
