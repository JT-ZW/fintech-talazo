// chart-manager.js - Enhanced chart management for Talazo AgriFinance Dashboard

// Initialize charts when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Financial Gauge
    initializeFinancialGauge();
    
    // Initialize Parameter Charts
    initializeParameterCharts();
    
    // Initialize Yield Chart
    initializeYieldChart();
});

// Initialize the main financial health gauge
function initializeFinancialGauge() {
    const gaugeElement = document.getElementById('financial-gauge');
    if (!gaugeElement || typeof GaugeChart !== 'function') {
        console.error('Cannot initialize financial gauge - missing element or GaugeChart library');
        return;
    }
    
    // Create gauge chart with initial value
    GaugeChart.gaugeChart(gaugeElement, {
        hasNeedle: true,
        needleColor: '#464A4F',
        needleUpdateSpeed: 1000,
        arcColors: ['#E74C3C', '#F39C12', '#2ECC71'],
        arcDelimiters: [40, 60],
        rangeLabel: ['0', '100'],
        centralLabel: '0'
    }).updateValue(50); // Default starting value
}

// Initialize parameter charts (for live monitoring)
function initializeParameterCharts() {
    const liveChartElement = document.getElementById('live-chart');
    if (!liveChartElement || typeof Plotly !== 'object') {
        console.error('Cannot initialize parameter charts - missing element or Plotly library');
        return;
    }
    
    // Create empty plot
    const layout = {
        showlegend: true,
        xaxis: {
            title: 'Time',
            type: 'date',
            tickformat: '%H:%M',
            rangeslider: {
                visible: false
            }
        },
        yaxis: {
            title: 'Value'
        },
        margin: { l: 50, r: 50, b: 50, t: 30, pad: 4 },
        hovermode: 'closest',
        legend: {
            orientation: 'h',
            x: 0,
            y: 1.1
        },
        font: {
            family: 'Poppins, sans-serif'
        },
        autosize: true
    };
    
    // Initialize empty chart (will be populated by the dashboard manager)
    Plotly.newPlot(liveChartElement, [], layout, {responsive: true});
    
    // Set up parameter selector change event
    const parameterSelect = document.getElementById('parameter-select');
    if (parameterSelect) {
        parameterSelect.addEventListener('change', function() {
            if (window.chartManager) {
                window.chartManager.updateChartParameter(this.value);
            }
        });
    }
    
    // Set up time window buttons
    const timeButtons = document.querySelectorAll('.time-window button');
    if (timeButtons.length) {
        timeButtons.forEach(button => {
            button.addEventListener('click', function() {
                timeButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                const minutes = parseInt(this.getAttribute('data-minutes'));
                if (window.chartManager) {
                    window.chartManager.updateTimeWindow(minutes);
                }
            });
        });
    }
}

// Initialize yield prediction chart
function initializeYieldChart() {
    const yieldChartElement = document.getElementById('yield-chart');
    if (!yieldChartElement || typeof Plotly !== 'object') {
        console.error('Cannot initialize yield chart - missing element or Plotly library');
        return;
    }
    
    // Create sample data to initialize the chart
    const sampleData = [{
        x: ['Maize', 'Sorghum', 'Groundnuts'],
        y: [3.5, 3.2, 2.8],
        type: 'bar',
        marker: {
            color: '#27AE60'
        }
    }];
    
    const layout = {
        margin: { t: 10, l: 40, r: 20, b: 50 },
        yaxis: {
            title: 'Yield (tons/ha)',
            range: [0, 5]
        },
        xaxis: {
            title: 'Crop'
        },
        font: {
            family: 'Poppins, sans-serif'
        }
    };
    
    Plotly.newPlot(yieldChartElement, sampleData, layout, {responsive: true});
}

