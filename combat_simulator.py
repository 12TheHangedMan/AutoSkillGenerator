
from actor import Actor
import config

class CombatSimulator:
    def __init__(self, actors : list[Actor], total_rounds = config.TOTAL_ROUNDS):
        self.actors = actors
        self.remaining_rounds = total_rounds

    def simulate_combat(self):
        while(self.remaining_rounds > 0):
            for actor in self.actors:
                actor.move()

            self.remaining_rounds -= 1
