"""
Batch Run Registry
Full feature parity with browser widget:
  - Auto-generated run ID shown read-only
  - Date pickers for start/end, auto-calculated duration
  - RQ + Yxs KPI fields
  - Edit / Duplicate / Mark achieved per run
  - Outcome pill + flag colour in run cards
  - Tag chips, styled prose blocks
  - Per-project success rate table in analytics
  - Coloured timeline dots with objective preview
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from modules import session

# ── Helpers ───────────────────────────────────────────────────────────────────

def _ts():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def _fmt(v, dec=3):
    if v in (None, "", 0):
        return ""
    try:
        return f"{float(v):.{dec}f}"
    except (TypeError, ValueError):
        return str(v)

def _safe_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def _calc_duration(start_str, end_str):
    """Return duration in hours as string, or empty string."""
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            s = datetime.strptime(start_str.strip(), fmt)
            e = datetime.strptime(end_str.strip(), fmt)
            hours = (e - s).total_seconds() / 3600
            return f"{hours:.1f}" if hours >= 0 else ""
        except (ValueError, AttributeError):
            continue
    return ""

# ── Outcome & flag metadata ───────────────────────────────────────────────────

OUTCOME_META = {
    "Fully achieved":    ("🟢", "#d4edda", "#155724"),
    "Partially achieved":("🟡", "#fff3cd", "#856404"),
    "Not achieved":      ("🔴", "#f8d7da", "#721c24"),
    "Ongoing":           ("🔵", "#cce5ff", "#004085"),
    "":                  ("⚪", "#f8f9fa", "#6c757d"),
}

FLAG_COLORS = {
    "Normal":          "#6c757d",
    "Important":       "#856404",
    "Needs review":    "#004085",
    "Repeat required": "#721c24",
    "Reference run":   "#4a1e6e",
}

# ── Main render ───────────────────────────────────────────────────────────────

def render():
    st.title("📋 Batch Run Registry")
    st.caption("Log every fermentation run · project · client · objectives · outcomes · KPIs")

    tab_new, tab_all, tab_saved, tab_analytics, tab_timeline = st.tabs(
        ["📝 New run", "📂 All runs", "💾 Saved runs", "📊 Analytics", "📅 Timeline"]
    )

    with tab_new:
        _new_run_form()
    with tab_all:
        _all_runs()
    with tab_saved:
        _saved_runs()
    with tab_analytics:
        _analytics()
    with tab_timeline:
        _timeline()


def _saved_runs():
    """Load runs persisted by DataManager."""
    from data_manager import DataManager, render_run_selector
    dm = st.session_state.get("data_manager")
    if dm is None:
        dm = DataManager()
        st.session_state.data_manager = dm

    run_data = render_run_selector(dm)
    if run_data and "data" in run_data:
        st.subheader("Data preview")
        st.dataframe(run_data["data"].head(20), use_container_width=True)

        if "kinetics" in run_data:
            st.subheader("Kinetics results")
            k = run_data["kinetics"].get("kinetics", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("μ_max", f"{k.get('mu_max', 0):.3f} h⁻¹" if k.get("mu_max") else "—")
            c2.metric("Titer", f"{k.get('titer', 0):.3f} g/L" if k.get("titer") else "—")
            c3.metric("STY",   f"{k.get('sty', 0):.4f} g/L/h" if k.get("sty") else "—")

        # Load into active session
        if st.button("📂 Load into active session", type="primary"):
            from views.data_import import auto_detect_mapping
            df = run_data["data"]
            label = run_data.get("run_id", "loaded_run")
            existing = st.session_state.get("uploaded_runs", {})
            existing[label] = {"df": df, "filename": run_data.get("original_filename", f"{label}.csv")}
            st.session_state.uploaded_runs = existing
            st.session_state.active_run = label
            st.session_state.run_data = df
            st.session_state.run_name = label
            st.session_state.col_map = auto_detect_mapping(df.columns.tolist())
            st.success(f"✅ Loaded **{label}** into active session. Switch to **Analysis** to view.")

        # Export
        if st.button("📥 Export as Excel"):
            export_path = dm.export_run(run_data["run_id"], "excel")
            if export_path:
                with open(export_path, "rb") as f:
                    st.download_button(
                        "Download Excel",
                        data=f,
                        file_name=f"{run_data['run_id']}_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )


# ── New / edit run form ───────────────────────────────────────────────────────

def _new_run_form():
    reg = st.session_state.run_registry

    # If editing an existing run, pre-load it
    edit_key = st.session_state.get("_registry_edit_id")
    editing  = None
    if edit_key:
        editing = next((r for r in reg if r.get("id") == edit_key), None)

    # Auto-generate new run ID (or reuse if editing)
    if editing:
        run_id = editing["id"]
        st.info(f"✏️ Editing existing run: **{run_id}**")
    else:
        run_id = f"RUN-{_ts()}-{len(reg)+1:03d}"

    def _v(field, default=""):
        """Get value from editing record or default."""
        return editing.get(field, default) if editing else default

    with st.form("run_form", clear_on_submit=False):

        # ── Run identity ──────────────────────────────────────────────────────
        st.subheader("🔖 Run identity")
        st.text_input("Run ID (auto-generated)", value=run_id, disabled=True,
                      help="Unique identifier stamped with date and sequence number")

        c1, c2, c3, c4 = st.columns(4)
        r_name   = c1.text_input("Run name / label *",
                                  value=_v("name", st.session_state.run_name or ""),
                                  placeholder="e.g. EColi-MVA-R07")
        r_type   = c2.selectbox("Run type",
                                 ["Development", "Optimisation", "Scale-up validation",
                                  "Client demonstration", "Production batch",
                                  "Feasibility study", "Troubleshooting"],
                                 index=["Development","Optimisation","Scale-up validation",
                                        "Client demonstration","Production batch",
                                        "Feasibility study","Troubleshooting"].index(
                                     _v("type","Development")) if _v("type") in
                                 ["Development","Optimisation","Scale-up validation",
                                  "Client demonstration","Production batch",
                                  "Feasibility study","Troubleshooting"] else 0)
        r_status = c3.selectbox("Status",
                                 ["Completed", "Running", "Planned", "Failed / aborted", "On hold"],
                                 index=["Completed","Running","Planned",
                                        "Failed / aborted","On hold"].index(
                                     _v("status","Completed")) if _v("status") in
                                 ["Completed","Running","Planned","Failed / aborted","On hold"] else 0)
        r_op     = c4.text_input("Operator / scientist",
                                  value=_v("operator", st.session_state.get("run_operator","")),
                                  placeholder="Name or initials")

        # ── Timing ────────────────────────────────────────────────────────────
        st.subheader("⏱ Timing")
        c1, c2, c3, c4 = st.columns(4)

        r_start = c1.text_input("Start (YYYY-MM-DD HH:MM)",
                                 value=_v("start"),
                                 placeholder="2024-03-15 09:00")
        r_end   = c2.text_input("End   (YYYY-MM-DD HH:MM)",
                                 value=_v("end"),
                                 placeholder="2024-03-16 09:00")
        r_dur_p = c3.text_input("Planned duration (h)",
                                 value=_v("dur_planned"),
                                 placeholder="24")

        # Auto-calculate actual duration
        dur_actual = _calc_duration(r_start, r_end)
        if not dur_actual and _v("duration"):
            dur_actual = _v("duration")
        c4.text_input("Actual duration (h)", value=dur_actual, disabled=True,
                      help="Auto-calculated from start and end times")

        # ── Project & client ──────────────────────────────────────────────────
        st.subheader("🏢 Project & client context")
        c1, c2, c3 = st.columns(3)
        r_proj   = c1.text_input("Project name",
                                  value=_v("project", st.session_state.get("run_project","")),
                                  placeholder="e.g. MVA Scale-up Phase 2")
        r_pcode  = c2.text_input("Project code / ID",
                                  value=_v("proj_code"),
                                  placeholder="PRJ-2024-07")
        r_prog   = c3.text_input("Programme / portfolio",
                                  value=_v("programme"),
                                  placeholder="e.g. Industrial biotech, Pharma APIs")

        c1, c2, c3 = st.columns(3)
        r_client  = c1.text_input("Target client / customer",
                                   value=_v("client"),
                                   placeholder="e.g. internal, partner company")
        r_contact = c2.text_input("Client contact",
                                   value=_v("client_contact"),
                                   placeholder="Name or email")
        r_stage   = c3.selectbox("Commercial stage",
                                  ["Internal R&D", "Proof of concept", "Client sample / demo",
                                   "Tech transfer", "Commercial supply", "Regulatory / GMP"],
                                  index=["Internal R&D","Proof of concept","Client sample / demo",
                                         "Tech transfer","Commercial supply","Regulatory / GMP"].index(
                                      _v("stage","Internal R&D")) if _v("stage") in
                                  ["Internal R&D","Proof of concept","Client sample / demo",
                                   "Tech transfer","Commercial supply","Regulatory / GMP"] else 0)

        # ── Objective & outcome ───────────────────────────────────────────────
        st.subheader("🎯 Objective & outcome")
        c1, c2 = st.columns(2)

        r_obj  = c1.text_area("Purpose / objective *",
                               value=_v("objective", st.session_state.get("run_objective","")),
                               height=95,
                               placeholder="e.g. Optimise fed-batch feeding strategy to increase MVA "
                                           "titer from 2.5 → >4 g/L. Evaluate pH 7.0 vs 6.8.")
        r_hyp  = c1.text_area("Hypothesis / expected outcome",
                               value=_v("hypothesis"),
                               height=75,
                               placeholder="e.g. Lower pH should suppress acetate overflow "
                                           "based on Run R05 data.")
        r_out  = c2.text_area("Outcome / result summary",
                               value=_v("outcome"),
                               height=95,
                               placeholder="e.g. Titer reached 3.8 g/L — below target. "
                                           "pH 6.8 reduced acetate by 40% but also reduced growth rate.")
        r_ach  = c2.selectbox("Was the objective achieved?",
                               ["Ongoing / not yet evaluated", "✓ Fully achieved",
                                "~ Partially achieved", "✗ Not achieved"],
                               index=["Ongoing / not yet evaluated","✓ Fully achieved",
                                      "~ Partially achieved","✗ Not achieved"].index(
                                   _v("achieved","Ongoing / not yet evaluated")) if _v("achieved") in
                               ["Ongoing / not yet evaluated","✓ Fully achieved",
                                "~ Partially achieved","✗ Not achieved"] else 0)
        r_next = c2.text_area("Next steps / follow-on actions",
                               value=_v("next_steps"),
                               height=75,
                               placeholder="e.g. Run R08: increase glucose feed rate by 20%.")

        # ── Bioprocess KPIs ───────────────────────────────────────────────────
        st.subheader("📈 Bioprocess KPIs")
        st.caption("Auto-filled from analyser — edit if needed")

        c1, c2, c3, c4 = st.columns(4)
        r_titer = c1.text_input("Titer (g/L)",
                                 value=_v("titer", _fmt(st.session_state.get("titer"))))
        r_sty   = c2.text_input("STY (g/L/h)",
                                 value=_v("sty", _fmt(st.session_state.get("sty"), 4)))
        r_yps   = c3.text_input("Yps (g product/g substrate)",
                                 value=_v("yps", _fmt(st.session_state.get("yps"), 4)))
        r_mu    = c4.text_input("μ max (h⁻¹)",
                                 value=_v("mu", _fmt(st.session_state.get("mu"), 3)))

        c1, c2, c3, c4 = st.columns(4)
        r_yxs   = c1.text_input("Yxs (g biomass/g substrate)",
                                 value=_v("yxs", _fmt(st.session_state.get("yxs"), 4)))
        r_rq    = c2.text_input("RQ (respiratory quotient)",
                                 value=_v("rq", _fmt(st.session_state.get("rq"), 3)))
        r_cbal  = c3.text_input("C balance closure (%)",
                                 value=_v("c_bal", _fmt(st.session_state.get("c_closure"), 1)))
        r_od    = c4.text_input("Max OD₆₀₀",
                                 value=_v("max_od"),
                                 placeholder="e.g. 7.4")

        c1, c2, c3 = st.columns(3)
        r_prod   = c1.text_input("Product",
                                  value=_v("product",
                                           st.session_state.products[0]
                                           if st.session_state.products else ""))
        r_strain = c2.text_input("Organism / strain",
                                  value=_v("strain",
                                           st.session_state.active_strain.get("name", "")
                                           if st.session_state.active_strain else ""))
        r_vol    = c3.text_input("Reactor volume (L)",
                                  value=_v("vol"), placeholder="e.g. 1.0")

        c1, c2, c3 = st.columns(3)
        r_med   = c1.text_input("Medium",
                                 value=_v("medium"), placeholder="M9 minimal glucose")
        r_pass  = c2.text_input("Passage # from stock",
                                 value=_v("passage"), placeholder="e.g. 2")
        r_mode  = c3.text_input("Process mode",
                                 value=_v("process_mode", st.session_state.run_mode))

        # ── Tags & notes ──────────────────────────────────────────────────────
        st.subheader("🏷 Tags & notes")
        c1, c2 = st.columns(2)
        r_tags = c1.text_input("Tags (comma-separated keywords)",
                                value=_v("tags"),
                                placeholder="fed-batch, pH-study, MVA, client-demo, scale-up")
        r_flag = c2.selectbox("Priority / flag",
                               ["Normal", "Important", "Needs review",
                                "Repeat required", "Reference run"],
                               index=["Normal","Important","Needs review",
                                      "Repeat required","Reference run"].index(
                                   _v("flag","Normal")) if _v("flag") in
                               ["Normal","Important","Needs review",
                                "Repeat required","Reference run"] else 0)
        r_notes = st.text_area("General notes / observations",
                                value=_v("notes"),
                                height=80,
                                placeholder="Free text — equipment issues, unexpected observations, "
                                            "deviations from SOP, sample timestamps…")
        r_docs  = st.text_input("Linked documents / ELN entries",
                                 value=_v("docs"),
                                 placeholder="e.g. ELN-2024-0315, Lab notebook p.42, SOP-FER-007-v2")

        # ── Submit ────────────────────────────────────────────────────────────
        c1, c2 = st.columns([2, 1])
        submitted = c1.form_submit_button(
            "💾 Save run record" if not editing else "💾 Update run record",
            type="primary", use_container_width=True
        )
        cleared = c2.form_submit_button("🗑 Clear form", use_container_width=True)

        if cleared:
            st.session_state["_registry_edit_id"] = None
            st.rerun()

        if submitted:
            if not r_name.strip():
                st.error("Run name is required before saving.")
                return

            # Normalise achieved value
            ach_map = {
                "✓ Fully achieved":           "Fully achieved",
                "~ Partially achieved":        "Partially achieved",
                "✗ Not achieved":              "Not achieved",
                "Ongoing / not yet evaluated": "Ongoing",
            }
            ach_clean = ach_map.get(r_ach, r_ach)

            rec = {
                "id":           run_id,
                "name":         r_name.strip(),
                "type":         r_type,
                "status":       r_status,
                "operator":     r_op,
                "start":        r_start,
                "end":          r_end,
                "duration":     dur_actual,
                "dur_planned":  r_dur_p,
                "project":      r_proj,
                "proj_code":    r_pcode,
                "programme":    r_prog,
                "client":       r_client,
                "client_contact": r_contact,
                "stage":        r_stage,
                "objective":    r_obj,
                "hypothesis":   r_hyp,
                "outcome":      r_out,
                "achieved":     ach_clean,
                "next_steps":   r_next,
                "titer":        r_titer,
                "sty":          r_sty,
                "yps":          r_yps,
                "mu":           r_mu,
                "yxs":          r_yxs,
                "rq":           r_rq,
                "c_bal":        r_cbal,
                "max_od":       r_od,
                "product":      r_prod,
                "strain":       r_strain,
                "vol":          r_vol,
                "medium":       r_med,
                "passage":      r_pass,
                "process_mode": r_mode,
                "tags":         r_tags,
                "flag":         r_flag,
                "notes":        r_notes,
                "docs":         r_docs,
                "saved_at":     datetime.now().isoformat(),
            }

            existing = next((i for i, r in enumerate(reg) if r.get("id") == run_id), -1)
            if existing >= 0:
                reg[existing] = rec
            else:
                reg.append(rec)

            session.save_registry()
            st.session_state["_registry_edit_id"] = None
            st.success(f"✅ Run **{r_name}** saved — {run_id}")


# ── All runs view ─────────────────────────────────────────────────────────────

def _all_runs():
    reg = st.session_state.run_registry
    if not reg:
        st.info("No runs saved yet. Use **New run** to add one.")
        return

    # ── Toolbar ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
    q      = c1.text_input("🔍 Search", placeholder="name, project, client, tags, product…",
                            label_visibility="collapsed")
    f_ach  = c2.selectbox("Outcome",
                           ["All", "Fully achieved", "Partially achieved", "Not achieved", "Ongoing"],
                           label_visibility="collapsed")
    f_type = c3.selectbox("Type",
                           ["All", "Development", "Optimisation", "Scale-up validation",
                            "Client demonstration", "Production batch", "Feasibility study"],
                           label_visibility="collapsed")
    projects = sorted(set(r.get("project", "") for r in reg if r.get("project", "")))
    f_proj = c4.selectbox("Project", ["All"] + projects, label_visibility="collapsed")

    def _matches(r):
        searchable = " ".join([
            r.get("name",""), r.get("project",""), r.get("client",""),
            r.get("tags",""), r.get("product",""), r.get("objective",""),
            r.get("strain",""), r.get("operator",""),
        ]).lower()
        return (
            (not q or q.lower() in searchable) and
            (f_ach == "All"  or r.get("achieved","") == f_ach) and
            (f_type == "All" or r.get("type","")     == f_type) and
            (f_proj == "All" or r.get("project","")  == f_proj)
        )

    filtered = sorted(
        [r for r in reg if _matches(r)],
        key=lambda r: r.get("saved_at", ""), reverse=True
    )

    c5_inner = c5.container()
    st.caption(f"Showing **{len(filtered)}** of {len(reg)} runs")

    # Export CSV
    if c5_inner.button("📥 CSV", help="Export filtered runs"):
        df_exp = pd.DataFrame(filtered)
        st.download_button("⬇ Download CSV", df_exp.to_csv(index=False),
                           "run_registry.csv", "text/csv", key="dl_csv")

    # ── Run cards ─────────────────────────────────────────────────────────────
    for r in filtered:
        _run_card(r, reg)


def _run_card(r, reg):
    ach = r.get("achieved", "")
    em, bg, fg = OUTCOME_META.get(ach, OUTCOME_META[""])
    flag = r.get("flag", "Normal")
    flag_color = FLAG_COLORS.get(flag, FLAG_COLORS["Normal"])

    # Tags as inline text list
    tags_raw = r.get("tags", "")
    tag_list = [t.strip() for t in tags_raw.split(",") if t.strip()]

    # Header line shown in expander label
    dur_str  = f"{r.get('duration','—')}h" if r.get("duration") else "—"
    date_str = r.get("start","")[:10] if r.get("start") else "—"
    titer_str = f" · {r.get('product','—')} {r.get('titer','—')} g/L" if r.get("titer") else ""

    label = (
        f"{em}  **{r.get('name','Unnamed')}**"
        f"{'  🚩 '+flag if flag != 'Normal' else ''}"
        f"  ·  {r.get('project','—')}"
        f"  ·  {date_str}  ({dur_str})"
        f"{titer_str}"
    )

    with st.expander(label):
        # ── Summary row ───────────────────────────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f"**ID**  \n`{r.get('id','—')}`")
        c2.markdown(f"**Type**  \n{r.get('type','—')}")
        c3.markdown(f"**Operator**  \n{r.get('operator','—')}")
        c4.markdown(f"**Status**  \n{r.get('status','—')}")
        c5.markdown(
            f"<span style='background:{bg};color:{fg};padding:3px 10px;"
            f"border-radius:12px;font-size:12px;font-weight:600'>{em} {ach or '—'}</span>",
            unsafe_allow_html=True
        )

        st.markdown("---")

        # ── Two-column detail ─────────────────────────────────────────────────
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("**Timing**")
            st.markdown(
                f"Start: `{r.get('start','—')}`  \n"
                f"End:   `{r.get('end','—')}`  \n"
                f"Duration: **{r.get('duration','—')} h** "
                f"(planned: {r.get('dur_planned','—')} h)"
            )
            st.markdown("**Project & client**")
            st.markdown(
                f"{r.get('project','—')} `{r.get('proj_code','')}` · "
                f"{r.get('programme','—')}  \n"
                f"Client: **{r.get('client','—')}** · {r.get('client_contact','—')}  \n"
                f"Stage: {r.get('stage','—')}"
            )

        with col_r:
            st.markdown("**Bioprocess KPIs**")
            kpi_parts = []
            if r.get("titer"):  kpi_parts.append(f"Titer **{r['titer']} g/L**")
            if r.get("sty"):    kpi_parts.append(f"STY {r['sty']} g/L/h")
            if r.get("yps"):    kpi_parts.append(f"Yps {r['yps']}")
            if r.get("yxs"):    kpi_parts.append(f"Yxs {r['yxs']}")
            if r.get("mu"):     kpi_parts.append(f"μ {r['mu']} h⁻¹")
            if r.get("rq"):     kpi_parts.append(f"RQ {r['rq']}")
            if r.get("c_bal"):  kpi_parts.append(f"C closure {r['c_bal']}%")
            if r.get("max_od"): kpi_parts.append(f"Max OD {r['max_od']}")
            st.markdown("  ·  ".join(kpi_parts) if kpi_parts else "—")

            st.markdown("**Strain / medium / volume**")
            st.markdown(
                f"{r.get('strain','—')} · {r.get('medium','—')} · "
                f"{r.get('vol','—')} L · Passage {r.get('passage','—')}"
            )
            if r.get("docs"):
                st.markdown(f"**Linked docs:** {r['docs']}")

        # ── Objective / outcome / next steps prose ────────────────────────────
        if r.get("objective"):
            st.markdown("**Objective**")
            st.info(r["objective"])
        if r.get("hypothesis"):
            st.markdown("**Hypothesis**")
            st.markdown(f"> {r['hypothesis']}")
        if r.get("outcome"):
            _, bg_o, fg_o = OUTCOME_META.get(ach, OUTCOME_META[""])
            st.markdown("**Outcome**")
            st.markdown(
                f"<div style='border-left:4px solid {fg_o};background:{bg_o};"
                f"padding:8px 12px;border-radius:4px;color:{fg_o};font-size:13px'>"
                f"{r['outcome']}</div>",
                unsafe_allow_html=True
            )
        if r.get("next_steps"):
            st.markdown("**Next steps**")
            st.markdown(f"> {r['next_steps']}")
        if r.get("notes"):
            with st.expander("📓 Notes"):
                st.markdown(r["notes"])

        # ── Tags ──────────────────────────────────────────────────────────────
        if tag_list:
            chips = " ".join(
                f"`{t}`" for t in tag_list
            )
            st.markdown(f"**Tags:** {chips}")

        # ── Action buttons ────────────────────────────────────────────────────
        st.markdown("---")
        b1, b2, b3, b4, b5 = st.columns(5)

        if b1.button("✏️ Edit", key=f"edit_{r['id']}", use_container_width=True):
            st.session_state["_registry_edit_id"] = r["id"]
            st.rerun()

        if b2.button("📋 Duplicate", key=f"dup_{r['id']}", use_container_width=True):
            new_rec = dict(r)
            new_rec["id"]       = f"RUN-{_ts()}-{len(reg)+1:03d}"
            new_rec["name"]     = r.get("name", "") + " (copy)"
            new_rec["achieved"] = "Ongoing"
            new_rec["saved_at"] = datetime.now().isoformat()
            st.session_state.run_registry.append(new_rec)
            session.save_registry()
            st.success(f"Duplicated as **{new_rec['name']}**")
            st.rerun()

        if b3.button("✅ Mark achieved", key=f"ach_{r['id']}", use_container_width=True):
            r["achieved"] = "Fully achieved"
            session.save_registry()
            st.rerun()

        if b4.button("⭐ Set golden batch", key=f"gold_{r['id']}", use_container_width=True):
            st.session_state.golden_batch = {
                "name":    r.get("name",""),
                "mu":      _safe_float(r.get("mu")),
                "titer":   _safe_float(r.get("titer")),
                "sty":     _safe_float(r.get("sty")),
                "yps":     _safe_float(r.get("yps")),
                "yxs":     _safe_float(r.get("yxs", 0.45)),
                "closure": _safe_float(r.get("c_bal", 97)),
                "rq":      _safe_float(r.get("rq", 1.0)),
                "notes":   r.get("notes", ""),
            }
            st.session_state.golden_batch_name = r.get("name","")
            st.success(f"⭐ Golden batch set to **{r.get('name','')}**")

        if b5.button("🗑 Delete", key=f"del_{r['id']}", use_container_width=True):
            st.session_state.run_registry = [
                x for x in st.session_state.run_registry if x.get("id") != r.get("id")
            ]
            session.save_registry()
            st.rerun()


# ── Analytics ─────────────────────────────────────────────────────────────────

def _analytics():
    reg = st.session_state.run_registry
    if not reg:
        st.info("No runs saved yet.")
        return

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    total   = len(reg)
    achieved= sum(1 for r in reg if r.get("achieved") == "Fully achieved")
    partial = sum(1 for r in reg if r.get("achieved") == "Partially achieved")
    ongoing = sum(1 for r in reg if r.get("achieved") == "Ongoing")
    failed  = sum(1 for r in reg if r.get("achieved") == "Not achieved")
    projects= len(set(r.get("project","") for r in reg if r.get("project","")))
    clients = len(set(r.get("client","")  for r in reg if r.get("client","")))
    titers  = [_safe_float(r["titer"]) for r in reg if r.get("titer","") not in ("","—")]
    avg_t   = sum(titers)/len(titers) if titers else 0
    max_t   = max(titers) if titers else 0
    success_rate = f"{achieved/total*100:.0f}%" if total else "—"

    # ── KPI metrics ───────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("Total runs",      total)
    c2.metric("Success rate",    success_rate)
    c3.metric("✅ Achieved",      achieved)
    c4.metric("~ Partial",       partial)
    c5.metric("Projects",        projects)
    c6.metric("Avg titer (g/L)", f"{avg_t:.2f}" if avg_t else "—")
    c7.metric("Best titer (g/L)",f"{max_t:.2f}" if max_t else "—")

    # ── Outcome + type charts ─────────────────────────────────────────────────
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Outcome breakdown", "Run type breakdown"),
        specs=[[{"type":"pie"}, {"type":"bar"}]]
    )
    oc = {}
    for r in reg:
        k = r.get("achieved","") or "Unknown"
        oc[k] = oc.get(k,0) + 1
    OC_COLORS = {
        "Fully achieved":"#28a745","Partially achieved":"#ffc107",
        "Not achieved":"#dc3545","Ongoing":"#007bff","Unknown":"#6c757d",
    }
    fig.add_trace(go.Pie(
        labels=list(oc.keys()), values=list(oc.values()),
        hole=0.45,
        marker_colors=[OC_COLORS.get(k,"#aaa") for k in oc.keys()],
        textinfo="label+percent", showlegend=False,
    ), row=1, col=1)

    tc = {}
    for r in reg:
        k = r.get("type","Unknown") or "Unknown"
        tc[k] = tc.get(k,0) + 1
    tc_sorted = dict(sorted(tc.items(), key=lambda x: x[1], reverse=True))
    fig.add_trace(go.Bar(
        x=list(tc_sorted.keys()), y=list(tc_sorted.values()),
        marker_color="#1f77b4", showlegend=False,
    ), row=1, col=2)
    fig.update_layout(height=320, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # ── Titer trend ───────────────────────────────────────────────────────────
    titered = [
        (r.get("start",""), r.get("name",""), _safe_float(r["titer"]), r.get("achieved",""))
        for r in reg if r.get("titer","") not in ("","—")
    ]
    titered.sort(key=lambda x: x[0])
    if len(titered) >= 2:
        st.subheader("Titer trend across runs")
        COLOR_MAP = {
            "Fully achieved":"#28a745","Partially achieved":"#ffc107",
            "Not achieved":"#dc3545","Ongoing":"#007bff","":"#6c757d",
        }
        fig3 = go.Figure()
        names  = [x[1] for x in titered]
        titers_v = [x[2] for x in titers] if False else [x[2] for x in titered]
        colors_v = [COLOR_MAP.get(x[3],"#6c757d") for x in titered]
        fig3.add_trace(go.Scatter(
            x=list(range(len(names))), y=titers_v, mode="lines",
            line=dict(color="#dee2e6", width=1), showlegend=False,
        ))
        fig3.add_trace(go.Scatter(
            x=list(range(len(names))), y=titers_v, mode="markers+text",
            text=names, textposition="top center",
            textfont=dict(size=9),
            marker=dict(color=colors_v, size=11, line=dict(width=1, color="white")),
            showlegend=False,
        ))
        fig3.update_layout(
            height=280, margin=dict(t=30, b=20),
            xaxis=dict(tickvals=list(range(len(names))), ticktext=names,
                       tickangle=-30, tickfont=dict(size=9)),
            yaxis_title="Titer (g/L)",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Per-project success rate table ────────────────────────────────────────
    st.subheader("Performance by project")
    proj_stats = {}
    for r in reg:
        p = r.get("project","") or "(no project)"
        if p not in proj_stats:
            proj_stats[p] = {"runs":0,"achieved":0,"partial":0,"titers":[]}
        proj_stats[p]["runs"] += 1
        if r.get("achieved") == "Fully achieved":
            proj_stats[p]["achieved"] += 1
        elif r.get("achieved") == "Partially achieved":
            proj_stats[p]["partial"] += 1
        t = r.get("titer","")
        if t not in ("","—"):
            try: proj_stats[p]["titers"].append(float(t))
            except: pass

    proj_rows = []
    for p, d in sorted(proj_stats.items(), key=lambda x: x[1]["runs"], reverse=True):
        rate = d["achieved"]/d["runs"]*100
        avg_tit = sum(d["titers"])/len(d["titers"]) if d["titers"] else None
        proj_rows.append({
            "Project":         p,
            "Runs":            d["runs"],
            "Achieved":        d["achieved"],
            "Partial":         d["partial"],
            "Success rate":    f"{rate:.0f}%",
            "Avg titer (g/L)": f"{avg_tit:.2f}" if avg_tit else "—",
            "Rating":          "🟢" if rate >= 70 else ("🟡" if rate >= 40 else "🔴"),
        })
    if proj_rows:
        st.dataframe(pd.DataFrame(proj_rows), hide_index=True, use_container_width=True)


# ── Timeline ──────────────────────────────────────────────────────────────────

def _timeline():
    reg = st.session_state.run_registry
    if not reg:
        st.info("No runs saved yet.")
        return

    sorted_reg = sorted(
        [r for r in reg if r.get("start","")],
        key=lambda r: r.get("start",""), reverse=True
    )
    if not sorted_reg:
        st.info("No runs with start dates yet.")
        return

    DOT = {
        "Fully achieved":    "🟢",
        "Partially achieved":"🟡",
        "Not achieved":      "🔴",
        "Ongoing":           "🔵",
        "":                  "⚪",
    }
    TYPE_COLORS = {
        "Development":"#6610f2","Optimisation":"#0069d9","Scale-up validation":"#117a8b",
        "Client demonstration":"#1e7e34","Production batch":"#b21f2d",
        "Feasibility study":"#e67e22","Troubleshooting":"#7f8c8d",
    }

    for r in sorted_reg:
        dot   = DOT.get(r.get("achieved",""),"⚪")
        date_str = r.get("start","")[:10] if r.get("start") else "—"
        dur   = f"{r.get('duration','—')}h" if r.get("duration") else ""
        tc    = TYPE_COLORS.get(r.get("type",""),"#6c757d")
        tags  = [t.strip() for t in r.get("tags","").split(",") if t.strip()]

        # Timeline entry
        col_dot, col_body = st.columns([0.05, 0.95])
        with col_dot:
            st.markdown(f"## {dot}")
        with col_body:
            st.markdown(
                f"**{date_str}** {f'· {dur}' if dur else ''}  \n"
                f"<span style='font-size:15px;font-weight:600'>{r.get('name','—')}</span>  "
                f"<span style='background:{tc}20;color:{tc};padding:2px 8px;"
                f"border-radius:10px;font-size:11px;font-weight:500'>"
                f"{r.get('type','—')}</span>",
                unsafe_allow_html=True
            )
            meta_parts = []
            if r.get("project"): meta_parts.append(f"📁 {r['project']}")
            if r.get("client"):  meta_parts.append(f"👤 {r['client']}")
            if r.get("product") and r.get("titer"):
                meta_parts.append(f"🧪 {r['product']} {r['titer']} g/L")
            if meta_parts:
                st.caption("  ·  ".join(meta_parts))
            if r.get("objective"):
                preview = r["objective"][:120] + ("…" if len(r["objective"]) > 120 else "")
                st.caption(f"*{preview}*")
            if tags:
                st.markdown(" ".join(f"`{t}`" for t in tags[:6]))

        st.markdown("---")
