document.addEventListener("DOMContentLoaded", function () {
  // Tab switching
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons and contents
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabContents.forEach((content) => content.classList.remove("active"));

      // Add active class to clicked button
      button.classList.add("active");

      // Show corresponding content
      const tabId = button.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");
    });
  });

  // Fetch farmers for dropdown
  fetchFarmers();

  // Farmer form submission
  const farmerForm = document.getElementById("farmer-form");
  if (farmerForm) {
    farmerForm.addEventListener("submit", function (e) {
      e.preventDefault();
      addFarmer();
    });
  }

  // Simulate data button
  const simulateBtn = document.getElementById("simulate-btn");
  if (simulateBtn) {
    simulateBtn.addEventListener("click", simulateData);
  }

  // Soil analysis form submission
  const form = document.getElementById('soil-analysis-form');
  const resultsDiv = document.getElementById('results');
  
  if (form) {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      try {
        // Get form data
        const formData = {
          ph_level: parseFloat(document.getElementById('ph_level').value),
          nitrogen_level: parseFloat(document.getElementById('nitrogen_level').value),
          phosphorus_level: parseFloat(document.getElementById('phosphorus_level').value),
          potassium_level: parseFloat(document.getElementById('potassium_level').value),
          organic_matter: parseFloat(document.getElementById('organic_matter').value || 0),
          cation_exchange_capacity: parseFloat(document.getElementById('cation_exchange_capacity').value || 0),
          moisture_content: parseFloat(document.getElementById('moisture_content').value || 0)
        };
        
        console.log("Sending data:", formData); // Add logging for debugging
        
        // Send POST request to the API
        const response = await fetch('/api/calculate-index', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to calculate index');
        }
        
        console.log("Received response:", data); // Add logging for debugging
        
        // Display results
        document.getElementById('credit-score').innerHTML = `
          <h3>Credit Score</h3>
          <p>${data.credit_score.toFixed(2)}</p>
        `;
        
        document.getElementById('risk-level').innerHTML = `
          <h3>Risk Level</h3>
          <p>${data.risk_level}</p>
        `;
        
        document.getElementById('premium').innerHTML = `
          <h3>Recommended Premium</h3>
          <p>$${data.recommended_premium.toFixed(2)}</p>
        `;
        
        // Display recommendations
        const recommendationsHtml = data.recommendations.length > 0
          ? `<h3>Recommendations</h3>
             <ul>${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>`
          : '';
        
        document.getElementById('recommendations').innerHTML = recommendationsHtml;
        
        // Show results
        resultsDiv.classList.remove('hidden');
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
        
      } catch (error) {
        console.error('Error:', error);
        alert('Error calculating index: ' + error.message);
      }
    });
  }
});

// Fetch farmers
function fetchFarmers() {
  // In a real app, this would be an API call
  // For prototype, we'll simulate with sample data
  const sampleFarmers = [
    { id: 1, name: "John Moyo", location: "Harare" },
    { id: 2, name: "Mary Ncube", location: "Bulawayo" },
    { id: 3, name: "Robert Dube", location: "Mutare" },
  ];

  const farmerSelect = document.getElementById("farmer-select");
  if (farmerSelect) {
    farmerSelect.innerHTML = '<option value="">Select a farmer or add new</option>';

    sampleFarmers.forEach((farmer) => {
      const option = document.createElement("option");
      option.value = farmer.id;
      option.textContent = `${farmer.name} (${farmer.location})`;
      farmerSelect.appendChild(option);
    });
  }

  // Also update the farmers list in the Manage Farmers tab
  const farmersList = document.getElementById("farmers-list");
  if (farmersList) {
    farmersList.innerHTML = '';
    
    // Create a table to display farmers
    const table = document.createElement('table');
    table.className = 'farmers-table';
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    
    // Add table header
    const thead = document.createElement('thead');
    thead.innerHTML = `
      <tr>
        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Name</th>
        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Location</th>
        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Actions</th>
      </tr>
    `;
    table.appendChild(thead);
    
    // Add table body
    const tbody = document.createElement('tbody');
    sampleFarmers.forEach(farmer => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="padding: 10px; border-bottom: 1px solid #ddd;">${farmer.name}</td>
        <td style="padding: 10px; border-bottom: 1px solid #ddd;">${farmer.location}</td>
        <td style="padding: 10px; border-bottom: 1px solid #ddd;">
          <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px;" onclick="viewFarmer(${farmer.id})">View</button>
          <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px;" onclick="editFarmer(${farmer.id})">Edit</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    
    farmersList.appendChild(table);
  }
}

// Add farmer
function addFarmer() {
  const name = document.getElementById('farmer-name').value;
  const location = document.getElementById('farmer-location').value;
  const farmSize = document.getElementById('farm-size').value;
  const cropType = document.getElementById('crop-type').value;
  
  if (!name || !location) {
    alert('Please enter farmer name and location');
    return;
  }
  
  alert(`Farmer added: ${name} from ${location}`);
  
  // In a real app, you'd send this to the server
  // For prototype, just reset form and refresh list
  document.getElementById('farmer-form').reset();
  fetchFarmers();
}

// View farmer 
function viewFarmer(id) {
  alert(`View farmer with ID: ${id}`);
  // In a real app, this would open a detail view
}

// Edit farmer
function editFarmer(id) {
  alert(`Edit farmer with ID: ${id}`);
  // In a real app, this would open an edit form
}

// Simulate data for testing
function simulateData() {
  document.getElementById('ph_level').value = 6.5;
  document.getElementById('nitrogen_level').value = 30;
  document.getElementById('phosphorus_level').value = 25;
  document.getElementById('potassium_level').value = 200;
  document.getElementById('organic_matter').value = 4;
  document.getElementById('cation_exchange_capacity').value = 15;
  document.getElementById('moisture_content').value = 25;
}