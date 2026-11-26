"""
Modern Flask Web Server for Crop Recommendation & Yield Prediction System.
Exposes a responsive, modern web interface, SQLite-backed secure farmer authentication,
session persistence, and two-stage ML prediction endpoints with financial ROI advisory.
"""

import os
import sys

# Ensure root directory is on pythonpath
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from src.pipeline import AgriculturalDecisionPipeline
from src.database import (
    register_user, authenticate_user, get_user_by_id,
    update_user_profile, save_advisory, get_user_advisories
)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize pipeline once on server startup
print("[*] Loading trained machine learning pipeline...")
pipeline = AgriculturalDecisionPipeline(models_dir=os.path.join(PROJECT_ROOT, "models"))
print("[*] Pipeline loaded successfully.")

# Available states and seasons in dataset
INDIAN_STATES = sorted([
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
])

SEASONS = ["Kharif", "Rabi", "Whole Year", "Summer", "Autumn", "Winter"]

# Benchmark market price per metric ton (INR) based on recent Indian MSP / APMC averages
CROP_MARKET_PRICES_PER_TON = {
    "Rice": 22000,
    "Wheat": 22750,
    "Maize": 20900,
    "Cotton": 70000,
    "Jute": 50500,
    "Chickpea": 54400,
    "Kidneybeans": 65000,
    "Pigeonpeas": 70000,
    "Mothbeans": 58000,
    "Mungbean": 85500,
    "Blackgram": 69500,
    "Lentil": 64250,
    "Pomegranate": 80000,
    "Banana": 18000,
    "Mango": 45000,
    "Grapes": 60000,
    "Watermelon": 12000,
    "Muskmelon": 15000,
    "Apple": 75000,
    "Orange": 40000,
    "Papaya": 20000,
    "Coconut": 35000,
    "Coffee": 180000
}

DEFAULT_CROP_PRICE_PER_TON = 25000

# ═══════════════════════════════════════════════════════════════════════════
# CACP & ICAR AGRICULTURAL COST OF CULTIVATION BENCHMARKS (INR PER ACRE)
# ═══════════════════════════════════════════════════════════════════════════
CROP_CULTIVATION_COSTS_PER_ACRE = {
    "Rice": {
        "planting_seeds": 4500,        # Land prep, nursery raising & transplanting
        "growing_nutrients": 6500,     # NPK fertilizers, irrigation pumping, weed control
        "harvesting_cutting": 4800,    # Cutting, combine harvester / threshing labor
        "transport_other": 1800        # Gunny bags, loading & local mandi cartage
    },
    "Wheat": {
        "planting_seeds": 3500,
        "growing_nutrients": 4800,
        "harvesting_cutting": 3600,
        "transport_other": 1500
    },
    "Maize": {
        "planting_seeds": 3800,
        "growing_nutrients": 4600,
        "harvesting_cutting": 3200,
        "transport_other": 1400
    },
    "Cotton": {
        "planting_seeds": 4200,        # Bt cotton seeds & sowing
        "growing_nutrients": 7800,     # Pest control (bollworm), micro-nutrients
        "harvesting_cutting": 6500,    # Multiple manual picking rounds
        "transport_other": 1800
    },
    "Jute": {
        "planting_seeds": 3600,
        "growing_nutrients": 4200,
        "harvesting_cutting": 5500,    # Retting and fiber extraction labor
        "transport_other": 1500
    },
    "Chickpea": {
        "planting_seeds": 3200,
        "growing_nutrients": 3600,
        "harvesting_cutting": 3200,
        "transport_other": 1200
    },
    "Kidneybeans": {
        "planting_seeds": 4500,
        "growing_nutrients": 4800,
        "harvesting_cutting": 3800,
        "transport_other": 1500
    },
    "Pigeonpeas": {
        "planting_seeds": 3200,
        "growing_nutrients": 4200,
        "harvesting_cutting": 3800,
        "transport_other": 1400
    },
    "Mothbeans": {
        "planting_seeds": 2500,
        "growing_nutrients": 2800,
        "harvesting_cutting": 2600,
        "transport_other": 1000
    },
    "Mungbean": {
        "planting_seeds": 2800,
        "growing_nutrients": 3200,
        "harvesting_cutting": 2800,
        "transport_other": 1100
    },
    "Blackgram": {
        "planting_seeds": 2900,
        "growing_nutrients": 3300,
        "harvesting_cutting": 2900,
        "transport_other": 1100
    },
    "Lentil": {
        "planting_seeds": 3100,
        "growing_nutrients": 3400,
        "harvesting_cutting": 3000,
        "transport_other": 1100
    },
    "Pomegranate": {
        "planting_seeds": 18000,       # Grafted saplings, pit digging & drip establishment
        "growing_nutrients": 24000,    # Fertigation, bahar treatment & bio-pesticides
        "harvesting_cutting": 12000,   # Delicate hand harvesting & sorting
        "transport_other": 8000        # Corrugated export boxes & cold chain dispatch
    },
    "Banana": {
        "planting_seeds": 14000,       # Tissue culture suckers, planting trenches
        "growing_nutrients": 16000,    # High potassium fertigation, desuckering, bunch covers
        "harvesting_cutting": 8000,    # Bunch harvesting, dehanding & crate stacking
        "transport_other": 5000
    },
    "Mango": {
        "planting_seeds": 12000,
        "growing_nutrients": 16000,
        "harvesting_cutting": 9000,
        "transport_other": 6000
    },
    "Grapes": {
        "planting_seeds": 22000,       # Trellis erection & planting
        "growing_nutrients": 28000,    # Pruning, thinning, GA3 sprays & drip
        "harvesting_cutting": 14000,   # Cluster snipping & field grading
        "transport_other": 9000
    },
    "Watermelon": {
        "planting_seeds": 5500,        # Mulching sheets & hybrid seeds
        "growing_nutrients": 6800,     # Drip fertigation & crop protection
        "harvesting_cutting": 4200,
        "transport_other": 3500
    },
    "Muskmelon": {
        "planting_seeds": 5200,
        "growing_nutrients": 6500,
        "harvesting_cutting": 4000,
        "transport_other": 3000
    },
    "Apple": {
        "planting_seeds": 20000,
        "growing_nutrients": 25000,
        "harvesting_cutting": 14000,
        "transport_other": 11000
    },
    "Orange": {
        "planting_seeds": 12000,
        "growing_nutrients": 15000,
        "harvesting_cutting": 7500,
        "transport_other": 4500
    },
    "Papaya": {
        "planting_seeds": 9000,
        "growing_nutrients": 13000,
        "harvesting_cutting": 6000,
        "transport_other": 4000
    },
    "Coconut": {
        "planting_seeds": 8000,
        "growing_nutrients": 9000,
        "harvesting_cutting": 5000,
        "transport_other": 3000
    },
    "Coffee": {
        "planting_seeds": 15000,
        "growing_nutrients": 22000,
        "harvesting_cutting": 18000,   # Selective cherry hand-picking labor
        "transport_other": 8000
    }
}

