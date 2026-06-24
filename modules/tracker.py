import streamlit as st

from utils.data_loader import load_clients
from utils.claude_client import call_claude

STATUS_COLORS = {
    "On Track": "#00C9A7",
    "At Risk": "#F4B400",
    "Blocked": "#FF5C5C",
    "Launched": "#6C8EFF",
}


def _status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#9FA6B2")
    return (
        f"<span style='background-color:{color}22;color:{color};"
        f"border:1px solid {color};border-radius:8px;padding:2px 10px;"
        f"font-size:0.85em;'>{status}</span>"
    )


def render():
    st.header("Onboarding Tracker")
    df = load_clients()

    display_df = df.copy()
    display_df["status"] = display_df["status"].apply(_status_badge)

    st.markdown(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("Run AI Risk Analysis"):
        at_risk_df = df[df["status"].isin(["At Risk", "Blocked"])]

        if at_risk_df.empty:
            st.info("No at-risk or blocked clients to analyze.")
            return

        with st.spinner("Analyzing at-risk clients with Claude..."):
            system_prompt = (
                "You are a healthcare SaaS onboarding operations analyst. "
                "For each client provided, give a short risk reasoning (1-2 sentences) "
                "and one concrete recommended intervention. Format your response with a "
                "clear heading per client using the client name, followed by 'Risk Reasoning:' "
                "and 'Recommended Intervention:' lines."
            )
            user_message = at_risk_df[
                ["client_name", "segment", "current_milestone", "milestone_completion_pct",
                 "days_to_launch", "blockers", "status"]
            ].to_csv(index=False)

            result = call_claude(system_prompt, user_message, max_tokens=1500)

        st.subheader("AI Risk Analysis")
        sections = result.split("\n\n")
        for client_name in at_risk_df["client_name"]:
            with st.expander(client_name):
                matched = [s for s in sections if client_name in s]
                st.markdown(matched[0] if matched else result)
