"""Mass Balance — multi-substrate, multi-product, C/H/O/N, DoR, yields."""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from modules.calcs import compute_mass_balance, SUBSTRATE_DB, BIOMASS_DB, PRODUCT_DB

def _get_col(df,cm,field):
    col=cm.get(field)
    if col and col in df.columns: return df[col].dropna().to_numpy(dtype=float)
    return None

def render():
    st.title("⚖️ Mass Balance")
    st.caption("Full C/H/O/N + degree-of-reduction balance · Multi-substrate · Multi-product · Impossible yield detection")

    df=st.session_state.run_data; cm=st.session_state.col_map
    if df is None: st.info("Load data in **Data Import** first."); return

    time_arr=_get_col(df,cm,"time"); od_arr=_get_col(df,cm,"od")
    n=min(len(time_arr) if time_arr is not None else 0,
          len(od_arr)   if od_arr is not None else 0)

    mode=st.session_state.run_mode
    prod_names=st.session_state.products
    sub_names =st.session_state.substrates

    with st.expander("⚙️ Balance parameters", expanded=True):
        st.subheader("Biomass")
        c1,c2,c3 = st.columns(3)
        organism  = c1.selectbox("Organism", list(BIOMASS_DB.keys()))
        dcw_f     = c2.number_input("OD→DCW factor", 0.1,2.0,0.40,0.05)
        _od_final_def = float(od_arr[-1]) if od_arr is not None else 7.4
        _od_init_def  = float(od_arr[0])  if od_arr is not None else 0.05
        _od_max_limit = max(1000.0, _od_final_def * 2.0)
        od_final  = c3.number_input("Final OD₆₀₀", 0.0, _od_max_limit,
                                     _od_final_def, 0.1, key="mb_od_final")
        od_initial= c3.number_input("Initial OD₆₀₀", 0.0, _od_max_limit,
                                     _od_init_def, 0.01, key="mb_od_initial")
        bm=BIOMASS_DB[organism]
        dx=max((od_final-od_initial)*dcw_f, 0.001)
        biomass_d={"dx":dx,"C":bm["C"],"H":bm["H"],"O":bm["O"],"N":bm["N"],"MW":bm["MW"],"gamma":bm["gamma"]}

        st.subheader("Substrates")
        substrates=[]
        for i,sname in enumerate(sub_names):
            st.caption(f"**{sname}**")
            c1,c2,c3,c4=st.columns(4)
            sdb_key=c1.selectbox("DB entry",list(SUBSTRATE_DB.keys()),key=f"sdb_{i}")
            sdb=SUBSTRATE_DB[sdb_key]
            s0=c2.number_input("Initial (g/L)",0.0,1000.0,20.0,0.1,key=f"s0_{i}")
            sf=c3.number_input("Final (g/L)",  0.0,1000.0,0.01,0.01,key=f"sf_{i}")
            fc=0.0
            if mode=="Fed-batch":
                fc=c4.number_input("Feed conc (g/L)",0.0,1000.0,0.0,key=f"sfc_{i}")
            substrates.append({"name":sname,"s0":s0,"sf":sf,"feed_conc":fc,
                "C":sdb["C"],"H":sdb["H"],"O":sdb["O"],"N":sdb["N"],"MW":sdb["MW"],"gamma":sdb["gamma"]})

        st.subheader("Products / metabolites")
        products=[]
        for i,pname in enumerate(prod_names):
            st.caption(f"**{pname}**")
            c1,c2,c3=st.columns(3)
            pdb_key=c1.selectbox("DB entry",["Custom"]+list(PRODUCT_DB.keys()),key=f"pdb_{i}")
            pdb=PRODUCT_DB.get(pdb_key,PRODUCT_DB["Custom"])
            prod_arr=_get_col(df,cm,"product")
            default_conc=float(prod_arr[-1]) if prod_arr is not None else 0.0
            conc=c2.number_input("Final conc (g/L)",0.0,500.0,default_conc,0.001,key=f"pc_{i}")
            mwp=c3.number_input("MW (g/mol)",1.0,2e6,float(min(pdb["MW"],1e6)),key=f"pmw_{i}")
            products.append({"name":pname,"conc":conc,"C":pdb["C"],"H":int(pdb.get("H",0)),
                "O":int(pdb.get("O",0)),"N":int(pdb.get("N",0)),"MW":mwp,"gamma":pdb["gamma"]})

        st.subheader("Gas & process")
        c1,c2,c3=st.columns(3)
        our=c1.number_input("OUR avg (mmol O₂/L/h)",0.0,200.0,
                             float(st.session_state.get("our_val",8.5)),0.1)
        cer=c2.number_input("CER avg (mmol CO₂/L/h)",0.0,200.0,
                             float(st.session_state.get("cer_val",9.2)),0.1)
        tf =c3.number_input("Process time (h)",0.1,500.0,
                             float(time_arr[-1]) if time_arr is not None else 24.0,0.5)
        feed_d=None
        if mode=="Fed-batch":
            c1,c2=st.columns(2)
            vf=c1.number_input("Feed volume (L)",0.0,100.0,0.0,0.01)
            feed_d={"vf":vf}
        elif mode=="Continuous":
            st.caption("**Chemostat / continuous mode** — enter steady-state operating conditions")
            c1,c2,c3=st.columns(3)
            D_rate=c1.number_input("Dilution rate D (h⁻¹)",0.001,2.0,0.10,0.005,format="%.3f",
                help="D = F/V. At steady state: μ = D for non-growing (washout avoided).")
            sin_cont=c2.number_input("Feed substrate conc (g/L)",0.0,1000.0,20.0,0.1,
                help="Concentration of substrate in the feed stream")
            vol_cont=c3.number_input("Working volume (L)",0.01,10000.0,1.0,0.1)
            feed_d={"D":D_rate,"feed_conc":sin_cont,"V":vol_cont}
            st.info(f"At D={D_rate:.3f} h⁻¹ → steady-state μ ≈ D = {D_rate:.3f} h⁻¹ · "
                    f"Residence time τ = {1/D_rate:.1f} h")

    if st.button("🧮 Compute balance", type="primary"):
        gas_d={"our":our,"cer":cer,"tf":tf}
        res=compute_mass_balance(substrates,products,biomass_d,gas_d,feed=feed_d,mode=mode)
        st.session_state["mb_result"]=res
        st.session_state.c_closure=res.get("closure",0)
        if res.get("yields"):
            st.session_state.yps=res["yields"].get("Yps",0)
            st.session_state.yxs=res["yields"].get("Yxs",0)
        st.session_state.rq=res.get("RQ",0)

    res=st.session_state.get("mb_result")
    if not res: return

    cl=res.get("closure",0)
    col=("🟢" if 95<=cl<=105 else "🟡" if 80<=cl<=115 else "🔴")
    st.subheader(f"Carbon balance closure: {col} {cl:.1f}%")

    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("C closure (%)",f"{cl:.1f}",delta="target 95–105%")
    c2.metric("RQ",f"{res.get('RQ',0):.3f}",delta="~1.0 aerobic")
    if res.get("yields"):
        y=res["yields"]
        c3.metric("Yxs (g/g)",f"{y['Yxs']:.4f}",delta=f"max {y['YxsMax']:.3f}")
        c4.metric("Yps (g/g)",f"{y['Yps']:.4f}",delta=f"max {y['YpsMax']:.3f}")
        c5.metric("C efficiency (%)",f"{y['Ceff']:.1f}")
        if y["Yps"]>y["YpsMax"]*1.05:
            st.error("🚫 **Impossible Yps!** Measured yield exceeds thermodynamic maximum. Check substrate/product concentrations or assay.")

    # Carbon balance bar chart
    st.subheader("Carbon balance")
    bar_data={"Biomass":res.get("C_biomass",0),"CO₂":res.get("C_CO2",0),"Unaccounted":max(res.get("C_unacc",0),0)}
    for pd_item in res.get("prod_details",[]):
        bar_data[pd_item["name"]]=pd_item["C_out"]
    fig=go.Figure()
    colors=["#1f77b4","#7f7f7f","#d62728","#2ca02c","#ff7f0e","#9467bd","#8c564b"]
    for i,(k,v) in enumerate(bar_data.items()):
        fig.add_trace(go.Bar(name=k,x=["Carbon out (g C/L)"],y=[v],marker_color=colors[i%len(colors)]))
    fig.add_hline(y=res.get("C_in",0),line_dash="dash",line_color="black",
                  annotation_text=f"C in = {res['C_in']:.4f} g C/L")
    fig.update_layout(barmode="stack",height=320,margin=dict(t=20,b=20),
                      yaxis_title="g C/L")
    st.plotly_chart(fig,use_container_width=True)

    # Elemental balance table
    if res.get("elem"):
        st.subheader("Elemental balance (mmol/L)")
        e=res["elem"]
        df_e=pd.DataFrame({
            "Element":["C","H","O","N"],
            "In (mmol/L)":[f"{e['inC']:.1f}",f"{e['inH']:.1f}",f"{e['inO']:.1f}","—"],
            "Out (mmol/L)":[f"{e['outC']:.1f}",f"{e['outH']:.1f}",f"{e['outO']:.1f}",f"{e['outN']:.1f}"],
            "Note":["","f\"H₂O produced: {e['H2O']:.0f} mmol/L\"","",""],
        })
        df_e.at[1,"Note"]=f"H₂O produced: {e['H2O']:.0f} mmol/L"
        st.dataframe(df_e,hide_index=True,use_container_width=True)

    # Degree of reduction
    if res.get("dor"):
        st.subheader("Degree of reduction (γ)")
        d=res["dor"]
        cl_dor=d["cl"]
        st.info(f"γ_in = {d['gin']:.4f} = γ_bio ({d['gbio']:.4f}) + γ_prod ({d['gprod']:.4f}) + 4×O₂ ({d['gO2']:.4f}) = {d['gout']:.4f}  →  closure {cl_dor:.1f}%")

    # Yield table
    if res.get("yields"):
        st.subheader("Yield coefficients")
        y=res["yields"]
        df_y=pd.DataFrame([
            {"Coefficient":"Yxs (g biomass/g substrate)","Value":f"{y['Yxs']:.4f}","Max/Lit":f"{y['YxsMax']:.3f}","OK":"✅" if y["Yxs"]<=y["YxsMax"]*1.05 else "❌"},
            {"Coefficient":"Yps (g product/g substrate)","Value":f"{y['Yps']:.4f}","Max/Lit":f"≤{y['YpsMax']:.3f}","OK":"✅" if y["Yps"]<=y["YpsMax"]*1.05 else "❌"},
            {"Coefficient":"Yxp (g product/g biomass)","Value":f"{y['Yxp']:.4f}","Max/Lit":"—","OK":"—"},
            {"Coefficient":"C efficiency (%)","Value":f"{y['Ceff']:.1f}%","Max/Lit":"100% = max","OK":"—"},
        ])
        st.dataframe(df_y,hide_index=True,use_container_width=True)
