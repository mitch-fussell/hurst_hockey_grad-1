#!/usr/bin/env python3
from sqlmodel import Session
from scripts.stats_instances import load_stats_instances
from models import engine, Stats


def update_existing(existing: Stats, new: Stats) -> None:
    """Update non-PK fields of `existing` with values from `new` when present."""
    fields = [
        'jersey_number','GP','G','A','PTS','SH','SH_PCT','Plus_Minus','PPG','SHG','FG',
        'GWG','GTG','OTG','HTG','UAG','PN_PIM','MIN','MAJ','OTH','BLK'
    ]
    for f in fields:
        val = getattr(new, f, None)
        if val is not None and val != '':
            setattr(existing, f, val)


def main():
    stats = load_stats_instances()
    seen = set()
    inserted = 0
    updated = 0

    with Session(engine) as session:
        for s in stats:
            if not s.first_name or not s.last_name:
                print('Skipping row with missing name:', s)
                continue
            key = (s.first_name, s.last_name)
            if key in seen:
                print('Skipping duplicate in CSV:', key)
                continue
            seen.add(key)

            existing = session.get(Stats, key)
            if existing:
                update_existing(existing, s)
                session.add(existing)
                updated += 1
            else:
                session.add(s)
                inserted += 1

        session.commit()

    print(f'Inserted: {inserted}, Updated: {updated}')


if __name__ == '__main__':
    main()
