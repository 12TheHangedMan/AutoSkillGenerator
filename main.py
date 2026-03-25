from utility import *
import time
from skill_builder import SkillBuilder
from pure_random_skill_generator import generate_pure_random_skill
from rule_based_random_skill_generator import generate_rule_based_random_skill
from ga_skill_generator import generate_ga_skill
import config
from data_loader import load_data
from fitness import calculate_fitness
from skill_simulator import SkillSimulator
import numpy as np
import matplotlib.pyplot as plt
import random

random.seed(config.SEED)
np.random.seed(config.SEED)


def main():
    start_time = time.perf_counter()

    base_character_status_templates, modifier_space, skeleton_constraints = load_data()

    base_character_status_basic_template = base_character_status_templates["basic_template"]

    base_character_status_berserk_template = base_character_status_templates["berserk_template"]
    base_character_status_glass_cannon_template = base_character_status_templates["glass_cannon_template"]
    base_character_status_tank_template = base_character_status_templates["tank_template"]
    base_character_status_elite_template = base_character_status_templates["elite_template"]
    base_character_status_boss_template = base_character_status_templates["boss_template"]

    target_base_character_status = base_character_status_boss_template

    skill_builder = SkillBuilder(modifier_space, skeleton_constraints)
    test_unit_skill = generate_pure_random_skill(
        modifier_space, skeleton_constraints, skill_builder
    )

    dummy_skill_data = load_json(config.DUMMY_SKILL)
    dummy_entries = skill_builder.load_entries_from_dict(dummy_skill_data)
    dummy_skill = skill_builder.load_skill_from_dict(dummy_skill_data)

    ss = SkillSimulator(base_character_status_basic_template, target_base_character_status, 4)
    pure_random_results = []

    start_time = time.perf_counter()
    # pure random skill evaluation and metrics
    for _ in range(config.SAMPLES_PER_FOLD):
        test_unit_skill = generate_pure_random_skill(
            modifier_space, skeleton_constraints, skill_builder
        )
        fitness = calculate_fitness(ss, test_unit_skill, dummy_skill)
        pure_random_results.append((fitness, test_unit_skill))

    top10 = sorted(pure_random_results, key=lambda x: x[0], reverse=True)[:10]

    for f, s in top10:
        print(f)
        print(s.get_params())

    pure_random_skill_fitness_list = [f for f, _ in pure_random_results]
    pure_random_skill_list = [s for _, s in pure_random_results]
    pure_random_skill_variance = np.var(pure_random_skill_fitness_list)
    filtered_pure_random_skill_results = [
        (f, s) for f, s in pure_random_results if f > -200
    ]
    unique_archetypes = len(
        set(s.archetype_id for _, s in filtered_pure_random_skill_results)
    )
    print("pure_random_skill_variance:", pure_random_skill_variance)
    print("mean:", np.mean(pure_random_skill_fitness_list))
    print("max:", np.max(pure_random_skill_fitness_list))
    print("min:", np.min(pure_random_skill_fitness_list))
    print("Filtered count:", len(filtered_pure_random_skill_results))
    print("Unique archetypes in filtered results:", unique_archetypes)

    plt.hist(pure_random_skill_fitness_list, bins=50)
    plt.show()

    # rules based skill evaluation
    rule_base_results = {}
    best_fold_results = []
    rule_base_best_mean = -float("inf")
    best_fold = 0

    fold_range = range(1, config.TOTAL_TIERS + 1)

    for fold in fold_range:
        rule_base_results_per_fold = []

        for _ in range(config.SAMPLES_PER_FOLD):
            test_unit_skill = generate_rule_based_random_skill(
                modifier_space, skeleton_constraints, skill_builder, fold
            )
            fitness = calculate_fitness(ss, test_unit_skill, dummy_skill)
            rule_base_results_per_fold.append((fitness, test_unit_skill))

        rule_based_skill_fitness_list = [f for f, _ in rule_base_results_per_fold]
        mean = np.mean(rule_based_skill_fitness_list)
        var = np.var(rule_based_skill_fitness_list)

        print(f"fold {fold}: mean={mean}, var={var}")

        if mean > rule_base_best_mean:
            rule_base_best_mean = mean
            best_fold_results = rule_base_results_per_fold
            best_fold = fold

        rule_base_results[fold] = rule_base_results_per_fold

    best_rule_based_skill_fitness_list = [f for f, _ in best_fold_results]
    best_rule_based_skill_variance = np.var(best_rule_based_skill_fitness_list)

    filtered_best_rule_based_skill_results = [
        (f, s) for f, s in best_fold_results if f > -200
    ]

    unique_archetypes = len(
        set(s.archetype_id for _, s in filtered_best_rule_based_skill_results)
    )

    print("best fold:", best_fold)
    print("best fold variance:", best_rule_based_skill_variance)
    print("mean:", np.mean(best_rule_based_skill_fitness_list))
    print("max:", np.max(best_rule_based_skill_fitness_list))
    print("min:", np.min(best_rule_based_skill_fitness_list))
    print("Filtered count:", len(filtered_best_rule_based_skill_results))
    print("Unique archetypes in filtered results:", unique_archetypes)

    plt.hist(best_rule_based_skill_fitness_list, bins=50)
    plt.show()

    # GA skill generation and evaluation
    ga_population = pure_random_skill_list

    total_runs = 10
    ga_generated_skill_list_with_fitness = []

    for _ in range(total_runs):
        ga_result = generate_ga_skill(
            modifier_space=modifier_space,
            skeleton_constraints=skeleton_constraints,
            skill_builder=skill_builder,
            skill_simulator=ss,
            target_entries=dummy_entries,
            # population=ga_population,
        )

        ga_generated_skill_list_with_fitness.extend(ga_result["scored_skills"])

    ga_generated_skill_fitness_list = [
        f for f, _ in ga_generated_skill_list_with_fitness
    ]
    ga_skill_variance = np.var(ga_generated_skill_fitness_list)
    filtered_ga_skill_results = [
        (f, s) for f, s in ga_generated_skill_list_with_fitness if f > -200
    ]

    unique_archetypes = len(set(s.archetype_id for _, s in filtered_ga_skill_results))

    print("GA variance:", ga_skill_variance)
    print("GA mean:", np.mean(ga_generated_skill_fitness_list))
    print("GA max:", np.max(ga_generated_skill_fitness_list))
    print("GA min:", np.min(ga_generated_skill_fitness_list))
    print("GA Filtered count:", len(filtered_ga_skill_results))
    print("GA Unique archetypes in filtered results:", unique_archetypes)

    plt.hist(ga_generated_skill_fitness_list, bins=50)
    plt.show()

    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time:.6f} seconds")


if __name__ == "__main__":
    main()
