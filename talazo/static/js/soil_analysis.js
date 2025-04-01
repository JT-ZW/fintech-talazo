// soil_analysis.js - Functionality for the soil analysis page

document.addEventListener('DOMContentLoaded', function() {
    // Initialize modules
    initializePage();
    setupEventListeners();
    initializeCharts();
    
    // Update last update time
    updateLastUpdateTime();
    
    // Add error handling for the entire script
    window.addEventListener('error', function(e) {
      console.error('Global error caught:', e);
      // Hide loading overlay if an error occurs
      document.getElementById('loading-overlay').classList.add('hidden');
      showToast('An error occurred. Please try again.', 'error');
    });
  });
  
  // Initialize page components
  function initializePage() {
    console.log('Soil analysis page initialized');
    
    // Initialize the gauge chart with default value
    initializeGauge();
    
    // Initialize parameter details view
    updateParameterDetailsView('bar');
  }
  
  // Set up event listeners for all interactive elements
  function setupEventListeners() {
    // Form submission
    document.getElementById('soil-metrics-form').addEventListener('submit', function(e) {
      e.preventDefault();
      try {
        calculateFinancialIndex();
      } catch (error) {
        console.error('Error during financial index calculation:', error);
        document.getElementById('loading-overlay').classList.add('hidden');
        showToast('Error calculating financial index. Please try again.', 'error');
      }
    });
    
    // Randomize data
    document.getElementById('randomize-data').addEventListener('click', randomizeData);
    
    // Sample data loading
    document.getElementById('load-sample-data').addEventListener('click', loadSampleData);
    
    // Form clearing
    document.getElementById('clear-form').addEventListener('click', clearForm);
    
    // View selector for parameter details
    document.querySelectorAll('.view-btn').forEach(button => {
      button.addEventListener('click', function() {
        const view = this.getAttribute('data-view');
        
        // Update active button
        document.querySelectorAll('.view-btn').forEach(btn => {
          btn.classList.remove('active');
        });
        this.classList.add('active');
        
        // Update view
        updateParameterDetailsView(view);
      });
    });
    
    // Chat functionality
    document.getElementById('send-message').addEventListener('click', sendMessage);
    document.getElementById('chat-input').addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
    
    // Quick questions
    document.querySelectorAll('.quick-question').forEach(question => {
      question.addEventListener('click', function() {
        const questionText = this.getAttribute('data-question');
        document.getElementById('chat-input').value = questionText;
        sendMessage();
      });
    });
    
    // Clear chat
    document.getElementById('clear-chat').addEventListener('click', clearChat);
    
    // Results actions
    document.getElementById('save-results').addEventListener('click', saveResults);
    document.getElementById('print-results').addEventListener('click', printResults);
    
    // Farmer selection
    document.getElementById('farmer-selector').addEventListener('change', function() {
      if (this.value) {
        loadFarmerData(this.value);
      }
    });
    
    // Refresh data
    document.getElementById('refresh-data').addEventListener('click', refreshData);
  }
  
  // Initialize the gauge chart
  function initializeGauge() {
    try {
      const gaugeElement = document.getElementById('financial-index-gauge');
      if (gaugeElement) {
        GaugeChart.gaugeChart(gaugeElement, {
          hasNeedle: true,
          needleColor: "#464A4F",
          arcColors: ["#F44336", "#FFC107", "#4CAF50"],
          arcDelimiters: [40, 60],
          rangeLabel: ["0", "100"],
          centralLabel: "0",
        });
      }
    } catch (error) {
      console.error('Error initializing gauge:', error);
    }
  }
  
  // Initialize charts
  function initializeCharts() {
    try {
      // Parameter scores chart
      const paramCtx = document.getElementById('parameter-chart');
      if (paramCtx) {
        window.parameterChart = new Chart(paramCtx, {
          type: 'bar',
          data: {
            labels: ['pH', 'Nitrogen', 'Phosphorus', 'Potassium', 'Organic Matter', 'CEC', 'Moisture'],
            datasets: [{
              label: 'Parameter Scores',
              data: [0, 0, 0, 0, 0, 0, 0],
              backgroundColor: [
                'rgba(75, 192, 192, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)',
                'rgba(76, 175, 80, 0.7)',
                'rgba(33, 150, 243, 0.7)',
                'rgba(255, 193, 7, 0.7)'
              ],
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `Score: ${context.raw.toFixed(1)}/100`;
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Score'
                }
              }
            }
          }
        });
      }
    } catch (error) {
      console.error('Error initializing charts:', error);
    }
  }
  
  // Randomize data in the form inputs
  function randomizeData() {
    try {
      console.log('Randomizing soil data');
      
      // Generate random values for each parameter
      document.getElementById('ph_level').value = (Math.random() * 4 + 4).toFixed(1); // 4.0-8.0
      document.getElementById('nitrogen_level').value = (Math.random() * 50 + 5).toFixed(1); // 5-55
      document.getElementById('phosphorus_level').value = (Math.random() * 35 + 5).toFixed(1); // 5-40
      document.getElementById('potassium_level').value = (Math.random() * 200 + 100).toFixed(1); // 100-300
      document.getElementById('organic_matter').value = (Math.random() * 7 + 1).toFixed(1); // 1-8
      document.getElementById('cation_exchange_capacity').value = (Math.random() * 20 + 5).toFixed(1); // 5-25
      document.getElementById('moisture_content').value = (Math.random() * 30 + 10).toFixed(1); // 10-40
      
      // Select a random region
      const regions = document.getElementById('region').options;
      const randomIndex = Math.floor(Math.random() * (regions.length - 1)) + 1;
      document.getElementById('region').selectedIndex = randomIndex;
      
      // Show toast notification
      showToast('Random soil data generated', 'success');
      
      // Calculate financial index automatically
      calculateFinancialIndex();
    } catch (error) {
      console.error('Error randomizing data:', error);
      showToast('Error generating random data', 'error');
    }
  }
  
  // Load sample data into the form
  function loadSampleData() {
    try {
      console.log('Loading sample soil data');
      
      document.getElementById('ph_level').value = '6.5';
      document.getElementById('nitrogen_level').value = '30.0';
      document.getElementById('phosphorus_level').value = '22.5';
      document.getElementById('potassium_level').value = '220.0';
      document.getElementById('organic_matter').value = '4.2';
      document.getElementById('cation_exchange_capacity').value = '16.5';
      document.getElementById('moisture_content').value = '25.0';
      document.getElementById('region').value = 'mashonaland_central';
      
      // Show toast notification
      showToast('Sample data loaded', 'success');
      
      // Calculate financial index automatically
      calculateFinancialIndex();
    } catch (error) {
      console.error('Error loading sample data:', error);
      showToast('Error loading sample data', 'error');
    }
  }
  
  // Clear the form
  function clearForm() {
    try {
      console.log('Clearing form data');
      
      // Reset the form
      document.getElementById('soil-metrics-form').reset();
      
      // Reset financial index display
      document.getElementById('financial-index-score').textContent = '--';
      document.getElementById('risk-level').textContent = '--';
      document.getElementById('loan-eligibility').textContent = '--';
      document.getElementById('interest-rate').textContent = '--';
      document.getElementById('insurance-premium').textContent = '--';
      document.getElementById('predicted-yield').textContent = '--';
      
      // Reset gauge
      initializeGauge();
      
      // Reset parameter chart
      if (window.parameterChart) {
        window.parameterChart.data.datasets[0].data = [0, 0, 0, 0, 0, 0, 0];
        window.parameterChart.update();
      }
      
      // Reset parameter details view
      updateParameterDetailsView('bar');
      
      // Show toast notification
      showToast('Form cleared', 'info');
    } catch (error) {
      console.error('Error clearing form:', error);
      showToast('Error clearing form', 'error');
    }
  }
  
  // Calculate financial index based on soil metrics
  function calculateFinancialIndex() {
    try {
      console.log('Starting financial index calculation...');
      
      // Show loading overlay
      document.getElementById('loading-overlay').classList.remove('hidden');
      
      // Get form values
      const soilData = {
        ph_level: parseFloat(document.getElementById('ph_level').value) || 0,
        nitrogen_level: parseFloat(document.getElementById('nitrogen_level').value) || 0,
        phosphorus_level: parseFloat(document.getElementById('phosphorus_level').value) || 0,
        potassium_level: parseFloat(document.getElementById('potassium_level').value) || 0,
        organic_matter: parseFloat(document.getElementById('organic_matter').value) || 0,
        cation_exchange_capacity: parseFloat(document.getElementById('cation_exchange_capacity').value) || 0,
        moisture_content: parseFloat(document.getElementById('moisture_content').value) || 0,
        region: document.getElementById('region').value
      };
      
      console.log('Soil data collected:', soilData);
      
      // Simulate API call/calculation delay
      setTimeout(() => {
        try {
          // Calculate soil health score
          const { overallScore, parameterScores, riskLevel } = calculateSoilHealthScore(soilData);
          console.log('Soil health calculation complete:', { overallScore, riskLevel });
          
          // Update display
          updateResults(overallScore, parameterScores, riskLevel);
          console.log('Results updated');
          
          // Update parameter details view
          updateParameterDetailsView(getActiveView(), parameterScores);
          console.log('Parameter details updated');
          
          // Hide loading overlay
          document.getElementById('loading-overlay').classList.add('hidden');
          
          // Show toast notification
          showToast('Financial index calculated successfully', 'success');
          
          // Add a soil health assessment message from the AI
          addBotMessage(generateSoilAssessment(overallScore, parameterScores, riskLevel));
          
          // Update last update time
          updateLastUpdateTime();
        } catch (error) {
          console.error('Error in financial index calculation:', error);
          document.getElementById('loading-overlay').classList.add('hidden');
          showToast('Error calculating financial index', 'error');
        }
      }, 1200);
    } catch (error) {
      console.error('Error in calculate financial index function:', error);
      document.getElementById('loading-overlay').classList.add('hidden');
      showToast('Error calculating financial index', 'error');
    }
  }
  
  // Calculate soil health score based on parameters
  function calculateSoilHealthScore(soilData) {
    console.log('Calculating soil health score for:', soilData);
    
    // Define ideal ranges for parameters
    const idealRanges = {
      ph_level: [6.0, 7.0],
      nitrogen_level: [20.0, 40.0],
      phosphorus_level: [15.0, 30.0],
      potassium_level: [150.0, 250.0],
      organic_matter: [3.0, 5.0],
      cation_exchange_capacity: [10.0, 20.0],
      moisture_content: [20.0, 30.0]
    };
    
    // Define weights for each parameter
    const weights = {
      ph_level: 0.20,
      nitrogen_level: 0.15,
      phosphorus_level: 0.15,
      potassium_level: 0.15,
      organic_matter: 0.15,
      cation_exchange_capacity: 0.10,
      moisture_content: 0.10
    };
    
    // Calculate score for each parameter
    const parameterScores = {};
    let weightedScore = 0;
    let totalWeight = 0;
    
    for (const [param, value] of Object.entries(soilData)) {
      if (param === 'region' || value === 0) continue;
      
      const [minIdeal, maxIdeal] = idealRanges[param] || [0, 0];
      let score = 0;
      
      // Perfect score if within ideal range
      if (value >= minIdeal && value <= maxIdeal) {
        score = 100;
      } else {
        // Calculate score based on distance from ideal range
        const deviation = value < minIdeal 
          ? (minIdeal - value) / minIdeal 
          : (value - maxIdeal) / maxIdeal;
        
        score = Math.max(0, 100 - (deviation * 100));
      }
      
      parameterScores[param] = score;
      weightedScore += score * weights[param];
      totalWeight += weights[param];
    }
    
    // Calculate overall score
    const overallScore = totalWeight > 0 ? weightedScore / totalWeight : 0;
    
    // Determine risk level
    let riskLevel;
    if (overallScore >= 80) {
      riskLevel = "Low Risk";
    } else if (overallScore >= 60) {
      riskLevel = "Medium-Low Risk";
    } else if (overallScore >= 40) {
      riskLevel = "Medium Risk";
    } else if (overallScore >= 20) {
      riskLevel = "Medium-High Risk";
    } else {
      riskLevel = "High Risk";
    }
    
    return { overallScore, parameterScores, riskLevel };
  }
  
  // Update the results display
  function updateResults(healthScore, parameterScores, riskLevel) {
    try {
      console.log('Updating results with:', { healthScore, riskLevel });
      
      // Update financial index score and gauge
      document.getElementById('financial-index-score').textContent = healthScore.toFixed(1);
      
      // Update gauge
      GaugeChart.gaugeChart(document.getElementById('financial-index-gauge'), {
        hasNeedle: true,
        needleColor: "#464A4F",
        arcColors: ["#F44336", "#FFC107", "#4CAF50"],
        arcDelimiters: [40, 60],
        rangeLabel: ["0", "100"],
        centralLabel: healthScore.toFixed(0),
        needleValue: healthScore
      });
      
      // Update risk level
      document.getElementById('risk-level').textContent = riskLevel;
      
      // Calculate financial implications
      // Loan eligibility
      let loanEligibility = "Not Eligible";
      if (healthScore >= 30) {
        loanEligibility = "Eligible";
      }
      document.getElementById('loan-eligibility').textContent = loanEligibility;
      
      // Interest rate (inversely proportional to health score)
      const baseRate = 15; // 15% base rate
      const interestRate = Math.max(5, baseRate - (healthScore / 10)).toFixed(1);
      document.getElementById('interest-rate').textContent = interestRate;
      
      // Insurance premium (inversely proportional to health score)
      const basePremium = 100;
      const riskFactor = (100 - healthScore) / 100;
      const premium = (basePremium * (1 + riskFactor ** 1.8)).toFixed(2);
      document.getElementById('insurance-premium').textContent = premium;
      
      // Predicted yield (directly proportional to health score)
      const baseYield = 2.0;
      const maxYield = 6.0;
      const predictedYield = (baseYield + ((maxYield - baseYield) * (healthScore / 100))).toFixed(1);
      document.getElementById('predicted-yield').textContent = predictedYield;
      
      // Update parameter chart
      updateParameterChart(parameterScores);
    } catch (error) {
      console.error('Error in updateResults:', error);
      throw error;
    }
  }
  
  // Update the parameter chart with scores
  function updateParameterChart(parameterScores) {
    try {
      console.log('Updating parameter chart with:', parameterScores);
      
      if (!window.parameterChart) {
        console.warn('Parameter chart not initialized');
        return;
      }
      
      const chartData = [
        parameterScores.ph_level || 0,
        parameterScores.nitrogen_level || 0,
        parameterScores.phosphorus_level || 0,
        parameterScores.potassium_level || 0,
        parameterScores.organic_matter || 0,
        parameterScores.cation_exchange_capacity || 0,
        parameterScores.moisture_content || 0
      ];
      
      // Update the chart colors based on scores
      window.parameterChart.data.datasets[0].backgroundColor = chartData.map(score => {
        if (score >= 80) return 'rgba(76, 175, 80, 0.7)'; // Optimal
        if (score >= 60) return 'rgba(139, 195, 74, 0.7)'; // Good
        if (score >= 40) return 'rgba(255, 193, 7, 0.7)'; // Average
        if (score >= 20) return 'rgba(255, 152, 0, 0.7)'; // Poor
        return 'rgba(244, 67, 54, 0.7)'; // Critical
      });
      
      window.parameterChart.data.datasets[0].data = chartData;
      window.parameterChart.update();
    } catch (error) {
      console.error('Error updating parameter chart:', error);
    }
  }
  
  // Get active view for parameter details
  function getActiveView() {
    const activeBtn = document.querySelector('.view-btn.active');
    return activeBtn ? activeBtn.getAttribute('data-view') : 'bar';
  }
  
  // Update parameter details view
  function updateParameterDetailsView(viewType, parameterScores = null) {
    try {
      console.log('Updating parameter details view to:', viewType);
      
      const container = document.getElementById('parameter-details-view');
      container.className = `${viewType}-view`;
      
      if (!parameterScores) {
        // If no scores provided, use empty view
        if (viewType === 'bar') {
          container.innerHTML = '<div class="empty-state">Enter soil metrics and calculate financial index to see parameter details.</div>';
        } else if (viewType === 'radar') {
          container.innerHTML = '<div class="empty-state">Enter soil metrics and calculate financial index to see radar chart.</div>';
        } else if (viewType === 'table') {
          container.innerHTML = '<div class="empty-state">Enter soil metrics and calculate financial index to see detailed table.</div>';
        }
        return;
      }
      
      // Parameters array for reference
      const parameters = [
        { id: 'ph_level', name: 'pH Level', unit: '', ideal: '6.0-7.0' },
        { id: 'nitrogen_level', name: 'Nitrogen', unit: 'mg/kg', ideal: '20.0-40.0' },
        { id: 'phosphorus_level', name: 'Phosphorus', unit: 'mg/kg', ideal: '15.0-30.0' },
        { id: 'potassium_level', name: 'Potassium', unit: 'mg/kg', ideal: '150.0-250.0' },
        { id: 'organic_matter', name: 'Organic Matter', unit: '%', ideal: '3.0-5.0' },
        { id: 'cation_exchange_capacity', name: 'CEC', unit: 'cmol/kg', ideal: '10.0-20.0' },
        { id: 'moisture_content', name: 'Moisture Content', unit: '%', ideal: '20.0-30.0' }
      ];
      
      if (viewType === 'table') {
        // Generate table view
        let tableHtml = `
          <table class="param-table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Value</th>
                <th>Ideal Range</th>
                <th>Score</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>
        `;
        
        for (const param of parameters) {
          const value = document.getElementById(param.id).value;
          const score = parameterScores[param.id] || 0;
          const rating = getRatingFromScore(score);
          
          tableHtml += `
            <tr>
              <td>${param.name}</td>
              <td>${value} ${param.unit}</td>
              <td>${param.ideal}</td>
              <td class="score">${score.toFixed(1)}</td>
              <td><span class="param-rating ${rating.toLowerCase()}">${rating}</span></td>
            </tr>
          `;
        }
        
        tableHtml += `
            </tbody>
          </table>
        `;
        
        container.innerHTML = tableHtml;
      } else if (viewType === 'radar') {
        // Create canvas for radar chart
        container.innerHTML = '<canvas id="radar-chart"></canvas>';
        
        const ctx = document.getElementById('radar-chart').getContext('2d');
        
        new Chart(ctx, {
          type: 'radar',
          data: {
            labels: parameters.map(p => p.name),
            datasets: [{
              label: 'Parameter Scores',
              data: parameters.map(p => parameterScores[p.id] || 0),
              fill: true,
              backgroundColor: 'rgba(76, 175, 80, 0.2)',
              borderColor: 'rgba(76, 175, 80, 1)',
              pointBackgroundColor: 'rgba(76, 175, 80, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(76, 175, 80, 1)'
            }]
          },
          options: {
            scales: {
              r: {
                angleLines: {
                  display: true
                },
                suggestedMin: 0,
                suggestedMax: 100
              }
            }
          }
        });
      } else {
        // Bar chart view - Using parameter-chart, no need to create new one
        // Just display a message
        container.innerHTML = '<div class="chart-note">Parameter details are displayed in the chart above.</div>';
      }
    } catch (error) {
      console.error('Error updating parameter details view:', error);
    }
  }
  
  // Get rating text from score
  function getRatingFromScore(score) {
    if (score >= 80) return 'Optimal';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Average';
    if (score >= 20) return 'Poor';
    return 'Critical';
  }
  
  // Send message in chat
  function sendMessage() {
    try {
      const input = document.getElementById('chat-input');
      const message = input.value.trim();
      
      if (!message) return;
      
      // Add user message to chat
      addUserMessage(message);
      
      // Clear input
      input.value = '';
      
      // Simulate thinking
      setTimeout(() => {
        // Process message and generate response
        const response = generateAIResponse(message);
        
        // Add bot message to chat
        addBotMessage(response);
      }, 1000);
    } catch (error) {
      console.error('Error sending message:', error);
      addBotMessage("I'm sorry, there was an error processing your message. Please try again.");
    }
  }
  
  // Add user message to chat
  function addUserMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message user';
    messageElement.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-user"></i>
      </div>
      <div class="message-content">
        <p>${message}</p>
      </div>
    `;
    
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Add bot message to chat
  function addBotMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message bot';
    messageElement.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-robot"></i>
      </div>
      <div class="message-content">
        <p>${message}</p>
      </div>
    `;
    
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Clear chat
  function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    
    // Remove all messages except the first one (welcome message)
    while (chatMessages.children.length > 1) {
      chatMessages.removeChild(chatMessages.lastChild);
    }
    
    showToast('Chat cleared', 'info');
  }
  
  // Generate AI response to user message
  function generateAIResponse(message) {
    // Get current form values to contextualize response
    const soilData = {
      ph_level: parseFloat(document.getElementById('ph_level').value) || 0,
      nitrogen_level: parseFloat(document.getElementById('nitrogen_level').value) || 0,
      phosphorus_level: parseFloat(document.getElementById('phosphorus_level').value) || 0,
      potassium_level: parseFloat(document.getElementById('potassium_level').value) || 0,
      organic_matter: parseFloat(document.getElementById('organic_matter').value) || 0,
      cation_exchange_capacity: parseFloat(document.getElementById('cation_exchange_capacity').value) || 0,
      moisture_content: parseFloat(document.getElementById('moisture_content').value) || 0
    };
    
    const financialIndex = document.getElementById('financial-index-score').textContent;
    const hasCalculated = financialIndex !== '--';
    
    // Check if any values are missing
    const isMissingValues = Object.values(soilData).some(val => val === 0);
    
    // Basic templated responses
    const responses = {
      greeting: "Hello! I'm your AI Soil Health Advisor. How can I help you improve your soil health and financial index today?",
      
      notCalculated: "I see you haven't calculated your financial index yet. Please fill in your soil metrics and click 'Calculate Financial Index' so I can provide more personalized recommendations.",
      
      missingValues: "It looks like some soil metrics are missing. For the most accurate recommendations, please provide values for all soil parameters.",
      
      generalImprovement: `Based on your current financial index of ${financialIndex}, here are some general recommendations to improve your soil health:<br><br>
        1. Focus on organic matter content by adding compost and incorporating crop residues<br>
        2. Implement crop rotation to balance nutrient uptake<br>
        3. Consider cover crops to prevent erosion and add nutrients<br>
        4. Monitor and adjust soil pH for optimal nutrient availability<br>
        5. Use soil tests regularly to track improvements`,
      
      phImprovement: function() {
        const ph = soilData.ph_level;
        if (ph === 0) return "Please provide your soil pH value for specific recommendations.";
        
        if (ph < 6.0) {
          return `Your soil pH of ${ph} is acidic. To raise pH:<br><br>
            • Apply agricultural lime at 2-4 tons per hectare<br>
            • Use dolomitic lime if magnesium is also needed<br>
            • Apply in small amounts over time for best results<br>
            • Retest soil after 3-6 months to check progress`;
        } else if (ph > 7.0) {
          return `Your soil pH of ${ph} is alkaline. To lower pH:<br><br>
            • Add organic matter such as compost and manure<br>
            • Apply elemental sulfur (follow package instructions)<br>
            • Use acidifying fertilizers like ammonium sulfate<br>
            • For severe cases, consider applying gypsum`;
        } else {
          return `Your soil pH of ${ph} is within the ideal range. Maintain current practices and monitor regularly to ensure it stays between 6.0-7.0.`;
        }
      },
      
      nitrogenImprovement: function() {
        const nitrogen = soilData.nitrogen_level;
        if (nitrogen === 0) return "Please provide your soil nitrogen value for specific recommendations.";
        
        if (nitrogen < 20.0) {
          return `Your nitrogen level of ${nitrogen} mg/kg is low. To increase nitrogen:<br><br>
            • Apply nitrogen fertilizer at 80-120 kg/ha<br>
            • Split applications for better uptake<br>
            • Plant legumes in rotation (beans, peas, groundnuts)<br>
            • Add well-rotted manure or compost<br>
            • Consider green manure crops as cover crops`;
        } else if (nitrogen > 40.0) {
          return `Your nitrogen level of ${nitrogen} mg/kg is high. Recommendations:<br><br>
            • Reduce nitrogen fertilizer applications<br>
            • Plant cover crops that use high nitrogen<br>
            • Increase carbon inputs to balance C:N ratio<br>
            • Implement crop rotation with high nitrogen-feeding crops`;
        } else {
          return `Your nitrogen level of ${nitrogen} mg/kg is within the ideal range. Maintain current practices with regular monitoring.`;
        }
      },
      
      phosphorusImprovement: function() {
        const phosphorus = soilData.phosphorus_level;
        if (phosphorus === 0) return "Please provide your soil phosphorus value for specific recommendations.";
        
        if (phosphorus < 15.0) {
          return `Your phosphorus level of ${phosphorus} mg/kg is low. To increase phosphorus:<br><br>
            • Apply phosphorus fertilizer (like superphosphate) at 50-80 kg/ha<br>
            • Add rock phosphate for slow release<br>
            • Incorporate manure and compost<br>
            • Ensure pH is around 6.5 for optimal phosphorus availability<br>
            • Reduce soil erosion to prevent phosphorus loss`;
        } else if (phosphorus > 30.0) {
          return `Your phosphorus level of ${phosphorus} mg/kg is high. Recommendations:<br><br>
            • Reduce or eliminate phosphorus fertilizer applications<br>
            • Implement buffer strips to prevent runoff<br>
            • Monitor water quality in nearby water bodies<br>
            • Consider crops that remove more phosphorus`;
        } else {
          return `Your phosphorus level of ${phosphorus} mg/kg is within the ideal range. Maintain current practices with regular monitoring.`;
        }
      },
      
      potassiumImprovement: function() {
        const potassium = soilData.potassium_level;
        if (potassium === 0) return "Please provide your soil potassium value for specific recommendations.";
        
        if (potassium < 150.0) {
          return `Your potassium level of ${potassium} mg/kg is low. To increase potassium:<br><br>
            • Apply potassium fertilizer (like muriate of potash) at 80-120 kg/ha<br>
            • Add wood ash in small amounts<br>
            • Incorporate banana peels and other potassium-rich organic matter<br>
            • Reduce soil compaction to improve potassium uptake`;
        } else if (potassium > 250.0) {
          return `Your potassium level of ${potassium} mg/kg is high. Recommendations:<br><br>
            • Reduce or eliminate potassium fertilizer applications<br>
            • Balance with other nutrients like calcium and magnesium<br>
            • Consider planting potassium-hungry crops<br>
            • Monitor for possible magnesium deficiency symptoms in plants`;
        } else {
          return `Your potassium level of ${potassium} mg/kg is within the ideal range. Maintain current practices with regular monitoring.`;
        }
      },
      
      organicMatterImprovement: function() {
        const om = soilData.organic_matter;
        if (om === 0) return "Please provide your soil organic matter value for specific recommendations.";
        
        if (om < 3.0) {
          return `Your organic matter content of ${om}% is low. To increase organic matter:<br><br>
            • Add compost at 10-20 tons per hectare<br>
            • Implement no-till or reduced tillage practices<br>
            • Use cover crops and green manures<br>
            • Return crop residues to the field<br>
            • Rotate crops to include those that produce more biomass<br>
            • This is a long-term process that may take several years`;
        } else if (om > 5.0) {
          return `Your organic matter content of ${om}% is high, which is excellent! Recommendations:<br><br>
            • Maintain current practices<br>
            • Continue adding organic matter to sustain this level<br>
            • Monitor nitrogen release, as high organic matter can release significant nitrogen<br>
            • Consider adjusting nitrogen fertilizer applications`;
        } else {
          return `Your organic matter content of ${om}% is within the ideal range. Continue your good practices to maintain this level.`;
        }
      },
      
      cecImprovement: function() {
        const cec = soilData.cation_exchange_capacity;
        if (cec === 0) return "Please provide your soil CEC value for specific recommendations.";
        
        if (cec < 10.0) {
          return `Your CEC of ${cec} cmol/kg is low, indicating limited nutrient holding capacity. Recommendations:<br><br>
            • Increase organic matter content<br>
            • Apply smaller, more frequent fertilizer applications<br>
            • Consider adding clay minerals if practical<br>
            • Use slow-release fertilizers<br>
            • Avoid over-irrigation which can leach nutrients`;
        } else if (cec > 20.0) {
          return `Your CEC of ${cec} cmol/kg is high, indicating excellent nutrient holding capacity. Recommendations:<br><br>
            • Maintain good nutrient balance<br>
            • Monitor soil pH as high CEC soils can resist pH changes<br>
            • May require more lime or sulfur to change pH<br>
            • Can likely reduce fertilizer frequency`;
        } else {
          return `Your CEC of ${cec} cmol/kg is within the ideal range, indicating good nutrient holding capacity. Maintain current practices.`;
        }
      },
      
      moistureImprovement: function() {
        const moisture = soilData.moisture_content;
        if (moisture === 0) return "Please provide your soil moisture content for specific recommendations.";
        
        if (moisture < 20.0) {
          return `Your moisture content of ${moisture}% is low. To improve moisture retention:<br><br>
            • Add organic matter to improve water holding capacity<br>
            • Apply mulch to reduce evaporation<br>
            • Implement conservation tillage practices<br>
            • Consider drip irrigation for efficient water use<br>
            • Use water-harvesting techniques like contour ridges or swales`;
        } else if (moisture > 30.0) {
          return `Your moisture content of ${moisture}% is high. To improve drainage:<br><br>
            • Create drainage channels if needed<br>
            • Consider raised beds for crops<br>
            • Reduce irrigation frequency<br>
            • Add organic matter to improve soil structure<br>
            • Avoid compaction by limiting traffic on wet soil`;
        } else {
          return `Your moisture content of ${moisture}% is within the ideal range. Maintain current practices.`;
        }
      },
      
      financialIndex: function() {
        if (!hasCalculated) return this.notCalculated;
        
        return `Your Financial Index Score is ${financialIndex}. This score directly impacts:<br><br>
          • Loan eligibility: ${document.getElementById('loan-eligibility').textContent}<br>
          • Interest rate: ${document.getElementById('interest-rate').textContent}%<br>
          • Insurance premium: ${document.getElementById('insurance-premium').textContent}/ha<br>
          • Predicted yield: ${document.getElementById('predicted-yield').textContent} tons/ha<br><br>
          Improving your soil health metrics will improve your financial index, resulting in better loan terms and lower insurance costs.`;
      },
      
      cropRecommendations: function() {
        if (!hasCalculated) return this.notCalculated;
        
        const index = parseFloat(financialIndex);
        let cropString = "";
        
        if (index >= 80) {
          cropString = "maize, tobacco, soybeans, vegetables (high-value crops)";
        } else if (index >= 60) {
          cropString = "maize, groundnuts, cotton, soybeans";
        } else if (index >= 40) {
          cropString = "sorghum, millet, groundnuts, cowpeas";
        } else {
          cropString = "sorghum, millet, cowpeas, drought-resistant varieties";
        }
        
        const ph = soilData.ph_level;
        let phNote = "";
        
        if (ph < 5.5) {
          phNote = "Note: Your acidic soil (pH " + ph + ") requires liming before planting sensitive crops like maize or soybeans.";
        } else if (ph > 7.5) {
          phNote = "Note: Your alkaline soil (pH " + ph + ") is better suited for crops like sorghum or millets.";
        }
        
        return `Based on your soil health and financial index of ${financialIndex}, suitable crops include: <br><br>
          • ${cropString}<br><br>
          ${phNote}<br><br>
          Consider crop rotation to improve soil health over time.`;
      },
      
      fallback: "I'm sorry, I don't have specific information about that. Please ask about soil parameters like pH, nitrogen, phosphorus, potassium, organic matter, CEC, moisture content, or general questions about improving your financial index."
    };
    
    // Lowercase message for easier matching
    const lowerMessage = message.toLowerCase();
    
    // Check for basic greeting
    if (/^(hello|hi|hey|greetings)/.test(lowerMessage)) {
      return responses.greeting;
    }
    
    // Check if calculations haven't been done yet
    if (!hasCalculated && !/calculate|missing|explain|what is|how does/.test(lowerMessage)) {
      return responses.notCalculated;
    }
    
    // Check for missing values
    if (isMissingValues && !/missing|explain|what is|how does/.test(lowerMessage)) {
      return responses.missingValues;
    }
    
    // Check for specific parameter questions
    if (/ph\s|ph$|acidic|alkaline|lime/.test(lowerMessage)) {
      return responses.phImprovement();
    }
    
    if (/nitrogen|n\s|fertilizer/.test(lowerMessage)) {
      return responses.nitrogenImprovement();
    }
    
    if (/phosphorus|p\s/.test(lowerMessage)) {
      return responses.phosphorusImprovement();
    }
    
    if (/potassium|potash|k\s/.test(lowerMessage)) {
      return responses.potassiumImprovement();
    }
    
    if (/organic matter|compost|manure/.test(lowerMessage)) {
      return responses.organicMatterImprovement();
    }
    
    if (/cec|cation|exchange capacity/.test(lowerMessage)) {
      return responses.cecImprovement();
    }
    
    if (/moisture|water|drainage|irrigation/.test(lowerMessage)) {
      return responses.moistureImprovement();
    }
    
    // Check for general improvement questions
    if (/how (can|do) i improve|how to improve|what (can|should) i do|recommendations/.test(lowerMessage)) {
      return responses.generalImprovement;
    }
    
    // Check for financial index questions
    if (/financial (index|score)|loan|interest|insurance|premium/.test(lowerMessage)) {
      return responses.financialIndex();
    }
    
    // Check for crop recommendation questions
    if (/crop|plant|grow|harvest|yield/.test(lowerMessage)) {
      return responses.cropRecommendations();
    }
    
    // Fallback response
    return responses.fallback;
  }
  
  // Generate soil assessment message
  function generateSoilAssessment(score, parameterScores, riskLevel) {
    // Find the lowest scoring parameters
    const paramNames = {
      ph_level: "pH level",
      nitrogen_level: "nitrogen",
      phosphorus_level: "phosphorus",
      potassium_level: "potassium",
      organic_matter: "organic matter",
      cation_exchange_capacity: "cation exchange capacity",
      moisture_content: "moisture content"
    };
    
    // Create array of parameter scores for sorting
    const scoreArray = Object.entries(parameterScores).map(([key, value]) => ({
      name: paramNames[key] || key,
      score: value
    }));
    
    // Sort by score ascending
    scoreArray.sort((a, b) => a.score - b.score);
    
    // Get the lowest 2 parameters (if they exist and are below 60)
    const lowParams = scoreArray.filter(param => param.score < 60).slice(0, 2);
    
    let assessmentMessage = `I've analyzed your soil data and calculated a Financial Index Score of ${score.toFixed(1)}, which indicates ${riskLevel}.`;
    
    if (score >= 80) {
      assessmentMessage += ` Your soil is in excellent condition, resulting in favorable financial terms. Keep up the good work!`;
    } else if (score >= 60) {
      assessmentMessage += ` Your soil is in good condition, but there's room for improvement to obtain better financial terms.`;
    } else if (score >= 40) {
      assessmentMessage += ` Your soil health is average, which is limiting your financial opportunities. Focus on improvement strategies.`;
    } else {
      assessmentMessage += ` Your soil health needs significant improvement to access better financial options.`;
    }
    
    if (lowParams.length > 0) {
      assessmentMessage += ` Consider focusing on improving your ${lowParams.map(p => p.name).join(' and ')}, which are your lowest-scoring parameters.`;
      assessmentMessage += ` Ask me specific questions about how to improve these areas!`;
    }
    
    return assessmentMessage;
  }
  
  // Save results
  function saveResults() {
    showToast('Results saved successfully', 'success');
    // In a real application, this would save the results to the server or download a file
  }
  
  // Print results
  function printResults() {
    window.print();
  }
  
  // Load farmer data
  function loadFarmerData(farmerId) {
    try {
      console.log('Loading farmer data for ID:', farmerId);
      // Show loading overlay
      document.getElementById('loading-overlay').classList.remove('hidden');
      
      // Simulate API call delay
      setTimeout(() => {
        try {
          // Sample farmer data
          const farmers = {
            1: {
              name: 'John Moyo',
              region: 'mashonaland_central',
              soilData: {
                ph_level: 6.3,
                nitrogen_level: 28.5,
                phosphorus_level: 22.1,
                potassium_level: 187.3,
                organic_matter: 3.8,
                cation_exchange_capacity: 14.2,
                moisture_content: 24.7
              }
            },
            2: {
              name: 'Mary Ncube',
              region: 'matabeleland_south',
              soilData: {
                ph_level: 7.1,
                nitrogen_level: 18.3,
                phosphorus_level: 14.5,
                potassium_level: 142.6,
                organic_matter: 2.4,
                cation_exchange_capacity: 9.8,
                moisture_content: 18.2
              }
            },
            3: {
              name: 'Robert Dube',
              region: 'manicaland',
              soilData: {
                ph_level: 5.8,
                nitrogen_level: 22.7,
                phosphorus_level: 19.3,
                potassium_level: 176.5,
                organic_matter: 4.1,
                cation_exchange_capacity: 13.6,
                moisture_content: 26.8
              }
            }
          };
          
          // Get selected farmer
          const farmer = farmers[farmerId];
          
          if (farmer) {
            // Populate form with farmer data
            document.getElementById('region').value = farmer.region;
            
            for (const [param, value] of Object.entries(farmer.soilData)) {
              const input = document.getElementById(param);
              if (input) {
                input.value = value;
              }
            }
            
            // Calculate financial index automatically
            calculateFinancialIndex();
          }
          
          // Hide loading overlay
          document.getElementById('loading-overlay').classList.add('hidden');
        } catch (error) {
          console.error('Error processing farmer data:', error);
          document.getElementById('loading-overlay').classList.add('hidden');
          showToast('Error loading farmer data', 'error');
        }
      }, 1000);
    } catch (error) {
      console.error('Error in loadFarmerData:', error);
      document.getElementById('loading-overlay').classList.add('hidden');
    }
  }
  
  // Refresh data
  function refreshData() {
    try {
      console.log('Refreshing data');
      // Show loading overlay
      document.getElementById('loading-overlay').classList.remove('hidden');
      
      // Simulate API call delay
      setTimeout(() => {
        try {
          // If we have values, recalculate financial index
          if (document.getElementById('ph_level').value) {
            calculateFinancialIndex();
          }
          
          // Hide loading overlay
          document.getElementById('loading-overlay').classList.add('hidden');
          
          // Update last update time
          updateLastUpdateTime();
          
          // Show toast notification
          showToast('Data refreshed successfully', 'success');
        } catch (error) {
          console.error('Error refreshing data:', error);
          document.getElementById('loading-overlay').classList.add('hidden');
          showToast('Error refreshing data', 'error');
        }
      }, 1000);
    } catch (error) {
      console.error('Error in refreshData:', error);
      document.getElementById('loading-overlay').classList.add('hidden');
    }
  }
  
  // Update last update time
  function updateLastUpdateTime() {
    try {
      const now = new Date();
      const timeString = now.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit'
      });
      document.getElementById('last-update-time').textContent = timeString;
    } catch (error) {
      console.error('Error updating last update time:', error);
    }
  }
  
  // Helper function to show toast notifications
  function showToast(message, type = 'info') {
    try {
      console.log(`Toast notification: ${message} (${type})`);
      Toastify({
        text: message,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "right",
        backgroundColor: type === 'success' ? "#4CAF50" : type === 'error' ? "#F44336" : "#2196F3",
      }).showToast();
    } catch (error) {
      console.error('Error showing toast notification:', error);
      // Fallback alert if toast fails
      alert(message);
    }
  }