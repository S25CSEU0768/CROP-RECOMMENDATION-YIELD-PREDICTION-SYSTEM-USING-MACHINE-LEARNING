# Crop Recommendation & Yield Prediction System Using Machine Learning
**Comprehensive Technical & Implementation Progress Report**  
**Institution:** Bennett University, Greater Noida  
**School:** School of Computer Science Engineering and Technology  
**Department:** Department of Computer Science & Engineering  
**Team Name:** TEAM ROCKET  

| S.No. | Student Name | Enrolment No. | Role & Contribution |
|---|---|---|---|
| 1 | **Manan Gupta** | S25CSEU0768 | Full-Stack Architecture, Pipeline Integration & Economics Engine |
| 2 | **Vansh Agarwal** | S25CSEU0743 | Machine Learning Modeling, Hyperparameter Tuning & Benchmarking |
| 3 | **Akasshat Garg** | S25CSEU0755 | Data Preprocessing, EDA, SQLite Relational Database & Testing |

**Course:** B.Tech Computer Science Engineering  
**Subject:** Machine Learning (CSE Project Track)  
**Academic Year:** 2025-2026  

---

## 1. Executive Summary

Agriculture employs approximately 42% of the Indian workforce and contributes over 18% to the national Gross Domestic Product (GDP). Despite this scale, farmers face severe crop failures and financial distress driven by erratic monsoon patterns, soil nutrient imbalances, and lack of data-driven guidance. Traditional advisory systems provide generic soil parameters or pest diagnostics without predicting expected yields or considering farmer capital constraints.

This report presents the complete technical architecture, empirical benchmarking, and production implementation of the **Crop Recommendation & Yield Prediction System** developed by TEAM ROCKET at Bennett University. The system combines:
1. **Stage 1: Multi-Class Crop Recommendation Classifier** — Tuned Random Forest model achieving **99.55% test accuracy** across 22 crop classes, benchmarked against 7 competing algorithms.
2. **Stage 2: Regional Crop Yield Regressor** — Tuned XGBoost Regressor achieving an **^2$ score of 0.7573** (MAE: 17.65 tons/ha) trained on 246,091 historical Indian agricultural production records across states, districts, and seasons.
3. **4-Phase Cost of Cultivation Engine** — Benchmarked using Indian Commission for Agricultural Costs & Prices (CACP/ICAR) standards across Planting, Growing, Cutting, and Mandi Transport phases.
4. **Budget Feasibility Sanity Checks** — Automated surplus buffer calculations or deficit alerts with Kisan Credit Card (KCC) 4% subsidized crop loan guidance and affordable acreage computation.
5. **Progressive Farmer Authentication & Relational Database** — 3-step progressive onboarding wizard with PBKDF2:SHA256 password hashing and multi-session SQLite persistence (users and dvisories tables).
6. **Live Profile Editing & Web Application** — Full-stack web dashboard (Flask + Tailwind CSS + Chart.js + Lucide) with single-click zero-command execution (LAUNCH_PROJECT.bat).

---

## 2. Problem Statement & Agricultural Context in India

India is the world's second-largest agricultural producer with over 156 million cultivable hectares. However, smallholder and commercial farmers continually face three core systemic challenges:

1. **Soil & Climate Misalignment:** Farmers frequently rely on generational intuition or regional peer imitation rather than empirical soil health chemistry (N, P, K, pH) and climatic conditions (temperature, humidity, rainfall), leading to suboptimal crop choices.
2. **Uncertain Yield & Harvest Forecasting:** Even when a suitable crop is planted, farmers lack accurate quantitative estimates of metric-ton yield per hectare tailored to localized historical weather and district trends.
3. **Capital Infeasibility & Agrarian Debt:** Standard ML tools frequently suggest high-value crops (such as apples, grapes, or pomegranates requiring INR 60,000 to 75,000/acre in upfront capital) to smallholders with an available budget of only INR 25,000. Without phase-by-phase expenditure visibility (seeds, nutrients, harvesting, mandi cartage), farmers incur severe debt.

The **Crop Recommendation & Yield Prediction System** bridges this critical gap by providing an end-to-end, capital-aware decision platform.

---

## 3. Literature Review & Existing Solution Comparison

