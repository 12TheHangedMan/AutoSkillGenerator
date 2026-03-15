import numpy as np
import json


# generate float levels
def generate_float_levels(min_val, max_val, step):
    return list(range(min_val, max_val + step, step))


# generate integer levels
def generate_levels(min_val, max_val, step):
    return list(range(min_val, max_val + 1, step))


def generate_groups(arr : np.ndarray, group_count: int):
    return np.array_split(arr, group_count)


# generate random integer value
def generate_modifier(range: dict[str, int], tier: int):
    return 0


# damage calculation
def damage_ratio_calculation(attack: float, defense: float):
    total = attack + defense
    if total <= 0.0:
        return 0.0
    return attack / total


def hit_ratio_calculation(hit_rate, dodge_rate):
    total = hit_rate + dodge_rate
    if total <= 0.0:
        return 0.0
    return hit_rate / total


def critical_ratio_calculation(critical_rate, anti_critical):
    total = critical_rate + anti_critical
    if total <= 0.0:
        return 0.0
    return critical_rate / total


def damage_output(raw_damage, damage_ratio, critical_multiplier):
    final_damage = raw_damage * damage_ratio * (1 + critical_multiplier / 100)
    return final_damage


def generate_skill_id() -> str:
    return "0"


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