// Generate random data for testing and demo purposes
function generateTestData(params = ['ph_level', 'nitrogen_level', 'moisture_content']) {
    const now = new Date();
    const data = [];
    
    // Generate data points for the last 24 hours at 30-minute intervals
    for (let i = 0; i < 48; i++) {
        const point = {
            timestamp: new Date(now.getTime() - (i * 30 * 60 * 1000))
        };
        
        // Add random values for each parameter
        params.forEach(param => {
            const baseValue = getBaseValue(param);
            const variation = Math.sin(i * 0.1) * getVariationScale(param) + (Math.random() - 0.5) * getNoiseScale(param);
            point[param] = Math.max(0, baseValue + variation);
        });
        
        data.push(point);
    }
    
    return data;
}

// Helper functions for data generation
function getBaseValue(param) {
    // Default base values for different parameters
    const baseValues = {
        'ph_level': 6.5,
        'nitrogen_level': 30,
        'phosphorus_level': 25,
        'potassium_level': 200,
        'organic_matter': 4,
        'cation_exchange_capacity': 15,
        'moisture_content': 25
    };
    
    return baseValues[param] || 0;
}

function getVariationScale(param) {
    // Scale of the sinusoidal variation for each parameter
    const variationScales = {
        'ph_level': 0.2,
        'nitrogen_level': 3,
        'phosphorus_level': 2,
        'potassium_level': 10,
        'organic_matter': 0.3,
        'cation_exchange_capacity': 1,
        'moisture_content': 4
    };
    
    return variationScales[param] || 0.5;
}

function getNoiseScale(param) {
    // Scale of random noise for each parameter
    const noiseScales = {
        'ph_level': 0.1,
        'nitrogen_level': 1.5,
        'phosphorus_level': 1,
        'potassium_level': 5,
        'organic_matter': 0.2,
        'cation_exchange_capacity': 0.5,
        'moisture_content': 2
    };
    
    return noiseScales[param] || 0.3;
}

// Function to update charts with new data from the dashboard
function updateCharts(soilData, trendData) {
    console.log('Updating charts with new data:', soilData);
    
    // If no trend data is provided, generate it based on current values
    if (!trendData) {
        trendData = generateTestData(Object.keys(soilData));
    }
    
    // Update charts if the chartManager exists
    if (window.chartManager) {
        window.chartManager.updateCharts({
            points: trendData,
            scores: calculateTrendScores(trendData)
        });
    }
}

// Calculate trend scores for soil health (simplified algorithm)
function calculateTrendScores(trendData) {
    // Ideal ranges for soil parameters
    const idealRanges = {
        'ph_level': [6.0, 7.0],
        'nitrogen_level': [20.0, 40.0],
        'phosphorus_level': [15.0, 30.0],
        'potassium_level': [150.0, 250.0],
        'organic_matter': [3.0, 5.0],
        'cation_exchange_capacity': [10.0, 20.0],
        'moisture_content': [20.0, 30.0]
    };
    
    // Parameter weights
    const weights = {
        'ph_level': 0.20,
        'nitrogen_level': 0.15,
        'phosphorus_level': 0.15,
        'potassium_level': 0.15,
        'organic_matter': 0.15,
        'cation_exchange_capacity': 0.10,
        'moisture_content': 0.10
    };
    
    return trendData.map(point => {
        let totalScore = 0;
        let totalWeight = 0;
        
        Object.entries(idealRanges).forEach(([param, range]) => {
            if (param in point && point[param] !== null) {
                const value = point[param];
                const weight = weights[param] || 0;
                
                // Calculate parameter score based on ideal range
                let paramScore;
                if (value >= range[0] && value <= range[1]) {
                    // Value is within ideal range
                    paramScore = 1.0;
                } else {
                    // Value is outside ideal range, calculate deviation
                    const deviation = value < range[0] 
                        ? (range[0] - value) / range[0]
                        : (value - range[1]) / range[1];
                    
                    paramScore = Math.max(0, 1 - deviation);
                }
                
                totalScore += paramScore * weight;
                totalWeight += weight;
            }
        });
        
        // Normalize score to 0-100 range
        return totalWeight > 0 ? (totalScore / totalWeight) * 100 : 0;
    });
}