| Approach / System | Primary Methodology | Capabilities Provided | Identified Critical Limitations |
|---|---|---|---|
| **Traditional Farming Knowledge** | Generational intuition | Localized crop experience | Fails under shifting climate patterns and extreme weather events. |
| **Government Soil Health Cards** | Chemical soil analysis | Static N, P, K & pH values | Purely descriptive; lacks predictive crop recommendation or yield forecasting. |
| **Pudumalar et al. (2017) [2]** | Random Forest Classifier | Crop recommendation on soil | Isolated single model; lacks yield regression and economic feasibility analysis. |
| **Rajak et al. (2017) [3]** | Support Vector Machine | Crop prediction on weather | Limited feature set; no multi-season yield prediction or capital modeling. |
| **Mobile Apps (Plantix, Kisan Suvidha)** | Heuristic rules & CNNs | Pest diagnosis, weather alerts | General diagnostic utility; lacks personalized ML yield and budget feasibility checks. |
| **Proposed System (TEAM ROCKET)** | Two-Stage ML (RF 99.55% + XGBoost R2 0.76) + CACP Cost Engine | End-to-end recommendation, yield forecasting, 4-phase cost breakdown, budget feasibility check, live profile editing, SQLite persistence | Overcomes all above limitations through a unified, capital-aware decision platform. |

---

## 4. Project Objectives & Scope

1. **Multi-Class Crop Recommendation (Classification):** Develop and benchmark supervised multi-class classifiers to recommend optimal crops from 22 categories based on soil (N, P, K, pH) and weather parameters (temperature, humidity, rainfall) with >99% test accuracy.
2. **Regional Yield Forecasting (Regression):** Develop regression pipelines trained on 246,000+ historical Indian records to forecast expected crop yield (metric tons/ha) and total harvest output for a farmer's specific state, district, season, and acreage.
3. **Two-Stage Pipeline Integration:** Orchestrate an automated end-to-end pipeline passing recommended crops from Stage 1 into Stage 2 alongside regional metadata for dual real-time inference.
4. **Progressive Farmer Authentication & Persistence:** Build dedicated Login and 3-step progressive onboarding wizards (Personal Info -> Land & Location -> Budget & Goals) backed by an encrypted SQLite relational database (PBKDF2:SHA256 password hashing).
5. **4-Phase Cost of Cultivation Engine & Budget Feasibility Advisory:** Model CACP/ICAR expenditure benchmarks across four phases (Planting/Seeds, Growing/Nutrients, Cutting/Harvesting, Mandi Transport) scaled by acreage. Execute automated budget sanity checks (surplus buffer vs deficit alert, affordable acreage, and KCC 4% subsidized crop loan guidance) with APMC/MSP revenue projections for true net profit and ROI.
6. **Production Web Application & Single-Click Launch:** Deploy a modern, responsive web application (Flask + Tailwind CSS + Chart.js + Lucide) with interactive soil simulations, 1-click presets, live 'Edit Budget & Land' modal workflow, and single-click zero-configuration execution via LAUNCH_PROJECT.bat.

---

## 5. System Architecture & Two-Stage ML Pipeline

The unified inference orchestrator is implemented in src/pipeline.py, encapsulating models/crop_recommender.pkl and models/yield_predictor.pkl.

---

## 6. Dataset Specifications & Exploratory Data Analysis (EDA)

### 6.1 Dataset 1: Crop Recommendation Dataset
- **Source:** Kaggle — Atharva Ingle [4]
- **Size:** 2,200 rows x 8 columns
- **Features:** Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, pH, Rainfall
- **Target:** label (22 crops)
- **Quality:** Perfectly balanced (100 samples per crop), zero missing values.

### 6.2 Dataset 2: India Agriculture Crop Production Dataset
- **Source:** Kaggle — The Devastator [5]
- **Size:** 246,091 records x 7 columns (1997-2021)
- **Features:** State_Name, District_Name, Crop_Year, Season, Crop, Area (hectares)
- **Target:** Production (metric tons) and derived Yield (tons/hectare)

### 6.3 Exploratory Data Visualizations
- **Figure 1:** Distribution of Soil Macronutrients (N, P, K) and Environmental Parameters across 2,200 samples (
eports/figures/01_soil_nutrients_distribution.png).
- **Figure 2:** Pearson Correlation Heatmap showing relationships among soil chemistry and climatic variables (
eports/figures/02_correlation_heatmap.png).
- **Figure 3:** Rainfall vs Temperature clustering illustrating distinct agro-climatic niches across 22 crop types (
eports/figures/03_rainfall_temperature_clusters.png).

---

## 7. Machine Learning Implementation & Empirical Benchmarks

### 7.1 Stage 1: Crop Recommendation (Multi-Class Classification)

