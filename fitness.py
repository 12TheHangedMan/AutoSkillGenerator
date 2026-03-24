import config
from models import Skill, Entry
from skill_simulator import SkillSimulator


def calculate_fitness(
    skill_simulator: SkillSimulator,
    attacker_skill: Skill,
    target_skill: Skill,
    target_hp: int = config.TARGET_HP,
) -> float:

    result = calculate_fitness_with_entries(
        skill_simulator=skill_simulator,
        attacker_skill_entries=attacker_skill.get_entries(),
        target_skill_entries=target_skill.get_entries(),
        target_hp=target_hp,
    )
    return result


def calculate_fitness_with_entries(
    skill_simulator: SkillSimulator,
    attacker_skill_entries: list[Entry],
    target_skill_entries: list[Entry],
    target_hp: int = config.TARGET_HP,
) -> float:

    result = skill_simulator.simulate_with_entries(
        attacker_entries=attacker_skill_entries, target_entries=target_skill_entries
    )

    total_dmg = result["total_dmg_made"]
    total_cost = result["total_cost"]
    total_fatigue = result["total_fatigue"]

    if total_cost * total_fatigue == 0:
       raise ValueError("Total cost/fatigue cannot be zero for fitness calculation.")

    # stronger penalty for higher damage loss
    dmg_loss = (1 - total_dmg / target_hp) ** 2

    cost_loss = (total_cost + 1) ** 0.8 / total_dmg
    fatigue_loss = (total_fatigue + 1) ** 0.8 / total_dmg

    cost_loss *= 0.5
    fatigue_loss *= 0.5

    fitness = -dmg_loss - cost_loss - fatigue_loss
    return fitness * 1000
