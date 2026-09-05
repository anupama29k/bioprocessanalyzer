import streamlit as st
import pandas as pd
from databank import ANALYTICAL_DATABANK

st.set_page_config(
    page_title="Analytical Data Bank | Biotech & Biopharma",
    page_icon="\U0001f52c",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom styling ──
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {padding: 8px 16px; font-weight: 500;}
    div[data-testid="stMetric"] {background: #f8f9fb; border-radius: 8px; padding: 12px; border-left: 4px solid #4e79a7;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ──
st.title("\U0001f52c Analytical Data Bank")
st.caption("Comprehensive reference for analytical instrumentation in Biotech & Biopharma — Principles, Industry Models, Methods by Product, and Data Reporting Standards")

# ── Sidebar Navigation ──
st.sidebar.header("Navigation")
categories = list(ANALYTICAL_DATABANK.keys())

# Stats
total_instruments = sum(len(v) for v in ANALYTICAL_DATABANK.values())
st.sidebar.metric("Total Instruments", total_instruments)
st.sidebar.metric("Categories", len(categories))

selected_category = st.sidebar.selectbox("Select Category", categories)
instruments = ANALYTICAL_DATABANK[selected_category]
instrument_names = list(instruments.keys())
selected_instrument = st.sidebar.selectbox("Select Instrument", instrument_names)

# Quick search
st.sidebar.markdown("---")
search_term = st.sidebar.text_input("\U0001f50d Search across all instruments", "")

# ── Search Results ──
if search_term.strip():
    st.header(f"Search Results for: \"{search_term}\"")
    results_found = False
    for cat, insts in ANALYTICAL_DATABANK.items():
        for inst_key, inst_data in insts.items():
            # Search in name, principle, and methods
            searchable = (
                inst_data.get("full_name", "")
                + " "
                + inst_key
                + " "
                + inst_data.get("principle", "")
            )
            # Also search in methods
            for product, methods in inst_data.get("methods_by_product", {}).items():
                searchable += " " + product
                for m in methods:
                    searchable += " " + m.get("method", "") + " " + m.get("purpose", "")

            if search_term.lower() in searchable.lower():
                results_found = True
                st.markdown(f"**{cat}** \u2192 **{inst_data.get('full_name', inst_key)}**")
                st.caption(inst_data.get("principle", "")[:200] + "...")
                st.markdown("---")

    if not results_found:
        st.info("No instruments found matching your search term.")

else:
    # ── Main Content ──
    data = instruments[selected_instrument]

    # Title bar
    st.header(f"{data.get('full_name', selected_instrument)}")
    st.markdown(f"**Category:** {selected_category} | **Short Code:** {selected_instrument}")

    # ── Tabs ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "\U0001f9ea Principle",
        "\U0001f3ed Industry Models",
        "\U0001f4cb Methods by Product",
        "\U0001f4ca Data Reporting",
        "\U0001f4d6 Regulatory References",
    ])

    # ── TAB 1: Principle ──
    with tab1:
        st.subheader("Working Principle")
        st.markdown(data.get("principle", "N/A"))

    # ── TAB 2: Industry Models ──
    with tab2:
        st.subheader("Industry Models & Equipment")
        models = data.get("industry_models", [])
        if models:
            df_models = pd.DataFrame(models)
            df_models.columns = [c.replace("_", " ").title() for c in df_models.columns]
            st.dataframe(df_models, use_container_width=True, hide_index=True)

            # Summary by vendor
            st.markdown("**Vendor Distribution:**")
            vendor_counts = df_models["Vendor"].value_counts()
            cols = st.columns(min(len(vendor_counts), 5))
            for i, (vendor, count) in enumerate(vendor_counts.items()):
                cols[i % len(cols)].metric(vendor, f"{count} model(s)")
        else:
            st.info("No model data available for this instrument.")

    # ── TAB 3: Methods by Product ──
    with tab3:
        st.subheader("Analytical Methods by Product Type")
        methods_by_product = data.get("methods_by_product", {})

        if methods_by_product:
            product_types = list(methods_by_product.keys())
            selected_product = st.selectbox("Select Product Type", product_types)

            methods = methods_by_product[selected_product]
            for i, method in enumerate(methods):
                with st.expander(f"\U0001f539 {method['method']} — {method['purpose']}", expanded=(i == 0)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Method:** {method.get('method', 'N/A')}")
                        st.markdown(f"**Purpose:** {method.get('purpose', 'N/A')}")
                        st.markdown(f"**Column / Setup:** {method.get('column', 'N/A')}")
                    with col2:
                        st.markdown(f"**Mobile Phase / Reagent:** {method.get('mobile_phase', 'N/A')}")
                        st.markdown(f"**Detection:** {method.get('detection', 'N/A')}")
                        st.markdown(f"**Run Time:** {method.get('run_time', 'N/A')}")

            # Methods summary table
            st.markdown("---")
            st.markdown("**All Methods Summary:**")
            summary_data = []
            for method in methods:
                summary_data.append({
                    "Method": method.get("method", ""),
                    "Purpose": method.get("purpose", ""),
                    "Detection": method.get("detection", ""),
                    "Run Time": method.get("run_time", ""),
                })
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
        else:
            st.info("No method data available for this instrument.")

    # ── TAB 4: Data Reporting ──
    with tab4:
        st.subheader("Data Reporting Standards")
        reporting = data.get("data_reporting", {})

        if reporting:
            # Report sections
            report_sections = reporting.get("report_sections", [])
            if report_sections:
                st.markdown("#### Report Sections")
                for i, section in enumerate(report_sections, 1):
                    st.markdown(f"{i}. {section}")

            st.markdown("---")

            # Key parameters
            key_params = reporting.get("key_parameters", {})
            if key_params:
                st.markdown("#### Key Parameters & Specifications")
                for param_group, params in key_params.items():
                    with st.expander(f"**{param_group}**", expanded=True):
                        for param in params:
                            st.markdown(f"- {param}")

            st.markdown("---")

            # Acceptance criteria
            acceptance = reporting.get("acceptance_criteria_examples", {})
            if acceptance:
                st.markdown("#### Acceptance Criteria Examples")
                for test_name, criteria in acceptance.items():
                    with st.expander(f"**{test_name}**"):
                        for param, limit in criteria.items():
                            st.markdown(f"- **{param}:** {limit}")
        else:
            st.info("No reporting data available for this instrument.")

    # ── TAB 5: Regulatory References ──
    with tab5:
        st.subheader("Regulatory & Pharmacopeial References")
        refs = data.get("regulatory_references", [])
        if refs:
            for ref in refs:
                st.markdown(f"- {ref}")
        else:
            st.info("No regulatory references listed.")

    # ── Cross-reference: All instruments in this category ──
    st.markdown("---")
    st.subheader(f"All Instruments in {selected_category}")
    overview_data = []
    for key, val in instruments.items():
        overview_data.append({
            "Instrument": key,
            "Full Name": val.get("full_name", ""),
            "Models Available": len(val.get("industry_models", [])),
            "Product Methods": len(val.get("methods_by_product", {})),
            "Regulatory Refs": len(val.get("regulatory_references", [])),
        })
    st.dataframe(pd.DataFrame(overview_data), use_container_width=True, hide_index=True)

# ── Footer ──
st.markdown("---")
st.caption(
    "Analytical Data Bank v1.0 | Biotech & Biopharma Instrumentation Reference | "
    "Covers Chromatography, Mass Spectrometry, Spectroscopy, Electrophoresis, "
    "Bioanalytical Assays, Particle Characterization, Cell-Based Methods, and Imaging."
)
