#!/usr/bin/env python3
"""Load `Stats` instances from `stats.csv`.

Provides `load_stats_instances(csv_path: str) -> list[Stats]`.
"""
from typing import List, Optional
import csv

from models import Stats


def _to_int(val: Optional[str]) -> Optional[int]:
    if val is None:
        return None
    v = str(val).strip()
    if v == "":
        return None
    try:
        return int(v)
    except ValueError:
        # handle values like '-14' or '7-22' (keep numeric part when sensible)
        if v.startswith('-') and v[1:].isdigit():
            return int(v)
        digits = ''.join(ch for ch in v if ch.isdigit() or ch == '-')
        try:
            return int(digits) if digits not in ('', '-') else None
        except ValueError:
            return None


def _to_float(val: Optional[str]) -> Optional[float]:
    if val is None:
        return None
    v = str(val).strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        # allow leading '.' like '.125'
        if v.startswith('.'):
            try:
                return float('0' + v)
            except ValueError:
                return None
        return None


def load_stats_instances(csv_path: str = "stats.csv") -> List[Stats]:
    """Read `csv_path` and return a list of `Stats` instances.

    Header normalization: column names with '-' are converted to '_', so
    `PN-PIM` becomes `PN_PIM` when mapping to the `Stats` attributes.
    """
    instances: List[Stats] = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # normalize keys: strip and replace '-' with '_'
            norm = {k.strip().replace('-', '_'): (v.strip() if v is not None else '') for k, v in row.items()}

            s = Stats(
                jersey_number=_to_int(norm.get('jersey_number')),
                first_name=(norm.get('first_name') or None),
                last_name=(norm.get('last_name') or None),
                GP=_to_int(norm.get('GP')),
                G=_to_int(norm.get('G')),
                A=_to_int(norm.get('A')),
                PTS=_to_int(norm.get('PTS')),
                SH=_to_int(norm.get('SH')),
                SH_PCT=_to_float(norm.get('SH_PCT')),
                Plus_Minus=_to_int(norm.get('Plus_Minus')),
                PPG=_to_int(norm.get('PPG')),
                SHG=_to_int(norm.get('SHG')),
                FG=_to_int(norm.get('FG')),
                GWG=_to_int(norm.get('GWG')),
                GTG=_to_int(norm.get('GTG')),
                OTG=_to_int(norm.get('OTG')),
                HTG=_to_int(norm.get('HTG')),
                UAG=_to_int(norm.get('UAG')),
                PN_PIM=(norm.get('PN_PIM') or None),
                MIN=_to_int(norm.get('MIN')),
                MAJ=_to_int(norm.get('MAJ')),
                OTH=_to_int(norm.get('OTH')),
                BLK=_to_int(norm.get('BLK')),
            )
            instances.append(s)
    return instances


if __name__ == '__main__':
    lst = load_stats_instances()
    print(f'Loaded {len(lst)} Stats instances')
