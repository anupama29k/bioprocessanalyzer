"""Scale-up engineering model — full design & validation."""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.calcs import (scaleup_vessel, ScaleUpEngine, ScaleUpParameters,
                           get_lab_data_korz_1995, get_lab_data_verduyn_1990,
                           get_lab_data_neuss_2025, get_lab_data_mohanty_2025,
                           get_lab_data_pichia_hfbi_2025)

# ── Literature reference datasets ─────────────────────────────────────────────
LITERATURE = {
    "Korz et al. 1995 – E. coli fed-batch": {
        "V": 10, "mu": 0.45, "Yxs": 0.42, "max_od": 45,
        "rpm": 800, "vvm": 1.0, "PV": 2500, "kLa": 180,
        "HD": 2.5, "Np": 5.0, "OUR": 26.5,
        "diameter": 0.25, "aspect": 2.5,
    },
    "Verduyn et al. 1990 – S. cerevisiae": {
        "V": 1, "mu": 0.48, "Yxs": 0.50, "max_od": 12,
        "rpm": 600, "vvm": 1.5, "PV": 1500, "kLa": 220,
        "HD": 2.0, "Np": 5.0, "OUR": 15.0,
        "diameter": 0.10, "aspect": 2.0,
    },
    "Neuss et al. 2025 – CHO mAb (OTRmax)": {
        "V": 0.05, "mu": 0.032, "Yxs": 0.15, "max_od": 8,
        "rpm": 250, "vvm": 0.5, "PV": 500, "kLa": 50,
        "HD": 1.5, "Np": 3.0, "OUR": 3.0,
        "diameter": 0.04, "aspect": 1.5,
    },
    "Mohanty et al. 2025 – E. coli Endo H": {
        "V": 0.25, "mu": 0.65, "Yxs": 0.40, "max_od": 114,
        "rpm": 200, "vvm": 1.0, "PV": 800, "kLa": 120,
        "HD": 1.8, "Np": 5.0, "OUR": 20.0,
        "diameter": 0.08, "aspect": 1.8,
    },
    "P. pastoris HFBI 2025 – Methanol induction": {
        "V": 0.05, "mu": 0.18, "Yxs": 0.35, "max_od": 25,
        "rpm": 250, "vvm": 1.0, "PV": 600, "kLa": 80,
        "HD": 1.5, "Np": 3.0, "OUR": 8.0,
        "diameter": 0.04, "aspect": 1.5,
    },
    "Custom / From Analysis": None,
}


