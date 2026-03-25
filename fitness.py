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
    total_dmg_taken = result["total_dmg_taken"]
    total_cost = result["total_cost"]
    total_fatigue = result["total_fatigue"]

    if total_cost * total_fatigue == 0:
        raise ValueError("Total cost/fatigue cannot be zero for fitness calculation.")

    # stronger penalty for higher damage loss
    dmg_loss = calculate_dmg_loss(total_dmg, target_hp)
    cost_loss = calculate_cost_loss(total_cost, total_dmg)
    fatigue_loss = calculate_fatigue_loss(total_fatigue, total_dmg)
    dmg_taken_loss = calculate_dmg_taken_loss(total_dmg_taken, total_dmg, target_hp)

    cost_loss *= 0.5
    fatigue_loss *= 0.5

    fitness = -dmg_loss - cost_loss - fatigue_loss - dmg_taken_loss / 1000
    return fitness * 1000


def calculate_dmg_loss(total_dmg: float, target_hp: int) -> float:
    # dmg loss is determined by how many rounds it takes to defeat the target
    # the ideal case is to defeat the target as close to the designed total rounds as possible
    dmg_loss = (1 - total_dmg / target_hp) ** 2

    return dmg_loss


def calculate_cost_loss(total_cost: float, total_dmg: float) -> float:
    cost_loss = (total_cost + 1) ** 0.8 / total_dmg

    return cost_loss


def calculate_fatigue_loss(total_fatigue: float, total_dmg: float) -> float:
    fatigue_loss = (total_fatigue + 1) ** 0.8 / total_dmg

    return fatigue_loss


def calculate_dmg_taken_loss(
    total_dmg_taken: float, total_dmg: float, target_hp: int
) -> float:
    # determined by how many rounds the battle lasts
    dmg_taken_loss = target_hp * total_dmg_taken / total_dmg

    return dmg_taken_loss
