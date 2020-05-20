// Configuration
let limitDays = true;
const DEFAULT_DAYS = 21;
Chart.defaults.line.spanGaps = true;

let charts = {};

// Returns true if on mobile (or it should at least...)
const isMobile = () => ((typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1));

// Data Range Togglers
const groupedToggle = (chartKey) => {
	let chart = charts[chartKey];
	
	let json = JSON.parse(getJSON(chartKey));

	if (!chart.toggleOn) {
		const everyX = 7;

		json.datasets.forEach(set => {
			let counter       = 0;
			let newDataPoints = [];

			set.data.forEach(data => {
				if (counter == 0 || (counter % everyX == 0)) {
					newDataPoints.push(data);
				}

				counter++;
			});

			set.data = newDataPoints;
		});

		json.labels = json.labels.filter((_, idx) => (idx == 0 || idx % everyX == 0));
	}

	chart.toggleOn = !chart.toggleOn;
	chart.data = json;
	chart.update();
};

const lastXdaysToggle = (chartKey) => {
	let chart = charts[chartKey];
	const days = 21;

	let json = JSON.parse(getJSON(chartKey));

	if (!chart.toggleOn) {
		json.datasets.forEach(set => set.data = set.data.slice(-days));
		json.labels = json.labels.slice(-days);
	}

	chart.toggleOn = !chart.toggleOn;
	chart.data = json;
	chart.update();
};

initCharts();

// Event handlers
function toggleData(e) {
	let on = e.innerHTML == 'Show less data';

	// Run toggles on each chart
	// TODO: This doesn't work properly, the old data and new data conflict...
	Object.keys(charts).forEach(key => { console.log(key);toggleDataDurations(key)});

	if (on) {
		e.innerHTML = "Show more data";
		limitDays = true;
	} else {
		e.innerHTML = "Show less data";
		limitDays = false;
	}

	initCharts();
}

function toggleDataDurations(chartKey) {
	if (!charts) return;

	if (charts[chartKey] && charts[chartKey].toggler) {
		charts[chartKey].toggler(chartKey);
	}
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
	let chartConfig = [
		{
			key: 'location',
			id:  'locationChart',
			rangeToggle: groupedToggle,
		},
		{
			key: 'totals',
			id:  'totalsChart',
			options: { layout: { padding: { top: isMobile() ? 0 : 42 } } }, // HACK: If not mobile then add padding so this graph aligns with the one to it's left
			rangeToggle: groupedToggle,
		},
		{
			key: 'newCases',
			id: 'newCasesChart',
			type: 'bar',
			toHide: ['Negative'],
			rangeToggle: lastXdaysToggle,
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

		chart = drawChart(config, json);

		charts[config.key] = chart;
		if (config.postFunc) config.postFunc(chart);
		if (chart.toggler) chart.toggler(config.key)
	});

	// TODO: Add buttons to change dates
	// breakdownChart.data.datasets[0].data.pop();
	// breakdownChart.data.labels.pop();
	// breakdownChart.update();
}

function drawChart(config, data) {
	if (config.toHide) {
		data.datasets.forEach(set => {
			config.toHide.forEach(label => {
				if (set.label == label) set.hidden = true;
			});
		});
	}

	let context = document.getElementById(config.id);
	let chart = new Chart(context, {
		type: config.type || 'line',
		data: data,
		options: {
			maintainAspectRatio: false,
			responsive: true,
			...config.options
		}
	});

	chart.toggler = config.rangeToggle;

	return chart;
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
