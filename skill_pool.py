from dataclasses import dataclass, field
from typing import Dict, List
from models import Skill


@dataclass
class SkillPool:
    skills: List[Skill] = field(default_factory=list)
    archetype_map: Dict[str, List[Skill]] = field(default_factory=dict)

    def add_skill(self, skill: Skill):
        self.skills.append(skill)

        if skill.archetype_id not in self.archetype_map:
            self.archetype_map[skill.archetype_id] = []

        self.archetype_map[skill.archetype_id].append(skill)

    def get_total_skills(self) -> int:
        return len(self.skills)

    def get_total_archetypes(self) -> int:
        return len(self.archetype_map)

    def get_skills_by_archetype(self, archetype_id: str) -> List[Skill]:
        return self.archetype_map.get(archetype_id, [])