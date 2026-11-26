"""
Data Preprocessing and Feature Engineering Utilities.
Provides reusable functions for loading, cleaning, and encoding datasets.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib


def load_recommendation_data(filepath="data/crop_recommendation.csv"):
    """
    Load and validate the crop recommendation dataset.
    Features: N, P, K, temperature, humidity, ph, rainfall
    Target: label
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    
    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower() for c in df.columns]
    
    expected_cols = ["n", "p", "k", "temperature", "humidity", "ph", "rainfall", "label"]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Missing expected column: {col}")
            
    return df


def prepare_recommendation_data(df, test_size=0.2, random_state=42, scale_features=True):
    """
    Preprocess crop recommendation dataset:
    - Train/Test Split (Stratified)
    - Feature Scaling
    - Label Encoding
    """
    X = df[["n", "p", "k", "temperature", "humidity", "ph", "rainfall"]]
    y = df["label"]
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
    )
    
    scaler = None
    if scale_features:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
    return X_train, X_test, y_train, y_test, scaler, le


def load_and_clean_yield_data(filepath="data/crop_yield.csv", min_area=5):
    """
    Load and clean historical India crop yield dataset.
    Computes Yield = Production / Area (metric tons / hectare).
    Filters extreme anomalies and missing records.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
        
    df = pd.read_csv(filepath)
    df.columns = [c.strip() for c in df.columns]
    
    # Handle missing production
    df = df.dropna(subset=["Production", "Area"])
    
    # Clean text columns
    text_cols = ["State_Name", "District_Name", "Season", "Crop"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
            
    # Filter non-zero and reasonable crop land areas
    df = df[df["Area"] >= min_area].copy()
    
    # Compute Yield (tons / hectare)
    df["Yield"] = df["Production"] / df["Area"]
    
    # Handle severe outliers (e.g. coconut units or statistical errors exceeding 99th percentile by crop)
    upper_bound = df.groupby("Crop")["Yield"].transform(lambda s: s.quantile(0.99))
    df = df[df["Yield"] <= upper_bound * 1.5].copy()
    
    return df
