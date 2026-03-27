from utility import *
import time
from skill_builder import SkillBuilder
from pure_random_skill_generator import generate_pure_random_skill_from_entries, generate_pure_random_entries
from rule_based_random_skill_generator import generate_rule_based_random_skill
from delta_greedy_skill_generator import generate_delta_greedy_skill
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

FILTER_FITNESS_THRESHOLD = -200


def main():
    start_time = time.perf_counter()

    base_character_status_templates, modifier_space, skeleton_constraints = load_data()

    # 1
    base_character_status_basic_template = base_character_status_templates[
        "basic_template"
    ]

    # 2
    base_character_status_berserk_template = base_character_status_templates[
        "berserk_template"
    ]

    # 3
    base_character_status_glass_cannon_template = base_character_status_templates[
        "glass_cannon_template"
    ]

    # 4
    base_character_status_tank_template = base_character_status_templates[
        "tank_template"
    ]

    # 5
    base_character_status_elite_template = base_character_status_templates[
        "elite_template"
    ]

    # 6
    base_character_status_boss_template = base_character_status_templates[
        "boss_template"
    ]

    target_base_character_status = base_character_status_boss_template

    skill_builder = SkillBuilder(modifier_space, skeleton_constraints)

    dummy_skill_data = load_json(config.DUMMY_SKILL)
    dummy_entries = skill_builder.load_entries_from_dict(dummy_skill_data)
    dummy_skill = skill_builder.load_skill_from_dict(dummy_skill_data)

    ss = SkillSimulator(
        base_character_status_basic_template, target_base_character_status, 4
    )
    pure_random_results = []

    start_time = time.perf_counter()

    # generate random entries pool
    entries_pool = []
    for _ in range(config.SAMPLES_PER_FOLD * 10):
        entries = generate_pure_random_entries(modifier_space, skeleton_constraints, skill_builder)
        entries_pool.append(entries)

    random.shuffle(entries_pool)

    pure_random_samples = random.sample(entries_pool, config.SAMPLES_PER_FOLD)
    
    # pure random skill evaluation and metrics
    for entries in pure_random_samples:
        test_unit_skill = generate_pure_random_skill_from_entries(
            entries, skill_builder
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
        (f, s) for f, s in pure_random_results if f > FILTER_FITNESS_THRESHOLD
    ]
    unique_archetypes = len(
        set(s.archetype_id for _, s in filtered_pure_random_skill_results)
    )

    np_pure_random_skill_fitness_list = np.array(pure_random_skill_fitness_list)

    print("pure_random_skill_variance:", pure_random_skill_variance)
    print("mean:", np.mean(np_pure_random_skill_fitness_list))
    print("max:", np.max(np_pure_random_skill_fitness_list))
    print("min:", np.min(np_pure_random_skill_fitness_list))
    print("Filtered count:", len(filtered_pure_random_skill_results))
    print("Unique archetypes in filtered results:", unique_archetypes)

    # fitness is negtive log (-fitness)
    log_pure_random_fitness = np.log10(-np_pure_random_skill_fitness_list + 1)

    plt.boxplot(log_pure_random_fitness, tick_labels=["Pure-random"])
    plt.title("Log-scaled Loss Pure Random")
    plt.ylabel("Log-scaled Loss")
    plt.show()

    plt.hist(log_pure_random_fitness, bins=50)
    plt.title("Log-scaled Loss Pure Random")
    plt.ylabel("Count")
    plt.xlabel("Log-scaled Loss")
    plt.show()

    # rules based skill evaluation
    rule_base_results = {}
    best_fold_results = []
    rule_base_best_mean = -float("inf")
    best_fold = 0

    fold_range = range(1, config.TOTAL_TIERS + 1)

    for fold in fold_range:
        rule_base_results_per_fold = []
        rule_based_skill_fitness_list = []

        for _ in range(config.SAMPLES_PER_FOLD):
            test_unit_skill = generate_rule_based_random_skill(
                modifier_space, skeleton_constraints, skill_builder, fold
            )
            fitness = calculate_fitness(ss, test_unit_skill, dummy_skill)
            rule_based_skill_fitness_list.append(fitness)
            rule_base_results_per_fold.append((fitness, test_unit_skill))

        mean = np.mean(rule_based_skill_fitness_list)
        var = np.var(rule_based_skill_fitness_list)

        print(f"fold {fold}: mean={mean}, var={var}")

        if mean > rule_base_best_mean:
            rule_base_best_mean = mean
            best_fold_results = rule_base_results_per_fold
            best_fold = fold

        rule_base_results[fold] = rule_base_results_per_fold

    best_rule_based_skill_fitness_list = [f for f, _ in best_fold_results]
    np_best_rule_based_skill_fitness_list = np.array(best_rule_based_skill_fitness_list)

    best_rule_based_skill_variance = np.var(best_rule_based_skill_fitness_list)

    filtered_best_rule_based_skill_results = [
        (f, s) for f, s in best_fold_results if f > FILTER_FITNESS_THRESHOLD
    ]

    unique_archetypes = len(
        set(s.archetype_id for _, s in filtered_best_rule_based_skill_results)
    )

    print("best fold:", best_fold)
    print("best fold variance:", best_rule_based_skill_variance)
    print("mean:", np.mean(np_best_rule_based_skill_fitness_list))
    print("max:", np.max(np_best_rule_based_skill_fitness_list))
    print("min:", np.min(np_best_rule_based_skill_fitness_list))
    print("Filtered count:", len(filtered_best_rule_based_skill_results))
    print("Unique archetypes in filtered results:", unique_archetypes)

    log_best_rule_based_fitness = np.log10(-np_best_rule_based_skill_fitness_list + 1)

    plt.boxplot(log_best_rule_based_fitness, tick_labels=["Rule-based"])
    plt.title("Log-scaled Loss Weak Rules Based")
    plt.ylabel("Log-scaled Loss")
    plt.show()

    plt.hist(log_best_rule_based_fitness, bins=50)
    plt.title("Log-scaled Loss Weak Rules Based")
    plt.ylabel("Count")
    plt.xlabel("Log-scaled Loss")
    plt.show()

    # GA skill generation and evaluation
    ga_generated_skill_list_with_fitness = []

    for i in range(0, len(entries_pool), config.SAMPLES_PER_FOLD):
        population = entries_pool[i: i+config.SAMPLES_PER_FOLD]

        ga_result = generate_ga_skill(
            modifier_space=modifier_space,
            skeleton_constraints=skeleton_constraints,
            skill_builder=skill_builder,
            skill_simulator=ss,
            target_entries=dummy_entries,
            population=population,
        )

        ga_generated_skill_list_with_fitness.extend(ga_result["scored_skills"])

    ga_generated_skill_fitness_list = [
        f for f, _ in ga_generated_skill_list_with_fitness
    ]
    np_ga_fitness = np.array(ga_generated_skill_fitness_list)

    ga_skill_variance = np.var(ga_generated_skill_fitness_list)

    filtered_ga_skill_results = [
        (f, s)
        for f, s in ga_generated_skill_list_with_fitness
        if f > FILTER_FITNESS_THRESHOLD
    ]

    unique_archetypes = len(set(s.archetype_id for _, s in filtered_ga_skill_results))

    best_by_archetype = {}

    for f, s in ga_generated_skill_list_with_fitness:
        key = s.archetype_id
        if key not in best_by_archetype or f > best_by_archetype[key][0]:
            best_by_archetype[key] = (f, s)

    unique_list = list(best_by_archetype.values())

    top_10 = sorted(unique_list, key=lambda x: x[0], reverse=True)[:10]

    for f, s in top_10:
        print(f"skill: {s.get_params()}")

    print("GA variance:", ga_skill_variance)
    print("GA mean:", np.mean(ga_generated_skill_fitness_list))
    print("GA max:", np.max(ga_generated_skill_fitness_list))
    print("GA min:", np.min(ga_generated_skill_fitness_list))
    print("GA Filtered count:", len(filtered_ga_skill_results))
    print("GA Unique archetypes in filtered results:", unique_archetypes)

    log_ga_fitness = np.log10(-np_ga_fitness + 1)

    plt.boxplot(log_ga_fitness, tick_labels=["GA"])
    plt.title("Log-scaled Loss GA")
    plt.ylabel("Log-scaled Loss")
    plt.show()

    plt.hist(log_ga_fitness, bins=50)
    plt.title("Log-scaled Loss GA")
    plt.ylabel("Count")
    plt.xlabel("lLog-scaled Loss")
    plt.show()

    # proxy strong rule based skill generation and evaluation
    delta_greedy_skill_fitness_list = []
    delta_greedy_skill_results = []

    c = 1

    for _ in range(config.SAMPLES_PER_FOLD):
        delta_greedy_skill = generate_delta_greedy_skill(
            modifier_space=modifier_space,
            skeleton_constraints=skeleton_constraints,
            skill_builder=skill_builder,
            skill_simulator=ss,
            target_entries=dummy_entries,
            c=c,
            samples_per_type=1,  # keep it 1 for fairness
        )
        fitness = calculate_fitness(ss, delta_greedy_skill, dummy_skill)
        delta_greedy_skill_fitness_list.append(fitness)
        delta_greedy_skill_results.append((fitness, delta_greedy_skill))

    delta_greedy_skill_variance = np.var(delta_greedy_skill_fitness_list)
    filtered_delta_greedy_skill_results = [
        (f, s) for f, s in delta_greedy_skill_results if f > FILTER_FITNESS_THRESHOLD
    ]

    np_delta_greedy_skill_fitness_list = np.array(delta_greedy_skill_fitness_list)

    top_10 = sorted(
        filtered_delta_greedy_skill_results, key=lambda x: x[0], reverse=True
    )[:10]

    for f, s in top_10:
        print(f"skill: {s.get_params()}")

    unique_archetypes = len(
        set(s.archetype_id for _, s in filtered_delta_greedy_skill_results)
    )
    print(f"Delta-Greedy (c={c}) variance: {delta_greedy_skill_variance}")
    print(f"Delta-Greedy (c={c}) mean: {np.mean(delta_greedy_skill_fitness_list)}")
    print(f"Delta-Greedy (c={c}) max: {np.max(delta_greedy_skill_fitness_list)}")
    print(f"Delta-Greedy (c={c}) min: {np.min(delta_greedy_skill_fitness_list)}")
    print(
        f"Delta-Greedy (c={c}) Filtered count: {len(filtered_delta_greedy_skill_results)}"
    )
    print(
        f"Delta-Greedy (c={c}) Unique archetypes in filtered results: {unique_archetypes}"
    )

    log_delta_greedy = np.log10(-np_delta_greedy_skill_fitness_list + 1)

    plt.boxplot(log_delta_greedy, tick_labels = ["delta_greedy"])
    plt.title("Log-scaled Loss Delta-Greedy")
    plt.ylabel("Log-scaled Loss")
    plt.show()

    plt.hist(log_delta_greedy, bins=50)
    plt.title("Log-scaled Loss Delta-Greedy")
    plt.ylabel("Count")
    plt.xlabel("Log-scaled Loss")
    plt.show()

    data = [
        log_pure_random_fitness,
        log_best_rule_based_fitness,
        log_delta_greedy,
        log_ga_fitness,
    ]

    labels = ["Pure-random", "Rule-based", "Delta-Greedy", "GA"]

    plt.boxplot(data, tick_labels=labels)
    plt.title("Log-scaled Loss Comparison Across Methods")
    plt.ylabel("Log-scaled Loss")
    plt.show()

    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time:.6f} seconds")


if __name__ == "__main__":
    main()
