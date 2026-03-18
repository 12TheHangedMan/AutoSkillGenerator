from models import Skill, Entry
import config


class SkillBuilder:
    def __init__(self, modifier_space: dict, skeleton_constraints: dict):
        self.modifier_space = modifier_space
        self.skeleton_constraints = skeleton_constraints
        self.skill_id_counter = config.SKILL_ID_START

        self.min_skeleton = self._generate_min_skeleton()
        self.min_skeleton_length = len(self.min_skeleton)

    # skill id is designed for extension when implying skill names
    def new_skill_id(self) -> int:
        self.skill_id_counter += 1
        return self.skill_id_counter

    def build_skill(self, entries: list[Entry], skill_id=None) -> Skill:
        # skill id can also be passed in for testing manually created skills
        if skill_id is None:
            skill_id = self.new_skill_id()
        return Skill(skill_id=skill_id, entries=entries)

    # generate the min skeleton based on the skill skeleton constraints
    def _generate_min_skeleton(self) -> list[str]:
        constraints: dict = self.skeleton_constraints["constraints"]
        max_slots: int = self.skeleton_constraints["max_slots"]

        skeleton = []

        for entry_type in constraints.keys():
            constraint: dict = constraints[entry_type]
            min_count: int = constraint.get("min", 0)

            for _ in range(min_count):
                skeleton.append(entry_type)

        if len(skeleton) > max_slots:
            raise ValueError("Minimum constraints exceed total_slots.")

        # sort min skeleton to ensure the essential entry types are in order (for GA crossover)
        return sorted(skeleton)

    def load_skill_from_dict(self, raw_skill_data: dict) -> Skill:
        entries = [
            Entry(
                entry_type=raw_entry["entry_type"],
                tier=raw_entry["tier"],
                value=raw_entry["value"],
            )
            for raw_entry in raw_skill_data.get("entries", [])
        ]

        skill_id = raw_skill_data.get("skill_id")

        return self.build_skill(entries=entries, skill_id=skill_id)
    
    def get_min_skeleton(self) -> list[str]:
        return self.min_skeleton
