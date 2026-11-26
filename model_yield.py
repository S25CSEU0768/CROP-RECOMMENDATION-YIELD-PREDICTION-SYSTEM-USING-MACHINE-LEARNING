"""
Model Training, Preprocessing, Benchmarking & Serialization
for Stage 2: Crop Yield Prediction (Regression)
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.data_preprocessing import load_and_clean_yield_data


def build_yield_pipeline(regressor):
    """
    Constructs a Pipeline with categorical One-Hot Encoding and numerical passthrough.
    """
    categorical_features = ["State_Name", "Season", "Crop"]
    numerical_features = ["Crop_Year", "Area"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", "passthrough", numerical_features)
        ]
    )
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", regressor)
    ])
    return pipeline


def train_and_evaluate_yield(sample_size=35000, output_dir="models"):
    """
    Train and benchmark regression models on historical agricultural yield data.
    Uses a stratified sample for high-efficiency, robust training across states & seasons.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "scalers"), exist_ok=True)
    
    print("Loading and cleaning crop production dataset...")
    df = load_and_clean_yield_data()
    print(f"Cleaned dataset rows: {len(df)}")
    
    # Stratified sampling across crops to preserve representation while keeping training responsive
    if len(df) > sample_size:
        df_sampled = df.groupby("Crop", group_keys=False).apply(
            lambda x: x.sample(min(len(x), int(sample_size * len(x) / len(df))), random_state=42)
        )
    else:
        df_sampled = df
        
    print(f"Training subset sample size: {len(df_sampled)}")
    
    X = df_sampled[["State_Name", "Season", "Crop", "Crop_Year", "Area"]]
    y = df_sampled["Yield"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    candidate_regressors = {
        "Ridge Regression": Ridge(alpha=1.0),
        "Lasso Regression": Lasso(alpha=0.1),
        "LightGBM Regressor": LGBMRegressor(n_estimators=150, random_state=42, verbose=-1),
        "XGBoost Regressor": XGBRegressor(n_estimators=150, learning_rate=0.1, max_depth=6, random_state=42),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1)
    }
    
    results = []
    trained_pipelines = {}
    
    print("\n--- Benchmarking Regression Models for Crop Yield ---")
    for name, reg in candidate_regressors.items():
        pipe = build_yield_pipeline(reg)
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        
        # Guard negative predictions from unconstrained linear models
        preds = np.clip(preds, a_min=0, a_max=None)
        
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        print(f" > {name:<25}: R2 = {r2:.4f} | MAE = {mae:.3f} tons/ha | RMSE = {rmse:.3f}")
        results.append({
            "Model": name,
            "R2_Score": r2,
            "MAE": mae,
            "RMSE": rmse
        })
        trained_pipelines[name] = pipe
        
    results_df = pd.DataFrame(results).sort_values(by="R2_Score", ascending=False)
    best_model_name = results_df.iloc[0]["Model"]
    best_pipe = trained_pipelines[best_model_name]
    
    print(f"\nBest Performing Yield Model: {best_model_name} with R2 = {results_df.iloc[0]['R2_Score']:.4f}")
    
    # Save the pipeline
    model_path = os.path.join(output_dir, "yield_predictor.pkl")
    joblib.dump(best_pipe, model_path)
    print(f"Saved best yield predictor pipeline to {model_path}")
    
    return results_df, best_pipe


if __name__ == "__main__":
    train_and_evaluate_yield()
