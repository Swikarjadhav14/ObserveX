# explain/explain.py
import pandas as pd

print("🔍 Loading detected anomalies...")
df = pd.read_parquet("data/detected.parquet")

def generate_explanation(row):
    """Generate simple text explanations for anomalies"""
    if not row['is_anomaly']:
        return ""
    reasons = []
    # Example rules for latency
    if row['latency_ms'] > row['rolling_mean_latency_10'] * 2:
        reasons.append("Latency spike (>{:.1f}× rolling mean)".format(
            row['latency_ms'] / max(row['rolling_mean_latency_10'], 1)))
    # Example rule for errors
    if row.get('status_error', 0) == 1:
        reasons.append("HTTP 5xx error detected")
    # Endpoint-specific hints
    if "/login" in str(row.get('endpoint', '')):
        reasons.append("Possible auth service slowdown")
    elif "/order" in str(row.get('endpoint', '')):
        reasons.append("Possible DB or payment issue")
    elif "/search" in str(row.get('endpoint', '')):
        reasons.append("Search index or API timeout")
    elif "/checkout" in str(row.get('endpoint', '')):
        reasons.append("Checkout pipeline delay")
    # Fallback
    if not reasons:
        reasons.append("General anomaly detected by AI ensemble model")
    return "; ".join(reasons)

print("🧠 Generating explanations...")
df['explanation'] = df.apply(generate_explanation, axis=1)

# Save explained dataset
df.to_parquet("data/detected_with_explain.parquet", index=False)
print("✅ Explanations saved to data/detected_with_explain.parquet")
print(f"Total anomalies explained: {df['is_anomaly'].sum()}")
