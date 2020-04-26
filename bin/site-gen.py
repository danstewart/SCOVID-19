#!/usr/bin/env python3

from dotenv import load_dotenv
load_dotenv()

import os
import sys
sys.path.append(os.path.join(os.environ['PROJECT_ROOT'], 'lib'))

import json
import IO
import Util
from jinja2 import Environment, FileSystemLoader, Template


def main():
	stats = load_stats()
	generate_js(stats)
	generate_site(stats)


def load_stats():
	stats = {}
	stat_dir = os.path.join(Util.project_root(), 'data')

	for file in os.listdir(stat_dir):
		file_contents = IO.read_file(os.path.join(stat_dir, file))
		parsed        = json.loads(file_contents)
		date          = os.path.splitext(file)[0]
		stats[date]   = parsed
	
	return stats


def generate_site(stats):
	file_loader   = FileSystemLoader('site/templates')
	env           = Environment(loader=file_loader)
	site_template = env.get_template('site.html')

	last_two = sorted(list(dict.keys(stats)))[-2:]

	summary = {
		'total_cases':  stats[last_two[1]]['totals']['positive'],
		'total_deaths': stats[last_two[1]]['totals']['died'],
		'new_cases':    stats[last_two[1]]['totals']['positive'] - stats[last_two[0]]['totals']['positive'],
		'new_deaths':   stats[last_two[1]]['totals']['died'] - stats[last_two[0]]['totals']['died'],
	}

	IO.write_file(
		os.path.join(Util.project_root(), 'site', 'index.html'),
		site_template.render(summary=summary)
	)


def generate_js(stats):
	totals    = generate_totals_json(stats)
	breakdown = generate_breakdown_json(stats)

	file_loader   = FileSystemLoader('site/templates')
	env           = Environment(loader=file_loader)
	js_template = env.get_template('site.js')

	IO.write_file(
		os.path.join(Util.project_root(), 'site', 'script.js'),
		js_template.render(json={'totals': totals, 'breakdown': breakdown})
	)


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

	return json.dumps(
		{
			'datasets': datasets,
			'labels': labels
		},
		sort_keys=True,
		indent=2,
		separators=(',', ': ')
	)


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

	return json.dumps(
		{
			'datasets': datasets,
			'labels': labels
		},
		sort_keys=True,
		indent=2,
		separators=(',', ': ')
	)


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
		'Golden Jubilee National Hospital': '#b3b3b3',
		# Totals
		'died': '#b3b3b3',
		'positive': '#ff7f00',
		'negative': '#b2df8a'
	}

	return mapping[key] if key in mapping else 'gray'


main()
