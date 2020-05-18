#!/usr/bin/env python3

# Takes the JSON from /data and generates the site from /site/templates

from dotenv import load_dotenv
load_dotenv()

import os
import sys
sys.path.append(os.path.join(os.environ['PROJECT_ROOT'], 'lib'))

import json
import datetime
import IO
import Util
from DT import DT
from jinja2 import Environment, FileSystemLoader, Template

template_dir = os.path.join(os.environ['PROJECT_ROOT'], 'site', 'templates')

def main():
	stats = load_stats()
	generate_js(stats)
	generate_site(stats)


# Parses all the JSON files and turns them into one big dict
def load_stats():
	stats = {}
	stat_dir = os.path.join(Util.project_root(), 'data')

	for file in os.listdir(stat_dir):
		file_contents = IO.read_file(os.path.join(stat_dir, file))
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
		os.path.join(Util.project_root(), 'site', 'index.html'),
		site_template.render(
			summary = summary,
			last_updated = DT().make_nice('%B {day} %Y at %H:%M').nice
		)
	)


# Generates the script.js from sites/templates/site.js
def generate_js(stats):
	totals     = generate_totals_json(stats)
	breakdown  = generate_breakdown_json(stats)
	new_cases  = generate_new_cases_json(stats, 'positive')
	new_deaths = generate_new_cases_json(stats, 'died')

	file_loader   = FileSystemLoader(template_dir)
	env           = Environment(loader=file_loader)
	js_template   = env.get_template('site.js')

	IO.write_file(
		os.path.join(Util.project_root(), 'site', 'script.js'),
		js_template.render(json = {
			'totals': totals,
			'breakdown': breakdown,
			'newCases': new_cases,
			'newDeaths': new_deaths
		})
	)


# Generates the totals JSON for generate_js()
def generate_totals_json(stats):
	dataset_mapping = { 'died': 0, 'negative': 1, 'positive': 2 }

	labels   = []
	datasets = [
		{
			'backgroundColor': color_map('died'),
			'borderColor': color_map('died'),
			'data': [],
			'fill': False,
			'label': 'Died',
		},
		{
			'backgroundColor': color_map('negative'),
			'borderColor': color_map('negative'),
			'data': [],
			'fill': False,
			'label': 'Negative',
			'hidden': True,
		},
		{
			'backgroundColor': color_map('positive'),
			'borderColor': color_map('positive'),
			'data': [],
			'fill': False,
			'label': 'Positive',
		}
	]

	for date in sorted(dict.keys(stats)):
		labels.append(date)

		for stat_type in stats[date]['totals']:
			idx = dataset_mapping[stat_type]
			datasets[idx]['data'].append(stats[date]['totals'][stat_type])

	return Util.to_json({
		'datasets': datasets,
		'labels': labels
	})


# Generates the breakdown JSON for generate_js()
def generate_breakdown_json(stats):
	labels   = []
	datasets = {}

	days_passed = 0
	for date in sorted(dict.keys(stats)):
		days_passed = days_passed + 1
		labels.append(date)

		if 'breakdown' not in stats[date]:
			continue

		for location in stats[date]['breakdown']:
			if location == 'Golden Jubilee Nation Hospital':
				continue

			if location not in datasets:
				datasets[location] = {
					'backgroundColor': color_map(location),
					'borderColor': color_map(location),
					'data': [0] * days_passed,
					'fill': False,
					'label': location,
				}

			datasets[location]['data'].append(stats[date]['breakdown'][location]['cases'])

	datasets = list(datasets.values())

	return Util.to_json({
		'datasets': datasets,
		'labels': labels
	})

def generate_new_cases_json(stats, type):
	labels    = []
	yesterday = 0

	dataset = {
		'backgroundColor': color_map(type),
		'borderColor': color_map(type),
		'data': [],
		'fill': False,
		'label': type.title()
	}

	for date in sorted(dict.keys(stats)):
		if 'totals' not in stats[date]:
			continue

		if 'positive' not in stats[date]['totals']:
			continue

		new = stats[date]['totals'][type] - yesterday
		yesterday += new

		labels.append(date)
		dataset['data'].append(new)

	return Util.to_json({
		'datasets': [ dataset ],
		'labels': labels
	})

# Maps each stats field to a color
def color_map(key):
	mapping = {
		# Breakdown
		# Ordered approx by most cases
		'Greater Glasgow and Clyde': '#33a02c',
		'Lothian': '#1f78b4',
		'Tayside': '#b2df8a',
		'Lanarkshire': '#a6cee3',
		'Ayrshire and Arran': '#fb9a99',
		'Fife': '#e31a1c',
		'Forth Valley': '#fdbf6f',
		'Grampian': '#ff7f00',
		'Borders': '#cab2d6',
		'Dumfries and Galloway': '#6a3d9a',
		'Highland': '#ffff99',
		'Shetland': '#b15928',
		'Eileanan Siar (Western Isles)': '#66c2a5',
		'Orkney': '#a6d854',
		# Totals
		'died': '#b3b3b3',
		'positive': '#ff7f00',
		'negative': '#b2df8a'
	}

	return mapping[key] if key in mapping else 'gray'


main()