DEFAULT_CULTIVATION_COST_PER_ACRE = {
    "planting_seeds": 4000,
    "growing_nutrients": 5500,
    "harvesting_cutting": 4000,
    "transport_other": 1500
}

BENCHMARK_DATA = {
    "classifiers": [
        {"model": "Random Forest (Tuned)", "cv_accuracy": 99.32, "test_accuracy": 99.55, "f1_score": 99.55, "best": True},
        {"model": "XGBoost Classifier", "cv_accuracy": 99.03, "test_accuracy": 99.09, "f1_score": 99.08, "best": False},
        {"model": "LightGBM Classifier", "cv_accuracy": 98.98, "test_accuracy": 98.86, "f1_score": 98.86, "best": False},
        {"model": "Support Vector Machine", "cv_accuracy": 97.95, "test_accuracy": 98.41, "f1_score": 98.40, "best": False},
        {"model": "Decision Tree", "cv_accuracy": 98.47, "test_accuracy": 97.95, "f1_score": 97.94, "best": False},
        {"model": "K-Nearest Neighbors", "cv_accuracy": 96.53, "test_accuracy": 97.95, "f1_score": 97.93, "best": False},
        {"model": "Logistic Regression", "cv_accuracy": 96.82, "test_accuracy": 97.27, "f1_score": 97.25, "best": False},
    ],
    "regressors": [
        {"model": "XGBoost Regressor", "r2": 0.7573, "mae": 17.65, "rmse": 283.06, "best": True},
        {"model": "Random Forest Regressor", "r2": 0.7378, "mae": 18.79, "rmse": 294.21, "best": False},
        {"model": "LightGBM Regressor", "r2": 0.7070, "mae": 23.99, "rmse": 311.04, "best": False},
        {"model": "Ridge Regression", "r2": 0.3515, "mae": 53.72, "rmse": 462.72, "best": False},
        {"model": "Lasso Regression", "r2": 0.3506, "mae": 52.35, "rmse": 463.03, "best": False},
    ]
}


