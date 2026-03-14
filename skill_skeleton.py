import random
from dataclasses import dataclass, field
from typing import List
import config


@dataclass(frozen=True)
class SkillSkeleton:
    entry_types: List[str]
    skeleton_id: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "skeleton_id", self._build_skeleton_id())

    def _build_skeleton_id(self) -> str:
        """
        Skeleton identity depends only on entry type multiset.
        Order does not matter.
        """
        parts = sorted(self.entry_types)
        return "|".join(parts)

    def get_total_slots(self) -> int:
        return len(self.entry_types)

    def get_non_damage_count(self) -> int:
        return sum(
            1
            for entry_type in self.entry_types
            if entry_type not in ["damage_range", "cost_range", "fatigue_range"]
        )

    def get_damage_count(self) -> int:
        return self.entry_types.count("damage_range")

    def to_dict(self) -> dict:
        return {
            "skeleton_id": self.skeleton_id,
            "entry_types": list(self.entry_types),
            "total_slots": self.get_total_slots(),
            "damage_count": self.get_damage_count(),
            "non_damage_count": self.get_non_damage_count(),
        }


def get_non_damage_types(modifier_space: dict) -> List[str]:
    return [
        key
        for key in modifier_space.keys()
        if key not in ["damage_range", "cost_range", "fatigue_range"]
    ]


def get_optional_types(modifier_space: dict) -> List[str]:
    return [
        key for key in modifier_space.keys() if key not in config.REQUIRED_ENTRY_TYPES
    ]


def generate_skill_skeleton(
    modifier_space: dict, total_slots: int | None = None
) -> SkillSkeleton:
    """
    Generate a legal skill skeleton under current structural constraints.
    """
    if total_slots is None:
        total_slots = config.TOTAL_SLOTS

    entry_types: List[str] = []

    # 1. required entries
    entry_types.extend(config.REQUIRED_ENTRY_TYPES)

    # 2. minimum active / damage entries
    min_damage = config.MIN_TYPE_COUNTS.get("damage_range", 0)
    entry_types.extend(["damage_range"] * min_damage)

    # 3. minimum non-damage entries
    non_damage_types = get_non_damage_types(modifier_space)
    for _ in range(config.MIN_NON_DAMAGE_COUNT):
        entry_types.append(random.choice(non_damage_types))

    # 4. fill remaining slots with constraint awareness
    remaining_slots = total_slots - len(entry_types)

    if remaining_slots < 0:
        raise ValueError(
            f"Invalid config: minimum required skeleton size ({len(entry_types)}) "
            f"exceeds total_slots ({total_slots})."
        )

    optional_types = get_optional_types(modifier_space)

    for _ in range(remaining_slots):
        current_non_damage = sum(
            1
            for t in entry_types
            if t not in ["damage_range", "cost_range", "fatigue_range"]
        )

        # if already reached max passive / non-damage count,
        # force remaining slots to be damage
        if current_non_damage >= config.MAX_NON_DAMAGE_COUNT:
            entry_types.append("damage_range")
        else:
            entry_types.append(random.choice(optional_types))

    return SkillSkeleton(entry_types=entry_types)
