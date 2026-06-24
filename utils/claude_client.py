import streamlit as st
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text
