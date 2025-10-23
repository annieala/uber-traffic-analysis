# Uber Traffic Analysis

This project analyzes Uber trip data using Flask API and Docker containerization.

## Project Structure
```
.
├── Dockerfile
├── requirements.txt
├── app.py
└── README.md
```

## Setup Instructions

### 1. Download the Dataset
```bash
wget https://github.com/fivethirtyeight/uber-tlc-foil-response/raw/master/uber-trip-data/uber-raw-data-janjune-15.csv.zip
unzip uber-raw-data-janjune-15.csv.zip
mv uber-raw-data-janjune-15.csv Uber-Jan-Feb-FOIL.csv
head -50000 Uber-Jan-Feb-FOIL.csv > Uber-small.csv
```

### 2. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
```

### 3. Build Docker Image
```bash
sudo docker build -t uber-app .
```

### 4. Run Container
```bash
sudo docker run -p 5000:5000 uber-app
```

### 5. Test the API
```bash
# Test homepage
curl http://localhost:5000/

# Test traffic prediction
curl "http://localhost:5000/predict_traffic?timestamp=2015-01-01%2000:00:00"
```

## API Endpoints

- `GET /` - Homepage
- `GET /predict_traffic?timestamp=YYYY-MM-DD HH:MM:SS` - Predict traffic for a given timestamp

## Features

- Data preprocessing and cleaning
- Traffic pattern analysis
- Flask REST API
- Docker containerization
- Load testing with JMeter

## Technologies Used

- Python 3.8
- Flask
- Pandas
- Docker
- JMeter
