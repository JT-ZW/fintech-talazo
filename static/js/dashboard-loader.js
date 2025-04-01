// dashboard-loader.js - Bootstrap script for Talazo AgriFinance Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Talazo AgriFinance Dashboard...');
    
    // Initialize dashboard manager (main controller)
    window.dashboardManager = new DashboardManager();
    
    // Set up demo data refresh timer if in demo mode
    setupDemoMode();
    
    // Set up event handlers for interactive elements
    setupEventHandlers();
    
    // Set starting values for last update time
    updateLastUpdateTime();
    
    // Hide loading overlay
    hideLoadingOverlay();
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
                
                document.getElementById('alerts-container').classList.toggle('hidden', tabName !== 'alerts');
                document.getElementById('recommendations-container').classList.toggle('hidden', tabName !== 'recommendations');
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