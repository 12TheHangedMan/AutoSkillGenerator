from combat_simulator import CombatSimulator
from actor import Actor
from utility import *
import time
from skill_builder import SkillBuilder
from pure_random_skill_generator import generate_pure_random_skill
import config
from data_loader import load_data

def main():
    start_time = time.perf_counter()

    base_character_status, modifier_space, skeleton_constraints = load_data()

    skill_builder = SkillBuilder(modifier_space, skeleton_constraints)
    test_unit_skill = generate_pure_random_skill(modifier_space, skeleton_constraints, skill_builder)

    dummy_skill_data = load_json(config.DUMMY_SKILL)
    dummy_skill = skill_builder.load_skill_from_dict(dummy_skill_data)

    test_unit = Actor(test_unit_skill, base_character_status)
    dummy = Actor(dummy_skill, base_character_status)

    cs = CombatSimulator(test_unit, dummy)
    cs.simulate_combat()
    cs.report_dmg()

    print(dummy.get_character_skill().get_params())

    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    main()