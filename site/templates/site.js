// Configuration
var limitDays = true;
const DEFAULT_DAYS = 21;
Chart.defaults.line.spanGaps = true;

var charts = [];

init();

// Event handlers
function toggleData(e) {
	let on = e.innerHTML == 'Show less data';

	// TODO: Would be better to update the datasets and call .update()
	charts.forEach(chart => chart.destroy());

	if (on) {
		e.innerHTML = "Show more data";
		limitDays = true;
	} else {
		e.innerHTML = "Show less data";
		limitDays = false;
	}

	init();
}

function toggleExtraStats(e) {
	let moreStats = document.getElementById('moreStats');
	let showing = Array.from(moreStats.classList).indexOf('is-hidden');
	moreStats.classList.toggle('is-hidden');

	e.children[0].classList.toggle('fa-chevron-up');
	e.children[0].classList.toggle('fa-chevron-down');
}

// Chart logic
function init() {
	let chartConfig = [
		{
			key: 'breakdown',
			id:  'breakdownChart',
		},
		{
			key: 'totals',
			id:  'totalsChart',
			postFunc: (chart) => {
				// HACK: If not mobile then add padding so this graph aligns with the other graph
				if (!((typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1))) {
					chart.options.layout.padding.top = 42;
					chart.update();
				}
			}
		}
	];

	// Generate charts
	chartConfig.forEach(config => {
		let json = JSON.parse(getJSON(config.key));

		if (limitDays) {
			json.datasets.forEach(set => set.data = set.data.slice(-DEFAULT_DAYS));
			json.labels = json.labels.slice(-DEFAULT_DAYS);
		}

		let context = document.getElementById(config.id);
		let chart = new Chart(context, {
			type: 'line',
			data: json,
			options: {
				maintainAspectRatio: false,
				responsive: true,
			}
		});

		charts.push(chart);
		if (config.postFunc) config.postFunc(chart);
	});

	// TODO: Add buttons to change dates
	// breakdownChart.data.datasets[0].data.pop();
	// breakdownChart.data.labels.pop();
	// breakdownChart.update();
}

// Fetch the JSON from the server
function getJSON(filename) {
	let JSONs = {
		breakdown: `{{ json.breakdown }}`,
		totals: `{{ json.totals }}`,
	};

	return JSONs[filename];
}
