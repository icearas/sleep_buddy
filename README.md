# 🌙 SleepBuddy

**Live app:** https://sleepbuddy-jnkc5xqmpozqeysquaazhw.streamlit.app

> Hello, parent! SleepBuddy helps you plan your baby's sleep rhythm based on their age and wake-up time. Get a full day schedule — backed by AAP, WHO and NHS guidelines. Powered by AI.

---

## Tech Stack

```
Streamlit + Claude Haiku API + Google OAuth + Supabase
```

| Component | Technology | Cost |
|-----------|------------|------|
| Hosting | Streamlit Cloud | Free |
| AI model | Claude Haiku (`claude-haiku-4-5-20251001`) | ~$0.001/request |
| Database | Supabase (PostgreSQL) | Free tier |
| Auth | Google OAuth 2.0 | Free |

---

## Project Structure

```
sleepbuddy-app/
├── app.py          # Main Streamlit app
├── auth.py         # Google OAuth
├── db.py           # Supabase — user data read/write
├── ai.py           # Claude Haiku requests
├── knowledge.py    # Knowledge base (AAP, WHO, NHS)
├── limits.py       # Daily usage limit (5/day)
├── requirements.txt
└── .streamlit/
    └── secrets.toml  # API keys (never commit this)
```

---

## Features

- **Google OAuth login** — user identified by Google email
- **Session memory** — baby age saved permanently; wake/nap times reset daily
- **Daily schedule generation** — AI-powered, based on age + wake-up time + naps taken
- **Usage limit** — 5 AI requests per user per day, auto-reset at midnight
- **Admin control** — block/unblock users, reset limits via Supabase Dashboard
- **Dynamic nap slots** — number of nap inputs adjusts based on baby's age (1–5 naps)
- **In-app manual** — collapsible how-to guide visible after login

---

## Setup

### 1. Supabase
1. Create a project at [supabase.com](https://supabase.com)
2. Run this SQL in the SQL Editor:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    is_blocked BOOLEAN DEFAULT FALSE,
    baby_age_months INTEGER DEFAULT 8,
    last_wake_time TEXT,
    last_nap1_start TEXT,
    last_nap1_end TEXT,
    last_nap2_start TEXT,
    last_nap2_end TEXT,
    last_nap3_start TEXT,
    last_nap3_end TEXT,
    daily_data_date DATE DEFAULT CURRENT_DATE,
    daily_uses INTEGER DEFAULT 0,
    daily_reset_date DATE DEFAULT CURRENT_DATE
);
```

3. Copy `Project URL` and `service_role` secret key

### 2. Google OAuth
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project → APIs & Services → Credentials
3. Configure OAuth consent screen (External)
4. Create OAuth 2.0 Client ID (Web Application)
5. Add Authorized redirect URI: `http://localhost:8501/callback`
6. Copy Client ID and Client Secret

### 3. Anthropic
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key

### 4. Configure secrets

Fill in `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-service-role-key"
GOOGLE_CLIENT_ID = "xxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-..."
APP_URL = "http://localhost:8501"
```

### 5. Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Admin Controls

| Action | Where |
|--------|-------|
| View all users | Supabase Dashboard → Table Editor → users |
| Block a user | Supabase → set `is_blocked = true` |
| Reset user limit | Supabase → set `daily_uses = 0` |
| Disable Google login | Google Cloud Console → disable OAuth app |
| Delete a user | Supabase → delete row from users table |

---

## Cost Estimate (Claude Haiku)

- Input: ~500 tokens = $0.0004
- Output: ~400 tokens = $0.0008
- **Total: ~$0.0012 per request**

At 5 requests/day per user: ~$0.006/user/day = **~$0.18/user/month**

---

## Deployment (Streamlit Cloud)

1. Push code to a private GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → connect repo
3. Settings → Secrets → paste contents of `secrets.toml`
4. Update `APP_URL` to your Streamlit Cloud URL
5. Add the Cloud URL to Google OAuth authorized redirect URIs

---

⚠️ Educational tool only. Does not replace consultation with a pediatrician.

---

## TODO

- [ ] Set up [UptimeRobot](https://uptimerobot.com) — free HTTP monitor pinging the app every 5 min to prevent cold starts (1-3 min load time on Streamlit free tier)
