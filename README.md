# 🌾 Crop Recommendation & Yield Prediction System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.6.0-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1.3-EB4224.svg)](https://xgboost.readthedocs.io/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

An intelligent precision agriculture decision-support system featuring an end-to-end two-stage Machine Learning pipeline designed to optimize crop selection and forecast expected harvest yields based on environmental and regional parameters.

---

## 📌 Pipeline Overview

The system operates via a cohesive **two-stage ML & agricultural economics pipeline**:

```text
[Farmer Profile: Location, Land Area, Budget]  <─── [Live ✏️ Edit Budget & Land]
                   │
                   ▼
┌──────────────────────────────────────┐
│  Phase 1: Progressive Onboarding     │
│  Step 1: Personal (Name, Phone, Age) │
│  Step 2: Land (State, Dist, Acreage) │
│  Step 3: Budget & Cultivation Goal   │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  Stage 1: Crop Recommendation        │
│  (Multi-Class Classification)        │
│  Inputs: N, P, K, Temp, Humidity,    │
│          pH, Rainfall                │
│  Model: Tuned Random Forest (99.55%) │
└──────────────────┬───────────────────┘
                   │ Recommended Crop
                   ▼
┌──────────────────────────────────────┐
│  Stage 2: Crop Yield Prediction      │
│  (Regional Regression Analysis)      │
│  Inputs: Crop, State, Season, Area   │
│  Model: XGBoost Regressor (R² = 0.76)│
└──────────────────┬───────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  Phase 3: Cost of Cultivation & Financial Blueprint    │
│  • 4-Phase Cost: Planting, Growing, Cutting, Mandi (₹) │
│  • Budget Feasibility: Surplus Buffer vs Deficit Alert │
│  • Real-World Advice: KCC 4% Loan & Acre Scale Advice  │
│  • APMC/MSP Revenue, Net Profit & Expected ROI %       │
└────────────────────────────────────────────────────────┘
```

1. **Phase 1 — Dedicated Authentication & 3-Step Create Account Wizard**:
   - **Distinct Login & Register Flows**: Separate views for returning farmers (quick phone/password login) and new farmers (structured 3-step registration wizard).
   - **Progressive Wizard**: Step 1 (Personal Details) → Step 2 (Farm Location & Land Acreage with auto-conversion) → Step 3 (Planned Seasonal Budget & Goals).
   - **SQLite Persistence & Security**: Profiles stored in `data/agri_database.db` with `PBKDF2:SHA256` password hashing. Seeded demo credentials: Phone `+919876543210`, Password `farmer123`.
2. **Stage 1 — Crop Recommendation (Classification)**:
   - Evaluates soil macronutrients ($N, P, K$), pH, and climate variables to identify the highest-yielding crop with 99.55% accuracy.
3. **Stage 2 — Crop Yield Prediction (Regression)**:
   - Utilizes historical Indian state/district crop production records to forecast yield rate in tons per hectare.
4. **Phase 3 — Cost of Cultivation Engine & Budget Feasibility Analysis**:
   - **4-Phase Agricultural Expenditure (CACP/ICAR Standards)**: Itemizes required investment scaled to the farmer's acreage:
     1. *Phase 1: Planting & Seeds* (land prep, seeds, nursery/sowing)
     2. *Phase 2: Growing & Nutrients* (NPK fertilizers, irrigation, weed/pest management)
     3. *Phase 3: Cutting & Harvesting* (reaping, combine harvesting, threshing labor)
     4. *Phase 4: Mandi Transport & Cartage* (gunny bags, loading, APMC transport)
   - **Budget Sanity Check**: Directly compares available budget against required cultivation capital.
     - *Surplus*: Computes emergency working capital buffer.
     - *Deficit*: Alerts the farmer with percentage shortfall, calculates affordable acreage, and provides actionable financial advice (e.g. applying for a Kisan Credit Card 4% subsidized crop loan).
   - **True Net Profit & ROI**: Computes true net profit ($\text{Gross Revenue} - \text{Total Required Cultivation Cost}$) and Return on Investment (% ROI).
   - **Live ✏️ Edit Budget & Land**: Farmers can click "Edit Budget & Land" right from the dashboard to simulate different budgets or land sizes, instantly updating the SQLite database and recalculating all predictions and cost breakdowns.
   - Saves past farm advisory reports to the SQLite database for historical tracking.

