import json
import re

import streamlit as st

from utils.claude_client import call_claude

PRIORITY_COLORS = {
    "High": "#FF5C5C",
    "Medium": "#F4B400",
    "Low": "#00C9A7",
}


def _priority_badge(priority: str) -> str:
    color = PRIORITY_COLORS.get(priority, "#9FA6B2")
    return (
        f"<span style='background-color:{color}22;color:{color};"
        f"border:1px solid {color};border-radius:8px;padding:2px 10px;"
        f"font-size:0.85em;'>{priority}</span>"
    )


def render():
    st.header("RCM Checklist")
    stack_description = st.text_input(
        "Client Tech Stack",
        placeholder="e.g. Uses Athelas for prior auth, manual billing, Epic EHR",
    )

    if not st.button("Submit"):
        return

    if not stack_description.strip():
        st.warning("Please describe the client's tech stack.")
        return

    with st.spinner("Generating RCM checklist with Claude..."):
        system_prompt = (
            "You are a healthcare revenue cycle management (RCM) onboarding expert. "
            "Given a description of a client's current tech stack and workflows, return ONLY "
            "valid JSON, no prose, no markdown fences: an array of objects with fields "
            '"category" (one of "Integration", "Training", "Risk", "Go-Live"), '
            '"item" (a specific task description), and "priority" (one of "High", "Medium", "Low").'
        )
        raw_result = call_claude(system_prompt, stack_description, max_tokens=1200)

    try:
        raw = raw_result.strip()
        clean = re.sub(r'```(?:json)?', '', raw).strip()
        items = json.loads(clean)
    except json.JSONDecodeError:
        st.error("Could not parse Claude's response as JSON.")
        return

    categories = {}
    for item in items:
        categories.setdefault(item.get("category", "Other"), []).append(item)

    for category, tasks in categories.items():
        st.subheader(category)
        for idx, task in enumerate(tasks):
            label = task.get("item", "")
            priority = task.get("priority", "Medium")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.checkbox(label, key=f"{category}-{idx}")
            with col2:
                st.markdown(_priority_badge(priority), unsafe_allow_html=True)
