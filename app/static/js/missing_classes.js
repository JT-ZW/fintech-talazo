// missing_classes.js - Error-free supporting classes for Talazo Dashboard

// =============================================================================
// SOIL HEALTH ALGORITHM CLASS
// =============================================================================
class SoilHealthAlgorithm {
    constructor() {
        this.optimalRanges = {
            ph_level: { min: 6.0, max: 7.0 },
            nitrogen_level: { min: 20, max: 40 },
            phosphorus_level: { min: 20, max: 30 },
            potassium_level: { min: 150, max: 250 },
            organic_matter: { min: 3, max: 5 },
            cation_exchange_capacity: { min: 10, max: 20 },
            moisture_content: { min: 20, max: 30 }
        };
        
        this.weights = {
            ph_level: 0.20,
            nitrogen_level: 0.18,
            phosphorus_level: 0.15,
            potassium_level: 0.15,
            organic_matter: 0.17,
            cation_exchange_capacity: 0.08,
            moisture_content: 0.07
        };
    }
    
    calculateScore(soilData) {
        if (!soilData || Object.keys(soilData).length === 0) {
            return 50;
        }
        
        let totalScore = 0;
        let totalWeight = 0;
        
        for (const [param, value] of Object.entries(soilData)) {
            if (param === 'timestamp' || param === 'sample_id') continue;
            
            const range = this.optimalRanges[param];
            const weight = this.weights[param];
            
            if (range && weight && typeof value === 'number') {
                const paramScore = this.calculateParameterScore(param, value);
                totalScore += paramScore * weight;
                totalWeight += weight;
            }
        }
        
        const finalScore = totalWeight > 0 ? (totalScore / totalWeight) * 100 : 50;
        return Math.max(0, Math.min(100, finalScore));
    }
    
    calculateParameterScore(parameter, value) {
        const range = this.optimalRanges[parameter];
        if (!range) return 0.5;
        
        const { min, max } = range;
        
        if (value >= min && value <= max) {
            return 1.0;
        } else if (value < min) {
            const deviation = (min - value) / min;
            return Math.max(0, 1 - deviation);
        } else {
            const deviation = (value - max) / max;
            const tolerance = this.getHighValueTolerance(parameter);
            return Math.max(0, 1 - (deviation / tolerance));
        }
    }
    
    getHighValueTolerance(parameter) {
        const tolerances = {
            ph_level: 1.5,
            nitrogen_level: 2.0,
            phosphorus_level: 2.0,
            potassium_level: 1.5,
            organic_matter: 3.0,
            cation_exchange_capacity: 2.0,
            moisture_content: 1.3
        };
        
        return tolerances[parameter] || 1.5;
    }
    
    determineRiskLevel(score) {
        if (score >= 80) return "Low Risk";
        if (score >= 65) return "Medium-Low Risk";
        if (score >= 50) return "Medium Risk";
        if (score >= 35) return "Medium-High Risk";
        return "High Risk";
    }
    
    calculatePremium(score) {
        const basePremium = 100;
        const riskMultiplier = Math.max(0.5, (100 - score) / 50);
        return Math.round(basePremium * riskMultiplier);
    }
    
    recommendSuitableCrops(soilData) {
        const allCrops = [
            { name: "Maize", suitability: this.calculateCropSuitability(soilData, "maize") },
            { name: "Groundnuts", suitability: this.calculateCropSuitability(soilData, "groundnuts") },
            { name: "Sorghum", suitability: this.calculateCropSuitability(soilData, "sorghum") },
            { name: "Cotton", suitability: this.calculateCropSuitability(soilData, "cotton") },
            { name: "Soybeans", suitability: this.calculateCropSuitability(soilData, "soybeans") },
            { name: "Sweet Potatoes", suitability: this.calculateCropSuitability(soilData, "sweet_potatoes") }
        ];
        
        return allCrops
            .sort((a, b) => b.suitability - a.suitability)
            .slice(0, 3)
            .map(crop => crop.name);
    }
    
