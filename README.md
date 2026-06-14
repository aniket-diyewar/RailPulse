# RailPulse 🚆

### Real-Time Railway Performance Intelligence & Delay Prediction System

Built for the **Railways Hackathon** — making railways safer, smarter, and more efficient.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Live Dashboard** | Real-time train status simulation with on-time/delayed/cancelled tracking |
| **Delay Prediction** | ML-powered prediction using Random Forest (73% accuracy, MAE ~8 min) |
| **Station Analytics** | Per-station delay analysis, busiest stations, worst performers |
| **Weather Impact** | How rain, fog, and storms affect railway punctuality |
| **Peak Hour Analysis** | Compare delays during peak vs off-peak hours |
| **Route Map** | Interactive Folium map showing station delays and route conditions |
| **Top Routes** | Identify the most delay-prone routes in the network |

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Machine Learning | Scikit-learn (Random Forest Regressor + Classifier) |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Folium |
| Data Storage | Apache Parquet |

## 📁 Project Structure

```
HackerEarth/
├── app.py                  # Main Streamlit dashboard (5 tabs)
├── data/
│   ├── generate_data.py    # Synthetic railway dataset generator
│   └── railways.parquet    # Generated dataset (5,000 records)
├── model/
│   ├── train_model.py      # Train delay prediction models
│   ├── predictor.py        # Prediction wrapper class
│   ├── delay_regressor.pkl # Trained regressor (MAE: 8.23 min)
│   ├── delay_classifier.pkl# Trained classifier (73% accuracy)
│   ├── station_encoder.pkl # Station label encoder
│   └── ...
├── utils/
│   ├── analytics.py        # Analytics & aggregation functions
│   └── simulation.py       # Real-time train feed simulator
├── assets/                 # Static assets
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data (optional — already included)
python data/generate_data.py

# 3. Train models (optional — already trained)
python model/train_model.py

# 4. Launch the dashboard
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 📊 Dataset

Synthetic dataset of **5,000 train records** across **20 major Indian railway stations** with:
- 20 train types (Rajdhani, Shatabdi, Vande Bharat, etc.)
- 4 weather conditions (clear, rain, fog, storm)
- Realistic delay patterns based on peak hours, weather, and congestion
- Temporal features (hour, day of week, month)

## 🎯 ML Models

- **Delay Regressor**: Predicts exact delay in minutes (MAE: 8.23 min)
- **Delay Classifier**: Predicts whether train will be delayed (>15 min) (73% accuracy)
- Features: distance, time encoding, weather, congestion, station, train type

## 🖥 Usage

### Live Dashboard
Shows simulated real-time train feed with auto-refresh. Monitor active trains, on-time rate, and delay distribution.

### Delay Prediction
1. Select from/to stations, date/time, weather, and train
2. Click "Predict Delay" to get ML-powered prediction
3. View comparison with historical patterns

### Analytics
Explore station performance, weather impact, peak hour effects, and most delayed routes through interactive charts.

---

Built with ❤️ for Railways Hackathon
