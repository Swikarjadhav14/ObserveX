# pipeline/detect.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import joblib

print("🚀 Loading preprocessed data...")
df = pd.read_parquet("data/features.parquet")

# Select numeric features for models
features = ['latency_ms', 'hour', 'status_error', 'rolling_mean_latency_10'] + \
           [c for c in df.columns if c.startswith('endpoint_')]
X = df[features].fillna(0)

# Normalize for neural network
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------- 1. Isolation Forest ----------
print("🌲 Training Isolation Forest...")
iso = IsolationForest(n_estimators=200, contamination=0.01, random_state=42)
iso.fit(X_scaled)
iso_scores = -iso.decision_function(X_scaled)  # higher = more anomalous

# ---------- 2. Autoencoder ----------
print("⚙️ Training Autoencoder...")
input_dim = X_scaled.shape[1]
autoencoder = Sequential([
    Dense(16, activation='relu', input_shape=(input_dim,)),
    Dense(8, activation='relu'),
    Dense(16, activation='relu'),
    Dense(input_dim, activation='linear')
])
autoencoder.compile(optimizer=Adam(0.001), loss='mse')
autoencoder.fit(X_scaled, X_scaled, epochs=10, batch_size=32, verbose=0)

# Reconstruction error (MSE)
reconstructions = autoencoder.predict(X_scaled)
recon_error = np.mean(np.square(X_scaled - reconstructions), axis=1)

# ---------- 3. Ensemble ----------
# Normalize both scores (0-1)
iso_norm = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())
recon_norm = (recon_error - recon_error.min()) / (recon_error.max() - recon_error.min())

# Weighted average (you can tune weights)
ensemble_score = 0.6 * iso_norm + 0.4 * recon_norm

# Set threshold at top 1% anomalies
threshold = np.percentile(ensemble_score, 99)
df['ensemble_score'] = ensemble_score
df['is_anomaly'] = ensemble_score > threshold

# ---------- Save models and results ----------
joblib.dump(iso, "models/isoforest.joblib")
joblib.dump(scaler, "models/scaler.joblib")
autoencoder.save("models/autoencoder.h5")
df.to_parquet("data/detected.parquet", index=False)

print("✅ Models trained and saved.")
print(f"⚠️ Anomalies detected: {df['is_anomaly'].sum()} / {len(df)}")
