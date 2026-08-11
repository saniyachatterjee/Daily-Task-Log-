# Field Log — Streamlit

Daily ops tracker + working journal for Network Success Operations, styled in
TraceLink's actual Anthem brand colors (Evergreen, Deep Ocean, Cyan, Emerald).

## Deploying to your existing Streamlit app (dailytasklog.streamlit.app)

1. Push these three files (`app.py`, `requirements.txt`, and an empty `data/`
   folder) to the GitHub repo that `dailytasklog.streamlit.app` is connected to,
   replacing what's there now.
2. Streamlit Cloud will auto-redeploy within a minute or two of the push.
3. Open the app — you'll land on **My Log**. Switch to **Manager View** from
   the sidebar to see the read-only rollup, comment box, and export buttons.

## Important: data persistence on Streamlit Cloud

Streamlit Community Cloud's filesystem is **ephemeral** — `data/entries.json`
persists while the app is running and being used, but a redeploy (e.g. pushing
new code) or the app going to sleep from inactivity can reset it back to the
seeded starting data.

For a personal tracker this is usually fine day-to-day, but if you want entries
to survive redeploys/sleep permanently, the next step up is pointing this at
a real backend — either your original Google Sheet (via `gspread` + a service
account) or a small hosted database (e.g. Supabase). Happy to wire either of
those up if you want it — just say the word.

## What's on each view

**My Log** (you)
- Today's Entry — ops fields (tasks, goals, hours, status, notes) manager sees,
  plus a Journal section (learning, idea, reflection) with a private toggle
- Ops Log — full table of every day
- Journal — your reflections as a timeline

**Manager View** (her)
- Read-only weekly rollup tables (private reflections excluded)
- Download the full spreadsheet (.xlsx) — same columns as your original
  Google Sheet, plus journal/manager-note columns
- Download a Word report (.docx) for any given week
- Leave a comment on a specific day, or a general note — both show back to you

## Local testing
```
pip install -r requirements.txt
streamlit run app.py
```