---

## 🛡️ Zero-Failure Self-Healing Execution Architecture

To guarantee the system **NEVER** fails to run or becomes unresponsive when clicking "Run", the project incorporates comprehensive self-healing safeguards:

1. **Automatic Port Recovery & Zombie Cleanup**:
   - If port `5000` is held by a hanging or stale background process, `run.py` automatically detects the offending PID via Windows network diagnostics and terminates it before binding Flask.
2. **Already-Running Server Detection**:
   - If the server is already active and healthy on port `5000`, running `run.py` or double-clicking the launcher will **NOT** crash with `[WinError 10048]`. Instead, it detects the healthy server, immediately opens the browser window to `http://localhost:5000`, and exits cleanly.
3. **Automatic Virtual Environment Rerouting**:
   - If executed via global/system Python (e.g. from an unconfigured IDE or terminal), `run.py` auto-detects `.\venv\Scripts\python.exe` and re-launches itself inside the dedicated virtual environment with zero manual steps.
4. **Safe Windows Console Encoding**:
   - Reconfigures terminal encoding to UTF-8 with ASCII fallback symbols (`[+]`, `[*]`, `[!]`), preventing `UnicodeEncodeError` on Windows `CP1252` and `CP437` code pages.
5. **Leak-Free Relational Database Connections**:
   - All SQLite database access is wrapped in robust context managers that cleanly close connections on every transaction, eliminating resource exhaustion.
6. **Active Health Monitoring Endpoint**:
   - Lightweight `/api/health` endpoint enables reliable browser launch synchronization (the browser only opens when the server is 100% ready to handle requests).

---

## 📂 Project Structure

```text
ML/
├── web/
│   ├── app.py                      # Flask web server, REST API & /api/health probe
│   ├── templates/
│   │   └── index.html              # Modern responsive SaaS dashboard
│   └── static/
│       ├── css/
│       │   └── style.css           # Custom styling, animations, tabular numerals
│       ├── js/
│       │   └── app.js              # Client-side analytics, Chart.js graphs, dynamic ROI updates
│       └── images/                 # Professional agricultural imagery
├── data/
│   ├── agri_database.db            # SQLite relational database (users & past advisories)
│   ├── crop_recommendation.csv     # Precision agriculture soil/weather dataset
│   └── crop_yield.csv              # Historical agricultural yield & production data
├── models/
│   ├── crop_recommender.pkl        # Trained Stage 1 classification model (Random Forest, 99.55%)
│   ├── yield_predictor.pkl         # Trained Stage 2 regression pipeline (XGBoost, R² = 0.76)
│   └── scalers/                    # Preprocessing transformers & standard scalers
├── notebooks/
│   └── 01_eda_and_model_recommendation.ipynb  # Exploratory analysis & modeling notebook
├── reports/
│   ├── Milestone_1_Report.docx     # Academic Word report (Times New Roman, IEEE format)
│   ├── Milestone_1_Report.md       # Markdown version of research report
│   ├── generate_figures.py         # Automated report charts generator
│   └── figures/                    # 5 High-resolution visualization PNGs
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── database.py                 # SQLite database manager & PBKDF2:SHA256 password hashing
│   ├── data_preprocessing.py       # Pipeline cleaning & feature engineering utilities
│   ├── model_recommendation.py     # Stage 1 training & benchmarking script
│   ├── model_yield.py              # Stage 2 yield regression training script
│   └── pipeline.py                 # Unified 2-stage inference orchestrator
├── tests/
│   ├── __init__.py                 # Tests package initialization
│   └── test_pipeline.py            # Automated test suite (8 tests covering all modules)
├── .vscode/
│   ├── settings.json               # IDE interpreter & extra paths configuration
│   └── launch.json                 # VS Code F5 and ▶️ Run button configuration
├── run.py                          # 🛡️ Self-healing launcher & execution orchestrator
├── main.py                         # Clean entrypoint wrapper
├── LAUNCH_PROJECT.bat              # ⚡ Interactive batch launcher
├── START_APP_BACKGROUND.vbs        # 🚀 Silent zero-window background launcher
├── STOP_APP.bat                    # 🛑 One-click clean server shutdown utility
├── START_APP.lnk                   # Desktop shortcut to interactive launcher
├── START_APP_BACKGROUND.lnk        # Desktop shortcut to silent launcher
├── requirements.txt                # Python dependencies and pinned versions
└── README.md                       # Project documentation
```

