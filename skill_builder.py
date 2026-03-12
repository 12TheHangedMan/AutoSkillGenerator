import hashlib
from models import Skill
from entry_generator import load_modifier_space, generate_entries
from entry_validator import validate_entries
from entry_aggregator import aggregate_entries
import config

skill_counter = 0

# use archetype id to determine if it is the same type skill
def build_archetype_id(entries):
    signature_parts = [
        f"{entry.entry_type}:{entry.tier}" for entry in entries
    ]
    # sort to ensure two same skills with different entry orders have same archetype id
    signature_parts.sort()
    signature = "|".join(signature_parts)

    return hashlib.sha1(signature.encode()).hexdigest()[:12]


def generate_skill(total_slots=None):
    if total_slots is None:
        total_slots = config.TOTAL_SLOTS

    modifier_space = load_modifier_space()

    while True:
        entries = generate_entries(modifier_space, total_slots)
        if validate_entries(entries):
            aggregated = aggregate_entries(entries)
            archetype_id = build_archetype_id(entries)

            return Skill(
                entries=entries,
                aggregated_params=aggregated,
                archetype_id=archetype_id
            )