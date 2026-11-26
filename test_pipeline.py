"""
Comprehensive Test Suite for Crop Recommendation and Yield Prediction System
Author: Team Rocket | Machine Learning Group, Bennett University
"""

import os
import sys
import unittest
import json

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pipeline import AgriculturalDecisionPipeline
from src.database import init_db, register_user, authenticate_user, save_advisory, get_user_advisories
from web.app import app


class TestPipelineModels(unittest.TestCase):
    """Verify Stage 1 Recommendation and Stage 2 Yield Prediction models via pipeline."""

    @classmethod
    def setUpClass(cls):
        models_dir = os.path.join(PROJECT_ROOT, "models")
        cls.pipeline = AgriculturalDecisionPipeline(models_dir=models_dir)

    def test_stage1_recommend_crop(self):
        result = self.pipeline.recommend_crop(
            n=90.0, p=42.0, k=43.0,
            temperature=20.8, humidity=82.0, ph=6.5, rainfall=202.9,
            top_k=3
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIn("crop", result[0])
        self.assertIn("confidence", result[0])
        self.assertGreater(result[0]["confidence"], 0.0)

    def test_stage2_predict_yield(self):
        forecast = self.pipeline.predict_yield(
            crop_name="Rice",
            state_name="Uttar Pradesh",
            season="Kharif",
            area_hectares=2.5,
            crop_year=2024
        )
        self.assertIsInstance(forecast, dict)
        self.assertIn("predicted_yield_tons_per_ha", forecast)
        self.assertIn("estimated_production_tons", forecast)
        self.assertGreater(forecast["predicted_yield_tons_per_ha"], 0.0)
        self.assertGreater(forecast["estimated_production_tons"], 0.0)

    def test_two_stage_integrated_pipeline(self):
        full_res = self.pipeline.run_two_stage_pipeline(
            n=90.0, p=42.0, k=43.0,
            temperature=24.0, humidity=80.0, ph=6.8, rainfall=210.0,
            state_name="Punjab", season="Kharif",
            area_hectares=4.0
        )
        self.assertIn("recommendations", full_res)
        self.assertIn("top_choice", full_res)
        self.assertIn("yield_forecast", full_res)
        self.assertIsInstance(full_res["recommendations"], list)
        self.assertGreaterEqual(len(full_res["recommendations"]), 1)
        self.assertGreater(full_res["yield_forecast"]["predicted_yield_tons_per_ha"], 0.0)
        self.assertGreater(full_res["yield_forecast"]["estimated_production_tons"], 0.0)


class TestDatabaseAndAuth(unittest.TestCase):
    """Verify SQLite database schema, user registration, authentication, and advisory persistence."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_register_and_authenticate(self):
        phone = "9876543210"
        user, err = register_user(
            full_name="Rajesh Kumar",
            phone=phone,
            password="SecurePassword123!",
            state="Punjab",
            district="Ludhiana",
            land_area=10.0,
            land_unit="Acres",
            investment_budget=150000.0
        )
        if err:
            self.assertIn("already exists", err)

        auth_user, auth_err = authenticate_user("9876543210", "SecurePassword123!")
        self.assertIsNone(auth_err)
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user["full_name"], "Rajesh Kumar")

    def test_advisory_persistence(self):
        user, _ = authenticate_user("9876543210", "SecurePassword123!")
        if user:
            adv_id = save_advisory(
                user_id=user["id"],
                recommended_crop="Rice",
                confidence=98.5,
                yield_rate=3.8,
                total_harvest=15.2,
                gross_revenue=334400.0,
                net_profit=184400.0,
                roi_percent=122.9,
                season="Kharif",
                n=90.0, p=42.0, k=43.0,
                temp=24.0, hum=80.0, ph=6.8, rain=210.0
            )
            self.assertIsNotNone(adv_id)

            history = get_user_advisories(user["id"])
            self.assertGreaterEqual(len(history), 1)
            self.assertEqual(history[0]["recommended_crop"], "Rice")


class TestFlaskEndpoints(unittest.TestCase):
    """Verify Flask web server routes and JSON API contracts."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "Crop Recommendation & Yield Prediction System")
        self.assertTrue(data.get("models_loaded"))

    def test_home_page_rendering(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        # Verify single primary run button and modern assets
        self.assertIn("btn-run-prediction", html)
        self.assertIn("style.css", html)
        self.assertIn("app.js", html)

    def test_predict_api_endpoint(self):
        payload = {
            "n": 85.0,
            "p": 45.0,
            "k": 40.0,
            "temperature": 25.0,
            "humidity": 78.0,
            "ph": 6.7,
            "rainfall": 190.0,
            "farmer_name": "Test Farmer",
            "state_name": "Haryana",
            "district": "Karnal",
            "season": "Kharif",
            "land_area": 5.0,
            "land_unit": "Acres",
            "investment_budget": 100000.0
        }
        response = self.client.post(
            "/api/predict",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data.get("status"), "success")
        self.assertIn("data", data)
        pred_data = data["data"]
        self.assertIn("recommendations", pred_data)
        self.assertIn("top_choice", pred_data)
        self.assertIn("yield_forecast", pred_data)
        self.assertIn("financial_projection", pred_data)
        self.assertGreater(pred_data["yield_forecast"]["predicted_yield_tons_per_ha"], 0.0)


if __name__ == "__main__":
    unittest.main()
