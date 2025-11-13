# pipeline/preprocess.py
import pandas as pd

# 1. Read the generated logs
df = pd.read_json("data/sample_logs.json")

# 2. Convert timestamp and sort by time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

# 3. Feature engineering
df['status_error'] = (df['status_code'] >= 500).astype(int)
df['hour'] = df['timestamp'].dt.hour

# One-hot encode the endpoint column
df = pd.concat([df, pd.get_dummies(df['endpoint'], prefix='endpoint')], axis=1)

# Rolling mean latency (approx 10 samples = 10 recent calls)
df['rolling_mean_latency_10'] = df['latency_ms'].rolling(window=10, min_periods=1).mean()

# Save the structured features for ML
df.to_parquet("data/features.parquet", index=False)

print("✅ Preprocessing complete — saved to data/features.parquet")
print("Columns ready for model:", df.columns.tolist())
