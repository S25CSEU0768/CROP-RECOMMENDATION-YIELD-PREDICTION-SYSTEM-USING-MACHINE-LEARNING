"""
Exploratory Data Analysis and Report Visualizations Generator.
Saves high-resolution plots to reports/figures/ for documentation, reports, and presentations.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("reports/figures", exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["font.size"] = 11

print("Generating EDA Figures...")

# 1. Load Crop Recommendation Data
df_rec = pd.read_csv("data/crop_recommendation.csv")
df_rec.columns = [c.strip().lower() for c in df_rec.columns]

# Fig 1: Soil Nutrients Distribution (N, P, K)
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
sns.histplot(df_rec["n"], kde=True, ax=axes[0], color="#2b5c8f")
axes[0].set_title("Nitrogen (N) Content Distribution")
axes[0].set_xlabel("Ratio (mg/kg)")

sns.histplot(df_rec["p"], kde=True, ax=axes[1], color="#e06666")
axes[1].set_title("Phosphorus (P) Content Distribution")
axes[1].set_xlabel("Ratio (mg/kg)")

sns.histplot(df_rec["k"], kde=True, ax=axes[2], color="#6aa84f")
axes[2].set_title("Potassium (K) Content Distribution")
axes[2].set_xlabel("Ratio (mg/kg)")
plt.tight_layout()
plt.savefig("reports/figures/01_soil_nutrients_distribution.png", dpi=300)
plt.close()

# Fig 2: Correlation Heatmap
plt.figure(figsize=(8, 6))
numeric_cols = ["n", "p", "k", "temperature", "humidity", "ph", "rainfall"]
corr = df_rec[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, cbar=True)
plt.title("Correlation Matrix of Soil & Climate Features")
plt.tight_layout()
plt.savefig("reports/figures/02_correlation_heatmap.png", dpi=300)
plt.close()

# Fig 3: Rainfall vs Temperature across Top Crops
top_crops = ["rice", "maize", "chickpea", "kidneybeans", "cotton", "coffee"]
df_sub = df_rec[df_rec["label"].isin(top_crops)]
plt.figure(figsize=(9, 5.5))
sns.scatterplot(
    data=df_sub, x="temperature", y="rainfall", hue="label", s=80, alpha=0.8, palette="tab10"
)
plt.title("Rainfall vs Temperature Clusters by Crop Type")
plt.xlabel("Temperature (°C)")
plt.ylabel("Annual Rainfall (mm)")
plt.legend(title="Crop", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("reports/figures/03_rainfall_temperature_clusters.png", dpi=300)
plt.close()

# Fig 4: Model Comparison Benchmarks
models = ["Random Forest", "XGBoost", "LightGBM", "SVM", "Decision Tree", "KNN", "Logistic Reg."]
accs = [99.55, 99.09, 98.86, 98.41, 97.95, 97.95, 97.27]

plt.figure(figsize=(10, 4.5))
bars = plt.barh(models[::-1], accs[::-1], color="#1A3C6E")
plt.xlim(95, 100)
plt.xlabel("Test Accuracy (%)")
plt.title("Classification Benchmark: Crop Recommendation Models")
for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"{w:.2f}%", va="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("reports/figures/04_model_accuracy_comparison.png", dpi=300)
plt.close()

# Fig 5: Yield Regression Models R2 Comparison
reg_models = ["XGBoost Regressor", "Random Forest", "LightGBM", "Ridge Regression", "Lasso Regression"]
r2_scores = [0.7573, 0.7378, 0.7070, 0.3515, 0.3506]

plt.figure(figsize=(9.5, 4.5))
bars2 = plt.bar(reg_models, r2_scores, color=["#107C41", "#2B579A", "#4B6EAF", "#D83B01", "#A80000"])
plt.ylim(0, 0.9)
plt.ylabel("R² Determination Coefficient")
plt.title("Crop Yield Regression Models: R² Score Comparison")
plt.xticks(rotation=15)
for bar in bars2:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h + 0.02, f"{h:.4f}", ha="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("reports/figures/05_yield_r2_comparison.png", dpi=300)
plt.close()

print("All 5 publication-ready figures saved in reports/figures/")
