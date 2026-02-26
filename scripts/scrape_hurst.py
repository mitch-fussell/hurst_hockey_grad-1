#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

BASE = 'https://hurstathletics.com'
ROSTER = BASE + '/sports/mens-ice-hockey/roster'


def get_soup(url):
    r = requests.get(url)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')


def extract_player_links(soup):
    links = set()
    for a in soup.find_all('a', href=True):
        h = a['href']
        if '/sports/mens-ice-hockey/roster/' in h and not h.rstrip('/').endswith('/sports/mens-ice-hockey/roster'):
            links.add(urljoin(BASE, h))
    return sorted(links)


def parse_player(url):
    s = get_soup(url)
    name_spans = s.select('.sidearm-roster-player-name span')
    if len(name_spans) >= 2:
        first = name_spans[0].get_text(strip=True)
        last = name_spans[1].get_text(strip=True)
    else:
        heading = s.select_one('.sidearm-roster-player-heading')
        text = heading.get_text(' ', strip=True) if heading else ''
        parts = text.split()
        first = parts[0] if parts else ''
        last = parts[-1] if parts else ''

    jersey_el = s.select_one('.sidearm-roster-player-jersey-number')
    jersey = jersey_el.get_text(strip=True) if jersey_el else ''

    fields = {}
    for dl in s.select('dl'):
        dt = dl.find('dt')
        dd = dl.find('dd')
        if dt and dd:
            key = dt.get_text(strip=True).rstrip(':')
            fields[key] = dd.get_text(' ', strip=True)

    position = fields.get('Position', '')
    height = fields.get('Height', '')
    weight = fields.get('Weight', '')
    class_year = fields.get('Class', '')
    hometown = fields.get('Hometown', '')
    high_school = fields.get('High School', '')

    return {
        'first': first,
        'last': last,
        'position': position,
        'jersey': jersey,
        'weight': weight,
        'height': height,
        'class_year': class_year,
        'hometown': hometown,
        'high_school': high_school,
    }


def main():
    roster_soup = get_soup(ROSTER)
    links = extract_player_links(roster_soup)

    existing = set()
    try:
        with open('bio.csv', 'r', newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                existing.add((row.get('first',''), row.get('last','')))
    except FileNotFoundError:
        pass

    rows = []
    for link in links:
        try:
            p = parse_player(link)
        except Exception as e:
            print('Failed to parse', link, e)
            continue
        key = (p['first'], p['last'])
        if key in existing:
            print('Skipping existing', key)
            continue
        rows.append(p)
        existing.add(key)

    if rows:
        with open('bio.csv', 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            for p in rows:
                w.writerow([
                    p['first'],
                    p['last'],
                    p['position'],
                    p['jersey'],
                    p['weight'],
                    p['height'],
                    p['class_year'],
                    p['hometown'],
                    p['high_school'],
                ])
    print('Appended', len(rows), 'rows')


if __name__ == '__main__':
    main()
