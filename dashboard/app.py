# dashboard/app.py
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# ==================== PAGE SETUP ====================
st.set_page_config(page_title="ObserveX | API Intelligence Console", layout="wide", page_icon="🛰️")

# ==================== STYLE ====================
st.markdown(
    """
    <style>
        .title { 
            font-size:44px !important; 
            font-weight:800; 
            color:#00C4FF; 
            text-shadow: 1px 1px 5px #222;
            margin-bottom: -10px;
        }
        .subtitle {
            font-size:20px !important;
            color:#BBBBBB;
            margin-top: 0px;
        }
        .metric-container {
            background-color:#111827;
            padding:20px;
            border-radius:12px;
            box-shadow: 0px 2px 6px #0a0a0a;
        }
        .stButton>button {
            background: linear-gradient(90deg, #00C4FF, #0072FF);
            color: white;
            border:none;
            border-radius:8px;
            padding:8px 20px;
            font-weight:600;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #00A4E0, #0057C2);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================== HEADER ====================
st.markdown('<p class="title">ObserveX — Unified API Intelligence Console</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Real-time API Analytics, Anomaly Detection, and Insights</p>', unsafe_allow_html=True)
st.markdown("---")

# ==================== LOAD DATA ====================
df = pd.read_parquet("data/detected_with_explain.parquet")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sidebar filters
st.sidebar.header("🔧 Filters")
endpoint_filter = st.sidebar.multiselect(
    "Select API Endpoint(s)",
    options=sorted(df["endpoint"].unique()),
    default=list(df["endpoint"].unique())
)
df_filtered = df[df["endpoint"].isin(endpoint_filter)]

# ==================== KPI SUMMARY ====================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total API Calls", len(df))
col2.metric("Anomalies Detected", int(df["is_anomaly"].sum()))
col3.metric("Detection Ratio", f"{(df['is_anomaly'].mean()*100):.2f}%")
col4.metric("Endpoints Monitored", df["endpoint"].nunique())

st.markdown("---")

# ==================== LATENCY CHART ====================
st.subheader("📊 API Latency Timeline (Blue = Normal | Red = Anomaly)")

lat_chart = (
    alt.Chart(df_filtered)
    .mark_line(color="#00AEEF", interpolate="monotone")
    .encode(
        x=alt.X("timestamp:T", title="Timestamp"),
        y=alt.Y("latency_ms:Q", title="Latency (ms)"),
        tooltip=["endpoint", "latency_ms", "status_code"]
    )
)

anom_points = (
    alt.Chart(df_filtered[df_filtered["is_anomaly"]])
    .mark_point(color="red", size=60)
    .encode(
        x="timestamp:T",
        y="latency_ms:Q",
        tooltip=["endpoint", "latency_ms", "explanation"]
    )
)
st.altair_chart(lat_chart + anom_points, use_container_width=True)
st.markdown("---")

# ==================== ANOMALY INSIGHTS ====================
st.subheader("🧠 Anomaly Insights Overview")

anomalies = df_filtered[df_filtered["is_anomaly"]]
if anomalies.empty:
    st.success("✅ System Stable — No anomalies detected.")
else:
    total = len(anomalies)
    avg_latency = anomalies["latency_ms"].mean()
    top_endpoint = anomalies["endpoint"].value_counts().idxmax()
    
    st.write(f"**Total anomalies:** {total}")
    st.write(f"**Average anomaly latency:** {avg_latency:.2f} ms")
    st.write(f"**Most affected endpoint:** `{top_endpoint}`")

    # Extract most common and minor reasons
    reason_counts = anomalies["explanation"].value_counts()
    most_common = reason_counts.index[0]
    st.markdown(f"**Most Common Reason:** {most_common}")

    if len(reason_counts) > 1:
        minor_reasons = reason_counts.index[1:4].tolist()
        st.markdown(f"**Other Minor Reasons:** {', '.join(minor_reasons)}")

    # Compact anomaly distribution chart
    st.markdown("#### 📈 Anomalies per Endpoint")
    chart1 = (
        alt.Chart(anomalies)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("endpoint:N", title="Endpoint", sort="-y"),
            y=alt.Y("count():Q", title="Anomalies Count"),
            tooltip=["endpoint", "count()"]
        )
        .properties(height=300)
    )
    st.altair_chart(chart1, use_container_width=True)

    # Distribution per hour
    st.markdown("#### ⏱️ Anomalies by Hour of Day")
    anomalies["hour"] = anomalies["timestamp"].dt.hour
    chart2 = (
        alt.Chart(anomalies)
        .mark_area(color="#00C4FF", opacity=0.6)
        .encode(
            x=alt.X("hour:O", title="Hour of Day"),
            y=alt.Y("count():Q", title="Anomalies Count"),
            tooltip=["hour", "count()"]
        )
        .properties(height=250)
    )
    st.altair_chart(chart2, use_container_width=True)

st.markdown("---")

# ==================== DETAILED ANOMALY LOG ====================
st.subheader("🚨 Detailed Anomaly Log")
if anomalies.empty:
    st.info("No anomalies available for display.")
else:
    st.dataframe(
        anomalies[["timestamp", "endpoint", "latency_ms", "status_code", "ensemble_score", "explanation"]]
        .sort_values("timestamp", ascending=False)
        .head(25),
        use_container_width=True,
        height=400,
    )

# ==================== ALERT CENTER ====================
st.markdown("---")
st.subheader("📣 Alert Center")

if not anomalies.empty:
    colA, colB, colC = st.columns(3)
    colA.error(f"🟥 Critical: {len(anomalies[anomalies['latency_ms'] > 400])}")
    colB.warning(f"🟧 Warning: {len(anomalies[(anomalies['latency_ms'] <= 400) & (anomalies['latency_ms'] > 200)])}")
    colC.success(f"🟩 Minor: {len(anomalies[anomalies['latency_ms'] <= 200])}")

if st.button("🚀 Dispatch Alert"):
    if not anomalies.empty:
        latest = anomalies.iloc[0]
        st.success(
            f"🔔 Alert Sent: {latest['endpoint']} latency {latest['latency_ms']} ms | {latest['explanation']}"
        )
        with open("data/alerts.log", "a") as f:
            f.write(f"[ALERT] {datetime.utcnow().isoformat()} {latest['endpoint']} {latest['latency_ms']}ms\n")
    else:
        st.info("No anomalies detected to alert 🚀")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    """
    <center>
    <p style='font-size:14px; color:#888;'>ObserveX © 2025 | Unified API Observability Console | 
    Built with ❤️ using Streamlit</p>
    </center>
    """,
    unsafe_allow_html=True,
)
