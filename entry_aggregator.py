def aggregate_entries(entries):
    result = {}

    for entry in entries:
        clean_key = entry.entry_type.replace("_range", "")
        result[clean_key] = result.get(clean_key, 0) + entry.value

    return result