// Configuration
var limitDays = true;
const DEFAULT_DAYS = 21;
Chart.defaults.line.spanGaps = true;

var breakdownChart;
var totalsChart;
init();

// Event handlers
function toggleData(e) {
	let on = e.innerHTML == 'Show less data';

	// TODO: Would be better to update the datasets and call .update()
	breakdownChart.destroy();
	totalsChart.destroy();

	if (on) {
		e.innerHTML = "Show more data";
		limitDays = true;
	} else {
		e.innerHTML = "Show less data";
		limitDays = false;
	}

	init();
}

function init() {
	// Draw the charts
	getJSON('breakdown').then(data => {
		if (limitDays) {
			data.datasets.forEach(set => set.data = set.data.slice(-DEFAULT_DAYS));
			data.labels = data.labels.slice(-DEFAULT_DAYS);
		}

		let breakdownCtx = document.getElementById('breakdownChart');
		breakdownChart = new Chart(breakdownCtx, {
			type: 'line',
			data: data,
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

	getJSON('totals').then(data => {
		if (limitDays) {
			data.datasets.forEach(set => set.data = set.data.slice(-DEFAULT_DAYS));
			data.labels = data.labels.slice(-DEFAULT_DAYS);
		}

		let totalsCtx = document.getElementById('totalsChart');
		totalsChart = new Chart(totalsCtx, {
			type: 'line',
			data: data,
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
}

// Fetch the JSON from the server
function getJSON(filename) {
	return fetch(`json/${filename}.json`).then(response => response.json());
}
