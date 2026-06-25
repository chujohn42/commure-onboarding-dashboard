import json

import streamlit as st

from utils.data_loader import load_clients
from utils.claude_client import call_claude
from utils.styles import (
    ACCENT_TEAL, CARD_BG, CARD_BORDER, TEXT_MUTED, TEXT_PRIMARY, priority_badge,
)


def render():
    st.header("Blocker Triage")
    st.markdown(
        f"<div style='color:{TEXT_MUTED};font-size:14px;margin-bottom:16px;'>"
        "Describe a client blocker and let Claude classify it, recommend an owner, "
        "and draft a stakeholder message.</div>",
        unsafe_allow_html=True,
    )

    df = load_clients()

    client_name = st.selectbox("Client", df["client_name"].tolist())
    blocker_text = st.text_area("Blocker Description", placeholder="Describe the blocker...")
    submitted = st.button("Triage Blocker", use_container_width=True)

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
        return

    severity = data.get("severity", "Medium")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown(
            f"""
            <div style='background-color:{CARD_BG};border:1px solid {CARD_BORDER};
            border-radius:10px;padding:16px;height:100%;'>
                <div style='color:{TEXT_MUTED};font-size:11px;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:6px;'>Blocker Type</div>
                <div style='color:{TEXT_PRIMARY};font-size:15px;margin-bottom:14px;'>
                {data.get('blocker_type', 'N/A')}</div>
                <div style='color:{TEXT_MUTED};font-size:11px;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:6px;'>Severity</div>
                {priority_badge(severity)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        steps_html = "".join(f"<li style='margin-bottom:4px;'>{s}</li>" for s in data.get("resolution_steps", []))
        st.markdown(
            f"""
            <div style='background-color:{CARD_BG};border:1px solid {CARD_BORDER};
            border-radius:10px;padding:16px;height:100%;'>
                <div style='color:{TEXT_MUTED};font-size:11px;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:6px;'>Recommended Owner</div>
                <div style='color:{TEXT_PRIMARY};font-size:15px;margin-bottom:14px;'>
                {data.get('recommended_owner', 'N/A')}</div>
                <div style='color:{TEXT_MUTED};font-size:11px;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:6px;'>Resolution Steps</div>
                <ul style='color:{TEXT_PRIMARY};font-size:14px;padding-left:18px;margin:0;'>
                {steps_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='color:{ACCENT_TEAL};font-size:11px;text-transform:uppercase;"
        f"letter-spacing:1px;margin-bottom:6px;'>Draft Message</div>",
        unsafe_allow_html=True,
    )
    st.code(data.get("stakeholder_message", ""), language="text")
    st.caption("Copy the message above using the copy icon in the top-right of the code block.")
