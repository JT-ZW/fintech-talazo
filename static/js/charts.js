class ChartManager {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        this.initParameterChart();
        this.setupEventListeners();
    }

    initParameterChart() {
        const ctx = document.getElementById('live-chart');
        if (!ctx) return;

        this.charts.parameters = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute'
                        }
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    updateCharts(data) {
        if (!data.parameters) return;

        const chart = this.charts.parameters;
        if (!chart) return;

        const now = new Date();

        Object.entries(data.parameters).forEach(([key, value]) => {
            const dataset = this.getOrCreateDataset(chart, key);
            dataset.data.push({
                x: now,
                y: value
            });

            // Keep only last 30 minutes of data
            const cutoff = new Date(now - 30 * 60 * 1000);
            dataset.data = dataset.data.filter(point => point.x > cutoff);
        });

        chart.update();
    }

    getOrCreateDataset(chart, parameter) {
        let dataset = chart.data.datasets.find(ds => ds.label === parameter);
        
        if (!dataset) {
            dataset = {
                label: parameter,
                data: [],
                borderColor: this.getParameterColor(parameter),
                fill: false,
                tension: 0.4
            };
            chart.data.datasets.push(dataset);
        }

        return dataset;
    }

    getParameterColor(parameter) {
        const colors = {
            ph_level: '#FF6384',
            nitrogen_level: '#36A2EB',
            phosphorus_level: '#FFCE56',
            potassium_level: '#4BC0C0',
            organic_matter: '#9966FF',
            cation_exchange_capacity: '#FF9F40',
            moisture_content: '#C9CBCF'
        };
        return colors[parameter] || '#000000';
    }

    setupEventListeners() {
        const parameterSelect = document.getElementById('parameter-select');
        if (parameterSelect) {
            parameterSelect.addEventListener('change', (e) => {
                this.updateParameterVisibility(e.target.value);
            });
        }
    }

    updateParameterVisibility(selectedParameter) {
        if (!this.charts.parameters) return;

        this.charts.parameters.data.datasets.forEach(dataset => {
            dataset.hidden = selectedParameter !== 'all' && dataset.label !== selectedParameter;
        });

        this.charts.parameters.update();
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chartManager = new ChartManager();
});