import json
import os
import threading
from datetime import date, datetime, timedelta
from io import BytesIO

import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ENTRIES_FILE = os.path.join(DATA_DIR, "entries.json")
NOTES_FILE = os.path.join(DATA_DIR, "manager_notes.json")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
LOCK = threading.Lock()

SEED = {
    "2026-08-03": {"date": "2026-08-03", "tasks": ["Reviewed, edited and sent 13 T18 documents to Alok", "Worked on Conval and Excellis Audit Report spreadsheet for Pooja"], "goals": "- Work on more T18 documents", "hours": 7, "status": "on-track", "notes": "", "learning": "", "idea": "", "reflection": "", "private": True},
    "2026-08-04": {"date": "2026-08-04", "tasks": ["Reviewed, edited and sent all remaining T18 documents", "Finished some Litmos courses", "Meeting with Alok, Pooja, Deepak on Partner Scorecard Dashboard"], "goals": "Set clearer goal for next day", "hours": 6, "status": "on-track", "notes": "Which Litmos course, how much time per activity — need to specify daily goals better", "learning": "", "idea": "", "reflection": "", "private": True},
    "2026-08-05": {"date": "2026-08-05", "tasks": ["Litmos courses completed: FOSCM, QMS Privacy & Data Protection, NS Overview for New Hires, QMS CS01 Technical Support, Preventing Harassment (Global Workplace), QMS Data Integrity Policy"], "goals": "- Complete QMS PS01 course\n- Complete more Litmos courses\n- Prepare and attend SPE Monthly Meet\n- Attend Use Org (Services Training) Meet", "hours": 7, "status": "on-track", "notes": "", "learning": "", "idea": "", "reflection": "", "private": True},
    "2026-08-06": {"date": "2026-08-06", "tasks": ["Meetings attended: SPE Monthly Meeting, Use Org (Services Training) Meet.", "Litmos completed: QMS PS01, SVC Use Org Training, Intro to GS1 Standards, OPUS No Code Fundamentals, MINT External Manufacturing Configuration"], "goals": "- Complete all remaining Litmos courses before 8 Aug deadline\n- Weekly catchup with manager", "hours": 7, "status": "under", "notes": "Litmos deadline is tight — running behind on hours logged mid-week", "learning": "", "idea": "", "reflection": "", "private": True},
}


def normalize_tasks(value):
    if isinstance(value, list):
        return [str(x).strip().lstrip("-•* ").strip() for x in value if str(x).strip()]
    text = str(value or "").strip()
    if not text:
        return []
    return [line.strip().lstrip("-•* ").strip() for line in text.splitlines() if line.strip()]


def normalize_entries(entries):
    changed = False
    for iso, entry in entries.items():
        tasks = normalize_tasks(entry.get("tasks"))
        if entry.get("tasks") != tasks:
            entry["tasks"] = tasks
            changed = True
    return entries, changed


def load_json(path, default):
    with LOCK:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=2, ensure_ascii=False)
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default


def save_json(path, value):
    with LOCK:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)


def load_entries():
    if not os.path.exists(ENTRIES_FILE):
        save_json(ENTRIES_FILE, SEED)
        return dict(SEED)
    entries = load_json(ENTRIES_FILE, {})
    entries, changed = normalize_entries(entries)
    if changed:
        save_json(ENTRIES_FILE, entries)
    return entries


def load_notes():
    return load_json(NOTES_FILE, [])


def save_entry(entry):
    entries = load_entries()
    entry = dict(entry)
    entry["tasks"] = normalize_tasks(entry.get("tasks"))
    entries[entry["date"]] = entry
    save_json(ENTRIES_FILE, entries)


