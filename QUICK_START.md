# 🚀 Quick Start Guide - Talazo AgriFinance Platform

## Prerequisites

- Python 3.9+ (Currently using 3.13.1)
- Virtual environment (already set up as `fintech-agric`)

## 1. Start the Application

```bash
# From the project root directory
python run.py
```

You should see:

```
============================================================
🌱 Talazo AgriFinance Platform Starting...
============================================================
📊 Dashboard URL: http://localhost:5000/dashboard
📡 API Base URL: http://localhost:5000/api
🏥 Health Check: http://localhost:5000/api/healthcheck
============================================================
✓ Database initialized
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

## 2. Test the System

### Health Check

```bash
curl http://localhost:5000/api/healthcheck
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-07-23T20:45:00.000Z",
  "version": "1.0.0",
  "database": "healthy",
  "statistics": {
    "total_farmers": 0,
    "total_soil_samples": 0,
    "recent_samples": 0
  }
}
```

### Create Demo Data

```bash
# In a new terminal, activate virtual environment
cd c:\Users\dell\Desktop\Code\fintech-talazo
fintech-agric\Scripts\activate.ps1

# Create demo farmers
flask create-demo-data --num-farmers 10
```

## 3. Main API Endpoints

### Farmers API

```bash
# Get all farmers
curl http://localhost:5000/api/farmers

# Get farmer by ID
curl http://localhost:5000/api/farmers/1

# Create new farmer
curl -X POST http://localhost:5000/api/farmers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Mukamuri",
    "email": "john@example.com",
    "phone_number": "+263771234567",
    "farm_size_hectares": 5.0,
    "location": "Harare",
    "crop_type": "maize"
  }'
```

### Soil Analysis API

```bash
# Analyze soil sample
curl -X POST http://localhost:5000/api/soil/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": 1,
    "ph_level": 6.5,
    "nitrogen_level": 45,
    "phosphorus_level": 25,
    "potassium_level": 180,
    "organic_matter": 3.2,
    "moisture_content": 22
  }'
```

### Farm Viability Scoring

```bash
# Calculate farm viability score
curl -X POST http://localhost:5000/api/scoring/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": 1,
    "soil_health_score": 75.5,
    "farm_size": 5.0,
    "farming_experience": 8,
    "crop_diversity": 3,
    "location_risk": "medium"
  }'
```

## 4. Directory Structure Overview

```
fintech-talazo/
├── app/                    # Main application (NEW, ORGANIZED)
│   ├── api/               # REST API endpoints
│   ├── core/              # Core components
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── instance/              # Instance-specific files
├── migrations/            # Database migrations
├── static/               # Static web assets
├── templates/            # HTML templates
├── tests/                # Test files
├── run.py                # Application entry point
├── wsgi.py               # WSGI entry point
└── requirements.txt      # Python dependencies
```

## 5. Development Workflow

### Run Tests

```bash
python test_reorganized_app.py
```

### Check Code Quality

```bash
python simple_test.py
```

### Export Data

```bash
flask export-data
```

### Train ML Models

```bash
flask train-models
```

## 6. Common Issues & Solutions

### Issue: Import Errors

**Solution**: Ensure virtual environment is activated

```bash
fintech-agric\Scripts\activate.ps1
```

### Issue: Database Errors

**Solution**: Reinitialize database

```bash
flask init-db
```

### Issue: Port Already in Use

**Solution**: Change port in run.py or kill existing process

```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 7. Production Deployment

### Environment Variables

Create `.env` file:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/talazo_prod
```

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
```

---

🎉 **You're all set!** The Talazo AgriFinance Platform is now running and ready for use.
