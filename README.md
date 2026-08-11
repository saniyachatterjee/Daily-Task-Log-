# Field Log — Streamlit

Daily ops tracker + working journal for Network Success Operations, styled in
TraceLink's actual Anthem brand colors (Evergreen, Deep Ocean, Cyan, Emerald).

## Deploying to your existing Streamlit app (dailytasklog.streamlit.app)

1. Push `app.py`, `requirements.txt`, `.streamlit/`, and an empty `data/`
   folder to the GitHub repo `dailytasklog.streamlit.app` is connected to,
   replacing what's there now.
2. Streamlit Cloud auto-redeploys within a minute or two of the push.

## Two links, one app

- **You:** `https://dailytasklog.streamlit.app/` — opens on My Log.
- **Your manager:** `https://dailytasklog.streamlit.app/?view=manager` —
  opens straight into Manager View.

Both URLs hit the same running app and the same data, so anything you save
shows up for her too — but she has to **refresh her tab** to see it; Streamlit
doesn't push live updates into an already-open page.

## Permanent storage: Google Sheets (recommended for a 1-year internship)

The default `data/entries.json` file is **ephemeral** on Streamlit Cloud — a
redeploy or the app sleeping from inactivity can reset it to the seeded data.
For something you're relying on for a full year, wire it to a Google Sheet
instead. The app already supports this — it just needs credentials.

**Setup (one-time, ~10 minutes):**

1. Go to console.cloud.google.com → create a project (or use an existing one).
2. Enable the **Google Sheets API** and **Google Drive API** for that project
   (APIs & Services → Library → search each → Enable).
3. Create a **Service Account**: APIs & Services → Credentials → Create
   Credentials → Service Account. Give it any name.
4. Open the service account → Keys → Add Key → Create new key → JSON.
   This downloads a `.json` file — keep it private, never commit it to GitHub.
5. Create (or reuse) a Google Sheet for this tracker. Open the downloaded JSON,
   copy the `client_email` value, and **Share** the Sheet with that email as
   **Editor**.
6. Copy the Sheet's ID from its URL: the long string between `/d/` and
   `/edit` in `https://docs.google.com/spreadsheets/d/<THIS_PART>/edit`.
7. In your Streamlit Cloud app → **Settings → Secrets**, paste (filling in
   values from the downloaded JSON and step 6):

```toml
sheet_id = "paste-the-sheet-id-here"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"
```

8. Save — the app redeploys and now reads/writes that Google Sheet instead of
   the local file. It creates two tabs automatically: `entries` and
   `manager_notes`. Nothing else in the app changes — same UI, same links.

Without these secrets configured, the app keeps working exactly as before on
the local JSON file (handy for testing on your own machine).

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
