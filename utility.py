import numpy as np
import json
from models import Entry


# generate float levels
# def generate_float_levels(min_val, max_val, step):
#     return list(range(min_val, max_val + step, step))


# generate integer levels
def generate_levels(min_val: int, max_val: int, step: int) -> list[int]:
    return list(range(min_val, max_val + 1, step))


# def generate_groups(arr: np.ndarray, group_count: int):
#     return np.array_split(arr, group_count)


# damage calculation
def calculate_damage_ratio(attack: float, defense: float) -> float:
    return base_ratio_calculation(attack, defense)


def calculate_hit_ratio(hit_rate, dodge_rate) -> float:
    return base_ratio_calculation(hit_rate, dodge_rate)


def calculate_critical_ratio(critical_rate, anti_critical) -> float:
    return base_ratio_calculation(critical_rate, anti_critical)


def base_ratio_calculation(a: int, b: int) -> float:
    if a < 0 or b < 0:
        raise ValueError("Input values can't be negative.")
    return a / (a + b + 1e-6)


# def damage_output(raw_damage, damage_ratio, critical_multiplier):
#     final_damage = raw_damage * damage_ratio * (1 + critical_multiplier / 100)
#     return final_damage


def split_into_tiers(levels, total_tiers):
    n = len(levels)
    base_size = n // total_tiers
    remainder = n % total_tiers

    tiers = []
    start = 0

    for i in range(total_tiers):
        extra = 1 if i < remainder else 0
        end = start + base_size + extra
        tiers.append(levels[start:end])
        start = end

    return tiers


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {path}")
