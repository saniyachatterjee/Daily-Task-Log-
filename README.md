# TraceLink Field Log — exact Streamlit UI

This version preserves the existing dashboard design and adds the requested workflow improvements.

## Changes in this version

- Today's Entry → **Tasks completed** uses separate bullet-style rows with **＋ Add task**.
- Today's Entry → **Goals for next day** now uses the same separate bullet-style rows with **＋ Add goal**.
- The intern dashboard has a full spreadsheet download under **Downloads**.
- The manager dashboard has the same full spreadsheet download under **Downloads**.
- The spreadsheet contains the daily log plus a Manager Notes sheet.
- Manager View remains read-only for work entries.
- Manager View refreshes its database data every 15 seconds while it is open.
- Supabase/Postgres is supported as persistent cloud storage; local JSON remains a fallback.
- A dedicated `MANAGER_GUIDE.md` is included for your manager.

## Your current links

**Intern dashboard:**
https://dailytasklog.streamlit.app/

**Manager dashboard — send this to your manager:**
https://dailytasklog.streamlit.app/?view=manager

The manager link opens only the read-only Manager View. Both dashboards read from the same database, so when you save an entry on the intern dashboard, the manager dashboard is the one that receives/reflects that update.

## How updates work

1. You open the intern dashboard.
2. You enter today's tasks and goals as separate bullets.
3. You click **Save entry**.
4. The entry is written to Supabase when Supabase is configured.
5. The manager dashboard re-reads the database every 15 seconds while open.
6. Your saved work appears in Manager View without her needing to edit or re-enter anything.

This is a dashboard update, not an email/Teams/Slack notification.

## Storage

For a one-year internship, use Supabase/Postgres for production. The local JSON files are only a fallback. Do not rely on Streamlit Cloud's local filesystem as the permanent database.

## Supabase

Run `supabase_schema.sql` in Supabase SQL Editor, then add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` to Streamlit Secrets.

## Local

```bash
pip install -r requirements.txt
streamlit run app.py
```
