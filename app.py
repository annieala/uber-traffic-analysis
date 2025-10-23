from flask import Flask, request, jsonify
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

app = Flask(__name__)

# Load the CSV file
print("Loading data...")
df = pd.read_csv("Uber-Jan-Feb-FOIL.csv")
print(f"Initial data shape: {df.shape}")

# Clean the data
print("\nCleaning data...")
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)
print(f"Final data shape: {df.shape}")

# Convert 'Pickup_date' column to datetime
print("\nConverting Pickup_date column...")
df['Pickup_date'] = pd.to_datetime(df['Pickup_date'])

# Feature extraction
print("\nExtracting features...")
df['Hour'] = df['Pickup_date'].dt.hour
df['Day'] = df['Pickup_date'].dt.date
df['DayOfWeek'] = df['Pickup_date'].dt.day_name()
df['IsWeekend'] = df['DayOfWeek'].isin(['Saturday', 'Sunday'])

# Aggregation
daily_trips = df.groupby('Day').size()
hourly_trips = df.groupby('Hour').size()

print("\nData loaded and processed successfully!")

# Flask routes
@app.route('/')
def home():
    return "Uber Traffic Analysis App - Data Loaded Successfully!"

@app.route('/predict_traffic', methods=['GET'])
def predict_traffic():
    try:
        timestamp = request.args.get('timestamp')
        if not timestamp:
            return jsonify({'error': 'No timestamp provided'}), 400
       
        dt = pd.to_datetime(timestamp, errors='coerce')
        if pd.isna(dt):
            return jsonify({'error': f'Invalid timestamp format: {timestamp}'}), 400
       
        hour = int(dt.hour)
        day_of_week = dt.day_name()
        traffic_count = int(hourly_trips.get(hour, 0))
       
        return jsonify({
            'timestamp': str(timestamp),
            'hour': hour,
            'day_of_week': day_of_week,
            'predicted_trips': traffic_count,
            'status': 'success'
        }), 200
       
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\nStarting Flask server...")
    print("API Endpoints:")
    print("  - http://0.0.0.0:5000/")
    print("  - http://0.0.0.0:5000/predict_traffic?timestamp=YYYY-MM-DD HH:MM:SS")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
