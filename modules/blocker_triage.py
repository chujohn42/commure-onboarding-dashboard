import json

import streamlit as st

from utils.data_loader import load_clients
from utils.claude_client import call_claude

SEVERITY_COLORS = {
    "High": "#FF5C5C",
    "Medium": "#F4B400",
    "Low": "#00C9A7",
}


def render():
    st.header("Blocker Triage")
    df = load_clients()

    client_name = st.selectbox("Client", df["client_name"].tolist())
    blocker_text = st.text_area("Blocker Description", placeholder="Describe the blocker...")
    submitted = st.button("Submit")

    if not submitted:
        return

    if not blocker_text.strip():
        st.warning("Please enter a blocker description.")
        return

    with st.spinner("Triaging blocker with Claude..."):
        system_prompt = (
            "You are a healthcare SaaS onboarding triage assistant. "
            "Return ONLY valid JSON, no prose, no markdown fences, with this exact shape: "
            '{"blocker_type": string, "severity": "High"|"Medium"|"Low", '
            '"recommended_owner": string, "resolution_steps": [string, ...], '
            '"stakeholder_message": string}'
        )
        user_message = f"Client: {client_name}\nBlocker: {blocker_text}"
        raw_result = call_claude(system_prompt, user_message, max_tokens=1000)

    try:
        cleaned = raw_result.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        st.error("Could not parse Claude's response as JSON.")
        st.code(raw_result)
        return

    severity = data.get("severity", "Medium")
    color = SEVERITY_COLORS.get(severity, "#9FA6B2")

    st.markdown(
        f"""
        <div style='background-color:#1A1D27;border:1px solid {color};
        border-radius:12px;padding:16px;margin-bottom:12px;'>
        <b>Blocker Type:</b> {data.get('blocker_type', 'N/A')}<br>
        <b>Severity:</b> <span style='color:{color};'>{severity}</span><br>
        <b>Recommended Owner:</b> {data.get('recommended_owner', 'N/A')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Resolution Steps:**")
    for step in data.get("resolution_steps", []):
        st.markdown(f"- {step}")

    st.markdown("**Stakeholder Message:**")
    st.code(data.get("stakeholder_message", ""), language="text")
    st.caption("Copy the message above using the copy icon in the top-right of the code block.")