    calculateCropSuitability(soilData, cropType) {
        let score = 100;
        
        if (!soilData) return score;
        
        const ph = soilData.ph_level || 6.5;
        const nitrogen = soilData.nitrogen_level || 30;
        const organic_matter = soilData.organic_matter || 3;
        
        switch(cropType) {
            case "maize":
                if (ph < 5.5 || ph > 7.5) score -= 20;
                if (nitrogen < 25) score -= 15;
                break;
            case "groundnuts":
                if (ph < 5.0 || ph > 7.0) score -= 15;
                if (nitrogen > 40) score -= 10;
                break;
            case "sorghum":
                if (ph < 5.5 || ph > 8.0) score -= 10;
                if (organic_matter < 2) score -= 15;
                break;
            default:
                if (ph < 6.0 || ph > 7.5) score -= 15;
                if (nitrogen < 20) score -= 10;
        }
        
        return Math.max(score, 20);
    }
    
    getRecommendations(soilData, region, crop) {
        const recommendations = [];
        
        if (!soilData) return recommendations;
        
        // pH recommendations
        if (soilData.ph_level < 6.0) {
            recommendations.push({
                title: 'Improve Soil pH',
                action: `Apply agricultural lime at 2-3 tons per hectare`,
                reason: `Current pH is ${soilData.ph_level.toFixed(1)}, which is acidic`,
                cost_estimate: 'Medium ($150-200 per hectare)',
                timeframe: '2-4 months',
                local_context: 'Lime is available from agricultural suppliers in most regions'
            });
        }
        
        // Nitrogen recommendations
        if (soilData.nitrogen_level < 20) {
            recommendations.push({
                title: 'Increase Nitrogen Levels',
                action: `Apply nitrogen fertilizer at ${Math.round(30 - soilData.nitrogen_level)} kg/ha`,
                reason: 'Soil nitrogen is below optimal range for good crop yields',
                cost_estimate: 'Medium ($100-150 per hectare)',
                timeframe: '2-4 weeks',
                local_context: 'Split application recommended during the growing season'
            });
        }
        
        // Organic matter recommendations
        if (soilData.organic_matter < 3) {
            recommendations.push({
                title: 'Increase Organic Matter',
                action: 'Apply compost or manure at 5-10 tons per hectare',
                reason: 'Low organic matter reduces nutrient retention and soil structure',
                cost_estimate: 'Low ($50-100 per hectare)',
                timeframe: '6-12 months',
                local_context: 'Use locally available resources like cattle manure'
            });
        }
        
        return recommendations.slice(0, 5);
    }
}

// =============================================================================
// CHART MANAGER CLASS
// =============================================================================
class ChartManager {
    constructor() {
        this.charts = {};
        this.currentParameter = 'ph_level';
        this.timeWindow = 24;
        this.isInitialized = false;
    }
    
    initializeCharts() {
        console.log('Initializing Chart Manager...');
        this.initializeTrendChart();
        this.initializeParameterChart();
        this.isInitialized = true;
    }
    
