from dataclasses import dataclass, field
from typing import List, Dict
import hashlib


@dataclass(frozen=True)
class Entry:
    entry_type: str
    tier: int
    value: int


@dataclass(frozen=True)
class Skill:
    skill_id: int
    entries: List[Entry]

    archetype_id: str = field(init=False)
    aggregated_params: Dict[str, int] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "aggregated_params", self._aggregate_entries())
        object.__setattr__(self, "archetype_id", self._build_archetype_id())

    def _aggregate_entries(self) -> Dict[str, int]:
        """
        Aggregate all entry values into one parameter dictionary.

        Example:
            damage_range -> damage
            cost_range -> cost
            fatigue_range -> fatigue
        """
        result: Dict[str, int] = {}

        for entry in self.entries:
            result[entry.entry_type] = result.get(entry.entry_type, 0) + entry.value

        return result

    def _build_archetype_signature(self) -> str:
        """
        Build a stable structure signature based only on:
            (entry_type, tier)

        Notes:
        - value does NOT affect archetype identity
        - entry order does NOT affect archetype identity
        """
        signature_parts = [f"{entry.entry_type}:{entry.tier}" for entry in self.entries]
        signature_parts.sort()
        return "|".join(signature_parts)

    def _build_archetype_id(self) -> str:
        signature = self._build_archetype_signature()
        return hashlib.sha1(signature.encode()).hexdigest()[:12]

    def get_param(self, key: str, default: int = 0) -> int:
        return self.aggregated_params.get(key, default)
    
    def get_params(self) -> dict:
        return dict(self.aggregated_params)
    
    def get_entries(self) -> list:
        return self.entries

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "archetype_id": self.archetype_id,
            "entries": [
                {"entry_type": e.entry_type, "tier": e.tier, "value": e.value}
                for e in self.entries
            ],
            "aggregated_params": dict(self.aggregated_params),
        }
