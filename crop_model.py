import joblib
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "crop_model.pkl"

_cached_model = None

def get_crop_model():
    """Load cached Random Forest crop recommendation model."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model
        
    if MODEL_PATH.exists():
        try:
            _cached_model = joblib.load(MODEL_PATH)
            return _cached_model
        except Exception as e:
            print(f"Error loading crop model: {e}")
            
    from train_models import pipeline_crop
    _cached_model = pipeline_crop
    return _cached_model


def recommend_crop_scientific(N, P, K, temperature, humidity, ph, rainfall):
    """
    Recommend optimal crop using trained Random Forest Classifier on ICAR/Kaggle dataset.
    Features: N, P, K, temperature, humidity, ph, rainfall.
    """
    model = get_crop_model()

    input_data = pd.DataFrame([{
        "N": float(N),
        "P": float(P),
        "K": float(K),
        "temperature": float(temperature),
        "humidity": float(humidity),
        "ph": float(ph),
        "rainfall": float(rainfall)
    }])

    predicted_crop = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    confidence = float(np.max(probabilities) * 100)

    return predicted_crop, round(confidence, 2)


def recommend_crop(
    soil_type="Loamy",
    water_availability="Medium",
    land_area=2.0,
    climate="Warm",
    pesticide_usage="Low"
):
    """
    Adapter function that converts high-level soil & farm conditions
    into scientific N-P-K and agro-climatic features for model prediction.
    """
    # Soil N-P-K heuristic mappings
    soil_map = {
        "Clay": {"N": 80.0, "P": 48.0, "K": 40.0, "ph": 6.5},
        "Loamy": {"N": 78.0, "P": 45.0, "K": 35.0, "ph": 6.3},
        "Black": {"N": 115.0, "P": 46.0, "K": 20.0, "ph": 7.0},
        "Sandy": {"N": 30.0, "P": 38.0, "K": 25.0, "ph": 6.0}
    }
    
    climate_map = {
        "Hot": {"temperature": 32.0, "humidity": 65.0},
        "Warm": {"temperature": 26.0, "humidity": 70.0},
        "Cool": {"temperature": 18.0, "humidity": 75.0},
        "Humid": {"temperature": 27.0, "humidity": 85.0},
        "Dry": {"temperature": 33.0, "humidity": 45.0}
    }
    
    water_map = {
        "High": 220.0,
        "Medium": 90.0,
        "Low": 50.0
    }

    s_profile = soil_map.get(str(soil_type), soil_map["Loamy"])
    c_profile = climate_map.get(str(climate), climate_map["Warm"])
    rain_val = water_map.get(str(water_availability), 90.0)

    return recommend_crop_scientific(
        N=s_profile["N"],
        P=s_profile["P"],
        K=s_profile["K"],
        temperature=c_profile["temperature"],
        humidity=c_profile["humidity"],
        ph=s_profile["ph"],
        rainfall=rain_val
    )


def get_crop_reason(crop_name):
    """Provide detailed scientific agronomic reasoning for the recommendation."""
    reasons = {
        "Rice": "Rice requires high rainfall (>200mm), moderate temperature (22-26°C), and high humidity with fertile clay/loamy soil rich in Nitrogen.",
        "Maize": "Maize thrives with well-drained loamy soil, balanced N-P-K, warm temperature (22-25°C), and moderate rainfall (~80mm).",
        "Tomato": "Tomato performs exceptionally in loamy or sandy loam soils with pH 6.0-6.8, warm temperatures (22-28°C), and controlled irrigation.",
        "Chilli": "Chilli requires warm semi-arid to sub-humid climate, moderate Nitrogen & Phosphorus, and well-drained soil with pH 6.0-7.0.",
        "Cotton": "Cotton is optimal for deep black soils with high Nitrogen, high temperatures (24-32°C), and moderate seasonal rainfall (~80mm).",
        "Groundnut": "Groundnut prefers sandy loam soil with low Nitrogen (due to self-nitrogen fixation), warm climate, and well-drained moisture (~70mm).",
        "Potato": "Potato excels in cool temperatures (16-20°C) with loose, friable loamy soil, good Phosphorus & Potassium, and moderate moisture.",
        "Onion": "Onion needs well-drained loamy soil with neutral pH (6.0-6.8), warm climate, and moderate humidity without waterlogging.",
        "Banana": "Banana demands high Potassium, high humidity (>80%), warm temperatures (27°C), and consistent watering (>100mm).",
        "Chickpea": "Chickpea requires dry cool weather, low humidity, and sandy to loamy soil with high Phosphorus & Potassium.",
        "Pomegranate": "Pomegranate thrives in semi-arid zones with light soils, low water need, and warm to hot climate.",
        "Coconut": "Coconut is suited for coastal humid climates (>90% humidity) with high rainfall and neutral sandy loam soil."
    }

    return reasons.get(
        crop_name,
        f"{crop_name} is scientifically optimal for the selected soil N-P-K nutrients, pH level, and climatic rainfall range."
    )
