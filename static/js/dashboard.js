class DashboardManager {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.dataHistory = {};
        this.gauge = null;
        this.init();
    }

    init() {
        // Initialize UI elements
        this.refreshButton = document.getElementById('refresh-data');
        this.lastUpdateSpan = document.getElementById('last-update-time');
        this.loadingOverlay = document.getElementById('loading-overlay');

        // Initialize gauge
        this.initializeGauge();
        
        // Set up event listeners
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => this.refreshData());
        }
        
        // Initialize parameter selector
        const parameterSelect = document.getElementById('parameter-select');
        if (parameterSelect) {
            parameterSelect.addEventListener('change', (e) => {
                if (window.chartManager) {
                    window.chartManager.updateParameterVisibility(e.target.value);
                }
            });
        }
        
        // Set up time window buttons
        document.querySelectorAll('.time-window button').forEach(button => {
            button.addEventListener('click', () => {
                document.querySelectorAll('.time-window button').forEach(b => b.classList.remove('active'));
                button.classList.add('active');
                // Update chart time window if needed
            });
        });
        
        // Start automatic updates
        this.refreshData();
        setInterval(() => this.refreshData(), this.updateInterval);
        
        console.log('Dashboard manager initialized');
    }

    initializeGauge() {
        const gaugeElement = document.getElementById('financial-gauge');
        if (!gaugeElement) {
            console.error('Financial gauge element not found');
            return;
        }

        console.log('Initializing gauge');
        
        // Initialize with GaugeChart
        this.gauge = GaugeChart.gaugeChart(gaugeElement, {
            hasNeedle: true,
            needleColor: '#464A4F',
            arcColors: ['#FF6B6B', '#FFD93D', '#6BCB77'],
            arcDelimiters: [40, 60],
            rangeLabel: ['0', '100'],
            centralLabel: '0'
        });
    }

    async refreshData() {
        try {
            console.log('Fetching new data...');
            this.showLoading();
            
            // Fetch soil data from API
            const response = await fetch('/api/soil-data');
            if (!response.ok) {
                throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Received data:', data);

            // Update UI components
            this.updateFinancialGauge(data.financial_index);
            this.updateParameters(data.parameters);
            this.updateLastUpdate();
            this.updateCropRecommendations(data.recommendations);
            
            // Trigger chart updates
            if (window.chartManager) {
                window.chartManager.updateCharts(data);
            }
            
            // Update alerts
            if (window.alertManager) {
                window.alertManager.updateAlerts({
                    alerts: data.alerts,
                    recommendations: data.recommendations
                });
            }

        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showError('Failed to update dashboard data');
        } finally {
            this.hideLoading();
        }
    }

    updateFinancialGauge(financialIndex) {
        if (!financialIndex) {
            console.warn('No financial index data received');
            return;
        }

        console.log('Updating gauge with value:', financialIndex.score);
        
        // Update gauge value
        if (this.gauge) {
            this.gauge.updateValue(financialIndex.score);
        } else {
            console.error('Gauge not initialized');
        }

        // Update related metrics
        const riskElement = document.getElementById('risk-level-indicator');
        const premiumElement = document.getElementById('premium-value');
        const yieldElement = document.getElementById('yield-prediction');

        if (riskElement) riskElement.textContent = financialIndex.risk_level;
        if (premiumElement) premiumElement.textContent = financialIndex.premium.toFixed(2);
        if (yieldElement && financialIndex.yield_prediction) {
            yieldElement.textContent = financialIndex.yield_prediction.toFixed(2);
        }
    }

    updateParameters(parameters) {
        if (!parameters) {
            console.warn('No parameter data received');
            return;
        }

        const grid = document.getElementById('parameters-grid');
        if (!grid) {
            console.error('Parameters grid element not found');
            return;
        }

        console.log('Updating parameters:', parameters);
        grid.innerHTML = ''; // Clear existing parameters

        Object.entries(parameters).forEach(([key, value]) => {
            const card = this.createParameterCard(key, value);
            grid.appendChild(card);
        });
    }

    updateCropRecommendations(recommendations) {
        if (!recommendations) {
            console.warn('No recommendations data received');
            return;
        }

        const listElement = document.getElementById('suitable-crops-list');
        if (!listElement) {
            console.error('Suitable crops list element not found');
            return;
        }

        console.log('Updating crop recommendations:', recommendations);
        
        listElement.innerHTML = '';
        
        if (Array.isArray(recommendations)) {
            recommendations.forEach(crop => {
                const li = document.createElement('li');
                li.className = 'crop-item';
                li.innerHTML = `<span class="crop-name">${crop}</span>`;
                listElement.appendChild(li);
            });
        }
    }

    createParameterCard(parameter, value) {
        const card = document.createElement('div');
        card.className = `parameter-card ${this.getParameterStatus(parameter, value)}`;
        
        card.innerHTML = `
            <h3>${this.formatParameterName(parameter)}</h3>
            <div class="value">${typeof value === 'number' ? value.toFixed(2) : value}</div>
            <div class="unit">${this.getParameterUnit(parameter)}</div>
        `;

        return card;
    }

    getParameterStatus(parameter, value) {
        const ranges = {
            ph_level: { optimal: [6.0, 7.0], warning: [5.5, 7.5] },
            nitrogen_level: { optimal: [20, 40], warning: [15, 45] },
            phosphorus_level: { optimal: [20, 30], warning: [15, 35] },
            potassium_level: { optimal: [150, 250], warning: [100, 300] },
            organic_matter: { optimal: [3, 5], warning: [2, 6] },
            moisture_content: { optimal: [20, 30], warning: [15, 35] }
        };

        const range = ranges[parameter];
        if (!range) return '';

        const val = parseFloat(value);
        if (val >= range.optimal[0] && val <= range.optimal[1]) return 'optimal';
        if (val >= range.warning[0] && val <= range.warning[1]) return 'warning';
        return 'critical';
    }

    formatParameterName(parameter) {
        return parameter
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    getParameterUnit(parameter) {
        const units = {
            ph_level: 'pH',
            nitrogen_level: 'mg/kg',
            phosphorus_level: 'mg/kg',
            potassium_level: 'mg/kg',
            organic_matter: '%',
            cation_exchange_capacity: 'meq/100g',
            moisture_content: '%'
        };
        return units[parameter] || '';
    }

    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.remove('hidden');
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.add('hidden');
    }

    updateLastUpdate() {
        const element = document.getElementById('last-update-time');
        if (element) {
            element.textContent = new Date().toLocaleTimeString();
        }
    }

    showError(message) {
        console.error(message);
        if (typeof Toastify === 'function') {
            Toastify({
                text: message,
                duration: 3000,
                close: true,
                gravity: "top",
                position: "right",
                backgroundColor: "#ff4444"
            }).showToast();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing dashboard');
    window.dashboardManager = new DashboardManager();
});