from combat_simulator import CombatSimulator
from actor import Actor
from utility import *

import time

def main():
    start_time = time.perf_counter()
    character = Actor(0,0,0)
    dummy = Actor(0,0,0)
    actors = [character, dummy]

    combat_simulator = CombatSimulator(actors)
    combat_simulator.simulate_combat()

    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    main()