class ScaleUpVisualizer:
    """Create plotly dashboard figures for scale-up results."""

    @staticmethod
    def create_scale_up_dashboard(results_df, mu_lab=None, kLa_req=None):
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("μ_max vs Scale", "kLa vs Scale",
                            "Mixing Time vs Scale", "Tip Speed vs Scale"))

        vols = results_df["Volume_L"].tolist()

        fig.add_trace(go.Scatter(
            x=vols, y=results_df["mu_max_h"],
            mode="lines+markers", name="μ_max",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=10)), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=vols, y=results_df["kLa_h"],
            mode="lines+markers", name="kLa predicted",
            line=dict(color="#2ca02c", width=3),
            marker=dict(size=10)), row=1, col=2)
        if kLa_req:
            fig.add_hline(y=kLa_req, line_dash="dash", line_color="red",
                          annotation_text=f"kLa required = {kLa_req:.0f} h⁻¹",
                          row=1, col=2)

        fig.add_trace(go.Scatter(
            x=vols, y=results_df["tm_s"],
            mode="lines+markers", name="Mixing time",
            line=dict(color="#ff7f0e", width=3),
            marker=dict(size=10)), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=vols, y=results_df["Tip_Speed_m_s"],
            mode="lines+markers", name="Tip speed",
            line=dict(color="#d62728", width=3),
            marker=dict(size=10)), row=2, col=2)
        # Shear threshold
        fig.add_hline(y=5.0, line_dash="dot", line_color="gray",
                      annotation_text="Shear limit (5 m/s)", row=2, col=2)

        for row in [1, 2]:
            for col in [1, 2]:
                fig.update_xaxes(type="log", title_text="Volume (L)",
                                 row=row, col=col)
        fig.update_yaxes(title_text="μ_max (h⁻¹)", row=1, col=1)
        fig.update_yaxes(title_text="kLa (h⁻¹)", row=1, col=2)
        fig.update_yaxes(title_text="Mix time (s)", row=2, col=1)
        fig.update_yaxes(title_text="Tip speed (m/s)", row=2, col=2)
        fig.update_layout(height=650, showlegend=False,
                          margin=dict(t=40, b=20))
        return fig

    @staticmethod
    def create_criteria_comparison(lab_params, target_volume, engine):
        criteria = ["power_per_volume", "tip_speed", "kLa"]
        labels = {
            "power_per_volume": "Constant P/V",
            "tip_speed": "Constant Tip Speed",
            "kLa": "Constant kLa",
        }
        rows = []
        for crit in criteria:
            r = engine.calculate_scale_up(lab_params, target_volume, crit)
            rows.append({
                "Criterion": labels[crit],
                "μ_max (h⁻¹)": r["biological_performance"]["mu_max_h"],
                "Agitation (rpm)": r["operational_parameters"]["agitation_rpm"],
                "Tip Speed (m/s)": r["operational_parameters"]["tip_speed_m_s"],
                "P/V (W/m³)": r["operational_parameters"]["power_per_volume_W_m3"],
                "kLa (h⁻¹)": r["oxygen_transfer"]["kLa_predicted_h"],
                "Mix time (s)": r["operational_parameters"]["mixing_time_s"],
            })
        return pd.DataFrame(rows)


