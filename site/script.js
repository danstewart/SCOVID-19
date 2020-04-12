// Draw the chart
getData().then(data => {
	Chart.defaults.line.spanGaps = true;
	let ctx = document.getElementById('casesChart');
	let casesChart = new Chart(ctx, {
		type:    'line',
		data:    data,
		options: {},
	});
	
	// TODO: Add buttons to change dates
	// casesChart.data.datasets[0].data.pop();
	// casesChart.data.labels.pop();
	// casesChart.update();
});

// Transform the breakdown.json into the correct format for chartjs
async function getData() {
	let json = await getJSON();

	let dates    = Object.keys(json).sort();
	let datasets = {};
	let seen     = {};
	let counter  = 0;

	dates.forEach(dt => {
		Object.keys(json[dt]).forEach(location => {
			if (!datasets[location]) {
				datasets[location] = new Array();
			}
			
			// Back fill the stats with zeroes for dates where there is no data
			if (!seen[location]) {
				Array.from({ length: counter }, () => datasets[location].push(0) );
				seen[location] = true;
			}

			datasets[location].label = location;
			datasets[location].push(json[dt][location]['cases']);
		});

		counter++;
	});

	return {
		labels: dates,
		datasets: Object.keys(datasets).sort().map(location => {
			let color = getColor(location);

			return {
				label: location,
				data: datasets[location],
				borderColor: color,
				backgroundColor: color,
				fill: false,
			}
		}),
	};
}

function getColor(location) {
	let colorMap = {
		'Ayrshire and Arran': 'orange',
		'Borders': '#ff6f69',
		'Dumfries and Galloway': '#ffcc5c',
		'Eileanan Siar (Western Isles)': '#baffc9',
		'Fife': 'pink',
		'Forth Valley': 'navy',
		'Grampian': '#fb958b',
		'Golden Jubilee National Hospital': '#4c516d',
		'Greater Glasgow and Clyde': '#e8ca93',
		'Highland': 'green',
		'Lanarkshire': '#bae1ff',
		'Lothian': '#007777',
		'Orkney': '#88d8b0',
		'Shetland': '#d696bb',
		'Tayside': 'rebeccapurple',
	};

	if (colorMap[location]) {
		return colorMap[location];
	}

	return 'gray';
}

// Fetch the breakdown.json from the server
function getJSON() {
	return fetch('breakdown.json').then(response => response.json())
}

