import json

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
                "For each client provided, return ONLY valid JSON, no prose, no markdown "
                "fences: an array of objects with this exact shape: "
                '{"client_name": string, "risk_reasoning": string (1-2 sentences), '
                '"recommended_intervention": string (one concrete action)}. '
                "Include exactly one object per client provided, using the client_name "
                "values exactly as given."
            )
            user_message = at_risk_df[
                ["client_name", "segment", "current_milestone", "milestone_completion_pct",
                 "days_to_launch", "blockers", "status"]
            ].to_csv(index=False)

            raw_result = call_claude(system_prompt, user_message, max_tokens=1500)

        st.subheader("AI Risk Analysis")
        st.write("Raw Claude response:")
        st.code(raw_result)

        try:
            cleaned = raw_result.strip().strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            analyses = json.loads(cleaned)
        except json.JSONDecodeError:
            st.error("Could not parse Claude's response as JSON.")
            return

        analyses_by_name = {item.get("client_name"): item for item in analyses}

        for _, row in at_risk_df.iterrows():
            client_name = row["client_name"]
            analysis = analyses_by_name.get(client_name)

            with st.expander(client_name):
                st.markdown(_status_badge(row["status"]), unsafe_allow_html=True)

                if analysis is None:
                    st.warning("No analysis returned for this client.")
                    continue

                st.markdown("**Risk Reasoning**")
                st.write(analysis.get("risk_reasoning", "N/A"))

                st.markdown("**Recommended Intervention**")
                st.write(analysis.get("recommended_intervention", "N/A"))
