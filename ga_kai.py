import copy
import random
import config

from models import Entry, Skill
from skill_builder import SkillBuilder
from skill_simulator import SkillSimulator
from entry_generator import generate_entry
from pure_random_skill_generator import generate_entries_from_skeleton

from fitness import calculate_fitness_with_entries


def generate_ga_skill(
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
    skill_simulator: SkillSimulator,
    target_entries: list[Entry],
    population=list[list[Entry]],
    population_size: int = config.GA_POPULATION_SIZE,
    generations: int = config.GA_GENERATIONS,
    mutation_rate: float = config.GA_MUTATION_RATE,
    elite_size: int = config.GA_ELITE_SIZE,
):
    if len(population) == 0:
        population = initialize_population(
            modifier_space=modifier_space,
            skeleton_constraints=skeleton_constraints,
            skill_builder=skill_builder,
            population_size=population_size,
        )
    else:
        population = list(population)

    history = []

    for _ in range(generations):
        scored_population = evaluate_population(
            population=population,
            skill_simulator=skill_simulator,
            target_entries=target_entries,
        )

        scored_population.sort(key=lambda x: x[0], reverse=True)
        history.append(scored_population[0][0])

        next_population = [skill for _, skill in scored_population[:elite_size]]

        while len(next_population) < population_size:
            parent_a = tournament_select(scored_population)
            parent_b = tournament_select(scored_population)

            child = crossover(
                parent_a=parent_a,
                parent_b=parent_b,
                modifier_space=modifier_space,
                skeleton_constraints=skeleton_constraints,
                skill_builder=skill_builder,
            )

            child = mutate(
                entries=child,
                modifier_space=modifier_space,
                skeleton_constraints=skeleton_constraints,
                skill_builder=skill_builder,
                mutation_rate=mutation_rate,
            )

            next_population.append(child)

        population = next_population

    final_scored_population = evaluate_population(
        population=population,
        skill_simulator=skill_simulator,
        target_entries=target_entries,
    )
    final_scored_population.sort(key=lambda x: x[0], reverse=True)

    best_fitness, best_skill = final_scored_population[0]

    return {
        "best_skill": best_skill,
        "best_fitness": best_fitness,
        "population": population,
        "history": history,
        "scored_population": final_scored_population,
    }


def initialize_population(
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
    population_size: int,
) -> list[Skill]:
    population = []

    for _ in range(population_size):
        entries = generate_entries_from_skeleton(
            modifier_space, skeleton_constraints, skill_builder
        )

        population.append(entries)

    return population


def evaluate_population(
    population: list[list[Entry]],
    skill_simulator: SkillSimulator,
    target_entries: list[Entry],
) -> list:
    scored_population = []

    for entries in population:
        fitness = calculate_fitness_with_entries(
            skill_simulator=skill_simulator,
            attacker_skill_entries=entries,
            target_skill_entries=target_entries,
        )
        scored_population.append((fitness, entries))

    return scored_population


def tournament_select(
    scored_population: list[tuple[float, list[Entry]]], tournament_size: int = 3
) -> list[Entry]:
    candidates = random.sample(scored_population, tournament_size)
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def crossover(
    parent_a: list[Entry],
    parent_b: list[Entry],
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
    min_len: int,
) -> list[Entry]:

    if len(parent_a) != len(parent_b):
        raise ValueError(
            "Parent skill entries must be of the same length for crossover."
        )

    length = len(parent_a)
    pivot = random.randint(1, length - 1)

    child_entries_1 = parent_a[:pivot] + parent_b[pivot:]
    child_entries_2 = parent_b[:pivot] + parent_a[pivot:]

    repaired_entries_1 = repair_entries(
        entries=child_entries_1,
        modifier_space=modifier_space,
        skeleton_constraints=skeleton_constraints,
    )

    repaired_entries_2 = repair_entries(
        entries=child_entries_2,
        modifier_space=modifier_space,
        skeleton_constraints=skeleton_constraints,
        min_len=min_len,
    )

    return skill_builder.build_skill(repaired_entries_1)


def mutate(
    entries: list[Entry],
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
    mutation_rate: float,
) -> list[Entry]:
    min_length = skill_builder.get_min_skeleton_length()
    min_skeleton = skill_builder.get_min_skeleton()

    for idx, entry in enumerate(entries):
        # filtering the mutation with mutation rate
        if random.random() >= mutation_rate:
            continue

        # only mutate tier for min skeleton slots
        if idx < min_length:
            new_tier = random.randint(1, config.TOTAL_TIERS)
            entries[idx] = generate_entry(
                modifier_space=modifier_space,
                entry_type=min_skeleton[idx],
                tier=new_tier,
            )

        # mutate either entry_type or tier for the rest slots
        else:
            new_tier = random.randint(1, config.TOTAL_TIERS)
            new_entry_type = random.choice(list(modifier_space.keys()))
            entries[idx] = generate_entry(
                modifier_space=modifier_space, entry_type=new_entry_type, tier=new_tier
            )

    repaired_entries = repair_entries(
        entries=entries,
        modifier_space=modifier_space,
        skeleton_constraints=skeleton_constraints,
        skill_builder=skill_builder,
    )

    return repaired_entries


def repair_entries(
    entries: list[Entry],
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
) -> list[Entry]:
    constraints: dict = copy.deepcopy(skeleton_constraints["constraints"])
    max_length: int = skeleton_constraints["max_slots"]
    min_length = skill_builder.get_min_skeleton_length()
    min_skeleton = skill_builder.get_min_skeleton()

    repaired_entries = copy.deepcopy(entries)

    candidate_entry_types = list(modifier_space.keys())

    # consume min skeleton quotas first
    for entry_type in min_skeleton:
        update_candidate_entry_types(entry_type, candidate_entry_types, constraints)

    # repair only optional part
    for idx in range(min_length, max_length):
        entry = repaired_entries[idx]
        entry_type = entry.entry_type

        if entry_type in candidate_entry_types:
            update_candidate_entry_types(entry_type, candidate_entry_types, constraints)
        else:
            replacement = generate_valid_entry(
                modifier_space=modifier_space,
                candidate_entry_types=candidate_entry_types,
                updated_constraints=constraints,
            )
            repaired_entries[idx] = replacement

    return repaired_entries


def update_candidate_entry_types(
    entry_type: str,
    candidate_entry_types: list[str],
    updated_constraints: dict,
):
    if entry_type in updated_constraints:
        updated_constraints[entry_type]["max"] -= 1

        if updated_constraints[entry_type]["max"] <= 0:
            if entry_type in candidate_entry_types:
                candidate_entry_types.remove(entry_type)


def generate_valid_entry(
    modifier_space: dict,
    candidate_entry_types: list[str],
    updated_constraints: dict,
) -> Entry:
    if not candidate_entry_types:
        raise ValueError("No available candidate entry type possible")

    chosen_entry_type = random.choice(candidate_entry_types)
    update_candidate_entry_types(
        chosen_entry_type, candidate_entry_types, updated_constraints
    )

    return generate_entry(
        modifier_space=modifier_space,
        entry_type=chosen_entry_type,
    )
