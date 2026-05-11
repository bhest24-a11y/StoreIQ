import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="StoreIQ", layout="wide")

# -----------------------------
# 🎨 ENTERPRISE UI STYLE
# -----------------------------
st.markdown("""
<style>
body {background-color: #0f172a;}
.block-container {padding-top: 2rem;}
h1 {font-size: 42px; color: white;}
h3, h2 {color: white;}
.metric-label {color: #9ca3af;}
</style>
""", unsafe_allow_html=True)

st.title("StoreIQ")
st.caption("Predictive Retail Intelligence System")

# -----------------------------
# 📂 LOAD DATA
# -----------------------------
file_path = "storescorecard_clean.xlsx"
df = pd.read_excel(file_path)

df["Daily Expected Impact"] = pd.to_numeric(df["Daily Expected Impact"], errors="coerce").fillna(0)

# -----------------------------
# 🧠 SMARTER PREDICTION ENGINE
# -----------------------------
risk_weight = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}

df["Risk Weight"] = df["Risk Score"].map(risk_weight)

# Score combines severity + impact
df["Risk Index"] = df["Risk Weight"] * df["Daily Expected Impact"]

def predict(row):
    if row["Risk Index"] > 3000:
        return "Critical Soon"
    elif row["Risk Index"] > 1500:
        return "Escalating"
    elif row["Risk Index"] > 500:
        return "Watch"
    else:
        return "Stable"

df["Predicted Risk"] = df.apply(predict, axis=1)

def days(row):
    if row["Predicted Risk"] == "Critical Soon":
        return 1
    if row["Predicted Risk"] == "Escalating":
        return 3
    if row["Predicted Risk"] == "Watch":
        return 7
    return 14

df["Days to Failure"] = df.apply(days, axis=1)

# SORT
ranked_df = df.sort_values("Risk Index", ascending=False)

top_store = ranked_df.iloc[0]

# -----------------------------
# 📊 EXEC DASHBOARD
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Stores", len(ranked_df))
col2.metric("Highest Risk", top_store["Store"])
col3.metric("Prediction", top_store["Predicted Risk"])
col4.metric("Days Left", top_store["Days to Failure"])

st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

st.divider()

# -----------------------------
# 📉 TABLE
# -----------------------------
def highlight(row):
    if row["Predicted Risk"] == "Critical Soon":
        return ["background-color:#7f1d1d;color:white"] * len(row)
    if row["Predicted Risk"] == "Escalating":
        return ["background-color:#b45309;color:white"] * len(row)
    return [""] * len(row)

st.subheader("Predictive Ranking Engine")

display_df = ranked_df.copy()
display_df["Daily Expected Impact"] = display_df["Daily Expected Impact"].apply(lambda x: f"${x:,.0f}")

st.dataframe(
    display_df.style.apply(highlight, axis=1),
    use_container_width=True,
    height=320
)

# -----------------------------
# 🚨 EXECUTIVE CARD
# -----------------------------
st.subheader("🚨 Executive Alert")

st.markdown(f"""
**Store:** {top_store['Store']}  
**Current Risk:** {top_store['Risk Score']}  
**Predicted:** {top_store['Predicted Risk']}  
**Days to Failure:** {top_store['Days to Failure']}  

**Impact:** ${top_store['Daily Expected Impact']:,.0f}  

**Issue:** {top_store['Biggest Issue']}  

**Action:**  
{top_store['Recommended Action']}
""")

# -----------------------------
# 🔍 DRILL DOWN
# -----------------------------
st.divider()

selected_store = st.selectbox("Drill Into Store", ranked_df["Store"])

store = ranked_df[ranked_df["Store"] == selected_store].iloc[0]

d1, d2, d3, d4 = st.columns(4)

d1.metric("Risk", store["Risk Score"])
d2.metric("Predicted", store["Predicted Risk"])
d3.metric("Days Left", store["Days to Failure"])
d4.metric("Impact", f"${store['Daily Expected Impact']:,.0f}")

st.markdown("### Root Cause")
st.write(store["Biggest Issue"])

st.markdown("### Action Plan")
st.success(store["Recommended Action"])

st.markdown("### AI Coaching")
st.info(
    f"If no action is taken, {store['Store']} will likely escalate to "
    f"{store['Predicted Risk']} within {store['Days to Failure']} days. "
    f"Focus immediately on {store['Biggest Issue']}."
)
