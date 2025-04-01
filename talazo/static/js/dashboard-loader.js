// dashboard-loader.js - Initializes the demo dashboard for pitch presentations

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Talazo AgriFinance Dashboard for presentation...');
    
    // Check if all required scripts are loaded
    if (typeof SoilHealthAlgorithm !== 'function') {
        console.error('SoilHealthAlgorithm not loaded! Make sure soil_health_algorithm.js is included.');
        showErrorOverlay('Missing required component: SoilHealthAlgorithm');
        return;
    }
    
    if (typeof DashboardManager !== 'function') {
        console.error('DashboardManager not loaded! Make sure dashboard.js is included.');
        showErrorOverlay('Missing required component: DashboardManager');
        return;
    }
    
    // Check if required libraries are available
    if (typeof GaugeChart === 'undefined') {
        console.error('GaugeChart library not loaded!');
        showErrorOverlay('Missing required library: GaugeChart');
        return;
    }
    
    if (typeof Plotly === 'undefined') {
        console.error('Plotly library not loaded!');
        showErrorOverlay('Missing required library: Plotly');
        return;
    }
    
    // Initialize Dashboard Manager
    try {
        window.dashboardManager = new DashboardManager();
        console.log('Dashboard initialized successfully');
        
        // Show welcome message
        setTimeout(() => {
            showWelcomeMessage();
        }, 500);
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        showErrorOverlay('Error initializing dashboard: ' + error.message);
    }
    
    // Add event listener for demo info modal
    const modal = document.getElementById('demo-info-modal');
    if (modal) {
        const closeButton = modal.querySelector('.modal-close');
        const startDemoButton = modal.querySelector('.start-demo-btn');
        
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        }
        
        if (startDemoButton) {
            startDemoButton.addEventListener('click', () => {
                modal.classList.add('hidden');
                if (window.dashboardManager) {
                    window.dashboardManager.toggleDemoMode();
                }
            });
        }
    }
});

function showWelcomeMessage() {
    // Show the welcome modal for the pitch presentation
    const modal = document.getElementById('demo-info-modal');
    if (modal) {
        modal.classList.remove('hidden');
    } else {
        // If modal element doesn't exist, create a notification
        if (typeof Toastify === 'function') {
            Toastify({
                text: "Welcome to Talazo AgriFinance Platform Demo",
                duration: 5000,
                close: true,
                gravity: "top",
                position: "center",
                backgroundColor: "#3498DB",
                stopOnFocus: true
            }).showToast();
        }
    }
}

function showErrorOverlay(message) {
    // Create error overlay if something fails during initialization
    const overlay = document.createElement('div');
    overlay.className = 'error-overlay';
    overlay.innerHTML = `
        <div class="error-content">
            <h2><i class="fas fa-exclamation-triangle"></i> Initialization Error</h2>
            <p>${message}</p>
            <p>Please check the console for more details.</p>
            <button class="btn btn-primary reload-btn">Reload Page</button>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Add reload button functionality
    const reloadBtn = overlay.querySelector('.reload-btn');
    if (reloadBtn) {
        reloadBtn.addEventListener('click', () => {
            window.location.reload();
        });
    }
}

// Add CSS for error overlay
const errorStyle = document.createElement('style');
errorStyle.textContent = `
.error-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.error-content {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    max-width: 500px;
    text-align: center;
}

.error-content h2 {
    color: #E74C3C;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.error-content p {
    margin-bottom: 1rem;
}

.reload-btn {
    margin-top: 1rem;
}
`;

document.head.appendChild(errorStyle);