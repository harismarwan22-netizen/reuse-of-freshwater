# Fresh Water Recovery & Reuse System

An intelligent water recovery and reuse monitoring system that uses AI and IoT to classify water quality and track recovery metrics.

## Features

- **Simulates wastewater collection** with realistic sensor data
- **Monitors water quality parameters**: pH, Turbidity, Temperature, TDS
- **AI-powered classification** into Safe for Reuse, Needs Treatment, or Unsafe
- **Real-time monitoring dashboard** with interactive charts
- **SQLite database** for storing sensor readings
- **Water recovery analytics** and statistics

## Tech Stack

- **Backend**: Python 3, Flask Framework
- **AI Model**: Scikit-learn (RandomForestClassifier)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite
- **Visualization**: Chart.js

## Project Structure

```
water_recovery_project/
├── app.py                  # Flask application
├── model.py               # AI model prediction module
├── train_model.py        # Model training script
├── requirements.txt      # Python dependencies
├── water_model.pkl      # Trained ML model (generated)
├── scaler.pkl           # Feature scaler (generated)
├── database.db          # SQLite database (generated)
├── templates/
│   ├── index.html       # Home page with input form
│   └── dashboard.html   # Analytics dashboard
├── static/
│   ├── style.css        # Custom styles
│   └── script.js       # JavaScript functionality
└── README.md           # This file
```

## Installation & Setup

### 1. Create Virtual Environment

```
bash
cd water_recovery_project
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```
bash
venv\Scripts\activate
```

**Mac/Linux:**
```
bash
source venv/bin/activate
```

### 3. Install Requirements

```
bash
pip install -r requirements.txt
```

### 4. Train the AI Model

```
bash
python train_model.py
```

This will:
- Generate 1000 sample water quality records
- Train a RandomForestClassifier
- Save the model as `water_model.pkl`
- Save the scaler as `scaler.pkl`
- Create sample data CSV

### 5. Run the Flask Server

```
bash
python app.py
```

### 6. Open in Browser

Navigate to: **http://127.0.0.1:5000**

## Usage

### Home Page (Input Form)
1. Enter sensor readings:
   - pH Level (0-14)
   - Turbidity (NTU)
   - Temperature (°C)
   - TDS (mg/L)
2. Click "Predict Water Quality"
3. View the AI prediction and confidence score

### Dashboard
1. Click "Dashboard" in the navigation
2. View statistics:
   - Total readings
   - Safe for Reuse count
   - Needs Treatment count
   - Unsafe count
   - Water Recovered (L)
   - Water Treated (L)
   - Water Reused (L)
3. View interactive charts:
   - Water Quality Distribution (Pie chart)
   - Average Parameters (Bar chart)
   - Historical Trends (Line chart)
4. View recent readings table

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/predict` | POST | Predict water quality |
| `/dashboard` | GET | Analytics dashboard |
| `/api/predict` | POST | JSON API for prediction |
| `/api/stats` | GET | JSON API for statistics |
| `/api/history` | GET | JSON API for historical data |

## Water Quality Parameters

| Parameter | Safe Range | Unit |
|-----------|------------|------|
| pH | 6.5 - 8.5 | - |
| Turbidity | < 10 | NTU |
| Temperature | 15 - 30 | °C |
| TDS | < 500 | mg/L |

## AI Classification

The system uses a RandomForestClassifier to categorize water into:

1. **Safe for Reuse** - Meets all quality parameters
2. **Needs Treatment** - Requires processing before use
3. **Unsafe** - Not suitable for any use

## Expected Output

### Training Output
```
Generating sample water quality dataset...
Dataset shape: (1000, 5)

Label distribution:
0    156
1    532
2    312

Training RandomForestClassifier...
Training accuracy: 0.9988
Test accuracy: 0.9700

Model saved to: water_model.pkl
Scaler saved to: scaler.pkl

Model training completed successfully!
```

### Server Output
```
Database initialized successfully!
AI Model loaded successfully!

==================================================
Water Recovery and Reuse Monitoring System
==================================================
Server running at: http://127.0.0.1:5000
==================================================
```

## Screenshots Description

### Home Page
- Navigation bar with system title
- Input form with 4 sensor fields
- Parameter range hints
- Prediction result card with:
  - Classification label (color-coded)
  - Confidence percentage
  - Probability distribution bars
  - Input summary

### Dashboard
- Statistics cards (4 cards)
- Recovery metrics cards (3 cards)
- Water Quality Distribution (doughnut chart)
- Average Parameters (bar chart)
- Historical Trends (line chart)
- Recent Readings table

## Troubleshooting

### Model not found error
Run `python train_model.py` first to generate the model files.

### Port already in use
Change the port in `app.py`:
```
python
app.run(debug=True, port=5001)
```

### Database error
The database is automatically created on first run. If issues persist, delete `database.db` and restart.

## License

This project is for educational purposes.

## Author

Created as a demonstration of AI and IoT integration for environmental monitoring.
