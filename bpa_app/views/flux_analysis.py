"""Flux Analysis — genome-scale FBA constrained by the run's measured rates."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.calcs import compute_growth_kinetics
from modules import flux

PATHWAY_ORDER = ["Uptake", "Glycolysis", "Pentose phosphate", "Pyruvate node",
                 "Fermentation", "Overflow (acetate)", "PDH bypass", "Redox balance",
                 "TCA cycle", "Glyoxylate shunt", "Anaplerosis", "Energy", "Exchange"]


def _num(df, col):
    return pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=float)


def _default_model(organism: str) -> int:
    o = (organism or "").lower()
    return 1 if ("cerevisiae" in o or "yeast" in o) else 0


@st.cache_data(show_spinner=False)
def _cached_fba(model_name, rate_tuples, mu, band, gases):
    rates = [flux.RateEstimate(*t) for t in rate_tuples]
    return flux.run_fba(model_name, rates, mu, band=band, constrain_gases=gases)


def render():
    st.title("🧬 Flux Analysis")
    st.caption("Genome-scale flux balance analysis constrained by this run's measured "
               "uptake and secretion rates · iML1515 (E. coli) · yeast-GEM (S. cerevisiae)")

    df = st.session_state.run_data
    if df is None:
        st.info("Load data in **Data Import** first.")
        return
    cm = st.session_state.col_map
    cols = list(df.columns)

    # ── Setup ────────────────────────────────────────────────────────────────
    with st.expander("⚙️ Model and data mapping", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        model_name = c1.selectbox("Genome-scale model", list(flux.MODELS),
                                  index=_default_model(st.session_state.get("run_organism")))
        tcol = c2.selectbox("Time (h)", cols,
                            index=cols.index(cm["time"]) if cm.get("time") in cols else 0)
        odcol = c3.selectbox("OD₆₀₀", cols,
                             index=cols.index(cm["od"]) if cm.get("od") in cols else min(1, len(cols) - 1))
        dcw_f = c4.number_input("OD→DCW factor (g/L per OD)", 0.1, 2.0, 0.40, 0.01,
                                help="E. coli typically 0.33–0.5, S. cerevisiae 0.2–0.6. "
                                     "Every specific rate is divided by biomass, so this "
                                     "factor scales all fluxes.")

        exch = flux.MODELS[model_name]["exchange"]
        rows = []
        for c in cols:
            key = flux.guess_metabolite(c)
            if key and key in exch and c not in (tcol, odcol):
                unit = "mM" if ("mm" in c.lower() and "mmol" not in c.lower()) else "g/L"
                rows.append({"Use": True, "Column": c, "Metabolite": key, "Unit": unit})
        st.markdown("**Measured metabolites** — substrates and products in the broth")
        mapping = st.data_editor(
            pd.DataFrame(rows or [{"Use": False, "Column": cols[0], "Metabolite": "glucose", "Unit": "g/L"}]),
            column_config={
                "Use": st.column_config.CheckboxColumn(),
                "Column": st.column_config.SelectboxColumn(options=cols, required=True),
                "Metabolite": st.column_config.SelectboxColumn(options=sorted(exch), required=True),
                "Unit": st.column_config.SelectboxColumn(options=["g/L", "mM"], required=True),
            },
            num_rows="dynamic", hide_index=True, key="flux_map_editor")

        g1, g2, g3 = st.columns(3)
        none = "— none —"
        guess_our = next((c for c in cols if "our" in c.lower()), none)
        guess_cer = next((c for c in cols if "cer" in c.lower()), none)
        our_col = g1.selectbox("OUR (mmol L⁻¹ h⁻¹)", [none] + cols,
                               index=([none] + cols).index(guess_our))
        cer_col = g2.selectbox("CER (mmol L⁻¹ h⁻¹)", [none] + cols,
                               index=([none] + cols).index(guess_cer))
        band = g3.slider("Measurement tolerance", 0.05, 0.30, 0.10, 0.05,
                         help="Minimum ± band around each measured rate (the 2·SE band "
                              "from the regression is used when it is wider).")

    t = _num(df, tcol)
    od = _num(df, odcol)
    ok = np.isfinite(t) & np.isfinite(od)
    if ok.sum() < 3:
        st.warning("Need at least 3 time points with OD.")
        return

    gk = compute_growth_kinetics(t[ok], od[ok], dcw_f)
    if not gk.get("mu"):
        st.warning("No exponential phase could be fitted to the OD data, so specific "
                   "rates cannot be computed.")
        return
    exp_t = gk["exp_t"]
    lo_def, hi_def = float(exp_t[0]), float(exp_t[-1])
    tmin, tmax = float(np.nanmin(t)), float(np.nanmax(t))
    win = st.slider("Exponential window used for rates (h)", tmin, tmax, (lo_def, hi_def),
                    step=max((tmax - tmin) / 200, 0.01),
                    help="Defaults to the window the Growth Kinetics engine fitted.")
    mu, mu_se = gk["mu"], gk["mu_se"] or 0.0

    conc = {}
    for _, r in mapping.iterrows():
        if not r.get("Use") or r["Column"] not in df.columns:
            continue
        v = _num(df, r["Column"])
        if r["Unit"] == "mM":
            v = v * flux.METABOLITES[r["Metabolite"]][0] / 1000
        conc[r["Metabolite"]] = v
    our = _num(df, our_col) if our_col != none else None
    cer = _num(df, cer_col) if cer_col != none else None

    rates = flux.specific_rates(t, od, conc, mu, mu_se, win, dcw_f, our=our, cer=cer)

    st.subheader("Specific rates in the exponential phase")
    st.caption(f"μ = {mu:.3f} ± {mu_se:.3f} h⁻¹ over {win[0]:.2f}–{win[1]:.2f} h · "
               "q = μ · dC/dX (concentration vs biomass regression); gases = OUR or CER ÷ biomass")
    if rates:
        st.dataframe(pd.DataFrame([{
            "Metabolite": r.metabolite, "q (mmol/gDCW/h)": round(r.q, 3),
            "± SE": round(r.q_se, 3), "Direction": r.kind,
            "Points": r.n, "R²": None if np.isnan(r.r2) else round(r.r2, 3), "From": r.source}
            for r in rates]), hide_index=True, width="stretch")
    if not any(r.metabolite in flux.SUBSTRATES and r.q < 0 for r in rates):
        st.warning("No consumed substrate found in the window. Map a substrate column "
                   "(e.g. glucose) with at least 3 samples during exponential growth.")
        return

    if not st.button("▶ Run flux analysis", type="primary"):
        st.caption("Solving takes ~5–15 s (genome-scale model, flux variability).")
        return

    with st.spinner(f"Solving {model_name}…"):
        res = _cached_fba(model_name,
                          tuple((r.metabolite, r.q, r.q_se, r.r2, r.n, r.source) for r in rates),
                          mu, band, True)

    # ── Headline ─────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("μ measured", f"{mu:.3f} h⁻¹")
    if res.mu_predicted is not None:
        m2.metric("μ supported by measured uptake", f"{res.mu_predicted:.3f} h⁻¹",
                  f"{(res.mu_predicted / mu - 1) * 100:+.0f} %", delta_color="off")
    if res.q_substrate_required is not None:
        m3.metric(f"{res.substrate.capitalize()} uptake: measured vs needed",
                  f"{-res.q_substrate_measured:.2f} / {-res.q_substrate_required:.2f}",
                  help="mmol/gDCW/h. 'Needed' = minimum uptake the model requires for the "
                       "measured μ and by-products.")
    if res.carbon_recovery:
        m4.metric("Carbon recovery (flux map)", f"{res.carbon_recovery * 100:.0f} %")

    for msg in res.messages:
        (st.warning if any(w in msg for w in ("inconsistent", "No flux", "widened", "could not"))
         else st.info)(msg)
    if res.status != "ok":
        return

    if res.gas_check:
        st.markdown("**Off-gas check** (at the measured μ and minimum substrate uptake)")
        st.dataframe(pd.DataFrame([{
            "Gas": g["gas"], "Measured (mmol/gDCW/h)": round(abs(g["measured"]), 2),
            "Model expects": round(abs(g["model"]), 2),
            "Difference": f"{(abs(g['measured']) / abs(g['model']) - 1) * 100:+.0f} %" if g["model"] else "—"}
            for g in res.gas_check]), hide_index=True)

    # ── Flux map ─────────────────────────────────────────────────────────────
    st.subheader("Central carbon fluxes at the measured μ")
    st.caption("Bar = parsimonious FBA flux; whisker = flux-variability range (all "
               "distributions consistent with the measurements, total flux ≤ 110 % of "
               "the parsimonious optimum). Narrow whiskers = well determined by your data.")
    cf = pd.DataFrame(res.central)
    cf["order"] = cf["Pathway"].map({p: i for i, p in enumerate(PATHWAY_ORDER)}).fillna(99)
    cf = cf.sort_values(["order"]).reset_index(drop=True)
    fig = go.Figure(go.Bar(
        y=cf["Reaction"], x=cf["Flux"], orientation="h",
        marker_color=["#2563eb" if v >= 0 else "#dc2626" for v in cf["Flux"]],
        error_x=dict(type="data", symmetric=False,
                     array=(cf["Max"] - cf["Flux"]).clip(lower=0),
                     arrayminus=(cf["Flux"] - cf["Min"]).clip(lower=0),
                     color="#6b7280", thickness=1.2),
        customdata=np.stack([cf["Pathway"], cf["Min"], cf["Max"], cf["ID"]], axis=1),
        hovertemplate="%{y}<br>%{customdata[0]} · %{customdata[3]}<br>flux %{x:.2f}"
                      "<br>range %{customdata[1]:.2f} – %{customdata[2]:.2f}<extra></extra>"))
    fig.update_layout(height=28 * len(cf) + 80, margin=dict(l=10, r=10, t=10, b=40),
                      xaxis_title="mmol gDCW⁻¹ h⁻¹ (negative = reverse direction)",
                      yaxis=dict(autorange="reversed"), plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch")

    show = cf[["Pathway", "Reaction", "ID", "Flux", "Min", "Max"]].round(3)
    c1, c2 = st.columns([3, 2])
    c1.dataframe(show, hide_index=True, width="stretch")
    c2.markdown("**Exchange fluxes in the flux map**")
    c2.dataframe(pd.DataFrame(res.exchanges).round(3), hide_index=True, width="stretch")
    c2.caption(f"Tolerance used: ±{res.band:.0%} · off-gas constrained: "
               f"{'yes' if res.used_gases else 'no'}")
    st.download_button("⬇ Download fluxes (CSV)", show.to_csv(index=False),
                       file_name=f"fluxes_{st.session_state.get('run_name') or 'run'}.csv",
                       mime="text/csv")

    st.session_state.flux_result = {"model": model_name, "mu_predicted": res.mu_predicted,
                                    "fluxes": show.to_dict("records")}

    with st.expander("ℹ️ Method and limitations"):
        st.markdown(f"""
- **Specific rates** come from the exponential window only, where balanced growth makes
  rates per gram biomass constant. q = μ · dC/dX avoids differentiating noisy data.
- **μ supported by measured uptake**: the model maximises growth with every measured
  exchange fixed at its point estimate. A large gap to the measured μ means the data are
  not stoichiometrically consistent — see the notes above for the usual causes.
- **Carbon can only leave** as measured products, CO₂ or biomass (plus trace cofactor
  side products), so missing by-products show up as an inconsistency instead of being
  hidden.
- **This is FBA, not ¹³C-MFA.** Internal fluxes are the most parsimonious distribution
  consistent with the measured exchanges; the variability ranges show how much the data
  actually determine. Parallel pathways (e.g. PPP vs glycolysis) need labelling data to
  resolve.
- Models: {flux.MODELS[model_name]['citation']}. Default biomass composition and
  maintenance (ATPM / NGAM) of the published model are used.
""")
