"""Growth Kinetics — μ, doubling time, lag, productivity, Luedeking-Piret."""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.calcs import compute_growth_kinetics, compute_productivity, get_lit, BIOMASS_DB

def _get_col(df, cm, field):
    import pandas as pd
    # Try col_map first, then fall back to sensor_map
    col = cm.get(field)
    if not col or col not in df.columns:
        # sensor_map may have the same keys
        sensor_map = st.session_state.get("col_map", {})
        col = sensor_map.get(field)
    if col and col in df.columns:
        s = df[col].replace(["-", "--", "N/A", "n/a", "NA", "#VALUE!", ""], float("nan"))
        s = pd.to_numeric(s, errors="coerce").dropna()
        return s.to_numpy(dtype=float) if len(s) > 0 else None
    return None

def render():
    st.title("📈 Growth Kinetics")
    st.caption("μ · doubling time · lag · productivity · Luedeking–Piret LP model")

    df = st.session_state.run_data
    if df is None:
        st.info("No data loaded. Go to **Data Import** first.")
        return
    cm = st.session_state.col_map

    # ── Parameters ────────────────────────────────────────────────────────────
    with st.expander("Parameters", expanded=True):
        c1,c2,c3,c4 = st.columns(4)
        dcw_factor = c1.number_input("OD→DCW factor (g/L/OD)", 0.1, 2.0, 0.40, 0.05)
        organism   = c2.selectbox("Organism (for literature)", list(BIOMASS_DB.keys()))
        medium     = c3.selectbox("Medium",
            ["M9 minimal glucose","LB rich","Defined industrial","Terrific broth (TB)"])
        mode       = c4.selectbox("Mode", ["Batch","Fed-batch","Continuous"],
                                   index=["Batch","Fed-batch","Continuous"].index(st.session_state.run_mode))

    time_arr = _get_col(df, cm, "time")
    od_arr   = _get_col(df, cm, "od")
    prod_arr = _get_col(df, cm, "product")

    if time_arr is None or od_arr is None:
        st.warning("Time and OD columns not found. Check column mapping.")
        return

    n = min(len(time_arr), len(od_arr))
    time_arr = time_arr[:n]; od_arr = od_arr[:n]

    # ── Compute growth ────────────────────────────────────────────────────────
    gk = compute_growth_kinetics(time_arr, od_arr, dcw_factor)
    dcw = gk["dcw"]

    # ── Compute productivity ──────────────────────────────────────────────────
    pk = {}
    if prod_arr is not None:
        np_ = min(len(prod_arr), n)
        pk = compute_productivity(time_arr[:np_], prod_arr[:np_], dcw[:np_])

    # Push to session state
    if gk.get("mu"):          st.session_state.mu = gk["mu"]
    if pk.get("titer"):       st.session_state.titer = pk["titer"]
    if pk.get("sty"):         st.session_state.sty   = pk["sty"]

    # ── Literature comparison ─────────────────────────────────────────────────
    lit = get_lit(organism, medium)

    mu = gk.get("mu")

    # ── Growth regime badge ───────────────────────────────────────────────────
    if mu is not None:
        if mu >= 0.6:
            regime_icon, regime_label, regime_color, regime_desc = \
                "🚀", "FAST", "#d4edda", "Rich medium / optimal conditions"
        elif mu >= 0.3:
            regime_icon, regime_label, regime_color, regime_desc = \
                "🌱", "MEDIUM", "#fff3cd", "Minimal medium / standard growth"
        else:
            regime_icon, regime_label, regime_color, regime_desc = \
                "🐢", "SLOW", "#f8d7da", "Stress conditions / poor carbon source"
        st.markdown(
            f"<div style='background:{regime_color};border-radius:8px;padding:10px 16px;"
            f"margin-bottom:8px;font-size:1.05em'>"
            f"<b>{regime_icon} GROWTH REGIME: {regime_label}</b> &nbsp;·&nbsp; "
            f"μ_max = {mu:.3f} h⁻¹ &nbsp;·&nbsp; {regime_desc}</div>",
            unsafe_allow_html=True)

    # ── Fed-batch warning ─────────────────────────────────────────────────────
    if gk["max_od"] > 20:
        st.warning(
            f"**Fed-batch fermentation detected** — Max OD: {gk['max_od']:.1f}\n\n"
            "μ_max shown is from the **initial batch phase only**. "
            "Do not compare directly with batch fermentation values.",
            icon="⚠️")

    # ── KPI metrics ───────────────────────────────────────────────────────────
    st.subheader("Growth KPIs")
    c1,c2,c3,c4,c5 = st.columns(5)
    mu_se = gk.get("mu_se")
    ci_str = f"±{1.96*mu_se:.3f} (95% CI)" if mu_se else None
    c1.metric("μ (h⁻¹)", f"{mu:.3f}" if mu else "—",
              delta=ci_str if mu else f"lit {lit['mu_min']}–{lit['mu_max']}")
    td = gk.get("td_min")
    c2.metric("Doubling time (min)", f"{td:.0f}" if td else "—",
              delta=f"lit {lit['td_min']}–{lit['td_max']} min" if td else None)
    c3.metric("Lag time (h)", f"{gk['lag_h']:.1f}")
    r2 = gk.get("r2")
    c4.metric("R²", f"{r2:.4f}" if r2 else "—")
    c5.metric("Max OD₆₀₀", f"{gk['max_od']:.2f}")

    # ── Quality score ─────────────────────────────────────────────────────────
    qs = gk.get("quality_score")
    if qs is not None:
        if qs >= 90:
            qs_color, qs_label, qs_msg = "#28a745", "Excellent", "Results are publication-ready"
        elif qs >= 75:
            qs_color, qs_label, qs_msg = "#ffc107", "Good", "Acceptable for process monitoring"
        elif qs >= 60:
            qs_color, qs_label, qs_msg = "#fd7e14", "Fair", "Consider collecting more data"
        else:
            qs_color, qs_label, qs_msg = "#dc3545", "Poor", "Check data quality or phase selection"
        bar_pct = qs
        st.markdown(
            f"<div style='margin:6px 0 10px 0'>"
            f"<b>Fit quality score: {qs}% — {qs_label}</b> &nbsp; <span style='color:gray;font-size:0.9em'>{qs_msg}</span><br>"
            f"<div style='background:#e9ecef;border-radius:4px;height:12px;margin-top:4px'>"
            f"<div style='background:{qs_color};width:{bar_pct}%;height:12px;border-radius:4px'></div>"
            f"</div></div>",
            unsafe_allow_html=True)

    if pk:
        st.subheader("Productivity KPIs")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Titer (g/L)",   f"{pk.get('titer',0):.3f}")
        c2.metric("STY (g/L/h)",   f"{pk.get('sty',0):.4f}")
        c3.metric("Qp max (g/L/h)",f"{pk.get('qp_max',0):.4f}")
        if pk.get("lp_alpha") is not None:
            c4.metric("LP α", f"{pk['lp_alpha']:.4f}")

    # ── Growth plot with phase shading ───────────────────────────────────────
    st.subheader("Growth curve")

    # Determine phase boundaries
    lag_end  = gk.get("lag_h", 0.0)
    exp_t    = gk.get("exp_t", np.array([]))
    exp_end  = float(exp_t[-1]) if len(exp_t) >= 2 else float(time_arr[-1])
    t_start  = float(time_arr[0])
    t_end    = float(time_arr[-1])

    # Local instantaneous μ for hover
    mu_local = np.zeros(n)
    for _i in range(n):
        lo, hi = max(0, _i-1), min(n-1, _i+1)
        if hi > lo and dcw[lo] > 0 and dcw[hi] > 0:
            mu_local[_i] = max(np.log(dcw[hi]/dcw[lo]) / (time_arr[hi]-time_arr[lo]), 0)

    # Phase label per point
    def _phase(t_val):
        if t_val < lag_end:   return "Lag"
        if t_val <= exp_end:  return "Exponential"
        return "Stationary"
    phase_labels = [_phase(t_val) for t_val in time_arr]

    hover_text = [
        f"Time: {time_arr[k]:.2f} h<br>OD: {od_arr[k]:.3f}<br>"
        f"μ_local: {mu_local[k]:.3f} h⁻¹<br>Phase: {phase_labels[k]}"
        for k in range(n)
    ]

    fig = make_subplots(rows=1, cols=2, subplot_titles=("OD₆₀₀ linear", "OD₆₀₀ log-scale"))

    for col_idx, logy in enumerate([False, True], 1):
        # Phase shading (lag=blue, exp=green, stationary=gray) — linear plot only
        if not logy:
            y_max_shade = float(gk["max_od"]) * 1.05
            if lag_end > t_start:
                fig.add_shape(type="rect", x0=t_start, x1=lag_end, y0=0, y1=y_max_shade,
                    fillcolor="rgba(173,216,230,0.25)", line_width=0, row=1, col=col_idx)
            if exp_end > lag_end:
                fig.add_shape(type="rect", x0=lag_end, x1=exp_end, y0=0, y1=y_max_shade,
                    fillcolor="rgba(144,238,144,0.20)", line_width=0, row=1, col=col_idx)
            if t_end > exp_end:
                fig.add_shape(type="rect", x0=exp_end, x1=t_end, y0=0, y1=y_max_shade,
                    fillcolor="rgba(200,200,200,0.20)", line_width=0, row=1, col=col_idx)
            # Phase labels on x-axis area
            for x_pos, label, color in [
                ((t_start+min(lag_end,t_end))/2, "Lag", "#6699cc"),
                ((lag_end+exp_end)/2, "Exp", "#339933"),
                ((exp_end+t_end)/2, "Stat.", "#888888"),
            ]:
                if x_pos < t_end:
                    fig.add_annotation(x=x_pos, y=y_max_shade*0.97, text=label,
                        showarrow=False, font=dict(size=10, color=color),
                        xref="x", yref="y", row=1, col=col_idx)

        fig.add_trace(go.Scatter(
            x=time_arr, y=od_arr, mode="lines+markers",
            name="OD₆₀₀", line=dict(color="#1f77b4", width=2),
            marker=dict(size=6),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_text,
            showlegend=(col_idx==1)), row=1, col=col_idx)

        # Regression line in exp window
        if gk.get("bgr_sl") and len(exp_t) >= 2:
            t_fit = np.linspace(exp_t[0], exp_t[-1], 50)
            od_fit = np.exp(gk["bgr_sl"]*t_fit + gk["bgr_ic"])
            mu_val = gk.get("mu", 0)
            mu_se_val = gk.get("mu_se", 0)
            ci_lo = mu_val - 1.96*mu_se_val
            ci_hi = mu_val + 1.96*mu_se_val
            reg_hover = [
                f"μ_max: {mu_val:.3f} h⁻¹<br>95% CI: [{ci_lo:.3f}, {ci_hi:.3f}]<br>"
                f"R²: {gk.get('r2',0):.4f}<br>Points: {gk.get('n_exp',0)}"
            ] * len(t_fit)
            fig.add_trace(go.Scatter(
                x=t_fit, y=od_fit, mode="lines",
                name=f"Regression (μ={mu_val:.3f}±{1.96*mu_se_val:.3f})",
                line=dict(color="#2ca02c", dash="dash", width=1.5),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=reg_hover,
                showlegend=(col_idx==1)), row=1, col=col_idx)
        if logy:
            fig.update_yaxes(type="log", row=1, col=col_idx)

    # Phase duration annotation below plot
    lag_dur  = max(lag_end - t_start, 0)
    exp_dur  = max(exp_end - lag_end, 0)
    stat_dur = max(t_end - exp_end, 0)
    phase_info = (f"**Lag:** {lag_dur:.1f} h  |  **Exp:** {exp_dur:.1f} h  |  "
                  f"**Stationary:** {stat_dur:.1f} h")

    fig.update_layout(height=400, margin=dict(t=40,b=20), legend=dict(x=0.01,y=0.99))
    fig.update_xaxes(title_text="Time (h)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(phase_info)

    # ── Productivity plot ─────────────────────────────────────────────────────
    if pk and prod_arr is not None:
        st.subheader("Productivity profile")
        np_ = min(len(prod_arr), n)
        fig2 = make_subplots(rows=1, cols=2, subplot_titles=("Product titer & Qp", "Luedeking–Piret fit"))

        fig2.add_trace(go.Scatter(x=time_arr[:np_], y=prod_arr[:np_], mode="lines+markers",
            name="Product (g/L)", line=dict(color="#9467bd"), yaxis="y1"), row=1, col=1)
        fig2.add_trace(go.Scatter(x=time_arr[:np_], y=pk["qp"], mode="lines",
            name="Qp (g/L/h)", line=dict(color="#ff7f0e", dash="dot"), yaxis="y2"), row=1, col=1)

        if pk.get("lp_alpha") is not None:
            mu_loc2 = np.zeros(np_)
            for i in range(np_):
                lo,hi = max(0,i-1),min(np_-1,i+1)
                if hi>lo and dcw[lo]>0 and dcw[hi]>0:
                    mu_loc2[i] = max(np.log(dcw[hi]/dcw[lo])/(time_arr[hi]-time_arr[lo]),0)
            sp = pk.get("sp", np.zeros(np_))[:np_]
            mu_fit = np.linspace(0, max(mu_loc2)*1.1, 50)
            sp_fit = pk["lp_alpha"]*mu_fit + pk["lp_beta"]
            fig2.add_trace(go.Scatter(x=mu_loc2[:np_], y=sp[:np_], mode="markers",
                name="Data", marker=dict(color="#1f77b4", size=6)), row=1, col=2)
            fig2.add_trace(go.Scatter(x=mu_fit, y=sp_fit, mode="lines",
                name=f"LP fit (α={pk['lp_alpha']:.3f}, β={pk['lp_beta']:.4f})",
                line=dict(color="#d62728")), row=1, col=2)
            fig2.update_xaxes(title_text="μ_local (h⁻¹)", row=1, col=2)
            fig2.update_yaxes(title_text="qp (g/g/h)", row=1, col=2)

        fig2.update_layout(height=350, margin=dict(t=40,b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Literature comparison table ───────────────────────────────────────────
    st.subheader("Literature comparison")
    import pandas as pd
    rows = []
    if mu:
        status = "✅" if lit["mu_min"] <= mu <= lit["mu_max"] else "⚠️"
        rows.append({"Parameter":"μ (h⁻¹)","Measured":f"{mu:.3f}","Literature":f"{lit['mu_min']}–{lit['mu_max']}","Status":status})
    if td:
        status = "✅" if lit["td_min"] <= td <= lit["td_max"] else "⚠️"
        rows.append({"Parameter":"t_d (min)","Measured":f"{td:.0f}","Literature":f"{lit['td_min']}–{lit['td_max']}","Status":status})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
