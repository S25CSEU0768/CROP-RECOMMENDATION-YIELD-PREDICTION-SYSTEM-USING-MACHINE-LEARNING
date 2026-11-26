"""
Inference and Two-Stage Pipeline Orchestrator.
Exposes clean functions to predict recommended crops and forecast expected yields.
"""

import os
import joblib
import pandas as pd
import numpy as np


class AgriculturalDecisionPipeline:
    """
    Two-stage decision support system:
    Stage 1: Multi-class classification (Crop Recommendation)
    Stage 2: Regression (Crop Yield Prediction)
    """

    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        
        # Load Stage 1 artifacts
        rec_path = os.path.join(models_dir, "crop_recommender.pkl")
        scaler_path = os.path.join(models_dir, "scalers", "rec_scaler.pkl")
        encoder_path = os.path.join(models_dir, "scalers", "rec_label_encoder.pkl")
        
        if not (os.path.exists(rec_path) and os.path.exists(scaler_path) and os.path.exists(encoder_path)):
            raise FileNotFoundError("Stage 1 recommendation model artifacts not found.")
            
        self.crop_recommender = joblib.load(rec_path)
        self.rec_scaler = joblib.load(scaler_path)
        self.rec_encoder = joblib.load(encoder_path)
        
        # Load Stage 2 artifacts
        yield_path = os.path.join(models_dir, "yield_predictor.pkl")
        if not os.path.exists(yield_path):
            raise FileNotFoundError("Stage 2 yield predictor pipeline not found.")
            
        self.yield_pipeline = joblib.load(yield_path)

    def recommend_crop(self, n, p, k, temperature, humidity, ph, rainfall, top_k=3):
        """
        Recommends top_k crops with corresponding confidence probabilities.
        """
        feature_df = pd.DataFrame([[n, p, k, temperature, humidity, ph, rainfall]],
                                   columns=["n", "p", "k", "temperature", "humidity", "ph", "rainfall"])
        features_scaled = self.rec_scaler.transform(feature_df)
        
        probs = self.crop_recommender.predict_proba(features_scaled)[0]
        top_indices = np.argsort(probs)[::-1][:top_k]
        
        recommendations = []
        for idx in top_indices:
            crop_name = self.rec_encoder.inverse_transform([idx])[0]
            confidence = float(probs[idx]) * 100
            recommendations.append({
                "crop": crop_name.title(),
                "confidence": round(confidence, 2)
            })
            
        return recommendations

    # Agronomic taxonomy mapping: Maps Stage 1 classification labels to Stage 2 survey categories
    AGRONOMIC_CROP_MAPPING = {
        "Cotton": "Cotton(Lint)",
        "Chickpea": "Gram",
        "Pigeonpeas": "Arhar/Tur",
        "Mungbean": "Moong(Green Gram)",
        "Mothbeans": "Moth",
        "Watermelon": "Water Melon",
        "Pomegranate": "Pome Granet",
        "Kidneybeans": "Beans & Mutter(Vegetable)",
        "Apple": "Pome Fruit",
        "Blackgram": "Blackgram",
        "Coconut": "Coconut",
        "Jute": "Jute",
        "Lentil": "Lentil",
        "Maize": "Maize",
        "Mango": "Mango",
        "Orange": "Orange",
        "Papaya": "Papaya",
        "Rice": "Rice",
        "Banana": "Banana",
        "Grapes": "Grapes",
        "Coffee": "Coffee"
    }

    def predict_yield(self, crop_name, state_name, season, area_hectares, crop_year=2024):
        """
        Predicts the agricultural yield (tons/hectare) and total expected production (tons).
        Translates botanical crop names to historical survey categories for the OneHotEncoder.
        """
        clean_crop = crop_name.strip().title()
        mapped_crop = self.AGRONOMIC_CROP_MAPPING.get(clean_crop, clean_crop)
        
        input_df = pd.DataFrame([{
            "State_Name": state_name.strip().title(),
            "Season": season.strip().title(),
            "Crop": mapped_crop,
            "Crop_Year": int(crop_year),
            "Area": max(0.1, float(area_hectares))
        }])
        
        predicted_yield = self.yield_pipeline.predict(input_df)[0]
        predicted_yield = max(0.05, float(predicted_yield))
        total_production = predicted_yield * max(0.1, float(area_hectares))
        
        return {
            "crop": clean_crop,
            "mapped_survey_crop": mapped_crop,
            "predicted_yield_tons_per_ha": round(predicted_yield, 2),
            "area_hectares": float(area_hectares),
            "estimated_production_tons": round(total_production, 2)
        }

    def run_two_stage_pipeline(self, n, p, k, temperature, humidity, ph, rainfall,
                               state_name, season, area_hectares, crop_year=2024):
        """
        Full End-to-End Execution:
        Takes environmental/soil values -> Recommends optimal crop -> Forecasts yield.
        """
        recs = self.recommend_crop(n, p, k, temperature, humidity, ph, rainfall, top_k=3)
        top_crop = recs[0]["crop"]
        
        yield_info = self.predict_yield(
            crop_name=top_crop,
            state_name=state_name,
            season=season,
            area_hectares=area_hectares,
            crop_year=crop_year
        )
        
        return {
            "recommendations": recs,
            "top_choice": top_crop,
            "yield_forecast": yield_info
        }


if __name__ == "__main__":
    pipeline = AgriculturalDecisionPipeline()
    sample = pipeline.run_two_stage_pipeline(
        n=90, p=42, k=43, temperature=21.0, humidity=82.0, ph=6.5, rainfall=202.0,
        state_name="Uttar Pradesh", season="Kharif", area_hectares=10.0
    )
    print("--- Test Pipeline Result ---")
    print("Recommendations:", sample["recommendations"])
    print("Yield Forecast:", sample["yield_forecast"])
