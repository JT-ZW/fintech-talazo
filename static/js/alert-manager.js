// alert-manager.js - Specialized alert and recommendation manager for Talazo AgriFinance Dashboard

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
        
        // Initialize containers with empty state messages
        if (this.alertsContainer) {
            this.alertsContainer.innerHTML = '<div class="empty-state">No alerts available. Soil parameters are within normal ranges.</div>';
        }
        
        if (this.recommendationsContainer) {
            this.recommendationsContainer.innerHTML = '<div class="empty-state">No recommendations available. Refresh data to get soil management insights.</div>';
        }
        
        // Add event listener for dismissing alerts
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
        // Sort alerts by priority and timestamp
        this.alerts = alerts.sort((a, b) => {
            // Sort by priority (critical first, then warning, then info)
            const priorityOrder = { 'critical': 0, 'warning': 1, 'info': 2 };
            const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
            if (priorityDiff !== 0) return priorityDiff;
            
            // If same priority, sort by timestamp (newest first)
            const aTime = new Date(a.timestamp).getTime();
            const bTime = new Date(b.timestamp).getTime();
            return bTime - aTime;
        });
        
        // Keep only the most recent alerts up to maxAlerts
        if (this.alerts.length > this.maxAlerts) {
            this.alerts = this.alerts.slice(0, this.maxAlerts);
        }
    }
    
    setRecommendations(recommendations) {
        // Only keep top 5 recommendations
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
            
            // Format timestamp
            const timestamp = new Date(alert.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            // Build alert content
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
            
            // Determine recommendation priority based on cost or index
            let priority = 'medium';
            if (recommendation.cost_estimate) {
                if (recommendation.cost_estimate.toLowerCase().includes('low')) {
                    priority = 'low';
                } else if (recommendation.cost_estimate.toLowerCase().includes('high')) {
                    priority = 'high';
                }
            } else {
                // Alternate priorities if no cost estimate
                priority = ['high', 'medium', 'low'][index % 3];
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
            
            // Build recommendation HTML
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
    
    generateAlertFromSoilData(soilData) {
        if (!soilData) return [];
        
        const alerts = [];
        const now = new Date().toISOString();
        
        // Check pH level
        if (soilData.ph_level < 5.5) {
            alerts.push({
                id: 'alert-ph-low-' + Date.now(),
                title: 'Critical pH Level',
                message: `Soil pH is ${soilData.ph_level.toFixed(2)}, which is extremely acidic. Urgent lime application is recommended.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.ph_level < 6.0) {
            alerts.push({
                id: 'alert-ph-warning-' + Date.now(),
                title: 'Low pH Level',
                message: `Soil pH is ${soilData.ph_level.toFixed(2)}, which is moderately acidic. Consider lime application.`,
                priority: 'warning',
                timestamp: now
            });
        } else if (soilData.ph_level > 7.5) {
            alerts.push({
                id: 'alert-ph-high-' + Date.now(),
                title: 'High pH Level',
                message: `Soil pH is ${soilData.ph_level.toFixed(2)}, which is alkaline. Consider adding organic matter.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check nitrogen level
        if (soilData.nitrogen_level < 15) {
            alerts.push({
                id: 'alert-nitrogen-low-' + Date.now(),
                title: 'Critical Nitrogen Deficiency',
                message: `Nitrogen level is very low at ${soilData.nitrogen_level.toFixed(2)} mg/kg. Crop yield will be severely affected.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.nitrogen_level < 20) {
            alerts.push({
                id: 'alert-nitrogen-warning-' + Date.now(),
                title: 'Low Nitrogen Level',
                message: `Nitrogen level is ${soilData.nitrogen_level.toFixed(2)} mg/kg, which is below the optimal range.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check organic matter
        if (soilData.organic_matter < 2.0) {
            alerts.push({
                id: 'alert-organic-low-' + Date.now(),
                title: 'Critical Organic Matter',
                message: `Organic matter is very low at ${soilData.organic_matter.toFixed(2)}%. This will negatively impact soil structure and nutrient retention.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.organic_matter < 3.0) {
            alerts.push({
                id: 'alert-organic-warning-' + Date.now(),
                title: 'Low Organic Matter',
                message: `Organic matter is ${soilData.organic_matter.toFixed(2)}%, which is below the optimal range. Consider adding compost or manure.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        // Check moisture content with seasonal context
        const currentMonth = new Date().getMonth() + 1;
        if ([5, 6, 7, 8].includes(currentMonth) && soilData.moisture_content < 15) {
            alerts.push({
                id: 'alert-moisture-low-' + Date.now(),
                title: 'Drought Risk',
                message: `Soil moisture is critically low at ${soilData.moisture_content.toFixed(2)}% during Zimbabwe's dry season. Implement water conservation measures.`,
                priority: 'critical',
                timestamp: now
            });
        } else if (soilData.moisture_content < 18) {
            alerts.push({
                id: 'alert-moisture-warning-' + Date.now(),
                title: 'Low Moisture Content',
                message: `Soil moisture is ${soilData.moisture_content.toFixed(2)}%, which may cause plant stress. Consider irrigation or mulching.`,
                priority: 'warning',
                timestamp: now
            });
        } else if ([11, 12, 1, 2, 3].includes(currentMonth) && soilData.moisture_content > 35) {
            alerts.push({
                id: 'alert-moisture-high-' + Date.now(),
                title: 'High Moisture Content',
                message: `Soil moisture is high at ${soilData.moisture_content.toFixed(2)}% during the rainy season. Consider improving drainage to prevent waterlogging.`,
                priority: 'warning',
                timestamp: now
            });
        }
        
        return alerts;
    }
}