// static/js/loan_assessment.js
class LoanAssessmentManager {
    constructor() {
        this.loanStatus = 'ineligible'; // ineligible, conditional, eligible
        this.financialScore = 0;
        this.maxLoanAmount = 0;
        this.interestRate = 0;
        this.loanTerm = 0;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Loan Assessment Manager...');
        
        // Initialize UI elements
        this.loanStatusIndicator = document.getElementById('loan-status-indicator');
        this.maxLoanElement = document.getElementById('max-loan-amount');
        this.interestRateElement = document.getElementById('interest-rate');
        this.loanTermElement = document.getElementById('loan-term');
        this.processLoanBtn = document.getElementById('process-loan-btn');
        this.viewHistoryBtn = document.getElementById('view-history-btn');
        
        // Set up event listeners
        if (this.processLoanBtn) {
            this.processLoanBtn.addEventListener('click', () => this.processLoan());
        }
        
        if (this.viewHistoryBtn) {
            this.viewHistoryBtn.addEventListener('click', () => this.viewLoanHistory());
        }
    }
    
    updateLoanAssessment(financialScore) {
        this.financialScore = financialScore;
        
        // Calculate loan parameters based on financial score
        if (financialScore >= 70) {
            this.loanStatus = 'eligible';
            this.maxLoanAmount = financialScore * 50; // Higher multiplier for good scores
            this.interestRate = 5.75;
            this.loanTerm = 36;
        } else if (financialScore >= 40) {
            this.loanStatus = 'conditional';
            this.maxLoanAmount = financialScore * 30;
            this.interestRate = 8.25;
            this.loanTerm = 24;
        } else {
            this.loanStatus = 'ineligible';
            this.maxLoanAmount = 0;
            this.interestRate = 0;
            this.loanTerm = 0;
        }
        
        // Update UI
        this.updateUI();
    }
    
    updateUI() {
        // Update loan status indicator
        if (this.loanStatusIndicator) {
            this.loanStatusIndicator.className = `status-indicator ${this.loanStatus}`;
            this.loanStatusIndicator.innerHTML = `
                <div class="status-text">${this.getStatusText()}</div>
                <div class="score">${Math.round(this.financialScore)}</div>
            `;
        }
        
        // Update loan details
        if (this.maxLoanElement) {
            this.maxLoanElement.textContent = this.maxLoanAmount.toFixed(2);
        }
        
        if (this.interestRateElement) {
            this.interestRateElement.textContent = this.loanStatus === 'ineligible' ? 'N/A' : this.interestRate.toFixed(2);
        }
        
        if (this.loanTermElement) {
            this.loanTermElement.textContent = this.loanStatus === 'ineligible' ? 'N/A' : this.loanTerm;
        }
        
        // Update button states
        if (this.processLoanBtn) {
            this.processLoanBtn.disabled = this.loanStatus === 'ineligible';
        }
    }
    
    getStatusText() {
        switch (this.loanStatus) {
            case 'eligible':
                return 'Eligible';
            case 'conditional':
                return 'Conditional';
            case 'ineligible':
                return 'Ineligible';
            default:
                return 'Unknown';
        }
    }
    
    processLoan() {
        if (this.loanStatus === 'ineligible') {
            this.showNotification('Cannot process loan: Farmer is ineligible based on soil health index', 'error');
            return;
        }
        
        // Show loading state
        if (window.dashboardManager) {
            window.dashboardManager.showLoading();
        }
        
        // Simulate API call with timeout
        setTimeout(() => {
            // Hide loading
            if (window.dashboardManager) {
                window.dashboardManager.hideLoading();
            }
            
            // Show different messages based on loan status
            if (this.loanStatus === 'eligible') {
                this.showModal({
                    title: 'Loan Pre-Approved',
                    message: `The farmer has been pre-approved for a loan of $${this.maxLoanAmount.toFixed(2)} at ${this.interestRate}% interest for ${this.loanTerm} months.`,
                    type: 'success',
                    actions: [
                        { label: 'View Details', primary: true, action: 'viewDetails' },
                        { label: 'Process Later', primary: false, action: 'close' }
                    ]
                });
            } else { // conditional
                this.showModal({
                    title: 'Conditional Approval',
                    message: `The farmer meets minimum requirements for a loan of $${this.maxLoanAmount.toFixed(2)}. Additional documentation and collateral may be required.`,
                    type: 'warning',
                    actions: [
                        { label: 'Begin Process', primary: true, action: 'beginProcess' },
                        { label: 'Not Now', primary: false, action: 'close' }
                    ]
                });
            }
        }, 1500);
    }
    
    viewLoanHistory() {
        // Show loading state
        if (window.dashboardManager) {
            window.dashboardManager.showLoading();
        }
        
        // Simulate API call with timeout
        setTimeout(() => {
            // Hide loading
            if (window.dashboardManager) {
                window.dashboardManager.hideLoading();
            }
            
            // For the prototype, just show a notification
            this.showNotification('Loan history will be available in the next update', 'default');
        }, 800);
    }
    
    showModal(options) {
        // Create modal element
        const modal = document.createElement('div');
        modal.className = 'loan-modal';
        
        // Set icon based on type
        let icon;
        switch (options.type) {
            case 'success':
                icon = '<i class="fas fa-check-circle success-icon"></i>';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-triangle warning-icon"></i>';
                break;
            case 'error':
                icon = '<i class="fas fa-times-circle error-icon"></i>';
                break;
            default:
                icon = '<i class="fas fa-info-circle info-icon"></i>';
        }
        
        // Create modal content
        modal.innerHTML = `
            <div class="loan-modal-content ${options.type}">
                <div class="loan-modal-header">
                    ${icon}
                    <h3>${options.title}</h3>
                    <button class="close-modal"><i class="fas fa-times"></i></button>
                </div>
                <div class="loan-modal-body">
                    <p>${options.message}</p>
                </div>
                <div class="loan-modal-footer">
                    ${options.actions.map(action => `
                        <button class="btn ${action.primary ? 'btn-primary' : 'btn-secondary'}" data-action="${action.action}">
                            ${action.label}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Add modal to body
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
        });
        
        // Add action button event listeners
        modal.querySelectorAll('.loan-modal-footer button').forEach(button => {
            button.addEventListener('click', () => {
                const action = button.dataset.action;
                modal.remove();
                
                // Handle different actions
                switch (action) {
                    case 'viewDetails':
                        this.showNotification('Loan details view will be implemented in the next update', 'default');
                        break;
                    case 'beginProcess':
                        this.showNotification('Loan application process started', 'success');
                        break;
                    // Other actions would be handled here
                }
            });
        });
        
        // Auto-close after 10 seconds
        setTimeout(() => {
            if (document.body.contains(modal)) {
                modal.remove();
            }
        }, 10000);
    }
    
    showNotification(message, type) {
        if (window.dashboardManager) {
            window.dashboardManager.showNotification(message, type);
        } else {
            alert(message);
        }
    }
}

// Initialize loan assessment when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Loan Assessment Manager...');
    window.loanAssessmentManager = new LoanAssessmentManager();
});