import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_clients
from utils.claude_client import call_claude
from utils.styles import ACCENT_TEAL, CARD_BG, CARD_BORDER, TEXT_PRIMARY


def _bar_chart(title: str, value: float, suffix: str = ""):
    fig = go.Figure(go.Bar(x=[title], y=[value], marker_color=ACCENT_TEAL))
    fig.update_layout(
        title=title,
        yaxis_title=suffix,
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,24,31,1)",
        font_color="#E6EDF3",
    )
    fig.update_xaxes(gridcolor="#2A2D3A")
    fig.update_yaxes(gridcolor="#2A2D3A")
    return fig


def render():
    st.header("Metrics Engine")
    df = load_clients()

    launched = df[df["status"] == "Launched"]
    active = df[df["status"] != "Launched"]

    throughput = len(launched)
    defect_rate = (
        round((launched["blockers"].astype(str).str.strip().replace("nan", "").ne("").mean()) * 100, 1)
        if len(launched) else 0.0
    )
    avg_time_to_launch = round(launched["days_elapsed"].mean(), 1) if len(launched) else 0.0
    at_risk_rate = (
        round(active["status"].isin(["At Risk", "Blocked"]).mean() * 100, 1)
        if len(active) else 0.0
    )

    col1, col2 = st.columns(2)
    col1.plotly_chart(_bar_chart("Throughput (Launched Clients)", throughput), use_container_width=True)
    col2.plotly_chart(_bar_chart("Defect Rate", defect_rate, "%"), use_container_width=True)

    col3, col4 = st.columns(2)
    col3.plotly_chart(_bar_chart("Avg Time to Launch", avg_time_to_launch, "days"), use_container_width=True)
    col4.plotly_chart(_bar_chart("At-Risk Rate", at_risk_rate, "%"), use_container_width=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    if st.button("Generate Weekly Ops Brief", use_container_width=True):
        with st.spinner("Generating ops brief with Claude..."):
            system_prompt = (
                "You are a healthcare SaaS operations VP writing a weekly onboarding brief. "
                "Write exactly 3 paragraphs: the first on wins, the second on risks, "
                "the third on recommended actions. Be concise and executive-level."
            )
            user_message = (
                f"Throughput (launched clients): {throughput}\n"
                f"Defect rate (% launched with lingering blockers): {defect_rate}%\n"
                f"Avg time to launch: {avg_time_to_launch} days\n"
                f"At-risk rate (active clients At Risk or Blocked): {at_risk_rate}%"
            )
            brief = call_claude(system_prompt, user_message, max_tokens=800)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='background-color:{CARD_BG};border:1px solid {CARD_BORDER};
            border-left:3px solid {ACCENT_TEAL};border-radius:10px;padding:20px;'>
                <div style='color:{ACCENT_TEAL};font-size:11px;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:10px;'>Weekly Ops Brief</div>
                <div style='color:{TEXT_PRIMARY};font-size:15px;line-height:1.7;'>
                {brief.replace(chr(10), '<br><br>')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
