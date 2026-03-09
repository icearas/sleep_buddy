import anthropic
import streamlit as st
from knowledge import KNOWLEDGE_BASE


def generate_schedule(wake_time: str, naps: list, baby_age_months: int) -> str:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    user_input = f"Baby age: {baby_age_months} months | Wake-up: {wake_time}"
    for i, nap in enumerate(naps, 1):
        if nap.get("start") and nap.get("end"):
            user_input += f" | Nap{i}: {nap['start']}-{nap['end']}"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=KNOWLEDGE_BASE,
        messages=[{"role": "user", "content": user_input}],
    )
    return response.content[0].text
