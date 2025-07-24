# MIGRATION_GUIDE.md

# Talazo AgriFinance Platform - Code Reorganization Guide

## Overview

This document outlines the reorganization of the Talazo AgriFinance Platform codebase to improve maintainability, scalability, and code organization.

## Old vs New Structure

### Before (Disorganized)

```
fintech-talazo/
├── app.py (monolithic file with 1500+ lines)
├── app_factory.py
├── config.py
├── farm_viability_scorer.py
├── demo.py
├── demo_server.py
├── talazo/ (conflicting structure)
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── various other files
├── app/ (partial structure)
│   ├── __init__.py
│   └── models.py
└── various loose files
```

### After (Organized)

```
fintech-talazo/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── api/                     # API blueprints
│   │   ├── __init__.py
│   │   ├── main.py              # Dashboard & health routes
│   │   ├── farmers.py           # Farmer management API
│   │   ├── scoring.py           # Farm scoring API
│   │   ├── soil.py              # Soil sample API
│   │   ├── loans.py             # Loan management API
│   │   ├── auth.py              # Authentication API
│   │   └── iot.py               # IoT/sensor data API
│   ├── core/                    # Core application modules
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── extensions.py        # Flask extensions
│   │   ├── errors.py            # Error handlers
│   │   └── cli.py               # CLI commands
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── farmer.py
│   │   ├── soil_sample.py
│   │   ├── credit_history.py
│   │   ├── loan_application.py
│   │   └── insurance_policy.py
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── farm_viability_scorer.py
│   │   ├── soil_analyzer.py
│   │   ├── risk_assessment.py
│   │   └── ml_predictor.py
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── validators.py
│       ├── formatters.py
│       └── helpers.py
├── static/                      # Static assets (CSS, JS, images)
├── templates/                   # HTML templates
├── instance/                    # Instance-specific files (databases, logs)
├── migrations/                  # Database migrations
├── tests/                       # Test files
├── run.py                       # Development server entry point
├── wsgi.py                      # Production WSGI entry point
└── config.py                    # Legacy config (deprecated)
```

## Key Changes

### 1. Application Factory Pattern

- **Before**: Multiple conflicting app creation methods
- **After**: Single, clean application factory in `app/__init__.py`

### 2. Blueprint Organization

- **Before**: All routes in one massive file
- **After**: Organized into logical API blueprints by functionality

### 3. Model Organization

- **Before**: All models in one file, scattered across multiple locations
- **After**: Each model in its own file with proper schemas

### 4. Service Layer

- **Before**: Business logic mixed with route handlers
- **After**: Clean separation with dedicated service classes

### 5. Configuration Management

- **Before**: Multiple config files with inconsistent patterns
- **After**: Centralized configuration with environment-specific settings

### 6. Error Handling

- **Before**: Inconsistent error responses
- **After**: Standardized error handling across all endpoints

## Migration Steps for Developers

### 1. Update Imports

**Old imports:**

```python
from app import create_app
from app.models import Farmer
from talazo.soil_analyzer import SoilHealthIndex
```

**New imports:**

```python
from app import create_app
from app.models import Farmer, SoilSample, CreditHistory
from app.services import FarmViabilityScorer, SoilAnalyzer
```

### 2. Configuration Updates

**Old configuration:**

```python
from config import Config
app.config.from_object(Config)
```

**New configuration:**

```python
from app.core.config import get_config
config_class = get_config()
app.config.from_object(config_class)
```

### 3. Database Model Updates

**Old model usage:**

```python
from app.models import db, Farmer
farmer = Farmer.query.first()
```

**New model usage:**

```python
from app.models import db, Farmer
from app.core.extensions import db
farmer = Farmer.query.first()
```

### 4. API Endpoint Updates

**Old endpoints:**

- `/api/calculate-index` → `/api/scoring/calculate`
- `/api/realtime-data` → `/api/iot/realtime-data`
- Various farmer endpoints → `/api/farmers/*`

### 5. Service Usage

**Old service usage:**

```python
# Direct instantiation in routes
scorer = SoilHealthIndex()
score = scorer.calculate_score(data)
```

**New service usage:**

```python
# Import and use service
from app.services import FarmViabilityScorer
scorer = FarmViabilityScorer()
result = scorer.calculate_comprehensive_score(farmer_id)
```

## API Changes

### New Endpoint Structure

| Functionality    | Old Endpoint           | New Endpoint                    |
| ---------------- | ---------------------- | ------------------------------- |
| Health Check     | `/test`                | `/api/healthcheck`              |
| Farm Scoring     | `/api/calculate-index` | `/api/scoring/calculate`        |
| Loan Eligibility | N/A                    | `/api/scoring/loan-eligibility` |
| Farmer List      | N/A                    | `/api/farmers/`                 |
| Farmer Details   | N/A                    | `/api/farmers/{id}`             |
| Soil Samples     | N/A                    | `/api/soil/samples`             |
| Dashboard Data   | N/A                    | `/api/dashboard/summary`        |

### Response Format Standardization

**Old response format:**

```json
{
  "credit_score": 75.5,
  "risk_level": "Medium",
  "error": "Some error"
}
```

**New response format:**

```json
{
  "success": true,
  "message": "Success message",
  "data": {
    "overall_score": 75.5,
    "risk_level": "MEDIUM"
  }
}
```

## Database Changes

### Model Improvements

1. **Enhanced Validation**: All models now include proper validation
2. **Computed Properties**: Models include calculated fields (scores, ratios)
3. **Better Relationships**: Improved foreign key relationships
4. **Schemas**: Marshmallow schemas for serialization/validation

### Migration Required

Run these commands to update your database:

```bash
# Initialize database
flask init-db

# Or if using migrations
flask db upgrade
```

## Environment Variables

### Required Environment Variables

```bash
# Flask configuration
FLASK_ENV=development  # or production
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///instance/talazo.db

# External APIs (optional)
GROQ_API_KEY=your-groq-api-key
SATELLITE_API_KEY=your-satellite-api-key
```

## Testing the Migration

### 1. Basic Health Check

```bash
curl http://localhost:5000/api/healthcheck
```

### 2. Test Farmer API

```bash
# List farmers
curl http://localhost:5000/api/farmers/

# Get farmer details
curl http://localhost:5000/api/farmers/1
```

### 3. Test Scoring API

```bash
curl -X POST http://localhost:5000/api/scoring/calculate \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": 1}'
```

## Benefits of New Structure

1. **Maintainability**: Clear separation of concerns
2. **Scalability**: Easy to add new features and endpoints
3. **Testability**: Isolated components are easier to test
4. **Documentation**: Self-documenting code structure
5. **Collaboration**: Multiple developers can work on different modules
6. **Performance**: Better code organization improves performance
7. **Security**: Centralized security and validation
8. **Monitoring**: Better error handling and logging

## Backwards Compatibility

- Legacy configuration file is maintained for compatibility
- Old import paths will show deprecation warnings but still work
- Gradual migration is possible - no need to change everything at once

## Next Steps

1. **Update existing code** to use new import paths
2. **Add comprehensive tests** for all new modules
3. **Implement authentication** in the auth module
4. **Add real IoT integration** in the iot module
5. **Enhance loan processing** in the loans module
6. **Add monitoring and logging** improvements

## Support

If you encounter issues during migration:

1. Check the error logs in `logs/talazo.log`
2. Verify environment variables are set correctly
3. Ensure database is properly initialized
4. Check import paths match new structure
5. Refer to this guide for API endpoint changes
