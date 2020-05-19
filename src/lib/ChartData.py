from lib import Util

class ChartData(object):

	def __init__(self, *types):
		self.labels = []
		self.data   = []
		self._map   = {}

		if len(types) > 0:
			for type in types:
				self.create(type)


	def create(self, type):
		vals = dict.values(self._map)

		if vals:
			next_idx = max(dict.values(self._map)) + 1
		else:
			next_idx = 0

		if type in self._map:
			return False

		self.data.append(self.make_dataset(type))
		self._map[type] = next_idx

		return self


	def add_label(self, label):
		self.labels.append(label)
		return self


	def add_data(self, data, type=None):
		idx = 0

		if (type is not None):
			idx = self._map[type]

		if isinstance(data, list):
			self.data[idx]['data'] += data
		else:
			self.data[idx]['data'].append(data)

		return self


	# Formatters
	def as_json(self):
		return Util.to_json({
			'labels': self.labels,
			'datasets': self.data
		})


	@staticmethod
	def make_dataset(type):
		return {
			'backgroundColor': ChartData.color_map(type),
			'borderColor': ChartData.color_map(type),
			'data': [],
			'fill': False,
			'label': str(type).title()
		}


	# Maps each stats field to a color
	@staticmethod
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


# Ugly hack to support Pie and Doughnut charts
class PieChart(ChartData):
	def __init__(self, *types):
		if len(types) > 0:
			super(PieChart, self).__init__(types)
		else:
			super(PieChart, self).__init__()


	def create(self, type):
		if len(self.data) > 0:
			self.data[0]['backgroundColor'].append(self.color_map(type))
			self.data[0]['borderColor'].append(self.color_map(type))
			return

		self.data.append(self.make_dataset(type))
		return self


	@staticmethod
	def make_dataset(*types):
		dataset = {
			'backgroundColor': [],
			'borderColor': [],
			'data': [],
		}

		if len(types) > 0:
			for type in types:
				dataset['backgroundColor'].append(ChartData.color_map(type))
				dataset['borderColor'].append(ChartData.color_map(type))

		return dataset
