function updateSoilHealthTab(farmer) {
    // Initialize the gauge
    const gaugeElement = document.getElementById('soil-health-gauge');
    if (gaugeElement) {
      GaugeChart.gaugeChart(gaugeElement, {
        hasNeedle: true,
        needleColor: "#464A4F",
        arcColors: ["#F44336", "#FFC107", "#4CAF50"],
        arcDelimiters: [40, 60],
        rangeLabel: ["0", "100"],
        centralLabel: farmer.financial_index.toString(),
        needleValue: farmer.financial_index
      });
    }
    
    // Update soil parameters
    if (farmer.soil_data) {
      // pH level
      document.getElementById('ph-level').textContent = farmer.soil_data.ph_level;
      setParameterFill('ph-fill', calculateParameterScore(farmer.soil_data.ph_level, 6.0, 7.0));
      
      // Nitrogen
      document.getElementById('nitrogen-level').textContent = `${farmer.soil_data.nitrogen_level} mg/kg`;
      setParameterFill('nitrogen-fill', calculateParameterScore(farmer.soil_data.nitrogen_level, 20.0, 40.0));
      
      // Phosphorus
      document.getElementById('phosphorus-level').textContent = `${farmer.soil_data.phosphorus_level} mg/kg`;
      setParameterFill('phosphorus-fill', calculateParameterScore(farmer.soil_data.phosphorus_level, 15.0, 30.0));
      
      // Potassium
      document.getElementById('potassium-level').textContent = `${farmer.soil_data.potassium_level} mg/kg`;
      setParameterFill('potassium-fill', calculateParameterScore(farmer.soil_data.potassium_level, 150.0, 250.0));
      
      // Organic Matter
      document.getElementById('organic-matter').textContent = `${farmer.soil_data.organic_matter}%`;
      setParameterFill('organic-matter-fill', calculateParameterScore(farmer.soil_data.organic_matter, 3.0, 5.0));
      
      // CEC
      document.getElementById('cec-level').textContent = `${farmer.soil_data.cation_exchange_capacity} cmol/kg`;
      setParameterFill('cec-fill', calculateParameterScore(farmer.soil_data.cation_exchange_capacity, 10.0, 20.0));
      
      // Moisture
      document.getElementById('moisture-level').textContent = `${farmer.soil_data.moisture_content}%`;
      setParameterFill('moisture-fill', calculateParameterScore(farmer.soil_data.moisture_content, 20.0, 30.0));
    }
  }
  
  // Calculate parameter score based on ideal range
  function calculateParameterScore(value, minIdeal, maxIdeal) {
    if (value >= minIdeal && value <= maxIdeal) {
      return 100; // Perfect score if within ideal range
    } else {
      // Calculate score based on distance from ideal range
      const deviation = value < minIdeal 
        ? (minIdeal - value) / minIdeal 
        : (value - maxIdeal) / maxIdeal;
      
      return Math.max(0, 100 - (deviation * 100));
    }
  }
  
  // Set parameter fill width based on score
  function setParameterFill(elementId, score) {
    const element = document.getElementById(elementId);
    if (element) {
      element.style.width = `${score}%`;
      
      // Add color class based on score
      element.className = 'parameter-fill';
      if (score >= 80) {
        element.classList.add('optimal');
      } else if (score >= 60) {
        element.classList.add('good');
      } else if (score >= 40) {
        element.classList.add('average');
      } else if (score >= 20) {
        element.classList.add('poor');
      } else {
        element.classList.add('critical');
      }
    }
  }
  
  // Load placeholder data for demo
  function loadPlaceholderData(farmer) {
    // Loan history placeholder
    document.getElementById('loan-history-body').innerHTML = `
      <tr>
        <td>${formatDate(new Date(new Date().setMonth(new Date().getMonth() - 2)))}</td>
        <td>${Math.round(farmer.financial_index * 50)}</td>
        <td>Seasonal inputs</td>
        <td><span class="badge badge-${farmer.financial_index > 60 ? 'low-risk' : 'medium-risk'}">Active</span></td>
        <td>In good standing</td>
      </tr>
      <tr>
        <td>${formatDate(new Date(new Date().setMonth(new Date().getMonth() - 8)))}</td>
        <td>${Math.round(farmer.financial_index * 30)}</td>
        <td>Equipment purchase</td>
        <td><span class="badge badge-low-risk">Completed</span></td>
        <td>Fully repaid</td>
      </tr>
    `;
    
    // Documents placeholder
    document.getElementById('documents-list').innerHTML = `
      <div class="document-item">
        <div class="document-icon"><i class="fas fa-id-card"></i></div>
        <div class="document-info">
          <div class="document-title">National ID</div>
          <div class="document-meta">Uploaded on ${formatDate(new Date(new Date().setMonth(new Date().getMonth() - 5)))}</div>
        </div>
        <div class="document-actions">
          <button><i class="fas fa-eye"></i></button>
          <button><i class="fas fa-download"></i></button>
        </div>
      </div>
      <div class="document-item">
        <div class="document-icon"><i class="fas fa-file-contract"></i></div>
        <div class="document-info">
          <div class="document-title">Loan Agreement</div>
          <div class="document-meta">Uploaded on ${formatDate(new Date(new Date().setMonth(new Date().getMonth() - 2)))}</div>
        </div>
        <div class="document-actions">
          <button><i class="fas fa-eye"></i></button>
          <button><i class="fas fa-download"></i></button>
        </div>
      </div>
      <div class="document-item">
        <div class="document-icon"><i class="fas fa-file-alt"></i></div>
        <div class="document-info">
          <div class="document-title">Soil Test Report</div>
          <div class="document-meta">Uploaded on ${formatDate(new Date(new Date().setMonth(new Date().getMonth() - 1)))}</div>
        </div>
        <div class="document-actions">
          <button><i class="fas fa-eye"></i></button>
          <button><i class="fas fa-download"></i></button>
        </div>
      </div>
    `;
    
    // Communication history placeholder
    document.getElementById('communication-history').innerHTML = `
      <div class="communication-item">
        <div class="communication-icon"><i class="fas fa-sms"></i></div>
        <div class="communication-content">
          <div class="communication-header-info">
            <div class="communication-type">SMS</div>
            <div class="communication-date">${formatDate(new Date(new Date().setDate(new Date().getDate() - 2)))}</div>
          </div>
          <div class="communication-message">
            Reminder: Your soil test appointment is scheduled for tomorrow at 10:00 AM.
          </div>
          <div class="communication-status">
            Delivered
          </div>
        </div>
      </div>
      <div class="communication-item">
        <div class="communication-icon"><i class="fas fa-envelope"></i></div>
        <div class="communication-content">
          <div class="communication-header-info">
            <div class="communication-type">Email</div>
            <div class="communication-date">${formatDate(new Date(new Date().setDate(new Date().getDate() - 7)))}</div>
          </div>
          <div class="communication-message">
            Your loan application has been pre-approved. Please visit our office to complete the documentation.
          </div>
          <div class="communication-status">
            Opened
          </div>
        </div>
      </div>
      <div class="communication-item">
        <div class="communication-icon"><i class="fas fa-user-friends"></i></div>
        <div class="communication-content">
          <div class="communication-header-info">
            <div class="communication-type">Farm Visit</div>
            <div class="communication-date">${formatDate(new Date(new Date().setDate(new Date().getDate() - 14)))}</div>
          </div>
          <div class="communication-message">
            Conducted farm inspection. Soil samples collected for analysis.
          </div>
          <div class="communication-status">
            Completed
          </div>
        </div>
      </div>
    `;
    
    // Soil recommendations placeholder
    document.getElementById('soil-recommendations-list').innerHTML = `
      <div class="recommendation-item">
        <div class="recommendation-title">Increase Nitrogen Levels</div>
        <div class="recommendation-details">
          Apply nitrogen fertilizer at ${Math.round(60 + Math.random() * 40)} kg/ha. Split application recommended.
        </div>
      </div>
      <div class="recommendation-item">
        <div class="recommendation-title">Improve Organic Matter</div>
        <div class="recommendation-details">
          Add compost or manure at 5-10 tons per hectare to improve soil structure and nutrient retention.
        </div>
      </div>
      <div class="recommendation-item">
        <div class="recommendation-title">${farmer.soil_data.ph_level < 6.0 ? 'Raise Soil pH' : 'Maintain Current pH'}</div>
        <div class="recommendation-details">
          ${farmer.soil_data.ph_level < 6.0 ? 
            'Apply agricultural lime at 2-3 tons per hectare to raise pH for optimal nutrient availability.' : 
            'Current pH level is optimal. Continue monitoring and maintain current practices.'}
        </div>
      </div>
    `;
  }
  
  function openAddFarmerModal() {
    // Reset the form
    document.getElementById('farmer-form').reset();
    document.getElementById('farmer-form-id').value = '';
    
    // Set modal title
    document.getElementById('add-edit-modal-title').textContent = 'Add New Farmer';
    
    // Show the modal
    document.getElementById('add-edit-farmer-modal').style.display = 'block';
  }
  
  function openEditFarmerModal(farmerId) {
    // Find the farmer
    const farmer = window.farmersData.find(f => f.id == farmerId);
    
    if (!farmer) {
      showToast('Farmer not found', 'error');
      return;
    }
    
    // Reset the form
    document.getElementById('farmer-form').reset();
    
    // Set form ID
    document.getElementById('farmer-form-id').value = farmer.id;
    
    // Fill in the form fields
    document.getElementById('form-first-name').value = farmer.first_name;
    document.getElementById('form-last-name').value = farmer.last_name;
    document.getElementById('form-gender').value = farmer.gender ? farmer.gender.toLowerCase() : '';
    document.getElementById('form-birth-date').value = farmer.birth_date || '';
    document.getElementById('form-id-number').value = farmer.id_number || '';
    document.getElementById('form-education').value = farmer.education || '';
    document.getElementById('form-phone').value = farmer.phone;
    document.getElementById('form-email').value = farmer.email || '';
    document.getElementById('form-address').value = farmer.address || '';
    document.getElementById('form-region').value = farmer.region;
    document.getElementById('form-district').value = farmer.district || '';
    document.getElementById('form-farm-size').value = farmer.farm_size;
    document.getElementById('form-farming-type').value = farmer.farming_type || '';
    document.getElementById('form-primary-crop').value = farmer.primary_crop;
    document.getElementById('form-secondary-crops').value = farmer.secondary_crops || '';
    document.getElementById('form-irrigation-type').value = farmer.irrigation_type || '';
    document.getElementById('form-soil-type').value = farmer.soil_type || '';
    
    // Set modal title
    document.getElementById('add-edit-modal-title').textContent = 'Edit Farmer';
    
    // Show the modal
    document.getElementById('add-edit-farmer-modal').style.display = 'block';
  }
  
  function saveFarmer() {
    showLoadingOverlay();
    
    // Get form values
    const formId = document.getElementById('farmer-form-id').value;
    const isEditing = formId !== '';
    
    // Create farmer object from form
    const farmer = {
      first_name: document.getElementById('form-first-name').value,
      last_name: document.getElementById('form-last-name').value,
      gender: document.getElementById('form-gender').value,
      birth_date: document.getElementById('form-birth-date').value,
      id_number: document.getElementById('form-id-number').value,
      education: document.getElementById('form-education').value,
      phone: document.getElementById('form-phone').value,
      email: document.getElementById('form-email').value,
      address: document.getElementById('form-address').value,
      region: document.getElementById('form-region').value,
      district: document.getElementById('form-district').value,
      farm_size: parseFloat(document.getElementById('form-farm-size').value),
      farming_type: document.getElementById('form-farming-type').value,
      primary_crop: document.getElementById('form-primary-crop').value,
      secondary_crops: document.getElementById('form-secondary-crops').value,
      irrigation_type: document.getElementById('form-irrigation-type').value,
      soil_type: document.getElementById('form-soil-type').value
    };
    
    // Add additional properties
    farmer.full_name = `${farmer.first_name} ${farmer.last_name}`;
    farmer.region_formatted = farmer.region.replace(/_/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase());
    
    // Simulate form submission delay
    setTimeout(() => {
      if (isEditing) {
        // Editing existing farmer
        const index = window.farmersData.findIndex(f => f.id == formId);
        if (index !== -1) {
          // Preserve ID and other properties that aren't on the form
          const originalFarmer = window.farmersData[index];
          farmer.id = originalFarmer.id;
          farmer.registration_date = originalFarmer.registration_date;
          farmer.financial_index = originalFarmer.financial_index;
          farmer.risk_level = originalFarmer.risk_level;
          farmer.soil_data = originalFarmer.soil_data;
          
          // Update farmer in the array
          window.farmersData[index] = farmer;
          
          hideLoadingOverlay();
          closeAllModals();
          showToast('Farmer updated successfully', 'success');
          
          // Refresh the display
          renderFarmersTable(getCurrentPageData());
          renderFarmersGrid(getCurrentPageData());
        } else {
          hideLoadingOverlay();
          showToast('Error: Farmer not found', 'error');
        }
      } else {
        // Adding new farmer
        // Generate ID, financial index, etc.
        farmer.id = window.farmersData.length > 0 ? Math.max(...window.farmersData.map(f => f.id)) + 1 : 1;
        farmer.registration_date = new Date();
        
        // Generate random financial index for demo
        farmer.financial_index = Math.floor(Math.random() * 100);
        
        // Determine risk level based on financial index
        if (farmer.financial_index >= 80) {
          farmer.risk_level = 'Low Risk';
        } else if (farmer.financial_index >= 60) {
          farmer.risk_level = 'Medium-Low Risk';
        } else if (farmer.financial_index >= 40) {
          farmer.risk_level = 'Medium Risk';
        } else if (farmer.financial_index >= 20) {
          farmer.risk_level = 'Medium-High Risk';
        } else {
          farmer.risk_level = 'High Risk';
        }
        
        // Generate random soil data for demo
        farmer.soil_data = {
          ph_level: Math.round((5.5 + Math.random() * 2) * 10) / 10,
          nitrogen_level: Math.round((15 + Math.random() * 30) * 10) / 10,
          phosphorus_level: Math.round((10 + Math.random() * 25) * 10) / 10,
          potassium_level: Math.round((120 + Math.random() * 150) * 10) / 10,
          organic_matter: Math.round((2 + Math.random() * 4) * 10) / 10,
          cation_exchange_capacity: Math.round((8 + Math.random() * 15) * 10) / 10,
          moisture_content: Math.round((15 + Math.random() * 20) * 10) / 10
        };
        
        // Add to farmers array
        window.farmersData.push(farmer);
        
        // Update pagination
        totalPages = Math.ceil(window.farmersData.length / pageSize);
        
        hideLoadingOverlay();
        closeAllModals();
        showToast('Farmer added successfully', 'success');
        
        // Refresh the display
        renderFarmersTable(getCurrentPageData());
        renderFarmersGrid(getCurrentPageData());
      }
    }, 1000);
  }
  
  function openDeleteConfirmationModal(farmerId) {
    // Find the farmer
    const farmer = window.farmersData.find(f => f.id == farmerId);
    
    if (!farmer) {
      showToast('Farmer not found', 'error');
      return;
    }
    
    // Set delete confirmation details
    document.getElementById('delete-farmer-name').textContent = farmer.full_name;
    document.getElementById('delete-farmer-id').textContent = farmer.id;
    document.getElementById('delete-farmer-location').textContent = farmer.region_formatted;
    
    // Set the confirm button's data-id attribute
    document.getElementById('confirm-delete-btn').setAttribute('data-id', farmer.id);
    
    // Show the modal
    document.getElementById('delete-confirmation-modal').style.display = 'block';
  }
  
  function deleteFarmer(farmerId) {
    showLoadingOverlay();
    
    // Simulate deletion delay
    setTimeout(() => {
      const index = window.farmersData.findIndex(f => f.id == farmerId);
      
      if (index !== -1) {
        // Remove the farmer from the array
        window.farmersData.splice(index, 1);
        
        // Update pagination
        totalPages = Math.ceil(window.farmersData.length / pageSize);
        if (currentPage > totalPages) {
          currentPage = totalPages || 1;
        }
        
        hideLoadingOverlay();
        closeAllModals();
        showToast('Farmer deleted successfully', 'success');
        
        // Refresh the display
        updatePaginationControls();
        renderFarmersTable(getCurrentPageData());
        renderFarmersGrid(getCurrentPageData());
      } else {
        hideLoadingOverlay();
        showToast('Error: Farmer not found', 'error');
      }
    }, 1000);
  }
  
  function openCommunicationModal(type) {
    // Set modal title based on communication type
    let title = '';
    if (type === 'sms') {
      title = 'Send SMS';
    } else if (type === 'email') {
      title = 'Send Email';
    } else if (type === 'visit') {
      title = 'Schedule Visit';
    }
    
    document.getElementById('communication-modal-title').textContent = title;
    
    // Get the current farmer from the detail modal
    const farmerId = document.getElementById('farmer-id').textContent;
    const farmer = window.farmersData.find(f => f.id == farmerId);
    
    if (farmer) {
      // Set recipient
      document.getElementById('comm-recipient').value = `${farmer.full_name} (${type === 'email' ? farmer.email : farmer.phone})`;
    }
    
    // Clear other fields
    document.getElementById('comm-subject').value = '';
    document.getElementById('comm-message').value = '';
    document.getElementById('comm-template').value = '';
    document.getElementById('comm-schedule').value = '';
    
    // Show the modal
    document.getElementById('communication-modal').style.display = 'block';
  }
  
  function applyTemplate(templateId) {
    if (!templateId) return;
    
    // Sample templates
    const templates = {
      soil_test_reminder: {
        subject: 'Soil Test Reminder',
        message: 'Dear Farmer,\n\nThis is a reminder that your scheduled soil test is due this week. Please ensure that your farm is accessible for our technicians.\n\nBest regards,\nTalazo AgriFinance Team'
      },
      loan_approval: {
        subject: 'Loan Application Approved',
        message: 'Dear Farmer,\n\nWe are pleased to inform you that your loan application has been approved. Please visit our office to complete the necessary documentation and collect your funds.\n\nBest regards,\nTalazo AgriFinance Team'
      },
      payment_reminder: {
        subject: 'Payment Reminder',
        message: 'Dear Farmer,\n\nThis is a friendly reminder that your loan payment is due in 5 days. Please ensure that your payment is made on time to avoid any late fees.\n\nBest regards,\nTalazo AgriFinance Team'
      },
      training_invitation: {
        subject: 'Agriculture Training Workshop Invitation',
        message: 'Dear Farmer,\n\nWe would like to invite you to attend our upcoming agricultural training workshop on modern farming techniques that will be held on [Date] at [Location]. This workshop will cover important topics such as soil health management, water conservation, and pest control.\n\nPlease confirm your attendance.\n\nBest regards,\nTalazo AgriFinance Team'
      }
    };
    
    // Apply the selected template
    const template = templates[templateId];
    if (template) {
      document.getElementById('comm-subject').value = template.subject;
      document.getElementById('comm-message').value = template.message;
    }
  }
  
  function sendCommunication() {
    showLoadingOverlay();
    
    // Simulate sending delay
    setTimeout(() => {
      hideLoadingOverlay();
      closeAllModals();
      showToast('Message sent successfully', 'success');
      
      // In a real application, you would send the message to the backend
    }, 1000);
  }
  
  function openUploadDocumentModal() {
    // Reset the form
    document.getElementById('upload-document-form').reset();
    
    // Show the modal
    document.getElementById('upload-document-modal').style.display = 'block';
  }
  
  function uploadDocument() {
    showLoadingOverlay();
    
    // Simulate upload delay
    setTimeout(() => {
      hideLoadingOverlay();
      closeAllModals();
      showToast('Document uploaded successfully', 'success');
      
      // In a real application, you would upload the document to the backend
    }, 1500);
  }
  
  function redirectToLoanProcessing(farmerId) {
    // In a real application, this would redirect to the loan processing page
    window.location.href = `/loans?farmer_id=${farmerId}`;
  }
  
  function redirectToSoilAnalysis(farmerId) {
    // In a real application, this would redirect to the soil analysis page
    window.location.href = `/soil_analysis?farmer_id=${farmerId}`;
  }
  
  function switchTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(`${tabId}-tab`).classList.add('active');
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    // Activate the selected tab button
    document.querySelector(`.tab-btn[data-tab="${tabId}"]`).classList.add('active');
  }
  
  function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
      modal.style.display = 'none';
    });
  }
  
  function showLoadingOverlay() {
    document.getElementById('loading-overlay').classList.remove('hidden');
  }
  
  function hideLoadingOverlay() {
    document.getElementById('loading-overlay').classList.add('hidden');
  }
  
  function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit'
    });
    document.getElementById('last-update-time').textContent = timeString;
  }
  
  function formatDate(date) {
    if (!(date instanceof Date)) {
      return 'Invalid date';
    }
    
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString(undefined, options);
  }
  
  // Helper function to show toast notifications
  function showToast(message, type = 'info') {
    try {
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
  }// farmers.js - Functionality for the farmers management page
  
  document.addEventListener('DOMContentLoaded', function() {
    // Initialize the farmers page
    initializePage();
    setupEventListeners();
    loadFarmersData();
    
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
    console.log('Farmers management page initialized');
  }
  
  // Set up event listeners for all interactive elements
  function setupEventListeners() {
    // Refresh data
    document.getElementById('refresh-data').addEventListener('click', function() {
      loadFarmersData();
    });
    
    // Add new farmer
    document.getElementById('add-farmer-btn').addEventListener('click', function() {
      openAddFarmerModal();
    });
    
    // Search functionality
    document.getElementById('farmer-search').addEventListener('input', function() {
      filterFarmers();
    });
    
    // Filters
    document.getElementById('region-filter').addEventListener('change', filterFarmers);
    document.getElementById('crop-filter').addEventListener('change', filterFarmers);
    document.getElementById('risk-filter').addEventListener('change', filterFarmers);
    
    // View toggles
    document.querySelectorAll('.view-toggle').forEach(button => {
      button.addEventListener('click', function() {
        const view = this.getAttribute('data-view');
        toggleView(view);
      });
    });
    
    // Table sorting
    document.querySelectorAll('.farmers-table th i').forEach(icon => {
      icon.addEventListener('click', function() {
        const column = this.parentElement.textContent.trim().toLowerCase().replace(' ', '_');
        sortFarmersTable(column);
      });
    });
    
    // Pagination
    document.getElementById('prev-page').addEventListener('click', function() {
      goToPreviousPage();
    });
    
    document.getElementById('next-page').addEventListener('click', function() {
      goToNextPage();
    });
    
    document.getElementById('page-size').addEventListener('change', function() {
      changePageSize();
    });
    
    // Grid pagination
    document.getElementById('grid-prev-page').addEventListener('click', function() {
      goToPreviousPage('grid');
    });
    
    document.getElementById('grid-next-page').addEventListener('click', function() {
      goToNextPage('grid');
    });
    
    // Close modals
    document.querySelectorAll('.close-modal').forEach(closeBtn => {
      closeBtn.addEventListener('click', function() {
        closeAllModals();
      });
    });
    
    // Modal backdrop click to close
    document.querySelectorAll('.modal').forEach(modal => {
      modal.addEventListener('click', function(e) {
        if (e.target === this) {
          closeAllModals();
        }
      });
    });
    
    // Farmer detail modal tabs
    document.querySelectorAll('.tab-btn').forEach(tab => {
      tab.addEventListener('click', function() {
        const tabId = this.getAttribute('data-tab');
        switchTab(tabId);
      });
    });
    
    // Form submission for adding/editing farmer
    document.getElementById('farmer-form').addEventListener('submit', function(e) {
      e.preventDefault();
      saveFarmer();
    });
    
    // Cancel button in add/edit form
    document.getElementById('cancel-farmer-form').addEventListener('click', function() {
      closeAllModals();
    });
    
    // Delete farmer button
    document.getElementById('delete-farmer-btn').addEventListener('click', function() {
      const farmerId = this.getAttribute('data-id');
      openDeleteConfirmationModal(farmerId);
    });
    
    // Cancel delete
    document.getElementById('cancel-delete-btn').addEventListener('click', function() {
      closeAllModals();
    });
    
    // Confirm delete
    document.getElementById('confirm-delete-btn').addEventListener('click', function() {
      const farmerId = this.getAttribute('data-id');
      deleteFarmer(farmerId);
    });
    
    // Communication buttons
    document.getElementById('send-sms-btn').addEventListener('click', function() {
      openCommunicationModal('sms');
    });
    
    document.getElementById('send-email-btn').addEventListener('click', function() {
      openCommunicationModal('email');
    });
    
    document.getElementById('schedule-visit-btn').addEventListener('click', function() {
      openCommunicationModal('visit');
    });
    
    // Cancel communication
    document.getElementById('cancel-comm-btn').addEventListener('click', function() {
      closeAllModals();
    });
    
    // Send communication
    document.getElementById('send-comm-btn').addEventListener('click', function() {
      sendCommunication();
    });
    
    // Template selection
    document.getElementById('comm-template').addEventListener('change', function() {
      applyTemplate(this.value);
    });
    
    // Upload document button
    document.getElementById('upload-document-btn').addEventListener('click', function() {
      openUploadDocumentModal();
    });
    
    // Cancel upload
    document.getElementById('cancel-upload-btn').addEventListener('click', function() {
      closeAllModals();
    });
    
    // Save document
    document.getElementById('save-document-btn').addEventListener('click', function() {
      uploadDocument();
    });
  
    // Other modal buttons in farmer detail view
    document.getElementById('edit-farmer-btn').addEventListener('click', function() {
      const farmerId = this.getAttribute('data-id');
      openEditFarmerModal(farmerId);
    });
    
    document.getElementById('process-loan-modal-btn').addEventListener('click', function() {
      const farmerId = this.getAttribute('data-id');
      redirectToLoanProcessing(farmerId);
    });
    
    document.getElementById('soil-analysis-modal-btn').addEventListener('click', function() {
      const farmerId = this.getAttribute('data-id');
      redirectToSoilAnalysis(farmerId);
    });
  }
  
  // Load farmers data from API
  function loadFarmersData() {
    showLoadingOverlay();
    
    // Simulate API call with timeout
    setTimeout(() => {
      try {
        // This would be a fetch call to your API in a real application
        // For now, we'll use dummy data
        const farmersData = generateDummyFarmers(50);
        
        // Store the data in a global variable for filtering, sorting, etc.
        window.farmersData = farmersData;
        
        // Initialize pagination
        initializePagination(farmersData);
        
        // Render the data
        renderFarmersTable(getCurrentPageData());
        renderFarmersGrid(getCurrentPageData());
        initializeMap(farmersData);
        
        // Hide loading overlay
        hideLoadingOverlay();
        
        // Update last update time
        updateLastUpdateTime();
        
        // Show success message
        showToast('Farmers data loaded successfully', 'success');
      } catch (error) {
        console.error('Error loading farmers data:', error);
        hideLoadingOverlay();
        showToast('Error loading farmers data', 'error');
      }
    }, 1000);
  }
  
  // Generate dummy farmers data for demonstration
  function generateDummyFarmers(count) {
    const regions = [
      'mashonaland_central', 'mashonaland_east', 'mashonaland_west',
      'matabeleland_north', 'matabeleland_south', 'midlands',
      'masvingo', 'manicaland', 'harare', 'bulawayo'
    ];
    
    const crops = [
      'maize', 'tobacco', 'cotton', 'groundnuts', 'soybeans',
      'wheat', 'sorghum', 'millet', 'vegetables', 'fruits'
    ];
    
    const riskLevels = [
      'Low Risk', 'Medium-Low Risk', 'Medium Risk', 'Medium-High Risk', 'High Risk'
    ];
    
    const farmers = [];
    
    for (let i = 1; i <= count; i++) {
      const financialIndex = Math.floor(Math.random() * 100);
      let riskLevel;
      
      if (financialIndex >= 80) {
        riskLevel = 'Low Risk';
      } else if (financialIndex >= 60) {
        riskLevel = 'Medium-Low Risk';
      } else if (financialIndex >= 40) {
        riskLevel = 'Medium Risk';
      } else if (financialIndex >= 20) {
        riskLevel = 'Medium-High Risk';
      } else {
        riskLevel = 'High Risk';
      }
      
      const farmer = {
        id: i,
        first_name: `First${i}`,
        last_name: `Last${i}`,
        gender: Math.random() > 0.5 ? 'Male' : 'Female',
        age: 25 + Math.floor(Math.random() * 40),
        phone: `+263 7${Math.floor(Math.random() * 10)}${Math.floor(Math.random() * 10)} ${Math.floor(Math.random() * 10000000)}`,
        email: `farmer${i}@example.com`,
        region: regions[Math.floor(Math.random() * regions.length)],
        district: `District ${Math.floor(Math.random() * 10) + 1}`,
        farm_size: Math.round((1 + Math.random() * 20) * 10) / 10,
        primary_crop: crops[Math.floor(Math.random() * crops.length)],
        financial_index: financialIndex,
        risk_level: riskLevel,
        registration_date: new Date(2020 + Math.floor(Math.random() * 4), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
        soil_data: {
          ph_level: Math.round((5.5 + Math.random() * 2) * 10) / 10,
          nitrogen_level: Math.round((15 + Math.random() * 30) * 10) / 10,
          phosphorus_level: Math.round((10 + Math.random() * 25) * 10) / 10,
          potassium_level: Math.round((120 + Math.random() * 150) * 10) / 10,
          organic_matter: Math.round((2 + Math.random() * 4) * 10) / 10,
          cation_exchange_capacity: Math.round((8 + Math.random() * 15) * 10) / 10,
          moisture_content: Math.round((15 + Math.random() * 20) * 10) / 10
        }
      };
      
      // Format the region name for display
      farmer.region_formatted = farmer.region.replace(/_/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase());
      
      // Add full name for convenience
      farmer.full_name = `${farmer.first_name} ${farmer.last_name}`;
      
      farmers.push(farmer);
    }
    
    return farmers;
  }
  
  // Pagination variables and functions
  let currentPage = 1;
  let pageSize = 10;
  let totalPages = 1;
  
  function initializePagination(data) {
    pageSize = parseInt(document.getElementById('page-size').value);
    totalPages = Math.ceil(data.length / pageSize);
    currentPage = 1;
    
    updatePaginationControls();
  }
  
  function updatePaginationControls() {
    // Update page indicator
    document.getElementById('page-indicator').textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('grid-page-indicator').textContent = `Page ${currentPage} of ${totalPages}`;
    
    // Enable/disable previous button
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('grid-prev-page').disabled = currentPage === 1;
    
    // Enable/disable next button
    document.getElementById('next-page').disabled = currentPage === totalPages;
    document.getElementById('grid-next-page').disabled = currentPage === totalPages;
  }
  
  function getCurrentPageData() {
    const filteredData = getFilteredData();
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    
    return filteredData.slice(start, end);
  }
  
  function goToPreviousPage(view = 'list') {
    if (currentPage > 1) {
      currentPage--;
      updatePaginationControls();
      
      if (view === 'grid') {
        renderFarmersGrid(getCurrentPageData());
      } else {
        renderFarmersTable(getCurrentPageData());
      }
    }
  }
  
  function goToNextPage(view = 'list') {
    if (currentPage < totalPages) {
      currentPage++;
      updatePaginationControls();
      
      if (view === 'grid') {
        renderFarmersGrid(getCurrentPageData());
      } else {
        renderFarmersTable(getCurrentPageData());
      }
    }
  }
  
  function changePageSize() {
    pageSize = parseInt(document.getElementById('page-size').value);
    totalPages = Math.ceil(getFilteredData().length / pageSize);
    currentPage = 1;
    
    updatePaginationControls();
    renderFarmersTable(getCurrentPageData());
  }
  
  // Filter functions
  function getFilteredData() {
    if (!window.farmersData) return [];
    
    const searchTerm = document.getElementById('farmer-search').value.toLowerCase();
    const regionFilter = document.getElementById('region-filter').value;
    const cropFilter = document.getElementById('crop-filter').value;
    const riskFilter = document.getElementById('risk-filter').value;
    
    return window.farmersData.filter(farmer => {
      // Search filter
      const searchMatch = !searchTerm || 
        farmer.full_name.toLowerCase().includes(searchTerm) ||
        farmer.region_formatted.toLowerCase().includes(searchTerm) ||
        farmer.id.toString().includes(searchTerm);
      
      // Region filter
      const regionMatch = !regionFilter || farmer.region === regionFilter;
      
      // Crop filter
      const cropMatch = !cropFilter || farmer.primary_crop === cropFilter;
      
      // Risk filter
      const riskMatch = !riskFilter || 
        farmer.risk_level.toLowerCase().replace(/ /g, '-') === riskFilter;
      
      return searchMatch && regionMatch && cropMatch && riskMatch;
    });
  }
  
  function filterFarmers() {
    const filteredData = getFilteredData();
    
    // Update pagination for filtered data
    totalPages = Math.ceil(filteredData.length / pageSize);
    currentPage = 1;
    
    updatePaginationControls();
    
    // Render filtered data
    renderFarmersTable(getCurrentPageData());
    renderFarmersGrid(getCurrentPageData());
    
    // Show toast with filter results
    showToast(`Showing ${filteredData.length} farmers matching filter criteria`, 'info');
  }
  
  // Sort functions
  let sortColumn = 'id';
  let sortDirection = 'asc';
  
  function sortFarmersTable(column) {
    if (sortColumn === column) {
      // Toggle sort direction if same column is clicked
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // Set new sort column and default to ascending
      sortColumn = column;
      sortDirection = 'asc';
    }
    
    // Sort the data
    window.farmersData.sort((a, b) => {
      let valueA = a[sortColumn];
      let valueB = b[sortColumn];
      
      // Handle special case for full name
      if (sortColumn === 'name') {
        valueA = a.full_name;
        valueB = b.full_name;
      }
      
      // Handle special case for location
      if (sortColumn === 'location') {
        valueA = a.region_formatted;
        valueB = b.region_formatted;
      }
      
      // Compare the values
      if (valueA < valueB) {
        return sortDirection === 'asc' ? -1 : 1;
      }
      if (valueA > valueB) {
        return sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });
    
    // Update the table
    renderFarmersTable(getCurrentPageData());
    
    // Show toast
    showToast(`Sorted by ${column.replace('_', ' ')} (${sortDirection === 'asc' ? 'ascending' : 'descending'})`, 'info');
  }
  
  // View toggle functions
  function toggleView(view) {
    // Remove active class from all toggle buttons
    document.querySelectorAll('.view-toggle').forEach(btn => {
      btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    document.querySelector(`.view-toggle[data-view="${view}"]`).classList.add('active');
    
    // Hide all views
    document.getElementById('farmers-list-view').classList.add('hidden');
    document.getElementById('farmers-grid-view').classList.add('hidden');
    document.getElementById('farmers-map-view').classList.add('hidden');
    
    // Show selected view
    document.getElementById(`farmers-${view}-view`).classList.remove('hidden');
    
    // Special handling for map view (initialize if needed)
    if (view === 'map' && window.farmersData) {
      initializeMap(window.farmersData);
    }
  }
  
  // Render functions
  function renderFarmersTable(farmers) {
    const tableBody = document.getElementById('farmers-table-body');
    
    if (!farmers || farmers.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="8" class="no-results">No farmers found matching the criteria.</td>
        </tr>
      `;
      return;
    }
    
    let html = '';
    
    farmers.forEach(farmer => {
      const riskClass = farmer.risk_level.toLowerCase().replace(/ /g, '-');
      
      html += `
        <tr data-id="${farmer.id}">
          <td>${farmer.id}</td>
          <td>${farmer.full_name}</td>
          <td>${farmer.region_formatted}</td>
          <td>${farmer.primary_crop.replace(/\b\w/g, l => l.toUpperCase())}</td>
          <td>${farmer.farm_size} ha</td>
          <td>${farmer.financial_index}</td>
          <td>
            <span class="badge badge-${riskClass}">${farmer.risk_level}</span>
          </td>
          <td>
            <button class="action-btn view-farmer-btn" data-id="${farmer.id}" title="View Details">
              <i class="fas fa-eye"></i>
            </button>
            <button class="action-btn edit-farmer-btn" data-id="${farmer.id}" title="Edit Farmer">
              <i class="fas fa-edit"></i>
            </button>
            <button class="action-btn delete-farmer-btn" data-id="${farmer.id}" title="Delete Farmer">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>
      `;
    });
    
    tableBody.innerHTML = html;
    
    // Add event listeners to action buttons
    document.querySelectorAll('.view-farmer-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const farmerId = this.getAttribute('data-id');
        openFarmerDetailModal(farmerId);
      });
    });
    
    document.querySelectorAll('.edit-farmer-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const farmerId = this.getAttribute('data-id');
        openEditFarmerModal(farmerId);
      });
    });
    
    document.querySelectorAll('.delete-farmer-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const farmerId = this.getAttribute('data-id');
        openDeleteConfirmationModal(farmerId);
      });
    });
  }
  
  function renderFarmersGrid(farmers) {
    const gridContainer = document.getElementById('farmers-grid-container');
    
    if (!farmers || farmers.length === 0) {
      gridContainer.innerHTML = `
        <div class="no-results-card">
          <p>No farmers found matching the criteria.</p>
        </div>
      `;
      return;
    }
    
    let html = '';
    
    farmers.forEach(farmer => {
      const riskClass = farmer.risk_level.toLowerCase().replace(/ /g, '-');
      
      html += `
        <div class="farmer-card" data-id="${farmer.id}">
          <div class="farmer-card-header">
            <h3 class="farmer-card-name">${farmer.full_name}</h3>
            <span class="badge badge-${riskClass}">${farmer.risk_level}</span>
          </div>
          <div class="farmer-card-details">
            <div class="farmer-card-row">
              <div class="farmer-card-label">Location:</div>
              <div class="farmer-card-value">${farmer.region_formatted}</div>
            </div>
            <div class="farmer-card-row">
              <div class="farmer-card-label">Primary Crop:</div>
              <div class="farmer-card-value">${farmer.primary_crop.replace(/\b\w/g, l => l.toUpperCase())}</div>
            </div>
            <div class="farmer-card-row">
              <div class="farmer-card-label">Farm Size:</div>
              <div class="farmer-card-value">${farmer.farm_size} ha</div>
            </div>
            <div class="farmer-card-row">
              <div class="farmer-card-label">Financial Index:</div>
              <div class="farmer-card-value">${farmer.financial_index}</div>
            </div>
          </div>
          <div class="farmer-card-footer">
            <button class="btn btn-primary view-farmer-btn" data-id="${farmer.id}">
              <i class="fas fa-eye"></i> View Details
            </button>
            <button class="btn btn-secondary edit-farmer-btn" data-id="${farmer.id}">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-danger delete-farmer-btn" data-id="${farmer.id}">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      `;
    });
    
    gridContainer.innerHTML = html;
    
    // Add event listeners to action buttons
    document.querySelectorAll('.farmer-card .view-farmer-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const farmerId = this.getAttribute('data-id');
        openFarmerDetailModal(farmerId);
      });
    });
    
    document.querySelectorAll('.farmer-card .edit-farmer-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const farmerId = this.getAttribute('data-id');
        openEditFarmerModal(farmerId);
      });
    });
    
    document.querySelectorAll('.farmer-card .delete-farmer-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const farmerId = this.getAttribute('data-id');
        openDeleteConfirmationModal(farmerId);
      });
    });
  }
  
  function initializeMap(farmers) {
    const mapElement = document.getElementById('farmers-map');
    
    // Clear existing map content
    mapElement.innerHTML = '';
    
    // In a real application, you would initialize a map library like Leaflet or Google Maps here
    // For this demo, we'll just show a placeholder
    mapElement.innerHTML = `
      <div class="map-placeholder">
        <p>Map view would display ${farmers.length} farmers across different regions in Zimbabwe.</p>
        <p>In a real implementation, this would use Leaflet or Google Maps to display farmer locations.</p>
      </div>
    `;
  }
  
  // Modal functions
  function openFarmerDetailModal(farmerId) {
    // Find the farmer by ID
    const farmer = window.farmersData.find(f => f.id == farmerId);
    
    if (!farmer) {
      showToast('Farmer not found', 'error');
      return;
    }
    
    // Set the modal title
    document.querySelector('#farmer-detail-modal .modal-header h2').textContent = 'Farmer Details';
    
    // Populate the profile tab
    document.getElementById('farmer-name').textContent = farmer.full_name;
    document.getElementById('farmer-location').textContent = `${farmer.region_formatted}, ${farmer.district}`;
    document.getElementById('farmer-contact').textContent = farmer.phone;
    document.getElementById('farmer-risk-badge').textContent = farmer.risk_level;
    
    // Add risk level class
    document.getElementById('farmer-risk-badge').className = 'farmer-risk-badge';
    document.getElementById('farmer-risk-badge').classList.add(farmer.risk_level.toLowerCase().replace(/ /g, '-'));
    
    // Fill in profile details
    document.getElementById('farmer-id').textContent = farmer.id;
    document.getElementById('registration-date').textContent = formatDate(farmer.registration_date);
    document.getElementById('farmer-gender').textContent = farmer.gender || 'Not specified';
    document.getElementById('farmer-age').textContent = farmer.age || 'Not specified';
    document.getElementById('farmer-education').textContent = farmer.education || 'Not specified';
    document.getElementById('farmer-household').textContent = farmer.household_size || 'Not specified';
    document.getElementById('farmer-experience').textContent = farmer.years_farming || 'Not specified';
    document.getElementById('farming-type').textContent = farmer.farming_type || 'Not specified';
    
    // Populate farm tab
    document.getElementById('farm-size').textContent = `${farmer.farm_size} hectares`;
    document.getElementById('primary-crop').textContent = farmer.primary_crop.replace(/\b\w/g, l => l.toUpperCase());
    document.getElementById('secondary-crops').textContent = farmer.secondary_crops || 'None';
    document.getElementById('irrigation-type').textContent = farmer.irrigation_type || 'Not specified';
    document.getElementById('soil-type').textContent = farmer.soil_type || 'Not specified';
    document.getElementById('last-soil-test').textContent = farmer.last_soil_test ? formatDate(farmer.last_soil_test) : 'No soil test recorded';
    document.getElementById('farm-equipment').textContent = farmer.equipment || 'Not specified';
    document.getElementById('farm-certifications').textContent = farmer.certifications || 'None';
    
    // Populate financial tab
    document.getElementById('financial-index').textContent = farmer.financial_index;
    document.getElementById('loan-eligibility').textContent = farmer.financial_index >= 40 ? 'Eligible' : 'Not Eligible';
    
    // Calculate financial metrics based on the index
    const maxLoan = Math.round(farmer.financial_index * 100) * (farmer.farm_size);
    const interestRate = Math.max(5, 15 - (farmer.financial_index / 10)).toFixed(1);
    const insurancePremium = (100 * (1 + ((100 - farmer.financial_index) / 100) ** 1.8)).toFixed(2);
    
    document.getElementById('max-loan-amount').textContent = `${maxLoan}`;
    document.getElementById('interest-rate').textContent = `${interestRate}%`;
    document.getElementById('insurance-premium').textContent = `${insurancePremium}/ha`;
    document.getElementById('risk-level').textContent = farmer.risk_level;
    
    // Soil health tab
    updateSoilHealthTab(farmer);
    
    // Set up buttons with farmer ID
    document.getElementById('edit-farmer-btn').setAttribute('data-id', farmer.id);
    document.getElementById('process-loan-modal-btn').setAttribute('data-id', farmer.id);
    document.getElementById('soil-analysis-modal-btn').setAttribute('data-id', farmer.id);
    document.getElementById('delete-farmer-btn').setAttribute('data-id', farmer.id);
    
    // Show the modal
    document.getElementById('farmer-detail-modal').style.display = 'block';
    
    // Reset to first tab
    switchTab('profile');
    
    // In a real application, you would also load:
    // - Loan history
    // - Financial history chart
    // - Soil health history chart
    // - Documents
    // - Communication history
    
    // For this demo, we'll show placeholders for these
    loadPlaceholderData(farmer);
  }