def _render_from_run():
    """Operating-window check of the loaded run in a target vessel."""
    from modules import process_scaleup as ps
    from modules.calcs import compute_growth_kinetics

    df = st.session_state.get("run_data")
    if df is None:
        st.info("Load a run in **Data Import** to scale up from its own data, "
                "or use the Quick / Advanced modes with literature presets.")
        return
    cm = st.session_state.get("col_map", {})
    cols = list(df.columns)
    num = lambda c: pd.to_numeric(df[c], errors="coerce").to_numpy(dtype=float)

    st.caption("Uses this run's growth rate, biomass and oxygen demand to check whether a "
               "target vessel can supply O₂, remove heat and mix fast enough.")
    with st.expander("Run data", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        tcol = c1.selectbox("Time (h)", cols, index=cols.index(cm["time"]) if cm.get("time") in cols else 0,
                            key="sr_t")
        odcol = c2.selectbox("OD₆₀₀", cols, index=cols.index(cm["od"]) if cm.get("od") in cols else 0,
                             key="sr_od")
        dcw = c3.number_input("OD→DCW (g/L per OD)", 0.1, 2.0, 0.40, 0.01, key="sr_dcw")
        none = "— none —"
        guess = next((c for c in cols if "our" in c.lower()), none)
        ourcol = c4.selectbox("OUR (mmol/L/h)", [none] + cols, index=([none] + cols).index(guess),
                              key="sr_our")

    t, od = num(tcol), num(odcol)
    ok = np.isfinite(t) & np.isfinite(od)
    gk = compute_growth_kinetics(t[ok], od[ok], dcw)
    if not gk.get("mu"):
        st.warning("No exponential phase found in the OD data.")
        return
    fr = st.session_state.get("flux_result") or {}
    q_flux = None
    for row in fr.get("fluxes", []):
        if row.get("Reaction") == "O2 uptake":
            q_flux = abs(row["Flux"])
    sources = (["Measured OUR ÷ biomass"] if ourcol != none else []) + \
              (["Flux Analysis result"] if q_flux else []) + ["Typical yield (Y_X/O ≈ 1 g/g)"]
    src = st.radio("O₂ demand from", sources, horizontal=True, key="sr_src")
    proc = ps.process_from_run(
        t, od, gk["mu"], dcw,
        our=num(ourcol) if (ourcol != none and src.startswith("Measured")) else None,
        q_o2=q_flux if src.startswith("Flux") else None,
        window=(float(gk["exp_t"][0]), float(gk["exp_t"][-1])))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("μ", f"{proc.mu_h:.3f} h⁻¹")
    m2.metric("q_O₂", f"{proc.q_o2:.1f} mmol/g/h", help=proc.source)
    m3.metric("Biomass reached", f"{proc.x_max_gL:.2f} g/L")
    m4.metric("Peak OUR (run)", f"{proc.our_peak:.1f} mmol/L/h")

    with st.expander("Target vessel", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        V = c1.number_input("Working volume (L)", 1.0, 500000.0, 1000.0, 100.0, key="sr_V")
        x_t = c2.number_input("Target biomass (g DCW/L)", 0.1, 200.0,
                              float(round(max(proc.x_max_gL, 0.1), 2)), 1.0, key="sr_xt",
                              help="Biomass the scaled process should reach — raise it to "
                                   "test a high-cell-density fed-batch.")
        hd = c3.number_input("H/D", 0.8, 4.0, 2.5, 0.1, key="sr_hd")
        imp = c4.selectbox("Impellers", ["Rushton (Np 5.0)", "Pitched blade (Np 1.3)",
                                         "Hydrofoil (Np 0.6)"], key="sr_imp")
        Np = {"Rushton": 5.0, "Pitched": 1.3, "Hydrofoil": 0.6}[imp.split()[0]]
        c1, c2, c3, c4 = st.columns(4)
        n_imp = c1.number_input("Number of impellers", 1, 6, 2, key="sr_ni")
        vvm = c2.number_input("Aeration (vvm)", 0.1, 3.0, 1.0, 0.1, key="sr_vvm")
        do = c3.number_input("DO setpoint (%)", 5.0, 80.0, 30.0, 5.0, key="sr_do")
        pv_max = c4.number_input("Max gassed P/V (W/m³)", 200.0, 20000.0, 3000.0, 250.0, key="sr_pv")
        c1, c2, c3, c4 = st.columns(4)
        tip_max = c1.number_input("Max tip speed (m/s)", 1.0, 10.0, 6.0, 0.5, key="sr_tip")
        bar = c2.number_input("Back-pressure (bar g)", 0.0, 2.0, 0.0, 0.1, key="sr_bar")
        o2f = c3.number_input("Inlet O₂ fraction", 0.21, 1.0, 0.21, 0.05, key="sr_o2")
        coal = c4.selectbox("Broth", ["Coalescing (conservative)", "Non-coalescing (salts)"],
                            key="sr_coal").startswith("Coal")
        c1, c2 = st.columns(2)
        U = c1.number_input("Jacket U (W/m²K)", 100.0, 1500.0, 400.0, 50.0, key="sr_U")
        tc = c2.number_input("Coolant temperature (°C)", 2.0, 30.0, 15.0, 1.0, key="sr_tc")

    vessel = ps.Vessel(volume_L=V, hd=hd, Np=Np, n_imp=int(n_imp), vvm=vvm,
                       max_PV_W_m3=pv_max, max_tip_m_s=tip_max, do_setpoint_pct=do,
                       head_pressure_bar_g=bar, o2_fraction=o2f, U_W_m2K=U,
                       coolant_C=tc, coalescing=coal)
    r = ps.evaluate(proc, vessel, x_t)

    st.subheader(f"Verdict at {V:,.0f} L")
    for sev, msg in r["verdict"]:
        {"ok": st.success, "warn": st.warning, "fail": st.error}[sev](msg)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("kLa required / max", f"{r['kLa required (h⁻¹)']:.0f} / {r['kLa max achievable (h⁻¹)']:.0f} h⁻¹")
    k2.metric("Max biomass before O₂ limit", f"{r['Max biomass before O₂ limitation (g/L)']:.1f} g/L")
    k3.metric("Agitation required / max", f"{r['Agitation required (rpm)']:.0f} / {r['Agitation max (rpm)']:.0f} rpm")
    k4.metric("Fed-batch μ max at target X", f"{r['Fed-batch μ max at target X (h⁻¹)']:.3f} h⁻¹")

    vols = sorted({v for v in [1, 10, 100, 1000, 10000, 100000] if v <= max(V * 10, 10)} | {V})
    scan = pd.DataFrame(ps.scan_volumes(proc, vessel, vols, x_t))
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Oxygen transfer", "Mixing vs O₂ depletion"))
    fig.add_trace(go.Scatter(x=scan["Volume (L)"], y=scan["kLa max achievable (h⁻¹)"],
                             name="kLa max achievable", mode="lines+markers"), 1, 1)
    fig.add_trace(go.Scatter(x=scan["Volume (L)"], y=scan["kLa required (h⁻¹)"],
                             name="kLa required", mode="lines+markers",
                             line=dict(dash="dash")), 1, 1)
    fig.add_trace(go.Scatter(x=scan["Volume (L)"], y=scan["Mixing time (s)"],
                             name="Mixing time", mode="lines+markers"), 1, 2)
    o2t = r["O₂ depletion time (s)"]
    fig.add_hline(y=o2t, line_dash="dot", annotation_text=f"O₂ depletion {o2t:.0f} s", row=1, col=2)
    fig.update_xaxes(type="log", title_text="Working volume (L)")
    fig.update_yaxes(title_text="h⁻¹", row=1, col=1)
    fig.update_yaxes(title_text="s", row=1, col=2)
    fig.update_layout(height=380, margin=dict(t=40, b=20), legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, width="stretch")

    with st.expander("All numbers"):
        detail = pd.DataFrame([{"Quantity": k, "Value": (f"{v:.3g}" if isinstance(v, float) else str(v))}
                               for k, v in r.items() if k not in ("verdict", "o2_ok", "heat_ok", "mix_ok")])
        st.dataframe(detail, hide_index=True, width="stretch")
        st.dataframe(scan.round(2), hide_index=True, width="stretch")
        st.download_button("⬇ Download scale-up scan (CSV)", scan.to_csv(index=False),
                           file_name=f"scaleup_{st.session_state.get('run_name') or 'run'}.csv")
    st.caption("kLa: van't Riet (1979); metabolic heat 460 kJ/mol O₂ (Cooney 1969); mixing "
               "time: Nienow (1997). q_O₂ is assumed proportional to μ (maintenance "
               "neglected) for the fed-batch limit.")


def render():
    st.title("🔬 Scale-up Model")
    st.caption("Predict performance at larger scales based on lab data.")

    # ── Auto-fill from current analysis (if available) ────────────────────
    mu_from_analysis = st.session_state.get("mu")
    yxs_from_analysis = st.session_state.get("yps")  # or yxs if stored
    od_from_analysis = None
    if st.session_state.get("run_data") is not None:
        _od_col = st.session_state.get("col_map", {}).get("od")
        if _od_col and _od_col in st.session_state.run_data.columns:
            od_from_analysis = float(st.session_state.run_data[_od_col].max())

    has_analysis = mu_from_analysis is not None

    # ── Mode selector: Quick (single target) or Advanced (multi-scale) ────
    mode = st.radio("Mode", ["🧪 From this run", "🚀 Quick Scale-Up", "🔧 Advanced Multi-Scale"],
                    horizontal=True, label_visibility="collapsed")
    if "From this run" in mode:
        _render_from_run()
        return

    # ── Literature preset ─────────────────────────────────────────────────
    preset = st.selectbox("Load reference dataset",
                          list(LITERATURE.keys()), key="su_preset")
    lit = LITERATURE.get(preset)

    # ── Lab-scale parameters ──────────────────────────────────────────────
    with st.expander("Lab-Scale Parameters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            lab_volume = st.number_input("Lab Volume (L)",
                value=float(lit["V"]) if lit else 2.5, step=0.5)
            lab_mu = st.number_input("μ_max (h⁻¹)", format="%.3f",
                value=float(mu_from_analysis) if has_analysis
                      else float(lit["mu"]) if lit else 0.45, step=0.01)
            lab_yield = st.number_input("Yield Yx/s (g/g)", format="%.3f",
                value=float(lit["Yxs"]) if lit else 0.42, step=0.01)
            lab_max_od = st.number_input("Max OD",
                value=float(od_from_analysis) if od_from_analysis
                      else float(lit["max_od"]) if lit else 8.5, step=0.5)
        with col2:
            lab_agitation = st.number_input("Agitation (rpm)",
                value=int(lit["rpm"]) if lit else 500, step=50)
            lab_aeration = st.number_input("Aeration (vvm)",
                value=float(lit["vvm"]) if lit else 1.0, step=0.1)
            lab_power = st.number_input("Power input (W/m³)",
                value=int(lit["PV"]) if lit else 1500, step=100)
            lab_kLa = st.number_input("kLa (h⁻¹)",
                value=int(lit["kLa"]) if lit else 200, step=20)
            lab_diameter = st.number_input("Vessel diameter (m)",
                value=float(lit.get("diameter", 0.15)) if lit else 0.15,
                step=0.01, format="%.3f")
            lab_aspect = st.number_input("Aspect ratio (H/D)",
                value=float(lit.get("aspect", 2.0)) if lit else 2.0, step=0.1)

    if has_analysis:
        st.info(f"Auto-filled from analysis: μ = {mu_from_analysis:.3f} h⁻¹"
                + (f", Max OD = {od_from_analysis:.1f}" if od_from_analysis else ""))

    # ── Build lab ScaleUpParameters ───────────────────────────────────────
    lab_params = ScaleUpParameters(
        volume_L=lab_volume,
        mu_max_h=lab_mu,
        yield_g_g=lab_yield,
        max_od=lab_max_od,
        agitation_rpm=float(lab_agitation),
        aeration_vvm=lab_aeration,
        power_input_W_m3=float(lab_power),
        kLa_h=float(lab_kLa),
        vessel_diameter_m=lab_diameter,
        impeller_diameter_m=lab_diameter * 0.33,
        aspect_ratio=lab_aspect,
        OUR=float(st.session_state.get("our_val", 8.5)),
    )
    engine = ScaleUpEngine()
    visualizer = ScaleUpVisualizer()

    # ══════════════════════════════════════════════════════════════════════
    #  QUICK MODE — single target volume
    # ══════════════════════════════════════════════════════════════════════
    if "Quick" in mode:
        scaling_criterion = st.selectbox("Scaling Criterion",
            ["power_per_volume", "tip_speed", "kLa"],
            format_func=lambda x: {
                "power_per_volume": "Constant Power per Volume (P/V)",
                "tip_speed": "Constant Tip Speed (shear-sensitive)",
                "kLa": "Constant kLa (oxygen-limited)",
            }[x])

        target_volume = st.number_input("Target Scale (L)",
                                         min_value=1, value=1000, step=100)

        if st.button("🔬 Calculate Scale-Up", type="primary"):
            with st.spinner("Calculating..."):
                result = engine.calculate_scale_up(
                    lab_params, float(target_volume), scaling_criterion)

            # ── Metrics row ──────────────────────────────────────────────
            st.subheader("📊 Scale-Up Predictions")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("μ_max",
                f"{result['biological_performance']['mu_max_h']:.3f} h⁻¹")
            c2.metric("Yield",
                f"{result['biological_performance']['yield_g_g']:.3f} g/g")
            c3.metric("Max OD",
                f"{result['biological_performance']['max_od']:.1f}")
            c4.metric("Scale Efficiency",
                f"{result['biological_performance']['scale_efficiency_percent']:.0f}%")

            c1, c2, c3 = st.columns(3)
            c1.metric("Agitation",
                f"{result['operational_parameters']['agitation_rpm']:.0f} rpm")
            c2.metric("Tip Speed",
                f"{result['operational_parameters']['tip_speed_m_s']:.1f} m/s")
            c3.metric("kLa",
                f"{result['oxygen_transfer']['kLa_predicted_h']:.0f} h⁻¹")

            # ── Risk assessment ──────────────────────────────────────────
            if result["risk_assessment"]:
                st.warning("⚠️ Risk Assessment")
                for risk in result["risk_assessment"]:
                    icon = {"High": "🔴", "Medium": "🟡",
                            "Low": "🟢"}.get(risk["severity"], "⚪")
                    st.markdown(f"{icon} **{risk['risk']}** "
                                f"(Severity: {risk['severity']})")
                    st.caption(f"→ {risk['mitigation']}")

            if result["recommendations"]:
                st.info("💡 Recommendations")
                for rec in result["recommendations"]:
                    st.markdown(f"- {rec}")

            # ── Multi-scale trend dashboard ──────────────────────────────
            st.markdown("---")
            st.subheader("📈 Scale-Up Trends")

            scales_to_plot = sorted(set(
                [s for s in [10, 100, 1000, 5000, 10000]
                 if s <= target_volume] + [target_volume]))

            results_df = engine.scale_multiple_sizes(
                lab_params, scales_to_plot, scaling_criterion)

            kLa_req = lab_params.OUR / (0.21 * 0.7) if lab_params.OUR > 0 else 200
            fig = visualizer.create_scale_up_dashboard(
                results_df, mu_lab=lab_mu, kLa_req=kLa_req)
            st.plotly_chart(fig, use_container_width=True)

            # ── Criteria comparison ──────────────────────────────────────
            with st.expander("Compare Scaling Criteria"):
                compare_df = visualizer.create_criteria_comparison(
                    lab_params, float(target_volume), engine)
                st.dataframe(compare_df, hide_index=True,
                             use_container_width=True)

            # ── Export ───────────────────────────────────────────────────
            st.markdown("---")
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Export Scale-Up Results as CSV",
                data=csv,
                file_name=f"scale_up_{target_volume}L.csv",
                mime="text/csv")

            st.session_state.scaleup_results = [result["_raw"]]

    # ══════════════════════════════════════════════════════════════════════
    #  ADVANCED MODE — multi-scale with vessel geometry per scale
    # ══════════════════════════════════════════════════════════════════════
    else:
        # Derived lab geometry
        HD_lab = lab_aspect
        Dt0 = lab_diameter
        N0 = float(lab_agitation) / 60.0
        Np = lab_params.Np
        OUR = lab_params.OUR
        cstar = lab_params.cstar
        do_sp = lab_params.DO_setpoint_percent
        Di0 = lab_params.impeller_diameter_m
        didt0 = Di0 / Dt0 if Dt0 > 0 else 0.33
        vvm_lab = lab_aeration

        criterion = st.selectbox("Scale-up criterion",
            ["Constant P/V", "Constant kLa", "Constant tip speed",
             "Constant Re", "Constant mixing time"])

        st.subheader("Target scales")
        n_scales = st.number_input("Number of scales", 1, 5, 3)
        scales = []
        cols = st.columns(int(n_scales))
        default_V = [10, 100, 1000, 5000, 10000]
        default_ni = [1, 2, 2, 3, 3]
        default_vvm = [1.0, 1.0, 0.8, 0.7, 0.6]
        for i, col in enumerate(cols):
            with col:
                st.caption(f"Scale {i + 1}")
                V = col.number_input("Volume (L)", 0.1, 100000.0,
                    float(default_V[min(i, 4)]), key=f"sv_{i}")
                HD = col.number_input("H/D ratio", 0.5, 5.0,
                    HD_lab, 0.1, key=f"hd_{i}")
                dd = col.number_input("Di/Dt", 0.1, 0.5,
                    round(didt0, 2), 0.01, key=f"dd_{i}")
                ni = col.number_input("# impellers", 1, 5,
                    default_ni[min(i, 4)], key=f"ni_{i}")
                vvm = col.number_input("vvm", 0.05, 5.0,
                    default_vvm[min(i, 4)], 0.05, key=f"vv_{i}")
                scales.append({"label": f"{V:.0f}L", "V": V, "HD": HD,
                                "dd": dd, "ni": ni, "vvm": vvm})

        if st.button("🔬 Compute Scale-Up", type="primary"):
            res_list = []
            for sc in scales:
                r = scaleup_vessel(sc["V"], sc["HD"], sc["dd"],
                    int(sc["ni"]), sc["vvm"], N0, Di0, criterion,
                    Np, OUR, cstar, do_sp, V0_L=lab_volume)
                r["label"] = sc["label"]
                r["V"] = sc["V"]
                res_list.append(r)

            # Lab reference
            lab_r = scaleup_vessel(lab_volume, HD_lab, didt0, 1, vvm_lab,
                N0, Di0, criterion, Np, OUR, cstar, do_sp, V0_L=lab_volume)
            lab_r["label"] = f"{lab_volume:.1f}L (lab)"
            lab_r["V"] = lab_volume
            all_r = [lab_r] + res_list
            st.session_state.scaleup_results = res_list

            # ── Engineering parameters table ─────────────────────────────
            st.subheader("Engineering Parameters")
            rows = []
            for r in all_r:
                rows.append({
                    "Scale": r["label"],
                    "Dt (m)": f"{r['Dt']:.3f}",
                    "Di (m)": f"{r['Di']:.3f}",
                    "H (m)": f"{r['H']:.3f}",
                    "N (rpm)": f"{r['N_rpm']:.0f}",
                    "Tip (m/s)": f"{r['tip']:.2f}",
                    "P/V (W/m³)": f"{r['PV']:.0f}",
                    "Q (L/min)": f"{r['Q_Lmin']:.1f}",
                    "Vs (m/s)": f"{r['Vs']:.4f}",
                    "kLa (h⁻¹)": f"{r['kLa']:.0f}",
                    "kLa req": f"{r['kLa_req']:.0f}",
                    "OTR": f"{r['OTR']:.1f}",
                    "tm (s)": f"{r['tm']:.1f}",
                    "Perf": f"{r['perf']:.3f}",
                    "OK": "✅" if r["kLa"] >= r["kLa_req"] else "❌",
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True,
                         use_container_width=True)

            # ── Biological performance ───────────────────────────────────
            st.subheader("Biological Performance Prediction")
            bio_rows = []
            for r in all_r:
                mu_s = lab_mu * r["mu_factor"]
                Yxs_s = lab_yield * r["Yxs_factor"]
                od_s = lab_max_od * r["od_factor"]
                bio_rows.append({
                    "Scale": r["label"],
                    "μ_max (h⁻¹)": f"{mu_s:.3f}",
                    "Yx/s (g/g)": f"{Yxs_s:.3f}",
                    "Max OD": f"{od_s:.1f}",
                    "Efficiency": f"{r['mu_factor']*100:.0f}%",
                })
            st.dataframe(pd.DataFrame(bio_rows), hide_index=True,
                         use_container_width=True)

            # ── 4-panel dashboard ────────────────────────────────────────
            st.subheader("Scale-Up Trends")
            vols = [r["V"] for r in all_r]
            dash_df = pd.DataFrame({
                "Volume_L": vols,
                "mu_max_h": [lab_mu * r["mu_factor"] for r in all_r],
                "kLa_h": [r["kLa"] for r in all_r],
                "tm_s": [r["tm"] for r in all_r],
                "Tip_Speed_m_s": [r["tip"] for r in all_r],
            })
            kLa_req = all_r[0]["kLa_req"]
            fig = visualizer.create_scale_up_dashboard(
                dash_df, mu_lab=lab_mu, kLa_req=kLa_req)
            st.plotly_chart(fig, use_container_width=True)

            # ── Performance factors ──────────────────────────────────────
            st.subheader("Performance Factors")
            fig2 = go.Figure()
            labels = [r["label"] for r in res_list]
            for metric, color, name in [("fo", "#1f77b4", "O₂ transfer"),
                                         ("fm", "#ff7f0e", "Mixing"),
                                         ("fc", "#2ca02c", "CO₂ removal")]:
                fig2.add_trace(go.Bar(x=labels,
                    y=[r[metric] for r in res_list], name=name,
                    marker_color=color))
            fig2.add_trace(go.Scatter(x=labels,
                y=[r["perf"] for r in res_list], name="Overall",
                mode="lines+markers", line=dict(color="black", width=2)))
            fig2.update_layout(height=320, barmode="group",
                yaxis_title="Factor (0–1)", yaxis=dict(range=[0, 1.1]),
                margin=dict(t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

            # ── Criteria comparison ──────────────────────────────────────
            largest = scales[-1]
            st.subheader(f"Criteria Comparison at {largest['label']}")
            crit_rows = []
            for crit_name in ["Constant P/V", "Constant kLa",
                              "Constant tip speed", "Constant Re",
                              "Constant mixing time"]:
                rc = scaleup_vessel(
                    largest["V"], largest["HD"], largest["dd"],
                    int(largest["ni"]), largest["vvm"], N0, Di0,
                    crit_name, Np, OUR, cstar, do_sp, V0_L=lab_volume)
                crit_rows.append({
                    "Criterion": crit_name,
                    "N (rpm)": f"{rc['N_rpm']:.0f}",
                    "Tip (m/s)": f"{rc['tip']:.2f}",
                    "P/V (W/m³)": f"{rc['PV']:.0f}",
                    "kLa (h⁻¹)": f"{rc['kLa']:.0f}",
                    "tm (s)": f"{rc['tm']:.1f}",
                    "Perf": f"{rc['perf']:.3f}",
                })
            st.dataframe(pd.DataFrame(crit_rows), hide_index=True,
                         use_container_width=True)

            # ── Risk assessment ──────────────────────────────────────────
            st.subheader("Risk Assessment & Recommendations")
            for r in res_list:
                if r["risks"]:
                    with st.expander(
                            f"⚠️ {r['label']} — {len(r['risks'])} risk(s)"):
                        for risk, severity, mitigation in r["risks"]:
                            icon = {"High": "🔴", "Medium": "🟡",
                                    "Low": "🟢"}.get(severity, "⚪")
                            st.markdown(f"{icon} **{risk}** ({severity})")
                            st.markdown(f"   → {mitigation}")
                else:
                    st.success(
                        f"✅ {r['label']} — No significant risks identified")

            if res_list and res_list[-1]["recommendations"]:
                st.markdown("**Recommendations for largest scale:**")
                for rec in res_list[-1]["recommendations"]:
                    st.markdown(f"- {rec}")

            # ── Export ───────────────────────────────────────────────────
            st.markdown("---")
            export_rows = []
            for r in all_r:
                export_rows.append({
                    "Scale": r["label"], "Volume_L": r["V"],
                    "Dt_m": r["Dt"], "Di_m": r["Di"], "H_m": r["H"],
                    "N_rpm": r["N_rpm"], "Tip_m_s": r["tip"],
                    "PV_W_m3": r["PV"], "kLa_h": r["kLa"],
                    "kLa_req_h": r["kLa_req"], "OTR": r["OTR"],
                    "tm_s": r["tm"], "perf": r["perf"],
                    "mu_factor": r["mu_factor"],
                    "Yxs_factor": r["Yxs_factor"],
                    "od_factor": r["od_factor"],
                })
            csv = pd.DataFrame(export_rows).to_csv(index=False)
            st.download_button(
                label="📥 Export Scale-Up Results as CSV",
                data=csv,
                file_name="scale_up_results.csv",
                mime="text/csv")
