import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_clients
from utils.claude_client import call_claude


def _bar_chart(title: str, value: float, suffix: str = ""):
    fig = go.Figure(go.Bar(x=[title], y=[value], marker_color="#00C9A7"))
    fig.update_layout(
        title=title,
        yaxis_title=suffix,
        height=300,
        plot_bgcolor="#0F1117",
        paper_bgcolor="#0F1117",
        font_color="#FAFAFA",
    )
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

    st.divider()

    if st.button("Generate Weekly Ops Brief"):
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

        st.success("Weekly Ops Brief")
        st.markdown(brief)
