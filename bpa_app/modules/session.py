"""Central session state initialisation."""
import streamlit as st
import json
from pathlib import Path

# Store registry/strain files next to app.py regardless of where the app lives
REGISTRY_FILE = Path(__file__).parent.parent / "run_registry.json"
STRAIN_FILE   = Path(__file__).parent.parent / "strain_library.json"

DEFAULTS = {
    # Active run
    "run_data": None,
    "run_date": "",
    "run_operator": "",
    "run_organism": "",
    "run_project": "",
    "run_objective": "",
    "run_notes": "",
    "reactor_type": "Stirred tank (STR)",
    "working_vol": 1.0,
    "temp_sp": 37.0,
    "ph_sp": 7.0,
    "do_sp": 30.0,
    # Multi-run upload store
    "uploaded_runs": {},
    # Sensor mapping (sensor_key -> column_name)
    "sensor_map": {},
    "run_name": "",
    "run_mode": "Batch",           # Batch | Fed-batch | Continuous
    "substrates": ["Glucose"],
    "products": ["Product 1"],
    "time_col": None,

    # Computed kinetics
    "mu": None,
    "doubling_time_min": None,
    "lag_time_h": None,
    "r2_growth": None,
    "titer": None,
    "sty": None,
    "yps": None,
    "yxs": None,
    "c_closure": None,
    "rq": None,
    "lp_alpha": None,
    "lp_beta": None,

    # Strain
    "active_strain": None,
    "strain_library": [],

    # Run registry
    "run_registry": [],

    # Golden batch reference
    "golden_batch": None,
    "golden_batch_name": "",

    # Digital twin
    "dt_model": None,
    "dt_params": {},

    # AI chat history
    "chat_history": [],

    # Contamination / anomaly flags
    "anomaly_flags": [],

    # Scale-up results
    "scaleup_results": None,

    # Column mapping
    "col_map": {},
}


def init():
    """Initialise all session state keys if not present."""
    for key, default in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Load persistent data from disk
    if not st.session_state.run_registry:
        _load_registry()
    if not st.session_state.strain_library:
        _load_strains()


def _load_registry():
    if REGISTRY_FILE.exists():
        try:
            st.session_state.run_registry = json.loads(REGISTRY_FILE.read_text())
        except Exception:
            st.session_state.run_registry = []


def _load_strains():
    if STRAIN_FILE.exists():
        try:
            st.session_state.strain_library = json.loads(STRAIN_FILE.read_text())
        except Exception:
            st.session_state.strain_library = []


def save_registry():
    REGISTRY_FILE.write_text(json.dumps(st.session_state.run_registry, indent=2))


def save_strains():
    STRAIN_FILE.write_text(json.dumps(st.session_state.strain_library, indent=2))
