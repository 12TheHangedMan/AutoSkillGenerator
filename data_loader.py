import config
from utility import load_json


def load_modifier_space(path=config.SKILL_MODIFIER_SPACE) -> dict:
    return load_json(path)


def load_skeleton_constraints(path=config.SKILL_SKELETON_CONSTRAINT_SPACE) -> dict:
    return load_json(path)


def load_charater_base_modifier(path=config.CHARACTER_BASIC_MODIFIERS) -> dict:
    return load_json(path)


def load_data() -> tuple[dict, dict, dict]:
    return (
        load_charater_base_modifier(path=config.CHARACTER_BASIC_MODIFIERS),
        load_modifier_space(path=config.SKILL_MODIFIER_SPACE),
        load_skeleton_constraints(path=config.SKILL_SKELETON_CONSTRAINT_SPACE)
    )