@app.route("/")
def index():
    return render_template(
        "index.html",
        states=INDIAN_STATES,
        seasons=SEASONS,
        benchmarks=BENCHMARK_DATA
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """Healthcheck endpoint for self-healing launchers, port recovery, and system monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "Crop Recommendation & Yield Prediction System",
        "version": "1.0.0",
        "models_loaded": pipeline is not None
    }), 200


# ═══════════════════════════════════════════════
# AUTHENTICATION & DATABASE REST ENDPOINTS
# ═══════════════════════════════════════════════
@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    try:
        data = request.get_json(force=True)
        user, err = register_user(
            full_name=data.get("full_name", ""),
            phone=data.get("phone", ""),
            password=data.get("password", ""),
            state=data.get("state", "Uttar Pradesh"),
            district=data.get("district", "Central"),
            land_area=float(data.get("land_area", 5.0)),
            land_unit=data.get("land_unit", "Acres"),
            investment_budget=float(data.get("investment_budget", 50000)),
            age=int(data.get("age", 35)),
            gender=data.get("gender", "Male"),
            goal=data.get("goal", "Maximum Profitability")
        )
        if err:
            return jsonify({"status": "error", "message": err}), 400
            
        return jsonify({"status": "success", "user": user})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    try:
        data = request.get_json(force=True)
        identifier = data.get("phone_or_name", "")
        password = data.get("password", "")
        
        user, err = authenticate_user(identifier, password)
        if err:
            return jsonify({"status": "error", "message": err}), 401
            
        return jsonify({"status": "success", "user": user})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/auth/update_profile", methods=["POST"])
def auth_update_profile():
    """Live update of farmer investment budget and cultivable land."""
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"status": "error", "message": "user_id is required"}), 400
            
        budget = data.get("investment_budget")
        area = data.get("land_area")
        unit = data.get("land_unit")
        
        user, err = update_user_profile(user_id, budget, area, unit)
        if err:
            return jsonify({"status": "error", "message": err}), 400
            
        return jsonify({"status": "success", "user": user})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/auth/history", methods=["GET"])
def auth_history():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400
        
    records = get_user_advisories(int(user_id))
    return jsonify({"status": "success", "history": records})


# ═══════════════════════════════════════════════
# PREDICTION & ADVISORY ENDPOINT
# ═══════════════════════════════════════════════
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        
        # Soil & Environmental Parameters (Sanitized & Bounded)
        n = max(0.0, min(200.0, float(data.get("n", 90))))
        p = max(0.0, min(200.0, float(data.get("p", 42))))
        k = max(0.0, min(300.0, float(data.get("k", 43))))
        temperature = max(-10.0, min(60.0, float(data.get("temperature", 21.0))))
        humidity = max(0.0, min(100.0, float(data.get("humidity", 82.0))))
        ph = max(1.0, min(14.0, float(data.get("ph", 6.5))))
        rainfall = max(0.0, min(2000.0, float(data.get("rainfall", 202.0))))
        
        # Farmer Profile & Location Metadata
        user_id = data.get("user_id")
        farmer_name = str(data.get("farmer_name", "Farmer")).strip()
        state_name = str(data.get("state_name", "Uttar Pradesh")).strip()
        district = str(data.get("district", "Central")).strip()
        season = str(data.get("season", "Kharif")).strip()
        
        # Land Area Handling (support acres and hectares)
        land_area = float(data.get("land_area", 5.0))
        land_unit = str(data.get("land_unit", "acres")).lower()
        if "acre" in land_unit:
            area_acres = land_area
            area_hectares = land_area * 0.404686
        else:
            area_hectares = land_area
            area_acres = land_area / 0.404686
            
        area_hectares = max(0.1, area_hectares)
        area_acres = max(0.1, area_acres)
        
        investment_budget = float(data.get("investment_budget", 50000))
        crop_year = int(data.get("crop_year", 2024))
        
        # Execute Two-Stage Machine Learning Pipeline
        results = pipeline.run_two_stage_pipeline(
            n=n, p=p, k=k,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            state_name=state_name,
            season=season,
            area_hectares=area_hectares,
            crop_year=crop_year
        )
        
        # Calculate Financial, Cost of Cultivation & Economic ROI Projections
        top_crop = results["top_choice"]
        predicted_tons = results["yield_forecast"]["estimated_production_tons"]
        price_per_ton = CROP_MARKET_PRICES_PER_TON.get(top_crop, DEFAULT_CROP_PRICE_PER_TON)
        
        # Cost of Cultivation (CACP/ICAR Indian Benchmark Breakdown)
        cost_benchmarks = CROP_CULTIVATION_COSTS_PER_ACRE.get(top_crop, DEFAULT_CULTIVATION_COST_PER_ACRE)
        planting_cost = round(cost_benchmarks["planting_seeds"] * area_acres, 2)
        growing_cost = round(cost_benchmarks["growing_nutrients"] * area_acres, 2)
        harvesting_cost = round(cost_benchmarks["harvesting_cutting"] * area_acres, 2)
        transport_cost = round(cost_benchmarks["transport_other"] * area_acres, 2)
        
        total_required_cost = round(planting_cost + growing_cost + harvesting_cost + transport_cost, 2)
        cost_per_acre_total = round(total_required_cost / area_acres, 2)
        
        # Budget Feasibility & Sanity Analysis
        budget_delta = round(investment_budget - total_required_cost, 2)
        is_sufficient = budget_delta >= 0
        
        if is_sufficient:
            feasibility_status = "SUFFICIENT"
            feasibility_advice = f"Your planned budget has a comfortable emergency reserve buffer of ₹{abs(budget_delta):,.0f}."
        else:
            deficit_pct = abs(budget_delta) / total_required_cost * 100
            affordable_acres = round(investment_budget / cost_per_acre_total, 1) if cost_per_acre_total > 0 else 0
            feasibility_status = "DEFICIT"
            feasibility_advice = (
                f"Budget deficit of ₹{abs(budget_delta):,.0f} ({deficit_pct:.1f}% shortfall). "
                f"Consider applying for a Kisan Credit Card (KCC) 4% subsidized crop loan, or scale cultivation to {affordable_acres} acres."
            )
            
        gross_revenue = round(predicted_tons * price_per_ton, 2)
        net_profit = round(gross_revenue - total_required_cost, 2)
        roi_percent = round((net_profit / total_required_cost * 100) if total_required_cost > 0 else 0.0, 1)
        
        results["financial_projection"] = {
            "farmer_name": farmer_name,
            "district": district,
            "state_name": state_name,
            "land_area_input": land_area,
            "land_unit": land_unit.title(),
            "area_acres": round(area_acres, 2),
            "area_hectares": round(area_hectares, 2),
            "investment_budget_inr": round(investment_budget, 2),
            "estimated_market_rate_per_ton": price_per_ton,
            "estimated_gross_revenue_inr": gross_revenue,
            "estimated_net_profit_inr": net_profit,
            "roi_percentage": roi_percent,
            
            # Itemized Cost of Cultivation
            "cost_of_cultivation": {
                "per_acre_planting": cost_benchmarks["planting_seeds"],
                "per_acre_growing": cost_benchmarks["growing_nutrients"],
                "per_acre_harvesting": cost_benchmarks["harvesting_cutting"],
                "per_acre_transport": cost_benchmarks["transport_other"],
                "per_acre_total": cost_per_acre_total,
                
                "total_planting_seeds_inr": planting_cost,
                "total_growing_nutrients_inr": growing_cost,
                "total_harvesting_cutting_inr": harvesting_cost,
                "total_transport_mandi_inr": transport_cost,
                "total_required_cost_inr": total_required_cost,
                
                "budget_delta_inr": budget_delta,
                "is_sufficient": is_sufficient,
                "feasibility_status": feasibility_status,
                "feasibility_advice": feasibility_advice
            }
        }
        
        # If user is authenticated, log advisory record in database
        if user_id:
            try:
                save_advisory(
                    user_id=int(user_id),
                    recommended_crop=top_crop,
                    confidence=results["recommendations"][0]["confidence"],
                    yield_rate=results["yield_forecast"]["predicted_yield_tons_per_ha"],
                    total_harvest=predicted_tons,
                    gross_revenue=gross_revenue,
                    net_profit=net_profit,
                    roi_percent=roi_percent,
                    season=season,
                    n=n, p=p, k=k,
                    temp=temperature, hum=humidity, ph=ph, rain=rainfall
                )
            except Exception as db_err:
                print(f"[!] Warning: Could not log advisory to database: {db_err}")
        
        return jsonify({
            "status": "success",
            "data": results
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route("/api/benchmarks", methods=["GET"])
def get_benchmarks():
    return jsonify(BENCHMARK_DATA)


@app.route("/api/download/report", methods=["GET"])
def download_report():
    docx_path = os.path.join(PROJECT_ROOT, "reports", "Milestone_1_Report.docx")
    if os.path.exists(docx_path):
        return send_file(
            docx_path,
            as_attachment=True,
            download_name="TeamRocket_Milestone_1_Report.docx"
        )
    return jsonify({"error": "Report file not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Crop Recommendation & Yield Prediction System serving at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
