#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv

URL = 'https://hurstathletics.com/sports/mens-ice-hockey/stats/2025-26'


def get_soup(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')


def find_skater_table(soup):
    # build the actual column order by expanding grouped header cells
    for table in soup.find_all('table'):
        theads = table.select('thead tr')
        if not theads:
            continue
        # parse first header row (which may contain grouped columns with colspan)
        row0 = [(th.get_text(' ', strip=True), int(th.get('colspan') or 1)) for th in theads[0].find_all('th')]
        # collect subcolumns from the second header row if present
        subcols = []
        if len(theads) > 1:
            subcols = [th.get_text(' ', strip=True) for th in theads[1].find_all('th')]

        headers = []
        sub_i = 0
        for text, colspan in row0:
            if colspan > 1 and text in ('Shots', 'Goals', 'Penalties'):
                # expand with next `colspan` subcolumns
                for _ in range(colspan):
                    if sub_i < len(subcols):
                        headers.append(subcols[sub_i])
                    sub_i += 1
            else:
                headers.append(text)
        # if there are remaining subcols (unlikely), append them
        while sub_i < len(subcols):
            headers.append(subcols[sub_i])
            sub_i += 1

        if 'Player' in headers and 'GP' in headers and 'SH%' in headers:
            return table, headers
    return None, []


def extract_rows(table):
    rows = []
    tbody = table.find('tbody') or table
    for tr in tbody.find_all('tr'):
        tds = [td.get_text(' ', strip=True) for td in tr.find_all(['td','th'])]
        # skip empty separator rows
        if not tds or all(not x for x in tds):
            continue
        rows.append(tds)
    return rows


def main():
    soup = get_soup(URL)
    table, table_headers = find_skater_table(soup)
    if table is None:
        print('Skater table not found')
        return

    parsed_rows = extract_rows(table)

    # read existing desired header order from stats.csv
    try:
        with open('stats.csv', 'r', encoding='utf-8') as f:
            first = f.readline().strip()
            desired_fields = [h.strip() for h in first.split(',') if h.strip()]
    except FileNotFoundError:
        # fallback: use a sensible default order
        desired_fields = ['#','Player','GP','G','A','PTS','SH','SH%','+/-','PPG','SHG','FG','GWG','GTG','OTG','HTG','UAG','PN-PIM','MIN','MAJ','OTH','BLK']

    # build header map from table_headers -> index
    header_map = {h: i for i, h in enumerate(table_headers)}

    out_rows = []
    for r in parsed_rows:
        # For each desired field, pick the corresponding value if present
        out = []
        for field in desired_fields:
            if field in header_map:
                idx = header_map[field]
                val = r[idx] if idx < len(r) else ''
            else:
                # try some common alternates
                alt = field
                if field == '#':
                    alt = '#'
                # if still not found, attempt by approximate matching
                val = ''
                for k in header_map:
                    if k.replace(' ', '').lower() == field.replace(' ', '').lower():
                        idx = header_map[k]
                        val = r[idx] if idx < len(r) else ''
                        break
            out.append(val)
        out_rows.append(out)

    # write header + rows (overwrite)
    with open('stats.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(desired_fields)
        for row in out_rows:
            w.writerow(row)

    print('Wrote', len(out_rows), 'rows to stats.csv')


if __name__ == '__main__':
    main()
