// add_farmer.js
class FarmerRegistrationForm {
    constructor() {
        // Form and input elements
        this.form = document.getElementById('add-farmer-form');
        this.fullNameInput = document.getElementById('full_name');
        this.nationalIdInput = document.getElementById('national_id');
        this.phoneInput = document.getElementById('phone_number');
        this.emailInput = document.getElementById('email');
        this.primaryCropSelect = document.getElementById('primary_crop');
        this.landAreaInput = document.getElementById('total_land_area');
        this.farmingExperienceInput = document.getElementById('farming_experience');
        this.regionSelect = document.getElementById('location_region');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.cancelBtn = document.getElementById('cancel-btn');
        
        // Location inputs and map
        this.latInput = document.getElementById('location_lat');
        this.lngInput = document.getElementById('location_lng');
        this.locationMap = document.getElementById('location-map');

        // Bind events
        this.bindEvents();

        // Initialize map if Leaflet is available
        this.initMap();
    }

    bindEvents() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });

        // Username validation
        this.usernameInput.addEventListener('blur', () => this.validateUsername());

        // Cancel button
        this.cancelBtn.addEventListener('click', () => {
            window.location.href = '/farmers';
        });

        // Optional: Auto-generate username
        this.fullNameInput.addEventListener('blur', () => {
            if (!this.usernameInput.value) {
                this.generateUsername();
            }
        });

        // Phone number validation
        this.phoneInput.addEventListener('input', () => this.validatePhoneNumber());

        // National ID validation
        this.nationalIdInput.addEventListener('input', () => this.validateNationalID());
    }

    initMap() {
        // Check if Leaflet is available
        if (typeof L !== 'undefined') {
            // Create map centered on Zimbabwe
            this.map = L.map(this.locationMap).setView([-19.0154, 29.1549], 6);

            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            // Add click event to get coordinates
            this.map.on('click', (e) => {
                const { lat, lng } = e.latlng;
                this.latInput.value = lat.toFixed(4);
                this.lngInput.value = lng.toFixed(4);

                // Remove previous marker if exists
                if (this.marker) {
                    this.map.removeLayer(this.marker);
                }

                // Add new marker
                this.marker = L.marker([lat, lng]).addTo(this.map);
            });

            // Optional: Add geolocation support
            this.map.addControl(
                L.Control.extend({
                    options: {
                        position: 'topright'
                    },
                    onAdd: () => {
                        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                        const link = L.DomUtil.create('a', 'leaflet-control-locate', container);
                        link.href = '#';
                        link.title = 'Locate Me';
                        link.innerHTML = '<i class="fas fa-location-arrow"></i>';
                        
                        link.onclick = (e) => {
                            e.preventDefault();
                            this.getCurrentLocation();
                        };
                        
                        return container;
                    }
                })
            );
        }
    }

    getCurrentLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    
                    // Update inputs
                    this.latInput.value = latitude.toFixed(4);
                    this.lngInput.value = longitude.toFixed(4);

                    // Center and mark map
                    if (this.map) {
                        this.map.setView([latitude, longitude], 10);
                        
                        // Remove previous marker
                        if (this.marker) {
                            this.map.removeLayer(this.marker);
                        }

                        // Add new marker
                        this.marker = L.marker([latitude, longitude]).addTo(this.map);
                    }
                },
                (error) => {
                    this.showNotification('Error getting location: ' + error.message, 'error');
                }
            );
        } else {
            this.showNotification('Geolocation is not supported by this browser.', 'warning');
        }
    }

    generateUsername() {
        // Generate username from full name
        const fullName = this.fullNameInput.value.trim();
        if (fullName) {
            // Remove spaces and convert to lowercase
            const baseUsername = fullName.toLowerCase().replace(/\s+/g, '');
            
            // Add random numbers to make it unique
            const randomNum = Math.floor(1000 + Math.random() * 9000);
            const suggestedUsername = `${baseUsername}${randomNum}`;
            
            this.usernameInput.value = suggestedUsername;
        }
    }

    validateUsername() {
        const username = this.usernameInput.value.trim();
        
        // Basic validation
        if (!username) {
            this.showNotification('Username cannot be empty', 'error');
            return false;
        }

        // Check username format (only alphanumeric)
        const usernameRegex = /^[a-zA-Z0-9_]+$/;
        if (!usernameRegex.test(username)) {
            this.showNotification('Username can only contain letters, numbers, and underscores', 'error');
            return false;
        }

        // Check with backend
        fetch(`/farmers/api/farmers/validate-username?username=${username}`)
            .then(response => response.json())
            .then(data => {
                if (!data.available) {
                    this.showNotification(data.message, 'error');
                    this.usernameInput.classList.add('is-invalid');
                } else {
                    this.usernameInput.classList.remove('is-invalid');
                }
            })
            .catch(error => {
                console.error('Username validation error:', error);
                this.showNotification('Error validating username', 'error');
            });
    }

    validatePhoneNumber() {
        const phoneNumber = this.phoneInput.value.trim();
        
        // Zimbabwe phone number validation (allow +263 or 07/08 formats)
        const phoneRegex = /^(\+263|0)(7|8)\d{8}$/;
        
        if (!phoneRegex.test(phoneNumber)) {
            this.phoneInput.classList.add('is-invalid');
            this.showNotification('Invalid Zimbabwean phone number format', 'error');
            return false;
        }
        
        this.phoneInput.classList.remove('is-invalid');
        return true;
    }

    validateNationalID() {
        const nationalId = this.nationalIdInput.value.trim();
        
        // Zimbabwe National ID format: XX-XXXXXX-X-XX
        const nationalIdRegex = /^\d{2}-\d{6}-[A-Z]-\d{2}$/;
        
        if (!nationalIdRegex.test(nationalId)) {
            this.nationalIdInput.classList.add('is-invalid');
            this.showNotification('Invalid National ID format (Use XX-XXXXXX-X-XX)', 'error');
            return false;
        }
        
        this.nationalIdInput.classList.remove('is-invalid');
        return true;
    }

    validateForm() {
        let isValid = true;

        // Validate each required field
        const requiredFields = [
            this.fullNameInput,
            this.nationalIdInput,
            this.phoneInput,
            this.primaryCropSelect,
            this.landAreaInput,
            this.farmingExperienceInput,
            this.usernameInput,
            this.passwordInput
        ];

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Additional specific validations
        isValid = this.validatePhoneNumber() && isValid;
        isValid = this.validateNationalID() && isValid;

        // Validate password strength
        if (this.passwordInput.value.length < 8) {
            this.passwordInput.classList.add('is-invalid');
            this.showNotification('Password must be at least 8 characters long', 'error');
            isValid = false;
        }

        return isValid;
    }

    submitForm() {
        // Validate form before submission
        if (!this.validateForm()) {
            return;
        }

        // Collect form data
        const formData = {
            full_name: this.fullNameInput.value.trim(),
            national_id: this.nationalIdInput.value.trim(),
            phone_number: this.phoneInput.value.trim(),
            email: this.emailInput.value.trim(),
            primary_crop: this.primaryCropSelect.value,
            total_land_area: parseFloat(this.landAreaInput.value),
            farming_experience: parseInt(this.farmingExperienceInput.value),
            location_region: this.regionSelect.value,
            username: this.usernameInput.value.trim(),
            password: this.passwordInput.value,
            address: document.getElementById('address').value.trim(),
            location_lat: this.latInput.value ? parseFloat(this.latInput.value) : null,
            location_lng: this.lngInput.value ? parseFloat(this.lngInput.value) : null
        };

        // Disable submit button and show loading state
        const submitButton = this.form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = 'Creating Profile... <i class="fas fa-spinner fa-spin"></i>';

        // Submit data to backend
        fetch('/farmers/api/farmers/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Farmer profile created successfully', 'success');
                
                // Redirect to farmers list or detail page after a short delay
                setTimeout(() => {
                    window.location.href = `/farmers/details/${data.farmer_id}`;
                }, 2000);
            } else {
                // Show error message
                this.showNotification(data.message || 'Failed to create farmer profile', 'error');
                
                // Re-enable submit button
                submitButton.disabled = false;
                submitButton.innerHTML = 'Create Farmer Profile';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Network error. Please try again.', 'error');
            
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.innerHTML = 'Create Farmer Profile';
        });
    }

    showNotification(message, type = 'info') {
        // Use Toastify for notifications
        if (typeof Toastify !== 'undefined') {
            const backgroundColor = {
                success: '#28a745',
                error: '#dc3545',
                warning: '#ffc107',
                info: '#17a2b8'
            }[type];

            Toastify({
                text: message,
                duration: 3000,
                close: true,
                gravity: 'top',
                position: 'right',
                backgroundColor: backgroundColor
            }).showToast();
        } else {
            // Fallback to browser alert
            alert(message);
        }
    }
}

// Initialize the form when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.farmerRegistrationForm = new FarmerRegistrationForm();
});