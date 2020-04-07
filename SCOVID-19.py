#!/usr/bin/env python3

import re
import sys
import json
import requests
from bs4 import BeautifulSoup

# URL='https://www.gov.scot/coronavirus-covid-19/'
URL='https://web.archive.org/web/20200310210227/https://www.gov.scot/coronavirus-covid-19/'

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    html      = requests.get(URL, headers = headers)
    print(html)
    parsed    = BeautifulSoup(html.text, 'html.parser')
    breakdown = get_cases_by_area(parsed)
    totals    = get_totals(parsed)

    print(json.dumps(
        { 'totals': totals, 'breakdown': breakdown },
        sort_keys=True,
        indent=2,
        separators=(',', ': ')
    ))


def clean_str(string):
    if not string: return ''
    return string.strip().replace(u'\u00a0', ' ')


def clean_int(string):
    if not string: return 0
    clean = re.sub('\D', '', string)

    try:
        return int(clean)
    except:
        return 0


def get_cases_by_area(parsed, verbose = False):
    stats = {}
    total = 0

    isHeader = True
    table = parsed.find('table')
    for row in table.findAll('tr'):
        if (isHeader):
            isHeader = False
            continue

        cells           = row.findAll('td')
        area            = clean_str(cells[0].get_text())
        number_of_cases = clean_int(clean_str(cells[1].get_text()))
        stats[area]     = number_of_cases
        total           = total + number_of_cases

        if (verbose):
            print('{}: {}'.format(area, number_of_cases))

    return stats


def get_totals(parsed, verbose = False):
    stats = []
    mapping = [ 'negative', 'positive', 'died' ]

    totals = parsed.find(id='overview').findAll('ul')[2].findAll('li')
    for total in totals:
        num = clean_str(total.get_text()).split(' ')[0]
        stats.append(num)

        if (verbose):
            print(clean_str(total.get_text()))

    return dict(zip(mapping, stats))

########################################

# In debug mode don't use a try/except
if (len(sys.argv) >= 2 and sys.argv[1] == '--debug'):
    main()
    sys.exit(0)

try:
    main()
except Exception as e:
    print("Error: " + str(e))
    sys.exit(1)
