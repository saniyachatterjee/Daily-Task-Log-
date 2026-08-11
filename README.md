# Field Log — Streamlit version

A Streamlit version of Saniya's TraceLink Field Log.

## What changed

- **Today's Entry → Tasks completed** is now a true multi-task input: each task gets its own bullet-style input row.
- Click **＋ Add task** for as many completed tasks as needed.
- Existing entries written in the old `- task` text format are automatically converted to task lists.
- Manager View renders completed work as clean bullet lists instead of one large text block.
- The app can be hosted on **Streamlit Community Cloud**, so Saniya and her UK-based manager do not need to be on the same Wi-Fi/VPN.
- The manager dashboard is read-only for work entries and is available at `?view=manager`.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints, normally `http://localhost:8501`.

## Manager link

After deployment, give your manager:

```text
https://YOUR-APP-NAME.streamlit.app/?view=manager
```

This is a cloud URL, so it works from India and the UK regardless of local office Wi-Fi/VPN, provided the Streamlit app is reachable from the internet.

## Important data note

This version keeps entries in `data/entries.json` and manager notes in `data/manager_notes.json` so it works immediately and remains compatible with the original project.

**For a production Streamlit Cloud deployment, use a persistent external database/storage layer** (for example Supabase, Google Sheets, or another hosted datastore) if you need entries to survive app restarts/redeployments reliably. Streamlit Cloud's local filesystem should not be treated as permanent storage.

## Streamlit Cloud deployment

1. Put this folder in a GitHub repository.
2. Open Streamlit Community Cloud and create a new app from that repository.
3. Set the main file to `app.py`.
4. Deploy.
5. Copy the resulting `https://...streamlit.app` URL.
6. Append `/?view=manager` for the manager's read-only view.

## Privacy

The app currently uses a URL-based manager view rather than authentication, matching the original tool's no-login design. Anyone who has the manager URL can open it. If the log contains sensitive information, add authentication before making it public.
