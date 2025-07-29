import re

def parse_duration(value: str):
    value = value.lower()
    hours = re.search(r'(\d+)\s*h', value)
    minutes = re.search(r'(\d+)\s*min', value)

    total = 0
    if hours:
        total += int(hours.group(1)) * 60
    if minutes:
        total += int(minutes.group(1))
    return total if total > 0 else None