| Rank | Algorithm | 5-Fold CV Acc (%) | Test Accuracy (%) | Precision (Weighted) | Recall (Weighted) | F1-Score (Weighted) |
|---|---|---|---|---|---|---|
| **1** | **Random Forest (Tuned) [BEST]** | **99.32%** | **99.55%** | **99.57%** | **99.55%** | **99.55%** |
| 2 | XGBoost Classifier | 99.03% | 99.09% | 99.15% | 99.09% | 99.08% |
| 3 | LightGBM Classifier | 98.98% | 98.86% | 98.91% | 98.86% | 98.86% |
| 4 | Support Vector Machine (RBF) | 97.95% | 98.41% | 98.56% | 98.41% | 98.40% |
| 5 | Decision Tree Classifier | 98.47% | 97.95% | 98.06% | 97.95% | 97.94% |
| 6 | K-Nearest Neighbors | 96.53% | 97.95% | 98.04% | 97.95% | 97.93% |
| 7 | Logistic Regression | 96.82% | 97.27% | 97.40% | 97.27% | 97.25% |

- **Figure 4:** Test Accuracy and Cross-Validation comparison across Stage 1 classification algorithms (
eports/figures/04_model_accuracy_comparison.png).

### 7.2 Stage 2: Crop Yield Prediction (Regression)

| Rank | Regressor Model | R2 Score | Mean Absolute Error (t/ha) | Root Mean Squared Error (RMSE) |
|---|---|---|---|---|
| **1** | **XGBoost Regressor [BEST]** | **0.7573** | **17.65 tons/ha** | **283.06** |
| 2 | Random Forest Regressor | 0.7378 | 18.79 tons/ha | 294.21 |
| 3 | LightGBM Regressor | 0.7070 | 23.99 tons/ha | 311.04 |
| 4 | Ridge Regression (L2) | 0.3515 | 53.72 tons/ha | 462.72 |
| 5 | Lasso Regression (L1) | 0.3506 | 52.35 tons/ha | 463.03 |

- **Figure 5:** R2 Score comparison demonstrating the superior predictive power of tree ensemble models (
eports/figures/05_yield_r2_comparison.png).

---

## 8. 4-Phase Cost of Cultivation Engine & Budget Feasibility Analysis

### 8.1 CACP/ICAR Agricultural Expenditure Benchmark Model

| Crop | Phase 1: Planting & Seeds | Phase 2: Growing & Nutrients | Phase 3: Cutting & Harvest | Phase 4: Mandi Transport | Total Cost / Acre |
|---|---|---|---|---|---|
| **Rice (Paddy)** | INR 4,500 | INR 6,500 | INR 4,800 | INR 1,800 | **INR 17,600** |
| **Wheat** | INR 3,800 | INR 5,200 | INR 4,000 | INR 1,500 | **INR 14,500** |
| **Maize** | INR 3,200 | INR 4,800 | INR 3,500 | INR 1,500 | **INR 13,000** |
| **Cotton** | INR 5,500 | INR 8,000 | INR 6,500 | INR 2,000 | **INR 22,000** |
| **Jute** | INR 3,500 | INR 4,500 | INR 5,500 | INR 1,500 | **INR 15,000** |
| **Chickpea** | INR 3,000 | INR 3,800 | INR 3,200 | INR 1,200 | **INR 11,200** |
| **Apple (Orchard)** | INR 25,000 | INR 30,000 | INR 15,000 | INR 5,000 | **INR 75,000** |
| **Grapes** | INR 22,000 | INR 28,000 | INR 14,000 | INR 4,500 | **INR 68,500** |
| **Pomegranate** | INR 20,000 | INR 24,000 | INR 12,000 | INR 4,000 | **INR 60,000** |
| **Coffee** | INR 15,000 | INR 22,000 | INR 18,000 | INR 8,000 | **INR 63,000** |

### 8.2 Budget Feasibility & Sanity Checks
- **Budget Delta:** Budget Delta = Available Seasonal Budget - Total Required Cultivation Cost
- **Feasibility Decision Rules:**
  - **Sufficient (Surplus):** Budget Delta >= 0 -> Displays green Budget Sufficient badge with emergency reserve buffer.
  - **Deficit (Shortfall):** Budget Delta < 0 -> Displays amber Budget Deficit alert showing exact shortfall, calculates affordable acreage, and provides actionable advice on applying for a Kisan Credit Card (KCC) 4% subsidized crop loan.
- **Financial Return Formulas:**
  - Gross Revenue = Predicted Production (Tons) x APMC/MSP Rate per Ton
  - Net Profit = Gross Revenue - Total Required Cultivation Cost
  - ROI (%) = (Net Profit / Total Required Cultivation Cost) x 100

