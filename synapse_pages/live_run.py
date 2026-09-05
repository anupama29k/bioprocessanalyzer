"""Live Run — Bioprocess analyser sub-pages with cross-referenced instrument methods."""
import streamlit as st
import pandas as pd
from datetime import datetime
from databank import ANALYTICAL_DATABANK
from pulse import pulse_fragment  # Pulse live telemetry writer

# Import all BPA page modules
from pages import (
    homepage,
    data_import,
    analysis,
    strain_library,
    mass_balance,
    scale_up,
    run_registry,
    golden_batch,
    digital_twin,
    ai_assistant,
)

# ── Sensor key -> databank (category, instrument) mapping ────────────────────
# Maps BPA sensor keys to the most relevant instrument in the Analytical Data Bank.
SENSOR_TO_INSTRUMENT = {
    "ph":            ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
    "do":            ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
    "temp":          ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
    "od":            ("Spectroscopy", "UV-Vis"),
    "dcm":           ("Spectroscopy", "UV-Vis"),
    "substrate":     ("Chromatography", "HPLC"),
    "product":       ("Chromatography", "HPLC"),
    "vcd":           ("Cell-Based & Microbiological", "Cell Counters"),
    "offgas_o2":     ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
    "offgas_co2":    ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
    "nh3":           ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
    "raman_glucose": ("Spectroscopy", "Raman"),
    "raman_lactate": ("Spectroscopy", "Raman"),
    "raman_glutamine": ("Spectroscopy", "Raman"),
    "nir_conc":      ("Spectroscopy", "NIR"),
    "conductivity":  ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
    "pco2":          ("Cell-Based & Microbiological", "Bioprocess Analyzers"),
}


def _render_instrument_panel():
    """Show relevant instrument reference info based on mapped sensors in the active run."""
    col_map = st.session_state.get("col_map", {})
    if not col_map:
        return

    # Collect unique instruments that are relevant to the current run
    active_instruments = {}
    for sensor_key, col_name in col_map.items():
        if col_name and sensor_key in SENSOR_TO_INSTRUMENT:
            cat, inst = SENSOR_TO_INSTRUMENT[sensor_key]
            active_instruments[(cat, inst)] = active_instruments.get((cat, inst), [])
            active_instruments[(cat, inst)].append(sensor_key)

    if not active_instruments:
        return

    st.divider()
    st.subheader("Relevant Instrument Methods & Acceptance Criteria")
    st.caption("Auto-matched from your active sensor mapping to the Analytical Data Bank")

    for (cat, inst_key), sensors in active_instruments.items():
        inst_data = ANALYTICAL_DATABANK.get(cat, {}).get(inst_key)
        if not inst_data:
            continue

        sensor_labels = ", ".join(sensors)
        with st.expander(
            f"{inst_data.get('full_name', inst_key)} — sensors: {sensor_labels}",
            expanded=False,
        ):
            # Principle (brief)
            principle = inst_data.get("principle", "")
            if principle:
                st.markdown(f"**Principle:** {principle[:300]}{'...' if len(principle) > 300 else ''}")

            # Methods by product (first product type as preview)
            methods_by_product = inst_data.get("methods_by_product", {})
            if methods_by_product:
                st.markdown("**Methods (first product type):**")
                first_product = next(iter(methods_by_product))
                methods = methods_by_product[first_product]
                rows = [
                    {
                        "Method": m.get("method", ""),
                        "Purpose": m.get("purpose", ""),
                        "Detection": m.get("detection", ""),
                        "Run Time": m.get("run_time", ""),
                    }
                    for m in methods
                ]
                st.dataframe(
                    pd.DataFrame(rows), use_container_width=True, hide_index=True
                )

            # Acceptance criteria
            reporting = inst_data.get("data_reporting", {})
            acceptance = reporting.get("acceptance_criteria_examples", {})
            if acceptance:
                st.markdown("**Acceptance Criteria:**")
                for test_name, criteria in acceptance.items():
                    items = " | ".join(f"**{p}:** {v}" for p, v in criteria.items())
                    st.markdown(f"- *{test_name}* — {items}")

            # Regulatory refs
            refs = inst_data.get("regulatory_references", [])
            if refs:
                st.markdown("**Regulatory refs:** " + " · ".join(refs))


def _fetch_supabase_batches():
    """Fetch all batches from Supabase for the pulse batch selector."""
    sb = st.session_state.get("supabase")
    if sb is None:
        return []
    try:
        resp = sb.table("batches").select("id,batch_code").order("created_at", desc=True).execute()
        return resp.data or []
    except Exception:
        return []


def _render_pulse_batch_selector():
    """Sidebar dropdown to designate which Supabase batch Pulse writes to."""
    sb = st.session_state.get("supabase")
    if sb is None:
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### Pulse — Live Writer")

    batches = _fetch_supabase_batches()
    if not batches:
        st.sidebar.caption("No batches in Supabase. Create one in Batch History.")
        st.session_state.pop("pulse_batch_id", None)
        return

    labels = ["— None —"] + [b["batch_code"] for b in batches]

    # Default to the most recently created batch on first load
    default_idx = 0
    if "pulse_batch_selector" not in st.session_state:
        # batches are already ordered by created_at desc, so index 1 = most recent
        if len(batches) > 0:
            default_idx = 1
    choice = st.sidebar.selectbox(
        "Write to batch", labels, index=default_idx, key="pulse_batch_selector"
    )

    if choice == "— None —":
        st.session_state.pop("pulse_batch_id", None)
        st.sidebar.caption("Pulse paused — no batch selected.")
    else:
        selected = next(b for b in batches if b["batch_code"] == choice)
        st.session_state["pulse_batch_id"] = selected["id"]
        st.sidebar.success(f"Pulse target: **{choice}**")

    # Status indicator
    last_write = st.session_state.get("_pulse_last_write")
    last_error = st.session_state.get("_pulse_last_error")
    last_count = st.session_state.get("_pulse_last_count", 0)

    if last_error:
        st.sidebar.error(f"Pulse error: {last_error}")
    elif last_write:
        try:
            ts = datetime.fromisoformat(last_write).astimezone()
            ts_str = ts.strftime("%H:%M:%S")
        except Exception:
            ts_str = last_write
        st.sidebar.caption(f"Last write: {ts_str} ({last_count} params)")


