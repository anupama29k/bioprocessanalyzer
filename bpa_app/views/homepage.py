"""Homepage / Dashboard — central hub for fermentation data management."""
import streamlit as st
import pandas as pd
from data_manager import DataManager


def render():
    # ── Custom styling ────────────────────────────────────────────────────
    st.markdown("""
    <style>
        .run-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            border-left: 4px solid #0066cc;
        }
        div[data-testid="stMetric"] {
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 12px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏠 Dashboard")
    st.caption("Fermentation data hub — manage runs, view KPIs, jump to analysis")

    dm: DataManager = st.session_state.get("data_manager")
    if dm is None:
        dm = DataManager()
        st.session_state.data_manager = dm

    runs_df = dm.get_all_runs()
    uploaded_runs = st.session_state.get("uploaded_runs", {})

    # ── Top metrics row ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    n_saved = len(runs_df) if not runs_df.empty else 0
    n_session = len(uploaded_runs)
    c1.metric("Saved Runs", n_saved)
    c2.metric("Session Runs", n_session)

    if not runs_df.empty and "strain" in runs_df.columns:
        c3.metric("Strains", runs_df["strain"].nunique())
    else:
        c3.metric("Strains", 0)

    # Show mu from current analysis if available
    mu_val = st.session_state.get("mu")
    c4.metric("Active μ (h⁻¹)", f"{mu_val:.3f}" if mu_val else "—")

    st.divider()

    # ── Two-column layout ────────────────────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    # ── LEFT: Run browser ────────────────────────────────────────────────
    with col_left:
        # Session runs (currently loaded)
        if uploaded_runs:
            st.subheader("🗂 Session Runs")
            for run_name, entry in uploaded_runs.items():
                df_run = entry["df"] if isinstance(entry, dict) and "df" in entry else entry
                is_active = run_name == st.session_state.get("active_run")
                cols = st.columns([3, 1, 1])
                prefix = "▶ " if is_active else ""
                cols[0].markdown(f"**{prefix}{run_name}**")
                cols[0].caption(f"{len(df_run)} rows × {len(df_run.columns)} cols")
                if cols[1].button("Load", key=f"home_load_{run_name}",
                                  disabled=is_active):
                    from views.data_import import auto_detect_mapping
                    st.session_state.active_run = run_name
                    st.session_state.run_data = df_run
                    st.session_state.run_name = run_name
                    st.session_state.col_map = auto_detect_mapping(
                        df_run.columns.tolist())
                    st.session_state.nav_page = "📊 Analysis"
                    st.rerun()
                if cols[2].button("📊", key=f"home_view_{run_name}"):
                    st.session_state.active_run = run_name
                    st.session_state.nav_page = "📊 Analysis"
                    st.rerun()
            st.divider()

        # Saved runs (from data_manager)
        st.subheader("📂 Saved Runs")
        if not runs_df.empty:
            # Search / filter
            fc1, fc2 = st.columns(2)
            filter_strain = fc1.text_input("Filter by strain", key="home_filter_strain")
            filter_medium = fc2.text_input("Filter by medium", key="home_filter_medium")

            display_df = runs_df.copy()
            if filter_strain:
                display_df = display_df[
                    display_df["strain"].str.contains(filter_strain, case=False, na=False)]
            if filter_medium:
                display_df = display_df[
                    display_df["medium"].str.contains(filter_medium, case=False, na=False)]

            if "upload_date" in display_df.columns:
                display_df = display_df.sort_values("upload_date", ascending=False)

            # Group by project if column exists, otherwise flat list
            has_project = ("project" in display_df.columns and
                           display_df["project"].notna().any() and
                           (display_df["project"] != "").any())

            if has_project:
                # Project-grouped view
                grouped = display_df.groupby("project", dropna=False)
                for project, group in grouped:
                    proj_label = project if project and str(project).strip() else "Ungrouped"
                    with st.expander(
                            f"📁 {proj_label} ({len(group)} runs)", expanded=True):
                        for _, row in group.iterrows():
                            _render_run_row(row, dm)
            else:
                # Flat recent list
                recent = display_df.head(10)
                for _, row in recent.iterrows():
                    _render_run_row(row, dm)

            # Full table in expander
            with st.expander(f"All runs ({len(display_df)})"):
                show_cols = [c for c in ["run_id", "strain", "medium",
                              "upload_date", "volume_L", "project", "objective"]
                             if c in display_df.columns]
                st.dataframe(display_df[show_cols] if show_cols else display_df,
                             hide_index=True, use_container_width=True)
        else:
            st.info("No saved runs yet. Upload data via the sidebar or "
                    "Data Import page, then save runs to build your library.")

    # ── RIGHT: Quick actions + activity ──────────────────────────────────
    with col_right:
        st.subheader("⚡ Quick Actions")

        if st.button("📥 Data Import", use_container_width=True):
            st.session_state.nav_page = "📥 Data Import"
            st.rerun()
        if st.button("📊 Analysis", use_container_width=True,
                      disabled=st.session_state.get("run_data") is None):
            st.session_state.nav_page = "📊 Analysis"
            st.rerun()
        if st.button("⚖️ Mass Balance", use_container_width=True,
                      disabled=st.session_state.get("run_data") is None):
            st.session_state.nav_page = "⚖️ Mass Balance"
            st.rerun()
        if st.button("🔬 Scale-Up Wizard", use_container_width=True):
            st.session_state.nav_page = "🔬 Scale-up Model"
            st.rerun()
        if st.button("✨ Golden Batch", use_container_width=True):
            st.session_state.nav_page = "✨ Golden Batch"
            st.rerun()

        st.divider()

        # KPI summary for active run
        st.subheader("📊 Active Run KPIs")
        if st.session_state.get("run_data") is not None:
            run_name = st.session_state.get("run_name", "Unnamed")
            st.success(f"**{run_name}**")

            kpi_data = {}
            if st.session_state.get("mu") is not None:
                kpi_data["μ_max (h⁻¹)"] = f"{st.session_state.mu:.3f}"
            if st.session_state.get("titer") is not None:
                kpi_data["Titer (g/L)"] = f"{st.session_state.titer:.3f}"
            if st.session_state.get("c_closure") is not None:
                kpi_data["C closure (%)"] = f"{st.session_state.c_closure:.1f}"
            if st.session_state.get("yxs") is not None:
                kpi_data["Yx/s (g/g)"] = f"{st.session_state.yxs:.3f}"
            if st.session_state.get("rq") is not None:
                kpi_data["RQ"] = f"{st.session_state.rq:.2f}"

            if kpi_data:
                for label, val in kpi_data.items():
                    st.metric(label, val)
            else:
                st.caption("Run analysis to populate KPIs.")
        else:
            st.info("No active run. Upload or load data to begin.")

        st.divider()

        # Recent activity log
        st.subheader("📋 Recent Activity")
        _render_activity_log()


def _render_run_row(row, dm):
    """Render a single run row with Load and Delete buttons."""
    run_id = row.get("run_id", "")
    strain = row.get("strain", "—")
    medium = row.get("medium", "—")
    date = str(row.get("upload_date", ""))[:10]
    vol = row.get("volume_L", "")
    tags = row.get("tags", "")

    cols = st.columns([3, 1, 1])
    cols[0].markdown(f"**{run_id}**")
    caption = f"{strain} on {medium} | {date}"
    if vol:
        caption += f" | {vol}L"
    if tags and str(tags).strip():
        caption += f" | 🏷 {tags}"
    cols[0].caption(caption)

    if cols[1].button("Load", key=f"home_saved_{run_id}"):
        _load_saved_run(dm, run_id)
    if cols[2].button("🗑", key=f"home_del_{run_id}"):
        dm.delete_run(run_id)
        st.rerun()


def _load_saved_run(dm: DataManager, run_id: str):
    """Load a saved run into session state and navigate to analysis."""
    run_data = dm.get_run_by_id(run_id)
    if run_data and "data" in run_data:
        df = run_data["data"]
        from views.data_import import auto_detect_mapping

        # Add to uploaded_runs
        runs = st.session_state.get("uploaded_runs", {})
        runs[run_id] = {"df": df, "filename": run_data.get("original_filename", run_id)}
        st.session_state.uploaded_runs = runs

        # Set as active
        st.session_state.active_run = run_id
        st.session_state.run_data = df
        st.session_state.run_name = run_id
        st.session_state.col_map = auto_detect_mapping(df.columns.tolist())

        # Navigate to analysis
        st.session_state.nav_page = "📊 Analysis"
        st.rerun()
    else:
        st.error(f"Could not load run {run_id} — data file may be missing.")


def _render_activity_log():
    """Show recent activity from session state."""
    log = st.session_state.get("activity_log", [])
    if log:
        for entry in log[-5:]:
            st.caption(f"• {entry}")
    else:
        # Show contextual hints
        hints = []
        if st.session_state.get("uploaded_runs"):
            for name in list(st.session_state.uploaded_runs.keys())[-3:]:
                hints.append(f"Loaded: {name}")
        if st.session_state.get("mu") is not None:
            hints.append(f"Analysis: μ = {st.session_state.mu:.3f} h⁻¹")
        if st.session_state.get("scaleup_results"):
            hints.append("Scale-up prediction computed")
        if st.session_state.get("c_closure") is not None:
            hints.append(f"Mass balance: C closure = {st.session_state.c_closure:.1f}%")

        if hints:
            for h in hints:
                st.caption(f"• {h}")
        else:
            st.caption("No activity yet. Start by importing data.")
