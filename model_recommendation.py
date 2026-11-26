"""
Model Training, Cross-Validation, Hyperparameter Tuning & Serialization
for Stage 1: Crop Recommendation (Multi-class Classification)
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV

from src.data_preprocessing import load_recommendation_data, prepare_recommendation_data


def get_candidate_classifiers():
    """Returns a dictionary of classification models to benchmark."""
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Support Vector Machine": SVC(probability=True, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(eval_metric="mlogloss", random_state=42),
        "LightGBM": LGBMClassifier(random_state=42, verbose=-1)
    }


def benchmark_classifiers(X_train, y_train, cv=5):
    """
    Perform 5-fold Stratified Cross-Validation on all candidate models.
    """
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    models = get_candidate_classifiers()
    results = []

    print(f"--- Running {cv}-Fold Stratified Cross-Validation Benchmark ---")
    for name, model in models.items():
        scores = cross_val_score(model, X_train, y_train, cv=skf, scoring="accuracy", n_jobs=-1)
        mean_acc = np.mean(scores) * 100
        std_acc = np.std(scores) * 100
        print(f" > {name:<25}: Mean Accuracy = {mean_acc:.2f}% (+/- {std_acc:.2f}%)")
        results.append({
            "Model": name,
            "CV_Mean_Accuracy": mean_acc,
            "CV_Std_Accuracy": std_acc
        })

    return pd.DataFrame(results).sort_values(by="CV_Mean_Accuracy", ascending=False)


def train_and_evaluate_all(X_train, X_test, y_train, y_test, label_encoder):
    """
    Train each model on train split and evaluate on hold-out test set.
    """
    models = get_candidate_classifiers()
    records = []
    fitted_models = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        acc = accuracy_score(y_test, preds) * 100
        prec = precision_score(y_test, preds, average="weighted") * 100
        rec = recall_score(y_test, preds, average="weighted") * 100
        f1 = f1_score(y_test, preds, average="weighted") * 100
        
        fitted_models[name] = model
        records.append({
            "Model": name,
            "Test_Accuracy": acc,
            "Precision_Weighted": prec,
            "Recall_Weighted": rec,
            "F1_Score_Weighted": f1
        })

    results_df = pd.DataFrame(records).sort_values(by="Test_Accuracy", ascending=False)
    return results_df, fitted_models


def tune_and_save_best_model(X_train, y_train, X_test, y_test, scaler, label_encoder, output_dir="models"):
    """
    Tune the top model (Random Forest) via GridSearch and serialize it.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "scalers"), exist_ok=True)
    
    param_grid = {
        "n_estimators": [100, 150, 200],
        "max_depth": [None, 12, 16],
        "min_samples_split": [2, 4],
        "criterion": ["gini", "entropy"]
    }
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(
        rf, param_grid, cv=5, scoring="accuracy", n_jobs=-1, verbose=1
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    
    test_acc = accuracy_score(y_test, best_model.predict(X_test)) * 100
    print(f"Optimal Params: {grid_search.best_params_}")
    print(f"Tuned Random Forest Test Accuracy: {test_acc:.2f}%")
    
    # Save artifacts
    model_path = os.path.join(output_dir, "crop_recommender.pkl")
    scaler_path = os.path.join(output_dir, "scalers", "rec_scaler.pkl")
    encoder_path = os.path.join(output_dir, "scalers", "rec_label_encoder.pkl")
    
    joblib.dump(best_model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(label_encoder, encoder_path)
    
    print(f"Saved Recommender model to {model_path}")
    return best_model, test_acc


if __name__ == "__main__":
    df = load_recommendation_data()
    X_train, X_test, y_train, y_test, scaler, le = prepare_recommendation_data(df)
    
    cv_df = benchmark_classifiers(X_train, y_train)
    test_df, models = train_and_evaluate_all(X_train, X_test, y_train, y_test, le)
    print("\n--- Test Set Evaluation Results ---")
    print(test_df.to_string(index=False))
    
    tune_and_save_best_model(X_train, y_train, X_test, y_test, scaler, le)
