// Enhanced dashboard.js - Main controller for the Talazo AgriFinance Dashboard
class DashboardManager {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.dataHistory = [];
        this.currentSoilData = {};
        this.currentFarmerId = null;
        this.gauge = null;
        this.gaugeValue = 0;
        this.soilHealthAlgorithm = new SoilHealthAlgorithm();
        this.chartManager = new ChartManager();
        this.alertManager = new AlertManager();
        this.aiRecommendationsManager = new AIRecommendationsManager();
        
        // Make instances available globally for component interaction
        window.chartManager = this.chartManager;
        window.alertManager = this.alertManager;
        window.aiRecommendationsManager = this.aiRecommendationsManager;
        
        // Bind methods to preserve context
        this.refreshData = this.refreshData.bind(this);
        this.updateDashboard = this.updateDashboard.bind(this);
        
        this.init();
    }

    init() {
        console.log('Initializing Enhanced Dashboard Manager...');
        
        // Initialize UI elements
        this.refreshButton = document.getElementById('refresh-data');
        this.lastUpdateSpan = document.getElementById('last-update-time');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.farmerSelector = document.getElementById('farmer-selector');
        
        // Initialize gauge with error handling
        this.initializeGauge();
        
        // Initialize loan assessment
        this.initializeLoanAssessment();
        
        // Initialize other components (only if they exist)
        if (typeof ChartManager !== 'undefined') {
            this.chartManager.initializeCharts();
        }
        if (typeof AlertManager !== 'undefined') {
            this.alertManager.initializeAlerts();
        }
        if (typeof AIRecommendationsManager !== 'undefined') {
            this.aiRecommendationsManager.initialize();
        }
        
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
        
        // Initialize tab controls
        this.setupTabControls();
        
        // Load initial data
        this.loadInitialData();
        
        // Start automatic updates
        setInterval(() => this.refreshData(), this.updateInterval);
    }

    loadInitialData() {
        console.log('Loading initial data...');
        
        // Generate initial simulated data
        const initialData = this.generateSimulatedData();
        
        // Update dashboard with initial data
        this.updateDashboard(initialData);
        
        // Hide loading overlay
        this.hideLoading();
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
                    const alertsContainer = document.getElementById('alerts-container');
                    const recommendationsContainer = document.getElementById('recommendations-container');
                    
                    if (alertsContainer) alertsContainer.classList.add('hidden');
                    if (recommendationsContainer) recommendationsContainer.classList.add('hidden');
                    
                    // Activate selected tab
                    button.classList.add('active');
                    
                    // Show selected content
                    const tabId = button.getAttribute('data-tab');
                    if (tabId === 'alerts' && alertsContainer) {
                        alertsContainer.classList.remove('hidden');
                    } else if (tabId === 'recommendations' && recommendationsContainer) {
                        recommendationsContainer.classList.remove('hidden');
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
                if (grid) {
                    if (view === 'list') {
                        grid.classList.add('list-view');
                    } else {
                        grid.classList.remove('list-view');
                    }
                }
            });
        });
        
        // Initialize parameter selector for chart
        const parameterSelect = document.getElementById('parameter-select');
        if (parameterSelect && this.chartManager && this.chartManager.updateChartParameter) {
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
                    if (this.chartManager && this.chartManager.updateTimeWindow) {
                        this.chartManager.updateTimeWindow(minutes);
                    }
                });
            });
        }
        
        // Set up AI recommendations generation button
        const generateRecBtn = document.getElementById('generate-recommendations-btn');
        if (generateRecBtn) {
            generateRecBtn.addEventListener('click', () => {
                if (this.aiRecommendationsManager && this.aiRecommendationsManager.generateRecommendations) {
                    this.aiRecommendationsManager.generateRecommendations(this.currentSoilData);
                }
            });
        }
    }

    initializeGauge() {
        const gaugeElement = document.getElementById('financial-gauge');
        if (!gaugeElement) {
            console.warn('Financial gauge element not found');
            this.createFallbackGauge();
            return;
        }

        console.log('Initializing gauge...');

        // Always use fallback gauge for now to ensure compatibility
        this.createFallbackGauge();
    }

    createFallbackGauge() {
        console.log('Creating fallback gauge display');
        const gaugeElement = document.getElementById('financial-gauge');
        if (gaugeElement) {
            gaugeElement.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <div id="gauge-value" style="font-size: 48px; font-weight: bold; color: #2E7D32;">0</div>
                    <div style="font-size: 14px; color: #666;">Financial Health Score</div>
                    <div id="gauge-indicator" style="width: 200px; height: 20px; background: #e0e0e0; border-radius: 10px; margin: 10px auto; position: relative;">
                        <div id="gauge-fill" style="height: 100%; background: #2ECC71; border-radius: 10px; width: 0%; transition: width 0.5s ease;"></div>
                    </div>
                </div>
            `;
        }
        
        // Create a simple object to mimic gauge behavior
        this.gauge = {
            updateValue: (value) => {
                this.gaugeValue = value;
                const valueElement = document.getElementById('gauge-value');
                const fillElement = document.getElementById('gauge-fill');
                
                if (valueElement) {
                    valueElement.textContent = Math.round(value);
                    valueElement.style.color = value >= 60 ? '#2ECC71' : value >= 40 ? '#F39C12' : '#E74C3C';
                }
                
                if (fillElement) {
                    fillElement.style.width = value + '%';
                    fillElement.style.background = value >= 60 ? '#2ECC71' : value >= 40 ? '#F39C12' : '#E74C3C';
                }
            }
        };
    }

    updateGaugeDisplay(value) {
        // Update the gauge visualization
        if (this.gauge && this.gauge.updateValue) {
            this.gauge.updateValue(value);
        }

        // Update the text value in the main score display
        const mainScoreElement = document.getElementById('mainScore');
        if (mainScoreElement) {
            mainScoreElement.textContent = Math.round(value);
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

    async refreshData() {
        try {
            console.log('Fetching new data...');
            this.showLoading();
            
            let response;
            let data;
            
            try {
                // Try to fetch from API
                response = await fetch('/api/demo-data');
                
                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }
                
                data = await response.json();
                
            } catch (error) {
                console.warn('Failed to fetch from API, using simulated data', error);
                // Generate simulated data as fallback
                data = this.generateSimulatedData();
            }
            
            // Store historical data
            this.dataHistory.push({
                timestamp: new Date(),
                data: data
            });
            
            // Keep only last 100 data points
            if (this.dataHistory.length > 100) {
                this.dataHistory = this.dataHistory.slice(-100);
            }
            
            // Update dashboard
            this.updateDashboard(data);
            
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showError('Failed to update dashboard data. Using simulated data.');
            
            // Use simulated data as fallback
            const simulatedData = this.generateSimulatedData();
            this.updateDashboard(simulatedData);
            
        } finally {
            this.hideLoading();
        }
    }

    updateDashboard(data) {
        if (!data) {
            console.error('No data provided to updateDashboard');
            return;
        }

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
        if (data.trend_data && this.chartManager && this.chartManager.updateCharts) {
            this.chartManager.updateCharts(data.trend_data);
        }
        
        // Update alerts and recommendations
        const alerts = this.generateAlertsFromSoilData(this.currentSoilData);
        if (this.alertManager && this.alertManager.updateAlerts) {
            this.alertManager.updateAlerts({
                alerts: alerts,
                recommendations: data.recommendations || []
            });
        }
        
        // Update AI recommendations if available
        if (data.recommendations && this.aiRecommendationsManager && this.aiRecommendationsManager.displayRecommendations) {
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
    
    generateSimulatedData() {
        // Generate random soil data with realistic values
        const getRandomInRange = (min, max) => {
            return Math.round((Math.random() * (max - min) + min) * 100) / 100;
        };
        
        // Health score between 0-100, weighted toward middle range
        const healthScore = Math.round(40 + getRandomInRange(-10, 30) + getRandomInRange(0, 40));
        
        // Generate soil parameters with controlled randomness
        const soilData = {
            ph_level: getRandomInRange(5.5, 7.5),
            nitrogen_level: getRandomInRange(15, 45),
            phosphorus_level: getRandomInRange(15, 35),
            potassium_level: getRandomInRange(150, 250),
            organic_matter: getRandomInRange(2, 6),
            cation_exchange_capacity: getRandomInRange(10, 20),
            moisture_content: getRandomInRange(15, 35)
        };
        
        // Calculate risk level, premium, etc. using soil health algorithm
        const riskLevel = this.soilHealthAlgorithm ? this.soilHealthAlgorithm.determineRiskLevel(healthScore) : 'Medium';
        const premium = this.soilHealthAlgorithm ? this.soilHealthAlgorithm.calculatePremium(healthScore) : 100;
        
        // Generate trend data
        const trendData = this.generateTrendData(soilData);
        
        // Generate yield prediction
        const yieldPrediction = {
            predicted_yield: getRandomInRange(2.5, 6),
            yield_range: {
                lower: getRandomInRange(1.5, 2.5),
                upper: getRandomInRange(6, 8),
            },
            confidence: getRandomInRange(70, 95),
            unit: 'tons per hectare'
        };
        
        // Generate crop recommendations
        const recommendedCrops = this.soilHealthAlgorithm ? 
            this.soilHealthAlgorithm.recommendSuitableCrops(soilData) :
            ['Maize', 'Groundnuts', 'Sorghum'];
        
        // Generate recommendations
        const recommendations = this.soilHealthAlgorithm ? 
            this.soilHealthAlgorithm.getRecommendations(soilData, this.getCurrentRegion(), this.getCurrentCrop()) :
            [
                {
                    title: 'Improve Soil pH',
                    action: 'Apply agricultural lime',
                    reason: 'Optimize nutrient availability',
                    cost_estimate: 'Medium',
                    timeframe: '2-4 weeks'
                }
            ];
        
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
                farmer_name: 'Demo Farmer',
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
            return this.soilHealthAlgorithm ? 
                this.soilHealthAlgorithm.calculateScore(soilData) :
                Math.random() * 100;
        });
        
        return {
            points: data,
            scores: healthScores
        };
    }
    
    generateAlertsFromSoilData(soilData) {
        // Generate alerts based on soil data
        const alerts = [];
        
        if (!soilData) {
            return alerts;
        }
        
        const now = new Date().toISOString();
        let alertId = 1;
        
        // Check pH level
        if (soilData.ph_level < 5.5) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Critical pH Level',
                message: `Soil pH is ${soilData.ph_level.toFixed(1)}, which is extremely acidic. Urgent lime application recommended.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.ph_level < 6.0) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Low pH Level',
                message: `Soil pH is ${soilData.ph_level.toFixed(1)}, which is moderately acidic. Consider lime application.`,
                priority: 'warning',
                timestamp: now
            });
        } else if (soilData.ph_level > 7.5) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'High pH Level',
                message: `Soil pH is ${soilData.ph_level.toFixed(1)}, which is alkaline. Consider adding organic matter.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check nitrogen level
        if (soilData.nitrogen_level < 15) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Critical Nitrogen Deficiency',
                message: `Nitrogen level is very low at ${soilData.nitrogen_level.toFixed(1)} mg/kg. Crop yield will be severely affected.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.nitrogen_level < 20) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Low Nitrogen Level',
                message: `Nitrogen level is ${soilData.nitrogen_level.toFixed(1)} mg/kg, which is below optimal range.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check phosphorus level
        if (soilData.phosphorus_level < 15) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Low Phosphorus Level',
                message: `Phosphorus level is ${soilData.phosphorus_level.toFixed(1)} mg/kg, which may limit root development and flowering.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check potassium level
        if (soilData.potassium_level < 130) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Low Potassium Level',
                message: `Potassium level is ${soilData.potassium_level.toFixed(1)} mg/kg, which may reduce stress tolerance and water efficiency.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check organic matter
        if (soilData.organic_matter < 2.0) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Critical Organic Matter',
                message: `Organic matter is very low at ${soilData.organic_matter.toFixed(1)}%. Soil structure and nutrient retention will be poor.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.organic_matter < 3.0) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Low Organic Matter',
                message: `Organic matter is ${soilData.organic_matter.toFixed(1)}%, which is below optimal range.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check moisture content during dry season
        const currentMonth = new Date().getMonth() + 1;
        if ([5, 6, 7, 8].includes(currentMonth) && soilData.moisture_content < 15) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Drought Risk',
                message: `Soil moisture is critically low at ${soilData.moisture_content.toFixed(1)}% during dry season. Irrigation recommended.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.moisture_content < 18) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'Low Moisture Content',
                message: `Soil moisture is ${soilData.moisture_content.toFixed(1)}%, which may cause plant stress.`,
                priority: 'warning',
                timestamp: now
            });
        } else if (soilData.moisture_content > 35) {
            alerts.push({
                id: `alert-${alertId++}`,
                title: 'High Moisture Content',
                message: `Soil moisture is high at ${soilData.moisture_content.toFixed(1)}%, which may cause waterlogging and root diseases.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        return alerts;
    }
    
    updateFinancialGauge(financialData) {
        if (!financialData) {
            console.warn('No financial data received');
            return;
        }

        const score = financialData.health_score || 0;
        console.log('Updating gauge with value:', score);

        // Update gauge value safely
        if (this.gauge && this.gauge.updateValue) {
            try {
                this.gauge.updateValue(score);
            } catch (error) {
                console.error('Error updating gauge:', error);
                // Fallback to manual update
                this.updateGaugeDisplay(score);
            }
        } else {
            console.warn('Gauge not properly initialized, using fallback');
            this.updateGaugeDisplay(score);
        }

        // Update related metrics
        const riskElement = document.getElementById('risk-level-indicator');
        const premiumElement = document.getElementById('premium-value');
        const yieldElement = document.getElementById('yield-prediction');

        const riskLevel = financialData.risk_level || (this.soilHealthAlgorithm ? this.soilHealthAlgorithm.determineRiskLevel(score) : 'Medium');
        const premium = financialData.premium_estimate || (this.soilHealthAlgorithm ? this.soilHealthAlgorithm.calculatePremium(score) : 100);
        const yieldPrediction = financialData.yield_prediction || 3.5;

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
        
        const icon = this.getParameterIcon(parameter);
        
        card.innerHTML = `
            <div class="parameter-icon">${icon}</div>
            <h3>${this.formatParameterName(parameter)}</h3>
            <div class="value">${typeof value === 'number' ? value.toFixed(2) : value}</div>
            <div class="unit">${this.getParameterUnit(parameter)}</div>
            <div class="status-indicator"></div>
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
    
    getParameterIcon(parameter) {
        const icons = {
            ph_level: '🧪',
            nitrogen_level: 'N',
            phosphorus_level: 'P',
            potassium_level: 'K',
            organic_matter: '🌱',
            cation_exchange_capacity: '⚡',
            moisture_content: '💧'
        };
        return icons[parameter] || '📊';
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
        
        crops.forEach((crop, index) => {
            const li = document.createElement('li');
            li.className = 'crop-item';
            
            // Add ranking and suitability indicator
            const suitabilityClass = index === 0 ? 'best-match' : index <= 2 ? 'good-match' : 'fair-match';
            
            li.innerHTML = `
                <span class="crop-rank">${index + 1}</span>
                <span class="crop-name ${suitabilityClass}">${crop}</span>
                <span class="crop-suitability">${this.getCropSuitabilityLabel(index)}</span>
            `;
            listElement.appendChild(li);
        });
    }
    
    getCropSuitabilityLabel(index) {
        if (index === 0) return '★ Best Match';
        if (index <= 2) return 'Good Match';
        return 'Fair Match';
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
            const yield_value = baseYield * cropFactor * (0.9 + Math.random() * 0.2);
            
            return {
                crop: crop,
                yield: yield_value.toFixed(2)
            };
        });
        
        // Sort by yield
        yields.sort((a, b) => b.yield - a.yield);
        
        // Create chart
        if (window.Plotly) {
            const data = [{
                x: yields.map(item => item.crop),
                y: yields.map(item => parseFloat(item.yield)),
                type: 'bar',
                marker: {
                    color: yields.map((_, index) => {
                        if (index === 0) return '#27AE60';
                        if (index <= 2) return '#52BE80';
                        return '#A9DFBF';
                    })
                },
                text: yields.map(item => `${item.yield} t/ha`),
                textposition: 'outside'
            }];
            
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
                    family: 'Poppins, sans-serif',
                    size: 11
                },
                hoverlabel: {
                    bgcolor: '#FFF',
                    bordercolor: '#27AE60',
                    font: { color: '#333' }
                }
            };
            
            Plotly.newPlot(yieldChartElement, data, layout, {
                responsive: true,
                displayModeBar: false
            });
        }
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
        
        // Simulate loan history data
        const loanHistory = [
            { date: '2024-06-15', amount: 2500, status: 'Paid', type: 'Seed Finance' },
            { date: '2023-11-20', amount: 5000, status: 'Paid', type: 'Equipment Loan' },
            { date: '2023-03-10', amount: 1500, status: 'Paid', type: 'Seasonal Loan' }
        ];
        
        this.showLoanHistoryModal(loanHistory);
    }
    
    showLoanHistoryModal(loanHistory) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        const historyHTML = loanHistory.map(loan => `
            <tr>
                <td>${loan.date}</td>
                <td>${loan.type}</td>
                <td>${loan.amount.toLocaleString()}</td>
                <td><span class="loan-status ${loan.status.toLowerCase()}">${loan.status}</span></td>
            </tr>
        `).join('');
        
        modal.innerHTML = `
            <div class="modal-content loan-history-modal">
                <div class="modal-header">
                    <h3>Loan History</h3>
                    <button class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <table class="loan-history-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${historyHTML}
                        </tbody>
                    </table>
                    <div class="loan-summary">
                        <p><strong>Total Loans:</strong> ${loanHistory.length}</p>
                        <p><strong>Total Amount:</strong> ${loanHistory.reduce((sum, loan) => sum + loan.amount, 0).toLocaleString()}</p>
                        <p><strong>Repayment Rate:</strong> 100%</p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary">Close</button>
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
                'success': '#2ECC71',
                'warning': '#F39C12',
                'error': '#E74C3C',
                'info': '#3498DB',
                'default': '#3498DB'
            };
            
            Toastify({
                text: message,
                duration: 3000,
                close: true,
                gravity: "top",
                position: "right",
                backgroundColor: bgColors[type],
                stopOnFocus: true
            }).showToast();
        } else {
            alert(message);
        }
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
        // For now, return a default crop
        // In a real implementation, this would come from the farmer's data
        return 'Maize';
    }
}

// Dummy classes for components that may not exist
class SoilHealthAlgorithm {
    determineRiskLevel(score) {
        if (score >= 80) return "Low Risk";
        if (score >= 60) return "Medium-Low Risk";
        if (score >= 40) return "Medium Risk";
        if (score >= 20) return "Medium-High Risk";
        return "High Risk";
    }
    
    calculatePremium(score) {
        return Math.round(100 + (100 - score) * 1.5);
    }
    
    recommendSuitableCrops(soilData) {
        const crops = ["Maize", "Groundnuts", "Sorghum", "Cotton", "Soybeans", "Sweet Potatoes"];
        return crops.slice(0, 3);
    }
    
    getRecommendations(soilData, region, crop) {
        return [
            {
                title: 'Improve Soil pH',
                action: 'Apply agricultural lime',
                reason: 'Optimize nutrient availability',
                cost_estimate: 'Medium',
                timeframe: '2-4 weeks'
            }
        ];
    }
    
    calculateScore(soilData) {
        return Math.random() * 100;
    }
}

class ChartManager {
    initializeCharts() {
        console.log('Chart manager initialized');
    }
    
    updateCharts(data) {
        console.log('Charts updated');
    }
    
    updateChartParameter(param) {
        console.log('Chart parameter updated:', param);
    }
    
    updateTimeWindow(minutes) {
        console.log('Chart time window updated:', minutes);
    }
}

class AlertManager {
    initializeAlerts() {
        console.log('Alert manager initialized');
    }
    
    updateAlerts(data) {
        console.log('Alerts updated');
    }
}

class AIRecommendationsManager {
    initialize() {
        console.log('AI recommendations manager initialized');
    }
    
    generateRecommendations(soilData) {
        console.log('Generating recommendations for:', soilData);
    }
    
    displayRecommendations(data) {
        console.log('Displaying recommendations:', data);
    }
}

// Make the DashboardManager class globally available
if (typeof window !== 'undefined') {
    window.DashboardManager = DashboardManager;
}

// Remove the automatic initialization from this file
// (it will be handled by dashboard-loader.js)
console.log('DashboardManager class loaded successfully!');