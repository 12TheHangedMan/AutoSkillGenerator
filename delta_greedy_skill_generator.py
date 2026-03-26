import random

from models import Entry, Skill
from skill_builder import SkillBuilder
from skill_simulator import SkillSimulator
from entry_generator import generate_entry
from fitness import calculate_fitness_with_entries
from ga_skill_generator import update_candidate_entry_types


def generate_delta_greedy_skill(
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
    skill_simulator: SkillSimulator,
    target_entries: list[Entry],
    c: float = 1.0,
    samples_per_type: int = 1,  # set 1 to remain fairness when compare with other algorithms
) -> Skill:
    entries = generate_delta_greedy_entries(
        modifier_space=modifier_space,
        skeleton_constraints=skeleton_constraints,
        skill_builder=skill_builder,
        skill_simulator=skill_simulator,
        target_entries=target_entries,
        c=c,
        samples_per_type=samples_per_type,
    )
    return skill_builder.build_skill(entries)


def generate_delta_greedy_entries(
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
    skill_simulator: SkillSimulator,
    target_entries: list[Entry],
    c: float = 1.0,
    samples_per_type: int = 1,
) -> list[Entry]:
    """
    Delta-greedy / soft-greedy generator.
    c in [0, 1]:
    Range-threshold selection.

    c = 1:
        pure greedy
    c < 1:
        allow candidates within a relative band from best
    c = 0:
        pure random
    """
    if c < 0:
        c = 0.0
    elif c > 1:
        c = 1.0

    min_skeleton = skill_builder.get_min_skeleton()
    max_slots = skeleton_constraints["max_slots"]

    # required prefix
    entries = [
        generate_entry(modifier_space=modifier_space, entry_type=entry_type)
        for entry_type in min_skeleton
    ]

    # reading constraints for entries
    remaining_quota = {
        entry_type: rule["max"]
        for entry_type, rule in skeleton_constraints["constraints"].items()
    }

    candidate_entry_types = set(modifier_space.keys())

    # consume required prefix quotas
    for entry_type in min_skeleton:
        update_candidate_entry_types(
            entry_type=entry_type,
            candidate_entry_types=candidate_entry_types,
            remaining_quota=remaining_quota,
        )

    while len(entries) < max_slots:
        scored_candidate_entries = collect_candidate_entries_with_fitness(
            current_entries=entries,
            modifier_space=modifier_space,
            candidate_entry_types=candidate_entry_types,
            skill_simulator=skill_simulator,
            target_entries=target_entries,
            samples_per_type=samples_per_type,
        )

        chosen_entry = select_entry_by_delta_greedy(
            candidate_scored_entries=scored_candidate_entries, c=c, mode="top_k"
        )

        entries.append(chosen_entry)

        update_candidate_entry_types(
            entry_type=chosen_entry.entry_type,
            candidate_entry_types=candidate_entry_types,
            remaining_quota=remaining_quota,
        )

    return entries


def collect_candidate_entries_with_fitness(
    current_entries: list[Entry],
    modifier_space: dict,
    candidate_entry_types: set[str],
    skill_simulator: SkillSimulator,
    target_entries: list[Entry],
    samples_per_type: int,
) -> list[tuple[float, Entry]]:
    """
    Generate sampled candidates from currently valid entry types,
    then score them using full simulator-based fitness.
    """
    if not candidate_entry_types:
        raise ValueError("No valid entry types available for delta greedy expansion.")

    scored_candidate_entries: list[tuple[float, Entry]] = []

    for entry_type in candidate_entry_types:
        for _ in range(samples_per_type):
            candidate_entry = generate_entry(
                modifier_space=modifier_space,
                entry_type=entry_type,
            )

            trial_entries = current_entries + [candidate_entry]

            fitness = calculate_fitness_with_entries(
                skill_simulator=skill_simulator,
                attacker_skill_entries=trial_entries,
                target_skill_entries=target_entries,
            )

            scored_candidate_entries.append((fitness, candidate_entry))

    return scored_candidate_entries


def select_entry_by_delta_greedy(
    candidate_scored_entries: list[tuple[float, Entry]], c: float, mode: str = "top_k"
):
    """
    mode:
    1. top_k: select the top k candidates and pick one from them. k is determined by c
    2. score_threshold: select the top candidates above score_threshold and pick one from them. score_threshold is determined by c
    """
    legal_modes = {"top_k", "score_threshold"}

    if mode not in legal_modes:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of {legal_modes}.")

    if mode == "top_k":
        return select_entry_by_delta_greedy_top_k(
            candidate_scored_entries=candidate_scored_entries, c=c
        )
    elif mode == "score_threshold":
        return select_entry_by_delta_greedy_score_threshold(
            candidate_scored_entries=candidate_scored_entries, c=c
        )


def select_entry_by_delta_greedy_score_threshold(
    candidate_scored_entries: list[tuple[float, Entry]],
    c: float,
) -> Entry:
    if not candidate_scored_entries:
        raise ValueError("No candidate entries to select from.")

    best_fitness = max(f for f, _ in candidate_scored_entries)
    worst_fitness = min(f for f, _ in candidate_scored_entries)

    score_range = best_fitness - worst_fitness

    if score_range <= 1e-12:
        return random.choice(candidate_scored_entries)[1]

    threshold = best_fitness - (1.0 - c) * score_range

    filtered_candidates = [
        (fitness, entry)
        for fitness, entry in candidate_scored_entries
        if fitness >= threshold
    ]

    if not filtered_candidates:
        best_candidates = [
            (fitness, entry)
            for fitness, entry in candidate_scored_entries
            if fitness == best_fitness
        ]
        return random.choice(best_candidates)[1]

    return random.choice(filtered_candidates)[1]


def select_entry_by_delta_greedy_top_k(
    candidate_scored_entries: list[tuple[float, Entry]],
    c: float,
) -> Entry:
    if not candidate_scored_entries:
        raise ValueError("No candidate entry")

    sorted_candidates = sorted(
        candidate_scored_entries, key=lambda x: x[0], reverse=True
    )
    num_candidates = len(sorted_candidates)

    # Compute k: higher c -> smaller k (more greedy)
    k = 1 + round((1 - c) * (num_candidates - 1))

    top_k_candidates = sorted_candidates[:k]
    return random.choice(top_k_candidates)[1]
