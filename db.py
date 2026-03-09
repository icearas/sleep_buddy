from datetime import date
from supabase import create_client, Client
import streamlit as st


def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def get_or_create_user(email: str, name: str) -> dict:
    db = get_supabase_client()
    result = db.table("users").select("*").eq("email", email).execute()

    if result.data:
        # Update last_seen
        db.table("users").update({"last_seen": date.today().isoformat()}).eq("email", email).execute()
        return result.data[0]

    # Create new user
    new_user = {
        "email": email,
        "name": name,
        "created_at": date.today().isoformat(),
        "last_seen": date.today().isoformat(),
        "is_blocked": False,
        "baby_age_months": 8,
        "daily_uses": 0,
        "daily_reset_date": date.today().isoformat(),
    }
    result = db.table("users").insert(new_user).execute()
    return result.data[0]


def is_user_blocked(email: str) -> bool:
    db = get_supabase_client()
    result = db.table("users").select("is_blocked").eq("email", email).execute()
    if result.data:
        return result.data[0].get("is_blocked", False)
    return False


def load_user_data(email: str) -> dict:
    db = get_supabase_client()
    result = db.table("users").select("*").eq("email", email).execute()

    if not result.data:
        return {"baby_age_months": 8, "wake_time": None, "naps": [{"start": None, "end": None}] * 3}

    user = result.data[0]
    today = date.today()
    daily_data_date = user.get("daily_data_date")

    data = {
        "baby_age_months": user.get("baby_age_months") or 8,
        "wake_time": None,
        "naps": [{"start": None, "end": None}] * 3,
    }

    if daily_data_date and str(daily_data_date) == str(today):
        data["wake_time"] = user.get("last_wake_time")
        data["naps"] = [
            {"start": user.get("last_nap1_start"), "end": user.get("last_nap1_end")},
            {"start": user.get("last_nap2_start"), "end": user.get("last_nap2_end")},
            {"start": user.get("last_nap3_start"), "end": user.get("last_nap3_end")},
        ]
        data["last_schedule"] = user.get("last_schedule")
    else:
        data["last_schedule"] = None

    return data


def save_schedule(email: str, schedule: str):
    db = get_supabase_client()
    db.table("users").update({"last_schedule": schedule}).eq("email", email).execute()


def save_user_data(email: str, age: int, wake_time: str, naps: list):
    db = get_supabase_client()
    db.table("users").update({
        "baby_age_months": age,
        "last_wake_time": wake_time,
        "last_nap1_start": naps[0].get("start"),
        "last_nap1_end": naps[0].get("end"),
        "last_nap2_start": naps[1].get("start"),
        "last_nap2_end": naps[1].get("end"),
        "last_nap3_start": naps[2].get("start"),
        "last_nap3_end": naps[2].get("end"),
        "daily_data_date": date.today().isoformat(),
    }).eq("email", email).execute()


def get_daily_uses(email: str) -> int:
    db = get_supabase_client()
    result = db.table("users").select("daily_uses, daily_reset_date").eq("email", email).execute()
    if not result.data:
        return 0
    user = result.data[0]
    today = date.today()
    reset_date = user.get("daily_reset_date")
    if reset_date and str(reset_date) < str(today):
        db.table("users").update({"daily_uses": 0, "daily_reset_date": today.isoformat()}).eq("email", email).execute()
        return 0
    return user.get("daily_uses", 0)


def increment_daily_uses(email: str):
    db = get_supabase_client()
    uses = get_daily_uses(email)
    db.table("users").update({"daily_uses": uses + 1}).eq("email", email).execute()
