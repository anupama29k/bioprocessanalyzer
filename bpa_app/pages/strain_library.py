"""Strain Library — glycerol stocks, passage history, shake flask stages."""
import streamlit as st
import pandas as pd
from datetime import date
from modules import session

def render():
    st.title("🧫 Strain Library")
    st.caption("Strain identity · Glycerol bank · Passage history · Shake flask pre-cultures")

    tab_view, tab_new, tab_active = st.tabs(["Library", "Add / Edit strain", "Active strain"])

    with tab_new:
        _strain_form()

    with tab_view:
        _library_view()

    with tab_active:
        _active_strain_panel()


def _strain_form(strain=None):
    s = strain or {}
    with st.form("strain_form"):
        st.subheader("Strain identity")
        c1,c2,c3,c4 = st.columns(4)
        name     = c1.text_input("Strain name",     value=s.get("name",""))
        organism = c2.selectbox("Organism",
            ["E. coli","S. cerevisiae","B. subtilis","K. phaffii","C. glutamicum",
             "C. acetobutylicum","A. terreus","Streptomyces sp.","Custom"],
            index=["E. coli","S. cerevisiae","B. subtilis","K. phaffii","C. glutamicum",
                   "C. acetobutylicum","A. terreus","Streptomyces sp.","Custom"].index(s.get("organism","E. coli")) if s.get("organism") else 0)
        plasmid  = c3.text_input("Plasmid / construct", value=s.get("plasmid",""))
        marker   = c4.text_input("Selection marker",    value=s.get("marker",""))
        c1,c2 = st.columns(2)
        genotype = c1.text_input("Genotype / modifications", value=s.get("genotype",""),
                                  placeholder="e.g. ΔldhA ΔpflB + mvaS mvaE")
        source   = c2.text_input("Source / origin", value=s.get("source",""),
                                  placeholder="e.g. ATCC 25922, lab stock")
        c1,c2 = st.columns(2)
        date_built = c1.text_input("Date constructed", value=s.get("date_built",""))
        built_by   = c2.text_input("Constructed by",   value=s.get("built_by",""))
        notes_id = st.text_area("Genetic history / notes", value=s.get("notes_id",""), height=70)

        st.subheader("Glycerol bank (cryostock)")
        c1,c2,c3,c4 = st.columns(4)
        stock_id    = c1.text_input("Stock ID / vial label", value=s.get("stock_id",""))
        glyc_pct    = c2.number_input("Glycerol %", 0.0, 50.0, float(s.get("glyc_pct",15.0)), 1.0)
        sto_temp    = c3.selectbox("Storage temp", ["-80 °C","-20 °C","-196 °C (LN₂)"],
                                    index=["-80 °C","-20 °C","-196 °C (LN₂)"].index(s.get("sto_temp","-80 °C")) if s.get("sto_temp") else 0)
        freeze_date = c4.text_input("Date frozen", value=s.get("freeze_date",""))
        c1,c2,c3,c4 = st.columns(4)
        stock_od    = c1.text_input("OD at banking", value=s.get("stock_od",""), placeholder="e.g. 0.6 (mid-log)")
        stock_phase = c2.selectbox("Phase at banking",["Mid-log (OD 0.4–0.8)","Early log","Late log","Stationary"],
                                    index=0)
        stock_med   = c3.text_input("Banking medium", value=s.get("stock_med","LB"))
        vials       = c4.text_input("Vials in bank",  value=s.get("vials","10"))
        viab_date   = c1.text_input("Viability check date", value=s.get("viab_date",""))
        viab_result = c2.text_input("Viability result", value=s.get("viab_result",""), placeholder="Passed / Failed")
        notes_stock = st.text_area("Stock notes", value=s.get("notes_stock",""), height=60)

        st.subheader("Passage history")
        st.caption("Each row is one transfer from glycerol stock to bioreactor")
        pass_limit = st.number_input("Passage limit (policy)", 1, 20, int(s.get("pass_limit",5)))
        passages_default = s.get("passages", [
            {"type":"Revive","medium":"LB","vol_mL":"5","inoculum":"10 µL stock","temp_C":"37","duration_h":"12","final_OD":"2.1","notes":""},
            {"type":"Pre-culture","medium":"M9 glucose","vol_mL":"50","inoculum":"1:100","temp_C":"37","duration_h":"8","final_OD":"0.8","notes":""},
        ])
        pass_df = pd.DataFrame(passages_default) if passages_default else pd.DataFrame(
            columns=["type","medium","vol_mL","inoculum","temp_C","duration_h","final_OD","notes"])
        edited_passes = st.data_editor(pass_df, num_rows="dynamic", use_container_width=True,
                                        column_config={
                                            "type": st.column_config.SelectboxColumn("Type",
                                                options=["Revive from stock","Agar plate","Overnight","Pre-culture","Seed flask","Transfer"]),
                                        })

        st.subheader("Shake flask pre-cultures")
        sf_default = s.get("shake_flasks", [
            {"flask_mL":"250","vol_mL":"50","baffled":"No","closure":"Foam stopper",
             "medium":"M9 glucose","temp_C":"37","rpm":"200","throw_mm":"50",
             "inoculum":"OD 0.05","duration_h":"8","final_OD":"0.8","antibiotic":"Amp 100 µg/mL","notes":""}
        ])
        sf_df = pd.DataFrame(sf_default) if sf_default else pd.DataFrame(
            columns=["flask_mL","vol_mL","baffled","closure","medium","temp_C","rpm","throw_mm","inoculum","duration_h","final_OD","antibiotic","notes"])
        edited_sf = st.data_editor(sf_df, num_rows="dynamic", use_container_width=True)

        c1,c2 = st.columns(2)
        inoc_vol   = c1.text_input("Bioreactor inoculum volume (mL)", value=s.get("inoc_vol","50"))
        inoc_od    = c2.text_input("Inoculum OD₆₀₀", value=s.get("inoc_od","0.8"))
        c1,c2 = st.columns(2)
        inoc_ratio = c1.text_input("Inoculum ratio (% v/v)", value=s.get("inoc_ratio","5"))
        start_od   = c2.text_input("Target starting OD in bioreactor", value=s.get("start_od","0.05"))

        submitted = st.form_submit_button("💾 Save strain", type="primary")
        if submitted:
            strain_rec = {
                "name":name,"organism":organism,"plasmid":plasmid,"marker":marker,
                "genotype":genotype,"source":source,"date_built":date_built,"built_by":built_by,"notes_id":notes_id,
                "stock_id":stock_id,"glyc_pct":glyc_pct,"sto_temp":sto_temp,"freeze_date":freeze_date,
                "stock_od":stock_od,"stock_phase":stock_phase,"stock_med":stock_med,"vials":vials,
                "viab_date":viab_date,"viab_result":viab_result,"notes_stock":notes_stock,
                "pass_limit":pass_limit,"passages":edited_passes.to_dict("records"),
                "shake_flasks":edited_sf.to_dict("records"),
                "inoc_vol":inoc_vol,"inoc_od":inoc_od,"inoc_ratio":inoc_ratio,"start_od":start_od,
            }
            lib = st.session_state.strain_library
            existing = next((i for i,s in enumerate(lib) if s.get("name")==name), -1)
            if existing >= 0: lib[existing] = strain_rec
            else: lib.append(strain_rec)
            session.save_strains()
            st.success(f"Strain **{name}** saved.")


