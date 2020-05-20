#!/usr/bin/env python3

# Takes the JSON from /data and generates the site from /site/templates

from dotenv import load_dotenv
load_dotenv()

import os
import json
import datetime
from lib import IO
from lib import Util
from lib.DT import DT
from lib.ChartData import ChartData, PieChart
from jinja2 import Environment, FileSystemLoader, Template

# Dirs
root_dir     = os.getenv('PROJECT_ROOT')
site_dir     = os.path.join(root_dir, 'site')
template_dir = os.path.join(root_dir, 'site', 'templates')
data_dir     = os.path.join(root_dir, 'data')

def main():
	stats = load_stats()
	generate_js(stats)
	generate_site(stats)


# Parses all the JSON files and turns them into one big dict
def load_stats():
	stats = {}

	for file in os.listdir(data_dir):
		file_contents = IO.read_file(os.path.join(data_dir, file))
		parsed        = json.loads(file_contents)
		date          = os.path.splitext(file)[0]
		stats[date]   = parsed

	return stats


# Generates the index.html from sites/templates/site.html
def generate_site(stats):
	file_loader   = FileSystemLoader(template_dir)
	env           = Environment(loader=file_loader)
	site_template = env.get_template('site.html')

	days = sorted(stats.keys())
	cases_breakdown = {}
	deaths_breakdown = {}
	prev_day = None

	# Func
	calc_change = lambda dt, src: stats[dt]['totals'][src] if not prev_day else stats[dt]['totals'][src] - stats[prev_day]['totals'][src]

	for date in days:
		cases_breakdown[date] = calc_change(date, 'positive')
		deaths_breakdown[date] = calc_change(date, 'died')
		prev_day = date

	day_with_most_cases  = max(cases_breakdown, key=cases_breakdown.get)
	day_with_most_deaths = max(deaths_breakdown, key=deaths_breakdown.get)

	summary = {
		'total_cases':  stats[days[-1]]['totals']['positive'],
		'total_deaths': stats[days[-1]]['totals']['died'],
		'new_cases':    cases_breakdown[days[-1]],
		'new_deaths':   deaths_breakdown[days[-1]],
		'most_cases':   { 'date': DT.from_date(day_with_most_cases).make_nice().nice,  'total': cases_breakdown[day_with_most_cases] },
		'most_deaths':  { 'date': DT.from_date(day_with_most_deaths).make_nice().nice, 'total': deaths_breakdown[day_with_most_deaths] }
	}

	IO.write_file(
		os.path.join(site_dir, 'index.html'),
		site_template.render(
			summary = summary,
			last_updated = DT().make_nice('%B {day} %Y at %H:%M').nice
		)
	)


# Generates the script.js from sites/templates/site.js
def generate_js(stats):
	totals    = generate_totals_json(stats)
	location  = generate_location_json(stats)
	new_cases = generate_new_cases_json(stats)
	breakdown = generate_breakdown_json(stats)

	file_loader   = FileSystemLoader(template_dir)
	env           = Environment(loader=file_loader)
	js_template   = env.get_template('site.js')

	IO.write_file(
		os.path.join(site_dir, 'script.js'),
		js_template.render(json = {
			'totals': totals,
			'location': location,
			'breakdown': breakdown,
			'newCases': new_cases,
		})
	)


# Generates the totals JSON for generate_js()
def generate_totals_json(stats):
	stat_types = ['died', 'negative', 'positive']
	chart      = ChartData(*stat_types)

	for date in sorted(dict.keys(stats)):
		chart.add_label(date)

		for stat_type in stat_types:
			chart.add_data(stats[date]['totals'][stat_type], stat_type)

	return chart.as_json()


# Generates the breakdown JSON for generate_js()
def generate_location_json(stats):

	chart = ChartData()
	days_passed = 0

	for date in sorted(dict.keys(stats)):
		days_passed = days_passed + 1
		chart.add_label(date)

		if 'breakdown' not in stats[date]:
			continue

		for location in stats[date]['breakdown']:
			if location == 'Golden Jubilee Nation Hospital':
				continue

			if chart.create(location):
				chart.add_data([0] * days_passed, location)

			chart.add_data(stats[date]['breakdown'][location]['cases'], location)

	return chart.as_json()


def generate_new_cases_json(stats):
	stat_types = ['died', 'negative', 'positive']
	chart      = ChartData(*stat_types)
	yesterday  = dict(zip(stat_types, [0] * len(stat_types)))

	for date in sorted(dict.keys(stats)):
		chart.add_label(date)

		for stat_type in stat_types:
			new = stats[date]['totals'][stat_type] - yesterday[stat_type]
			yesterday[stat_type] += new

			chart.add_data(new, stat_type)

	return chart.as_json()

# TODO: Change to use ChartData
def generate_breakdown_json(stats):
	stat_types = ['died', 'negative', 'positive']
	chart      = PieChart()
	today      = sorted(dict.keys(stats))[-1]

	for stat_type in stat_types:
		chart.create(stat_type)
		chart.add_label(stat_type.title())
		chart.add_data(stats[today]['totals'][stat_type])

	return chart.as_json()

main()
