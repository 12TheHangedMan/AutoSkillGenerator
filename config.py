# not in game parameters
SEED = 10087
SKILL_SKELETON_CONSTRAINT_SPACE = "skill_skeleton_constraint_space.json"
CHARACTER_BASIC_MODIFIERS = "character_basic_modifier.json"
SKILL_MODIFIER_SPACE = "skill_modifier_space.json"
DUMMY_SKILL = "dummy_skill.json"
EMPTY_PADDING = "skill_empty_space"

# in game parameters
# not starting from 0, saving space for manual input testing skills
SKILL_ID_START = 100

# skill generation parameters
GA_POPULATION_SIZE = 100
GA_GENERATIONS = 50
GA_MUTATION_RATE = 0.15
GA_ELITE_SIZE = 10

# game evaluation parameters
SAMPLES_PER_FOLD = 1000

# game design parameters
TOTAL_TIERS = 4

MAX_SLOTS = 8

TOTAL_ROUNDS = 3

TARGET_ROUNDS = 4
TARGET_HP = 1000
