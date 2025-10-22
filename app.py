from flask import Flask, request, jsonify
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

app = Flask(__name__)

# Load the CSV file into a Pandas DataFrame
print("Loading data...")
df = pd.read_csv("Uber-Jan-Feb-FOIL.csv")
print(f"Initial data shape: {df.shape}")

# Display column names
print("\nColumn names:", df.columns.tolist())

# Clean the data by removing rows with missing values and duplicates
print("\nCleaning data...")
initial_rows = len(df)
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)
final_rows = len(df)
print(f"Removed {initial_rows - final_rows} rows (missing values and duplicates)")
print(f"Final data shape: {df.shape}")

# Convert 'Pickup_date' column to datetime object
print("\nConverting Pickup_date column...")
df['Pickup_date'] = pd.to_datetime(df['Pickup_date'])
print("Date/Time conversion complete")

# Feature extraction
print("\nExtracting features...")
df['Hour'] = df['Pickup_date'].dt.hour
df['Day'] = df['Pickup_date'].dt.date
df['DayOfWeek'] = df['Pickup_date'].dt.day_name()
df['IsWeekend'] = df['DayOfWeek'].isin(['Saturday', 'Sunday'])
print("Feature extraction complete")

# Preview and document data
print("\n" + "="*80)
print("DATA PREVIEW - df.head()")
print("="*80)
print(df.head())

print("\n" + "="*80)
print("DATA INFO - df.info()")
print("="*80)
df.info()

print("\n" + "="*80)
print("DATA STATISTICS - df.describe()")
print("="*80)
print(df.describe())

print("\n" + "="*80)
print("ADDITIONAL INSIGHTS")
print("="*80)
print(f"\nTotal number of records: {len(df)}")
print(f"Date range: {df['Pickup_date'].min()} to {df['Pickup_date'].max()}")
print(f"\nWeekend vs Weekday distribution:")
print(df['IsWeekend'].value_counts())
print(f"\nTraffic by Day of Week:")
print(df['DayOfWeek'].value_counts().sort_index())

# ============================================================================
# NEW SECTION: AGGREGATION AND ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("AGGREGATION - TRIPS BY DAY AND HOUR")
print("="*80)

# Aggregate/group data by day and hour
daily_trips = df.groupby('Day').size()
hourly_trips = df.groupby('Hour').size()

print("\nDaily Trips Summary:")
print(daily_trips)

print("\nHourly Trips Summary:")
print(hourly_trips)

# Find busiest day and peak hours
busiest_day = daily_trips.idxmax()
busiest_day_count = daily_trips.max()
peak_hour = hourly_trips.idxmax()
peak_hour_count = hourly_trips.max()

print("\n" + "="*80)
print("PEAK TRAFFIC ANALYSIS")
print("="*80)
print(f"\nBusiest Day: {busiest_day}")
print(f"Trips on Busiest Day: {busiest_day_count}")
print(f"\nPeak Hour: {peak_hour}:00")
print(f"Trips during Peak Hour: {peak_hour_count}")

# ============================================================================
# NEW SECTION: VISUALIZATIONS
# ============================================================================

print("\n" + "="*80)
print("GENERATING VISUALIZATIONS")
print("="*80)

# Set style for better-looking plots
sns.set_style("whitegrid")

# 1. Bar chart: Trip counts by Day
print("\n1. Creating bar chart for Daily Trips...")
plt.figure(figsize=(12, 6))
daily_trips.plot(kind='bar', color='steelblue')
plt.title('Trip Counts by Day', fontsize=16, fontweight='bold')
plt.xlabel('Day', fontsize=12)
plt.ylabel('Number of Trips', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('daily_trips_chart.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved as: daily_trips_chart.png")
plt.close()

# 2. Bar chart: Trip counts by Hour
print("\n2. Creating bar chart for Hourly Trips...")
plt.figure(figsize=(12, 6))
hourly_trips.plot(kind='bar', color='coral')
plt.title('Trip Counts by Hour of Day', fontsize=16, fontweight='bold')
plt.xlabel('Hour', fontsize=12)
plt.ylabel('Number of Trips', fontsize=12)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('hourly_trips_chart.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved as: hourly_trips_chart.png")
plt.close()

# 3. Heatmap: Trip frequency by Day of Week and Hour
print("\n3. Creating heatmap for Trip Frequency by Day and Hour...")
plt.figure(figsize=(14, 8))
heatmap_data = df.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)

# Reorder days of week
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = heatmap_data.reindex(day_order)

sns.heatmap(heatmap_data, cmap='viridis', annot=False, fmt='d', linewidths=0.5)
plt.title('Trip Frequency by Day and Hour', fontsize=16, fontweight='bold')
plt.xlabel('Hour of Day', fontsize=12)
plt.ylabel('Day of Week', fontsize=12)
plt.tight_layout()
plt.savefig('trip_heatmap.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved as: trip_heatmap.png")
plt.close()

print("\n" + "="*80)
print("ALL VISUALIZATIONS SAVED SUCCESSFULLY!")
print("="*80)
print("\nGenerated files:")
print("  - daily_trips_chart.png")
print("  - hourly_trips_chart.png")
print("  - trip_heatmap.png")

# ============================================================================
# FLASK ROUTES
# ============================================================================

# Basic Flask route
@app.route('/')
def home():
    return "Uber Traffic Analysis App - Data Loaded Successfully!"

# Traffic prediction endpoint for JMeter testing - IMPROVED VERSION
@app.route('/predict_traffic', methods=['GET'])
def predict_traffic():
    try:
        timestamp = request.args.get('timestamp')
       
        # Check if timestamp parameter exists
        if not timestamp:
            return jsonify({'error': 'No timestamp provided'}), 400
       
        # Handle if timestamp is literally the string "Pickup_date" (CSV not loading)
        if timestamp == 'Pickup_date' or 'Pickup_date' in timestamp:
            return jsonify({'error': 'Invalid timestamp - CSV variable not loading properly'}), 400
       
        # Convert timestamp to datetime with error handling
        dt = pd.to_datetime(timestamp, errors='coerce')
       
        # Check if conversion was successful
        if pd.isna(dt):
            return jsonify({'error': f'Invalid timestamp format: {timestamp}'}), 400
       
        hour = int(dt.hour)
        day_of_week = dt.day_name()
       
        # Get traffic prediction based on hour (simplified for stability)
        traffic_count = int(hourly_trips.get(hour, 0))
       
        return jsonify({
            'timestamp': str(timestamp),
            'hour': hour,
            'day_of_week': day_of_week,
            'predicted_trips': traffic_count,
            'status': 'success'
        }), 200
       
    except Exception as e:
        # Log the error but don't crash the server
        print(f"ERROR in predict_traffic: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'status': 'failed'
        }), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nStarting Flask server for JMeter testing...")
    print("API Endpoints:")
    print("  - http://localhost:5000/")
    print("  - http://localhost:5000/predict_traffic?timestamp=YYYY-MM-DD HH:MM:SS")
    print("="*80)
    print("\nServer Configuration:")
    print("  - Threading: Enabled")
    print("  - Debug Mode: Disabled (for stability)")
    print("  - Host: 0.0.0.0 (all interfaces)")
    print("  - Port: 5000")
    print("="*80)
   
    # More robust server configuration for load testing
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
