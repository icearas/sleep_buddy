import streamlit as st
from datetime import time as dtime

from auth import get_login_url, handle_callback, is_logged_in, logout
from db import get_or_create_user, is_user_blocked, load_user_data, save_user_data, save_schedule
from limits import check_and_increment_limit, get_remaining
from ai import generate_schedule

st.set_page_config(page_title="SleepBuddy", page_icon="🌙", layout="centered")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_time(value: str | None):
    """Convert 'HH:MM' string to datetime.time, or None."""
    if not value:
        return None
    try:
        parts = value.split(":")
        return dtime(int(parts[0]), int(parts[1]))
    except Exception:
        return None


def _fmt_time(t) -> str | None:
    """Convert datetime.time to 'HH:MM' string."""
    if t is None:
        return None
    return t.strftime("%H:%M")


# ── OAuth callback handling ───────────────────────────────────────────────────

def handle_oauth_callback():
    code = st.query_params.get("code")
    if code and not is_logged_in():
        user_info = handle_callback(code)
        if user_info and user_info.get("email"):
            st.session_state["user_email"] = user_info["email"]
            st.session_state["user_name"] = user_info.get("name", "")
            get_or_create_user(user_info["email"], user_info.get("name", ""))
            st.query_params.clear()
            st.rerun()


handle_oauth_callback()


# ── Login page ────────────────────────────────────────────────────────────────

if not is_logged_in():
    st.title("🌙 SleepBuddy")
    st.markdown("🌙 Hello, parent! SleepBuddy helps you plan your baby's sleep rhythm based on their age and wake-up time. Enter today's details below and get a full day schedule — backed by AAP, WHO and NHS guidelines. Powered by AI.")
    st.markdown("---")
    st.markdown("### Sign in to get started")
    login_url = get_login_url()
    st.link_button("🔐 Sign in with Google", login_url, use_container_width=True)
    st.markdown("---")
    st.caption("⚠️ Educational tool only. Does not replace consultation with a pediatrician.")
    st.stop()


# ── Blocked user ──────────────────────────────────────────────────────────────

email = st.session_state["user_email"]
name = st.session_state.get("user_name", "")

if is_user_blocked(email):
    st.error("Your account has been blocked. Please contact support.")
    if st.button("Logout"):
        logout()
        st.rerun()
    st.stop()


# ── Main app ──────────────────────────────────────────────────────────────────

col1, col2 = st.columns([4, 1])
with col1:
    st.title("🌙 SleepBuddy")
with col2:
    if st.button("Logout", key="logout_btn"):
        logout()
        st.rerun()

first_name = name.split()[0] if name else "parent"
st.markdown(f"🌙 Hello, **{first_name}**! SleepBuddy helps you plan your baby's sleep rhythm based on their age and wake-up time. Enter today's details below and get a full day schedule — backed by AAP, WHO and NHS guidelines. Powered by AI. If this app helps you, you can [buy me a coffee](https://buycoffee.to/icearas). Thank you! ☕")

remaining = get_remaining(email)
st.info(f"Remaining today: **{remaining} / 5** schedule generations")

st.markdown("---")

# Load saved data
saved = load_user_data(email)


# ── Form ──────────────────────────────────────────────────────────────────────

st.subheader("Tell me about your baby's day")

baby_age = st.slider(
    "Baby's age (months)",
    min_value=0,
    max_value=24,
    value=saved["baby_age_months"],
    step=1,
)

wake_time = st.time_input(
    "Wake-up time",
    value=_parse_time(saved["wake_time"]),
)

st.markdown("**Naps today** (leave blank if not taken yet)")

nap_cols = st.columns(3)
naps = []

for i in range(3):
    with nap_cols[i]:
        st.markdown(f"**Nap {i + 1}**")
        nap_start = st.time_input(
            "Fell asleep",
            value=_parse_time(saved["naps"][i]["start"]),
            key=f"nap{i + 1}_start",
        )
        nap_end = st.time_input(
            "Woke up",
            value=_parse_time(saved["naps"][i]["end"]),
            key=f"nap{i + 1}_end",
        )
        naps.append({"start": _fmt_time(nap_start), "end": _fmt_time(nap_end)})

st.markdown("---")

generate_btn = st.button(
    "✨ Generate daily schedule",
    use_container_width=True,
    disabled=(remaining <= 0),
)

if remaining <= 0:
    st.warning(
        "You've used all 5 schedule generations for today. "
        "Come back tomorrow, or [☕ buy me a coffee](https://buycoffee.to/icearas) to support the project!"
    )


# ── Generate ──────────────────────────────────────────────────────────────────

if generate_btn:
    wake_str = _fmt_time(wake_time)

    # Only include naps where both times are set
    naps_clean = [n for n in naps if n["start"] and n["end"]]
    while len(naps_clean) < 3:
        naps_clean.append({"start": None, "end": None})

    save_user_data(email, baby_age, wake_str, naps_clean)

    can_use, remaining_after = check_and_increment_limit(email)
    if not can_use:
        st.error("Daily limit reached. Try again tomorrow.")
        st.stop()

    with st.spinner("Generating your baby's schedule..."):
        try:
            schedule = generate_schedule(wake_str, naps_clean, baby_age)
            save_schedule(email, schedule)
            st.session_state["last_schedule"] = schedule
            st.info(f"Remaining today: **{remaining_after} / 5** schedule generations")
            st.rerun()
        except Exception as e:
            st.error(f"Something went wrong: {e}")


# ── Show last schedule ────────────────────────────────────────────────────────

last_schedule = st.session_state.get("last_schedule") or saved.get("last_schedule")
if last_schedule:
    st.success("Here's your schedule for today!")
    st.markdown(last_schedule)

# ── Footer ─────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "🌙 SleepBuddy | Based on AAP, WHO & NHS guidelines | "
    "[☕ Buy me a coffee](https://buycoffee.to/icearas)"
)
st.caption("Made by Arkadiusz Michnej · ⚠️ Educational tool only. Does not replace consultation with a pediatrician.")