    initializeTrendChart() {
        const trendChartElement = document.getElementById('trend-chart');
        if (!trendChartElement) {
            console.warn('Trend chart element not found');
            return;
        }
        
        if (window.Plotly) {
            const data = [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Soil Health Score',
                line: { color: '#2ECC71' }
            }];
            
            const layout = {
                title: 'Soil Health Trend',
                xaxis: { title: 'Time' },
                yaxis: { title: 'Health Score', range: [0, 100] },
                margin: { t: 50, l: 50, r: 50, b: 50 }
            };
            
            Plotly.newPlot(trendChartElement, data, layout, { responsive: true });
            this.charts.trend = true;
        }
    }
    
    initializeParameterChart() {
        const paramChartElement = document.getElementById('parameter-chart');
        if (!paramChartElement) {
            console.warn('Parameter chart element not found');
            return;
        }
        
        if (window.Plotly) {
            const data = [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines',
                name: 'pH Level',
                line: { color: '#3498DB' }
            }];
            
            const layout = {
                title: 'Parameter Trend',
                xaxis: { title: 'Time' },
                yaxis: { title: 'Value' },
                margin: { t: 50, l: 50, r: 50, b: 50 }
            };
            
            Plotly.newPlot(paramChartElement, data, layout, { responsive: true });
            this.charts.parameter = true;
        }
    }
    
    updateCharts(trendData) {
        if (!this.isInitialized || !trendData) {
            console.warn('Charts not initialized or no data provided');
            return;
        }
        
        this.updateTrendChart(trendData);
        this.updateParameterChart(trendData);
    }
    
    updateTrendChart(trendData) {
        const trendChartElement = document.getElementById('trend-chart');
        if (!trendChartElement || !window.Plotly) return;
        
        const scores = trendData.scores || [];
        const points = trendData.points || [];
        
        if (scores.length === 0) return;
        
        const timestamps = points.map(point => new Date(point.timestamp));
        
        const data = [{
            x: timestamps,
            y: scores,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Soil Health Score',
            line: { color: '#2ECC71', width: 2 },
            marker: { size: 4 }
        }];
        
        const layout = {
            title: 'Soil Health Score Trend (Last 24 Hours)',
            xaxis: { 
                title: 'Time',
                type: 'date'
            },
            yaxis: { 
                title: 'Health Score', 
                range: [0, 100] 
            },
            margin: { t: 50, l: 50, r: 50, b: 80 },
            font: { family: 'Arial, sans-serif', size: 12 }
        };
        
        Plotly.react(trendChartElement, data, layout, { responsive: true });
    }
    
    updateParameterChart(trendData) {
        const paramChartElement = document.getElementById('parameter-chart');
        if (!paramChartElement || !window.Plotly) return;
        
        const points = trendData.points || [];
        if (points.length === 0) return;
        
        const timestamps = points.map(point => new Date(point.timestamp));
        const values = points.map(point => point[this.currentParameter] || 0);
        
        const data = [{
            x: timestamps,
            y: values,
            type: 'scatter',
            mode: 'lines',
            name: this.formatParameterName(this.currentParameter),
            line: { color: '#3498DB', width: 2 }
        }];
        
        const layout = {
            title: `${this.formatParameterName(this.currentParameter)} Trend`,
            xaxis: { 
                title: 'Time',
                type: 'date'
            },
            yaxis: { 
                title: this.getParameterUnit(this.currentParameter)
            },
            margin: { t: 50, l: 50, r: 50, b: 80 },
            font: { family: 'Arial, sans-serif', size: 12 }
        };
        
        Plotly.react(paramChartElement, data, layout, { responsive: true });
    }
    
    updateChartParameter(parameter) {
        this.currentParameter = parameter;
        console.log('Chart parameter updated to:', parameter);
    }
    
    updateTimeWindow(minutes) {
        this.timeWindow = minutes / 60;
        console.log('Chart time window updated to:', this.timeWindow, 'hours');
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
}

// =============================================================================
// ALERT MANAGER CLASS
// =============================================================================
class AlertManager {
    constructor() {
        this.alerts = [];
        this.recommendations = [];
        this.maxAlerts = 5;
        this.alertsContainer = document.getElementById('alerts-container');
        this.recommendationsContainer = document.getElementById('recommendations-container');
        this.initialize();
    }
    
    initialize() {
        console.log('Initializing Alert Manager');
        this.initializeAlerts();
    }
    
    initializeAlerts() {
        if (this.alertsContainer) {
            this.alertsContainer.innerHTML = '<div class="empty-state">No alerts available. Soil parameters are within normal ranges.</div>';
        }
        
        if (this.recommendationsContainer) {
            this.recommendationsContainer.innerHTML = '<div class="empty-state">No recommendations available. Refresh data to get soil management insights.</div>';
        }
        
        document.addEventListener('click', (event) => {
            const dismissButton = event.target.closest('.dismiss-alert');
            if (dismissButton) {
                const alertElement = dismissButton.closest('.alert-item');
                if (alertElement) {
                    const alertId = alertElement.getAttribute('data-id');
                    this.dismissAlert(alertId);
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
            const priorityOrder = { 'critical': 0, 'warning': 1, 'info': 2 };
            const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
            if (priorityDiff !== 0) return priorityDiff;
            
            const aTime = new Date(a.timestamp).getTime();
            const bTime = new Date(b.timestamp).getTime();
            return bTime - aTime;
        });
        
        if (this.alerts.length > this.maxAlerts) {
            this.alerts = this.alerts.slice(0, this.maxAlerts);
        }
    }
    
    setRecommendations(recommendations) {
        this.recommendations = recommendations.slice(0, 5);
    }
    
    renderAlerts() {
        if (!this.alertsContainer) return;
        
        if (this.alerts.length === 0) {
            this.alertsContainer.innerHTML = '<div class="empty-state">No alerts available. Soil parameters are within normal ranges.</div>';
            return;
        }
        
        this.alertsContainer.innerHTML = '';
        
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
            
            this.alertsContainer.appendChild(alertElement);
        });
    }
    
