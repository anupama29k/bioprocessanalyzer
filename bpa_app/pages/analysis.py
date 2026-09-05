"""Analysis — combined growth, substrate, product and all sensor profiles."""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.calcs import compute_growth_kinetics, compute_productivity, get_lit, BIOMASS_DB

COLORS = {
    "od": "#1f77b4", "substrate": "#2ca02c", "product": "#9467bd",
    "acetate": "#ff7f0e", "ph": "#8c564b", "do": "#17becf",
    "temp": "#e377c2", "rpm": "#bcbd22",
}


def _arr(df, cm, *fields):
    """Return numpy array for the first field key that is mapped and has ≥2 values."""
    for f in fields:
        col = cm.get(f)
        if col and col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(s) >= 2:
                return s.to_numpy(dtype=float)
    return None


def _phase(t_val, lag_end, exp_end):
    if t_val < lag_end:  return "Lag"
    if t_val <= exp_end: return "Exponential"
    return "Stationary"


def render():
    st.title("📊 Analysis")
    st.caption("Growth kinetics · Substrate & yield · Product & productivity · All sensor profiles")

    df = st.session_state.run_data
    cm = st.session_state.col_map
    if df is None:
        st.info("No data loaded. Go to **Data Import** first.")
        return

    # ── Parameters ────────────────────────────────────────────────────────────
    with st.expander("⚙️ Parameters", expanded=False):
        c1, c2, c3 = st.columns(3)
        dcw_f    = c1.number_input("OD→DCW factor (g/L/OD)", 0.1, 2.0, 0.40, 0.05)
        organism = c2.selectbox("Organism (for literature)", list(BIOMASS_DB.keys()))
        medium   = c3.selectbox("Medium",
            ["M9 minimal glucose", "LB rich", "Defined industrial", "Terrific broth (TB)"])

    # ── Fetch arrays ──────────────────────────────────────────────────────────
    time_arr = _arr(df, cm, "time")
    od_arr   = _arr(df, cm, "od")
    sub_arr  = _arr(df, cm, "substrate", "glucose")
    prod_arr = _arr(df, cm, "product")
    ph_arr   = _arr(df, cm, "ph")
    do_arr   = _arr(df, cm, "do")
    temp_arr = _arr(df, cm, "temp")
    rpm_arr  = _arr(df, cm, "rpm")

    if time_arr is None or od_arr is None:
        st.warning("Time and OD/Biomass columns not mapped. Check **Column Mapping** in the sidebar.")
        return

    n        = min(len(time_arr), len(od_arr))
    time_arr = time_arr[:n]
    od_arr   = od_arr[:n]

    # ── Compute ───────────────────────────────────────────────────────────────
    gk  = compute_growth_kinetics(time_arr, od_arr, dcw_f)
    dcw = gk["dcw"]
    lit = get_lit(organism, medium)

    pk = {}
    if prod_arr is not None:
        np_ = min(len(prod_arr), n)
        pk = compute_productivity(time_arr[:np_], prod_arr[:np_], dcw[:np_])

    # Push KPIs to sidebar
    if gk.get("mu"):    st.session_state.mu    = gk["mu"]
    if pk.get("titer"): st.session_state.titer = pk["titer"]
    if pk.get("sty"):   st.session_state.sty   = pk["sty"]

    mu     = gk.get("mu")
    mu_se  = gk.get("mu_se", 0.0)
    r2     = gk.get("r2")
    td     = gk.get("td_min")
    lag    = gk.get("lag_h", 0.0)
    max_od = gk.get("max_od", 0.0)
    qs     = gk.get("quality_score")
    n_exp  = gk.get("n_exp", 0)
    exp_t  = gk.get("exp_t", np.array([]))
    t_start, t_end = float(time_arr[0]), float(time_arr[-1])
    lag_end = lag
    exp_end = float(exp_t[-1]) if len(exp_t) >= 2 else t_end

    # ── Growth regime badge ───────────────────────────────────────────────────
    if mu is not None:
        if mu >= 0.6:
            r_icon, r_label, r_bg, r_desc = "🚀", "FAST",   "#d4edda", "Rich medium / optimal conditions"
        elif mu >= 0.3:
            r_icon, r_label, r_bg, r_desc = "🌱", "MEDIUM", "#fff3cd", "Minimal medium / standard growth"
        else:
            r_icon, r_label, r_bg, r_desc = "🐢", "SLOW",   "#f8d7da", "Stress / poor carbon source"
        st.markdown(
            f"<div style='background:{r_bg};border-radius:8px;padding:10px 16px;"
            f"margin-bottom:8px;font-size:1.05em'>"
            f"<b>{r_icon} GROWTH REGIME: {r_label}</b> &nbsp;·&nbsp; "
            f"μ_max = {mu:.3f} h⁻¹ &nbsp;·&nbsp; {r_desc}</div>",
            unsafe_allow_html=True)

    if max_od > 20:
        st.warning(
            f"**Fed-batch detected** — Max OD {max_od:.1f}. "
            "μ_max is from the initial batch phase only.", icon="⚠️")

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1: PROCESS PROFILES
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("Process Profiles")

    # Local instantaneous μ for hover tooltips
    mu_loc = np.zeros(n)
    for i in range(n):
        lo, hi = max(0, i-1), min(n-1, i+1)
        if hi > lo and dcw[lo] > 0 and dcw[hi] > 0:
            mu_loc[i] = max(np.log(dcw[hi] / dcw[lo]) / (time_arr[hi] - time_arr[lo]), 0)

    hover = [
        f"Time: {time_arr[k]:.2f} h<br>OD: {od_arr[k]:.3f}<br>"
        f"μ_local: {mu_loc[k]:.3f} h⁻¹<br>Phase: {_phase(time_arr[k], lag_end, exp_end)}"
        for k in range(n)
    ]

    # OD plots (linear + log)
    fig_od = make_subplots(rows=1, cols=2,
        subplot_titles=("OD₆₀₀ — linear", "OD₆₀₀ — log scale"))

    for ci, logy in enumerate([False, True], 1):
        if not logy:
            y_top = max_od * 1.05
            for x0, x1, fill in [
                (t_start, lag_end,  "rgba(173,216,230,0.25)"),
                (lag_end, exp_end,  "rgba(144,238,144,0.20)"),
                (exp_end, t_end,    "rgba(200,200,200,0.20)"),
            ]:
                if x1 > x0:
                    fig_od.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=y_top,
                        fillcolor=fill, line_width=0, row=1, col=ci)
            for x_pos, label, color in [
                ((t_start + min(lag_end, t_end)) / 2, "Lag",  "#6699cc"),
                ((lag_end + exp_end) / 2,              "Exp",  "#339933"),
                ((exp_end + t_end) / 2,                "Stat.","#888888"),
            ]:
                if t_start < x_pos < t_end:
                    fig_od.add_annotation(x=x_pos, y=y_top * 0.96, text=label,
                        showarrow=False, font=dict(size=10, color=color), row=1, col=ci)

        fig_od.add_trace(go.Scatter(
            x=time_arr, y=od_arr, mode="lines+markers", name="OD₆₀₀",
            line=dict(color=COLORS["od"], width=2), marker=dict(size=5),
            hovertemplate="%{customdata}<extra></extra>", customdata=hover,
            showlegend=(ci == 1)), row=1, col=ci)

        if gk.get("bgr_sl") and len(exp_t) >= 2:
            t_fit  = np.linspace(exp_t[0], exp_t[-1], 60)
            od_fit = np.exp(gk["bgr_sl"] * t_fit + gk["bgr_ic"])
            ci_lo  = mu - 1.96 * mu_se
            ci_hi  = mu + 1.96 * mu_se
            rh = [f"μ_max={mu:.3f} h⁻¹  95%CI=[{ci_lo:.3f},{ci_hi:.3f}]<br>R²={r2:.4f}  n={n_exp}"] * len(t_fit)
            fig_od.add_trace(go.Scatter(
                x=t_fit, y=od_fit, mode="lines",
                name=f"Regression μ={mu:.3f}",
                line=dict(color="#2ca02c", dash="dash", width=1.5),
                hovertemplate="%{customdata}<extra></extra>", customdata=rh,
                showlegend=(ci == 1)), row=1, col=ci)

        if logy:
            fig_od.update_yaxes(type="log", row=1, col=ci)

    fig_od.update_layout(height=360, margin=dict(t=40, b=10),
                         legend=dict(x=0.01, y=0.99))
    fig_od.update_xaxes(title_text="Time (h)")
    st.plotly_chart(fig_od, use_container_width=True)
    lag_dur = max(lag_end - t_start, 0)
    exp_dur = max(exp_end - lag_end, 0)
    st.caption(f"**Lag:** {lag_dur:.1f} h  |  **Exponential:** {exp_dur:.1f} h  |"
               f"  **Stationary:** {max(t_end - exp_end, 0):.1f} h")

    # Substrate + product profiles
    met_cols = []
    if sub_arr  is not None: met_cols.append(("Substrate (g/L)", sub_arr,  COLORS["substrate"]))
    if prod_arr is not None: met_cols.append(("Product (g/L)",   prod_arr, COLORS["product"]))

    if met_cols:
        fig_met = make_subplots(rows=1, cols=len(met_cols),
            subplot_titles=[m[0] for m in met_cols])
        for ci, (title, arr, color) in enumerate(met_cols, 1):
            nm = min(len(arr), n)
            fig_met.add_trace(go.Scatter(
                x=time_arr[:nm], y=arr[:nm], mode="lines+markers",
                name=title, line=dict(color=color, width=2), marker=dict(size=5),
                showlegend=False), row=1, col=ci)
        fig_met.update_layout(height=250, margin=dict(t=40, b=10))
        fig_met.update_xaxes(title_text="Time (h)")
        st.plotly_chart(fig_met, use_container_width=True)

    # Environmental sensors (pH, DO, temp, rpm)
    env_traces = []
    if ph_arr   is not None: env_traces.append(("pH",        ph_arr,   COLORS["ph"]))
    if do_arr   is not None: env_traces.append(("DO (%)",    do_arr,   COLORS["do"]))
    if temp_arr is not None: env_traces.append(("Temp (°C)", temp_arr, COLORS["temp"]))
    if rpm_arr  is not None: env_traces.append(("RPM",       rpm_arr,  COLORS["rpm"]))

    if env_traces:
        fig_env = go.Figure()
        for label, arr, color in env_traces:
            nm = min(len(arr), n)
            fig_env.add_trace(go.Scatter(
                x=time_arr[:nm], y=arr[:nm], mode="lines",
                name=label, line=dict(color=color, width=2)))
        fig_env.update_layout(height=220, margin=dict(t=10, b=10),
                               xaxis_title="Time (h)",
                               legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig_env, use_container_width=True)

    # Any other mapped sensors not yet plotted
    skip_keys = {"time", "od", "substrate", "glucose", "product",
                 "ph", "do", "temp", "rpm", "dcm", "vcd"}
    extra = {k: v for k, v in cm.items()
             if k not in skip_keys and v and v in df.columns}
    if extra:
        with st.expander(f"➕ Additional mapped sensors ({len(extra)})", expanded=False):
            figs_ex = []
            for key, col in extra.items():
                arr = pd.to_numeric(df[col], errors="coerce").dropna().to_numpy(dtype=float)
                if len(arr) >= 2:
                    figs_ex.append((col, arr))
            if figs_ex:
                fig_all = go.Figure()
                for col, arr in figs_ex:
                    nm = min(len(arr), n)
                    fig_all.add_trace(go.Scatter(
                        x=time_arr[:nm], y=arr[:nm], mode="lines+markers",
                        name=col, line=dict(width=1.5), marker=dict(size=4)))
                fig_all.update_layout(height=280, margin=dict(t=10, b=10),
                                      xaxis_title="Time (h)",
                                      legend=dict(orientation="h", y=-0.3))
                st.plotly_chart(fig_all, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2: GROWTH CALCULATIONS
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("Growth Calculations")

    # Quality score bar
    if qs is not None:
        if qs >= 90:   qc, ql, qm = "#28a745", "Excellent", "Publication-ready"
        elif qs >= 75: qc, ql, qm = "#ffc107", "Good",      "Acceptable for process monitoring"
        elif qs >= 60: qc, ql, qm = "#fd7e14", "Fair",      "Consider collecting more data"
        else:          qc, ql, qm = "#dc3545", "Poor",      "Check data quality / phase selection"
        st.markdown(
            f"<div style='margin:0 0 12px 0'>"
            f"<b>Fit quality: {qs}% — {ql}</b>  "
            f"<span style='color:gray;font-size:0.9em'>{qm}</span><br>"
            f"<div style='background:#e9ecef;border-radius:4px;height:10px;margin-top:4px'>"
            f"<div style='background:{qc};width:{qs}%;height:10px;border-radius:4px'></div>"
            f"</div></div>", unsafe_allow_html=True)

    ci_str = f"±{1.96*mu_se:.3f}" if mu_se else None
    exp_dur_v = max(exp_end - max(lag_end, t_start), 0)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("μ_max (h⁻¹)",      f"{mu:.3f}"    if mu    else "—", delta=ci_str)
    c2.metric("Doubling time",    f"{td:.0f} min" if td    else "—",
              delta=f"lit {lit['td_min']}–{lit['td_max']} min" if td else None)
    c3.metric("Lag phase (h)",    f"{lag:.1f}")
    c4.metric("Exp phase (h)",    f"{exp_dur_v:.1f}")
    c5.metric("Max OD₆₀₀",       f"{max_od:.2f}")
    c6.metric("Max DCW (g/L)",    f"{gk.get('max_dcw', 0):.2f}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R²",              f"{r2:.4f}" if r2   else "—",
              delta=f"lit μ {lit['mu_min']}–{lit['mu_max']}" if mu else None)
    c2.metric("Exp-phase points", str(n_exp) if n_exp else "—")
    if mu and mu_se:
        c3.metric("95% CI",      f"[{mu-1.96*mu_se:.3f}, {mu+1.96*mu_se:.3f}]")
    c4.metric("Total data pts",   str(n))

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3: SUBSTRATE & YIELD
    # ─────────────────────────────────────────────────────────────────────────
    if sub_arr is not None:
        st.subheader("Substrate & Yield")
        ns   = min(len(sub_arr), n)
        tail = max(1, ns // 10)
        s0   = float(np.nanmedian(sub_arr[:max(1, ns // 10)]))
        sf   = float(np.nanmedian(sub_arr[ns - tail:]))
        ds   = max(s0 - sf, 1e-9)
        dx   = float(dcw[ns - 1] - dcw[0]) if ns > 1 else 0.0
        yxs  = dx / ds if ds > 0 else None

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("S₀ (initial g/L)", f"{s0:.2f}")
        c2.metric("Sf (final g/L)",   f"{sf:.2f}")
        c3.metric("ΔS consumed (g/L)",f"{ds:.2f}")
        c4.metric("Yx/s (g DCW/g S)", f"{yxs:.3f}" if yxs else "—")
    else:
        ds = None
        yxs = None

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4: PRODUCT & PRODUCTIVITY
    # ─────────────────────────────────────────────────────────────────────────
    if prod_arr is not None and pk:
        st.subheader("Product & Productivity")
        np_ = min(len(prod_arr), n)
        dp  = max(float(prod_arr[np_ - 1]) - float(prod_arr[0]), 0)
        yps = (dp / ds) if (ds and ds > 0) else None

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Titer (g/L)",     f"{pk.get('titer', 0):.3f}")
        c2.metric("STY (g/L/h)",     f"{pk.get('sty', 0):.4f}")
        c3.metric("Qp_max (g/L/h)",  f"{pk.get('qp_max', 0):.4f}")
        c4.metric("Yp/s (g prod/g S)", f"{yps:.4f}" if yps else "—")
        if pk.get("lp_alpha") is not None:
            c5.metric("LP α",        f"{pk['lp_alpha']:.4f}")

        # Product titer + Qp + LP model
        fig_p = make_subplots(rows=1, cols=2 if pk.get("lp_alpha") is not None else 1,
            subplot_titles=(["Product titer & Qp", "Luedeking–Piret fit"]
                            if pk.get("lp_alpha") is not None else ["Product titer & Qp"]))

        fig_p.add_trace(go.Scatter(
            x=time_arr[:np_], y=prod_arr[:np_], mode="lines+markers",
            name="Product (g/L)", line=dict(color=COLORS["product"])), row=1, col=1)
        fig_p.add_trace(go.Scatter(
            x=time_arr[:np_], y=pk["qp"], mode="lines",
            name="Qp (g/L/h)", line=dict(color=COLORS["acetate"], dash="dot")), row=1, col=1)

        if pk.get("lp_alpha") is not None:
            mu_loc2 = np.zeros(np_)
            for i in range(np_):
                lo, hi = max(0, i-1), min(np_-1, i+1)
                if hi > lo and dcw[lo] > 0 and dcw[hi] > 0:
                    mu_loc2[i] = max(np.log(dcw[hi] / dcw[lo]) / (time_arr[hi] - time_arr[lo]), 0)
            sp_arr  = pk.get("sp", np.zeros(np_))[:np_]
            mu_fit  = np.linspace(0, max(mu_loc2) * 1.1, 50)
            sp_fit  = pk["lp_alpha"] * mu_fit + pk["lp_beta"]
            fig_p.add_trace(go.Scatter(x=mu_loc2[:np_], y=sp_arr[:np_],
                mode="markers", name="Data", marker=dict(color=COLORS["od"], size=6)), row=1, col=2)
            fig_p.add_trace(go.Scatter(x=mu_fit, y=sp_fit, mode="lines",
                name=f"LP fit (α={pk['lp_alpha']:.3f}, β={pk['lp_beta']:.4f})",
                line=dict(color="#d62728")), row=1, col=2)
            fig_p.update_xaxes(title_text="μ_local (h⁻¹)", row=1, col=2)
            fig_p.update_yaxes(title_text="qp (g/g/h)", row=1, col=2)

        fig_p.update_layout(height=300, margin=dict(t=40, b=10))
        fig_p.update_xaxes(title_text="Time (h)", row=1, col=1)
        st.plotly_chart(fig_p, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 5: LITERATURE COMPARISON
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("Literature Comparison")
    lit_rows = []
    if mu:
        lit_rows.append({
            "Parameter": "μ (h⁻¹)",
            "Measured": f"{mu:.3f}",
            "Literature": f"{lit['mu_min']}–{lit['mu_max']}",
            "Status": "✅" if lit["mu_min"] <= mu <= lit["mu_max"] else "⚠️",
        })
    if td:
        lit_rows.append({
            "Parameter": "t_d (min)",
            "Measured": f"{td:.0f}",
            "Literature": f"{lit['td_min']}–{lit['td_max']}",
            "Status": "✅" if lit["td_min"] <= td <= lit["td_max"] else "⚠️",
        })
    if lit_rows:
        st.dataframe(pd.DataFrame(lit_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Set organism and medium in Parameters to see literature comparison.")
