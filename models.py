from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Entry:
    entry_type: str
    tier: int
    value: int
    slot_id: int


@dataclass
class Skill:
    entries: List[Entry]
    aggregated_params: Dict[str, float]
    archetype_id: str
