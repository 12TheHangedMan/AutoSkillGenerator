import config
from models import Skill, Entry
from skill_simulator import SkillSimulator


def calculate_fitness(
    skill_simulator: SkillSimulator,
    attacker_skill: Skill,
    target_skill: Skill,
) -> float:
    return calculate_fitness_with_entries(
        skill_simulator=skill_simulator,
        attacker_skill_entries=attacker_skill.get_entries(),
        target_skill_entries=target_skill.get_entries(),
    )


def calculate_fitness_with_entries(
    skill_simulator: SkillSimulator,
    attacker_skill_entries: list[Entry],
    target_skill_entries: list[Entry],
) -> float:
    result = skill_simulator.simulate_with_entries(
        attacker_entries=attacker_skill_entries,
        target_entries=target_skill_entries,
    )

    target_hp = result["target_hp"]

    losses = calculate_loss_components_from_result(
        result=result,
        target_hp=target_hp,
    )

    return aggregate_losses_to_fitness(losses)


def calculate_loss_components_from_result(
    result: dict,
    target_hp: int,
) -> dict:
    total_dmg = result["total_dmg_made"]
    total_dmg_taken = result["total_dmg_taken"]
    total_cost = result["total_cost"]
    total_fatigue = result["total_fatigue"]

    if total_cost * total_fatigue == 0:
        raise ValueError("Total cost/fatigue cannot be zero for fitness calculation.")

    dmg_loss = calculate_dmg_loss(total_dmg, target_hp)
    cost_loss = calculate_cost_loss(total_cost, total_dmg)
    fatigue_loss = calculate_fatigue_loss(total_fatigue, total_dmg)
    dmg_taken_loss = calculate_dmg_taken_loss(total_dmg_taken, total_dmg, target_hp)

    return {
        "dmg_loss": dmg_loss,
        "cost_loss": cost_loss,
        "fatigue_loss": fatigue_loss,
        "dmg_taken_loss": dmg_taken_loss,
    }


def aggregate_losses_to_fitness(losses: dict) -> float:
    total_loss = (
        losses["dmg_loss"] * 1.0
        + (losses["cost_loss"] + losses["fatigue_loss"]) * 0.5
        + losses["dmg_taken_loss"]
    )
    return -total_loss * 1000


def calculate_dmg_loss(total_dmg: float, target_hp: int) -> float:
    return (1 - target_hp / total_dmg) ** 2


def calculate_cost_loss(total_cost: float, total_dmg: float) -> float:
    return (1 - total_dmg / (total_cost * 1 + 1e-6)) ** 2


def calculate_fatigue_loss(total_fatigue: float, total_dmg: float) -> float:
    return (1 - total_dmg / (total_fatigue * 1 + 1e-6)) ** 2


def calculate_dmg_taken_loss(
    total_dmg_taken: float, total_dmg: float, target_hp: int
) -> float:
    return total_dmg_taken / total_dmg
