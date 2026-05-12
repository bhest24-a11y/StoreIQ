import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="StoreIQ", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #1e293b 0%, #020617 45%);
    color: white;
}

[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1e293b;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1 {
    font-size: 52px;
    font-weight: 900;
    letter-spacing: -2px;
}

.hero {
    background: linear-gradient(135deg, rgba(37,99,235,.25), rgba(15,23,42,.95));
    border: 1px solid #334155;
    border-radius: 28px;
    padding: 30px;
    margin-bottom: 28px;
    box-shadow: 0 20px 60px rgba(0,0,0,.35);
}

.hero-title {
    font-size: 30px;
    font-weight: 900;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 16px;
    margin-top: 8px;
}

.kpi-card {
    background: rgba(15,23,42,.85);
    border: 1px solid #334155;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 12px 35px rgba(0,0,0,.35);
}

.kpi-label {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 800;
}

.kpi-value {
    color: #f8fafc;
    font-size: 28px;
    font-weight: 900;
    margin-top: 8px;
}

.panel {
    background: rgba(15,23,42,.88);
    border: 1px solid #334155;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 12px 35px rgba(0,0,0,.30);
}

.badge {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    background: #1d4ed8;
    color: white;
}

.alert {
    background: linear-gradient(135deg, #7f1d1d, #1e293b);
    border: 1px solid #ef4444;
    border-radius: 22px;
    padding: 22px;
    font-size: 18px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">StoreIQ Command Center</div>
    <div class="hero-subtitle">
        Predictive retail execution intelligence for prioritizing risk, impact, ownership, and action.
    </div>
</div>
""", unsafe_allow_html=True)

df = pd.read_excel("storescorecard_clean.xlsx")
df.columns = df.columns.str.strip()

df["Daily Expected Impact"] = pd.to_numeric(df["Daily Expected Impact"], errors="coerce").fillna(0)

if "Yesterday Impact" not in df.columns:
    df["Yesterday Impact"] = 0

df["Yesterday Impact"] = pd.to_numeric(df["Yesterday Impact"], errors="coerce").fillna(0)

if "Owner" not in df.columns:
    df["Owner"] = "Unassigned"

if "District" not in df.columns:
    df["District"] = "D60"

risk_weight = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
df["Risk Weight"] = df["Risk Score"].map(risk_weight).fillna(1)
df["Risk Index"] = df["Risk Weight"] * df["Daily Expected Impact"]
df["Trend"] = df["Daily Expected Impact"] - df["Yesterday Impact"]

def predict(row):
    if row["Risk Index"] >= 2500:
        return "Critical Soon"
    elif row["Risk Index"] >= 1200:
        return "Escalating"
    elif row["Risk Index"] >= 500:
        return "Watch"
    return "Stable"

def days(row):
    if row["Predicted Risk"] == "Critical Soon":
        return 1
    if row["Predicted Risk"] == "Escalating":
        return 3
    if row["Predicted Risk"] == "Watch":
        return 7
    return 14

df["Predicted Risk"] = df.apply(predict, axis=1)
df["Days to Failure"] = df.apply(days, axis=1)

ranked_df = df.sort_values("Risk Index", ascending=False)

st.sidebar.title("StoreIQ")
st.sidebar.caption("Executive Controls")
st.sidebar.divider()

district_filter = st.sidebar.selectbox("District", ["All"] + sorted(ranked_df["District"].unique()))
risk_filter = st.sidebar.selectbox("Risk Level", ["All", "Critical", "High", "Medium", "Low"])
prediction_filter = st.sidebar.selectbox("Prediction", ["All"] + sorted(ranked_df["Predicted Risk"].unique()))

filtered_df = ranked_df.copy()

if district_filter != "All":
    filtered_df = filtered_df[filtered_df["District"] == district_filter]

if risk_filter != "All":
    filtered_df = filtered_df[filtered_df["Risk Score"] == risk_filter]

if prediction_filter != "All":
    filtered_df = filtered_df[filtered_df["Predicted Risk"] == prediction_filter]

top_store = filtered_df.iloc[0] if len(filtered_df) else ranked_df.iloc[0]

st.markdown(f"""
<div class="alert">
    🔥 Today’s Focus: {top_store['Store']} — {top_store['Biggest Issue']} 
    could impact ${top_store['Daily Expected Impact']:,.0f} today.
</div>
""", unsafe_allow_html=True)

st.write("")

c1, c2, c3, c4, c5 = st.columns(5)

cards = [
    ("Stores Reviewed", len(filtered_df)),
    ("Highest Risk", top_store["Store"]),
    ("Prediction", top_store["Predicted Risk"]),
    ("Days Left", top_store["Days to Failure"]),
    ("Impact", f"${top_store['Daily Expected Impact']:,.0f}")
]

for col, (label, value) in zip([c1, c2, c3, c4, c5], cards):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

left, right = st.columns([2.3, 1])

with left:
    st.markdown("### Predictive Priority Board")

    display_df = filtered_df.copy()
    display_df["Daily Expected Impact"] = display_df["Daily Expected Impact"].apply(lambda x: f"${x:,.0f}")
    display_df["Yesterday Impact"] = display_df["Yesterday Impact"].apply(lambda x: f"${x:,.0f}")
    display_df["Trend"] = display_df["Trend"].apply(lambda x: f"${x:,.0f}")
    display_df["Risk Index"] = display_df["Risk Index"].apply(lambda x: f"{x:,.0f}")

    st.dataframe(display_df, use_container_width=True, height=360)

with right:
    st.markdown("### Executive Brief")
    st.markdown(f"""
    <div class="panel">
        <span class="badge">{top_store['Predicted Risk']}</span><br><br>
        <b>Store:</b> {top_store['Store']}<br><br>
        <b>Risk:</b> {top_store['Risk Score']}<br><br>
        <b>Owner:</b> {top_store['Owner']}<br><br>
        <b>Issue:</b> {top_store['Biggest Issue']}<br><br>
        <b>Action:</b> {top_store['Recommended Action']}<br><br>
        <b>Impact:</b> ${top_store['Daily Expected Impact']:,.0f}
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown("### Top 3 Actions Today")

for _, row in filtered_df.head(3).iterrows():
    st.markdown(f"""
    <div class="panel">
        <b>{row['Store']}</b> — {row['Recommended Action']}<br>
        Owner: <b>{row['Owner']}</b> | Prediction: <b>{row['Predicted Risk']}</b> | Impact: <b>${row['Daily Expected Impact']:,.0f}</b>
    </div>
    <br>
    """, unsafe_allow_html=True)

st.divider()

selected_store = st.selectbox("Drill Into Store", sorted(ranked_df["Store"].tolist()))
store = ranked_df[ranked_df["Store"] == selected_store].iloc[0]

st.markdown("### Store Intelligence")

d1, d2, d3, d4 = st.columns(4)

d1.metric("Risk", store["Risk Score"])
d2.metric("Prediction", store["Predicted Risk"])
d3.metric("Days Left", store["Days to Failure"])
d4.metric("Impact", f"${store['Daily Expected Impact']:,.0f}", delta=f"${store['Trend']:,.0f}")

st.markdown(f"""
<div class="panel">
<b>Root Cause:</b><br>
{store['Biggest Issue']}<br><br>

<b>Recommended Action:</b><br>
{store['Recommended Action']}<br><br>

<b>AI Coaching:</b><br>
If no action is taken, {store['Store']} may escalate to {store['Predicted Risk']} within {store['Days to Failure']} days.
</div>
""", unsafe_allow_html=True)
