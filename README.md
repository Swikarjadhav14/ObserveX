# 🛰️ ObserveX — Unified API Intelligence Console

**ObserveX** is a prototype for API observability and anomaly detection.  
It simulates API traffic, detects anomalies using an **ensemble of Isolation Forest and Autoencoder models**, and visualizes insights using a Streamlit dashboard.

---

## ⚙️ Quick Setup & Run

### 🔹 Step 1: Clone Repository
```bash
git clone https://github.com/Swikarjadhav14/ObserveX.git
cd ObserveX
python -m venv venv
venv\Scripts\activate     # For Windows
# OR
source venv/bin/activate  # For Linux/Mac
pip install -r requirements.txt
.\run_demo.bat
