class AlertManager {
    constructor() {
        this.alerts = [];
        this.recommendations = [];
        this.init();
    }

    init() {
        this.setupTabSystem();
        this.setupEventListeners();
    }

    setupTabSystem() {
        const tabButtons = document.querySelectorAll('.alerts-tabs .tab-button');
        const containers = {
            alerts: document.getElementById('alerts-container'),
            recommendations: document.getElementById('recommendations-container')
        };

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.dataset.tab;
                
                // Update active tab button
                tabButtons.forEach(btn => btn.classList.toggle('active', btn === button));
                
                // Show selected container
                Object.entries(containers).forEach(([key, container]) => {
                    container.classList.toggle('hidden', key !== tab);
                });
            });
        });
    }

    setupEventListeners() {
        // Add event listeners for alert interactions
        document.getElementById('alerts-container').addEventListener('click', (e) => {
            if (e.target.classList.contains('dismiss-alert')) {
                this.dismissAlert(e.target.dataset.alertId);
            }
        });
    }

    updateAlerts(data) {
        this.alerts = data.alerts || [];
        this.recommendations = data.recommendations || [];
        
        this.renderAlerts();
        this.renderRecommendations();
        this.updateAlertCount();
    }

    renderAlerts() {
        const container = document.getElementById('alerts-container');
        container.innerHTML = this.alerts.length ? '' : '<p>No active alerts</p>';

        this.alerts.forEach(alert => {
            container.appendChild(this.createAlertElement(alert));
        });
    }

    renderRecommendations() {
        const container = document.getElementById('recommendations-container');
        container.innerHTML = this.recommendations.length ? '' : '<p>No recommendations available</p>';

        this.recommendations.forEach(rec => {
            container.appendChild(this.createRecommendationElement(rec));
        });
    }

    createAlertElement(alert) {
        const div = document.createElement('div');
        div.className = `alert-item ${alert.priority}`;
        div.innerHTML = `
            <div class="alert-header">
                <span class="alert-title">${alert.title}</span>
                <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="alert-message">${alert.message}</div>
            <button class="dismiss-alert" data-alert-id="${alert.id}">Dismiss</button>
        `;
        return div;
    }

    createRecommendationElement(recommendation) {
        const div = document.createElement('div');
        div.className = 'recommendation-item';
        div.innerHTML = `
            <div class="recommendation-header">
                <span class="recommendation-title">${recommendation.title}</span>
                <span class="recommendation-priority ${recommendation.priority}">
                    ${recommendation.priority}
                </span>
            </div>
            <div class="recommendation-details">
                <p>${recommendation.description}</p>
                <div class="recommendation-meta">
                    <span>Expected Impact: ${recommendation.impact}</span>
                    <span>Estimated Cost: $${recommendation.cost}</span>
                </div>
            </div>
            <button class="action-button">Take Action</button>
        `;
        return div;
    }

    dismissAlert(alertId) {
        // Remove alert from UI
        const alertElement = document.querySelector(`[data-alert-id="${alertId}"]`).parentNode;
        alertElement.remove();
        
        // Remove from alerts array
        this.alerts = this.alerts.filter(alert => alert.id !== alertId);
        
        // Update alert count
        this.updateAlertCount();
        
        // Send dismissal to server
        fetch(`/api/alerts/${alertId}/dismiss`, { method: 'POST' })
            .catch(error => console.error('Error dismissing alert:', error));
    }

    updateAlertCount() {
        const count = this.alerts.length;
        const criticalCount = this.alerts.filter(a => a.priority === 'critical').length;
        
        // Update UI elements showing alert counts
        document.querySelector('.alerts-tabs [data-tab="alerts"]')
            .setAttribute('data-count', count);
            
        if (criticalCount > 0) {
            this.showNotification(`${criticalCount} critical alerts require attention`);
        }
    }

    showNotification(message) {
        Toastify({
            text: message,
            duration: 5000,
            close: true,
            gravity: "top",
            position: "right",
            backgroundColor: "#ff4444"
        }).showToast();
    }
}

// Initialize alert manager
window.alertManager = new AlertManager();