---

## 🌐 Backend REST API Endpoints

The Flask server (`web/app.py`) provides high-performance JSON endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Main responsive dashboard & landing page |
| `/api/health` | `GET` | Health check & model status probe for launchers |
| `/api/auth/register` | `POST` | Registers new farmer profile with 3-step wizard attributes in SQLite |
| `/api/auth/login` | `POST` | Authenticates returning farmer via phone/name & PBKDF2:SHA256 password hash |
| `/api/auth/update_profile` | `POST` | Updates seasonal investment budget and land area dynamically |
| `/api/auth/history` | `GET` | Fetches historical advisories associated with a user ID |
| `/api/predict` | `POST` | Executes 2-stage ML pipeline, calculates 4-phase cultivation costs, budget feasibility, and net profit |
| `/api/benchmarks` | `GET` | Retrieves empirical classification & regression benchmarking metrics |
| `/api/download/report` | `GET` | Downloads the official academic Word document report (`.docx`) |

---

## 🚀 How to Run the System (Multiple Ways)

### Option 1: Desktop Double-Click (Zero Commands)
- **Interactive Console**: Double-click **`LAUNCH_PROJECT.bat`** (or **`START_APP.lnk`**). Displays live execution logs and auto-opens your browser.
- **Silent Background Launch**: Double-click **`START_APP_BACKGROUND.vbs`** (or **`START_APP_BACKGROUND.lnk`**). Starts the application seamlessly in the background without keeping a console window open, and brings up your browser!

### Option 2: VS Code / Cursor IDE One-Click Run
- Open this project in VS Code.
- Press **`F5`** (or **`Ctrl+F5`**), or click the top-right ▶️ **Run** button on `run.py`.
- The configured `.vscode/settings.json` and `.vscode/launch.json` automatically route to `.\venv\Scripts\python.exe`.

### Option 3: Command Line
```powershell
# From the project root folder:
python run.py
# or directly with venv:
.\venv\Scripts\python.exe run.py
```

### Option 4: Stopping the Server
- To cleanly shut down any background instance, simply double-click **`STOP_APP.bat`**.

---

## 🧪 Automated Testing & Verification

Run the comprehensive unit test suite:

```bash
.\venv\Scripts\python.exe -m unittest tests/test_pipeline.py
```

All 8 test suites (including Stage 1 classification, Stage 2 regression, 2-stage integrated pipeline, SQLite authentication, user updates, and `/api/health`) pass in ~1.2s with zero warnings or connection leaks.

---

## 👥 Authors & Academic Affiliation

- **Institution**: Bennett University (Times of India Group), Greater Noida, India
- **Department**: School of Computer Science Engineering and Technology
- **Project**: Machine Learning Subject Project — Crop Recommendation & Yield Prediction System
- **Team**: **TEAM ROCKET**

| S.No. | Student Name | Enrolment No. | Role & Contribution |
|---|---|---|---|
| 1 | **Manan Gupta** | `S25CSEU0768` | Full-Stack Architecture, Pipeline Integration & Economics Engine |
| 2 | **Vansh Agarwal** | `S25CSEU0743` | Machine Learning Modeling, Hyperparameter Tuning & Benchmarking |
| 3 | **Akasshat Garg** | `S25CSEU0755` | Data Preprocessing, EDA, SQLite Relational Database & Testing |
