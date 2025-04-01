// farmers.js - Farmers Management Page Functionality
class FarmersManager {
    constructor() {
        // UI Elements
        this.farmersTableBody = document.getElementById('farmers-table-body');
        this.totalFarmersCount = document.getElementById('total-farmers-count');
        this.totalLandArea = document.getElementById('total-land-area');
        this.avgFarmingExperience = document.getElementById('avg-farming-experience');
        
        // Pagination Elements
        this.prevPageBtn = document.getElementById('prev-page');
        this.nextPageBtn = document.getElementById('next-page');
        this.currentPageSpan = document.getElementById('current-page');
        
        // Filter Elements
        this.locationFilter = document.getElementById('location-filter');
        this.cropFilter = document.getElementById('crop-filter');
        this.minLandArea = document.getElementById('min-land-area');
        this.maxLandArea = document.getElementById('max-land-area');
        
        // Modal Elements
        this.farmerDetailsModal = document.getElementById('farmer-details-modal');
        this.closeModalBtn = document.querySelector('.close-modal');
        
        // Farmer Details Modal Fields
        this.farmerNameTitle = document.getElementById('farmer-name-title');
        this.farmerPhone = document.getElementById('farmer-phone');
        this.farmerAddress = document.getElementById('farmer-address');
        this.farmerNationalId = document.getElementById('farmer-national-id');
        this.farmerPrimaryCrop = document.getElementById('farmer-primary-crop');
        this.farmerLandArea = document.getElementById('farmer-land-area');
        this.farmerExperience = document.getElementById('farmer-experience');
        this.farmPlotsBody = document.getElementById('farm-plots-body');
        
        // State
        this.currentPage = 1;
        this.totalPages = 1;
        
        // Bind events
        this.bindEvents();
        
        // Initialize page
        this.loadFarmersStats();
        this.loadFarmers();
    }

    bindEvents() {
        // Pagination events
        this.prevPageBtn.addEventListener('click', () => this.changePage(-1));
        this.nextPageBtn.addEventListener('click', () => this.changePage(1));
        
        // Filter events
        this.locationFilter.addEventListener('change', () => this.loadFarmers());
        this.cropFilter.addEventListener('change', () => this.loadFarmers());
        this.minLandArea.addEventListener('change', () => this.loadFarmers());
        this.maxLandArea.addEventListener('change', () => this.loadFarmers());
        
        // Modal close event
        this.closeModalBtn.addEventListener('click', () => this.closeDetailsModal());
        
        // Add farmer button (placeholder)
        const addFarmerBtn = document.getElementById('add-farmer-btn');
        if (addFarmerBtn) {
            addFarmerBtn.addEventListener('click', () => this.showAddFarmerModal());
        }
    }

    async loadFarmersStats() {
        try {
            const response = await fetch('/api/farmers/stats');
            const stats = await response.json();
            
            // Update stats cards
            this.totalFarmersCount.textContent = stats.total_farmers;
            this.totalLandArea.textContent = `${stats.total_land_area.toFixed(2)} Ha`;
            this.avgFarmingExperience.textContent = `${stats.average_farming_experience.toFixed(1)} Years`;
            
            // Optional: Create crop distribution chart
            this.createCropDistributionChart(stats.crop_distribution);
        } catch (error) {
            console.error('Error loading farmers stats:', error);
            this.showErrorNotification('Failed to load farmers statistics');
        }
    }

    async loadFarmers() {
        try {
            // Construct query parameters from filters
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: 10
            });

            // Add location filter
            const selectedLocations = Array.from(this.locationFilter.selectedOptions)
                .map(option => option.value)
                .filter(val => val);
            if (selectedLocations.length) {
                params.append('location', selectedLocations.join(','));
            }

            // Add crop filter
            const selectedCrops = Array.from(this.cropFilter.selectedOptions)
                .map(option => option.value)
                .filter(val => val);
            if (selectedCrops.length) {
                params.append('crop', selectedCrops.join(','));
            }

            // Add land area filters
            if (this.minLandArea.value) {
                params.append('min_land_area', this.minLandArea.value);
            }
            if (this.maxLandArea.value) {
                params.append('max_land_area', this.maxLandArea.value);
            }

            // Fetch farmers
            const response = await fetch(`/api/farmers?${params.toString()}`);
            const data = await response.json();

            // Clear existing table rows
            this.farmersTableBody.innerHTML = '';

