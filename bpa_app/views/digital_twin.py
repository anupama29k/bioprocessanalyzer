"""Lightweight self-learning digital twin — ODE Monod model fit and prediction."""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from modules.calcs import fit_twin_to_data, run_digital_twin

def _get(df,cm,field):
    col=cm.get(field)
    if col and col in df.columns: return df[col].dropna().to_numpy(float)
    return None

def render():
    st.title("🤖 Digital Twin")
    st.caption("Lightweight self-learning ODE model · Monod kinetics · Luedeking–Piret product · Fed-batch ready")

    df=st.session_state.run_data; cm=st.session_state.col_map
    if df is None: st.info("Load data in **Data Import** first."); return

    time=_get(df,cm,"time"); od=_get(df,cm,"od")
    sub=_get(df,cm,"substrate"); prod=_get(df,cm,"product")
    if time is None or od is None:
        st.warning("Need at least time + OD columns."); return

    n=min(len(time), len(od),
          len(sub)  if sub  is not None else 999,
          len(prod) if prod is not None else 999)
    time=time[:n]; od=od[:n]
    if sub  is not None: sub  = sub[:n]
    if prod is not None: prod = prod[:n]

    with st.expander("⚙️ Model parameters", expanded=True):
        c1,c2,c3,c4=st.columns(4)
        dcw_f = c1.number_input("OD→DCW factor",0.1,2.0,0.40,0.05)
        V0    = c2.number_input("Initial volume (L)",0.01,1000.,1.0,0.1)
        mode  = c3.selectbox("Mode",["Batch","Fed-batch","Continuous"])
        if mode == "Fed-batch":
            F_rate= c4.number_input("Feed rate (L/h)",0.0,100.,0.0,0.001)
            Sin   = c1.number_input("Feed substrate (g/L)",0.0,1000.,0.0,1.0)
        elif mode == "Continuous":
            D_rate= c4.number_input("Dilution rate D (h⁻¹)",0.001,2.0,0.1,0.005,format="%.3f",
                help="At steady state μ=D. ODE will simulate approach to steady state.")
            Sin   = c1.number_input("Feed substrate (g/L)",0.0,1000.,20.0,1.0)
            F_rate = D_rate * V0   # F = D * V
        else:
            F_rate = 0.0
            Sin    = 0.0

    st.subheader("1. Fit model to current data")
    if st.button("🔧 Fit ODE parameters", type="primary"):
        with st.spinner("Fitting Monod ODE to experimental data…"):
            params = fit_twin_to_data(time, od,
                                      sub if sub is not None else np.linspace(20,0,n),
                                      prod, dcw_f, V0)
            params["F"]   = F_rate
            params["Sin"] = Sin
            st.session_state.dt_params = params
            st.session_state.dt_model  = "fitted"

        p=st.session_state.dt_params
        st.success(f"Fit {'converged ✅' if p.get('converged') else 'did not converge ⚠️'} · loss = {p.get('fit_loss',0):.6f}")
        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric("μ_max (h⁻¹)",   f"{p['mu_max']:.3f}")
        c2.metric("Ks (g/L)",       f"{p['Ks']:.4f}")
        c3.metric("Yxs (g/g)",      f"{p['Yxs']:.4f}")
        c4.metric("LP α",           f"{p['lp_alpha']:.4f}")
        c5.metric("LP β",           f"{p['lp_beta']:.5f}")

    if st.session_state.dt_params:
        st.subheader("2. Validate fit against experimental data")
        p = st.session_state.dt_params
        t_eval = np.linspace(time[0], time[-1], 200)
        df_twin = run_digital_twin(p, (time[0],time[-1]), t_eval)
        if df_twin.empty:
            st.error("ODE solver failed. Try different initial parameter guesses.")
        else:
            dcw = od * dcw_f
            fig = go.Figure()
            # Biomass
            fig.add_trace(go.Scatter(x=time, y=dcw, mode="markers",
                name="DCW exp", marker=dict(color="#1f77b4",size=7,symbol="circle")))
            fig.add_trace(go.Scatter(x=df_twin["time"], y=df_twin["X_twin"], mode="lines",
                name="X twin", line=dict(color="#1f77b4",width=2)))
            # Substrate
            if sub is not None:
                fig.add_trace(go.Scatter(x=time, y=sub, mode="markers",
                    name="Substrate exp", marker=dict(color="#2ca02c",size=7,symbol="square")))
                fig.add_trace(go.Scatter(x=df_twin["time"], y=df_twin["S_twin"], mode="lines",
                    name="S twin", line=dict(color="#2ca02c",width=2,dash="dot")))
            # Product
            if prod is not None:
                fig.add_trace(go.Scatter(x=time, y=prod, mode="markers",
                    name="Product exp", marker=dict(color="#9467bd",size=7,symbol="diamond")))
                fig.add_trace(go.Scatter(x=df_twin["time"], y=df_twin["P_twin"], mode="lines",
                    name="P twin", line=dict(color="#9467bd",width=2,dash="dash")))
            fig.update_layout(height=380, xaxis_title="Time (h)", yaxis_title="Concentration (g/L)",
                              margin=dict(t=20,b=20), legend=dict(orientation="h",y=-0.15))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("3. Predict extended / modified run")
        c1,c2,c3=st.columns(3)
        tf_pred = c1.number_input("Predict until (h)", float(time[-1]), 500., float(time[-1])*2, 1.0)
        with st.expander("Override parameters for prediction"):
            c1,c2,c3,c4=st.columns(4)
            mu_max_ov = c1.number_input("μ_max override", 0.01, 5.0, float(p["mu_max"]), 0.001, format="%.3f")
            Ks_ov     = c2.number_input("Ks override",    0.001,50.,float(p["Ks"]),0.001,format="%.4f")
            F_ov      = c3.number_input("Feed rate (L/h)",0.0,100.,float(p.get("F",0)),0.001,format="%.3f")
            Sin_ov    = c4.number_input("Feed substrate", 0.0,1000.,float(p.get("Sin",0)),1.0)

        if st.button("▶ Run prediction"):
            p_pred = {**p, "mu_max":mu_max_ov, "Ks":Ks_ov, "F":F_ov, "Sin":Sin_ov}
            t_pred = np.linspace(time[0], tf_pred, 400)
            df_pred = run_digital_twin(p_pred, (time[0],tf_pred), t_pred)
            if not df_pred.empty:
                fig2=go.Figure()
                fig2.add_trace(go.Scatter(x=df_pred["time"],y=df_pred["X_twin"],name="Biomass (pred)",line=dict(color="#1f77b4")))
                fig2.add_trace(go.Scatter(x=df_pred["time"],y=df_pred["S_twin"],name="Substrate (pred)",line=dict(color="#2ca02c",dash="dot")))
                fig2.add_trace(go.Scatter(x=df_pred["time"],y=df_pred["P_twin"],name="Product (pred)",line=dict(color="#9467bd",dash="dash")))
                fig2.add_vline(x=time[-1],line_dash="dash",line_color="gray",annotation_text="Data end")
                fig2.update_layout(height=320,xaxis_title="Time (h)",yaxis_title="Concentration (g/L)",
                                   margin=dict(t=20,b=20))
                st.plotly_chart(fig2,use_container_width=True)
                final=df_pred.iloc[-1]
                c1,c2,c3=st.columns(3)
                c1.metric("Predicted titer",f"{final['P_twin']:.3f} g/L")
                c2.metric("Predicted DCW",  f"{final['X_twin']:.3f} g/L")
                c3.metric("Predicted sub",  f"{final['S_twin']:.3f} g/L")
