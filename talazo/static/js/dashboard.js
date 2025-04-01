// Enhanced dashboard.js for pitch presentations
class DashboardManager {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.dataHistory = {};
        this.currentSoilData = {};
        this.currentFarmerId = null;
        this.gauge = null;
        this.soilHealthAlgorithm = new SoilHealthAlgorithm();
        this.chartManager = new ChartManager();
        this.alertManager = new AlertManager();
        this.aiRecommendationsManager = new AIRecommendationsManager();
        
        // Demo mode settings
        this.isDemoMode = false;
        this.demoInterval = null;
        this.demoSpeed = 5000; // 5 seconds between updates in demo mode
        
        // Make instances available globally for component interaction
        window.chartManager = this.chartManager;
        window.alertManager = this.alertManager;
        window.aiRecommendationsManager = this.aiRecommendationsManager;
        
        this.init();
    }

    init() {
        console.log('Initializing Enhanced Dashboard Manager...');
        
        // Initialize UI elements
        this.refreshButton = document.getElementById('refresh-data');
        this.lastUpdateSpan = document.getElementById('last-update-time');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.farmerSelector = document.getElementById('farmer-selector');
        
        // Initialize gauge
        this.initializeGauge();
        this.initializeLoanAssessment();
        
        // Initialize other components
        this.chartManager.initializeCharts();
        this.alertManager.initializeAlerts();
        this.aiRecommendationsManager.initialize();
        
        // Set up event listeners
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => this.refreshData());
        }
        
        if (this.farmerSelector) {
            this.farmerSelector.addEventListener('change', (e) => {
                this.currentFarmerId = e.target.value;
                this.refreshData();
            });
        }
        
        // Initialize tab controls for Alerts & Recommendations
        this.setupTabControls();
        
        // Set up demo mode
        this.setupDemoMode();
        
        // Load initial data
        this.loadInitialData();
    }

    setupTabControls() {
        // Tab switching for alerts and recommendations
        const tabButtons = document.querySelectorAll('.tab-button');
        if (tabButtons.length) {
            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    // Deactivate all tabs
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    
                    // Hide all tab content
                    document.getElementById('alerts-container').classList.add('hidden');
                    document.getElementById('recommendations-container').classList.add('hidden');
                    
                    // Activate selected tab
                    button.classList.add('active');
                    
                    // Show selected content
                    const tabId = button.getAttribute('data-tab');
                    if (tabId === 'alerts') {
                        document.getElementById('alerts-container').classList.remove('hidden');
                    } else if (tabId === 'recommendations') {
                        document.getElementById('recommendations-container').classList.remove('hidden');
                    }
                });
            });
        }
        
        // Set up view toggles for soil parameters
        document.querySelectorAll('.toggle-view').forEach((button) => {
            button.addEventListener('click', function() {
                const view = this.getAttribute('data-view');
                const grid = document.getElementById('parameters-grid');
                
                // Remove active class from all view buttons
                document.querySelectorAll('.toggle-view').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Update grid view
                if (view === 'list') {
                    grid.classList.add('list-view');
                } else {
                    grid.classList.remove('list-view');
                }
            });
        });
        
        // Initialize parameter selector for chart
        const parameterSelect = document.getElementById('parameter-select');
        if (parameterSelect) {
            parameterSelect.addEventListener('change', () => {
                this.chartManager.updateChartParameter(parameterSelect.value);
            });
        }
        
        // Initialize time window buttons for chart
        const timeButtons = document.querySelectorAll('.time-window button');
        if (timeButtons.length) {
            timeButtons.forEach(button => {
                button.addEventListener('click', () => {
                    timeButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    
                    const minutes = parseInt(button.getAttribute('data-minutes'));
                    this.chartManager.updateTimeWindow(minutes);
                });
            });
        }
        
        // Set up AI recommendations generation button
        const generateRecBtn = document.getElementById('generate-recommendations-btn');
        if (generateRecBtn) {
            generateRecBtn.addEventListener('click', () => {
                this.aiRecommendationsManager.generateRecommendations(this.currentSoilData);
            });
        }
    }

    setupDemoMode() {
        // Create demo mode toggle button
        const headerControls = document.querySelector('.header-controls');
        if (!headerControls) return;
        
        const demoButton = document.createElement('button');
        demoButton.id = 'demo-mode-toggle';
        demoButton.className = 'demo-button';
        demoButton.innerHTML = '<i class="fas fa-play"></i> Demo Mode';
        
        // Insert before refresh button
        if (this.refreshButton && this.refreshButton.parentNode) {
            headerControls.insertBefore(demoButton, this.refreshButton);
        } else {
            headerControls.appendChild(demoButton);
        }
        
        // Add demo speed control
        const demoSpeedControl = document.createElement('div');
        demoSpeedControl.className = 'demo-speed hidden';
        demoSpeedControl.innerHTML = `
            <label>Demo Speed:</label>
            <div class="speed-buttons">
                <button data-speed="slow" class="active">Slow</button>
                <button data-speed="medium">Medium</button>
                <button data-speed="fast">Fast</button>
            </div>
        `;
        headerControls.insertBefore(demoSpeedControl, demoButton.nextSibling);
        
        // Set up event listeners
        demoButton.addEventListener('click', () => this.toggleDemoMode());
        
        // Demo speed buttons
        const speedButtons = demoSpeedControl.querySelectorAll('.speed-buttons button');
        speedButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Update active state
                speedButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Set speed
                const speed = button.getAttribute('data-speed');
                if (speed === 'slow') this.demoSpeed = 8000;
                else if (speed === 'medium') this.demoSpeed = 5000;
                else if (speed === 'fast') this.demoSpeed = 3000;
                
                // Restart demo interval if running
                if (this.isDemoMode) {
                    this.stopDemoInterval();
                    this.startDemoInterval();
                }
            });
        });
    }

    toggleDemoMode() {
        this.isDemoMode = !this.isDemoMode;
        
        const demoButton = document.getElementById('demo-mode-toggle');
        const demoSpeed = document.querySelector('.demo-speed');
        
        if (this.isDemoMode) {
            // Start demo mode
            this.startDemoInterval();
            if (demoButton) {
                demoButton.innerHTML = '<i class="fas fa-stop"></i> Stop Demo';
                demoButton.classList.add('active');
            }
            if (demoSpeed) demoSpeed.classList.remove('hidden');
            this.showNotification('Demo Mode Activated - Data will update automatically', 'info');
        } else {
            // Stop demo mode
            this.stopDemoInterval();
            if (demoButton) {
                demoButton.innerHTML = '<i class="fas fa-play"></i> Demo Mode';
                demoButton.classList.remove('active');
            }
            if (demoSpeed) demoSpeed.classList.add('hidden');
            this.showNotification('Demo Mode Deactivated', 'info');
        }
    }

    startDemoInterval() {
        // Clear any existing interval
        this.stopDemoInterval();
        
        // Set new interval to refresh data
        this.demoInterval = setInterval(() => {
            this.refreshData(true); // true flag indicates this is a demo update
        }, this.demoSpeed);
        
        // Initial refresh
        this.refreshData(true);
    }

    stopDemoInterval() {
        if (this.demoInterval) {
            clearInterval(this.demoInterval);
            this.demoInterval = null;
        }
    }

    initializeGauge() {
        const gaugeElement = document.getElementById('financial-gauge');
        if (!gaugeElement) {
            console.error('Financial gauge element not found');
            return;
        }

        console.log('Initializing gauge...');

        // Ensure GaugeChart is defined before using it
        if (typeof GaugeChart !== 'undefined') {
            this.gauge = GaugeChart.gaugeChart(gaugeElement, {
                hasNeedle: true,
                needleColor: '#464A4F',
                arcColors: ['#E74C3C', '#F39C12', '#2ECC71'],
                arcDelimiters: [40, 60],
                rangeLabel: ['0', '100'],
                centralLabel: '0'
            });
        } else {
            console.error('GaugeChart library is not loaded');
        }
    }
    
    initializeLoanAssessment() {
        const loanStatusIndicator = document.getElementById('loan-status-indicator');
        if (!loanStatusIndicator) return;
        
        // Default to ineligible state until we get data
        this.updateLoanEligibility(0);
        
        // Set up loan processing button
        const processLoanBtn = document.getElementById('process-loan-btn');
        if (processLoanBtn) {
            processLoanBtn.addEventListener('click', () => this.processLoanApplication());
        }
        
        // Set up view history button
        const viewHistoryBtn = document.getElementById('view-history-btn');
        if (viewHistoryBtn) {
            viewHistoryBtn.addEventListener('click', () => this.viewLoanHistory());
        }
    }

    loadInitialData() {
        // Load initial data with predefined optimal values
        const initialData = this.generateOptimalData();
        this.updateDashboard(initialData);
        this.updateLastUpdate();
    }

    generateOptimalData() {
        // Generate sample data with optimal values for initial display
        const soilData = {
            ph_level: 6.5,
            nitrogen_level: 32,
            phosphorus_level: 25,
            potassium_level: 220,
            organic_matter: 4.2,
            cation_exchange_capacity: 15.4,
            moisture_content: 28
        };
        
        // Calculate health score using soil health algorithm
        const healthScore = this.soilHealthAlgorithm.calculateScore(soilData);
        
        // Calculate risk level, premium, etc.
        const riskLevel = this.soilHealthAlgorithm.determineRiskLevel(healthScore);
        const premium = this.soilHealthAlgorithm.calculatePremium(healthScore);
        
        // Generate trend data based on current values
        const trendData = this.generateTrendData(soilData);
        
        // Generate yield prediction
        const yieldPrediction = {
            predicted_yield: 5.2,
            yield_range: {
                lower: 4.8,
                upper: 5.6,
            },
            confidence: 85,
            unit: 'tons per hectare'
        };
        
        // Generate crop recommendations
        const recommendedCrops = this.soilHealthAlgorithm.recommendSuitableCrops(soilData);
        
        // Generate recommendations
        const recommendations = this.soilHealthAlgorithm.getRecommendations(soilData, this.getCurrentRegion(), this.getCurrentCrop());
        
        // Build complete initial dashboard data
        return {
            soil_health: {
                initial: true,
                timestamp: new Date().toISOString(),
                soil_data: soilData,
                health_score: healthScore,
                risk_level: riskLevel,
                parameter_scores: {
                    ph_level: 95,
                    nitrogen_level: 90,
                    phosphorus_level: 88,
                    potassium_level: 92,
                    organic_matter: 85,
                    cation_exchange_capacity: 78,
                    moisture_content: 89
                }
            },
            financial: {
                index_score: healthScore,
                risk_level: riskLevel,
                premium_estimate: premium,
                loan_eligibility: healthScore >= 40
            },
            trend_data: trendData,
            yield_prediction: yieldPrediction,
            recommended_crops: recommendedCrops,
            recommendations: recommendations,
            metadata: {
                farmer_id: this.currentFarmerId || 1,
                farmer_name: 'Demo Farmer',
                primary_crop: this.getCurrentCrop(),
                generated_at: new Date().toISOString()
            }
        };
    }

    async refreshData(isDemoUpdate = false) {
        try {
            if (!isDemoUpdate) {
                console.log('Fetching new data...');
                this.showLoading();
            }
            
            let response;
            
            try {
                // For pitch presentations, always use simulated data
                throw new Error("Using simulated data for presentation");
                
                // In a real environment, this would fetch from the API:
                // response = await fetch('/api/demo-data');
                // if (!response.ok) throw new Error(`API request failed with status ${response.status}`);
                // const data = await response.json();
                // this.processApiData(data);
                
            } catch (error) {
                console.warn('Using simulated data for presentation', error);
                
                // Generate simulated data
                const data = this.generateSimulatedData(isDemoUpdate);
                this.updateDashboard(data);
            }
            
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showError('Failed to update dashboard data. Using simulated data.');
            
            // Use simulated data as fallback
            const data = this.generateSimulatedData(isDemoUpdate);
            this.updateDashboard(data);
            
        } finally {
            this.hideLoading();
        }
    }

    generateSimulatedData(isDemoUpdate = false) {
        // Keep changes smaller for demo updates to make the transitions smoother
        const variationFactor = isDemoUpdate ? 0.3 : 1.0;
        
        // Get random value in range with controlled variation
        const getRandomInRange = (min, max, currentValue = null) => {
            if (currentValue !== null && isDemoUpdate) {
                // Create small variation from current value for demo mode
                const maxChange = (max - min) * 0.15 * variationFactor;
                const change = (Math.random() * 2 - 1) * maxChange; // Random change between -maxChange and +maxChange
                return Math.max(min, Math.min(max, currentValue + change));
            } else {
                // Generate a new random value in range
                return Math.min(max, Math.max(min, min + (Math.random() * (max - min))));
            }
        };
        
        // Get current soil data or initialize
        const currentSoilData = this.currentSoilData || {};
        
        // Generate soil parameters with controlled randomness
        const soilData = {
            ph_level: getRandomInRange(5.5, 7.5, currentSoilData.ph_level),
            nitrogen_level: getRandomInRange(15, 45, currentSoilData.nitrogen_level),
            phosphorus_level: getRandomInRange(15, 35, currentSoilData.phosphorus_level),
            potassium_level: getRandomInRange(150, 250, currentSoilData.potassium_level),
            organic_matter: getRandomInRange(2, 6, currentSoilData.organic_matter),
            cation_exchange_capacity: getRandomInRange(10, 20, currentSoilData.cation_exchange_capacity),
            moisture_content: getRandomInRange(15, 35, currentSoilData.moisture_content)
        };
        
        // Calculate health score using soil health algorithm
        const healthScore = this.soilHealthAlgorithm.calculateScore(soilData);
        
        // Calculate risk level, premium, etc. using soil health algorithm
        const riskLevel = this.soilHealthAlgorithm.determineRiskLevel(healthScore);
        const premium = this.soilHealthAlgorithm.calculatePremium(healthScore);
        
        // Generate trend data
        const trendData = this.generateTrendData(soilData);
        
        // Generate yield prediction with more realistic variations
        let yieldBase = healthScore / 20; // Base yield correlates with soil health
        
        const yieldPrediction = {
            predicted_yield: getRandomInRange(yieldBase * 0.9, yieldBase * 1.1),
            yield_range: {
                lower: getRandomInRange(yieldBase * 0.7, yieldBase * 0.9),
                upper: getRandomInRange(yieldBase * 1.1, yieldBase * 1.3),
            },
            confidence: getRandomInRange(70, 95),
            unit: 'tons per hectare'
        };
        
        // Generate crop recommendations based on soil data
        const recommendedCrops = this.soilHealthAlgorithm.recommendSuitableCrops(soilData);
        
        // Generate recommendations
        const recommendations = this.soilHealthAlgorithm.getRecommendations(soilData, this.getCurrentRegion(), this.getCurrentCrop());
        
        // Build complete simulated dashboard data
        return {
            soil_health: {
                simulated: true,
                timestamp: new Date().toISOString(),
                soil_data: soilData,
                health_score: healthScore,
                risk_level: riskLevel,
                parameter_scores: {
                    ph_level: getRandomInRange(60, 100),
                    nitrogen_level: getRandomInRange(60, 100),
                    phosphorus_level: getRandomInRange(60, 100),
                    potassium_level: getRandomInRange(60, 100),
                    organic_matter: getRandomInRange(60, 100),
                    cation_exchange_capacity: getRandomInRange(60, 100),
                    moisture_content: getRandomInRange(60, 100)
                }
            },
            financial: {
                index_score: healthScore,
                risk_level: riskLevel,
                premium_estimate: premium,
                loan_eligibility: healthScore >= 40
            },
            trend_data: trendData,
            yield_prediction: yieldPrediction,
            recommended_crops: recommendedCrops,
            recommendations: recommendations,
            metadata: {
                farmer_id: this.currentFarmerId || 1,
                farmer_name: this.getCurrentFarmerName(),
                primary_crop: this.getCurrentCrop(),
                generated_at: new Date().toISOString()
            }
        };
    }

    generateTrendData(currentSoilData) {
        // Generate historical trend data based on current values
        const now = new Date();
        const data = [];
        
        // Generate data points for the last 24 hours at 30-minute intervals
        for (let i = 0; i < 48; i++) {
            const timestamp = new Date(now.getTime() - (i * 30 * 60 * 1000));
            
            // Variation factors per parameter
            const variations = {
                ph_level: (Math.sin(i * 0.1) * 0.2) + (Math.random() * 0.1),
                nitrogen_level: (Math.sin(i * 0.05) * 3) + (Math.random() * 1.5),
                phosphorus_level: (Math.sin(i * 0.07) * 2) + (Math.random() * 1),
                potassium_level: (Math.sin(i * 0.03) * 10) + (Math.random() * 5),
                organic_matter: (Math.sin(i * 0.02) * 0.3) + (Math.random() * 0.2),
                cation_exchange_capacity: (Math.sin(i * 0.06) * 1) + (Math.random() * 0.5),
                moisture_content: (Math.sin(i * 0.12) * 4) + (Math.random() * 2)
            };
            
            // Calculate values with variation from current
            const point = {
                timestamp: timestamp.toISOString()
            };
            
            for (const [param, currentValue] of Object.entries(currentSoilData)) {
                if (param === 'timestamp') continue;
                const variation = variations[param] || 0;
                point[param] = Math.max(0, parseFloat(currentValue) + variation);
            }
            
            data.push(point);
        }
        
        // Calculate health score for each point
        const healthScores = data.map(point => {
            const soilData = {...point};
            delete soilData.timestamp;
            
            // Calculate score using soil health algorithm
            return this.soilHealthAlgorithm.calculateScore(soilData);
        });
        
        return {
            points: data,
            scores: healthScores
        };
    }

    updateDashboard(data) {
        // Update Financial Index Gauge
        if (data.soil_health) {
            this.updateFinancialGauge(data.soil_health);
            
            // Store current soil data for other components
            if (data.soil_health.soil_data) {
                this.currentSoilData = data.soil_health.soil_data;
                
                // Update parameters display
                this.updateParameters(data.soil_health.soil_data);
            }
            
            // Update loan eligibility based on health score
            this.updateLoanEligibility(data.soil_health.health_score);
        }
        
        // Update other components
        this.updateLastUpdate();
        
        // Update crop recommendations
        if (data.recommended_crops) {
            this.updateCropRecommendations(data.recommended_crops);
        }
        
        // Update yield prediction
        if (data.yield_prediction) {
            this.updateYieldPrediction(data.yield_prediction);
        }
        
        // Update chart data
        if (data.trend_data) {
            this.chartManager.updateCharts(data.trend_data);
        }
        
        // Update alerts and recommendations
        const alerts = this.generateAlertsFromSoilData(this.currentSoilData);
        this.alertManager.updateAlerts({
            alerts: alerts,
            recommendations: data.recommendations || []
        });
        
        // Update AI recommendations if available
        if (data.recommendations) {
            this.aiRecommendationsManager.displayRecommendations({
                status: 'success',
                recommendations: data.recommendations,
                metadata: {
                    source: data.metadata?.source || 'system',
                    request_context: {
                        region: this.getCurrentRegion(),
                        crop: this.getCurrentCrop()
                    },
                    timestamp: new Date().toISOString()
                }
            });
        }
    }

    updateFinancialGauge(financialData) {
        if (!financialData) {
            console.warn('No financial data received');
            return;
        }

        const score = financialData.health_score || 0;
        console.log('Updating gauge with value:', score);
        
        // Update gauge value
        if (this.gauge) {
            this.gauge.updateValue(score);
        } else {
            console.error('Gauge not initialized');
        }

        // Update related metrics
        const riskElement = document.getElementById('risk-level-indicator');
        const premiumElement = document.getElementById('premium-value');
        const yieldElement = document.getElementById('yield-prediction');

        const riskLevel = financialData.risk_level || this.soilHealthAlgorithm.determineRiskLevel(score);
        const premium = financialData.premium_estimate || this.soilHealthAlgorithm.calculatePremium(score);
        const yieldPrediction = 3.5; // Default value if not provided

        if (riskElement) riskElement.textContent = riskLevel;
        if (premiumElement) premiumElement.textContent = premium.toFixed(2);
        if (yieldElement) yieldElement.textContent = yieldPrediction.toFixed(2);
    }
    
    updateLoanEligibility(score) {
        const loanStatusIndicator = document.getElementById('loan-status-indicator');
        const maxLoanAmount = document.getElementById('max-loan-amount');
        const interestRate = document.getElementById('interest-rate');
        const loanTerm = document.getElementById('loan-term');
        
        if (!loanStatusIndicator) return;
        
        let statusClass, statusText, loanAmount, rate, term;
        
        if (score >= 70) {
            statusClass = 'eligible';
            statusText = 'Eligible';
            loanAmount = (score * 50).toFixed(2);
            rate = '5.75';
            term = '36';
        } else if (score >= 40) {
            statusClass = 'conditional';
            statusText = 'Conditional';
            loanAmount = (score * 30).toFixed(2);
            rate = '8.25';
            term = '24';
        } else {
            statusClass = 'ineligible';
            statusText = 'Ineligible';
            loanAmount = '0.00';
            rate = 'N/A';
            term = 'N/A';
        }
        
        loanStatusIndicator.className = 'status-indicator ' + statusClass;
        loanStatusIndicator.innerHTML = `
            <div class="status-text">${statusText}</div>
            <div class="score">${Math.round(score)}</div>
        `;
        
        if (maxLoanAmount) maxLoanAmount.textContent = loanAmount;
        if (interestRate) interestRate.textContent = rate;
        if (loanTerm) loanTerm.textContent = term;
        
        // Update the process loan button state
        const processLoanBtn = document.getElementById('process-loan-btn');
        if (processLoanBtn) {
            processLoanBtn.disabled = score < 40;
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
            // Skip non-soil parameters
            if (key === 'timestamp' || key === 'sample_id') return;
            
            const card = this.createParameterCard(key, value);
            grid.appendChild(card);
        });
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
            cation_exchange_capacity: { optimal: [10, 20], warning: [5, 25] },
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
    
    updateCropRecommendations(crops) {
        if (!crops || !Array.isArray(crops)) {
            console.warn('No crop recommendations data received');
            return;
        }

        const listElement = document.getElementById('suitable-crops-list');
        if (!listElement) {
            console.error('Suitable crops list element not found');
            return;
        }

        console.log('Updating crop recommendations:', crops);
        
        listElement.innerHTML = '';
        
        if (crops.length === 0) {
            listElement.innerHTML = '<li>No suitable crops found for current soil conditions</li>';
            return;
        }
        
        crops.forEach(crop => {
            const li = document.createElement('li');
            li.className = 'crop-item';
            li.innerHTML = `<span class="crop-name">${crop}</span>`;
            listElement.appendChild(li);
        });
    }
    
    updateYieldPrediction(prediction) {
        if (!prediction) {
            console.warn('No yield prediction data received');
            return;
        }
        
        // Update yield prediction value in gauge details
        const yieldElement = document.getElementById('yield-prediction');
        if (yieldElement) {
            yieldElement.textContent = prediction.predicted_yield.toFixed(2);
        }
        
        // Update yield chart
        this.updateYieldChart(prediction);
    }
    
    updateYieldChart(prediction) {
        const yieldChartElement = document.getElementById('yield-chart');
        if (!yieldChartElement) return;

        // Get suitable crops from list
        const cropsList = document.querySelectorAll('#suitable-crops-list .crop-name');
        const crops = Array.from(cropsList).map(item => item.textContent);

        if (crops.length === 0) return;

        // Create yield data based on prediction and crops
        const baseYield = prediction.predicted_yield || 3.5;
        const yields = crops.map((crop, index) => {
            // Calculate a yield based on crop and base yield
            const cropFactor = 0.8 + (index / 10); // First crops are more suitable
            const yieldValue = baseYield * cropFactor * (0.9 + Math.random() * 0.2);

            return {
                crop: crop,
                yield: yieldValue.toFixed(2)
            };
        });

        // Sort by yield
        yields.sort((a, b) => b.yield - a.yield);

        if (typeof Plotly !== 'undefined') {
            const data = [
                {
                    x: yields.map(item => item.crop),
                    y: yields.map(item => parseFloat(item.yield)),
                    type: 'bar',
                    marker: {
                        color: '#27AE60'
                    }
                }
            ];

            const layout = {
                margin: { t: 10, l: 40, r: 20, b: 50 },
                yaxis: {
                    title: 'Yield (tons/ha)',
                    range: [0, Math.max(...yields.map(item => parseFloat(item.yield))) * 1.2]
                },
                xaxis: {
                    title: 'Crop'
                },
                font: {
                    family: 'Poppins, sans-serif'
                }
            };

            Plotly.newPlot(yieldChartElement, data, layout, { responsive: true });
        } else {
            console.error('Plotly library is not loaded');
        }
    }
    
    generateAlertsFromSoilData(soilData) {
        // Generate alerts based on soil data
        const alerts = [];
        
        if (!soilData) {
            return alerts;
        }
        
        const now = new Date().toISOString();
        
        // Check pH level
        if (soilData.ph_level < 5.5) {
            alerts.push({
                id: 'alert-ph-low',
                title: 'Critical pH Level',
                message: `Soil pH is ${soilData.ph_level}, which is extremely acidic. Urgent lime application recommended.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.ph_level < 6.0) {
            alerts.push({
                id: 'alert-ph-warning',
                title: 'Low pH Level',
                message: `Soil pH is ${soilData.ph_level}, which is moderately acidic. Consider lime application.`,
                priority: 'warning',
                timestamp: now
            });
        } else if (soilData.ph_level > 7.5) {
            alerts.push({
                id: 'alert-ph-high',
                title: 'High pH Level',
                message: `Soil pH is ${soilData.ph_level}, which is alkaline. Consider adding organic matter.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check nitrogen level
        if (soilData.nitrogen_level < 15) {
            alerts.push({
                id: 'alert-nitrogen-low',
                title: 'Critical Nitrogen Deficiency',
                message: `Nitrogen level is very low at ${soilData.nitrogen_level} mg/kg. Crop yield will be severely affected.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.nitrogen_level < 20) {
            alerts.push({
                id: 'alert-nitrogen-warning',
                title: 'Low Nitrogen Level',
                message: `Nitrogen level is ${soilData.nitrogen_level} mg/kg, which is below optimal range.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check phosphorus level
        if (soilData.phosphorus_level < 15) {
            alerts.push({
                id: 'alert-phosphorus-low',
                title: 'Low Phosphorus Level',
                message: `Phosphorus level is ${soilData.phosphorus_level} mg/kg, which may limit root development and flowering.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check potassium level
        if (soilData.potassium_level < 130) {
            alerts.push({
                id: 'alert-potassium-low',
                title: 'Low Potassium Level',
                message: `Potassium level is ${soilData.potassium_level} mg/kg, which may reduce stress tolerance and water efficiency.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check organic matter
        if (soilData.organic_matter < 2.0) {
            alerts.push({
                id: 'alert-organic-low',
                title: 'Critical Organic Matter',
                message: `Organic matter is very low at ${soilData.organic_matter}%. Soil structure and nutrient retention will be poor.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.organic_matter < 3.0) {
            alerts.push({
                id: 'alert-organic-warning',
                title: 'Low Organic Matter',
                message: `Organic matter is ${soilData.organic_matter}%, which is below optimal range.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check moisture content during dry season
        const currentMonth = new Date().getMonth() + 1;
        if ([5, 6, 7, 8].includes(currentMonth) && soilData.moisture_content < 15) {
            alerts.push({
                id: 'alert-moisture-low',
                title: 'Drought Risk',
                message: `Soil moisture is critically low at ${soilData.moisture_content}% during dry season. Irrigation recommended.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.moisture_content < 18) {
            alerts.push({
                id: 'alert-moisture-warning',
                title: 'Low Moisture Content',
                message: `Soil moisture is ${soilData.moisture_content}%, which may cause plant stress.`,
                priority: 'warning',
                timestamp: now
            });
        } else if (soilData.moisture_content > 35) {
            alerts.push({
                id: 'alert-moisture-high',
                title: 'High Moisture Content',
                message: `Soil moisture is high at ${soilData.moisture_content}%, which may cause waterlogging and root diseases.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        return alerts;
    }
    
    processLoanApplication() {
        const scoreElement = document.querySelector('.status-indicator .score');
        const score = parseInt(scoreElement?.textContent || '0');
        
        if (score < 40) {
            this.showNotification('Loan application cannot be processed due to low financial index score', 'error');
            return;
        }
        
        this.showLoading();
        
        // Simulate API call for loan processing
        setTimeout(() => {
            this.hideLoading();
            if (score >= 70) {
                this.showNotification('Loan application has been pre-approved! A loan officer will contact the farmer.', 'success');
                this.showLoanModal({
                    title: 'Loan Pre-Approved',
                    message: `The farmer qualifies for a loan of ${(score * 50).toFixed(2)} at 5.75% for 36 months based on soil health index.`,
                    type: 'success'
                });
            } else {
                this.showNotification('Loan application submitted for review. Additional documentation may be required.', 'warning');
                this.showLoanModal({
                    title: 'Conditional Approval',
                    message: 'Additional documentation and collateral will be required. The loan officer will contact the farmer for next steps.',
                    type: 'warning'
                });
            }
        }, 2000);
    }
    
    viewLoanHistory() {
        this.showNotification('Viewing loan history for this farmer', 'info');
        this.showLoanModal({
            title: 'Loan History',
            message: 'No previous loans have been recorded for this farmer.',
            type: 'info'
        });
    }
    
    showLoanModal(options) {
        // Create modal element if it doesn't exist
        let modal = document.querySelector('.modal-overlay');
        if (modal) {
            modal.remove(); // Remove existing modal
        }
        
        modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        let iconHtml = '';
        if (options.type === 'success') {
            iconHtml = '<i class="fas fa-check-circle" style="color: #2ECC71;"></i>';
        } else if (options.type === 'warning') {
            iconHtml = '<i class="fas fa-exclamation-triangle" style="color: #F39C12;"></i>';
        } else if (options.type === 'error') {
            iconHtml = '<i class="fas fa-times-circle" style="color: #E74C3C;"></i>';
        } else {
            iconHtml = '<i class="fas fa-info-circle" style="color: #3498DB;"></i>';
        }
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    ${iconHtml}
                    <h3>${options.title}</h3>
                    <button class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <p>${options.message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary">Continue</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.querySelector('.btn-primary').addEventListener('click', () => {
            modal.remove();
        });
        
        // Auto-close after 10 seconds
        setTimeout(() => {
            if (document.body.contains(modal)) {
                modal.remove();
            }
        }, 10000);
    }
    
    getCurrentFarmerName() {
        // Get farmer name from selector
        const farmerSelector = document.getElementById('farmer-selector');
        if (farmerSelector && farmerSelector.selectedOptions && farmerSelector.selectedOptions.length > 0) {
            const farmerText = farmerSelector.selectedOptions[0].text;
            if (farmerText.includes('(')) {
                return farmerText.split('(')[0].trim();
            }
            return farmerText;
        }
        return 'Demo Farmer';
    }
    
    getCurrentRegion() {
        // Get region from farmer selection if available
        const farmerSelector = document.getElementById('farmer-selector');
        if (farmerSelector && farmerSelector.selectedOptions && farmerSelector.selectedOptions.length > 0) {
            const farmerText = farmerSelector.selectedOptions[0].text;
            if (farmerText.includes('(')) {
                return farmerText.split('(')[1].replace(')', '').trim();
            }
        }
        return 'Zimbabwe';
    }
    
    getCurrentCrop() {
        // For now, return a default crop based on region
        const region = this.getCurrentRegion().toLowerCase();
        
        if (region.includes('harare') || region.includes('mashonaland')) {
            return 'Maize';
        } else if (region.includes('bulawayo') || region.includes('matabeleland')) {
            return 'Sorghum';
        } else if (region.includes('mutare') || region.includes('manicaland')) {
            return 'Tobacco';
        } else if (region.includes('gweru') || region.includes('midlands')) {
            return 'Cotton';
        }
        
        return 'Maize'; // Default crop
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
            const now = new Date();
            const formattedTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            element.textContent = formattedTime;
        }
    }

    showError(message) {
        console.error(message);
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type = 'default') {
        if (typeof Toastify === 'function') {
            const bgColors = {
                success: '#2ECC71',
                warning: '#F39C12',
                error: '#E74C3C',
                info: '#3498DB',
                default: '#3498DB'
            };

            Toastify({
                text: message,
                duration: 3000,
                close: true,
                gravity: 'top',
                position: 'right',
                backgroundColor: bgColors[type],
                stopOnFocus: true
            }).showToast();
        } else {
            alert(message);
        }
    }
}

// ChartManager class to handle all chart visualizations
class ChartManager {
    constructor() {
        this.charts = {};
        this.timeWindow = 30; // minutes
        this.selectedParameter = 'all';
        this.chartData = {
            timestamps: [],
            parameters: {},
            scores: []
        };
    }
    
    initializeCharts() {
        // Initialize live chart
        this.initializeLiveChart();
    }
    
    initializeLiveChart() {
        const liveChartElement = document.getElementById('live-chart');
        if (!liveChartElement || !window.Plotly) {
            console.error('Live chart element or Plotly not found');
            return;
        }
        
        // Create empty chart
        const layout = {
            title: 'Soil Parameters Trends',
            showlegend: true,
            xaxis: {
                title: 'Time',
                type: 'date',
                tickformat: '%H:%M'
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
        
        Plotly.newPlot(liveChartElement, [], layout, {responsive: true});
        this.charts.liveChart = liveChartElement;
    }
    
    updateCharts(trendData) {
        // Update chart data
        if (trendData.points) {
            this.updateChartData(trendData.points, trendData.scores);
            this.refreshLiveChart();
        }
    }
    
    updateChartData(points, scores) {
        if (!points || points.length === 0) return;
        
        // Extract timestamps
        const timestamps = points.map(point => new Date(point.timestamp));
        
        // Extract parameters
        const parameters = {};
        
        // Determine which parameters exist in the data
        const paramNames = Object.keys(points[0]).filter(key => key !== 'timestamp');
        
        // Initialize parameter arrays
        paramNames.forEach(param => {
            parameters[param] = points.map(point => point[param]);
        });
        
        // Store the data
        this.chartData = {
            timestamps: timestamps,
            parameters: parameters,
            scores: scores || []
        };
    }
    
    refreshLiveChart() {
        const liveChartElement = this.charts.liveChart;
        if (!liveChartElement || !window.Plotly) return;
        
        // Get filtered data based on time window
        const { timestamps, parameters } = this.getFilteredData();
        
        if (timestamps.length === 0) return;
        
        // Create traces based on selected parameter
        const traces = [];
        
        if (this.selectedParameter === 'all') {
            // Show all parameters
            Object.entries(parameters).forEach(([param, values], index) => {
                if (param === 'timestamp') return;
                
                traces.push({
                    x: timestamps,
                    y: values,
                    mode: 'lines+markers',
                    name: this.formatParameterName(param),
                    line: {
                        color: this.getParameterColor(param, index)
                    },
                    type: 'scatter'
                });
            });
        } else {
            // Show only selected parameter
            const values = parameters[this.selectedParameter];
            if (values) {
                traces.push({
                    x: timestamps,
                    y: values,
                    mode: 'lines+markers',
                    name: this.formatParameterName(this.selectedParameter),
                    line: { color: '#27AE60' },
                    type: 'scatter'
                });
            }
        }
        
        // Update chart
        Plotly.react(liveChartElement, traces);
    }
    
    getFilteredData() {
        // Filter data based on time window
        const endTime = new Date();
        const startTime = new Date(endTime.getTime() - (this.timeWindow * 60 * 1000));
        
        // Find index of the first data point within the time window
        const startIndex = this.chartData.timestamps.findIndex(time => time >= startTime);
        
        if (startIndex === -1) {
            // No data within time window
            return { timestamps: [], parameters: {} };
        }
        
        // Filter timestamps
        const timestamps = this.chartData.timestamps.slice(startIndex);
        
        // Filter parameters
        const parameters = {};
        Object.entries(this.chartData.parameters).forEach(([param, values]) => {
            parameters[param] = values.slice(startIndex);
        });
        
        return { timestamps, parameters };
    }
    
    updateChartParameter(parameter) {
        this.selectedParameter = parameter;
        this.refreshLiveChart();
    }
    
    updateTimeWindow(minutes) {
        this.timeWindow = minutes;
        this.refreshLiveChart();
    }
    
    getParameterColor(parameter, index) {
        const colors = [
            '#27AE60', // Green
            '#3498DB', // Blue
            '#E74C3C', // Red
            '#F39C12', // Orange
            '#9B59B6', // Purple
            '#1ABC9C', // Turquoise
            '#34495E'  // Dark Blue
        ];
        
        // Predefined colors for specific parameters
        const paramColors = {
            'ph_level': '#3498DB',
            'nitrogen_level': '#27AE60',
            'phosphorus_level': '#E74C3C',
            'potassium_level': '#F39C12',
            'organic_matter': '#9B59B6',
            'moisture_content': '#1ABC9C'
        };
        
        return paramColors[parameter] || colors[index % colors.length];
    }
    
    formatParameterName(parameter) {
        return parameter
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}

// AlertManager class to handle alerts and recommendations
class AlertManager {
    constructor() {
        this.alerts = [];
        this.recommendations = [];
        this.maxAlerts = 5;
    }
    
    initializeAlerts() {
        // Initialize containers
        const alertsContainer = document.getElementById('alerts-container');
        const recommendationsContainer = document.getElementById('recommendations-container');
        
        if (alertsContainer) {
            alertsContainer.innerHTML = '<div class="empty-state">No alerts available</div>';
        }
        
        if (recommendationsContainer) {
            recommendationsContainer.innerHTML = '<div class="empty-state">No recommendations available</div>';
        }
        
        // Set up event delegation for dismiss buttons
        document.addEventListener('click', (event) => {
            if (event.target.closest('.dismiss-alert')) {
                const alertItem = event.target.closest('.alert-item');
                if (alertItem) {
                    this.dismissAlert(alertItem.getAttribute('data-id'));
                }
            }
        });
    }
    
    updateAlerts(data) {
        if (data.alerts) {
            this.setAlerts(data.alerts);
        }
        
        if (data.recommendations) {
            this.setRecommendations(data.recommendations);
        }
        
        this.renderAlerts();
        this.renderRecommendations();
    }
    
    setAlerts(alerts) {
        this.alerts = alerts.sort((a, b) => {
            // Sort by priority (critical first, then warning, then info)
            const priorityOrder = { 'critical': 0, 'warning': 1, 'info': 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
        
        // Keep only the most recent alerts
        if (this.alerts.length > this.maxAlerts) {
            this.alerts = this.alerts.slice(0, this.maxAlerts);
        }
    }
    
    setRecommendations(recommendations) {
        this.recommendations = recommendations.slice(0, 5); // Keep only top 5 recommendations
    }
    
    renderAlerts() {
        const container = document.getElementById('alerts-container');
        if (!container) return;
        
        if (this.alerts.length === 0) {
            container.innerHTML = '<div class="empty-state">No alerts at this time</div>';
            return;
        }
        
        container.innerHTML = '';
        
        this.alerts.forEach(alert => {
            const alertElement = document.createElement('div');
            alertElement.className = `alert-item ${alert.priority}`;
            alertElement.setAttribute('data-id', alert.id);
            
            const timestamp = new Date(alert.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            alertElement.innerHTML = `
                <div class="alert-header">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-time">${timestamp}</div>
                </div>
                <div class="alert-message">${alert.message}</div>
                <button class="dismiss-alert">Dismiss</button>
            `;
            
            container.appendChild(alertElement);
        });
    }
    
    renderRecommendations() {
        const container = document.getElementById('recommendations-container');
        if (!container) return;
        
        if (this.recommendations.length === 0) {
            container.innerHTML = '<div class="empty-state">No recommendations available</div>';
            return;
        }
        
        container.innerHTML = '';
        
        this.recommendations.forEach(recommendation => {
            const recElement = document.createElement('div');
            recElement.className = 'recommendation-item';
            
            // Determine recommendation priority
            let priority = 'medium';
            if (recommendation.cost_estimate && recommendation.cost_estimate.toLowerCase().includes('low')) {
                priority = 'low';
            } else if (recommendation.cost_estimate && recommendation.cost_estimate.toLowerCase().includes('high')) {
                priority = 'high';
            }
            
            // Create recommendation content
            let detailsHtml = '';
            if (recommendation.action) {
                detailsHtml += `<p><strong>Action:</strong> ${recommendation.action}</p>`;
            }
            if (recommendation.reason) {
                detailsHtml += `<p><strong>Reason:</strong> ${recommendation.reason}</p>`;
            }
            
            let metaHtml = '';
            if (recommendation.cost_estimate) {
                metaHtml += `<span><i class="fas fa-dollar-sign"></i> ${recommendation.cost_estimate}</span>`;
            }
            if (recommendation.timeframe) {
                metaHtml += `<span><i class="fas fa-clock"></i> ${recommendation.timeframe}</span>`;
            }
            
            let localContextHtml = '';
            if (recommendation.local_context) {
                localContextHtml = `<div class="local-context"><i class="fas fa-map-marker-alt"></i> ${recommendation.local_context}</div>`;
            }
            
            recElement.innerHTML = `
                <div class="recommendation-header">
                    <div class="recommendation-title">${recommendation.title || 'Recommendation'}</div>
                    <div class="recommendation-priority ${priority}">${priority}</div>
                </div>
                <div class="recommendation-details">${detailsHtml}</div>
                ${localContextHtml}
                <div class="recommendation-meta">${metaHtml}</div>
            `;
            
            container.appendChild(recElement);
        });
    }
    
    dismissAlert(alertId) {
        this.alerts = this.alerts.filter(alert => alert.id !== alertId);
        this.renderAlerts();
    }
}

// AIRecommendationsManager for the AI-driven insights component
class AIRecommendationsManager {
    constructor() {
        this.isLoading = false;
        this.recommendations = [];
    }
    
    initialize() {
        // Get the recommendation components
        this.loadingElement = document.getElementById('ai-recommendations-loading');
        this.contentElement = document.getElementById('ai-recommendations-content');
        this.generateButton = document.getElementById('generate-recommendations-btn');
        
        if (this.generateButton) {
            this.generateButton.addEventListener('click', () => this.generate());
        }
        
        // Initialize content
        if (this.contentElement) {
            this.contentElement.innerHTML = '<div class="empty-state">No AI recommendations available. Click the button below to generate insights.</div>';
        }
    }
    
    async generate() {
        if (this.isLoading) return;
        this.setLoading(true);
        
        try {
            // Try to fetch from the AI recommendations API (would be a real API in production)
            // For the prototype, we'll simulate a response after a delay
            setTimeout(() => {
                this.generateSimulatedRecommendations();
                this.setLoading(false);
            }, 2500);
        } catch (error) {
            console.error('Failed to generate AI recommendations:', error);
            this.setLoading(false);
            this.showError('Failed to generate AI recommendations. Please try again later.');
        }
    }
    
    generateRecommendations(soilData) {
        if (!soilData || Object.keys(soilData).length === 0) {
            this.showError('No soil data available to generate recommendations.');
            return;
        }
        
        this.generate(); // Use the simulated generator for the prototype
    }
    
    generateSimulatedRecommendations() {
        const regions = ['Mashonaland', 'Matabeleland', 'Manicaland', 'Midlands'];
        const region = regions[Math.floor(Math.random() * regions.length)];

        const crops = ['Maize', 'Groundnuts', 'Cotton', 'Sorghum', 'Soybeans'];
        const crop = crops[Math.floor(Math.random() * crops.length)];

        this.recommendations = [
            {
                type: 'soil_analysis',
                content: `Based on the analyzed soil data, your soil health is showing signs of ${Math.random() > 0.5 ? 'moderate stress' : 'good balance'} with some key areas for improvement. The pH level at ${(Math.random() * 2 + 5).toFixed(1)} indicates ${Math.random() > 0.5 ? 'slight acidity' : 'near-neutral conditions'}, which affects nutrient availability. Nitrogen levels are ${Math.random() > 0.5 ? 'below optimal range' : 'within acceptable range'}, potentially impacting plant growth and yield potential.`
            },
            {
                type: 'recommendations',
                content: `<h4>Priority Recommendations</h4>
                <ol>
                    <li>
                        <strong>ACTION:</strong> Apply ${Math.random() > 0.5 ? 'agricultural lime at 2-3 tons per hectare' : 'nitrogen fertilizer (Ammonium Nitrate) at 120-150 kg/ha'}<br>
                        <strong>REASON:</strong> ${Math.random() > 0.5 ? 'To correct soil acidity and improve nutrient availability' : 'To address nitrogen deficiency and promote vegetative growth'}<br>
                        <strong>COST:</strong> Medium<br>
                        <strong>TIMEFRAME:</strong> ${Math.random() > 0.5 ? '3-6 months for full effect' : '2-4 weeks for visible results'}<br>
                        <strong>LOCAL CONSIDERATIONS:</strong> ${Math.random() > 0.5 ? 'Lime is available from agricultural supply stores in most districts' : 'Split application recommended during the growing season in Zimbabwe\'s climate'}
                    </li>
                    <li>
                        <strong>ACTION:</strong> ${Math.random() > 0.5 ? 'Implement water conservation techniques such as mulching and tied ridges' : 'Incorporate organic matter and crop residues into the soil'}<br>
                        <strong>REASON:</strong> ${Math.random() > 0.5 ? 'To improve soil moisture retention and reduce evaporation' : 'To enhance soil structure and nutrient retention'}<br>
                        <strong>COST:</strong> Low<br>
                        <strong>TIMEFRAME:</strong> ${Math.random() > 0.5 ? 'Immediate effect' : '1-2 months for visible results'}<br>
                        <strong>LOCAL CONSIDERATIONS:</strong> ${Math.random() > 0.5 ? 'Mulching materials are readily available in most farming areas' : 'Organic matter can be sourced from crop residues or compost'}
                    </li>
                </ol>`
            }
        ];

        if (this.contentElement) {
            this.contentElement.innerHTML = this.recommendations.map(rec => `<div class="recommendation">${rec.content}</div>`).join('');
        }
    }
    
    setLoading(isLoading) {
        this.isLoading = isLoading;
        if (this.loadingElement) {
            this.loadingElement.classList.toggle('hidden', !isLoading);
        }
        if (this.contentElement) {
            this.contentElement.classList.toggle('hidden', isLoading);
        }
    }
    
    showError(message) {
        console.error(message);
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type = 'default') {
        if (typeof Toastify === 'function') {
            const bgColors = {
                success: '#2ECC71',
                warning: '#F39C12',
                error: '#E74C3C',
                info: '#3498DB',
                default: '#3498DB'
            };

            Toastify({
                text: message,
                duration: 3000,
                close: true,
                gravity: 'top',
                position: 'right',
                backgroundColor: bgColors[type],
                stopOnFocus: true
            }).showToast();
        } else {
            alert(message);
        }
    }
}