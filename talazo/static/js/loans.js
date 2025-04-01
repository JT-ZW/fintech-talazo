// loans.js - JavaScript for Talazo AgriFinance Loans page

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the loans page
    const loansManager = new LoansManager();
    loansManager.initialize();
  });
  
  class LoansManager {
    constructor() {
      // Soil health data - would normally be fetched from the API
      this.soilHealthData = {
        health_score: 72,
        risk_level: "Medium-Low Risk",
        soil_data: {
          ph_level: 6.5,
          nitrogen_level: 30,
          phosphorus_level: 25,
          potassium_level: 200,
          organic_matter: 4.0,
          cation_exchange_capacity: 15,
          moisture_content: 25
        }
      };
      
      // Maximum loan amounts based on score ranges
      this.loanScoreRanges = {
        0: 0,          // 0 score = $0 max loan
        20: 500,       // 20 score = $500 max loan
        40: 1000,      // 40 score = $1000 max loan
        60: 2000,      // 60 score = $2000 max loan
        80: 3000,      // 80 score = $3000 max loan
        90: 5000       // 90+ score = $5000 max loan
      };
      
      // Interest rates based on score ranges
      this.interestRateRanges = {
        0: 0,          // 0 score = Not eligible
        20: 15,        // 20 score = 15% interest
        40: 12,        // 40 score = 12% interest
        60: 8.25,      // 60 score = 8.25% interest
        80: 5.75,      // 80 score = 5.75% interest
        90: 4.5        // 90+ score = 4.5% interest
      };
      
      // Maximum loan terms based on score ranges
      this.termRanges = {
        0: 0,          // 0 score = Not eligible
        20: 6,         // 20 score = 6 months max
        40: 12,        // 40 score = 12 months max
        60: 24,        // 60 score = 24 months max
        80: 36,        // 80 score = 36 months max
        90: 48         // 90+ score = 48 months max
      };
    }
    
    initialize() {
      console.log('Initializing Loans Manager');
      
      // Initialize loan eligibility display
      this.initializeLoanEligibility();
      
      // Initialize soil impact chart
      this.initializeSoilImpactChart();
      
      // Initialize loan application form
      this.initializeLoanApplication();
      
      // Initialize loan history table
      this.initializeLoanHistory();
      
      // Initialize financial institutions
      this.initializeInstitutions();
      
      // Initialize loan recommendations
      this.initializeLoanRecommendations();
      
      // Set up event listeners
      this.setupEventListeners();
    }
    
    initializeLoanEligibility() {
      // Get the financial health score from soil data
      const score = this.soilHealthData.health_score;
      
      // Update the financial index display
      document.getElementById('financial-index').textContent = score;
      
      // Calculate loan terms based on score
      const maxLoanAmount = this.calculateMaxLoanAmount(score);
      const interestRate = this.calculateInterestRate(score);
      const maxTerm = this.calculateMaxTerm(score);
      
      // Update the loan eligibility card
      document.getElementById('max-loan-amount').textContent = maxLoanAmount.toLocaleString();
      document.getElementById('interest-rate').textContent = interestRate.toFixed(2);
      document.getElementById('loan-term').textContent = maxTerm;
      
      // Update the loan slider max value
      const loanSlider = document.getElementById('loan-amount');
      if (loanSlider) {
        loanSlider.max = maxLoanAmount;
        document.getElementById('max-slider-value').textContent = maxLoanAmount.toLocaleString();
      }
      
      // Update the loan status indicator
      this.updateLoanStatusIndicator(score);
    }
    
    updateLoanStatusIndicator(score) {
      const statusIndicator = document.getElementById('loan-status-indicator');
      if (!statusIndicator) return;
      
      let statusClass, statusText;
      
      if (score >= 70) {
        statusClass = 'eligible';
        statusText = 'Eligible';
      } else if (score >= 40) {
        statusClass = 'conditional';
        statusText = 'Conditional';
      } else {
        statusClass = 'ineligible';
        statusText = 'Ineligible';
      }
      
      statusIndicator.className = 'status-indicator ' + statusClass;
      statusIndicator.innerHTML = `
        <div class="status-text">${statusText}</div>
        <div class="score">${score}</div>
      `;
    }
    
    initializeSoilImpactChart() {
      const chartElement = document.getElementById('soil-impact-chart');
      if (!chartElement || !window.Plotly) return;
      
      // Get current score and max loan amount
      const currentScore = this.soilHealthData.health_score;
      const currentLoan = this.calculateMaxLoanAmount(currentScore);
      
      // Calculate loan amounts for different soil parameter improvements
      const improvements = [
        { param: 'pH Level', increase: '+0.5', loanIncrease: this.calculateLoanIncreaseForParamImprovement('ph_level', 0.5) },
        { param: 'Nitrogen', increase: '+5 mg/kg', loanIncrease: this.calculateLoanIncreaseForParamImprovement('nitrogen_level', 5) },
        { param: 'Organic Matter', increase: '+1%', loanIncrease: this.calculateLoanIncreaseForParamImprovement('organic_matter', 1) },
        { param: 'Phosphorus', increase: '+5 mg/kg', loanIncrease: this.calculateLoanIncreaseForParamImprovement('phosphorus_level', 5) }
      ];
      
      // Sort improvements by impact
      improvements.sort((a, b) => b.loanIncrease - a.loanIncrease);
      
      // Create chart data
      const data = [{
        x: improvements.map(item => `${item.param}<br>${item.increase}`),
        y: improvements.map(item => item.loanIncrease),
        type: 'bar',
        marker: {
          color: '#27AE60'
        },
        text: improvements.map(item => `$${item.loanIncrease.toFixed(0)}`),
        textposition: 'auto',
        hoverinfo: 'x+y',
        hovertemplate: '<b>%{x}</b><br>Loan increase: $%{y:.0f}<extra></extra>'
      }];
      
      // Chart layout
      const layout = {
        title: {
          text: 'Potential Loan Amount Increase',
          font: { size: 16 }
        },
        xaxis: {
          title: 'Soil Parameter Improvement',
          tickangle: 0
        },
        yaxis: {
          title: 'Additional Loan Amount ($)',
          tickprefix: '$'
        },
        margin: { t: 50, b: 80, l: 80, r: 30 },
        font: { family: 'Poppins, sans-serif' },
        bargap: 0.3
      };
      
      // Create the chart
      Plotly.newPlot(chartElement, data, layout, { responsive: true });
    }
    
    calculateLoanIncreaseForParamImprovement(param, increase) {
      // Clone the current soil data
      const improvedSoilData = JSON.parse(JSON.stringify(this.soilHealthData));
      
      // Apply the improvement
      improvedSoilData.soil_data[param] += increase;
      
      // Calculate the new score (simplified algorithm)
      const newScore = this.calculateImprovedScore(param, increase);
      
      // Calculate the loan difference
      const currentLoan = this.calculateMaxLoanAmount(this.soilHealthData.health_score);
      const newLoan = this.calculateMaxLoanAmount(newScore);
      
      return newLoan - currentLoan;
    }
    
    calculateImprovedScore(param, increase) {
      // This is a simplified algorithm to estimate score improvements
      // In a real implementation, this would use the actual soil health algorithm
      
      // Base weights for each parameter
      const weights = {
        'ph_level': 0.20,
        'nitrogen_level': 0.15,
        'phosphorus_level': 0.15,
        'potassium_level': 0.15,
        'organic_matter': 0.15,
        'cation_exchange_capacity': 0.10,
        'moisture_content': 0.10
      };
      
      // Estimated impact per unit change
      const impactPerUnit = {
        'ph_level': 10,  // 1.0 pH change = ~10 points
        'nitrogen_level': 1,  // 1 mg/kg = ~1 point
        'phosphorus_level': 1.2,  // 1 mg/kg = ~1.2 points
        'potassium_level': 0.1,  // 10 mg/kg = ~1 point
        'organic_matter': 8,  // 1% = ~8 points
        'cation_exchange_capacity': 3,  // 1 unit = ~3 points
        'moisture_content': 2  // 1% = ~2 points
      };
      
      // Calculate estimated score increase
      const paramWeight = weights[param] || 0.15;
      const paramImpact = impactPerUnit[param] || 1;
      const estimatedIncrease = paramWeight * paramImpact * increase;
      
      // Apply a cap to make results realistic
      const cappedIncrease = Math.min(estimatedIncrease, 15);
      
      // Return new estimated score
      return Math.min(100, this.soilHealthData.health_score + cappedIncrease);
    }
    
    initializeLoanApplication() {
      // Initialize the loan amount slider
      const loanSlider = document.getElementById('loan-amount');
      const amountDisplay = document.getElementById('amount-display');
      
      if (loanSlider && amountDisplay) {
        // Set initial value
        amountDisplay.textContent = parseInt(loanSlider.value).toLocaleString();
        
        // Update display when slider changes
        loanSlider.addEventListener('input', () => {
          amountDisplay.textContent = parseInt(loanSlider.value).toLocaleString();
          this.updateLoanCalculations();
        });
      }
      
      // Initialize the term selector
      const termSelect = document.getElementById('loan-term-select');
      if (termSelect) {
        termSelect.addEventListener('change', () => {
          this.updateLoanCalculations();
        });
      }
      
      // Initial calculation
      this.updateLoanCalculations();
    }
    
    updateLoanCalculations() {
      const loanAmount = parseFloat(document.getElementById('loan-amount').value) || 0;
      const termMonths = parseInt(document.getElementById('loan-term-select').value) || 12;
      const interestRate = this.calculateInterestRate(this.soilHealthData.health_score);
      
      // Calculate monthly payment (simple formula for demonstration)
      const monthlyInterestRate = interestRate / 100 / 12;
      const monthlyPayment = (loanAmount * monthlyInterestRate) / (1 - Math.pow(1 + monthlyInterestRate, -termMonths));
      
      // Calculate total interest
      const totalPayment = monthlyPayment * termMonths;
      const totalInterest = totalPayment - loanAmount;
      
      // Update the display
      document.getElementById('monthly-payment').textContent = monthlyPayment.toFixed(2);
      document.getElementById('total-interest').textContent = totalInterest.toFixed(2);
    }
    
    initializeLoanHistory() {
      // Sample loan history data - would normally come from API
      const loanHistory = [
        {
          id: 'LOAN-2023-0127',
          date: '2023-10-15',
          amount: 1200,
          purpose: 'Farm Inputs',
          status: 'completed',
          soil_score: 65
        },
        {
          id: 'LOAN-2024-0086',
          date: '2024-03-22',
          amount: 1800,
          purpose: 'Equipment',
          status: 'active',
          soil_score: 70
        },
        {
          id: 'LOAN-2024-0231',
          date: '2024-11-05',
          amount: 500,
          purpose: 'Emergency',
          status: 'pending',
          soil_score: 72
        }
      ];
      
      // Populate the loan history table
      const tableBody = document.getElementById('loan-history-body');
      if (!tableBody) return;
      
      tableBody.innerHTML = '';
      
      loanHistory.forEach(loan => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
          <td>${loan.id}</td>
          <td>${loan.date}</td>
          <td>$${loan.amount.toLocaleString()}</td>
          <td>${loan.purpose}</td>
          <td><span class="history-status ${loan.status}">${this.capitalizeFirst(loan.status)}</span></td>
          <td>${loan.soil_score}</td>
          <td class="actions">
            <button class="action-button" title="View Details"><i class="fas fa-eye"></i></button>
            <button class="action-button" title="Download"><i class="fas fa-download"></i></button>
          </td>
        `;
        
        tableBody.appendChild(row);
      });
    }
    
    initializeInstitutions() {
      // Sample financial institutions data
      const institutions = [
        {
          name: 'AgriBank Zimbabwe',
          type: 'Bank',
          interest: this.calculateInterestRate(this.soilHealthData.health_score) - 0.5,
          logo: 'AB'
        },
        {
          name: 'Microfinance Rural',
          type: 'Microfinance',
          interest: this.calculateInterestRate(this.soilHealthData.health_score) + 1.25,
          logo: 'MR'
        },
        {
          name: 'Farm Credit Union',
          type: 'Credit Union',
          interest: this.calculateInterestRate(this.soilHealthData.health_score),
          logo: 'FC'
        }
      ];
      
      // Populate the institutions grid
      const institutionsGrid = document.getElementById('institutions-grid');
      if (!institutionsGrid) return;
      
      institutionsGrid.innerHTML = '';
      
      institutions.forEach(institution => {
        const card = document.createElement('div');
        card.className = 'institution-card';
        
        card.innerHTML = `
          <div class="institution-logo">${institution.logo}</div>
          <div class="institution-details">
            <div class="institution-name">${institution.name}</div>
            <div class="institution-type">${institution.type}</div>
            <div class="institution-interest">Interest Rate: <span>${institution.interest.toFixed(2)}%</span></div>
          </div>
        `;
        
        institutionsGrid.appendChild(card);
      });
    }
    
    initializeLoanRecommendations() {
      // Sample AI recommendations based on soil health data
      const recommendations = [
        {
          title: 'Optimal Loan for Current Season',
          amount: Math.round(this.calculateMaxLoanAmount(this.soilHealthData.health_score) * 0.75),
          details: 'Based on your current soil health index and seasonal needs, we recommend a focused loan for key inputs.',
          benefits: [
            'Aligned with current soil health status',
            'Optimized for seasonal requirements',
            'Manageable repayment schedule'
          ]
        },
        {
          title: 'Soil Improvement Investment',
          amount: Math.round(this.calculateMaxLoanAmount(this.soilHealthData.health_score) * 0.4),
          details: 'A targeted loan to address specific soil deficiencies, which will improve both productivity and future loan terms.',
          benefits: [
            'Could increase soil health score by 8-12 points',
            'Potential yield increase of 15-20%',
            'Better loan terms in future applications'
          ]
        }
      ];
      
      // Populate the recommendations container
      const recommendationsContainer = document.getElementById('loan-recommendations');
      if (!recommendationsContainer) return;
      
      recommendationsContainer.innerHTML = '';
      
      recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        
        // Create benefits list
        const benefitsList = rec.benefits.map(benefit => `<li>${benefit}</li>`).join('');
        
        item.innerHTML = `
          <div class="recommendation-title">
            ${rec.title}
            <span class="recommendation-amount">$${rec.amount.toLocaleString()}</span>
          </div>
          <div class="recommendation-details">
            ${rec.details}
          </div>
          <div class="recommendation-benefits">
            <ul class="benefits-list">
              ${benefitsList}
            </ul>
          </div>
        `;
        
        recommendationsContainer.appendChild(item);
      });
    }
    
    setupEventListeners() {
      // Handle form submission
      const loanForm = document.getElementById('loan-application-form');
      if (loanForm) {
        loanForm.addEventListener('submit', (e) => {
          e.preventDefault();
          this.submitLoanApplication();
        });
      }
      
      // Handle modal close button
      const modalCloseButtons = document.querySelectorAll('.modal-close, .modal-footer .btn');
      modalCloseButtons.forEach(button => {
        button.addEventListener('click', () => {
          document.getElementById('success-modal').classList.add('hidden');
        });
      });
    }
    
    submitLoanApplication() {
      // Get form data
      const purpose = document.getElementById('loan-purpose').value;
      const amount = document.getElementById('loan-amount').value;
      const term = document.getElementById('loan-term-select').value;
      
      // Validate form
      if (!purpose || !amount || !term) {
        this.showNotification('Please fill in all required fields', 'warning');
        return;
      }
      
      // Show loading overlay
      document.getElementById('loading-overlay').classList.remove('hidden');
      
      // Simulate API call
      setTimeout(() => {
        // Hide loading overlay
        document.getElementById('loading-overlay').classList.add('hidden');
        
        // Show success modal
        document.getElementById('success-modal').classList.remove('hidden');
        
        // Reset form
        document.getElementById('loan-application-form').reset();
        
        // Update calculations
        this.updateLoanCalculations();
      }, 1500);
    }
    
    calculateMaxLoanAmount(score) {
      // Find the appropriate loan range
      let maxAmount = 0;
      
      for (const [rangeScore, amount] of Object.entries(this.loanScoreRanges)) {
        if (score >= parseInt(rangeScore)) {
          maxAmount = amount;
        }
      }
      
      // Apply a linear interpolation between the ranges for smoother results
      const ranges = Object.keys(this.loanScoreRanges).map(Number).sort((a, b) => a - b);
      
      for (let i = 0; i < ranges.length - 1; i++) {
        const lowerScore = ranges[i];
        const upperScore = ranges[i + 1];
        
        if (score >= lowerScore && score < upperScore) {
          const lowerAmount = this.loanScoreRanges[lowerScore];
          const upperAmount = this.loanScoreRanges[upperScore];
          
          // Linear interpolation
          const scoreRatio = (score - lowerScore) / (upperScore - lowerScore);
          maxAmount = lowerAmount + scoreRatio * (upperAmount - lowerAmount);
          break;
        }
      }
      
      return Math.round(maxAmount);
    }
    
    calculateInterestRate(score) {
      // Find the appropriate interest rate range
      let interestRate = this.interestRateRanges[0];
      
      for (const [rangeScore, rate] of Object.entries(this.interestRateRanges)) {
        if (score >= parseInt(rangeScore)) {
          interestRate = rate;
        }
      }
      
      return interestRate;
    }
    
    calculateMaxTerm(score) {
      // Find the appropriate term range
      let maxTerm = this.termRanges[0];
      
      for (const [rangeScore, term] of Object.entries(this.termRanges)) {
        if (score >= parseInt(rangeScore)) {
          maxTerm = term;
        }
      }
      
      return maxTerm;
    }
    
    capitalizeFirst(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    showNotification(message, type = 'default') {
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
        alert(message);
      }
    }
  }