from utility import *
import time
from skill_builder import SkillBuilder
from pure_random_skill_generator import (
    generate_pure_random_skill_from_entries,
    generate_pure_random_entries,
)
from rule_guided_delta_greedy import generate_delta_greedy_skill
from ga_skill_generator import generate_ga_skill
import config
from data_loader import load_data
from fitness import calculate_fitness
from skill_simulator import SkillSimulator
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd
import os

all_results = []

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

    target_base_character_status = base_character_status_glass_cannon_template

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
        entries = generate_pure_random_entries(
            modifier_space, skeleton_constraints, skill_builder
        )
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
    
    all_results.append({
    "method": "pure_random",
    "variance": pure_random_skill_variance,
    "mean": np.mean(np_pure_random_skill_fitness_list),
    "max": np.max(np_pure_random_skill_fitness_list),
    "min": np.min(np_pure_random_skill_fitness_list),
    "filtered_count": len(filtered_pure_random_skill_results),
    })

    # fitness is negtive log (-fitness)
    log_pure_random_fitness = np.log10(-np_pure_random_skill_fitness_list + 1)

    # plt.boxplot(log_pure_random_fitness, tick_labels=["Pure-random"])
    # plt.title("Log-scaled Loss Pure Random")
    # plt.ylabel("Log-scaled Loss")
    # plt.show()

    plt.hist(log_pure_random_fitness, bins=50)
    plt.title("Log-scaled Loss Pure Random")
    plt.ylabel("Count")
    plt.xlabel("Log-scaled Loss")
    plt.axvline(
        x=np.log10(-FILTER_FITNESS_THRESHOLD + 1),
        color="red",
        linestyle="--",
        label=f"Threshold (fitness: {FILTER_FITNESS_THRESHOLD})",
    )
    plt.legend()
    plt.show()
    
    # all_results.append({
    # "method": "rule_based",
    # "variance": best_rule_based_skill_variance,
    # "mean": np.mean(np_best_rule_based_skill_fitness_list),
    # "max": np.max(np_best_rule_based_skill_fitness_list),
    # "min": np.min(np_best_rule_based_skill_fitness_list),
    # "filtered_count": len(filtered_best_rule_based_skill_results),
    # })

    # GA skill generation and evaluation
    ga_generated_skill_list_with_fitness = []

    for i in range(0, len(entries_pool), config.SAMPLES_PER_FOLD):
        population = entries_pool[i : i + config.SAMPLES_PER_FOLD]

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

    # plt.boxplot(log_ga_fitness, tick_labels=["GA"])
    # plt.title("Log-scaled Loss GA")
    # plt.ylabel("Log-scaled Loss")
    # plt.show()

    plt.hist(log_ga_fitness, bins=50)
    plt.title("Log-scaled Loss GA")
    plt.ylabel("Count")
    plt.xlabel("lLog-scaled Loss")
    plt.axvline(
        x=np.log10(-FILTER_FITNESS_THRESHOLD + 1),
        color="red",
        linestyle="--",
        label=f"Threshold (fitness: {FILTER_FITNESS_THRESHOLD})",
    )
    plt.legend()
    plt.show()
    
    all_results.append({
    "method": "GA",
    "variance": ga_skill_variance,
    "mean": np.mean(ga_generated_skill_fitness_list),
    "max": np.max(ga_generated_skill_fitness_list),
    "min": np.min(ga_generated_skill_fitness_list),
    "filtered_count": len(filtered_ga_skill_results),
    })

    # proxy strong rule based skill generation and evaluation
    c = 0.75

    fold_range = range(1, config.TOTAL_TIERS + 1)
    log_delta_greedy_all_tiers_fitness_list = []

    for fold in fold_range:
        delta_greedy_skill_fitness_list = []
        delta_greedy_skill_with_fitness_list = []

        for _ in range(config.SAMPLES_PER_FOLD):
            delta_greedy_skill = generate_delta_greedy_skill(
                modifier_space=modifier_space,
                skeleton_constraints=skeleton_constraints,
                skill_builder=skill_builder,
                skill_simulator=ss,
                target_entries=dummy_entries,
                min_skeleton_tier=fold,
                c=c,
            )

            fitness = calculate_fitness(ss, delta_greedy_skill, dummy_skill)
            delta_greedy_skill_fitness_list.append(fitness)
            delta_greedy_skill_with_fitness_list.append((fitness, delta_greedy_skill))

        np_delta_greedy_skill_fitness_list = np.array(delta_greedy_skill_fitness_list)

        delta_greedy_skill_variance = np.var(np_delta_greedy_skill_fitness_list)
        filtered_delta_greedy_skills = [
            (f, s)
            for f, s in delta_greedy_skill_with_fitness_list
            if f > FILTER_FITNESS_THRESHOLD
        ]

        top_10 = sorted(filtered_delta_greedy_skills, key=lambda x: x[0], reverse=True)[
            :10
        ]

        for f, s in top_10:
            print(f"skill: {s.get_params()}")

        unique_archetypes = len(
            set(s.archetype_id for _, s in filtered_delta_greedy_skills)
        )

        print(
            f"Rule-Guided Delta Greedy (c={c}) tier={fold} variance: {delta_greedy_skill_variance}"
        )
        print(
            f"Rule-Guided Delta Greedy (c={c}) tier={fold} mean: {np.mean(delta_greedy_skill_fitness_list)}"
        )
        print(
            f"Rule-Guided Delta Greedy (c={c}) tier={fold} max: {np.max(delta_greedy_skill_fitness_list)}"
        )
        print(
            f"Rule-Guided Delta Greedy (c={c}) tier={fold} min: {np.min(delta_greedy_skill_fitness_list)}"
        )
        print(
            f"Rule-Guided Delta Greedy (c={c}) tier={fold} Filtered count: {len(filtered_delta_greedy_skills)}"
        )
        print(
            f"Rule-Guided Delta Greedy (c={c}) tier={fold} Unique archetypes in filtered results: {unique_archetypes}"
        )
    
        unique_archetypes = len(
            set(s.archetype_id for _, s in filtered_delta_greedy_skills)
        )
        print(f"Delta-Greedy (c={c}) variance: {delta_greedy_skill_variance}")
        print(f"Delta-Greedy (c={c}) mean: {np.mean(delta_greedy_skill_fitness_list)}")
        print(f"Delta-Greedy (c={c}) max: {np.max(delta_greedy_skill_fitness_list)}")
        print(f"Delta-Greedy (c={c}) min: {np.min(delta_greedy_skill_fitness_list)}")
        print(
            f"Delta-Greedy (c={c}) Filtered count: {len(filtered_delta_greedy_skills)}"
        )
        print(
            f"Delta-Greedy (c={c}) Unique archetypes in filtered results: {unique_archetypes}"
        )
        
        all_results.append({
            "method": "delta_greedy",
            "variance": delta_greedy_skill_variance,
            "mean": np.mean(delta_greedy_skill_fitness_list),
            "max": np.max(delta_greedy_skill_fitness_list),
            "min": np.min(delta_greedy_skill_fitness_list),
            "filtered_count": len(filtered_delta_greedy_skills),
        })

        log_delta_greedy = np.log10(-np_delta_greedy_skill_fitness_list + 1)
        log_delta_greedy_all_tiers_fitness_list.append(log_delta_greedy)

        # plt.boxplot(log_delta_greedy, tick_labels=["delta_greedy"])
        # plt.title("Log-scaled Loss Delta-Greedy")
        # plt.ylabel("Log-scaled Loss")
        # plt.show()

        plt.hist(log_delta_greedy, bins=50)
        plt.title(f"Log-scaled Loss Rule-Guided Delta Greedy Tier {fold}")
        plt.ylabel("Count")
        plt.xlabel("Log-scaled Loss")
        plt.axvline(
            x=np.log10(-FILTER_FITNESS_THRESHOLD + 1),
            color="red",
            linestyle="--",
            label=f"Threshold (fitness: {FILTER_FITNESS_THRESHOLD})",
        )
        plt.legend()
        plt.show()

    data = [log_pure_random_fitness]
    data.extend(log_delta_greedy_all_tiers_fitness_list)
    data.append(log_ga_fitness)

    log_delta_greedy_labels = [
        f"RGDG T{idx + 1}"
        for idx in range(len(log_delta_greedy_all_tiers_fitness_list))
    ]

    labels = ["RDM"]
    labels.extend(log_delta_greedy_labels)
    labels.append("GA")

    plt.boxplot(data, tick_labels=labels)
    plt.title("Log-scaled Loss Comparison Across Methods")
    plt.ylabel("Log-scaled Loss")
    plt.axhline(
        y=np.log10(-FILTER_FITNESS_THRESHOLD + 1),
        linestyle="--",
        label=f"Threshold (fitness: {FILTER_FITNESS_THRESHOLD})",
    )
    plt.legend()
    plt.show()

    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time:.6f} seconds")
    
        # ========= SAVE CSV =========
    df = pd.DataFrame(all_results)
    df.to_csv("results_summary.csv", index=False)

    print("\nSaved results_summary.csv")
    print(df)

    # Filtered count
    pivot = df.set_index("method")["filtered_count"]

    pivot.plot(kind="bar")
    plt.title("Filtered Count Comparison")
    plt.ylabel("Filtered Count")
    plt.tight_layout()
    plt.savefig("filtered_count.png")
    plt.show()

    # Mean（重要）
    df["mean_abs"] = df["mean"].abs()

    pivot = df.set_index("method")["mean_abs"]

    pivot.plot(kind="bar")
    plt.title("Mean (Closer to 0 is better)")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig("mean.png")
    plt.show()

    # Variance
    pivot = df.set_index("method")["variance"]

    pivot.plot(kind="bar")
    plt.title("Variance")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig("variance.png")
    plt.show()


if __name__ == "__main__":
    main()
