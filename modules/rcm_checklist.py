import json
import re

import streamlit as st

from utils.claude_client import call_claude
from utils.styles import ACCENT_TEAL, TEXT_PRIMARY, priority_badge

PRIORITY_MARKDOWN_COLORS = {
    "High": None,
    "Medium": "gray",
    "Low": "gray",
}


def render():
    st.header("RCM Checklist")
    stack_description = st.text_input(
        "Client Tech Stack",
        placeholder="e.g. Uses Athelas for prior auth, manual billing, Epic EHR",
    )

    if not st.button("Generate Checklist", use_container_width=True):
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
        st.markdown(
            f"""
            <div style='margin-top:20px;margin-bottom:10px;'>
                <span style='font-size:16px;font-weight:700;color:{TEXT_PRIMARY};'>{category}</span>
                <div style='border-bottom:2px solid {ACCENT_TEAL};width:60px;margin-top:4px;'></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for idx, task in enumerate(tasks):
            label = task.get("item", "")
            priority = task.get("priority", "Medium")
            md_color = PRIORITY_MARKDOWN_COLORS.get(priority)
            checkbox_label = f":{md_color}[{label}]" if md_color else label

            col1, col2 = st.columns([4, 1])
            with col1:
                st.checkbox(checkbox_label, key=f"{category}-{idx}")
            with col2:
                st.markdown(priority_badge(priority), unsafe_allow_html=True)
