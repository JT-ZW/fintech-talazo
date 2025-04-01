// static/js/ai_recommendations.js - Enhanced version
class AIRecommendationManager {
  constructor() {
      this.apiEndpoint = '/api/soil/ai-recommendations';
      this.loadingElement = document.getElementById('ai-recommendations-loading');
      this.contentElement = document.getElementById('ai-recommendations-content');
      this.generateButton = document.getElementById('generate-recommendations-btn');
      this.recommendations = [];
      this.lastGeneratedTime = null;
      
      this.init();
  }
  
  init() {
      console.log('Initializing AI Recommendation Manager...');
      
      if (this.generateButton) {
          this.generateButton.addEventListener('click', () => this.generateRecommendations());
      }
      
      // Add print and share functionality
      this.setupActionButtons();
      
      // Check if we should auto-generate recommendations
      if (this.contentElement && this.contentElement.children.length === 0) {
          // Auto-generate after a brief delay to let the dashboard load
          setTimeout(() => {
              // Only auto-generate if we haven't already done so
              if (!this.lastGeneratedTime) {
                  this.generateRecommendations();
              }
          }, 2000);
      }
  }
  
  setupActionButtons() {
      // Setup action buttons in the card header if they exist
      const printButton = document.querySelector('.ai-recommendations .fa-print');
      if (printButton && printButton.parentElement) {
          printButton.parentElement.addEventListener('click', () => this.printRecommendations());
      }
      
      const shareButton = document.querySelector('.ai-recommendations .fa-share-alt');
      if (shareButton && shareButton.parentElement) {
          shareButton.parentElement.addEventListener('click', () => this.shareRecommendations());
      }
  }
  
