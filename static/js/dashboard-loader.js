// dashboard-loader.js - Bootstrap script for Talazo AgriFinance Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Talazo AgriFinance Dashboard...');
    
    // Function to check if all required classes are loaded
    function checkDependencies() {
        const requiredClasses = ['DashboardManager', 'SoilHealthAlgorithm', 'ChartManager', 'AlertManager', 'AIRecommendationsManager'];
        const missing = [];
        
        for (const className of requiredClasses) {
            if (typeof window[className] === 'undefined') {
                missing.push(className);
            }
        }
        
        return missing;
    }
    
    // Function to initialize the dashboard
    function initializeDashboard() {
        const missing = checkDependencies();
        
        if (missing.length > 0) {
            console.warn('Missing classes:', missing);
            console.log('Retrying in 100ms...');
            setTimeout(initializeDashboard, 100);
            return;
        }
        
        try {
            console.log('All dependencies loaded. Initializing dashboard...');
            
            // Initialize dashboard manager (main controller)
            window.dashboardManager = new DashboardManager();
            
            // Set up demo mode functionality
            setupDemoMode();
            
            // Set up event handlers for interactive elements
            setupEventHandlers();
            
            // Set starting values for last update time
            updateLastUpdateTime();
            
            // Hide loading overlay
            hideLoadingOverlay();
            
            console.log('Dashboard initialized successfully!');
            
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            
            // Show error message to user
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #f44336; color: white; padding: 1rem; border-radius: 4px; z-index: 10000;';
            errorDiv.textContent = 'Dashboard initialization failed. Please refresh the page.';
            document.body.appendChild(errorDiv);
            
            // Auto-remove error after 5 seconds
            setTimeout(() => errorDiv.remove(), 5000);
        }
    }
    
    // Start initialization
    initializeDashboard();
    
    const dashboardManager = new DashboardManager();

    fetch('/api/demo-data')
        .then(response => response.json())
        .then(data => {
            dashboardManager.updateDashboard(data);
        })
        .catch(error => {
            console.error('Failed to fetch demo data:', error);
        });
});

// Setup demo mode functionality
function setupDemoMode() {
    const urlParams = new URLSearchParams(window.location.search);
    const demoMode = urlParams.get('demo') === 'true';
    
    if (demoMode) {
        console.log('Demo mode enabled - will simulate real-time data updates');
        
        // Add demo mode indicator
        const header = document.querySelector('.page-title');
        if (header) {
            const demoIndicator = document.createElement('div');
            demoIndicator.className = 'demo-mode-indicator';
            demoIndicator.innerHTML = '<i class="fas fa-flask"></i> Demo Mode';
            header.appendChild(demoIndicator);
        }
        
        // Set up automatic refresh every 30 seconds
        setInterval(function() {
            if (window.dashboardManager) {
                window.dashboardManager.refreshData();
            }
        }, 30000);
        
        // Generate initial data refresh
        setTimeout(function() {
            if (window.dashboardManager) {
                window.dashboardManager.refreshData();
            }
        }, 1000);
    }
}

// Set up additional event handlers not covered by the dashboard manager
function setupEventHandlers() {
    // Handle refresh button click
    const refreshButton = document.getElementById('refresh-data');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            showLoadingOverlay();
            
            setTimeout(function() {
                if (window.dashboardManager) {
                    window.dashboardManager.refreshData();
                }
                hideLoadingOverlay();
                updateLastUpdateTime();
            }, 1000);
        });
    }
    
    // Set up alerts tab switching
    const alertsTabs = document.querySelectorAll('.alerts-tabs .tab-button');
    if (alertsTabs.length) {
        alertsTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Deactivate all tabs
                alertsTabs.forEach(t => t.classList.remove('active'));
                
                // Activate this tab
                this.classList.add('active');
                
                // Show corresponding content
                const tabName = this.getAttribute('data-tab');
                
                const alertsContainer = document.getElementById('alerts-container');
                const recommendationsContainer = document.getElementById('recommendations-container');
                
                if (alertsContainer) {
                    alertsContainer.classList.toggle('hidden', tabName !== 'alerts');
                }
                if (recommendationsContainer) {
                    recommendationsContainer.classList.toggle('hidden', tabName !== 'recommendations');
                }
            });
        });
    }
    
    // Set up parameter view toggles
    const viewToggles = document.querySelectorAll('.toggle-view');
    if (viewToggles.length) {
        viewToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                // Deactivate all toggles
                viewToggles.forEach(t => t.classList.remove('active'));
                
                // Activate this toggle
                this.classList.add('active');
                
                // Update the parameters grid view
                const viewType = this.getAttribute('data-view');
                const paramsGrid = document.getElementById('parameters-grid');
                
                if (paramsGrid) {
                    paramsGrid.classList.toggle('list-view', viewType === 'list');
                }
            });
        });
    }
}

// Update the last update time display
function updateLastUpdateTime() {
    const lastUpdateSpan = document.getElementById('last-update-time');
    if (lastUpdateSpan) {
        const now = new Date();
        const formattedTime = now.toLocaleTimeString([], { 
            hour: '2-digit',
            minute: '2-digit', 
            second: '2-digit' 
        });
        lastUpdateSpan.textContent = formattedTime;
    }
}

// Show loading overlay
function showLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('hidden');
    }
}

// Hide loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// Show notification
function showNotification(message, type = 'default') {
    // Check if Toastify is available
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
        // Fallback to standard alert if Toastify is not available
        alert(message);
    }
}