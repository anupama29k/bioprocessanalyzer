"""Golden Batch analysis — compare current run to reference, automated explanations."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.calcs import compare_to_golden

def render():
    st.title("✨ Golden Batch Analysis")
    st.caption("Set a reference run → compare KPIs → automated explanations for deviations")

    tab_set, tab_compare = st.tabs(["Set golden batch", "Compare to golden"])

    with tab_set:
        st.subheader("Define golden batch reference")
        st.info("The golden batch is your best validated run. Set it once; compare all future runs against it.")

        with st.form("golden_form"):
            c1,c2 = st.columns(2)
            gb_name = c1.text_input("Golden batch name / run ID", placeholder="e.g. MVA-R02-golden")
            c1,c2,c3,c4 = st.columns(4)
            gb_mu     = c1.number_input("μ (h⁻¹)",        0.0, 5.0,  0.68, 0.001, format="%.3f")
            gb_titer  = c2.number_input("Titer (g/L)",    0.0, 1000., 3.10, 0.01)
            gb_sty    = c3.number_input("STY (g/L/h)",    0.0, 100., 0.129, 0.0001, format="%.4f")
            gb_yps    = c4.number_input("Yps (g/g)",      0.0, 5.0,  0.157, 0.001, format="%.4f")
            c1,c2,c3,c4 = st.columns(4)
            gb_yxs    = c1.number_input("Yxs (g/g)",      0.0, 5.0,  0.45,  0.001, format="%.3f")
            gb_cl     = c2.number_input("C closure (%)",  0.0, 200., 97.2,  0.1)
            gb_rq     = c3.number_input("RQ",             0.0, 5.0,  1.05,  0.01)
            gb_notes  = c4.text_area("Notes", placeholder="Conditions that made this the golden batch…", height=70)

            if st.form_submit_button("⭐ Set as golden batch", type="primary"):
                st.session_state.golden_batch = {
                    "name":gb_name, "mu":gb_mu, "titer":gb_titer, "sty":gb_sty,
                    "yps":gb_yps, "yxs":gb_yxs, "closure":gb_cl, "rq":gb_rq,
                    "notes":gb_notes,
                }
                st.session_state.golden_batch_name = gb_name
                st.success(f"✅ Golden batch set: **{gb_name}**")

        # Quick load from registry
        reg = st.session_state.run_registry
        if reg:
            st.subheader("Or load from run registry")
            run_names = [r.get("name","") for r in reg if r.get("name","")]
            sel = st.selectbox("Select run", ["— select —"]+run_names)
            if sel != "— select —" and st.button("Load this run as golden batch"):
                r = next((x for x in reg if x.get("name")==sel), None)
                if r:
                    def safe(k, default=0.0):
                        v = r.get(k,"")
                        try: return float(v)
                        except: return default
                    st.session_state.golden_batch = {
                        "name": sel,
                        "mu":    safe("mu"),    "titer": safe("titer"),
                        "sty":   safe("sty"),   "yps":   safe("yps"),
                        "yxs":   safe("yxs",0.45), "closure": safe("c_bal",97),
                        "rq":    safe("rq",1.0),  "notes": r.get("notes",""),
                    }
                    st.session_state.golden_batch_name = sel
                    st.success(f"Golden batch loaded from registry: **{sel}**")

    with tab_compare:
        gb = st.session_state.golden_batch
        if gb is None:
            st.info("Set a golden batch first (in the 'Set golden batch' tab).")
            return

        st.success(f"Golden batch: **{gb.get('name','—')}**")

        st.subheader("Current run KPIs")
        current = {}
        c1,c2,c3,c4 = st.columns(4)
        current["mu"]     = c1.number_input("μ (h⁻¹)", 0.0, 5.0,
            float(st.session_state.mu or gb.get("mu",0.5)), 0.001, format="%.3f", key="cmu")
        current["titer"]  = c2.number_input("Titer (g/L)", 0.0, 1000.,
            float(st.session_state.titer or gb.get("titer",0.0)), 0.01, key="ctit")
        current["sty"]    = c3.number_input("STY (g/L/h)", 0.0, 100.,
            float(st.session_state.sty or gb.get("sty",0.0)), 0.0001, format="%.4f", key="csty")
        current["yps"]    = c4.number_input("Yps (g/g)", 0.0, 5.0,
            float(st.session_state.yps or gb.get("yps",0.0)), 0.001, format="%.4f", key="cyps")
        c1,c2,c3 = st.columns(3)
        current["yxs"]    = c1.number_input("Yxs (g/g)", 0.0, 5.0,
            float(st.session_state.yxs or gb.get("yxs",0.4)), 0.001, format="%.3f", key="cyxs")
        current["closure"]= c2.number_input("C closure (%)", 0.0, 200.,
            float(st.session_state.c_closure or gb.get("closure",95.0)), 0.1, key="ccl")
        current["rq"]     = c3.number_input("RQ", 0.0, 5.0,
            float(st.session_state.rq or gb.get("rq",1.0)), 0.01, key="crq")

        if st.button("🔍 Compare", type="primary"):
            cmp = compare_to_golden(current, gb)

            st.subheader("Comparison results")
            STATUS_ICON={"ok":"✅","warn":"⚠️","fail":"❌"}
            STATUS_COLOR={"ok":"#d4edda","warn":"#fff3cd","fail":"#f8d7da"}

            rows=[]
            for k,v in cmp.items():
                rows.append({
                    "Parameter": v["label"],
                    "Current":   f"{v['current']:.4f} {v['unit']}",
                    "Golden":    f"{v['golden']:.4f} {v['unit']}",
                    "Δ":         f"{v['delta']:+.4f}",
                    "Δ%":        f"{v['delta_pct']:+.1f}%",
                    "Status":    STATUS_ICON[v["status"]],
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

            # Radar / spider chart
            labels  = [v["label"] for v in cmp.values()]
            def safe_ratio(v):
                if v["golden"]==0: return 1.0
                return min(abs(v["current"]/v["golden"]),2.0)
            curr_r = [safe_ratio(v) for v in cmp.values()]
            gold_r = [1.0]*len(labels)
            fig=go.Figure()
            fig.add_trace(go.Scatterpolar(r=curr_r+[curr_r[0]], theta=labels+[labels[0]],
                fill="toself", name="Current", line=dict(color="#1f77b4")))
            fig.add_trace(go.Scatterpolar(r=gold_r+[gold_r[0]], theta=labels+[labels[0]],
                fill="toself", name="Golden", line=dict(color="#2ca02c",dash="dash"), opacity=0.4))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,2])),
                              height=380, margin=dict(t=20,b=20))
            st.plotly_chart(fig, use_container_width=True)

            # Automated explanations
            explanations = [(v["label"],v["explanation"]) for v in cmp.values() if v.get("explanation")]
            if explanations:
                st.subheader("Automated explanations")
                for label, expl in explanations:
                    st.warning(f"**{label}:** {expl}")
            else:
                st.success("All parameters within tolerance of golden batch. 🎉")
