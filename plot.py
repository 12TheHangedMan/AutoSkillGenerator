from utility import *
import time
import os
from datetime import datetime

from skill_builder import SkillBuilder
from pure_random_skill_generator import generate_pure_random_skill
from rule_based_random_skill_generator import generate_rule_based_random_skill
from delta_greedy_skill_generator import generate_delta_greedy_skill
from ga_skill_generator import generate_ga_skill
import config
from data_loader import load_data
from fitness import calculate_fitness
from skill_simulator import SkillSimulator

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random

random.seed(config.SEED)
np.random.seed(config.SEED)

FILTER_FITNESS_THRESHOLD = -200


def summarize_results(fitness_list, results, method_name, template_name):
    """
    Return a summary dictionary for one method under one template.
    """
    variance = np.var(fitness_list)
    mean_val = np.mean(fitness_list)
    max_val = np.max(fitness_list)
    min_val = np.min(fitness_list)

    filtered_results = [(f, s) for f, s in results if f > FILTER_FITNESS_THRESHOLD]
    unique_archetypes = len(set(s.archetype_id for _, s in filtered_results))

    print(f"\n[{template_name}] {method_name}")
    print("variance:", variance)
    print("mean:", mean_val)
    print("max:", max_val)
    print("min:", min_val)
    print("Filtered count:", len(filtered_results))
    print("Unique archetypes in filtered results:", unique_archetypes)

    return {
        "template": template_name,
        "method": method_name,
        "variance": variance,
        "mean": mean_val,
        "max": max_val,
        "min": min_val,
        "filtered_count": len(filtered_results),
        "unique_archetypes": unique_archetypes,
    }


def save_plots(df, output_dir):
    """
    Save comparison plots from the final dataframe.
    """
    if df.empty:
        print("No data to plot.")
        return

    # For mean, closer to zero is better, so use abs(mean)
    df = df.copy()
    df["mean_abs"] = df["mean"].abs()

    # 1) Filtered count
    pivot_filtered = df.pivot(index="template", columns="method", values="filtered_count")
    ax = pivot_filtered.plot(kind="bar", figsize=(10, 6))
    ax.set_title("Filtered Count Comparison")
    ax.set_ylabel("Filtered Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "filtered_count_comparison.png"), dpi=200)
    plt.close()

    # 2) Absolute mean
    pivot_mean = df.pivot(index="template", columns="method", values="mean_abs")
    ax = pivot_mean.plot(kind="bar", figsize=(10, 6))
    ax.set_title("Absolute Mean Comparison (Lower is Better)")
    ax.set_ylabel("|Mean Fitness|")
    ax.set_yscale("log")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "mean_abs_comparison.png"), dpi=200)
    plt.close()

    # 3) Variance
    pivot_var = df.pivot(index="template", columns="method", values="variance")
    ax = pivot_var.plot(kind="bar", figsize=(10, 6))
    ax.set_title("Variance Comparison (Lower is Better)")
    ax.set_ylabel("Variance")
    ax.set_yscale("log")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "variance_comparison.png"), dpi=200)
    plt.close()

    # 4) Max fitness
    pivot_max = df.pivot(index="template", columns="method", values="max")
    ax = pivot_max.plot(kind="bar", figsize=(10, 6))
    ax.set_title("Max Fitness Comparison (Higher is Better)")
    ax.set_ylabel("Max Fitness")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "max_fitness_comparison.png"), dpi=200)
    plt.close()

    print("Plots saved.")