            // Populate table
            data.farmers.forEach(farmer => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${farmer.full_name}</td>
                    <td>${farmer.address}</td>
                    <td>${farmer.primary_crop}</td>
                    <td>${farmer.total_land_area.toFixed(2)}</td>
                    <td>${farmer.soil_health_score ? farmer.soil_health_score.toFixed(2) : 'N/A'}</td>
                    <td>
                        <button class="btn btn-sm btn-info view-farmer" data-farmer-id="${farmer.id}">
                            <i class="fas fa-eye"></i> View
                        </button>
                    </td>
                `;

                // Add click event to view farmer details
                const viewButton = row.querySelector('.view-farmer');
                viewButton.addEventListener('click', () => this.showFarmerDetails(farmer.id));

                this.farmersTableBody.appendChild(row);
            });

            // Update pagination
            this.totalPages = data.pages;
            this.updatePaginationControls();
        } catch (error) {
            console.error('Error loading farmers:', error);
            this.showErrorNotification('Failed to load farmers');
        }
    }

    async showFarmerDetails(farmerId) {
        try {
            const response = await fetch(`/api/farmers/${farmerId}`);
            const farmerData = await response.json();

            // Update personal info
            this.farmerNameTitle.textContent = farmerData.personal_info.full_name;
            this.farmerPhone.textContent = farmerData.personal_info.phone_number;
            this.farmerAddress.textContent = farmerData.personal_info.address;
            this.farmerNationalId.textContent = farmerData.personal_info.national_id;

            // Update farming details
            this.farmerPrimaryCrop.textContent = farmerData.farming_details.primary_crop;
            this.farmerLandArea.textContent = farmerData.farming_details.total_land_area.toFixed(2);
            this.farmerExperience.textContent = farmerData.farming_details.farming_experience;

            // Populate farm plots
            this.farmPlotsBody.innerHTML = '';
            farmerData.farm_plots.forEach(plot => {
                const plotRow = document.createElement('tr');
                plotRow.innerHTML = `
                    <td>${plot.name}</td>
                    <td>${plot.area.toFixed(2)}</td>
                    <td>${plot.current_crop}</td>
                `;
                this.farmPlotsBody.appendChild(plotRow);
            });

            // Create soil samples chart
            this.createSoilSamplesChart(farmerData.soil_samples);

            // Show modal
            this.farmerDetailsModal.style.display = 'block';
        } catch (error) {
            console.error('Error fetching farmer details:', error);
            this.showErrorNotification('Failed to load farmer details');
        }
    }

    createSoilSamplesChart(soilSamples) {
        const chartContainer = document.getElementById('soil-samples-chart');
        chartContainer.innerHTML = ''; // Clear previous chart

        // Create chart only if we have samples
        if (!soilSamples || soilSamples.length === 0) {
            chartContainer.innerHTML = '<p>No soil samples available</p>';
            return;
        }

        // Prepare chart data
        const labels = soilSamples.map(sample => 
            new Date(sample.collection_date).toLocaleDateString()
        );
        
        const datasets = [
            {
                label: 'Financial Index Score',
                data: soilSamples.map(sample => sample.financial_index_score),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            },
            {
                label: 'pH Level',
                data: soilSamples.map(sample => sample.ph_level),
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }
        ];

        // Create canvas
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);

        // Create chart
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Soil Samples Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }

    createCropDistributionChart(cropDistribution) {
        // This could be implemented similar to soil samples chart
        // For brevity, I'll skip the full implementation
        console.log('Crop Distribution:', cropDistribution);
    }

    changePage(direction) {
        const newPage = this.currentPage + direction;
        
        // Validate page bounds
        if (newPage < 1 || newPage > this.totalPages) {
            return;
        }

        this.currentPage = newPage;
        this.loadFarmers();
    }

    updatePaginationControls() {
        // Update pagination buttons and current page text
        this.prevPageBtn.disabled = this.currentPage === 1;
        this.nextPageBtn.disabled = this.currentPage === this.totalPages;
        this.currentPageSpan.textContent = `Page ${this.currentPage} of ${this.totalPages}`;
    }

    closeDetailsModal() {
        this.farmerDetailsModal.style.display = 'none';
    }

    showAddFarmerModal() {
        // Placeholder for add farmer functionality
        alert('Add Farmer functionality to be implemented');
    }

    showErrorNotification(message) {
        // Use Toastify or a similar notification library
        if (typeof Toastify !== 'undefined') {
            Toastify({
                text: message,
                duration: 3000,
                gravity: "top",
                position: "right",
                backgroundColor: "#FF0000",
            }).showToast();
        } else {
            alert(message);
        }
    }
}

// Initialize the Farmers Management Page
document.addEventListener('DOMContentLoaded', () => {
    window.farmersManager = new FarmersManager();
});