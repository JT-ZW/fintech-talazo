// insurance.js - Functionality for the insurance premium calculator

document.addEventListener('DOMContentLoaded', function() {
    // Initialize modules
    initializePage();
    setupEventListeners();
    initializeGauges();
    initializeCharts();
    
    // Set today's date as default for the policy start date
    const today = new Date();
    document.getElementById('policy-start-date').valueAsDate = today;
    
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
    // Set initial values for coverage fields
    document.getElementById('base-coverage').textContent = '1,000';
    
    // Initialize other components as needed
    console.log('Insurance page initialized');
  }
  
  // Set up event listeners for all interactive elements
  function setupEventListeners() {
    // Form submission
    document.getElementById('soil-metrics-form').addEventListener('submit', function(e) {
      e.preventDefault();
      try {
        calculatePremium();
      } catch (error) {
        console.error('Error during premium calculation:', error);
        document.getElementById('loading-overlay').classList.add('hidden');
        showToast('Error calculating premium. Please try again.', 'error');
      }
    });
    
    // Sample data loading
    document.getElementById('load-sample-data').addEventListener('click', loadSampleData);
    
    // Form clearing
    document.getElementById('clear-form').addEventListener('click', clearForm);
    
    // Policy tab switching
    document.querySelectorAll('.policy-tab').forEach(tab => {
      tab.addEventListener('click', function() {
        switchPolicyTab(this.getAttribute('data-plan'));
      });
    });
    
    // Plan selection
    document.querySelectorAll('.select-plan').forEach(button => {
      button.addEventListener('click', function() {
        selectPlan(this.getAttribute('data-plan'));
      });
    });
    
    // Modal functionality
    document.querySelector('.close-modal').addEventListener('click', closeModal);
    document.querySelector('.close-modal-btn').addEventListener('click', closeModal);
    
    // Plan confirmation
    document.getElementById('confirm-plan').addEventListener('click', confirmPlan);
    
    // Coverage area changes
    document.getElementById('coverage-area').addEventListener('input', updateTotalPremium);
    
    // Generate more recommendations
    document.getElementById('generate-more-recommendations').addEventListener('click', generateMoreRecommendations);
    
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
  
  // Initialize gauge charts
  function initializeGauges() {
    const gaugeElement = document.getElementById('soil-health-gauge');
    if (gaugeElement) {
      try {
        GaugeChart.gaugeChart(gaugeElement, {
          hasNeedle: true,
          needleColor: "#464A4F",
          arcColors: ["#F44336", "#FFC107", "#4CAF50"],
          arcDelimiters: [40, 60],
          rangeLabel: ["0", "100"],
          centralLabel: "0",
        });
      } catch (error) {
        console.error('Error initializing gauge:', error);
      }
    }
  }
  
  // Initialize charts for premium factors and impact
  function initializeCharts() {
    try {
      // Premium factors chart (initial empty state)
      const factorsCtx = document.getElementById('factors-chart');
      if (factorsCtx) {
        window.factorsChart = new Chart(factorsCtx, {
          type: 'bar',
          data: {
            labels: ['pH Level', 'Nitrogen', 'Phosphorus', 'Potassium', 'Organic Matter', 'CEC', 'Moisture'],
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
      
      // Intervention impact chart (initial empty state)
      const impactCtx = document.getElementById('impact-chart');
      if (impactCtx) {
        window.impactChart = new Chart(impactCtx, {
          type: 'line',
          data: {
            labels: ['Current', 'After 1 Mo', 'After 3 Mo', 'After 6 Mo', 'After 12 Mo'],
            datasets: [{
              label: 'Premium Amount',
              data: [0, 0, 0, 0, 0],
              borderColor: 'rgba(255, 99, 132, 1)',
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `$${context.raw.toFixed(2)}`;
                  }
                }
              }
            },
            scales: {
              y: {
                title: {
                  display: true,
                  text: 'Premium ($)'
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
  
  // Load sample data into the form
  function loadSampleData() {
    document.getElementById('ph_level').value = '6.2';
    document.getElementById('nitrogen_level').value = '25.3';
    document.getElementById('phosphorus_level').value = '18.7';
    document.getElementById('potassium_level').value = '185.0';
    document.getElementById('organic_matter').value = '3.8';
    document.getElementById('cation_exchange_capacity').value = '14.5';
    document.getElementById('moisture_content').value = '22.6';
    document.getElementById('region').value = 'mashonaland_central';
    
    // Show toast notification
    showToast('Sample data loaded', 'success');
  }
  
  // Clear the form
  function clearForm() {
    document.getElementById('soil-metrics-form').reset();
    
    // Clear results
    document.getElementById('soil-health-score').textContent = '--';
    document.getElementById('premium-amount').textContent = '--';
    document.getElementById('risk-level').textContent = '--';
    document.getElementById('drought-protection').textContent = '--';
    document.getElementById('pest-disease').textContent = '--';
    document.getElementById('current-premium').textContent = '--';
    document.getElementById('potential-savings').textContent = '--';
    
    // Reset charts
    resetCharts();
    
    // Clear recommendations
    document.getElementById('recommendations-list').innerHTML = `
      <div class="loading-recommendations">
        <div class="spinner"></div>
        <p>Enter soil metrics to generate personalized recommendations</p>
      </div>
    `;
    
    // Reset policy prices
    document.getElementById('basic-plan-price').textContent = '--';
    document.getElementById('standard-plan-price').textContent = '--';
    document.getElementById('premium-plan-price').textContent = '--';
    
    // Reset gauge
    try {
      GaugeChart.gaugeChart(document.getElementById('soil-health-gauge'), {
        hasNeedle: true,
        needleColor: "#464A4F",
        arcColors: ["#F44336", "#FFC107", "#4CAF50"],
        arcDelimiters: [40, 60],
        rangeLabel: ["0", "100"],
        centralLabel: "0",
      });
    } catch (error) {
      console.error('Error resetting gauge:', error);
    }
    
    // Show toast notification
    showToast('Form cleared', 'info');
  }
  
  // Calculate premium based on soil metrics
  function calculatePremium() {
    console.log('Starting premium calculation...');
    // Show loading overlay
    document.getElementById('loading-overlay').classList.remove('hidden');
    
    try {
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
      
      // Calculate soil health score using soil health algorithm
      const { overallScore, parameterScores, riskLevel } = calculateSoilHealthScore(soilData);
      console.log('Soil health calculation complete:', { overallScore, riskLevel });
      
      // Calculate premium based on soil health score
      const premium = calculatePremiumAmount(overallScore);
      console.log('Premium calculated:', premium);
      
      // Update display
      updateResults(overallScore, premium, parameterScores, riskLevel);
      console.log('Results updated');
      
      // Generate recommendations
      generateRecommendations(soilData, overallScore, premium);
      console.log('Recommendations generated');
      
      // Update policy prices
      updatePolicyPrices(premium);
      console.log('Policy prices updated');
      
      // Hide loading overlay
      document.getElementById('loading-overlay').classList.add('hidden');
      
      // Show toast notification
      showToast('Premium calculated successfully', 'success');
      
      // Update last update time
      updateLastUpdateTime();
    } catch (error) {
      console.error('Error in calculate premium:', error);
      // Hide loading overlay in case of error
      document.getElementById('loading-overlay').classList.add('hidden');
      showToast('Error calculating premium. Check console for details.', 'error');
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
  
  // Calculate premium amount based on soil health score
  function calculatePremiumAmount(healthScore) {
    console.log('Calculating premium for health score:', healthScore);
    
    // Base premium amount (for a perfect score)
    const basePremium = 100;
    
    // Calculate risk factor (higher health score = lower risk)
    const riskFactor = (100 - healthScore) / 100;
    
    // Apply non-linear relationship for more realistic premiums
    const premiumMultiplier = 1 + (riskFactor ** 1.8);
    
    // Calculate premium
    let premium = basePremium * premiumMultiplier;
    
    // Apply min/max bounds for premiums
    const minPremium = basePremium * 0.8;  // Minimum discount of 20%
    const maxPremium = basePremium * 3.0;  // Maximum increase of 200%
    
    premium = Math.max(minPremium, Math.min(maxPremium, premium));
    
    return Math.round(premium * 100) / 100;  // Round to 2 decimal places
  }
  
  // Update the results display
  function updateResults(healthScore, premium, parameterScores, riskLevel) {
    try {
      console.log('Updating results with:', { healthScore, premium, riskLevel });
      
      // Update soil health score and gauge
      document.getElementById('soil-health-score').textContent = healthScore.toFixed(1);
      
      // Update gauge
      GaugeChart.gaugeChart(document.getElementById('soil-health-gauge'), {
        hasNeedle: true,
        needleColor: "#464A4F",
        arcColors: ["#F44336", "#FFC107", "#4CAF50"],
        arcDelimiters: [40, 60],
        rangeLabel: ["0", "100"],
        centralLabel: healthScore.toFixed(0),
        needleValue: healthScore
      });
      
      // Update premium amount
      document.getElementById('premium-amount').textContent = premium.toFixed(2);
      
      // Update risk level
      document.getElementById('risk-level').textContent = riskLevel;
      
      // Update coverage details based on risk level
      if (riskLevel.includes("Low")) {
        document.getElementById('drought-protection').textContent = "Included";
        document.getElementById('pest-disease').textContent = "Included";
      } else if (riskLevel.includes("Medium")) {
        document.getElementById('drought-protection').textContent = "Included";
        document.getElementById('pest-disease').textContent = "Optional (+15%)";
      } else {
        document.getElementById('drought-protection').textContent = "Limited";
        document.getElementById('pest-disease').textContent = "Optional (+25%)";
      }
      
      // Update comparison values
      const marketRate = 175;
      document.getElementById('current-premium').textContent = premium.toFixed(2);
      const savings = marketRate - premium;
      document.getElementById('potential-savings').textContent = savings > 0 ? savings.toFixed(2) : "0.00";
      
      // Update the factors chart
      updateFactorsChart(parameterScores);
    } catch (error) {
      console.error('Error in updateResults:', error);
      throw error;
    }
  }
  
  // Update the factors chart with parameter scores
  function updateFactorsChart(parameterScores) {
    try {
      console.log('Updating factors chart with:', parameterScores);
      if (!window.factorsChart) {
        console.warn('Factors chart not initialized');
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
      
      window.factorsChart.data.datasets[0].data = chartData;
      window.factorsChart.update();
    } catch (error) {
      console.error('Error updating factors chart:', error);
    }
  }
  
  // Reset all charts to default state
  function resetCharts() {
    try {
      if (window.factorsChart) {
        window.factorsChart.data.datasets[0].data = [0, 0, 0, 0, 0, 0, 0];
        window.factorsChart.update();
      }
      
      if (window.impactChart) {
        window.impactChart.data.datasets[0].data = [0, 0, 0, 0, 0];
        window.impactChart.update();
      }
    } catch (error) {
      console.error('Error resetting charts:', error);
    }
  }
  
  // Generate recommendations based on soil data
  function generateRecommendations(soilData, healthScore, premium) {
    try {
      console.log('Generating recommendations for:', soilData);
      
      // Clear the recommendations container
      const recommendationsContainer = document.getElementById('recommendations-list');
      recommendationsContainer.innerHTML = `
        <div class="loading-recommendations">
          <div class="spinner"></div>
          <p>Generating personalized recommendations...</p>
        </div>
      `;
      
      // Simulate API call delay
      setTimeout(() => {
        try {
          // Generate recommendations based on soil parameters
          const recommendations = [];
          const problemParams = [];
          
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
          
          // Check each parameter against ideal range
          for (const [param, value] of Object.entries(soilData)) {
            if (param === 'region' || value === 0) continue;
            
            const [minIdeal, maxIdeal] = idealRanges[param] || [0, 0];
            
            // If parameter is outside ideal range, add recommendation
            if (value < minIdeal || value > maxIdeal) {
              problemParams.push({ param, value, minIdeal, maxIdeal });
            }
          }
          
          // Sort problems by severity (distance from ideal range)
          problemParams.sort((a, b) => {
            const aDeviation = Math.min(Math.abs(a.value - a.minIdeal), Math.abs(a.value - a.maxIdeal));
            const bDeviation = Math.min(Math.abs(b.value - b.minIdeal), Math.abs(b.value - b.maxIdeal));
            return bDeviation - aDeviation;
          });
          
          // Generate recommendations for top problems
          for (const problem of problemParams.slice(0, 3)) {
            recommendations.push(generateRecommendationForParameter(problem));
          }
          
          // Add a general recommendation if we have less than 3
          if (recommendations.length < 3) {
            recommendations.push({
              title: "Implement Crop Rotation Plan",
              content: "Rotate crops strategically to balance soil nutrient utilization and break pest cycles.",
              impact: "medium",
              costEstimate: "Low",
              timeframe: "Next planting season",
              reduction: 7
            });
          }
          
          console.log('Generated recommendations:', recommendations);
          
          // Display recommendations
          displayRecommendations(recommendations, premium);
          
          // Update potential premium reduction
          const totalReduction = recommendations.reduce((sum, rec) => sum + rec.reduction, 0);
          const potentialReduction = Math.min(totalReduction, 40); // Cap at 40%
          
          document.getElementById('potential-reduction-percentage').textContent = potentialReduction.toFixed(0);
          document.getElementById('potential-reduction-amount').textContent = ((premium * potentialReduction) / 100).toFixed(2);
          
          // Update impact chart
          updateImpactChart(premium, recommendations);
        } catch (error) {
          console.error('Error in recommendation generation:', error);
          recommendationsContainer.innerHTML = '<p>Error generating recommendations. Please try again.</p>';
        }
      }, 1000);
    } catch (error) {
      console.error('Error in generateRecommendations:', error);
      throw error;
    }
  }
  
  // Generate a recommendation for a specific soil parameter
  function generateRecommendationForParameter(problem) {
    try {
      console.log('Generating recommendation for problem:', problem);
      const { param, value, minIdeal, maxIdeal } = problem;
      
      // Define recommendation templates for different parameters
      const recommendations = {
        ph_level: {
          low: {
            title: "Increase Soil pH Level",
            content: `Apply agricultural lime at ${2 + Math.max(0, (minIdeal - value) * 2).toFixed(1)}-${4 + Math.max(0, (minIdeal - value) * 3).toFixed(1)} tons/ha to raise pH from ${value.toFixed(1)} towards the ideal range of ${minIdeal.toFixed(1)}-${maxIdeal.toFixed(1)}.`,
            impact: "high",
            costEstimate: "Medium",
            timeframe: "3-6 months",
            reduction: 15
          },
          high: {
            title: "Decrease Soil pH Level",
            content: `Apply elemental sulfur at ${Math.max(0, (value - maxIdeal) * 300).toFixed(0)}-${Math.max(0, (value - maxIdeal) * 500).toFixed(0)} kg/ha to lower pH from ${value.toFixed(1)} towards the ideal range of ${minIdeal.toFixed(1)}-${maxIdeal.toFixed(1)}.`,
            impact: "high",
            costEstimate: "Medium",
            timeframe: "3-6 months",
            reduction: 15
          }
        },
        nitrogen_level: {
          low: {
            title: "Increase Nitrogen Levels",
            content: `Apply nitrogen fertilizer (like ammonium nitrate) at ${100 + Math.max(0, (minIdeal - value) * 5).toFixed(0)}-${150 + Math.max(0, (minIdeal - value) * 10).toFixed(0)} kg/ha to boost levels from ${value.toFixed(1)} mg/kg.`,
            impact: "high",
            costEstimate: "Medium",
            timeframe: "2-4 weeks",
            reduction: 12
          },
          high: {
            title: "Reduce Nitrogen Application",
            content: `Decrease nitrogen fertilizer application and consider planting legumes as cover crops to naturally regulate nitrogen from current ${value.toFixed(1)} mg/kg.`,
            impact: "medium",
            costEstimate: "Low",
            timeframe: "Next planting season",
            reduction: 8
          }
        },
        phosphorus_level: {
          low: {
            title: "Increase Phosphorus Levels",
            content: `Apply phosphate fertilizer (like triple superphosphate) at ${60 + Math.max(0, (minIdeal - value) * 3).toFixed(0)}-${100 + Math.max(0, (minIdeal - value) * 5).toFixed(0)} kg/ha to improve levels from ${value.toFixed(1)} mg/kg.`,
            impact: "high",
            costEstimate: "Medium",
            timeframe: "Before planting",
            reduction: 10
          },
          high: {
            title: "Reduce Phosphorus Application",
            content: `Decrease phosphate fertilizer use in upcoming seasons to bring levels from ${value.toFixed(1)} mg/kg down to the ideal range.`,
            impact: "medium",
            costEstimate: "Low",
            timeframe: "Next planting season",
            reduction: 6
          }
        },
        potassium_level: {
          low: {
            title: "Increase Potassium Levels",
            content: `Apply potassium fertilizer (like muriate of potash) at ${50 + Math.max(0, (minIdeal - value) * 0.2).toFixed(0)}-${100 + Math.max(0, (minIdeal - value) * 0.3).toFixed(0)} kg/ha to improve from ${value.toFixed(1)} mg/kg.`,
            impact: "high",
            costEstimate: "Medium",
            timeframe: "Before planting",
            reduction: 12
          },
          high: {
            title: "Adjust Potassium Levels",
            content: `Reduce potassium fertilizer application in future seasons and consider crops that utilize more potassium to bring levels down from ${value.toFixed(1)} mg/kg.`,
            impact: "low",
            costEstimate: "Low",
            timeframe: "Next planting season",
            reduction: 5
          }
        },
        organic_matter: {
          low: {
            title: "Increase Organic Matter",
            content: `Apply compost or manure at 5-10 tons per hectare and incorporate crop residues to improve from ${value.toFixed(1)}% to the ideal range.`,
            impact: "high",
            costEstimate: "Low-Medium",
            timeframe: "6-12 months",
            reduction: 18
          },
          high: {
            title: "Manage High Organic Matter",
            content: `Your organic matter content of ${value.toFixed(1)}% is above optimal range. This is generally beneficial but monitor nitrogen release.`,
            impact: "low",
            costEstimate: "Low",
            timeframe: "Ongoing",
            reduction: 3
          }
        },
        cation_exchange_capacity: {
          low: {
            title: "Improve Cation Exchange Capacity",
            content: `Increase organic matter and apply clay minerals if available to improve nutrient retention from current CEC of ${value.toFixed(1)} cmol/kg.`,
            impact: "medium",
            costEstimate: "Medium",
            timeframe: "1-2 years",
            reduction: 8
          },
          high: {
            title: "Manage High CEC",
            content: `Your soil's high CEC of ${value.toFixed(1)} cmol/kg indicates good nutrient retention. Focus on balanced fertilization.`,
            impact: "low",
            costEstimate: "Low",
            timeframe: "Ongoing",
            reduction: 3
          }
        },
        moisture_content: {
          low: {
            title: "Improve Soil Moisture Retention",
            content: `Apply mulch at 5-10 cm thickness and implement water conservation practices to improve from ${value.toFixed(1)}%.`,
            impact: "high",
            costEstimate: "Low-Medium",
            timeframe: "Immediate",
            reduction: 15
          },
          high: {
            title: "Improve Drainage",
            content: `Create drainage channels or raised beds to manage excess moisture of ${value.toFixed(1)}% and prevent waterlogging issues.`,
            impact: "medium",
            costEstimate: "Medium",
            timeframe: "Before rainy season",
            reduction: 10
          }
        }
      };
      
      // Determine if parameter is low or high compared to ideal range
      let type = 'low';
      if (value > maxIdeal) {
        type = 'high';
      }
      
      // Get recommendation for this parameter and type
      if (recommendations[param] && recommendations[param][type]) {
        return recommendations[param][type];
      }
      
      // Fallback recommendation if specific one isn't available
      return {
        title: `Optimize ${param.replace('_', ' ')}`,
        content: `Work towards bringing ${param.replace('_', ' ')} levels from ${value.toFixed(1)} to the ideal range of ${minIdeal.toFixed(1)}-${maxIdeal.toFixed(1)}.`,
        impact: "medium",
        costEstimate: "Medium",
        timeframe: "Varies",
        reduction: 5
      };
    } catch (error) {
      console.error('Error in generateRecommendationForParameter:', error);
      throw error;
    }
  }
  
  // Display recommendations in the UI
  function displayRecommendations(recommendations, premium) {
    try {
      console.log('Displaying recommendations:', recommendations);
      const container = document.getElementById('recommendations-list');
      container.innerHTML = '';
      
      if (recommendations.length === 0) {
        container.innerHTML = '<p>No specific recommendations are needed at this time. Your soil health is in good condition.</p>';
        return;
      }
      
      recommendations.forEach(rec => {
        const premiumReduction = ((premium * rec.reduction) / 100).toFixed(2);
        
        const html = `
          <div class="recommendation-item">
            <div class="recommendation-header">
              <div class="recommendation-title">${rec.title}</div>
              <div class="recommendation-impact ${rec.impact}">${rec.impact.charAt(0).toUpperCase() + rec.impact.slice(1)} Impact</div>
            </div>
            <div class="recommendation-content">${rec.content}</div>
            <div class="recommendation-details">
              <div class="recommendation-detail">
                <i class="fas fa-dollar-sign"></i> Cost: ${rec.costEstimate}
              </div>
              <div class="recommendation-detail">
                <i class="fas fa-clock"></i> Timeframe: ${rec.timeframe}
              </div>
              <div class="recommendation-detail">
                <i class="fas fa-chart-line"></i> Premium reduction: -${rec.reduction}% (${premiumReduction})
              </div>
            </div>
          </div>
        `;
        
        container.innerHTML += html;
      });
    } catch (error) {
      console.error('Error in displayRecommendations:', error);
      document.getElementById('recommendations-list').innerHTML = '<p>Error displaying recommendations. Please try again.</p>';
    }
  }
  
  // Update impact chart with projected premium reductions
  function updateImpactChart(premium, recommendations) {
    try {
      console.log('Updating impact chart with recommendations');
      if (!window.impactChart) {
        console.warn('Impact chart not initialized');
        return;
      }
      
      // Calculate cumulative reductions over time
      // Assuming implementations happen in order of recommendations
      const currentPremium = premium;
      
      // For simplicity, we'll assume these reductions happen over time
      // Month 1: First recommendation takes effect
      // Month 3: Second recommendation takes effect
      // Month 6: Third recommendation takes effect
      // Month 12: All recommendations fully implemented
      
      let oneMonthReduction = 0;
      let threeMonthReduction = 0;
      let sixMonthReduction = 0;
      let twelveMonthReduction = 0;
      
      if (recommendations.length > 0) {
        oneMonthReduction = recommendations[0].reduction / 2; // Partial effect
      }
      
      if (recommendations.length > 0) {
        threeMonthReduction = recommendations[0].reduction;
        if (recommendations.length > 1) {
          threeMonthReduction += recommendations[1].reduction / 2;
        }
      }
      
      if (recommendations.length > 0) {
        sixMonthReduction = recommendations[0].reduction;
        if (recommendations.length > 1) {
          sixMonthReduction += recommendations[1].reduction;
        }
        if (recommendations.length > 2) {
          sixMonthReduction += recommendations[2].reduction / 2;
        }
      }
      
      // Full implementation of all recommendations
      twelveMonthReduction = recommendations.reduce((sum, rec) => sum + rec.reduction, 0);
      
      // Cap reduction at 40%
      oneMonthReduction = Math.min(oneMonthReduction, 40);
      threeMonthReduction = Math.min(threeMonthReduction, 40);
      sixMonthReduction = Math.min(sixMonthReduction, 40);
      twelveMonthReduction = Math.min(twelveMonthReduction, 40);
      
      // Calculate premiums
      const oneMonthPremium = premium * (1 - oneMonthReduction / 100);
      const threeMonthPremium = premium * (1 - threeMonthReduction / 100);
      const sixMonthPremium = premium * (1 - sixMonthReduction / 100);
      const twelveMonthPremium = premium * (1 - twelveMonthReduction / 100);
      
      window.impactChart.data.datasets[0].data = [
        premium,
        oneMonthPremium,
        threeMonthPremium,
        sixMonthPremium,
        twelveMonthPremium
      ];
      
      window.impactChart.update();
    } catch (error) {
      console.error('Error updating impact chart:', error);
    }
  }
  
  // Update policy prices based on calculated premium
  function updatePolicyPrices(premium) {
    try {
      console.log('Updating policy prices with premium:', premium);
      // Basic plan: 100% of base premium
      document.getElementById('basic-plan-price').textContent = premium.toFixed(2);
      
      // Standard plan: 125% of base premium
      document.getElementById('standard-plan-price').textContent = (premium * 1.25).toFixed(2);
      
      // Premium plan: 150% of base premium
      document.getElementById('premium-plan-price').textContent = (premium * 1.5).toFixed(2);
    } catch (error) {
      console.error('Error updating policy prices:', error);
    }
  }
  
  // Switch between policy tabs
  function switchPolicyTab(plan) {
    try {
      console.log('Switching to policy tab:', plan);
      // Hide all plans first
      document.querySelectorAll('.policy-plan').forEach(planElement => {
        planElement.classList.add('hidden');
      });
      
      // Show selected plan
      document.getElementById(`${plan}-plan`).classList.remove('hidden');
      
      // Update active tab
      document.querySelectorAll('.policy-tab').forEach(tab => {
        tab.classList.remove('active');
      });
      document.querySelector(`.policy-tab[data-plan="${plan}"]`).classList.add('active');
    } catch (error) {
      console.error('Error switching policy tab:', error);
    }
  }
  
  // Show modal for plan selection
  function selectPlan(plan) {
    try {
      console.log('Selecting plan:', plan);
      const modal = document.getElementById('plan-modal');
      modal.style.display = 'block';
      
      // Set plan name
      let planName = 'Basic Protection Plan';
      if (plan === 'standard') {
        planName = 'Standard Protection Plan';
      } else if (plan === 'premium') {
        planName = 'Premium Protection Plan';
      }
      document.getElementById('selected-plan-name').textContent = planName;
      
      // Set premium amount
      let premium = parseFloat(document.getElementById(`${plan}-plan-price`).textContent);
      document.getElementById('modal-premium-amount').textContent = premium.toFixed(2);
      
      // Update total premium
      updateTotalPremium();
    } catch (error) {
      console.error('Error in selectPlan:', error);
    }
  }
  
  // Update total premium based on coverage area
  function updateTotalPremium() {
    try {
      console.log('Updating total premium');
      const premium = parseFloat(document.getElementById('modal-premium-amount').textContent);
      const area = parseFloat(document.getElementById('coverage-area').value) || 1;
      
      const total = premium * area;
      document.getElementById('total-premium').textContent = total.toFixed(2);
    } catch (error) {
      console.error('Error updating total premium:', error);
    }
  }
  
  // Close the modal
  function closeModal() {
    try {
      console.log('Closing modal');
      document.getElementById('plan-modal').style.display = 'none';
    } catch (error) {
      console.error('Error closing modal:', error);
    }
  }
  
  // Confirm policy selection
  function confirmPlan() {
    try {
      console.log('Confirming plan selection');
      // Get plan details
      const planName = document.getElementById('selected-plan-name').textContent;
      const premium = document.getElementById('modal-premium-amount').textContent;
      const area = document.getElementById('coverage-area').value;
      const total = document.getElementById('total-premium').textContent;
      const startDate = document.getElementById('policy-start-date').value;
      
      // Close modal
      closeModal();
      
      // Show confirmation message
      showToast(`${planName} selected successfully! Total premium: ${total}`, 'success');
      
      // In a real application, this would send data to the server
      console.log('Plan selected:', {
        planName,
        premium,
        area,
        total,
        startDate
      });
    } catch (error) {
      console.error('Error confirming plan:', error);
    }
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
            
            // Calculate premium automatically
            calculatePremium();
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
          // If we have values, recalculate premium
          if (document.getElementById('ph_level').value) {
            calculatePremium();
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
  
  // Generate more AI recommendations
  function generateMoreRecommendations() {
    try {
      console.log('Generating more recommendations');
      // Show loading state
      document.getElementById('recommendations-list').innerHTML = `
        <div class="loading-recommendations">
          <div class="spinner"></div>
          <p>Generating additional recommendations...</p>
        </div>
      `;
      
      // Simulate API call delay
      setTimeout(() => {
        try {
          // Add more general recommendations
          const additionalRecommendations = [
            {
              title: "Implement Crop Rotation Plan",
              content: "Rotate crops strategically to balance soil nutrient utilization and break pest cycles. Consider legumes to improve nitrogen fixation.",
              impact: "medium",
              costEstimate: "Low",
              timeframe: "Next planting season",
              reduction: 7
            },
            {
              title: "Adopt Conservation Tillage",
              content: "Reduce tillage intensity to minimize soil disturbance and erosion, while preserving soil structure and organic matter.",
              impact: "medium",
              costEstimate: "Medium",
              timeframe: "Next planting season",
              reduction: 8
            },
            {
              title: "Install Water Management System",
              content: "Implement contour ridges or tied ridges to maximize water utilization and reduce erosion during heavy rainfall events.",
              impact: "high",
              costEstimate: "Medium-High",
              timeframe: "Before rainy season",
              reduction: 12
            }
          ];
          
          // Get current premium
          const premium = parseFloat(document.getElementById('premium-amount').textContent) || 100;
          
          // Display recommendations
          displayRecommendations(additionalRecommendations, premium);
          
          // Update reduction potential
          const currentReduction = parseFloat(document.getElementById('potential-reduction-percentage').textContent) || 0;
          const additionalReduction = Math.min(
            additionalRecommendations.reduce((sum, rec) => sum + rec.reduction, 0),
            40 - currentReduction  // Cap at 40% total
          );
          
          const newTotalReduction = Math.min(currentReduction + additionalReduction, 40);
          
          document.getElementById('potential-reduction-percentage').textContent = newTotalReduction.toFixed(0);
          document.getElementById('potential-reduction-amount').textContent = ((premium * newTotalReduction) / 100).toFixed(2);
        } catch (error) {
          console.error('Error generating more recommendations:', error);
          document.getElementById('recommendations-list').innerHTML = '<p>Error generating additional recommendations. Please try again.</p>';
        }
      }, 1500);
    } catch (error) {
      console.error('Error in generateMoreRecommendations:', error);
    }
  }