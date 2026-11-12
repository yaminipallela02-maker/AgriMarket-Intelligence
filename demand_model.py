import joblib
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "demand_model.pkl"

_cached_model = None

def get_demand_model():
    """Load cached XGBoost demand model."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model
        
    if MODEL_PATH.exists():
        try:
            _cached_model = joblib.load(MODEL_PATH)
            return _cached_model
        except Exception as e:
            print(f"Error loading demand model: {e}")
            
    from train_models import pipeline_demand
    _cached_model = pipeline_demand
    return _cached_model


def predict_demand(
    crop_name,
    month,
    land_area,
    water_source="Borewell"
):
    """
    Predict market demand volume (in Quintals) using trained XGBoost Regressor.
    """
    model = get_demand_model()

    input_data = pd.DataFrame([{
        "crop_name": str(crop_name).strip(),
        "month": int(month),
        "land_area": float(land_area),
        "water_source": str(water_source)
    }])

    predicted_demand = float(model.predict(input_data)[0])
    return max(50.0, round(predicted_demand, 1))


def get_demand_level(demand):
    """Classify numeric demand value into category."""
    val = float(demand)
    if val >= 720:
        return "High Demand 📈"
    elif val >= 520:
        return "Moderate Demand 📊"
    else:
        return "Low Demand 📉"


def get_monthly_demand_predictions(
    crop_name,
    land_area,
    water_source="Borewell"
):
    """
    Generate 12-month demand trend forecast for chart visualizations.
    """
    model = get_demand_model()
    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    rows = []
    for m in months:
        input_data = pd.DataFrame([{
            "crop_name": str(crop_name).strip(),
            "month": m,
            "land_area": float(land_area),
            "water_source": str(water_source)
        }])
        pred = float(model.predict(input_data)[0])
        rows.append({
            "Month_Num": m,
            "Month": month_names[m - 1],
            "Predicted Demand": max(50.0, round(pred, 1))
        })

    return pd.DataFrame(rows)
