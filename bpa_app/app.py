"""
Unified Bioprocess Analyser
A scientist-first platform for batch, fed-batch, and continuous fermentation analysis.
"""

import streamlit as st
from pathlib import Path

# ── Page config (must be first) ───────────────────────────────────────────────
st.set_page_config(
    page_title="Bioprocess Analyser",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import modules ────────────────────────────────────────────────────────────
from modules import session, ui_styles
from views import (
    homepage,
    data_import,
    analysis,
    growth_kinetics,
    product_profiles,
    strain_library,
    mass_balance,
    scale_up,
    run_registry,
    golden_batch,
    digital_twin,
    ai_assistant,
)
from data_manager import DataManager, render_project_sidebar

# ── Apply custom CSS ──────────────────────────────────────────────────────────
ui_styles.apply()

# ── Initialise session state ──────────────────────────────────────────────────
session.init()

# ── Initialise data manager ──────────────────────────────────────────────────
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()

# ── Sidebar — navigation + sensor mapping (always visible) ────────────────────
with st.sidebar:
    st.markdown("### 🧬 Bioprocess Analyser")
    st.caption("Bench-to-scale fermentation platform · v2.2")
    st.divider()

    # Page navigation
    pages = {
        "🏠 Dashboard": homepage,
        "📥 Data Import": data_import,
        "📊 Analysis": analysis,
        "📈 Growth Kinetics": growth_kinetics,
        "🧪 Product Profiles": product_profiles,
        "⚖️ Mass Balance": mass_balance,
        "🔬 Scale-up Model": scale_up,
        "✨ Golden Batch": golden_batch,
        "🤖 Digital Twin": digital_twin,
        "🧫 Strain Library": strain_library,
        "📋 Run Registry": run_registry,
        "💬 AI Assistant": ai_assistant,
    }

    # Allow "Go to Analysis" button in data_import to navigate here
    _nav_default = st.session_state.pop("nav_page", None)
    _nav_index   = list(pages.keys()).index(_nav_default) if _nav_default in pages else 0

    selected = st.radio(
        "Navigate",
        list(pages.keys()),
        index=_nav_index,
        label_visibility="collapsed",
        key="nav_radio",
    )

    # ── Batch run selector ─────────────────────────────────────────────────
    _runs = st.session_state.get("uploaded_runs", {})
    if _runs:
        st.divider()
        st.markdown("#### 🗂 Active Batch")
        _run_names   = list(_runs.keys())
        _active_now  = st.session_state.get("active_run", _run_names[0])
        if _active_now not in _run_names:
            _active_now = _run_names[0]
        _selected_run = st.selectbox(
            "Switch run",
            _run_names,
            index=_run_names.index(_active_now),
            key="batch_selector",
            label_visibility="collapsed",
        )
        if _selected_run != st.session_state.get("active_run"):
            _entry = _runs[_selected_run]
            _df    = _entry["df"] if isinstance(_entry, dict) and "df" in _entry else _entry
            st.session_state.active_run  = _selected_run
            st.session_state.run_data    = _df
            st.session_state.run_name    = _selected_run
            # Re-detect sensor mapping for the new run
            from views.data_import import auto_detect_mapping
            st.session_state.col_map = auto_detect_mapping(_df.columns.tolist())
            st.rerun()
        st.caption(f"{len(_run_names)} batch(es) loaded")

    st.divider()

    # Quick KPI summary (shows after analysis)
    if st.session_state.get("run_data") is not None:
        st.success(f"**Active run:** {st.session_state.get('run_name', 'Unnamed')}")
        if st.session_state.get("mu") is not None:
            st.metric("μ (h⁻¹)", f"{st.session_state.mu:.3f}")
        if st.session_state.get("titer") is not None:
            st.metric("Titer (g/L)", f"{st.session_state.titer:.3f}")
        if st.session_state.get("c_closure") is not None:
            st.metric("C closure (%)", f"{st.session_state.c_closure:.1f}")
    else:
        st.info("No run loaded. Start with **Data Import**.")

    # Scale-up KPI summary (shows after scale-up compute)
    _su = st.session_state.get("scaleup_results")
    if _su:
        st.divider()
        st.markdown("#### 🔬 Scale-up")
        for r in _su[-1:]:  # show largest scale only
            st.caption(r.get("label", ""))
            st.metric("N (rpm)", f"{r['N_rpm']:.0f}")
            st.metric("kLa (h⁻¹)", f"{r['kLa']:.0f}")
            _perf = r.get("perf", 0)
            st.metric("Perf factor", f"{_perf:.3f}")

    # ── Project management sidebar ─────────────────────────────────────────
    render_project_sidebar(st.session_state.data_manager)

    st.divider()

# ── Sensor sidebar — always visible, rendered outside the nav block ───────────
# Renders file upload + all sensor mapping groups into st.sidebar
data_import.render_sensor_sidebar()

# ── Sync sensor_map → col_map + run_data on every page load ──────────────────
# This ensures growth_kinetics, mass_balance etc. always see the latest mapping
# regardless of which page the user is on.
_runs = st.session_state.get("uploaded_runs", {})
_active = st.session_state.get("active_run")
if _active and _active in _runs:
    _run_entry = _runs[_active]
    # uploaded_runs stores {"df": df, "filename": ...}
    _df = _run_entry["df"] if isinstance(_run_entry, dict) and "df" in _run_entry else _run_entry
    st.session_state.run_data = _df

    # Build col_map from sensor_map, only keeping columns that exist in the df
    _sm = st.session_state.get("col_map", {})  # already set by render_sensor_sidebar
    # Make sure legacy keys used by other pages are mapped
    # e.g. growth_kinetics uses "time", "od", "product", "glucose"
    # These should already match since sensor keys == legacy keys for core fields
    valid_cm = {k: v for k, v in _sm.items() if v and v in _df.columns}
    st.session_state.col_map = valid_cm

# ── Render selected page ──────────────────────────────────────────────────────
pages[selected].render()