def _library_view():
    lib = st.session_state.strain_library
    if not lib:
        st.info("No strains saved yet. Use 'Add / Edit strain' to add one.")
        return
    search = st.text_input("Search strains", placeholder="name, organism, plasmid…")
    filtered = [s for s in lib if not search or
                search.lower() in (s.get("name","")+" "+s.get("organism","")+" "+s.get("plasmid","")).lower()]
    for s in filtered:
        passes = len(s.get("passages",[]))
        limit  = s.get("pass_limit",5)
        badge  = "🟢" if passes<=limit else "🔴"
        with st.expander(f"{badge} **{s.get('name','—')}** · {s.get('organism','—')} · {s.get('plasmid','—')} · Stock: {s.get('stock_id','—')}"):
            c1,c2,c3 = st.columns(3)
            c1.metric("Passages", f"{passes}/{limit}")
            c2.metric("Storage", s.get("sto_temp","—"))
            c3.metric("Frozen", s.get("freeze_date","—"))
            st.caption(f"**Genotype:** {s.get('genotype','—')}")
            st.caption(f"**Viability:** {s.get('viab_result','—')} ({s.get('viab_date','—')})")
            if s.get("passages"):
                st.dataframe(pd.DataFrame(s["passages"]), use_container_width=True)
            col1, col2 = st.columns([1,1])
            if col1.button(f"Set as active strain", key=f"set_{s['name']}"):
                st.session_state.active_strain = s
                st.success(f"Active strain set to **{s['name']}**")
            if col2.button(f"Delete", key=f"del_{s['name']}"):
                st.session_state.strain_library = [x for x in lib if x.get("name")!=s.get("name")]
                session.save_strains()
                st.rerun()


def _active_strain_panel():
    s = st.session_state.active_strain
    if not s:
        st.info("No active strain set. Go to Library and click 'Set as active strain'.")
        return
    st.success(f"Active: **{s.get('name','—')}** · {s.get('organism','—')}")
    passes = len(s.get("passages",[]))
    limit  = s.get("pass_limit",5)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Passages from stock", f"{passes}")
    c2.metric("Passage limit", f"{limit}")
    c3.metric("Stock ID", s.get("stock_id","—"))
    c4.metric("Storage", s.get("sto_temp","—"))
    if passes > limit:
        st.error(f"⚠️ Passage limit exceeded ({passes} > {limit}). Revive fresh vial before next run.")
    elif passes == limit:
        st.warning(f"⚠️ At passage limit ({passes}/{limit}). Consider reviving fresh stock.")
    else:
        st.success(f"✅ Within passage limit ({passes}/{limit})")
    with st.expander("Full strain record"):
        import json
        st.code(json.dumps(s, indent=2), language="json")
