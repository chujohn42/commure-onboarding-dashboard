import streamlit as st

from utils.data_loader import load_clients
from modules import tracker, blocker_triage, metrics, rcm_checklist

st.set_page_config(page_title="Commure Onboarding Command Center", layout="wide")

CUSTOM_CSS = """
<style>
[data-testid="stMetric"] {
    background-color: #1A1D27;
    border: 1px solid #00C9A7;
    border-radius: 12px;
    padding: 16px;
}
[data-testid="stMetricLabel"] {
    color: #9FA6B2;
}
[data-testid="stMetricValue"] {
    color: #00C9A7;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Onboarding Tracker", "Blocker Triage", "Metrics Engine", "RCM Checklist"],
)

if page == "Home":
    st.header("Commure Onboarding Command Center")
    st.subheader("Real-time visibility into every healthcare client launch")

    df = load_clients()
    active = df[df["status"] != "Launched"]

    total_active = len(active)
    on_track_pct = round((active["status"] == "On Track").mean() * 100, 1) if total_active else 0
    avg_days_to_launch = round(active["days_to_launch"].mean(), 1) if total_active else 0
    open_blockers = active["blockers"].astype(str).str.strip().replace("nan", "").ne("").sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Active Clients", total_active)
    col2.metric("On-Track %", f"{on_track_pct}%")
    col3.metric("Avg Days to Launch", avg_days_to_launch)
    col4.metric("Open Blockers", int(open_blockers))

elif page == "Onboarding Tracker":
    tracker.render()
elif page == "Blocker Triage":
    blocker_triage.render()
elif page == "Metrics Engine":
    metrics.render()
elif page == "RCM Checklist":
    rcm_checklist.render()