def render():
    """Render the Live Run section with BPA sub-page navigation."""
    # ── Sub-page navigation ──
    bpa_pages = {
        "Dashboard":      homepage,
        "Data Import":    data_import,
        "Analysis":       analysis,
        "Mass Balance":   mass_balance,
        "Scale-up Model": scale_up,
        "Golden Batch":   golden_batch,
        "Digital Twin":   digital_twin,
        "Strain Library": strain_library,
        "Run Registry":   run_registry,
        "AI Assistant":   ai_assistant,
    }

    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Run Pages")

    # Allow "Go to Analysis" button in data_import to navigate here
    _nav_default = st.session_state.pop("nav_page", None)
    # Map the BPA nav label to our label (strip emoji prefix)
    _default_key = None
    if _nav_default:
        for key in bpa_pages:
            if key in _nav_default:
                _default_key = key
                break
    _nav_index = list(bpa_pages.keys()).index(_default_key) if _default_key else 0

    selected_sub = st.sidebar.radio(
        "Sub-page",
        list(bpa_pages.keys()),
        index=_nav_index,
        label_visibility="collapsed",
        key="live_run_sub",
    )

    # ── Batch run selector ──
    _runs = st.session_state.get("uploaded_runs", {})
    if _runs:
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### Active Batch")
        _run_names = list(_runs.keys())
        _active_now = st.session_state.get("active_run", _run_names[0])
        if _active_now not in _run_names:
            _active_now = _run_names[0]
        _selected_run = st.sidebar.selectbox(
            "Switch run",
            _run_names,
            index=_run_names.index(_active_now),
            key="lr_batch_selector",
            label_visibility="collapsed",
        )
        if _selected_run != st.session_state.get("active_run"):
            _entry = _runs[_selected_run]
            _df = _entry["df"] if isinstance(_entry, dict) and "df" in _entry else _entry
            st.session_state.active_run = _selected_run
            st.session_state.run_data = _df
            st.session_state.run_name = _selected_run
            from pages.data_import import auto_detect_mapping
            st.session_state.col_map = auto_detect_mapping(_df.columns.tolist())
            st.rerun()
        st.sidebar.caption(f"{len(_run_names)} batch(es) loaded")

    # ── Quick KPI sidebar ──
    if st.session_state.get("run_data") is not None:
        st.sidebar.markdown("---")
        st.sidebar.success(f"**Active run:** {st.session_state.get('run_name', 'Unnamed')}")
        if st.session_state.get("mu") is not None:
            st.sidebar.metric("mu (1/h)", f"{st.session_state.mu:.3f}")
        if st.session_state.get("titer") is not None:
            st.sidebar.metric("Titer (g/L)", f"{st.session_state.titer:.3f}")
        if st.session_state.get("c_closure") is not None:
            st.sidebar.metric("C closure (%)", f"{st.session_state.c_closure:.1f}")
    else:
        st.sidebar.info("No run loaded. Start with **Data Import**.")

    # ── Supabase batch selector for Pulse ──
    _render_pulse_batch_selector()

    # ── pulse_batch_id is now set by _render_pulse_batch_selector above ──

    # ── Start Pulse fragment (60-second auto-write cycle) ──
    if st.session_state.get("supabase") and st.session_state.get("pulse_batch_id"):
        pulse_fragment()

    # ── Sensor sidebar (file upload + mapping) ──
    data_import.render_sensor_sidebar()

    # ── Sync sensor_map -> col_map + run_data ──
    _runs = st.session_state.get("uploaded_runs", {})
    _active = st.session_state.get("active_run")
    if _active and _active in _runs:
        _run_entry = _runs[_active]
        _df = _run_entry["df"] if isinstance(_run_entry, dict) and "df" in _run_entry else _run_entry
        st.session_state.run_data = _df
        _sm = st.session_state.get("col_map", {})
        valid_cm = {k: v for k, v in _sm.items() if v and v in _df.columns}
        st.session_state.col_map = valid_cm

    # ── Pulse status bar (visible in main area) ──
    _pulse_id = st.session_state.get("pulse_batch_id", "NOT SET")
    _pulse_last = st.session_state.get("_pulse_last_write")
    _pulse_err = st.session_state.get("_pulse_last_error")
    _pulse_count = st.session_state.get("_pulse_last_count", 0)

    if _pulse_err:
        st.error(f"Pulse error: {_pulse_err} | batch_id = `{_pulse_id}`")
    elif _pulse_last:
        try:
            _ts = datetime.fromisoformat(_pulse_last).astimezone().strftime("%H:%M:%S")
        except Exception:
            _ts = _pulse_last
        st.success(
            f"Pulse active — writing to batch `{_pulse_id}` | "
            f"Last write: {_ts} ({_pulse_count} params)"
        )
    elif _pulse_id != "NOT SET":
        st.info(f"Pulse armed — batch `{_pulse_id}` selected, waiting for first write cycle (60s).")
    else:
        st.warning(f"Pulse idle — no batch selected. `pulse_batch_id` = `{_pulse_id}`")

    # ── Render selected BPA sub-page ──
    bpa_pages[selected_sub].render()

    # ── Instrument cross-reference panel (below the BPA content) ──
    _render_instrument_panel()