def add_manager_note(week_start, author, text):
    notes = load_notes()
    notes.append({
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "week_start": week_start,
        "text": text.strip(),
        "author": author.strip() or "Manager",
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_json(NOTES_FILE, notes)


def day_name(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%A")


def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def week_start(iso):
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return (d - timedelta(days=d.weekday())).isoformat()


def tasks_text(tasks):
    return "\n".join(f"- {task}" for task in normalize_tasks(tasks))


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700;9..144,800&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        /* TraceLink brand palette: Evergreen #006341, Citron #ECE81A, White */
        :root{--green-dark:#00301F;--green:#006341;--green-mid:#0B8558;--citron:#ECE81A;--line:#D3ECDE;}
        html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}
        .stApp{background:radial-gradient(circle at 8% 0%,rgba(0,99,65,.08),transparent 40%),radial-gradient(circle at 100% 10%,rgba(236,232,26,.10),transparent 45%),#F6FBF8;}
        h1,h2,h3{font-family:'Fraunces',serif !important;}
        .hero{background:linear-gradient(120deg,#00301F,#006341 45%,#0B8558 80%,#ECE81A);padding:28px 32px;border-radius:0 0 22px 22px;color:white;margin:-1rem -1rem 1.5rem -1rem;box-shadow:0 8px 32px rgba(0,48,31,.25);}
        .hero-eyebrow{font:700 12px 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#ECE81A;}
        .hero h1{font-size:44px;margin:4px 0;color:white !important;}
        .hero p{margin:0;color:#E3F5EC;}
        .task-card{background:white;border:1px solid #D3ECDE;border-radius:14px;padding:10px 12px;margin-bottom:8px;box-shadow:0 2px 8px rgba(0,99,65,.06);}
        .task-number{font:700 12px 'IBM Plex Mono',monospace;color:#006341;padding-top:9px;}
        .manager-banner{background:#E3F3EC;border:1px solid #BFE3D2;border-radius:12px;padding:14px 16px;color:#00432C;}
        .task-list{margin:0;padding-left:20px;}
        .task-list li{margin-bottom:5px;}
        .small-muted{color:#6b7280;font-size:.85rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(manager=False):
    label = "MANAGER VIEW" if manager else "YOUR DASHBOARD"
    subtitle = "Read-only overview of Saniya's daily progress" if manager else "Daily ops tracking & working journal — Saniya"
    st.markdown(f'<div class="hero"><div class="hero-eyebrow">Intern · TraceLink · {label}</div><div class="hero h1"><h1>Field Log</h1></div><p>{subtitle}</p></div>', unsafe_allow_html=True)


def render_task_list(tasks):
    tasks = normalize_tasks(tasks)
    if not tasks:
        st.caption("No tasks logged.")
        return
    st.markdown('<ul class="task-list">' + ''.join(f'<li>{task.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</li>' for task in tasks) + '</ul>', unsafe_allow_html=True)


def render_stats(entries):
    today = date.today()
    ws = (today - timedelta(days=today.weekday())).isoformat()
    week_entries = [e for d,e in entries.items() if week_start(d) == ws]
    hours = sum(float(e.get("hours") or 0) for e in week_entries)
    on = sum(e.get("status") == "on-track" for e in week_entries)
    under = sum(e.get("status") == "under" for e in week_entries)
    blocked = sum(e.get("status") == "blocked" for e in week_entries)
    cols = st.columns(6)
    vals = [(len(week_entries),"Entries this week"),(hours,"Hours this week"),(on,"On track"),(under,"Under target"),(blocked,"Blocked"),(len(entries),"Total days")]
    for col,(v,lbl) in zip(cols,vals):
        col.metric(lbl, v)


def render_entry(entries):
    st.header("Log a day")
    st.caption("Add each completed task as its own bullet. Use + Add task when you have more work to record.")
    dates = sorted(entries.keys())
    default = date.today()
    if dates and default.isoformat() not in entries:
        default = date.today()
    selected = st.date_input("Date", value=default, key="entry_date")
    iso = selected.isoformat()
    existing = entries.get(iso, {})
    st.caption(f"{day_name(iso)} · {fmt_date(iso)}")

    existing_tasks = normalize_tasks(existing.get("tasks"))
    if "task_rows" not in st.session_state or st.session_state.get("task_date") != iso:
        st.session_state.task_rows = existing_tasks[:] if existing_tasks else [""]
        st.session_state.task_date = iso

    st.subheader("Ops — visible to manager")
    st.markdown("**Tasks completed**")
    st.caption("One task per line, with separate inputs for cleaner bullets in the Manager View.")
    remove_idx = None
    for i in range(len(st.session_state.task_rows)):
        c1, c2, c3 = st.columns([0.06, 0.84, 0.10])
        with c1:
            st.markdown(f'<div class="task-number">{i+1:02}</div>', unsafe_allow_html=True)
        with c2:
            st.session_state.task_rows[i] = st.text_input("", value=st.session_state.task_rows[i], key=f"task_{iso}_{i}", placeholder="e.g. Reviewed and sent T18 documents", label_visibility="collapsed")
        with c3:
            if len(st.session_state.task_rows) > 1 and st.button("✕", key=f"remove_{iso}_{i}"):
                remove_idx = i
    if remove_idx is not None:
        st.session_state.task_rows.pop(remove_idx)
        st.rerun()
    if st.button("＋ Add task", key=f"add_task_{iso}"):
        st.session_state.task_rows.append("")
        st.rerun()

    goals = st.text_area("Goals for tomorrow", value=existing.get("goals", ""), placeholder="- Finish remaining Litmos courses\n- Prep notes for weekly catchup")
    c1,c2 = st.columns(2)
    with c1:
        hours = st.number_input("Hours spent", min_value=0.0, max_value=16.0, step=0.5, value=float(existing.get("hours") or 0))
    with c2:
        status_options = ["on-track","under","blocked"]
        current_status = existing.get("status", "on-track") if existing.get("status") in status_options else "on-track"
        status = st.selectbox("Status", status_options, index=status_options.index(current_status), format_func=lambda x: {"on-track":"🟢 On track","under":"🟠 Under target","blocked":"🔴 Blocked"}[x])
    notes = st.text_area("Notes / blockers (optional)", value=existing.get("notes", ""), placeholder="Anything slowing you down or worth flagging")

    st.subheader("Journal — your working reflection")
    learning = st.text_area("Key learning today", value=existing.get("learning", ""))
    idea = st.text_area("Idea / spark (optional)", value=existing.get("idea", ""))
    reflection = st.text_area("Thoughts / reflection", value=existing.get("reflection", ""))
    private = st.checkbox("Keep this reflection private (excluded from Manager View)", value=existing.get("private", True))

    if st.button("Save entry", type="primary", use_container_width=True):
        clean_tasks = [x.strip() for x in st.session_state.task_rows if x.strip()]
        save_entry({"date":iso,"tasks":clean_tasks,"goals":goals,"hours":hours,"status":status,"notes":notes,"learning":learning,"idea":idea,"reflection":reflection,"private":private})
        st.success("Entry saved.")
        st.rerun()


def render_ops_log(entries):
    st.header("Ops Log")
    if not entries:
        st.info("No entries yet.")
        return
    for iso in sorted(entries.keys(), reverse=True):
        e = entries[iso]
        with st.expander(f"{fmt_date(iso)} · {day_name(iso)} · {e.get('hours',0)}h · {e.get('status','on-track').replace('-',' ').title()}", expanded=(iso == date.today().isoformat())):
            render_task_list(e.get("tasks"))
            st.write(f"**Goals:** {e.get('goals') or '—'}")
            st.write(f"**Notes / blockers:** {e.get('notes') or '—'}")


def render_journal(entries):
    st.header("Journal")
    rows = [(d,e) for d,e in sorted(entries.items(), reverse=True) if e.get("learning") or e.get("idea") or e.get("reflection")]
    if not rows:
        st.info("No journal reflections yet.")
        return
    for iso,e in rows:
        with st.expander(f"{fmt_date(iso)} · {day_name(iso)}"):
            if e.get("learning"): st.write("**Key learning**", e["learning"])
            if e.get("idea"): st.write("**Idea / spark**", e["idea"])
            if e.get("reflection"): st.write("**Reflection**", e["reflection"])
            if e.get("private", True): st.caption("Reflection marked private in the Manager View.")


def render_manager(entries, notes):
    render_header(manager=True)
    st.markdown('<div class="manager-banner">This is a read-only manager dashboard. Work updates are visible here; private reflections are not. Your manager can leave feedback below each week.</div>', unsafe_allow_html=True)
    st.write("")
    render_stats(entries)
    if not entries:
        st.info("Nothing logged yet.")
        return
    weeks = {}
    for iso in entries:
        weeks.setdefault(week_start(iso), []).append(iso)
    for ws in sorted(weeks.keys(), reverse=True):
        wdates = sorted(weeks[ws])
        total_hours = sum(float(entries[d].get("hours") or 0) for d in wdates)
        st.subheader(f"Week of {fmt_date(ws)} · {total_hours:g}h logged")
        for iso in wdates:
            e = entries[iso]
            with st.container(border=True):
                c1,c2 = st.columns([0.18,0.82])
                with c1:
                    st.markdown(f"**{fmt_date(iso)}**")
                    st.caption(day_name(iso))
                    st.caption(f"{e.get('hours',0)}h · {e.get('status','on-track').replace('-',' ').title()}")
                with c2:
                    st.markdown("**Tasks completed**")
                    render_task_list(e.get("tasks"))
                    st.markdown(f"**Goals:** {e.get('goals') or '—'}")
                    if e.get("learning"):
                        st.markdown(f"**Key learning:** {e['learning']}")
                    if e.get("idea"):
                        st.markdown(f"**Idea:** {e['idea']}")
        st.markdown("**Leave a note or suggestion for this week**")
        c1,c2,c3 = st.columns([0.2,0.6,0.2])
        author = c1.text_input("Name", value="Manager", key=f"author_{ws}")
        text = c2.text_input("Note", placeholder="Comment, suggestion, or feedback", key=f"note_{ws}")
        if c3.button("Post note", key=f"post_{ws}"):
            if text.strip():
                add_manager_note(ws, author, text)
                st.success("Note posted.")
                st.rerun()
            else:
                st.warning("Please enter a note first.")
        week_notes = [n for n in notes if n.get("week_start") == ws]
        for n in week_notes:
            st.info(f"**{n.get('author','Manager')}** · {n.get('ts','')}\n\n{n.get('text','')}")


def render_feedback(notes):
    st.header("Feedback")
    if not notes:
        st.info("No manager notes yet.")
        return
    for n in sorted(notes, key=lambda x:(x.get("week_start",""),x.get("ts","")), reverse=True):
        st.container(border=True).markdown(f"**{n.get('author','Manager')}** · Week of {fmt_date(n.get('week_start'))} · {n.get('ts','')}\n\n{n.get('text','')}")


def build_word(entries, ws):
    from docx import Document
    from docx.shared import RGBColor
    doc = Document()
    title = doc.add_heading("Weekly Field Log", level=1)
    title.runs[0].font.color.rgb = RGBColor(0x00,0x63,0x41)
    doc.add_paragraph("Saniya · Intern · TraceLink").runs[0].italic = True
    doc.add_paragraph(f"Week of {fmt_date(ws)}").runs[0].bold = True
    dates = sorted([d for d in entries if week_start(d) == ws])
    doc.add_paragraph(f"Total hours logged: {sum(float(entries[d].get('hours') or 0) for d in dates):g}")
    table = doc.add_table(rows=1, cols=5)
    table.style = "Light Grid Accent 1"
    for i,h in enumerate(["Date","Tasks completed","Goals for next day","Hrs","Status"]): table.rows[0].cells[i].text=h
    for d in dates:
        e=entries[d]; row=table.add_row().cells
        row[0].text=f"{fmt_date(d)} ({day_name(d)})"
        row[1].text=tasks_text(e.get('tasks')) or "—"
        row[2].text=e.get('goals') or "—"
        row[3].text=str(e.get('hours') or 0)
        row[4].text=(e.get('status') or 'on-track').replace('-',' ').title()
    notes=[n for n in load_notes() if n.get('week_start')==ws]
    if notes:
        doc.add_heading("Manager notes",level=2)
        for n in notes: doc.add_paragraph(f"{n.get('author','Manager')} ({n.get('ts','')}): {n.get('text','')}")
    bio=BytesIO(); doc.save(bio); bio.seek(0); return bio


def build_xlsx(entries, notes):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook()
    ws = wb.active
    ws.title = "Daily Log"
    headers = ["Date", "Day", "Tasks completed", "Goals for next day", "Hours", "Status", "Notes / blockers", "Key learning", "Idea", "Reflection"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="006341")
    for iso in sorted(entries):
        e = entries[iso]
        ws.append([iso, day_name(iso), tasks_text(e.get("tasks")), e.get("goals", ""), e.get("hours", 0), (e.get("status") or "on-track").replace("-", " ").title(), e.get("notes", ""), e.get("learning", ""), e.get("idea", ""), e.get("reflection", "")])
    widths = [14, 12, 55, 40, 10, 16, 40, 40, 40, 50]
    for i,w in enumerate(widths,1): ws.column_dimensions[chr(64+i)].width = w
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    wn = wb.create_sheet("Manager Notes")
    wn.append(["Week of", "Author", "Timestamp", "Note"])
    for cell in wn[1]:
        cell.font = Font(bold=True, color="006341")
        cell.fill = PatternFill("solid", fgColor="ECE81A")
    for n in notes:
        wn.append([n.get("week_start", ""), n.get("author", "Manager"), n.get("ts", ""), n.get("text", "")])
    for col,w in zip("ABCD", [14,22,20,80]): wn.column_dimensions[col].width=w
    for row in wn.iter_rows():
        for cell in row: cell.alignment = Alignment(vertical="top", wrap_text=True)
    bio = BytesIO(); wb.save(bio); bio.seek(0); return bio


def render_downloads(entries, notes):
    st.subheader("Downloads")
    xlsx = build_xlsx(entries, notes)
    st.download_button("⬇ Download full spreadsheet", data=xlsx, file_name="Field_Log_Full.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="xlsx_full")
    weeks=sorted({week_start(d) for d in entries}, reverse=True)
    for ws in weeks:
        bio=build_word(entries,ws)
        st.download_button(f"⬇ Word report — week of {fmt_date(ws)}", data=bio, file_name=f"Field_Log_Week_{ws}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"word_{ws}")


def main():
    st.set_page_config(page_title="Field Log — Saniya", page_icon="FL", layout="wide", initial_sidebar_state="collapsed")
    inject_css()
    entries = load_entries()
    notes = load_notes()
    manager_mode = st.query_params.get("view", "") == "manager"
    if manager_mode:
        render_manager(entries, notes)
        return
    render_header(manager=False)
    render_stats(entries)
    with st.expander("Downloads"):
        render_downloads(entries, notes)
    st.caption("Tip: share the Manager View link with your manager. Because this is hosted online, it works across different Wi-Fi/VPN networks.")
    tabs = st.tabs(["Today's Entry", "Ops Log", "Journal", "Manager View", "Feedback"])
    with tabs[0]: render_entry(entries)
    with tabs[1]: render_ops_log(entries)
    with tabs[2]: render_journal(entries)
    with tabs[3]:
        st.subheader("Manager View")
        st.markdown("Your manager can use the direct read-only URL: `?view=manager`")
        st.code(f"{st.context.headers.get('Host','YOUR-APP.streamlit.app')}/?view=manager", language="text")
        render_manager(entries, notes)
    with tabs[4]: render_feedback(notes)

if __name__ == "__main__":
    main()
