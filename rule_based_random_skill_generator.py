import random
import config

from skill_builder import SkillBuilder
from entry_generator import generate_entry, append_entries
from pure_random_skill_generator import extend_skeleton
from models import Entry


# using gauss distribution to avoid over homogeneous when using rule based random generation
def sample_tier_by_gauss(
    mean: float, sigma: float, max_tier: int, min_tier: int = 1
) -> int:
    """
    Sample a tier around a fold-centered mean using Gaussian distribution.
    Then clamp into valid tier range.
    """
    tier = round(random.gauss(mean, sigma))
    tier = max(min_tier, min(max_tier, tier))
    return tier


def generate_rule_based_random_skill(
    modifier_space: dict,
    skeleton_constraints: dict,
    skill_builder: SkillBuilder,
    tier_mean: float,
    sigma: float = 0.8,
):
    min_skeleton = skill_builder.generate_min_skeleton()
    extended_skeleton = extend_skeleton(
        modifier_space, skeleton_constraints, min_skeleton
    )

    entries = fill_skeleton(
        modifier_space=modifier_space,
        skeleton=extended_skeleton,
        tier_mean=tier_mean,
        sigma=sigma,
    )

    return skill_builder.build_skill(entries)


def fill_skeleton(
    modifier_space: dict,
    skeleton: list[str],
    tier_mean: float,
    sigma: float,
) -> list[Entry]:
    entries: list[Entry] = []

    for entry_type in skeleton:
        tier = sample_tier_by_gauss(
            mean=tier_mean,
            sigma=sigma,
            max_tier=config.TOTAL_TIERS,
        )

        entries.append(
            generate_entry(
                modifier_space=modifier_space,
                entry_type=entry_type,
                tier=tier,
            )
        )

    return entries
