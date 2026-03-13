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
    entries: List[Entry]
    archetype_id: str = field(init=False)
    aggregated_params: Dict[str, int] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "aggregated_params", self._aggregate_entries())
        object.__setattr__(self, "archetype_id", self._build_archetype_id())

    def _aggregate_entries(self) -> Dict[str, int]:
        """
        Aggregate all entry values into a single parameter dictionary.
        Example:
            damage_range -> damage
            cost_range -> cost
            fatigue_range -> fatigue
        """
        result: Dict[str, int] = {}

        for entry in self.entries:
            clean_key = entry.entry_type.replace("_range", "")
            result[clean_key] = result.get(clean_key, 0) + entry.value

        return result

    def _build_archetype_signature(self) -> str:
        """
        Build a stable structure signature using only (entry_type, tier).
        Value differences within the same tier do NOT change archetype.
        Order of entries does NOT matter.
        """
        signature_parts = [
            f"{entry.entry_type}:{entry.tier}"
            for entry in self.entries
        ]
        signature_parts.sort()
        return "|".join(signature_parts)

    def _build_archetype_id(self) -> str:
        signature = self._build_archetype_signature()
        return hashlib.sha1(signature.encode()).hexdigest()[:12]

    def get_param(self, key: str, default: int = 0) -> int:
        return self.aggregated_params.get(key, default)

    def to_dict(self) -> dict:
        return {
            "archetype_id": self.archetype_id,
            "entries": [
                {
                    "entry_type": e.entry_type,
                    "tier": e.tier,
                    "value": e.value
                }
                for e in self.entries
            ],
            "aggregated_params": dict(self.aggregated_params)
        }