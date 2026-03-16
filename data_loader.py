import config
from utility import load_json


def load_modifier_space(path=config.SKILL_MODIFIER_SPACE):
    return load_json(path)


def load_skeleton_constraints(path=config.SKILL_SKELETON_CONSTRAINT_SPACE):
    return load_json(path)


def load_charater_base_modifier(path=config.CHARACTER_BASIC_MODIFIERS):
    return load_json(path)


def load_data():
    return (
        load_charater_base_modifier(path=config.CHARACTER_BASIC_MODIFIERS),
        load_modifier_space(path=config.SKILL_MODIFIER_SPACE),
        load_skeleton_constraints(path=config.SKILL_SKELETON_CONSTRAINT_SPACE)
    )
