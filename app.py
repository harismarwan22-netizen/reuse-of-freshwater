"""
Flask Application
Water Recovery and Reuse Monitoring System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime
import json

# Import model
from model import water_model, LABELS

app = Flask(__name__)

# Database configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create water_quality table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ph REAL NOT NULL,
            turbidity REAL NOT NULL,
            temperature REAL NOT NULL,
            tds REAL NOT NULL,
            prediction INTEGER NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL
        )
    ''')
    
    # Create recovery_stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recovery_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            water_recovered_liters REAL NOT NULL,
            water_treated_liters REAL NOT NULL,
            water_reused_liters REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Home page with input form"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict water quality using AI model"""
    try:
        # Get form data
        ph = float(request.form.get('ph', 0))
        turbidity = float(request.form.get('turbidity', 0))
        temperature = float(request.form.get('temperature', 0))
        tds = float(request.form.get('tds', 0))
        
        # Get prediction from model
        result = water_model.predict(ph, turbidity, temperature, tds)
        
        if 'error' in result:
            return render_template('index.html', error=result['error'])
        
        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO water_quality 
            (timestamp, ph, turbidity, temperature, tds, prediction, label, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, ph, turbidity, temperature, tds, 
              result['prediction'], result['label'], result['confidence']))
        
        conn.commit()
        conn.close()
        
        return render_template('index.html', 
                             result=result,
                             ph=ph,
                             turbidity=turbidity,
                             temperature=temperature,
                             tds=tds,
                             result_label=result.get('label', ''),
                             confidence=result.get('confidence', 0),
                             safe_pct=result.get('probabilities', {}).get('Safe for Reuse', 0),
                             treatment_pct=result.get('probabilities', {}).get('Needs Treatment', 0),
                             unsafe_pct=result.get('probabilities', {}).get('Unsafe', 0))
    
    except Exception as e:
        return render_template('index.html', error=str(e))

@app.route('/dashboard')
def dashboard():
    """Display analytics dashboard"""
    try:
        conn = get_db_connection()
        
        # Get recent water quality readings
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM water_quality 
            ORDER BY id DESC LIMIT 50
        ''')
        readings = cursor.fetchall()
        
        # Get statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN label = 'Safe for Reuse' THEN 1 ELSE 0 END) as safe_count,
                SUM(CASE WHEN label = 'Needs Treatment' THEN 1 ELSE 0 END) as treatment_count,
                SUM(CASE WHEN label = 'Unsafe' THEN 1 ELSE 0 END) as unsafe_count,
                AVG(ph) as avg_ph,
                AVG(turbidity) as avg_turbidity,
                AVG(temperature) as avg_temperature,
                AVG(tds) as avg_tds
            FROM water_quality
        ''')
        stats = cursor.fetchone()
        
        # Get daily statistics
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as count,
                AVG(ph) as avg_ph,
                AVG(turbidity) as avg_turbidity,
                AVG(temperature) as avg_temperature,
                AVG(tds) as avg_tds
            FROM water_quality
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 7
        ''')
        daily_stats = cursor.fetchall()
        
        conn.close()
        
        # Calculate recovery metrics
        total_readings = stats['total'] if stats['total'] else 0
        safe_count = stats['safe_count'] if stats['safe_count'] else 0
        treatment_count = stats['treatment_count'] if stats['treatment_count'] else 0
        
        # Simulated recovery data
        water_recovered = safe_count * 100  # liters per safe reading
        water_treated = treatment_count * 80  # liters per treatment needed
        water_reused = safe_count * 85  # liters actually reused
        
        return render_template('dashboard.html',
                             readings=readings,
                             stats=stats,
                             daily_stats=daily_stats,
                             water_recovered=water_recovered,
                             water_treated=water_treated,
                             water_reused=water_reused)
    
    except Exception as e:
        return render_template('dashboard.html', error=str(e))

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for prediction"""
    try:
        data = request.get_json()
        
        ph = float(data.get('ph', 0))
        turbidity = float(data.get('turbidity', 0))
        temperature = float(data.get('temperature', 0))
        tds = float(data.get('tds', 0))
        
        result = water_model.predict(ph, turbidity, temperature, tds)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN label = 'Safe for Reuse' THEN 1 ELSE 0 END) as safe_count,
                SUM(CASE WHEN label = 'Needs Treatment' THEN 1 ELSE 0 END) as treatment_count,
                SUM(CASE WHEN label = 'Unsafe' THEN 1 ELSE 0 END) as unsafe_count,
                AVG(ph) as avg_ph,
                AVG(turbidity) as avg_turbidity,
                AVG(temperature) as avg_temperature,
                AVG(tds) as avg_tds
            FROM water_quality
        ''')
        stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'total': stats['total'] if stats['total'] else 0,
            'safe_count': stats['safe_count'] if stats['safe_count'] else 0,
            'treatment_count': stats['treatment_count'] if stats['treatment_count'] else 0,
            'unsafe_count': stats['unsafe_count'] if stats['unsafe_count'] else 0,
            'avg_ph': round(stats['avg_ph'], 2) if stats['avg_ph'] else 0,
            'avg_turbidity': round(stats['avg_turbidity'], 2) if stats['avg_turbidity'] else 0,
            'avg_temperature': round(stats['avg_temperature'], 2) if stats['avg_temperature'] else 0,
            'avg_tds': round(stats['avg_tds'], 2) if stats['avg_tds'] else 0
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/history')
def api_history():
    """API endpoint for historical data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM water_quality 
            ORDER BY id DESC LIMIT 100
        ''')
        readings = cursor.fetchall()
        
        data = []
        for row in readings:
            data.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'ph': row['ph'],
                'turbidity': row['turbidity'],
                'temperature': row['temperature'],
                'tds': row['tds'],
                'prediction': row['prediction'],
                'label': row['label'],
                'confidence': row['confidence']
            })
        
        conn.close()
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Check if model is loaded
    if water_model.is_trained():
        print("AI Model loaded successfully!")
    else:
        print("Warning: Model not loaded. Please run train_model.py first!")
    
    # Run Flask app
    print("\n" + "="*50)
    print("Water Recovery and Reuse Monitoring System")
    print("="*50)
    print("Server running at: http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    app.run(debug=True)
