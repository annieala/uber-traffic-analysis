from flask import Flask, request, jsonify
import pandas as pd
import redis
import json
from datetime import datetime
import os

app = Flask(__name__)

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
USE_SSL = os.getenv('REDIS_SSL', 'False').lower() == 'true'

# Connect to Redis
print("\n" + "="*50)
print("INITIALIZING REDIS CONNECTION")
print("="*50)
try:
    if REDIS_PASSWORD:
        # Azure Redis with SSL
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            ssl=USE_SSL,
            decode_responses=True,
            socket_connect_timeout=5
        )
    else:
        # Local Redis without password
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5
        )
    
    # Test connection
    redis_client.ping()
    print(f"✓ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    redis_available = True
except Exception as e:
    print(f"✗ Redis connection failed: {e}")
    print("  Application will run without caching")
    redis_client = None
    redis_available = False

# Load and process Uber data
print("\n" + "="*50)
print("LOADING UBER DATASET")
print("="*50)

try:
    # Load the CSV file
    print("Loading data from CSV...")
    df = pd.read_csv("Uber-Jan-Feb-FOIL.csv")
    print(f"✓ Initial data shape: {df.shape}")

    # Clean the data
    print("\nCleaning data...")
    initial_rows = len(df)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    cleaned_rows = len(df)
    print(f"✓ Removed {initial_rows - cleaned_rows} rows")
    print(f"✓ Final data shape: {df.shape}")

    # Convert 'Pickup_date' column to datetime
    print("\nConverting Pickup_date column...")
    df['Pickup_date'] = pd.to_datetime(df['Pickup_date'])
    print("✓ Date conversion complete")

    # Feature extraction
    print("\nExtracting features...")
    df['Hour'] = df['Pickup_date'].dt.hour
    df['Day'] = df['Pickup_date'].dt.date
    df['DayOfWeek'] = df['Pickup_date'].dt.day_name()
    df['IsWeekend'] = df['DayOfWeek'].isin(['Saturday', 'Sunday'])
    print("✓ Features extracted")

    # Aggregation for predictions
    print("\nAggregating trip data...")
    daily_trips = df.groupby('Day').size()
    hourly_trips = df.groupby('Hour').size()
    day_hour_trips = df.groupby(['DayOfWeek', 'Hour']).size()
    print(f"✓ Found data for {len(hourly_trips)} unique hours")
    print(f"✓ Found data for {len(daily_trips)} unique days")

    # Calculate statistics
    total_trips = len(df)
    avg_hourly = hourly_trips.mean()
    peak_hour = hourly_trips.idxmax()
    peak_trips = hourly_trips.max()

    print(f"\nDataset Statistics:")
    print(f"  Total trips: {total_trips:,}")
    print(f"  Average trips per hour: {avg_hourly:.1f}")
    print(f"  Peak hour: {peak_hour}:00 with {peak_trips:,} trips")
    
    data_loaded = True
    print("\n✓ Data loaded and processed successfully!")

except FileNotFoundError:
    print("✗ ERROR: Uber-Jan-Feb-FOIL.csv not found")
    print("  Application will use simulated data")
    data_loaded = False
    df = None
    hourly_trips = None
    day_hour_trips = None
except Exception as e:
    print(f"✗ ERROR loading data: {e}")
    print("  Application will use simulated data")
    data_loaded = False
    df = None
    hourly_trips = None
    day_hour_trips = None

print("="*50)


# Flask routes
@app.route('/')
def home():
    status = {
        "message": "Uber Traffic Prediction API with Redis Caching",
        "data_loaded": data_loaded,
        "redis_available": redis_available,
        "endpoints": {
            "/": "Home (this page)",
            "/health": "Health check",
            "/predict_traffic": "Predict traffic (GET with timestamp parameter)",
            "/cache/stats": "Redis cache statistics",
            "/cache/clear": "Clear cache (POST)",
            "/data/stats": "Dataset statistics"
        }
    }
    
    if data_loaded:
        status["dataset_info"] = {
            "total_trips": int(len(df)),
            "date_range": f"{df['Day'].min()} to {df['Day'].max()}"
        }
    
    return jsonify(status)


@app.route('/health')
def health():
    """Health check endpoint"""
    redis_status = "not_configured"
    
    if redis_client:
        try:
            redis_client.ping()
            redis_status = "connected"
        except Exception as e:
            redis_status = f"disconnected: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "redis": redis_status,
        "data_loaded": data_loaded,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/predict_traffic', methods=['GET'])
def predict_traffic():
    """
    Predict Uber traffic based on timestamp.
    Uses Redis caching to improve performance on repeated queries.
    
    Query parameter:
        timestamp: DateTime string (e.g., "2015-01-15 14:30:00" or "2015-01-15T14:30:00")
    
    Returns:
        JSON with predicted trips and metadata
    """
    try:
        # Get timestamp parameter
        timestamp = request.args.get('timestamp')
        if not timestamp:
            retur
