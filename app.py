import streamlit as st

from utils.data_loader import load_clients
from utils.styles import (
    ACCENT_TEAL, BG, CARD_BG, CARD_BORDER, DANGER, SIDEBAR_BG,
    SUCCESS, TEXT_MUTED, TEXT_PRIMARY, WARNING,
)
from modules import tracker, blocker_triage, metrics, rcm_checklist

st.set_page_config(page_title="Commure Onboarding Command Center", layout="wide")

PAGES = ["Home", "Onboarding Tracker", "Blocker Triage", "Metrics Engine", "RCM Checklist"]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Home"

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background-color: {BG};
}}

section[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG};
}}

[data-testid="stRadio"] > label {{
    display: none;
}}

h1, h2, h3, h4 {{
    font-family: 'Inter', sans-serif;
    color: {TEXT_PRIMARY};
}}

p, span, div, label {{
    font-family: 'Inter', sans-serif;
}}

[data-testid="stMetric"] {{
    background-color: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
    padding: 16px;
}}

[data-testid="stMetricLabel"] {{
    color: {TEXT_MUTED};
}}

[data-testid="stMetricValue"] {{
    color: {ACCENT_TEAL};
}}

.stButton > button {{
    background-color: {ACCENT_TEAL} !important;
    color: {BG} !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 6px !important;
    height: 44px !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif;
}}

.stButton > button:hover {{
    background-color: #00B89A !important;
    color: {BG} !important;
}}

.sidebar-wordmark {{
    color: {ACCENT_TEAL};
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 4px 0 12px 0;
}}

.sidebar-divider {{
    border-top: 1px solid {CARD_BORDER};
    margin-bottom: 14px;
}}

.sidebar-nav-label {{
    color: {TEXT_MUTED};
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='sidebar-wordmark'>⬡ COMMURE OPS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-nav-label'>MODULES</div>", unsafe_allow_html=True)
    page = st.radio("Go to", PAGES, index=PAGES.index(st.session_state.nav_page))
    st.session_state.nav_page = page

page = st.session_state.nav_page

if page == "Home":
    st.header("Commure Onboarding Command Center")

    df = load_clients()
    active = df[df["status"] != "Launched"]

    total_active = len(active)
    on_track_pct = round((active["status"] == "On Track").mean() * 100, 1) if total_active else 0
    avg_days_to_launch = round(active["days_to_launch"].mean(), 1) if total_active else 0
    open_blockers = active["blockers"].astype(str).str.strip().replace("nan", "").ne("").sum()

    def kpi_card(label: str, value: str, trend: str) -> str:
        return f"""
        <div style='background-color:{CARD_BG};border:1px solid {CARD_BORDER};
        border-top:3px solid {ACCENT_TEAL};border-radius:10px;padding:16px;'>
            <div style='color:{TEXT_MUTED};font-size:11px;text-transform:uppercase;
            letter-spacing:1px;'>{label}</div>
            <div style='color:{ACCENT_TEAL};font-size:32px;font-weight:700;
            font-family:Inter,sans-serif;margin:4px 0;'>{value}</div>
            <div style='color:{TEXT_MUTED};font-size:12px;'>{trend}</div>
        </div>
        """

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(kpi_card("Total Active Clients", str(total_active), "↗ steady this week"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("On-Track %", f"{on_track_pct}%", "↗ healthy portfolio"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Avg Days to Launch", str(avg_days_to_launch), "→ on pace"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Open Blockers", str(int(open_blockers)), "↘ needs attention"), unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.subheader("Portfolio Health")

    on_track_n = int((active["status"] == "On Track").sum())
    at_risk_n = int((active["status"] == "At Risk").sum())
    blocked_n = int((active["status"] == "Blocked").sum())
    total_n = max(on_track_n + at_risk_n + blocked_n, 1)

    on_track_w = on_track_n / total_n * 100
    at_risk_w = at_risk_n / total_n * 100
    blocked_w = blocked_n / total_n * 100

    health_bar = f"""
    <div style='display:flex;width:100%;height:14px;border-radius:7px;overflow:hidden;
    border:1px solid {CARD_BORDER};margin-bottom:10px;'>
        <div style='width:{on_track_w}%;background-color:{SUCCESS};'></div>
        <div style='width:{at_risk_w}%;background-color:{WARNING};'></div>
        <div style='width:{blocked_w}%;background-color:{DANGER};'></div>
    </div>
    <div style='display:flex;gap:24px;font-size:13px;color:{TEXT_MUTED};'>
        <span><span style='color:{SUCCESS};'>●</span> On Track ({on_track_n})</span>
        <span><span style='color:{WARNING};'>●</span> At Risk ({at_risk_n})</span>
        <span><span style='color:{DANGER};'>●</span> Blocked ({blocked_n})</span>
    </div>
    """
    st.markdown(health_bar, unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    st.subheader("Quick Actions")

    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("View Tracker →", use_container_width=True):
            st.session_state.nav_page = "Onboarding Tracker"
            st.rerun()
    with qa2:
        if st.button("Triage a Blocker →", use_container_width=True):
            st.session_state.nav_page = "Blocker Triage"
            st.rerun()
    with qa3:
        if st.button("Generate Ops Brief →", use_container_width=True):
            st.session_state.nav_page = "Metrics Engine"
            st.rerun()

elif page == "Onboarding Tracker":
    tracker.render()
elif page == "Blocker Triage":
    blocker_triage.render()
elif page == "Metrics Engine":
    metrics.render()
elif page == "RCM Checklist":
    rcm_checklist.render()
