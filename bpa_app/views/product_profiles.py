"""Product profiles, multi-metabolite plots, assay integration, anomaly detection."""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.calcs import detect_anomalies, PRODUCT_DB

def _get(df,cm,field):
    col=cm.get(field)
    if col and col in df.columns: return df[col].dropna().to_numpy(dtype=float)
    return None

def render():
    st.title("🧪 Product & Metabolite Profiles")
    st.caption("Time-course profiles · Multi-product · Assay methods · Contamination detection")

    df=st.session_state.run_data; cm=st.session_state.col_map
    if df is None: st.info("Load data in **Data Import** first."); return

    time=_get(df,cm,"time"); od=_get(df,cm,"od")
    ph=_get(df,cm,"ph"); do=_get(df,cm,"do")
    prod=_get(df,cm,"product"); glc=_get(df,cm,"glucose"); ace=_get(df,cm,"acetate")
    eth=_get(df,cm,"ethanol")

    if time is None: st.warning("No time column found."); return

    # ── Main profile plot ──────────────────────────────────────────────────────
    st.subheader("Process profiles")
    fig=make_subplots(rows=2,cols=2,
        subplot_titles=("Biomass & substrates","Products & byproducts","pH & DO","OD log-scale"),
        specs=[[{"secondary_y":True},{"secondary_y":False}],
               [{"secondary_y":True},{"secondary_y":False}]])

    COLORS={"od":"#1f77b4","glc":"#2ca02c","prod":"#9467bd","ace":"#ff7f0e",
            "eth":"#d62728","ph":"#8c564b","do":"#17becf"}

    if od is not None:
        n=min(len(time),len(od))
        fig.add_trace(go.Scatter(x=time[:n],y=od[:n],name="OD₆₀₀",
            line=dict(color=COLORS["od"],width=2),mode="lines+markers",marker=dict(size=5)),row=1,col=1)
    if glc is not None:
        n=min(len(time),len(glc))
        fig.add_trace(go.Scatter(x=time[:n],y=glc[:n],name="Glucose (g/L)",
            line=dict(color=COLORS["glc"],dash="dot",width=2)),row=1,col=1,secondary_y=True)
    if prod is not None:
        n=min(len(time),len(prod))
        fig.add_trace(go.Scatter(x=time[:n],y=prod[:n],name="Product (g/L)",
            line=dict(color=COLORS["prod"],width=2),mode="lines+markers",marker=dict(size=5)),row=1,col=2)
    if ace is not None:
        n=min(len(time),len(ace))
        fig.add_trace(go.Scatter(x=time[:n],y=ace[:n],name="Acetate (g/L)",
            line=dict(color=COLORS["ace"],dash="dot")),row=1,col=2)
    if eth is not None:
        n=min(len(time),len(eth))
        fig.add_trace(go.Scatter(x=time[:n],y=eth[:n],name="Ethanol (g/L)",
            line=dict(color=COLORS["eth"],dash="dash")),row=1,col=2)
    if ph is not None:
        n=min(len(time),len(ph))
        fig.add_trace(go.Scatter(x=time[:n],y=ph[:n],name="pH",
            line=dict(color=COLORS["ph"],width=2)),row=2,col=1)
    if do is not None:
        n=min(len(time),len(do))
        fig.add_trace(go.Scatter(x=time[:n],y=do[:n],name="DO (%)",
            line=dict(color=COLORS["do"],width=2)),row=2,col=1,secondary_y=True)
    if od is not None:
        n=min(len(time),len(od))
        fig.add_trace(go.Scatter(x=time[:n],y=od[:n],name="OD₆₀₀ (log)",
            line=dict(color=COLORS["od"],width=1.5)),row=2,col=2)
        fig.update_yaxes(type="log",row=2,col=2)

    fig.update_layout(height=520,margin=dict(t=40,b=20),showlegend=True,
                      legend=dict(orientation="h",y=-0.12))
    fig.update_xaxes(title_text="Time (h)")
    st.plotly_chart(fig,use_container_width=True)

    # ── Extra metabolites (user-defined) ──────────────────────────────────────
    with st.expander("➕ Add extra metabolite profiles"):
        st.caption("Map additional data columns to metabolites")
        extra_cols=[c for c in df.columns if c not in [cm.get(f) for f in cm]]
        if extra_cols:
            sel=st.multiselect("Columns to plot",extra_cols)
            if sel:
                fig_e=go.Figure()
                for i,c in enumerate(sel):
                    vals=df[c].dropna().to_numpy(dtype=float)
                    n=min(len(time),len(vals))
                    fig_e.add_trace(go.Scatter(x=time[:n],y=vals[:n],name=c,mode="lines+markers"))
                fig_e.update_layout(height=300,margin=dict(t=20,b=20),xaxis_title="Time (h)")
                st.plotly_chart(fig_e,use_container_width=True)
        else:
            st.info("All columns are already mapped.")

    # ── Anomaly / contamination detection ─────────────────────────────────────
    st.subheader("🔬 Contamination & anomaly detection")
    flags=detect_anomalies(time,od=od,ph=ph,do_pct=do)
    st.session_state.anomaly_flags=flags
    if not flags:
        st.success("✅ No anomalies detected.")
    else:
        for f in flags:
            sev=f.get("sev","medium")
            t_str=f"at t={f['time']}h" if f.get("time") else ""
            msg=f"**{f['param']}** {t_str}: {f['msg']}"
            if sev=="high":   st.error(f"🔴 {msg}")
            elif sev=="medium": st.warning(f"🟡 {msg}")
            else:             st.info(f"🔵 {msg}")

    # ── Product database reference ─────────────────────────────────────────────
    with st.expander("📚 Product database reference"):
        import pandas as pd
        cat_filter=st.selectbox("Category",["All"]+sorted(set(v["cat"] for v in PRODUCT_DB.values() if v["cat"]!="other")))
        rows=[]
        for name,p in PRODUCT_DB.items():
            if name=="Custom": continue
            if cat_filter!="All" and p["cat"]!=cat_filter: continue
            rows.append({"Product":name,"Formula":p["formula"],"MW":p["MW"],"γ":p["gamma"],
                         "Titer range":f"{p['tmin']}–{p['tmax']} g/L",
                         "STY range":f"{p['sty_min']}–{p['sty_max']} g/L/h",
                         "Category":p["cat"]})
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