def plot():
    total_start_time = time.perf_counter()

    # Create output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("analysis_outputs", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    base_character_status_templates, modifier_space, skeleton_constraints = load_data()

    templates = {
        "basic": base_character_status_templates["basic_template"],
        "berserk": base_character_status_templates["berserk_template"],
        "glass_cannon": base_character_status_templates["glass_cannon_template"],
        "tank": base_character_status_templates["tank_template"],
        "elite": base_character_status_templates["elite_template"],
        "boss": base_character_status_templates["boss_template"],
    }

    # Builder / dummy
    skill_builder = SkillBuilder(modifier_space, skeleton_constraints)

    dummy_skill_data = load_json(config.DUMMY_SKILL)
    dummy_entries = skill_builder.load_entries_from_dict(dummy_skill_data)
    dummy_skill = skill_builder.load_skill_from_dict(dummy_skill_data)

    # Collect all summary rows here
    all_results = []

    for template_name, target_base_character_status in templates.items():
        print("\n" + "=" * 70)
        print(f"Running template: {template_name}")
        print("=" * 70)

        template_start_time = time.perf_counter()

        # Keep your original simulator setting
        ss = SkillSimulator(
            templates["basic"],   # source/basic template as in your original code
            target_base_character_status,
            4
        )

        # =========================================================
        # 1) Pure random
        # =========================================================
        pure_random_results = []

        for _ in range(config.SAMPLES_PER_FOLD):
            test_unit_skill = generate_pure_random_skill(
                modifier_space, skeleton_constraints, skill_builder
            )
            fitness = calculate_fitness(ss, test_unit_skill, dummy_skill)
            pure_random_results.append((fitness, test_unit_skill))

        pure_random_skill_fitness_list = [f for f, _ in pure_random_results]
        pure_random_skill_list = [s for _, s in pure_random_results]

        top10_random = sorted(pure_random_results, key=lambda x: x[0], reverse=True)[:10]
        print(f"\nTop 10 pure random skills for template [{template_name}]")
        for f, s in top10_random:
            print("fitness:", f)
            print("params:", s.get_params())

        all_results.append(
            summarize_results(
                pure_random_skill_fitness_list,
                pure_random_results,
                "pure_random",
                template_name,
            )
        )

        # =========================================================
        # 2) Rule-based (choose best fold by mean)
        # =========================================================
        rule_base_results = {}
        best_fold_results = []
        rule_base_best_mean = -float("inf")
        best_fold = None

        fold_range = range(1, config.TOTAL_TIERS + 1)

        for fold in fold_range:
            rule_base_results_per_fold = []
            rule_based_skill_fitness_list_per_fold = []

            for _ in range(config.SAMPLES_PER_FOLD):
                test_unit_skill = generate_rule_based_random_skill(
                    modifier_space, skeleton_constraints, skill_builder, fold
                )
                fitness = calculate_fitness(ss, test_unit_skill, dummy_skill)
                rule_based_skill_fitness_list_per_fold.append(fitness)
                rule_base_results_per_fold.append((fitness, test_unit_skill))

            fold_mean = np.mean(rule_based_skill_fitness_list_per_fold)
            fold_var = np.var(rule_based_skill_fitness_list_per_fold)

            print(f"fold {fold}: mean={fold_mean}, var={fold_var}")

            if fold_mean > rule_base_best_mean:
                rule_base_best_mean = fold_mean
                best_fold_results = rule_base_results_per_fold
                best_fold = fold

            rule_base_results[fold] = rule_base_results_per_fold

        best_rule_based_skill_fitness_list = [f for f, _ in best_fold_results]

        print(f"\n[{template_name}] best fold: {best_fold}")

        all_results.append(
            summarize_results(
                best_rule_based_skill_fitness_list,
                best_fold_results,
                "best_fold",
                template_name,
            )
        )

        # =========================================================
        # 3) GA
        # =========================================================
        total_runs = 10
        ga_generated_skill_list_with_fitness = []

        # If you want to use pure_random_skill_list as initial population later,
        # keep it here. Your original code created ga_population but did not use it.
        # ga_population = pure_random_skill_list

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

        ga_generated_skill_fitness_list = [f for f, _ in ga_generated_skill_list_with_fitness]

        best_by_archetype = {}
        for f, s in ga_generated_skill_list_with_fitness:
            key = s.archetype_id
            if key not in best_by_archetype or f > best_by_archetype[key][0]:
                best_by_archetype[key] = (f, s)

        unique_list = list(best_by_archetype.values())
        top_10_ga = sorted(unique_list, key=lambda x: x[0], reverse=True)[:10]

        print(f"\nTop 10 GA skills for template [{template_name}]")
        for f, s in top_10_ga:
            print("fitness:", f)
            print("params:", s.get_params())

        all_results.append(
            summarize_results(
                ga_generated_skill_fitness_list,
                ga_generated_skill_list_with_fitness,
                "GA",
                template_name,
            )
        )

        # =========================================================
        # 4) Delta-Greedy
        # =========================================================
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

        filtered_delta_greedy_skill_results = [
            (f, s) for f, s in delta_greedy_skill_results if f > FILTER_FITNESS_THRESHOLD
        ]
        top_10_delta = sorted(
            filtered_delta_greedy_skill_results,
            key=lambda x: x[0],
            reverse=True
        )[:10]

        print(f"\nTop 10 Delta-Greedy skills for template [{template_name}]")
        for f, s in top_10_delta:
            print("fitness:", f)
            print("params:", s.get_params())

        all_results.append(
            summarize_results(
                delta_greedy_skill_fitness_list,
                delta_greedy_skill_results,
                f"Delta-Greedy(c={c})",
                template_name,
            )
        )

        template_end_time = time.perf_counter()
        print(
            f"\nTemplate [{template_name}] finished in "
            f"{template_end_time - template_start_time:.6f} seconds"
        )

    # =========================================================
    # Save summary csv
    # =========================================================
    df = pd.DataFrame(all_results)
    csv_path = os.path.join(output_dir, "results_summary.csv")
    df.to_csv(csv_path, index=False)

    print("\nSummary dataframe:")
    print(df)

    # =========================================================
    # Save plots
    # =========================================================
    save_plots(df, output_dir)

    total_end_time = time.perf_counter()
    print(f"\nAll done. Total time: {total_end_time - total_start_time:.6f} seconds")
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    plot()