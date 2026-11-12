import joblib
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "price_model.pkl"

_cached_model = None

def get_price_model():
    """Load or retrain the price model."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model
        
    if MODEL_PATH.exists():
        try:
            _cached_model = joblib.load(MODEL_PATH)
            return _cached_model
        except Exception as e:
            print(f"Error loading price model: {e}")
            
    # If model file does not exist, run training script
    from train_models import pipeline_price
    _cached_model = pipeline_price
    return _cached_model


def predict_price(
    crop_name,
    month,
    land_area,
    water_source="Borewell",
    pesticide_usage="Medium"
):
    """
    Predict crop price per Quintal (100 kg) using real ML trained XGBoost model.
    """
    model = get_price_model()

    input_data = pd.DataFrame([{
        "crop_name": str(crop_name).strip(),
        "month": int(month),
        "land_area": float(land_area),
        "water_source": str(water_source),
        "pesticide_usage": str(pesticide_usage)
    }])

    predicted_price = float(model.predict(input_data)[0])
    return max(50.0, round(predicted_price, 2))


def get_monthly_predictions(
    crop_name,
    land_area,
    water_source="Borewell",
    pesticide_usage="Medium"
):
    """
    Generate 12-month price forecasting trend for Streamlit charts.
    """
    model = get_price_model()
    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    rows = []
    for m in months:
        input_data = pd.DataFrame([{
            "crop_name": str(crop_name).strip(),
            "month": m,
            "land_area": float(land_area),
            "water_source": str(water_source),
            "pesticide_usage": str(pesticide_usage)
        }])
        pred = float(model.predict(input_data)[0])
        rows.append({
            "Month_Num": m,
            "Month": month_names[m - 1],
            "Predicted Price": max(50.0, round(pred, 2))
        })

    return pd.DataFrame(rows)
