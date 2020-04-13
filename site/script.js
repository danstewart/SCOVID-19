// Draw the charts
Chart.defaults.line.spanGaps = true;

getBreakdownData().then(data => {
	let breakdownCtx = document.getElementById('breakdownChart');
	let breakdownChart = new Chart(breakdownCtx, {
		type:    'line',
		data:    data,
		options: {
			maintainAspectRatio: false,
			responsive: true,
		},
	});

	// TODO: Add buttons to change dates
	// breakdownChart.data.datasets[0].data.pop();
	// breakdownChart.data.labels.pop();
	// breakdownChart.update();
});

getTotalsData().then(data => {
	let totalsCtx = document.getElementById('totalsChart');
	let totalsChart = new Chart(totalsCtx, {
		type:    'line',
		data:    data,
		options: {
			maintainAspectRatio: false,
			responsive: true,
		},
	});

	// HACK: If not mobile then add padding so this graph aligns with the other graph
	if (!((typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1))) {
		totalsChart.options.layout.padding.top = 42;
		totalsChart.update();
	}

});

// Transform the breakdown.json into the correct format for chartjs
async function getBreakdownData() {
	return getData('breakdown.json', (json, dt, cat) => json[dt][cat]['cases']);
}

async function getTotalsData() {
	return getData('totals.json', (json, dt, cat) => json[dt][cat]);
}

async function getData(filename, diggerFn) {
	let json = await getJSON(filename);

	let dates    = Object.keys(json).sort();
	let datasets = {};
	let seen     = {};
	let counter  = 0;

	dates.forEach(dt => {
		Object.keys(json[dt]).forEach(category => {
			if (!datasets[category]) {
				datasets[category] = new Array();
			}

			// Back fill the stats with zeroes for dates where there is no data
			if (!seen[category]) {
				Array.from({ length: counter }, () => datasets[category].push(0) );
				seen[category] = true;
			}

			datasets[category].label = category;
			datasets[category].push(diggerFn(json, dt, category));
		});

		counter++;
	});

	return {
		labels: dates,
		datasets: Object.keys(datasets).sort().map(category => {
			let color = getColor(category);

			return {
				label: category.charAt(0).toUpperCase() + category.slice(1),
				data: datasets[category],
				borderColor: color,
				backgroundColor: color,
				fill: false,
			}
		}),
	};
}

// Fetch the breakdown.json from the server
function getJSON(filename) {
	return fetch(filename).then(response => response.json())
}

function getColor(key) {
	let colorMap = {
		// Breakdown
		// Ordered approx by most cases
		'Greater Glasgow and Clyde': '#a6cee3',
		'Lothian': '#1f78b4',
		'Tayside': '#b2df8a',
		'Lanarkshire': '#33a02c',
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
		
		// Totals
		'died': '#b3b3b3',
		'positive': '#ff7f00',
		'negative': '#b2df8a'
	};

	if (colorMap[key]) {
		return colorMap[key];
	}

	return 'gray';
}
