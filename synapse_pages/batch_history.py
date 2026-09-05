"""Batch History — Create batches, log measurements, view records & trend charts."""
import streamlit as st
import pandas as pd

# ── Organism options ─────────────────────────────────────────────────────────
ORGANISMS = [
    "CHO", "CHO-S", "HEK293", "E. coli",
    "Pichia pastoris", "S. cerevisiae", "NS0", "Sp2/0", "BHK-21",
]

# ── Parameter catalogue: display name → (db_name, default_unit) ─────────────
PARAMETER_CATALOGUE = {
    "pH":          ("pH",          ""),
    "DO":          ("DO",          "%"),
    "Glucose":     ("glucose",     "g/L"),
    "Lactate":     ("lactate",     "g/L"),
    "Ammonia":     ("ammonia",     "mM"),
    "VCD":         ("VCD",         "x10^6 cells/mL"),
    "Viability":   ("viability",   "%"),
    "Titer":       ("titer",       "g/L"),
    "CO2":         ("CO2",         "%"),
    "O2":          ("O2",          "%"),
    "Temperature": ("temperature", "°C"),
    "Agitation":   ("agitation",   "rpm"),
}


def _get_sb():
    """Return the shared Supabase client or None."""
    return st.session_state.get("supabase")


# ── Data helpers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def _fetch_batches(_sb_id):
    """Fetch all batches. _sb_id is only used for cache-busting."""
    sb = _get_sb()
    if sb is None:
        return []
    resp = sb.table("batches").select("*").order("created_at", desc=True).execute()
    return resp.data or []


def _fetch_measurements(batch_id):
    """Fetch measurements for a specific batch."""
    sb = _get_sb()
    if sb is None:
        return []
    resp = (
        sb.table("process_measurements")
        .select("*")
        .eq("batch_id", batch_id)
        .order("day_of_run")
        .execute()
    )
    return resp.data or []


def _invalidate_cache():
    _fetch_batches.clear()


