// All of the charts
let charts = {};

// Global ChartJS Configuration
Chart.defaults.line.spanGaps = true;

const original = Chart.defaults.global.legend.onClick;
Chart.defaults.global.legend.onClick = function(e, legendItem) {
	charts[this.chart.key].hidden[legendItem.text] = !legendItem.hidden;
	original.call(this, e, legendItem);
};


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

	// Takes every X element but starting from the end
	const reducer = (data) => {
		let newData = new Array();
		let dataLength = data.length;

		for (let i = 0; i < dataLength; i++) {
			if (i == 0 || i % daysBetween == 0) {
				let idx = dataLength - (i + 1);
				newData.unshift(data[idx]);
			}
		}

		return newData;
	};

	data.datasets.forEach(set => {
		set.data = reducer(set.data);
	});

	data.labels = reducer(data.labels);
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
		chart.data = getData(chartKey);

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
function toggleData(e, chartKey) {
	let on = e.innerHTML == 'Show less';

	toggleChartDataSet(chartKey);

	if (on) {
		e.innerHTML = 'Show more';
	} else {
		e.innerHTML = 'Show less';
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
			hidden: { 'Negative': true },
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
		// Bit of a hack so that if we want anything hidden by default
		// then getData() will pick it up
		if (config.hidden) {
			charts[config.key] = {};
			charts[config.key].hidden = config.hidden;
		}

		let data = getData(config.key);
		if (config.dataMutatorFn) config.dataMutatorFn(data);

		chart = makeChart(config, data);
		chart.toggleOn = true;

		charts[config.key] = chart;
		if (config.postFunc) config.postFunc(chart);
	});
}

// Instantiates the Chart()
function makeChart(config, data) {
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
	chart.key = config.key;
	chart.hidden = config.hidden || {};

	return chart;
}

// Return the appropriate data for this chart
// Automatically generated server side
function getData(chartKey) {
	let JSONs = {
		location:  `{{ json.location }}`,
		totals:    `{{ json.totals }}`,
		newCases:  `{{ json.newCases }}`,
		breakdown: `{{ json.breakdown }}`,
	};

	let data = JSON.parse(JSONs[chartKey]);

	// Figure out which sets should be hidden
	if (charts && charts[chartKey] && charts[chartKey].hidden) {
		data.datasets.forEach(set => {
			Object.keys(charts[chartKey].hidden).forEach(label => {
				if (charts[chartKey].hidden[label] && set.label == label) {
					set.hidden = true;
				}
			});
		});
	}

	return data;
}
