// Global ChartJS Configuration
Chart.defaults.line.spanGaps = true;

// All of the charts
let charts = {};

/*
* Helpers
*/
// Returns true if on mobile (or it should at least...)
const isMobile = () => ((typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1));

/* 
* Data range mutators 
*/
// Converts a dataset from daily points to weekly points
const everyXdays = (data, daysBetween = undefined) => {
	if (daysBetween == undefined) {
		const magicNumber = 18; // The magic disvisor to make the graph look decent, just a guess
		const totalDays = data.labels.length;
		daysBetween = Math.floor(totalDays / magicNumber);
	}

	data.datasets.forEach(set => {
		let counter       = 0;
		let newDataPoints = [];

		set.data.forEach(data => {
			if (counter == 0 || (counter % daysBetween == 0)) {
				newDataPoints.push(data);
			}
			counter++;
		});

		set.data = newDataPoints;
	});

	data.labels = data.labels.filter((_, idx) => (idx == 0 || idx % daysBetween == 0));
};

// Converts a dataset to just have the last $days worth of data
const lastXdays = (data, days = 21) => {
	data.datasets.forEach(set => set.data = set.data.slice(-days));
	data.labels = data.labels.slice(-days);
};

// Wrapper to call
const toggleChartDataSet = (chartKey) => {
	let chart = charts[chartKey];
	if (!chart.dataMutatorFn) return;

	if (chart.toggleOn) {
		chart.data = JSON.parse(getJSON(chartKey));
	} else {
		chart.dataMutatorFn(chart.data);
	}

	chart.toggleOn = !chart.toggleOn;
	chart.update();
};

// Draw the charts for the first time
initCharts();

/*
* Event handlers
*/
// Toggles between showing all data on the chart or the smaller dataset
function toggleData(e) {
	let on = e.innerHTML == 'Show less data';

	// Run toggles on each chart
	Object.keys(charts).forEach(key => toggleChartDataSet(key));

	if (on) {
		e.innerHTML = "Show more data";
		limitDays = true;
	} else {
		e.innerHTML = "Show less data";
		limitDays = false;
	}
}

// Toggles the extra stat cards
function toggleExtraCards(e) {
	let moreStats = document.getElementById('moreStats');

	e.children[0].classList.toggle('fa-chevron-up');
	e.children[0].classList.toggle('fa-chevron-down');
	moreStats.classList.toggle('closed');
}

/*
* Charts
*/
// Chart config parsing
function initCharts() {
	let chartConfig = [
		{
			key: 'location',
			htmlId: 'locationChart',
			dataMutatorFn: everyXdays,
		},
		{
			key: 'totals',
			htmlId: 'totalsChart',
			options: { layout: { padding: { top: isMobile() ? 0 : 42 } } }, // HACK: If not mobile then add padding so this graph aligns with the one to it's left
			dataMutatorFn: everyXdays,
		},
		{
			key: 'newCases',
			htmlId: 'newCasesChart',
			type: 'bar',
			hiddenByDefault: ['Negative'],
			dataMutatorFn: lastXdays,
		},
		{
			key: 'breakdown',
			htmlId: 'breakdownChart',
			type: 'doughnut',
		}
	];

	// Generate charts
	chartConfig.forEach(config => {
		let data = JSON.parse(getJSON(config.key));
		if (config.dataMutatorFn) config.dataMutatorFn(data);

		chart = makeChart(config, data);
		chart.toggleOn = true;

		charts[config.key] = chart;
		if (config.postFunc) config.postFunc(chart);
	});
}

// Instantiates the Chart()
function makeChart(config, data) {
	// TODO: Improve
	if (config.hiddenByDefault) {
		data.datasets.forEach(set => {
			config.hiddenByDefault.forEach(label => {
				if (set.label == label) {
					set.hidden = true;
				}
			});
		});
	}

	let context = document.getElementById(config.htmlId);
	let chart = new Chart(context, {
		type: config.type || 'line',
		data: data,
		options: {
			maintainAspectRatio: false,
			responsive: true,
			...config.options
		}
	});

	// Put in some of the things we need later
	chart.dataMutatorFn = config.dataMutatorFn;

	return chart;
}

// Return the appropriate JSON
// Automatically generated server side
function getJSON(filename) {
	let JSONs = {
		location:  `{{ json.location }}`,
		totals:    `{{ json.totals }}`,
		newCases:  `{{ json.newCases }}`,
		breakdown: `{{ json.breakdown }}`,
	};

	return JSONs[filename];
}
