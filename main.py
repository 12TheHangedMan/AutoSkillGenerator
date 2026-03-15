from combat_simulator import CombatSimulator
from actor import Actor, load_charater_base_modifier
from utility import *
import time
from skill_builder import load_modifier_space, load_skeleton_constraints, generate_skill_random, SkillBuilder


def main():
    start_time = time.perf_counter()

    modifier_space = load_modifier_space()
    skeleton_constraints = load_skeleton_constraints()
    test_unit_skill = generate_skill_random(modifier_space, skeleton_constraints)

    skill_builder = SkillBuilder(modifier_space, skeleton_constraints)

    dummy_skill_data = load_json("dummy_skill.json")
    dummy_skill = skill_builder.load_skill_from_dict(dummy_skill_data)

    base_character_status = load_charater_base_modifier()

    test_unit = Actor(test_unit_skill, base_character_status)
    dummy = Actor(dummy_skill, base_character_status)

    cs = CombatSimulator(test_unit, dummy)
    cs.simulate_combat()
    cs.report_dmg()

    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    main()