# ── Sidebar: Create New Batch ────────────────────────────────────────────────
def _render_sidebar_create_batch():
    """Sidebar form to create a new batch."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Create New Batch")
    with st.sidebar.form("create_batch_form", clear_on_submit=True):
        batch_code = st.text_input("Batch Code *", placeholder="e.g. BX-2026-042")
        organism = st.selectbox("Organism", ORGANISMS)
        product_type = st.text_input("Product Type", placeholder="e.g. mAb, Vaccine")
        scale = st.number_input("Scale (litres)", min_value=0.0, step=0.1, format="%.1f")
        start_date = st.date_input("Start Date")
        notes = st.text_area("Notes", height=68, placeholder="Optional run notes")
        submitted = st.form_submit_button("Create Batch", type="primary", use_container_width=True)

    if submitted:
        sb = _get_sb()
        if sb is None:
            st.sidebar.error("Supabase not connected.")
            return
        if not batch_code.strip():
            st.sidebar.warning("Batch Code is required.")
            return

        row = {
            "batch_code": batch_code.strip(),
            "organism": organism,
            "product_type": product_type.strip(),
            "scale_liters": scale if scale > 0 else None,
            "start_date": start_date.isoformat(),
            "notes": notes.strip(),
        }
        row = {k: v for k, v in row.items() if v is not None and v != ""}
        try:
            sb.table("batches").insert(row).execute()
            st.sidebar.success(f"Batch **{batch_code}** created.")
            _invalidate_cache()
        except Exception as exc:
            msg = str(exc)
            if "duplicate" in msg.lower() or "unique" in msg.lower():
                st.sidebar.error(f"Batch **{batch_code}** already exists.")
            else:
                st.sidebar.error(f"Failed: {msg}")


# ── Main-area: Batch selector + measurement form + trend chart ───────────────
def _render_batch_selector(batches):
    """Dropdown to pick a batch; returns selected batch dict or None."""
    if not batches:
        st.info("No batches found — create one in the sidebar.")
        return None
    labels = [b["batch_code"] for b in batches]
    idx = st.selectbox("Select Batch", range(len(labels)), format_func=lambda i: labels[i], key="bh_batch_sel")
    return batches[idx]


def _render_log_measurement(batch):
    """Form to log a measurement for the selected batch."""
    st.subheader("Log Process Measurement")
    param_names = list(PARAMETER_CATALOGUE.keys())

    with st.form("log_measurement_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            param_display = st.selectbox("Parameter *", param_names)
            db_name, default_unit = PARAMETER_CATALOGUE[param_display]
            value = st.number_input("Value *", format="%.4f")
            unit = st.text_input("Unit", value=default_unit)
        with col2:
            day_of_run = st.number_input(
                "Day of Run", min_value=0.0, step=0.5, format="%.1f",
                help="Elapsed days since batch start",
            )
            instrument = st.text_input("Instrument", placeholder="e.g. BioProfile FLEX2")

        submitted = st.form_submit_button("Log Measurement", type="primary", use_container_width=True)

    if submitted:
        sb = _get_sb()
        if sb is None:
            st.error("Supabase not connected.")
            return
        row = {
            "batch_id": batch["id"],
            "parameter_name": db_name,
            "value": value,
            "unit": unit.strip() if unit.strip() else None,
            "day_of_run": day_of_run,
            "instrument": instrument.strip() if instrument.strip() else None,
        }
        row = {k: v for k, v in row.items() if v is not None}
        try:
            sb.table("process_measurements").insert(row).execute()
            st.success(f"Logged **{param_display} = {value} {unit}** at day {day_of_run}.")
        except Exception as exc:
            st.error(f"Failed to log measurement: {exc}")


def _render_trend_chart(batch):
    """Line chart of a selected parameter vs day of run for the batch."""
    st.subheader("Trend Chart")
    data = _fetch_measurements(batch["id"])

    if not data:
        st.info("No measurements for this batch yet. Log some above.")
        return

    df = pd.DataFrame(data)
    available = sorted(df["parameter_name"].dropna().unique().tolist())

    if not available:
        st.info("No parameters recorded yet.")
        return

    # Map db names back to display names for the selector
    db_to_display = {v[0]: k for k, v in PARAMETER_CATALOGUE.items()}
    display_options = [db_to_display.get(a, a) for a in available]

    selected_display = st.selectbox("Parameter to chart", display_options, key="trend_param")
    # Resolve back to db name
    selected_db = PARAMETER_CATALOGUE.get(selected_display, (selected_display, ""))[0]

    plot_df = df[df["parameter_name"] == selected_db][["day_of_run", "value"]].dropna()
    plot_df = plot_df.sort_values("day_of_run").reset_index(drop=True)

    if plot_df.empty:
        st.warning(f"No data points for **{selected_display}**.")
        return

    # Build y-axis label with unit
    unit_series = df[df["parameter_name"] == selected_db]["unit"].dropna()
    unit = unit_series.iloc[0] if len(unit_series) > 0 else ""
    y_label = f"{selected_display} ({unit})" if unit else selected_display
    plot_df = plot_df.rename(columns={"day_of_run": "Day of Run", "value": y_label})

    st.line_chart(plot_df, x="Day of Run", y=y_label)
    st.caption(f"{len(plot_df)} data point(s)")


def _render_batches_table(batches):
    """Display all existing batches in a table."""
    st.subheader("All Batches")
    if not batches:
        return

    display_cols = {
        "batch_code": "Batch Code",
        "product_type": "Product Type",
        "organism": "Organism",
        "scale_liters": "Scale (L)",
        "start_date": "Start Date",
        "notes": "Notes",
        "created_at": "Created",
    }
    rows = [{label: b.get(col, "") for col, label in display_cols.items()} for b in batches]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(f"{len(batches)} batch(es)")


# ── Main render ──────────────────────────────────────────────────────────────
def render():
    st.title("Batch History")
    st.caption("Create batches, log process measurements, and analyse trends")

    sb = _get_sb()
    if sb is None:
        st.error(
            "Supabase is not connected. Set `SUPABASE_URL` and `SUPABASE_KEY` "
            "in your `.env` file and restart the app."
        )
        return

    # ── Sidebar: batch creation form ──
    _render_sidebar_create_batch()

    # ── Fetch batches ──
    batches = _fetch_batches(id(sb))

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Batches", len(batches))
    organisms = {b.get("organism", "") for b in batches} - {"", None}
    col2.metric("Organisms", len(organisms) if organisms else "—")
    products = {b.get("product_type", "") for b in batches} - {"", None}
    col3.metric("Product Types", len(products) if products else "—")

    st.divider()

    # ── Batch selector ──
    batch = _render_batch_selector(batches)
    if batch is None:
        return

    st.divider()

    # ── Measurement form + trend chart side by side ──
    left, right = st.columns(2)
    with left:
        _render_log_measurement(batch)
    with right:
        _render_trend_chart(batch)

    st.divider()

    # ── Full batches table ──
    _render_batches_table(batches)
