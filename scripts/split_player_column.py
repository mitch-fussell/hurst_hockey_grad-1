#!/usr/bin/env python3
import csv

IN = 'stats.csv'
OUT = 'stats.csv'

def split_name(player_cell: str):
    # Expect formats like: "Last, First Last, First" or "Last, First"
    if not player_cell:
        return '', ''
    s = player_cell.strip()
    # find first comma
    idx = s.find(',')
    if idx == -1:
        # fallback: try splitting on space
        parts = s.split()
        if len(parts) == 1:
            return '', parts[0]
        return parts[0], parts[-1]
    last = s[:idx].strip()
    remainder = s[idx+1:].strip()
    # remainder often contains repeated name; take first token as first name
    first = remainder.split()[0] if remainder else ''
    return first, last


def main():
    with open(IN, newline='', encoding='utf-8') as f:
        r = csv.reader(f)
        rows = list(r)
    if not rows:
        print('Empty file')
        return

    header = rows[0]
    if 'Player' not in header:
        print('No Player column found; nothing changed')
        return

    pidx = header.index('Player')
    # build new header: replace Player with first_name,last_name (first_name first)
    new_header = header[:pidx] + ['first_name','last_name'] + header[pidx+1:]

    new_rows = [new_header]
    for row in rows[1:]:
        # pad row if shorter than header
        if len(row) < len(header):
            row = row + [''] * (len(header) - len(row))
        player_cell = row[pidx]
        first, last = split_name(player_cell)
        new_row = row[:pidx] + [first, last] + row[pidx+1:]
        new_rows.append(new_row)

    # overwrite the file
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerows(new_rows)

    print('Wrote', len(new_rows)-1, 'rows with split names')


if __name__ == '__main__':
    main()
