#!/usr/bin/env python3
"""Helpers to load `Bio` instances from the `bio.csv` file.

Provides `load_bio_instances(csv_path: str) -> list[Bio]` which returns
a list of `Bio` objects (from `models.py`).
"""
from typing import List, Optional
import csv

from models import Bio


def _to_int(val: Optional[str]) -> Optional[int]:
    if val is None:
        return None
    v = str(val).strip()
    if v == "":
        return None
    try:
        return int(v)
    except ValueError:
        # guard: remove non-digit characters and try again
        digits = ''.join(ch for ch in v if ch.isdigit())
        return int(digits) if digits else None


def load_bio_instances(csv_path: str = "bio.csv") -> List[Bio]:
    """Read `csv_path` and return a list of `Bio` instances.

    The function attempts to coerce numeric fields (`jersey_number`, `weight`)
    to integers and leaves other fields as strings or None.
    """
    instances: List[Bio] = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            b = Bio(
                first_name=(row.get('first_name') or '').strip() or None,
                last_name=(row.get('last_name') or '').strip() or None,
                position=(row.get('position') or '').strip() or None,
                jersey_number=_to_int(row.get('jersey_number')),
                weight=_to_int(row.get('weight')),
                height=(row.get('height') or '').strip() or None,
                class_year=(row.get('class_year') or '').strip() or None,
                hometown=(row.get('hometown') or '').strip() or None,
                high_school=(row.get('high_school') or '').strip() or None,
            )
            instances.append(b)
    return instances


if __name__ == '__main__':
    lst = load_bio_instances()
    print(f'Loaded {len(lst)} Bio instances')