### 8.3 Live Edit Budget & Land Workflow
Farmers can adjust their seasonal budget or land size directly on the dashboard via an interactive modal (POST /api/auth/update_profile).

---

## 9. Progressive Authentication & SQLite Database Architecture

### 9.1 Database Schema
- **users Table:** Stores farmer registration details (id, ull_name, phone, password_hash, ge, gender, state, district, land_area, land_unit, investment_budget, arming_goal, created_at).
- **dvisories Table:** Stores past generated advisory logs linked to the farmer (id, user_id, 
ecommended_crop, confidence, yield_rate, 	otal_harvest, gross_revenue, 
et_profit, season, created_at).

---

## 10. Full-Stack Web Application Interface & Zero-Failure Self-Healing Launch

- **Backend:** High-performance Flask WSGI application with RESTful API, dynamic SQLite connection management, and `/api/health` monitoring probe.
- **Frontend:** Semantic HTML5 dashboard with modular CSS (`web/static/css/style.css`), vanilla JavaScript controller (`web/static/js/app.js`), Tailwind CSS, Lucide icons, and Chart.js visualizations.
- **Zero-Failure Execution Engine (`run.py`):**
  - Automatic virtual environment detection and execution handoff.
  - Automatic port 5000 conflict resolution, stale zombie PID termination, and fallback port allocation.
  - Active detection of already-running instances (redirects to browser without `[WinError 10048]` socket crash).
  - Safe Windows terminal CP1252/CP437 console encoding protection.
  - One-click launch options: `LAUNCH_PROJECT.bat` (interactive console), `START_APP_BACKGROUND.vbs` (silent background runner), VS Code `F5` / ▶️ Run button, and `STOP_APP.bat` (clean shutdown).

---

## 11. Automated Verification & Current Implementation Status

### 11.1 Verification Results (tests/test_pipeline.py)
- Stage 1 Crop Recommendation Classifier (Random Forest): **PASSED [OK]**
- Stage 2 Crop Yield Predictor (XGBoost): **PASSED [OK]**
- Unified Two-Stage Agronomic Decision Pipeline with Crop Mapping: **PASSED [OK]**
- SQLite database user registration, authentication & advisory persistence: **PASSED [OK]**
- Flask home view rendering & REST prediction endpoints (`/api/predict`): **PASSED [OK]**
- Flask `/api/health` system monitoring probe: **PASSED [OK]**
- All 8 automated unit and integration tests completed with **zero defects (100% PASS)**.

### 11.2 Implementation Progress Matrix
- **Milestone 1 (Problem & Literature):** 100% COMPLETE
- **Milestone 2 (Preprocessing & ML Benchmarks):** 100% COMPLETE
- **Milestone 3 (Pipeline Integration, Cost Engine, Web App):** 100% COMPLETE
- **Zero-Failure Self-Healing Deployment:** 100% COMPLETE

---

## 12. References

1. Food and Agriculture Organization of the United Nations (FAO), 'FAOSTAT: India Agriculture Statistics,' 2024. [Online]. Available: https://www.fao.org/faostat.
2. S. Pudumalar et al., 'Crop recommendation system for precision agriculture,' in Proc. 8th Int. Conf. Advanced Computing (ICoAC), Chennai, India, 2017, pp. 32-36.
3. R. K. Rajak et al., 'Crop recommendation system to maximize crop yield using machine learning technique,' in Proc. Int. Conf. Computing, Communication and Automation (ICCCA), Greater Noida, India, 2017, pp. 950-953.
4. A. Ingle, 'Crop Recommendation Dataset,' Kaggle, 2021.
5. The Devastator, 'India Agriculture Crop Production,' Kaggle, 2023.
6. Commission for Agricultural Costs and Prices (CACP), 'Price Policy for Kharif Crops: The Policy Report,' Ministry of Agriculture, Govt. of India, 2024.
7. Indian Council of Agricultural Research (ICAR), 'Handbook of Agriculture,' 6th ed., ICAR, New Delhi, 2023.
8. T. Chen and C. Guestrin, 'XGBoost: A Scalable Tree Boosting System,' in Proc. 22nd ACM SIGKDD, 2016, pp. 785-794.
9. L. Breiman, 'Random Forests,' Machine Learning, vol. 45, no. 1, pp. 5-32, 2001.
10. S. M. Lundberg and S.-I. Lee, 'A Unified Approach to Interpreting Model Predictions,' in NeurIPS 2017, pp. 4765-4774.
