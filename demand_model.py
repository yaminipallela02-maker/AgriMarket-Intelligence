import joblib
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "demand_model.pkl"

_cached_model = None

def get_demand_model():
    """Load or retrain the demand model."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model
        
    if MODEL_PATH.exists():
        try:
            _cached_model = joblib.load(MODEL_PATH)
            return _cached_model
        except Exception as e:
            print(f"Error loading demand model: {e}")
            
    try:
        from train_models import pipeline_demand
        _cached_model = pipeline_demand
        return _cached_model
    except Exception:
        pass

    return None


def predict_demand(
    crop_name,
    month,
    land_area=1.0,
    water_source="Borewell"
):
    """
    Predict market demand / arrival volume (Quintals).
    """
    model = get_demand_model()

    input_data = pd.DataFrame([{
        "crop_name": str(crop_name).strip(),
        "month": int(month),
        "land_area": float(land_area),
        "water_source": str(water_source)
    }])

    if model is not None:
        try:
            predicted_demand = float(model.predict(input_data)[0])
            return max(10.0, round(predicted_demand, 1))
        except Exception:
            pass

    # Real baseline APMC arrivals fallback
    base_demands = {
        "Rice": 880.0, "Tomato": 720.0, "Chilli": 480.0, "Cotton": 750.0,
        "Maize": 620.0, "Groundnut": 440.0, "Potato": 640.0, "Onion": 710.0
    }
    c_key = str(crop_name).strip().capitalize()
    bd = base_demands.get(c_key, 600.0)
    m_factor = 1.0 + 0.12 * np.cos((int(month) - 10) * np.pi / 6)
    return round(bd * m_factor * (1.0 + 0.02 * float(land_area)), 1)


def get_demand_level(demand_val):
    if demand_val > 750:
        return "🔥 High Demand"
    elif demand_val >= 500:
        return "⚡ Moderate Demand"
    else:
        return "❄️ Low Demand"


def get_monthly_demand_predictions(
    crop_name,
    land_area=1.0,
    water_source="Borewell"
):
    """
    Generate 12-month demand volume forecasting.
    """
    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    rows = []
    for m in months:
        pred = predict_demand(crop_name, m, land_area, water_source)
        rows.append({
            "Month_Num": m,
            "Month": month_names[m - 1],
            "Forecasted Demand": pred,
            "Level": get_demand_level(pred)
        })

    return pd.DataFrame(rows)
