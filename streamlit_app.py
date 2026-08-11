import os
import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# Optional online database
try:
    from supabase import create_client
except ImportError:
    create_client = None

st.set_page_config(
    page_title="TraceLink Field Log",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
LOCAL_DB = APP_DIR / "field_log.db"
LEGACY_JSON = APP_DIR / "data" / "entries.json"

SEED = {
    "2026-08-03": {
        "date": "2026-08-03",
        "tasks": [
            "Reviewed, edited and sent 13 T18 documents to Alok",
            "Worked on Conval and Excellis Audit Report spreadsheet for Pooja",
        ],
        "goals": ["Work on more T18 documents"],
        "hours": 7,
        "status": "on-track",
        "notes": "",
        "learning": "",
        "idea": "",
        "reflection": "",
    },
    "2026-08-04": {
        "date": "2026-08-04",
        "tasks": [
            "Reviewed, edited and sent all remaining T18 documents",
            "Finished some Litmos courses",
            "Meeting with Alok, Pooja, Deepak on Partner Scorecard Dashboard",
        ],
        "goals": ["Set clearer goal for next day"],
        "hours": 6,
        "status": "on-track",
        "notes": "Which Litmos course, how much time per activity — need to specify daily goals better",
        "learning": "",
        "idea": "",
        "reflection": "",
    },
    "2026-08-05": {
        "date": "2026-08-05",
        "tasks": [
            "Litmos courses completed: FOSCM, QMS Privacy & Data Protection, NS Overview for New Hires, QMS CS01 Technical Support, Preventing Harassment (Global Workplace), QMS Data Integrity Policy",
        ],
        "goals": [
            "Complete QMS PS01 course",
            "Complete more Litmos courses",
            "Prepare and attend SPE Monthly Meet",
            "Attend Use Org (Services Training) Meet",
        ],
        "hours": 7,
        "status": "on-track",
        "notes": "",
        "learning": "",
        "idea": "",
        "reflection": "",
    },
    "2026-08-06": {
        "date": "2026-08-06",
        "tasks": [
            "Meetings attended: SPE Monthly Meeting, Use Org (Services Training) Meet",
            "Litmos completed: QMS PS01, SVC Use Org Training, Intro to GS1 Standards, OPUS No Code Fundamentals, MINT External Manufacturing Configuration",
        ],
        "goals": [
            "Complete all remaining Litmos courses before 8 Aug deadline",
            "Weekly catchup with manager",
        ],
        "hours": 7,
        "status": "under",
        "notes": "Litmos deadline is tight — running behind on hours logged mid-week",
        "learning": "",
        "idea": "",
        "reflection": "",
    },
}


# -------------------- Database layer --------------------

def secrets_get(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def get_supabase():
    if create_client is None:
        return None
    url = secrets_get("SUPABASE_URL")
    key = secrets_get("SUPABASE_SERVICE_ROLE_KEY") or secrets_get("SUPABASE_KEY")
    if url and key:
        try:
            return create_client(url, key)
        except Exception:
            return None
    return None


def init_local_db():
    con = sqlite3.connect(LOCAL_DB, check_same_thread=False)
    con.execute(
        """CREATE TABLE IF NOT EXISTS entries (
            entry_date TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS manager_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT NOT NULL,
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    con.commit()
    return con


LOCAL_CON = init_local_db()
SB = get_supabase()


def normalize_entry(e):
    e = dict(e)
    for key in ("tasks", "goals"):
        value = e.get(key, [])
        if isinstance(value, str):
            value = [x.strip().lstrip("-• ").strip() for x in value.splitlines() if x.strip()]
        e[key] = [x for x in value if str(x).strip()]
    e["hours"] = float(e.get("hours") or 0)
    e["status"] = e.get("status") or "on-track"
    return e


def get_entries():
    if SB:
        try:
            res = SB.table("entries").select("*").order("entry_date").execute()
            rows = res.data or []
            return {
                r["entry_date"]: normalize_entry({
                    "date": r["entry_date"],
                    "tasks": r.get("tasks") or [],
                    "goals": r.get("goals") or [],
                    "hours": r.get("hours") or 0,
                    "status": r.get("status") or "on-track",
                    "notes": r.get("notes") or "",
                    "learning": r.get("learning") or "",
                    "idea": r.get("idea") or "",
                    "reflection": r.get("reflection") or "",
                })
                for r in rows
            }
        except Exception as exc:
            st.warning(f"Online database unavailable; using local database. ({exc})")

    rows = LOCAL_CON.execute("SELECT entry_date, payload FROM entries ORDER BY entry_date").fetchall()
    if not rows:
        # First-run seed. Also import the legacy JSON if it exists.
        source = {}
        if LEGACY_JSON.exists():
            try:
                source = json.loads(LEGACY_JSON.read_text(encoding="utf-8"))
            except Exception:
                source = {}
        if not source:
            source = SEED
        for k, v in source.items():
            save_entry(normalize_entry(v), silent=True)
        rows = LOCAL_CON.execute("SELECT entry_date, payload FROM entries ORDER BY entry_date").fetchall()

    return {d: normalize_entry(json.loads(payload)) for d, payload in rows}


def save_entry(entry, silent=False):
    entry = normalize_entry(entry)
    now = datetime.now().isoformat(timespec="seconds")
    if SB:
        try:
            SB.table("entries").upsert({
                "entry_date": entry["date"],
                "tasks": entry["tasks"],
                "goals": entry["goals"],
                "hours": entry["hours"],
                "status": entry["status"],
                "notes": entry["notes"],
                "learning": entry["learning"],
                "idea": entry["idea"],
                "reflection": entry["reflection"],
                "updated_at": now,
            }, on_conflict="entry_date").execute()
            return
        except Exception as exc:
            if not silent:
                st.error(f"Could not save to the online database: {exc}")
                return

    LOCAL_CON.execute(
        """INSERT INTO entries(entry_date, payload, updated_at)
           VALUES (?, ?, ?)
           ON CONFLICT(entry_date) DO UPDATE SET payload=excluded.payload,
           updated_at=excluded.updated_at""",
        (entry["date"], json.dumps(entry), now),
    )
    LOCAL_CON.commit()


def delete_entry(iso):
    if SB:
        try:
            SB.table("entries").delete().eq("entry_date", iso).execute()
            return
        except Exception as exc:
            st.error(f"Could not delete from online database: {exc}")
            return
    LOCAL_CON.execute("DELETE FROM entries WHERE entry_date=?", (iso,))
    LOCAL_CON.commit()


def get_notes():
    if SB:
        try:
            res = SB.table("manager_notes").select("*").order("created_at", desc=True).execute()
            return res.data or []
        except Exception:
            pass
    rows = LOCAL_CON.execute(
        "SELECT id, week_start, text, author, created_at FROM manager_notes ORDER BY created_at DESC"
    ).fetchall()
    return [
        {"id": r[0], "week_start": r[1], "text": r[2], "author": r[3], "created_at": r[4]}
        for r in rows
    ]


def add_note(week_start, text, author):
    now = datetime.now().isoformat(timespec="seconds")
    if SB:
        try:
            SB.table("manager_notes").insert({
                "week_start": week_start,
                "text": text,
                "author": author,
                "created_at": now,
            }).execute()
            return True
        except Exception as exc:
            st.error(f"Could not save manager note: {exc}")
            return False
    LOCAL_CON.execute(
        "INSERT INTO manager_notes(week_start,text,author,created_at) VALUES (?,?,?,?)",
        (week_start, text, author, now),
    )
    LOCAL_CON.commit()
    return True


# -------------------- Auth --------------------

def check_password(role):
    if role == "manager":
        return secrets_get("MANAGER_PASSWORD", "manager-demo")
    return secrets_get("APP_PASSWORD", "saniya-demo")


if "role" not in st.session_state:
    st.session_state.role = None


def login():
    st.title("📘 TraceLink Field Log")
    st.caption("Private internship tracker · Saniya")
    st.write("Choose your dashboard.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("My dashboard")
        pw = st.text_input("Password", type="password", key="user_pw")
        if st.button("Open my dashboard", use_container_width=True):
            if pw == check_password("user"):
                st.session_state.role = "user"
                st.rerun()
            else:
                st.error("Incorrect password.")
    with c2:
        st.subheader("Manager dashboard")
        pw = st.text_input("Manager password", type="password", key="manager_pw")
        if st.button("Open manager dashboard", use_container_width=True):
            if pw == check_password("manager"):
                st.session_state.role = "manager"
                st.rerun()
            else:
                st.error("Incorrect manager password.")

    st.info("For local-only use, the defaults are shown in the setup guide. For online hosting, put your own passwords in Streamlit Secrets.")


# -------------------- Helpers --------------------

def week_start(iso):
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return (d - timedelta(days=d.weekday())).isoformat()


def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def tasks_to_df(items):
    return pd.DataFrame({"Task completed": items or [""]})


def goals_to_df(items):
    return pd.DataFrame({"Goal": items or [""]})


def clean_rows(df, column):
    return [str(x).strip() for x in df[column].tolist() if str(x).strip() and str(x).strip().lower() != "nan"]


def entry_to_row(e):
    return {
        "Date": fmt_date(e["date"]),
        "Day": datetime.strptime(e["date"], "%Y-%m-%d").strftime("%a"),
        "Tasks completed": "\n".join(f"• {x}" for x in e["tasks"]),
        "Goals for next day": "\n".join(f"• {x}" for x in e["goals"]),
        "Hours": e["hours"],
        "Status": e["status"].replace("-", " ").title(),
        "Notes / blockers": e["notes"],
        "Key learning": e["learning"],
        "Idea / spark": e["idea"],
    }


def logout_sidebar():
    st.sidebar.divider()
    if st.button("Log out", use_container_width=True):
        st.session_state.role = None
        st.rerun()


# -------------------- User dashboard --------------------

def render_today():
    today = date.today().isoformat()
    entries = get_entries()
    existing = entries.get(today, {
        "date": today, "tasks": [""], "goals": [""], "hours": 0,
        "status": "on-track", "notes": "", "learning": "", "idea": "", "reflection": "",
    })

    st.header("Today’s Entry")
    st.caption(f"{fmt_date(today)} · Log your work as you go.")

    st.subheader("Tasks completed")
    st.caption("One task per bullet. Add or delete rows as needed.")
    task_df = st.data_editor(
        tasks_to_df(existing["tasks"]),
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        row_height=38,
        column_config={
            "Task completed": st.column_config.TextColumn(
                "• Task completed",
                width="large",
                help="Write one completed task per row.",
            )
        },
        key=f"tasks_{today}",
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Goals for next day")
        goal_df = st.data_editor(
            goals_to_df(existing["goals"]),
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            row_height=38,
            column_config={"Goal": st.column_config.TextColumn("→ Goal", width="large")},
            key=f"goals_{today}",
        )
    with c2:
        st.subheader("Workday")
        hours = st.number_input("Hours", min_value=0.0, max_value=24.0, step=0.5, value=float(existing["hours"]))
        status = st.selectbox(
            "Status",
            ["on-track", "under", "ahead"],
            index=["on-track", "under", "ahead"].index(existing["status"]) if existing["status"] in ["on-track", "under", "ahead"] else 0,
        )

    st.subheader("Notes & journal")
    notes = st.text_area("Notes / blockers", value=existing["notes"], height=90)
    learning = st.text_area("Key learning", value=existing["learning"], height=90)
    idea = st.text_area("Idea / spark", value=existing["idea"], height=90)
    reflection = st.text_area("Private reflection", value=existing["reflection"], height=100)

    if st.button("Save today’s entry", type="primary", use_container_width=True):
        save_entry({
            "date": today,
            "tasks": clean_rows(task_df, "Task completed"),
            "goals": clean_rows(goal_df, "Goal"),
            "hours": hours,
            "status": status,
            "notes": notes,
            "learning": learning,
            "idea": idea,
            "reflection": reflection,
        })
        st.success("Saved. Your manager dashboard will see the update the next time it refreshes.")


def render_ops_log():
    entries = get_entries()
    st.header("Ops Log")
    if not entries:
        st.info("No entries yet.")
        return
    rows = [entry_to_row(entries[d]) for d in sorted(entries, reverse=True)]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=500)


def render_manager_view():
    entries = get_entries()
    st.header("Manager View")
    st.caption("This is the same read-only view your manager sees.")

    visible = []
    for d in sorted(entries, reverse=True):
        e = entries[d]
        visible.append(entry_to_row(e))
    if visible:
        st.dataframe(pd.DataFrame(visible), hide_index=True, width="stretch", height=520)
    else:
        st.info("No work entries yet.")

    st.subheader("Manager feedback")
    notes = get_notes()
    for n in notes:
        st.info(f"**{n.get('author','Manager')} · week of {fmt_date(n['week_start'])}**\n\n{n['text']}")


def render_journal():
    entries = get_entries()
    st.header("Journal")
    st.caption("Private reflections are not shown in Manager View.")
    for d in sorted(entries, reverse=True):
        e = entries[d]
        if e.get("learning") or e.get("idea") or e.get("reflection"):
            with st.expander(f"{fmt_date(d)}"):
                if e.get("learning"):
                    st.markdown("**Key learning**")
                    st.write(e["learning"])
                if e.get("idea"):
                    st.markdown("**Idea / spark**")
                    st.write(e["idea"])
                if e.get("reflection"):
                    st.markdown("**Private reflection**")
                    st.write(e["reflection"])


@st.fragment(run_every="15s")
def live_manager_feed():
    st.subheader("Live updates")
    entries = get_entries()
    latest = sorted(entries.values(), key=lambda x: x["date"], reverse=True)
    if latest:
        e = latest[0]
        st.success(f"Latest entry: **{fmt_date(e['date'])}** · {len(e['tasks'])} task(s) · {e['hours']} hours")
        for task in e["tasks"]:
            st.markdown(f"• {task}")
    else:
        st.info("No entries yet.")
    st.caption("This panel checks the database every 15 seconds while the page is open.")


def render_feedback():
    st.header("Feedback")
    notes = get_notes()
    if not notes:
        st.info("No manager notes yet.")
        return
    for n in notes:
        st.container(border=True).markdown(
            f"**{n.get('author','Manager')} · week of {fmt_date(n['week_start'])}**\n\n{n['text']}"
        )


def user_dashboard():
    st.sidebar.title("📘 Field Log")
    st.sidebar.caption("Saniya · TraceLink")
    page = st.sidebar.radio("Navigate", ["Today’s Entry", "Ops Log", "Journal", "Manager View", "Feedback"])
    st.sidebar.caption("Database: " + ("Supabase/Postgres" if SB else "Local SQLite"))
    logout_sidebar()

    if page == "Today’s Entry":
        render_today()
    elif page == "Ops Log":
        render_ops_log()
    elif page == "Journal":
        render_journal()
    elif page == "Manager View":
        render_manager_view()
    else:
        render_feedback()


# -------------------- Manager dashboard --------------------

def manager_dashboard():
    st.sidebar.title("📘 Manager View")
    st.sidebar.caption("Read-only · TraceLink")
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.role = None
        st.rerun()

    st.title("TraceLink · Weekly Field Log")
    st.caption("Read-only manager dashboard · live database")

    live_manager_feed()

    entries = get_entries()
    st.divider()
    st.subheader("All weekly activity")

    weeks = sorted({week_start(d) for d in entries}, reverse=True)
    if not weeks:
        st.info("No entries yet.")
    else:
        for ws in weeks:
            week_entries = [entries[d] for d in sorted(entries) if week_start(d) == ws]
            total_hours = sum(float(e["hours"]) for e in week_entries)
            with st.expander(f"Week of {fmt_date(ws)} · {total_hours:g} hours", expanded=(ws == weeks[0])):
                rows = [entry_to_row(e) for e in week_entries]
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
                st.markdown("**Manager note / suggestion**")
                note = st.text_area("Write feedback", key=f"note_{ws}", height=80, label_visibility="collapsed")
                if st.button("Save note", key=f"save_note_{ws}"):
                    if note.strip():
                        if add_note(ws, note.strip(), "Manager"):
                            st.success("Feedback saved.")
                            st.rerun()
                    else:
                        st.warning("Write a note first.")


# -------------------- Main --------------------

if st.session_state.role is None:
    login()
elif st.session_state.role == "manager":
    manager_dashboard()
else:
    user_dashboard()
