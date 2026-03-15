from models import Skill, Entry
from entry_generator import generate_entries
from skill_skeleton import generate_skill_skeleton
from utility import load_json
import config


def load_modifier_space(path="skill_modifier_space.json"):
    return load_json(path)


def load_skeleton_constraints(path="skill_skeleton_constraints.json"):
    return load_json(path)


def generate_skill_random(modifier_space, skeleton_constraints):
    skill_skeleton = generate_skill_skeleton(modifier_space, skeleton_constraints)
    entries = generate_entries(modifier_space, skill_skeleton)

    sb = SkillBuilder(modifier_space, skeleton_constraints)

    return sb.build_skill(entries)


class SkillBuilder:
    def __init__(self, modifier_space: dict, skeleton_constraints: dict):
        self.modifier_space = modifier_space
        self.skeleton_constraints = skeleton_constraints
        self.skill_id_counter = config.SKILL_ID_START 

    # skill id is for future extension when implying skill names, not a hard requirement in this experiment
    def new_skill_id(self) -> int:
        self.skill_id_counter += 1
        return self.skill_id_counter

    def build_skill(self, entries: list[Entry], skill_id=None) -> Skill:
        if skill_id is None:
            skill_id = self.new_skill_id()
        return Skill(skill_id=skill_id, entries=entries)

    # generate the min skeleton based on the skill skeleton constraints
    def generate_min_skeleton(self) -> list[str]: 
        constraints = self.skeleton_constraints["constraints"]
        total_slots = self.skeleton_constraints["total_slots"]

        skeleton = []

        for item in constraints:
            entry_type = item["entry_type"]
            min_count = item["min"]

            for _ in range(min_count):
                skeleton.append(entry_type)

        if len(skeleton) > total_slots:
            raise ValueError("Minimum constraints exceed total_slots.")

        return skeleton
    
    def load_skill_from_dict(self, raw_skill_data: dict) -> Skill:
        entries = [
            Entry(
                entry_type=raw_entry["entry_type"],
                tier=raw_entry["tier"],
                value=raw_entry["value"],
            )
            for raw_entry in raw_skill_data.get("entries", [])
        ]

        skill_id=raw_skill_data.get("skill_id")

        return self.build_skill(entries=entries, skill_id=skill_id)