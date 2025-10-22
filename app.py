from flask import Flask
import pandas as pd

app = Flask(__name__)

# Load the CSV file into a Pandas DataFrame
print("Loading data...")
df = pd.read_csv("Uber-Jan-Feb-FOIL.csv")
print(f"Initial data shape: {df.shape}")

# Clean the data by removing rows with missing values and duplicates
print("\nCleaning data...")
initial_rows = len(df)
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)
final_rows = len(df)
print(f"Removed {initial_rows - final_rows} rows (missing values and duplicates)")
print(f"Final data shape: {df.shape}")

# Convert 'Date/Time' column to datetime object
print("\nConverting Date/Time column...")
df['Date/Time'] = pd.to_datetime(df['Date/Time'])
print("Date/Time conversion complete")

# Feature extraction
print("\nExtracting features...")
df['Hour'] = df['Date/Time'].dt.hour
df['Day'] = df['Date/Time'].dt.date
df['DayOfWeek'] = df['Date/Time'].dt.day_name()
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
print(f"Date range: {df['Date/Time'].min()} to {df['Date/Time'].max()}")
print(f"\nWeekend vs Weekday distribution:")
print(df['IsWeekend'].value_counts())
print(f"\nTraffic by Day of Week:")
print(df['DayOfWeek'].value_counts().sort_index())

# Basic Flask route (for Subtask 1.3)
@app.route('/')
def home():
    return "Uber Traffic Analysis App - Data Loaded Successfully!"

if __name__ == '__main__':
    print("\n" + "="*80)
    print("Flask app ready. To run the server, use: python3 app.py")
    print("="*80)
