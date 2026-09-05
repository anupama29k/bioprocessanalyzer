"""
PULSE — Live telemetry writer for SYNAPSE.

Reads the latest process readings from the bioprocess analyser session state
and writes each parameter as a row to the Supabase `process_measurements`
table every 60 seconds while a batch is active.
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# ── Sensor key → (parameter_name, unit) mapping ────────────────────────────
# Maps BPA session-state sensor keys to the names/units stored in Supabase.
SENSOR_MAP = {
    "ph":              ("pH",          ""),
    "do":              ("DO",          "%"),
    "temp":            ("temperature", "°C"),
    "rpm":             ("agitation",   "rpm"),
    "od":              ("OD600",       "AU"),
    "dcm":             ("DCM",         "g/L"),
    "vcd":             ("VCD",         "x10^6 cells/mL"),
    "substrate":       ("glucose",     "g/L"),
    "product":         ("titer",       "g/L"),
    "nh3":             ("ammonia",     "mM"),
    "air_flow":        ("air_flow",    "SLPM"),
    "o2_flow":         ("O2_flow",     "SLPM"),
    "co2_flow":        ("CO2_flow",    "SLPM"),
    "offgas_o2":       ("offgas_O2",   "%"),
    "offgas_co2":      ("offgas_CO2",  "%"),
    "weight":          ("weight",      "g"),
    "base_vol":        ("base_vol",    "mL"),
    "acid_vol":        ("acid_vol",    "mL"),
    "pressure":        ("pressure",    "bar"),
    "conductivity":    ("conductivity", "mS/cm"),
    "pco2":            ("pCO2",        "mmHg"),
    "raman_glucose":   ("raman_glucose",   "g/L"),
    "raman_lactate":   ("raman_lactate",   "g/L"),
    "raman_glutamine": ("raman_glutamine", "g/L"),
    "nir_conc":        ("NIR_conc",    "g/L"),
}

# All sensor keys we attempt to read (order preserved for consistency).
SENSOR_KEYS = list(SENSOR_MAP.keys())


def _safe_float(val):
    """Convert a value to a plain Python float, or return None."""
    if val is None:
        return None
    try:
        f = float(val)
        if np.isfinite(f):
            return f
    except (ValueError, TypeError):
        pass
    return None


def _get_latest_readings():
    """
    Extract the latest row of process data from session state.

    Returns (elapsed_time_h, dict_of_readings) or (None, None) if no active run.
    """
    run_data: pd.DataFrame | None = st.session_state.get("run_data")
    if run_data is None or run_data.empty:
        return None, None

    col_map: dict = st.session_state.get("col_map", {})
    if not col_map:
        return None, None

    last_idx = run_data.index[-1]

    # Get elapsed time
    time_col = col_map.get("time")
    elapsed_h = None
    if time_col and time_col in run_data.columns:
        elapsed_h = _safe_float(run_data.at[last_idx, time_col])

    readings = {}
    for key in SENSOR_KEYS:
        col = col_map.get(key)
        if col and col in run_data.columns:
            val = _safe_float(run_data.at[last_idx, col])
            if val is not None:
                readings[key] = val

    return elapsed_h, readings


def _has_instrument_source(sb):
    """Check if instrument_source column exists (cached per session)."""
    key = "_pulse_has_inst_source"
    if key in st.session_state:
        return st.session_state[key]
    try:
        sb.table("process_measurements").select("instrument_source").limit(0).execute()
        st.session_state[key] = True
    except Exception:
        st.session_state[key] = False
    return st.session_state[key]


def _write_measurements(sb, batch_id, elapsed_h, readings):
    """Insert one row per parameter into process_measurements."""
    day_of_run = round(elapsed_h / 24.0, 4) if elapsed_h is not None else 0.0
    add_source = _has_instrument_source(sb)

    rows = []
    for sensor_key, value in readings.items():
        param_name, unit = SENSOR_MAP[sensor_key]
        row = {
            "batch_id": batch_id,
            "parameter_name": param_name,
            "value": value,
            "day_of_run": day_of_run,
        }
        if unit:
            row["unit"] = unit
        if add_source:
            row["instrument_source"] = "online"
        rows.append(row)

    if rows:
        sb.table("process_measurements").insert(rows).execute()

    return len(rows)


@st.fragment(run_every=timedelta(seconds=60))
def pulse_fragment():
    """
    Streamlit fragment that fires every 60 seconds.
    Reads the latest sensor readings and writes them to Supabase.
    """
    sb = st.session_state.get("supabase")
    if sb is None:
        return

    # Batch must be selected via the Live Run sidebar selector
    batch_id = st.session_state.get("pulse_batch_id")
    if not batch_id:
        return

    elapsed_h, readings = _get_latest_readings()
    if not readings:
        return

    # Avoid duplicate writes for the same elapsed_time_h
    last_key = "_pulse_last_elapsed"
    if elapsed_h is not None and elapsed_h == st.session_state.get(last_key):
        return
    st.session_state[last_key] = elapsed_h

    try:
        count = _write_measurements(sb, batch_id, elapsed_h, readings)
        st.session_state["_pulse_last_write"] = datetime.now(timezone.utc).isoformat()
        st.session_state["_pulse_last_count"] = count
        st.session_state.pop("_pulse_last_error", None)
    except Exception as exc:
        st.session_state["_pulse_last_error"] = str(exc)
