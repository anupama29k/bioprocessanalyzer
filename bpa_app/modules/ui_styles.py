"""Custom CSS for clean, scientist-friendly UI."""
import streamlit as st

def apply():
    st.markdown("""
    <style>
    /* Clean metric cards */
    [data-testid="metric-container"] {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px 16px;
    }
    /* Sidebar style */
    section[data-testid="stSidebar"] {
        background: #1a1a2e;
    }
    section[data-testid="stSidebar"] * {
        color: #e8e8f0 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 13px;
        padding: 4px 0;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        font-size: 13px;
        font-weight: 500;
    }
    /* Status badges */
    .badge-green { background:#d4edda; color:#155724; border-radius:12px; padding:2px 10px; font-size:11px; font-weight:600; }
    .badge-amber { background:#fff3cd; color:#856404; border-radius:12px; padding:2px 10px; font-size:11px; font-weight:600; }
    .badge-red   { background:#f8d7da; color:#721c24; border-radius:12px; padding:2px 10px; font-size:11px; font-weight:600; }
    .badge-blue  { background:#cce5ff; color:#004085; border-radius:12px; padding:2px 10px; font-size:11px; font-weight:600; }
    /* Equation blocks */
    .eq-block {
        background: #f1f3f5;
        border-left: 3px solid #6c757d;
        border-radius: 4px;
        padding: 8px 12px;
        font-family: monospace;
        font-size: 12px;
        margin: 8px 0;
        white-space: pre-wrap;
    }
    /* Check list items */
    .check-ok   { color: #28a745; font-weight: 600; }
    .check-warn { color: #fd7e14; font-weight: 600; }
    .check-fail { color: #dc3545; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)
