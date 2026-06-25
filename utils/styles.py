BG = "#0A0B0F"
SIDEBAR_BG = "#111318"
CARD_BG = "#16181F"
CARD_BG_ALT = "#1E2028"
CARD_BORDER = "#2A2D3A"

ACCENT_TEAL = "#00C9A7"
ACCENT_PURPLE = "#6C63FF"
WARNING = "#F5A623"
DANGER = "#E5534B"
SUCCESS = "#3FB950"

TEXT_PRIMARY = "#E6EDF3"
TEXT_MUTED = "#7D8590"
TEXT_MUTED_2 = "#4D5260"

STATUS_STYLES = {
    "On Track": {"bg": "#1A3A2A", "color": SUCCESS},
    "At Risk": {"bg": "#3A2A0A", "color": WARNING},
    "Blocked": {"bg": "#3A1A1A", "color": DANGER},
    "Launched": {"bg": "#1A2A3A", "color": ACCENT_TEAL},
}

PRIORITY_STYLES = {
    "High": {"bg": "#3A1A1A", "color": DANGER},
    "Medium": {"bg": "#3A2A0A", "color": WARNING},
    "Low": {"bg": "#1A3A2A", "color": ACCENT_TEAL},
}


def badge(label: str, styles: dict, fallback_color: str = TEXT_MUTED) -> str:
    style = styles.get(label, {"bg": "#1A1D27", "color": fallback_color})
    return (
        f"<span style='background-color:{style['bg']};color:{style['color']};"
        f"border:1px solid {style['color']};border-radius:12px;padding:2px 10px;"
        f"font-size:12px;font-weight:600;'>{label}</span>"
    )


def status_badge(status: str) -> str:
    return badge(status, STATUS_STYLES)


def priority_badge(priority: str) -> str:
    return badge(priority, PRIORITY_STYLES)
