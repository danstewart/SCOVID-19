#!/usr/bin/env python3

# Scrape the gov.scot website for the latest COVID-19 stats and store them as JSON

import re
import sys
import json
import requests
from bs4 import BeautifulSoup

URL='https://www.gov.scot/publications/coronavirus-covid-19-tests-and-cases-in-scotland/'

def main(verbose=False):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    html      = requests.get(URL, headers = headers)
    parsed    = BeautifulSoup(html.text, 'html.parser')
    totals    = get_totals(parsed, verbose)
    breakdown = get_cases_by_area(parsed, verbose)

    print(json.dumps(
        { 'totals': totals, 'breakdown': breakdown },
        sort_keys=True,
        indent=2,
        separators=(',', ': ')
    ))


def clean_str(string):
    if not string: return ''
    return str(string).strip().replace(u'\u00a0', ' ')


def clean_int(string):
    if not string: return 0
    if string == '*': return '<5' # A * represents less than 5 cases

    clean = re.sub('\D', '', string)

    try:
        return int(clean)
    except:
        return 0


def get_cases_by_area(parsed, verbose = False):
    stats = {}
    mapping = [ 'cases', 'in_hospital', 'in_icu' ]

    isHeader = True
    table = parsed.find('table', class_='Table')
    for row in table.findAll('tr'):
        if (isHeader):
            isHeader = False
            continue

        cells = row.findAll('td')
        cells = list(map(clean_str, [c.get_text() for c in cells]))
        key   = cells.pop(0)
        cells = map(clean_int, cells)
        stat  = dict(zip(mapping, cells))
        stats[key] = stat

        if (verbose):
            print('{} has {} cases, {} in hospital and {} in the ICU'.format(key, *stat.values()))

    return stats


def get_totals(parsed, verbose = False):
    stats = []
    mapping = [ 'negative', 'positive', 'died' ]

    totals = parsed.find(id='preamble').findAll('ul')[0].findAll('li')
    for total in totals:
        num = clean_str(total.get_text()).split(' ')[0]
        stats.append(num)

        if (verbose):
            print(clean_str(total.get_text()))

    return dict(zip(mapping, stats))

########################################

# In debug mode don't use a try/except
if (len(sys.argv) >= 2 and sys.argv[1] == '--debug'):
    main(verbose=True)
    sys.exit(0)

try:
    main()
except Exception as e:
    print("Error: " + str(e))
    sys.exit(1)
