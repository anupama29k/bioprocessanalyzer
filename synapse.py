"""
SYNAPSE — Unified Bioprocess & Analytical Platform
Merges the Analytical Data Bank and Bioprocess Analyser into one multi-page app.
"""
import os
import sys
from pathlib import Path

# ── Load environment variables from .env ─────────────────────────────────────
from dotenv import load_dotenv

_here = Path(__file__).resolve().parent
load_dotenv(_here / ".env")

# ── Make existing app modules importable without modifying them ───────────────
_bpa_dir = _here / "bpa_app"
_adb_dir = _here / "analytical_databank"

for p in (_bpa_dir, _adb_dir):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

# ── Streamlit must be imported after sys.path setup ──────────────────────────
import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="SYNAPSE",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import BPA initialisation ────────────────────────────────────────────────
from modules import session, ui_styles  # noqa: E402
from data_manager import DataManager  # noqa: E402

# ── Import SYNAPSE pages ─────────────────────────────────────────────────────
from synapse_pages import instrument_reference, run_manager  # noqa: E402

# Strain Library and Run Registry remain as standalone pages
from views import strain_library, run_registry  # noqa: E402

# Pulse — imported so Run Manager can invoke it
from pulse import pulse_fragment  # noqa: E402

# ── Supabase client ──────────────────────────────────────────────────────────
from supabase import create_client  # noqa: E402

@st.cache_resource
def _init_supabase():
    """Create a single Supabase client shared across all sessions."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

supabase_client = _init_supabase()
if supabase_client:
    st.session_state["supabase"] = supabase_client

# ── Apply global styles ──────────────────────────────────────────────────────
ui_styles.apply()

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: #f8f9fb;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #4e79a7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Initialise session state ─────────────────────────────────────────────────
session.init()

if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()

# ── Sidebar — top-level navigation ───────────────────────────────────────────
with st.sidebar:
    st.markdown("### SYNAPSE")
    st.caption("Unified Bioprocess & Analytical Platform")
    if supabase_client:
        st.caption("Cloud: connected")
    else:
        st.caption("Cloud: offline (check .env)")
    st.divider()

    section = st.radio(
        "Section",
        ["Run Manager", "Instrument Reference", "Strain Library", "Run Registry"],
        label_visibility="collapsed",
        key="synapse_section",
    )

# ── Start Pulse when on Run Manager (wires into Tab 2 automatically) ────────
if section == "Run Manager" and supabase_client:
    if st.session_state.get("pulse_batch_id"):
        pulse_fragment()

# ── Render selected section ──────────────────────────────────────────────────
if section == "Run Manager":
    run_manager.render()
elif section == "Instrument Reference":
    instrument_reference.render()
elif section == "Strain Library":
    strain_library.render()
elif section == "Run Registry":
    run_registry.render()

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "SYNAPSE v1.0 | Unified Bioprocess & Analytical Platform | "
    "Run Manager · Instrument Reference · Strain Library · Run Registry"
)