    renderRecommendations() {
        if (!this.recommendationsContainer) return;
        
        if (this.recommendations.length === 0) {
            this.recommendationsContainer.innerHTML = '<div class="empty-state">No recommendations available. Refresh data to get soil management insights.</div>';
            return;
        }
        
        this.recommendationsContainer.innerHTML = '';
        
        this.recommendations.forEach((recommendation, index) => {
            const recElement = document.createElement('div');
            recElement.className = 'recommendation-item';
            
            let priority = 'medium';
            if (recommendation.cost_estimate) {
                if (recommendation.cost_estimate.toLowerCase().includes('low')) {
                    priority = 'low';
                } else if (recommendation.cost_estimate.toLowerCase().includes('high')) {
                    priority = 'high';
                }
            } else {
                priority = ['high', 'medium', 'low'][index % 3];
            }
            
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
            
            this.recommendationsContainer.appendChild(recElement);
        });
    }
    
    dismissAlert(alertId) {
        this.alerts = this.alerts.filter(alert => alert.id !== alertId);
        this.renderAlerts();
    }
}

// =============================================================================
// AI RECOMMENDATIONS MANAGER CLASS
// =============================================================================
class AIRecommendationsManager {
    constructor() {
        this.recommendations = [];
        this.isInitialized = false;
    }
    
    initialize() {
        console.log('AI Recommendations Manager initialized');
        this.isInitialized = true;
    }
    
    generateRecommendations(soilData) {
        console.log('Generating recommendations for:', soilData);
        
        const recommendations = [];
        
        if (!soilData) {
            console.warn('No soil data provided for recommendations');
            return;
        }
        
        if (soilData.ph_level && soilData.ph_level < 6.0) {
            recommendations.push({
                title: 'Improve Soil pH',
                action: 'Apply agricultural lime',
                reason: 'Low pH limits nutrient availability',
                cost_estimate: 'Medium',
                timeframe: '2-4 months'
            });
        }
        
        if (soilData.nitrogen_level && soilData.nitrogen_level < 20) {
            recommendations.push({
                title: 'Increase Nitrogen',
                action: 'Apply nitrogen fertilizer',
                reason: 'Low nitrogen affects plant growth',
                cost_estimate: 'Medium',
                timeframe: '2-4 weeks'
            });
        }
        
        if (soilData.organic_matter && soilData.organic_matter < 3) {
            recommendations.push({
                title: 'Add Organic Matter',
                action: 'Apply compost or manure',
                reason: 'Improves soil structure and water retention',
                cost_estimate: 'Low',
                timeframe: '6-12 months'
            });
        }
        
        this.recommendations = recommendations;
        this.displayRecommendations({
            status: 'success',
            recommendations: recommendations,
            metadata: {
                source: 'system',
                timestamp: new Date().toISOString()
            }
        });
    }
    
    displayRecommendations(data) {
        console.log('Displaying recommendations:', data);
        
        if (data.recommendations && data.recommendations.length > 0) {
            console.log(`Generated ${data.recommendations.length} recommendations`);
        }
    }
}

// =============================================================================
// MAKE CLASSES GLOBALLY AVAILABLE
// =============================================================================
if (typeof window !== 'undefined') {
    window.SoilHealthAlgorithm = SoilHealthAlgorithm;
    window.ChartManager = ChartManager;
    window.AlertManager = AlertManager;
    window.AIRecommendationsManager = AIRecommendationsManager;
}

// =============================================================================
// AUTO-INITIALIZATION
// =============================================================================
console.log('Missing classes loaded successfully!');