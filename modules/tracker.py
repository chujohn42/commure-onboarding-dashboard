import json

import streamlit as st

from utils.data_loader import load_clients
from utils.claude_client import call_claude
from utils.styles import (
    ACCENT_TEAL, CARD_BG, CARD_BG_ALT, CARD_BORDER, STATUS_STYLES,
    TEXT_MUTED, TEXT_PRIMARY, status_badge,
)


def _build_table_html(df) -> str:
    columns = [
        "client_name", "segment", "launch_date_target", "current_milestone",
        "milestone_completion_pct", "days_elapsed", "days_to_launch", "blockers", "status",
    ]
    headers = "".join(
        f"<th style='padding:10px 14px;text-align:left;font-size:12px;"
        f"text-transform:uppercase;letter-spacing:0.5px;'>{col.replace('_', ' ')}</th>"
        for col in columns
    )

    rows_html = ""
    for idx, row in df.iterrows():
        row_bg = CARD_BG if idx % 2 == 0 else CARD_BG_ALT
        cells = ""
        for col in columns:
            if col == "status":
                cell_value = status_badge(row[col])
            else:
                value = row[col]
                cell_value = "—" if (value is None or str(value).strip() in ("", "nan")) else str(value)
            cells += f"<td style='padding:10px 14px;font-size:13px;color:{TEXT_PRIMARY};'>{cell_value}</td>"
        rows_html += f"<tr style='background-color:{row_bg};'>{cells}</tr>"

    return f"""
    <div style='border:1px solid {CARD_BORDER};border-radius:10px;overflow:hidden;'>
    <table style='width:100%;border-collapse:collapse;font-family:Inter,sans-serif;'>
        <thead>
            <tr style='background-color:{ACCENT_TEAL};color:#0A0B0F;'>{headers}</tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """


def render():
    st.header("Onboarding Tracker")
    df = load_clients()

    st.markdown(_build_table_html(df), unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    run_clicked = st.button("Run AI Risk Analysis", use_container_width=True)

    if not run_clicked:
        return

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

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.subheader("AI Risk Analysis")

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
        status = row["status"]
        analysis = analyses_by_name.get(client_name)
        border_color = STATUS_STYLES.get(status, {}).get("color", ACCENT_TEAL)

        with st.container():
            if analysis is None:
                card_body = f"<div style='color:{TEXT_MUTED};'>No analysis returned for this client.</div>"
            else:
                card_body = f"""
                <div style='color:{TEXT_MUTED};font-size:14px;margin-bottom:10px;'>
                    {analysis.get('risk_reasoning', 'N/A')}
                </div>
                <div style='background-color:rgba(0,201,167,0.1);border-radius:8px;
                padding:10px 14px;font-size:14px;color:{TEXT_PRIMARY};'>
                    <span style='color:{ACCENT_TEAL};font-weight:600;'>Recommended Intervention:</span>
                    {analysis.get('recommended_intervention', 'N/A')}
                </div>
                """

            st.markdown(
                f"""
                <div style='background-color:{CARD_BG};border:1px solid {CARD_BORDER};
                border-left:4px solid {border_color};border-radius:10px;padding:16px;
                margin-bottom:12px;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;
                    margin-bottom:8px;'>
                        <span style='font-size:16px;font-weight:600;color:{TEXT_PRIMARY};'>
                        {client_name}</span>
                        {status_badge(status)}
                    </div>
                    {card_body}
                </div>
                """,
                unsafe_allow_html=True,
            )
