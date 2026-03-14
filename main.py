from combat_simulator import CombatSimulator
# from actor import Actor
from utility import *
import config
import time
from skill_builder import generate_skill


def main():
    total_slots = config.TOTAL_SLOTS
    skill = generate_skill(total_slots)
    start_time = time.perf_counter()

    print("Archetype ID:", skill.archetype_id)
    print("Entries:")
    for e in skill.entries:
        print(vars(e))

    print("Aggregated Params:")
    print(skill.archetype_id)
    print(skill.aggregated_params)

    cs = CombatSimulator()
    cs.simulate_combat()
    cs.report_dmg()

    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    main()