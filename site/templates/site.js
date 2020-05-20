// Configuration
var limitDays = true;
const DEFAULT_DAYS = 21;
Chart.defaults.line.spanGaps = true;

var charts = [];

// Returns true if on mobile (or it should at least...)
const isMobile = () => ((typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1));

initCharts();

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

	initCharts();
}

// Toggles the extra stat cards
function toggleExtraStats(e) {
	let moreStats = document.getElementById('moreStats');

	e.children[0].classList.toggle('fa-chevron-up');
	e.children[0].classList.toggle('fa-chevron-down');
	moreStats.classList.toggle('closed');
}

// Chart initialisation
function initCharts() {

	const hideDataSet = (chart, setLabel) => {
		chart.data.datasets.forEach(set => {
			if (set.label == setLabel) {
				set.hidden = true;
				chart.update();
			}
		});
	};

	let chartConfig = [
		{
			key: 'location',
			id:  'locationChart',
		},
		{
			key: 'totals',
			id:  'totalsChart',
			options: { layout: { padding: { top: isMobile() ? 0 : 42 } } } // HACK: If not mobile then add padding so this graph aligns with the one to it's left
		},
		{
			key: 'newCases',
			id: 'newCasesChart',
			type: 'bar',
			postFunc: (chart) => hideDataSet(chart, 'Negative'),
		},
		{
			key: 'breakdown',
			id: 'breakdownChart',
			type: 'doughnut',
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
			type: config.type || 'line',
			data: json,
			options: {
				maintainAspectRatio: false,
				responsive: true,
				...config.options
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
		location:  `{{ json.location }}`,
		totals:    `{{ json.totals }}`,
		newCases:  `{{ json.newCases }}`,
		breakdown: `{{ json.breakdown }}`,
	};

	return JSONs[filename];
}
