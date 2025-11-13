@echo off
title ObserveX Demo Launcher
echo =======================================================
echo           🚀  Launching ObserveX AI Console
echo =======================================================
echo.

REM --- Step 1: Generate synthetic API logs
python ingestion\generator.py
if %errorlevel% neq 0 exit /b

REM --- Step 2: Preprocess logs into structured features
python pipeline\preprocess.py
if %errorlevel% neq 0 exit /b

REM --- Step 3: Train ensemble models (Isolation Forest + Autoencoder)
python pipeline\detect.py
if %errorlevel% neq 0 exit /b

REM --- Step 4: Generate AI explanations
python explain\explain.py
if %errorlevel% neq 0 exit /b

REM --- Step 5: Start the Streamlit dashboard
echo.
echo =======================================================
echo  🌐 Opening ObserveX dashboard at http://localhost:8501
echo =======================================================
start "" streamlit run dashboard\app.py
pause
