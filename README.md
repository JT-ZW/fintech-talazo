# Talazo AgriFinance Platform

A prototype system that helps Zimbabwean small-scale farmers access financial services through soil health metrics. The platform analyzes soil data to calculate a financial index score, assess creditworthiness, and recommend appropriate insurance premiums.

## 🌱 Features

- **Real-time Soil Monitoring**: Simulate sensors for soil data collection
- **Financial Index Calculation**: Convert soil health metrics into financial indices
- **AI-Driven Recommendations**: Generate context-aware farming recommendations
- **Crop Yield Prediction**: Machine learning models to predict harvest yields
- **Risk Assessment**: Calculate insurance premiums based on soil health
- **Interactive Dashboard**: Visualize soil health and financial insights
- **Data Simulation**: Generate realistic demo data for testing

## 📋 System Requirements

- Python 3.8 or higher
- Flask 2.0+
- SQLAlchemy 1.4+
- Scikit-learn 0.24+
- Node.js 14+ (for frontend development)

## 🚀 Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/talazo-agrifinance.git
   cd talazo-agrifinance
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   ```

4. Initialize the development environment:

   ```bash
   python scripts/init_dev.py
   ```

5. Generate demo data:
   ```bash
   flask simulation generate-demo-data --num-farmers 50
   ```

### Configuration

1. Set up your environment variables by editing the `.env` file:

   ```
   FLASK_APP=talazo
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///instance/talazo.db
   GROQ_API_KEY=your_groq_api_key_here
   ```

2. For AI-powered recommendations, get an API key from [Groq](https://console.groq.com) and update the `.env` file.

### Running the Application

1. Start the development server:

   ```bash
   flask run
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Demo Users

After initialization, the following users are available:

- **Admin**: Username: `admin`, Password: `admin123`
- **Farmers**: Various demo farmer accounts (see console output for details)

## 📊 Dashboard

The dashboard provides:

- Real-time soil health monitoring
- Financial index score visualization
- Crop recommendations based on soil conditions
- AI-driven farming recommendations
- Alerts for critical soil parameters
- Historical trend analysis

## 🧪 Simulation

The system includes robust simulation components to demonstrate functionality without actual hardware:

- Soil sensor simulation with realistic values
- Weather event simulation (rain, drought, etc.)
- Seasonal variations in soil parameters
- Farm management simulation

### Generating Test Data

You can generate more test data using the CLI:

```bash
# Generate and save to database
flask simulation generate-demo-data --num-farmers 100

# Export to CSV files
flask simulation export-demo-data --output data
```

## 🌐 API Documentation

API documentation is available at:

```
http://localhost:5000/api/docs
```

## 📱 Mobile Interface

A progressive web app interface is available for farmers to:

- View soil health status
- Access recommendations
- Track financial index over time
- Request loans and insurance based on their score

## 🔄 Development Workflow

1. Set up your development environment
2. Create a feature branch
3. Implement your changes
4. Run tests
5. Submit a pull request

## 🛠️ Project Structure

```
talazo/
├── __init__.py          # Flask application factory
├── routes.py            # API and view routes
├── models.py            # Database models
├── soil_analyzer.py     # Soil health calculation
├── sensors.py           # Sensor simulation
├── ml_models.py         # Machine learning models
├── ai_recommendations.py # LLM integration
├── simulation.py        # Data simulation
├── cli.py               # Command-line interface
├── static/              # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── img/             # Images
└── templates/           # HTML templates
    ├── index.html       # Landing page
    ├── dashboard.html   # Main dashboard
    └── partials/        # Reusable template components
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- [Your Name](https://github.com/yourusername)
- [Contributor Name](https://github.com/contributor)

## 🙏 Acknowledgements

- [Africa University](https://www.africau.edu) for research collaboration
- Small-scale farmers in Zimbabwe who provided insights
- [Agricultural Research Trust](https://www.art.org.zw) for soil science expertise
