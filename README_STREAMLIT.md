# TraceLink Field Log — Streamlit version

This replaces the Flask UI with a Streamlit UI while keeping the same workflow:
- Today's Entry
- Ops Log
- Journal
- Manager View
- Manager feedback
- multiple tasks/goals per day
- private reflection
- persistent storage

## The task input is now multi-row

Today's Entry uses Streamlit's `st.data_editor` with dynamic rows, so you get one row per completed task instead of one giant textbox. You can add/delete rows and paste multiple tasks from Excel/Sheets.

## Storage

There are two modes:

1. **Supabase/Postgres (recommended for your 1-year internship)**
   - permanent cloud database
   - survives app restarts/redeploys
   - manager can see changes even when your laptop is off
   - configure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in Streamlit Secrets

2. **Local SQLite fallback**
   - if Supabase is not configured, the app creates `field_log.db`
   - this is persistent on your own computer
   - it is NOT suitable as the production database for an online Streamlit deployment because hosted app files can be ephemeral

The existing JSON data from the Flask version is automatically imported into SQLite on first run if `data/entries.json` exists.

## Updates to your manager

When the manager dashboard is open, the Live Updates panel checks the database every 15 seconds using Streamlit fragments.

That means:
1. you save an entry;
2. it is written to Supabase;
3. your manager's open dashboard checks the database;
4. the new entry appears without her manually refreshing the whole page.

This is a dashboard update, not a phone/email notification. If you want a notification such as "Saniya added today's update" by email/Teams/Slack, that can be added separately.

## Setup locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py
```

Open the URL Streamlit prints, usually `http://localhost:8501`.

Default demo passwords:
- user: `saniya-demo`
- manager: `manager-demo`

Change them before hosting.

## Supabase setup

1. Create a Supabase project.
2. Open SQL Editor.
3. Run `supabase_schema.sql`.
4. Copy the project's URL and service-role key.
5. Put them in `.streamlit/secrets.toml` locally or Streamlit Cloud Secrets online.
6. Change both passwords.

Use the service-role key ONLY as a server-side Streamlit secret. Never put it into browser JavaScript, GitHub, or a public repository.

## Hosting

A simple production setup is:

Streamlit app → Supabase Postgres

Your laptop does not need to stay on. You and your manager both open the hosted Streamlit URL.

For an internship-long tracker, this is preferable to keeping `entries.json` on a hosted filesystem.

## Important privacy point

The current manager dashboard is intentionally read-only for work information. Private reflections stay in the user's Journal and are not displayed in the manager dashboard.

If the app is deployed publicly, keep the password gate enabled and do not commit `.streamlit/secrets.toml`.