  async generateRecommendations() {
      // Show loading state
      this.showLoading();
      
      try {
          // Get current soil data from dashboard if available
          let soilData = {};
          let region = 'Zimbabwe';
          let crop = 'Maize';
          
          // Try to get soil data from dashboard
          if (window.dashboardManager && window.dashboardManager.currentSoilData) {
              soilData = window.dashboardManager.currentSoilData;
          } else {
              // If dashboard data is not available, create sample data
              soilData = this.createSampleSoilData();
          }
          
          // Get farmer selection if available
          const farmerSelector = document.getElementById('farmer-selector');
          if (farmerSelector && farmerSelector.selectedOptions && farmerSelector.selectedOptions.length > 0) {
              const farmerText = farmerSelector.selectedOptions[0].text;
              if (farmerText.includes('(')) {
                  region = farmerText.split('(')[1].replace(')', '').trim();
              }
          }
          
          // Try to get API data
          let data;
          try {
              // Make API request
              const response = await fetch(this.apiEndpoint, {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json'
                  },
                  body: JSON.stringify({
                      soil_data: soilData,
                      region: region,
                      crop: crop,
                      farmer_info: {
                          primary_crop: crop,
                          farm_size: 2.5
                      }
                  })
              });
              
              if (!response.ok) {
                  throw new Error(`API request failed with status ${response.status}`);
              }
              
              data = await response.json();
              
          } catch (error) {
              console.warn('API request failed, using fallback recommendations', error);
              // Use fallback recommendations
              data = this.getFallbackRecommendations(soilData, region, crop);
          }
          
          this.recommendations = data.recommendations || [];
          this.lastGeneratedTime = new Date();
          this.displayRecommendations(data);
          
      } catch (error) {
          console.error('Error generating AI recommendations:', error);
          this.showError('Failed to generate recommendations. Using fallback recommendations instead.');
          
          // Use fallback in case of errors
          const data = this.getFallbackRecommendations(this.createSampleSoilData(), 'Zimbabwe', 'Maize');
          this.recommendations = data.recommendations || [];
          this.displayRecommendations(data);
      } finally {
          this.hideLoading();
      }
  }
  
  createSampleSoilData() {
      // Create sample soil data if none is available
      return {
          ph_level: 6.2,
          nitrogen_level: 25,
          phosphorus_level: 18,
          potassium_level: 180,
          organic_matter: 3.5,
          cation_exchange_capacity: 14,
          moisture_content: 22
      };
  }
  
  getFallbackRecommendations(soilData, region, crop) {
      // Generate reasonable recommendations based on soil data
      const recommendations = [];
      
      // Check pH level
      if (soilData.ph_level < 6.0) {
          recommendations.push({
              title: 'Correct Soil pH',
              action: `Apply agricultural lime at ${Math.round((6.5 - soilData.ph_level) * 2)} tons per hectare`,
              reason: 'Soil is too acidic, which limits nutrient availability',
              cost_estimate: 'Medium',
              timeframe: '3-6 months',
              local_context: 'Locally available agricultural lime can be sourced from most agricultural supply stores in Zimbabwe'
          });
      } else if (soilData.ph_level > 7.0) {
          recommendations.push({
              title: 'Reduce Soil pH',
              action: 'Apply organic matter such as compost or manure',
              reason: 'Soil is too alkaline, which can limit certain nutrient uptake',
              cost_estimate: 'Low to Medium',
              timeframe: '3-6 months',
              local_context: 'Manure from local livestock can be an affordable option'
          });
      }
      
      // Check nitrogen level
      if (soilData.nitrogen_level < 20) {
          recommendations.push({
              title: 'Increase Nitrogen Levels',
              action: `Apply nitrogen fertilizer (Ammonium Nitrate) at ${Math.round(150 - soilData.nitrogen_level * 5)} kg/ha`,
              reason: 'Nitrogen deficiency will limit plant growth and yield',
              cost_estimate: 'Medium',
              timeframe: '2-4 weeks',
              local_context: 'Consider split application during the growing season for better efficiency in Zimbabwe\'s climate'
          });
      }
      
      // Check organic matter
      if (soilData.organic_matter < 3.0) {
          recommendations.push({
              title: 'Increase Organic Matter',
              action: 'Apply compost or incorporate crop residues into the soil',
              reason: 'Low organic matter reduces soil structure, water retention, and nutrient availability',
              cost_estimate: 'Low',
              timeframe: '6-12 months for full benefits',
              local_context: 'Conservation agriculture techniques are promoted in Zimbabwe to build organic matter over time'
          });
      }
      
      // Check moisture content
      if (soilData.moisture_content < 20) {
          recommendations.push({
              title: 'Improve Water Management',
              action: 'Apply mulch and implement water conservation practices like tied ridges or basins',
              reason: 'Low soil moisture will stress plants and reduce yields',
              cost_estimate: 'Low to Medium',
              timeframe: 'Immediate benefits',
              local_context: 'Critical for rainfed agriculture in Zimbabwe\'s drought-prone regions'
          });
      }
      
      return {
          status: 'success',
          recommendations: recommendations,
          metadata: {
              source: 'fallback',
              request_context: {
                  region: region,
                  crop: crop
              },
              timestamp: new Date().toISOString()
          }
      };
  }
  
  displayRecommendations(data) {
      if (!data.recommendations || data.status === 'error') {
          this.showError(data.error || 'An error occurred generating recommendations');
          return;
      }
      
      // Clear previous content
      this.contentElement.innerHTML = '';
      
      // Create recommendations UI
      const recommendations = data.recommendations || [];
      
      if (recommendations.length === 0) {
          this.contentElement.innerHTML = `
              <div class="empty-state">
                  <i class="fas fa-robot"></i>
                  <p>No specific recommendations available for the current soil conditions.</p>
              </div>
          `;
          this.contentElement.classList.remove('hidden');
          return;
      }
      
      // Add header with metadata
      const header = document.createElement('div');
      header.className = 'ai-recommendations-header';
      header.innerHTML = `
          <div class="metadata">
              <div class="meta-item">
                  <span class="label">Generated:</span>
                  <span class="value">${new Date().toLocaleString()}</span>
              </div>
              <div class="meta-item">
                  <span class="label">Region:</span>
                  <span class="value">${data.metadata?.request_context?.region || 'Zimbabwe'}</span>
              </div>
              <div class="meta-item">
                  <span class="label">Crop:</span>
                  <span class="value">${data.metadata?.request_context?.crop || 'General'}</span>
              </div>
          </div>
      `;
      this.contentElement.appendChild(header);
      
      // Create recommendation cards
      const recList = document.createElement('div');
      recList.className = 'recommendation-list';
      
      recommendations.forEach((rec, index) => {
          const card = this.createRecommendationCard(rec, index + 1);
          recList.appendChild(card);
      });
      
      this.contentElement.appendChild(recList);
      
      // Show the content
      this.contentElement.classList.remove('hidden');
  }
  
  createRecommendationCard(recommendation, index) {
      const card = document.createElement('div');
      card.className = 'recommendation-card';
      card.setAttribute('data-rec-id', `ai-rec-${index}`);
      
      // Extract recommendation details
      const title = recommendation.title || 'Soil Improvement Recommendation';
      const action = recommendation.action || '';
      const reason = recommendation.reason || '';
      const costEstimate = recommendation.cost_estimate || 'Unknown';
      const timeframe = recommendation.timeframe || '';
      const localContext = recommendation.local_context || '';
      
      // Build card content
      let cardContent = `
          <div class="recommendation-header">
              <div class="recommendation-number">${index}</div>
              <h3>${title}</h3>
          </div>
          <div class="recommendation-body">
      `;
      
      // Add recommendation details
      if (action) {
          cardContent += `<p class="recommendation-action"><strong>Action:</strong> ${action}</p>`;
      }
      
      if (reason) {
          cardContent += `<p><strong>Why:</strong> ${reason}</p>`;
      }
      
      if (costEstimate) {
          cardContent += `<p><strong>Estimated Cost:</strong> <span class="cost-tag ${this.getCostClass(costEstimate)}">${costEstimate}</span></p>`;
      }
      
      if (timeframe) {
          cardContent += `<p><strong>Timeframe:</strong> ${timeframe}</p>`;
      }
      
      if (localContext) {
          cardContent += `<div class="local-context"><strong>Local Considerations:</strong> ${localContext}</div>`;
      }
      
      cardContent += `
          </div>
          <div class="recommendation-footer">
              <button class="btn btn-sm implement-btn">Implement</button>
              <button class="btn btn-sm btn-outline save-btn">Save for Later</button>
          </div>
      `;
      
      card.innerHTML = cardContent;
      
      // Add event listeners
      card.querySelector('.implement-btn').addEventListener('click', () => this.implementRecommendation(index));
      card.querySelector('.save-btn').addEventListener('click', () => this.saveRecommendation(index));
      
      return card;
  }
  
  implementRecommendation(index) {
      if (index >= this.recommendations.length) return;
      
      const recommendation = this.recommendations[index];
      console.log('Implementing recommendation:', recommendation);
      
      // Show confirmation notification
      if (window.dashboardManager) {
          window.dashboardManager.showNotification(`Implementing "${recommendation.title || 'recommendation'}"`, 'success');
      }
      
      // Update card to show implemented status
      const card = document.querySelector(`[data-rec-id="ai-rec-${index}"]`);
      if (card) {
          card.classList.add('implemented');
          card.querySelector('.recommendation-footer').innerHTML = `
              <div class="implemented-status">
                  <i class="fas fa-check-circle"></i> Implementation in progress
              </div>
          `;
      }
  }
  
  saveRecommendation(index) {
      if (index >= this.recommendations.length) return;
      
      const recommendation = this.recommendations[index];
      console.log('Saving recommendation:', recommendation);
      
      // Show confirmation notification
      if (window.dashboardManager) {
          window.dashboardManager.showNotification(`Saved "${recommendation.title || 'recommendation'}" for later`, 'default');
      }
      
      // Update button to show saved status
      const card = document.querySelector(`[data-rec-id="ai-rec-${index}"]`);
      if (card) {
          const saveBtn = card.querySelector('.save-btn');
          if (saveBtn) {
              saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved';
              saveBtn.classList.add('saved');
              saveBtn.disabled = true;
          }
      }
  }
  
  printRecommendations() {
      if (this.recommendations.length === 0) {
          if (window.dashboardManager) {
              window.dashboardManager.showNotification('No recommendations to print', 'warning');
          }
          return;
      }
      
      // Create a printable version
      const printWindow = window.open('', '_blank', 'width=800,height=600');
      if (!printWindow) {
          alert('Please allow pop-ups to print recommendations');
          return;
      }
      
      const html = `
          <!DOCTYPE html>
          <html>
          <head>
              <title>Talazo AgriFinance - AI Recommendations</title>
              <style>
                  body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
                  h1 { color: #1E8449; }
                  .recommendation { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; page-break-inside: avoid; }
                  .recommendation h3 { margin-top: 0; color: #1E8449; }
                  .metadata { margin-bottom: 20px; color: #666; font-size: 0.9em; }
                  .footer { margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }
              </style>
          </head>
          <body>
              <h1>Talazo AgriFinance - AI Recommendations</h1>
              <div class="metadata">
                  <p>Generated: ${new Date().toLocaleString()}</p>
                  <p>Soil Health Index: ${document.getElementById('financial-gauge')?.querySelector('.label')?.textContent || 'N/A'}</p>
              </div>
              
              ${this.recommendations.map((rec, index) => `
                  <div class="recommendation">
                      <h3>${index + 1}. ${rec.title || 'Soil Improvement'}</h3>
                      ${rec.action ? `<p><strong>Action:</strong> ${rec.action}</p>` : ''}
                      ${rec.reason ? `<p><strong>Why:</strong> ${rec.reason}</p>` : ''}
                      ${rec.cost_estimate ? `<p><strong>Cost Estimate:</strong> ${rec.cost_estimate}</p>` : ''}
                      ${rec.timeframe ? `<p><strong>Timeframe:</strong> ${rec.timeframe}</p>` : ''}
                      ${rec.local_context ? `<p><strong>Local Context:</strong> ${rec.local_context}</p>` : ''}
                  </div>
              `).join('')}
              
              <div class="footer">
                  <p>Talazo AgriFinance Platform © ${new Date().getFullYear()}</p>
                  <p>Soil-based financial analytics for Zimbabwean farmers</p>
              </div>
          </body>
          </html>
      `;
      
      printWindow.document.write(html);
      printWindow.document.close();
      
      // Trigger print after content is loaded
      printWindow.addEventListener('load', () => {
          printWindow.print();
      });
  }
  
  shareRecommendations() {
      if (this.recommendations.length === 0) {
          if (window.dashboardManager) {
              window.dashboardManager.showNotification('No recommendations to share', 'warning');
          }
          return;
      }
      
      // Show sharing options (simplified for prototype)
      const options = ['Email', 'WhatsApp', 'SMS', 'Download PDF'];
      
      // Create a simple popup for sharing options
      const popup = document.createElement('div');
      popup.className = 'share-popup';
      popup.innerHTML = `
          <div class="share-popup-content">
              <h3>Share Recommendations</h3>
              <div class="share-options">
                  ${options.map(option => `
                      <button class="share-option" data-option="${option.toLowerCase()}">
                          <i class="fas fa-${option === 'Email' ? 'envelope' : option === 'WhatsApp' ? 'whatsapp' : option === 'SMS' ? 'sms' : 'file-pdf'}"></i>
                          ${option}
                      </button>
                  `).join('')}
              </div>
              <button class="close-popup"><i class="fas fa-times"></i></button>
          </div>
      `;
      
      document.body.appendChild(popup);
      
      // Add event listeners
      popup.querySelector('.close-popup').addEventListener('click', () => {
          popup.remove();
      });
      
      popup.querySelectorAll('.share-option').forEach(button => {
          button.addEventListener('click', () => {
              const option = button.dataset.option;
              popup.remove();
              
              if (window.dashboardManager) {
                  window.dashboardManager.showNotification(`Sharing via ${option} will be available in the next update`, 'default');
              }
          });
      });
  }
  
  getCostClass(costEstimate) {
      const cost = costEstimate.toLowerCase();
      if (cost.includes('low')) return 'cost-low';
      if (cost.includes('medium')) return 'cost-medium';
      if (cost.includes('high')) return 'cost-high';
      return '';
  }
  
  showLoading() {
      if (this.loadingElement) {
          this.loadingElement.classList.remove('hidden');
      }
      
      if (this.contentElement) {
          this.contentElement.classList.add('hidden');
      }
      
      if (this.generateButton) {
          this.generateButton.disabled = true;
      }
  }
  
  hideLoading() {
      if (this.loadingElement) {
          this.loadingElement.classList.add('hidden');
      }
      
      if (this.generateButton) {
          this.generateButton.disabled = false;
      }
  }
  
  showError(message) {
      if (this.contentElement) {
          this.contentElement.innerHTML = `
              <div class="error-message">
                  <i class="fas fa-exclamation-triangle"></i>
                  <p>${message}</p>
                  <p>Please try again or use our basic recommendations instead.</p>
              </div>
          `;
          this.contentElement.classList.remove('hidden');
      }
  }
}

// Initialize AI recommendations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('Initializing AI Recommendation Manager...');
  window.aiRecommendationManager = new AIRecommendationManager();
});