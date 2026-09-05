# BPA-v2.2 — Data Import with comprehensive sidebar sensor mapping
import io, streamlit as st, pandas as pd, numpy as np
from modules import session
from data_manager import render_run_metadata_form

SENSORS = {
    "time":   {"label":"Time","unit":"h","section":"time",
        "aliases":["time","elapsed","t_h","time_h","hours","process_time","elapsed time_h","elapsed_time_h","timestamp","runtime"],
        "tooltip":"Elapsed process time in hours"},
    "ph":     {"label":"pH","unit":"","section":"core",
        "aliases":["ph","ph_value","ph actual","ph_act"],"tooltip":"Process pH electrode"},
    "do":     {"label":"Dissolved Oxygen","unit":"%","section":"core",
        "aliases":["do","do%","po2","dissolved oxygen","dissolved_o2","do_pct","do_value"],"tooltip":"DO % air saturation"},
    "temp":   {"label":"Temperature","unit":"°C","section":"core",
        "aliases":["temp","temperature","temp_c","temperature_value"],"tooltip":"Vessel temperature"},
    "rpm":    {"label":"Agitation Speed","unit":"rpm","section":"core",
        "aliases":["rpm","stirrer","agitation","stirrer speed","agitator","n[rpm]"],"tooltip":"Impeller speed"},
    "weight": {"label":"Reactor Weight / Load Cell","unit":"g","section":"core",
        "aliases":["weight","load cell","reactor weight","mass","scale"],"tooltip":"Gravimetric feed tracking"},
    "air_flow":    {"label":"Air Flow Rate","unit":"SLPM","section":"gas",
        "aliases":["air","air flow","air_flow","airflow","total flow","total_flow"],"tooltip":"Total air sparged"},
    "o2_flow":     {"label":"Oxygen Flow Rate","unit":"SLPM","section":"gas",
        "aliases":["o2 flow","o2_flow","o2 slpm","o2,slpm","oxygen flow"],"tooltip":"Pure O2 supplementation"},
    "co2_flow":    {"label":"CO2 Flow Rate","unit":"SLPM","section":"gas",
        "aliases":["co2 flow","co2_flow","co2 slpm","co2,slpm","co2_slpm"],"tooltip":"CO2 addition flow"},
    "offgas_o2":   {"label":"Off-gas O2","unit":"%","section":"gas",
        "aliases":["offgas o2","offgas_o2","exhaust o2","our"],"tooltip":"O2% in exhaust — for OUR calculation"},
    "offgas_co2":  {"label":"Off-gas CO2","unit":"%","section":"gas",
        "aliases":["offgas co2","offgas_co2","exhaust co2","cer","co2_off"],"tooltip":"CO2% in exhaust — for CER & RQ"},
    "od":          {"label":"Biomass / OD600","unit":"AU","section":"metabolite",
        "aliases":["od","od600","od_600","absorbance","od600nm","biomass_od","optical density","biomass"],"tooltip":"OD at 600 nm"},
    "dcm":         {"label":"Dry Cell Mass (DCM/CDW)","unit":"g/L","section":"metabolite",
        "aliases":["dcm","cdw","dcw","dry cell","drycell","manual dcm","manualdcm"],"tooltip":"Gravimetric dry cell weight"},
    "vcd":         {"label":"Viable Cell Density / Capacitance","unit":"pF/cm","section":"metabolite",
        "aliases":["vcd","viable","capacitance","viable cell","cell density"],"tooltip":"VCD from probe or counter"},
    "substrate":   {"label":"Substrate (C-source)","unit":"g/L","section":"metabolite",
        "aliases":["glucose","glc","substrate","carbon","sugar","fructose","glycerol","methanol","sucrose","lactose","xylose","arabinose","galactose","mannose","cellobiose","starch","cellulose","maltose","trehalose","acetate","aceticacid","formicacid","formate","pyruvate","sorbitol","mannitol","oil","lipid","fat","oleic","palmitic","fatty acid","vegetable oil","waste oil","cooking oil"]},
    "product":     {"label":"Product / Titer","unit":"g/L","section":"metabolite",
        "aliases":["product","prod","titer","phb","pha","ethanol","succinate","lactate","mva","target","compound","polymer","titre","protease","enzyme","lipase","amylase","cellulase","activity","protein","recombinant","antibody","igg","fab","scfv","gfp","lysine","glutamate","threonine","tryptophan","valine","aminoacid","amino acid","butanol","acetone","isobutanol","propanol","butyrate","citrate","itaconate","fumarate","lipid","fatty acid","fame","tag","triacylglycerol","squalene","carotenoid","astaxanthin","betacarotene","lycopene","mab","monoclonal","bispecific","nanobody","fusion protein","adalimumab","rituximab","trastuzumab"]},
    "nh3":         {"label":"NH3 / Ammonia","unit":"g/L","section":"metabolite",
        "aliases":["nh3","ammonia","nitrogen","nh4","ammonium","nh3 g/l"]},
    "base_vol":    {"label":"Base Addition Volume","unit":"mL","section":"metabolite",
        "aliases":["base","base vol","base_vol","base addition","naoh","koh","nh3 vol"],"tooltip":"Cumulative base for pH control"},
    "acid_vol":    {"label":"Acid Addition Volume","unit":"mL","section":"metabolite",
        "aliases":["acid","acid vol","acid_vol","acid addition","hcl","h2so4"],"tooltip":"Cumulative acid for pH control"},
    "pressure":    {"label":"Pressure","unit":"bar","section":"metabolite",
        "aliases":["pressure","pres","bar","pressure_bar","headspace pressure"]},
    "raman_glucose":   {"label":"Raman — Glucose","unit":"g/L","section":"pat",
        "aliases":["raman glucose","raman_glucose","glucose raman"]},
    "raman_lactate":   {"label":"Raman — Lactate","unit":"g/L","section":"pat",
        "aliases":["raman lactate","raman_lactate","lactate raman"]},
    "raman_glutamine": {"label":"Raman — Glutamine","unit":"mmol/L","section":"pat",
        "aliases":["raman glutamine","glutamine raman","gln raman"]},
    "nir_conc":    {"label":"NIR-derived Concentration","unit":"g/L","section":"pat",
        "aliases":["nir","nir conc","nir_conc","near infrared"]},
    "conductivity":{"label":"Conductivity","unit":"mS/cm","section":"pat",
        "aliases":["conductivity","conduct","cond","conductance"]},
    "pco2":        {"label":"Dissolved CO2 (pCO2)","unit":"mmHg","section":"pat",
        "aliases":["pco2","dissolved co2","pco2_mmhg","dco2"]},
}

MISSING_VALS  = ["-","--","N/A","n/a","NA","#VALUE!","#REF!","#DIV/0!",""]
DATE_PATTERNS = ["dateandtime","dateantime","datetime","datestamp","datum"]

def _is_float(s):
    try: float(s); return True
    except: return False

def _detect_sep(line):
    if "\t" in line: return "\t"
    if ";" in line:  return ";"
    return ","

def _is_date_col(h):
    h2 = h.lower().replace(" ","").replace("_","").replace("-","")
    return any(p in h2 for p in DATE_PATTERNS)

def _norm(s):
    return s.lower().replace(" ","").replace("_","").replace(",","").replace("/","").replace("-","")

def _match_sensor(col, key):
    h = _norm(col)
    for a in SENSORS[key]["aliases"]:
        na = _norm(a)
        if h == na:
            return True
        if na in h:
            # Guard against short aliases matching inside longer words
            # e.g. "ph" should not match "phagl" or "phosphate"
            idx = h.index(na)
            end = idx + len(na)
            # Accept substring match only if alias is at a word boundary
            # (start/end of string, or preceded/followed by a digit or 'g'/'l'
            #  which typically denote units like g/L)
            at_start = idx == 0
            at_end = end == len(h)
            # Check if the next char after the alias is a unit-like boundary
            next_is_boundary = at_end or h[end] in '0123456789'
            prev_is_boundary = at_start or h[idx-1] in '0123456789'
            # Short aliases (<=2 chars) require exact match or unit boundary
            if len(na) <= 2:
                if at_start and next_is_boundary:
                    return True
                # Skip: too short to safely substring-match
                continue
            return True
    return False

def auto_detect_mapping(columns):
    mapping = {}
    for key in SENSORS:
        for col in columns:
            if key == "time" and _is_date_col(col): continue
            if _match_sensor(col, key) and key not in mapping:
                mapping[key] = col; break
    return mapping

@st.cache_data(show_spinner=False)
def parse_file(content, filename):
    ext = filename.rsplit(".",1)[-1].lower()
    if ext in ("xlsx","xls"):
        try:
            engine = "openpyxl" if ext=="xlsx" else "xlrd"
            df = pd.read_excel(io.BytesIO(content), engine=engine,
                               na_values=MISSING_VALS, keep_default_na=True)
            return _clean(df), ""
        except Exception as e:
            return None, f"Excel: {e}"
    try:
        raw = content.decode("utf-8-sig", errors="replace").strip()
    except Exception as e:
        return None, str(e)
    lines = raw.splitlines()
    first = next((l for l in lines if l.strip()), "")
    sep   = _detect_sep(first)
    hidx  = 0
    for i, line in enumerate(lines):
        if not line.strip(): continue
        nxt = next((l for l in lines[i+1:] if l.strip()), "")
        nc  = nxt.split(sep)
        if sum(1 for c in nc if _is_float(c.strip())) >= max(1, len(nc)//2):
            hidx = i; break
    try:
        df = pd.read_csv(io.StringIO("\n".join(lines[hidx:])), sep=sep,
                         encoding_errors="replace", on_bad_lines="skip",
                         na_values=MISSING_VALS, keep_default_na=True)
        return _clean(df), ""
    except Exception as e:
        return None, f"CSV: {e}"

def _clean(df):
    df.columns = [str(c).lstrip("\ufeff").strip().strip('"').strip("'") for c in df.columns]
    seen, new_cols = {}, []
    for col in df.columns:
        if col in seen: seen[col]+=1; new_cols.append(f"{col}_{seen[col]}")
        else: seen[col]=0; new_cols.append(col)
    df.columns = new_cols
    df = df.dropna(axis=1,how="all").dropna(how="all").reset_index(drop=True)
    for col in df.columns:
        conv = pd.to_numeric(df[col], errors="coerce")
        if conv.notna().sum()/max(len(conv),1) > 0.5: df[col] = conv
    return df

def get_arr(df, col_map, field):
    col = col_map.get(field)
    if col and col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        return s.to_numpy(dtype=float) if len(s)>=2 else None
    return None

def render_sensor_sidebar(all_columns=None):
    # If called from app.py with no args, pull columns from session state
    if all_columns is None:
        runs = st.session_state.get("uploaded_runs", {})
        all_columns = []
        for run in runs.values():
            for c in run["df"].columns if isinstance(run, dict) and "df" in run else run.columns:
                if c not in all_columns:
                    all_columns.append(c)
        if not all_columns:
            # No files uploaded yet — show upload prompt in sidebar
            with st.sidebar:
                st.divider()
                st.markdown("### 🗂 Sensor Mapping")
                st.caption("Upload files on the **Data Import** page to enable sensor mapping.")
            return
    opts    = ["— not mapped —"] + all_columns
    col_map = st.session_state.get("col_map", {}).copy()

    def _sel(key):
        s   = SENSORS[key]
        lbl = s["label"] + (f" ({s['unit']})" if s.get("unit") else "")
        cur = col_map.get(key,"— not mapped —")
        if cur not in opts: cur = "— not mapped —"
        sel = st.selectbox(lbl, opts, index=opts.index(cur),
                           key=f"snsr_{key}", help=s.get("tooltip"))
        return None if sel=="— not mapped —" else sel

    with st.sidebar:
        st.markdown("#### ⏱ Time Column")
        topts = ["— not mapped —"]+[c for c in all_columns if not _is_date_col(c)]
        cur_t = col_map.get("time","— not mapped —")
        if cur_t not in topts: cur_t = "— not mapped —"
        sel_t = st.selectbox("Time (h)", topts, index=topts.index(cur_t),
                             key="snsr_time", help="Elapsed time in hours")
        col_map["time"] = sel_t if sel_t!="— not mapped —" else None

        with st.expander("🌡 Core Sensors", expanded=True):
            for k in ["ph","do","temp","rpm","weight"]: col_map[k]=_sel(k)
        with st.expander("💨 Gas & Off-Gas", expanded=False):
            for k in ["air_flow","o2_flow","co2_flow","offgas_o2","offgas_co2"]: col_map[k]=_sel(k)
        with st.expander("🧬 Metabolite & Biomass", expanded=True):
            for k in ["od","dcm","vcd","substrate","product","nh3","base_vol","acid_vol","pressure"]: col_map[k]=_sel(k)
        with st.expander("🔬 Advanced PAT", expanded=False):
            st.caption("Raman, NIR, and inline analysers")
            for k in ["raman_glucose","raman_lactate","raman_glutamine","nir_conc","conductivity","pco2"]: col_map[k]=_sel(k)

    col_map = {k:v for k,v in col_map.items() if v}
    st.session_state.col_map = col_map
    return col_map

def render():
    st.title("📥 Data Import")
    st.caption("Upload fermentation data · Map sensors · Review before analysis")

    with st.expander("📋 Run information", expanded=True):
        c1,c2,c3 = st.columns(3)
        st.session_state.run_name = c1.text_input("Run name / ID *",
            value=st.session_state.run_name or "Run_001", placeholder="e.g. EColi-MVA-R01")
        st.session_state["run_date"]     = c2.text_input("Run date", placeholder="YYYY-MM-DD",
            value=st.session_state.get("run_date",""))
        st.session_state["run_operator"] = c3.text_input("Operator", placeholder="Name or initials",
            value=st.session_state.get("run_operator",""))

        c1,c2,c3,c4 = st.columns(4)
        st.session_state.run_mode = c1.selectbox("Process mode",["Batch","Fed-batch","Continuous"],
            index=["Batch","Fed-batch","Continuous"].index(st.session_state.run_mode))
        st.session_state["reactor_type"] = c2.selectbox("Reactor type",
            ["Stirred tank (STR)","Shake flask","Bubble column","Airlift","Benchtop","Pilot scale"])
        st.session_state["working_vol"]  = c3.number_input("Working volume (L)",0.001,10000.0,
            float(st.session_state.get("working_vol",1.0)),0.01)
        st.session_state["temp_sp"]      = c4.number_input("Temp setpoint (°C)",0.0,80.0,
            float(st.session_state.get("temp_sp",37.0)),0.5)

        c1,c2,c3 = st.columns(3)
        st.session_state["run_organism"] = c1.text_input("Organism / strain",
            placeholder="e.g. E. coli BL21(DE3)", value=st.session_state.get("run_organism",""))
        st.session_state["run_project"]  = c2.text_input("Project",
            placeholder="e.g. MVA Scale-up", value=st.session_state.get("run_project",""))
        st.session_state["run_objective"]= c3.text_input("Objective",
            placeholder="e.g. Optimise feed rate", value=st.session_state.get("run_objective",""))

        c1,c2,c3,c4 = st.columns(4)
        n_sub  = c1.number_input("# substrates",1,5,1)
        n_prod = c2.number_input("# products",1,8,1)
        st.session_state["ph_sp"] = c3.number_input("pH setpoint",0.0,14.0,
            float(st.session_state.get("ph_sp",7.0)),0.1)
        st.session_state["do_sp"] = c4.number_input("DO setpoint (%)",0.0,100.0,
            float(st.session_state.get("do_sp",30.0)),1.0)

        st.session_state.substrates = (["Glucose"] if n_sub==1 else
            [st.columns(int(n_sub))[i].text_input(f"Substrate {i+1}",f"Substrate {i+1}",key=f"sn_{i}") for i in range(int(n_sub))])
        st.session_state.products = (["Product"] if n_prod==1 else
            [st.columns(int(n_prod))[i].text_input(f"Product {i+1}",f"Product {i+1}",key=f"pn_{i}") for i in range(int(n_prod))])
        st.session_state["run_notes"] = st.text_area("Run notes",
            placeholder="Inoculum details, deviations, observations…",
            value=st.session_state.get("run_notes",""), height=55)

    st.subheader("📁 Upload data files")
    st.caption("Supports **.csv · .tsv · .xlsx · .xls** — upload one or multiple runs at once")

    uploaded = st.file_uploader("Drop files here", type=["csv","tsv","txt","xlsx","xls"],
                                accept_multiple_files=True, label_visibility="collapsed")

    if not uploaded:
        st.info("👆 Upload at least one file to begin sensor mapping.")
        with st.expander("📖 Supported formats"):
            st.markdown("""
- **CSV/TSV**: any separator, quoted columns with commas handled, metadata preamble skipped
- **Excel .xlsx/.xls**: first sheet, headers in row 1, empty rows/cols dropped
- **Multi-file**: upload multiple at once; first file = active run; all visible in Comparison tab
- **Missing values**: `-`, `#VALUE!`, `N/A` all treated as blank automatically
- **Minimum required**: Time (hours) + OD600/Biomass column
            """)
        return

    all_dfs, all_cols, errors = {}, [], []
    for f in uploaded:
        df, err = parse_file(f.read(), f.name)
        if err: errors.append(f"❌ {f.name}: {err}")
        else:
            label = f.name.rsplit(".",1)[0]
            all_dfs[label] = {"df": df, "filename": f.name}  # store as dict with "df" key
            for c in df.columns:
                if c not in all_cols: all_cols.append(c)

    for e in errors: st.error(e)
    if not all_dfs: return

    primary_name = list(all_dfs.keys())[0]
    primary_df   = all_dfs[primary_name]["df"]

    # Accumulate runs — do not discard previously uploaded batches
    existing = st.session_state.get("uploaded_runs", {})
    existing.update(all_dfs)
    st.session_state["uploaded_runs"] = existing
    st.session_state.run_data = primary_df
    st.session_state["active_run"] = primary_name
    if not st.session_state.run_name or st.session_state.run_name == "Run_001":
        st.session_state.run_name = primary_name

    # Auto-detect column mapping for any sensor not yet mapped
    existing_map = st.session_state.get("col_map", {})
    detected = auto_detect_mapping(primary_df.columns.tolist())
    merged = {**detected, **existing_map}   # existing manual choices win
    st.session_state.col_map = {k: v for k, v in merged.items() if v and v in primary_df.columns}

    total_runs = len(st.session_state.get("uploaded_runs", {}))
    extra = f"  |  +{len(all_dfs)-1} additional run(s)" if len(all_dfs) > 1 else ""
    st.success(f"✅ **{primary_name}** — {len(primary_df)} rows, {len(primary_df.columns)} columns{extra}"
               f"  |  **{total_runs} batch(es) saved**")

    # Sensor sidebar is rendered globally from app.py
    # Just get current col_map for the summary below
    col_map = st.session_state.get("col_map", {})

    st.subheader("🗺 Mapped sensors")
    if not col_map:
        st.warning("No sensors mapped. Use the sidebar or click **Auto-detect sensors**.")
    else:
        rows = []
        for key, col in col_map.items():
            s = SENSORS.get(key, {})
            if col in primary_df.columns:
                num = pd.to_numeric(primary_df[col], errors="coerce")
                n_valid = int(num.notna().sum())
                sample  = ", ".join(f"{v:.3g}" for v in num.dropna().head(3).tolist())
            else:
                n_valid, sample = 0, "—"
            rows.append({
                "": "✅" if col in primary_df.columns else "⚠️",
                "Sensor": s.get("label",key)+(f" ({s.get('unit','')})" if s.get("unit") else ""),
                "Section": s.get("section","").upper(),
                "Column": col,
                "Valid rows": n_valid,
                "Sample values": sample,
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        missing = [k for k in ["time","od"] if k not in col_map]
        if missing:
            st.warning(f"⚠️ Required sensors not mapped: **{', '.join(missing)}**")
        else:
            st.success("✅ All required sensors mapped — ready for analysis.")
            if st.button("▶ Go to Analysis", type="primary", use_container_width=True):
                st.session_state["nav_page"] = "📊 Analysis"
                st.rerun()

    # ── Save run to persistent storage ───────────────────────────────────────
    with st.expander("💾 Save run to project library", expanded=False):
        metadata = render_run_metadata_form()
        if st.button("💾 Save Run", type="secondary", use_container_width=True):
            dm = st.session_state.get("data_manager")
            if dm:
                # Pass DataFrame directly — DataManager accepts both file and DataFrame
                class _NamedDF:
                    """Thin wrapper so DataManager can read .name for the file extension."""
                    def __init__(self, df, fname):
                        self._df = df
                        self.name = fname
                    def __class_getitem__(cls, _): return cls  # unused

                fname = all_dfs[primary_name].get("filename", f"{primary_name}.csv")
                saved = dm.save_raw_file(_NamedDF(primary_df, fname), metadata)

                # Also persist kinetics if already computed
                mu = st.session_state.get("mu")
                if mu is not None:
                    dm.save_kinetics_results(saved["run_id"], {
                        "mu_max": mu,
                        "doubling_time_min": st.session_state.get("doubling_time_min"),
                        "lag_h": st.session_state.get("lag_time_h"),
                        "titer": st.session_state.get("titer"),
                        "sty": st.session_state.get("sty"),
                    })

                st.success(f"✅ Saved — Run ID: **{saved['run_id']}**")
            else:
                st.error("Data manager not initialised.")

    st.subheader(f"Data preview — {primary_name}")
    t1,t2,t3 = st.tabs(["📊 Raw data","📈 Quick stats",f"📁 All runs ({len(all_dfs)})"])
    with t1:
        st.dataframe(primary_df, use_container_width=True, height=320)
    with t2:
        num = primary_df.select_dtypes(include=np.number)
        if not num.empty: st.dataframe(num.describe().round(4), use_container_width=True)
        else: st.info("No numeric columns detected.")
    with t3:
        if len(all_dfs)>1:
            for name,run in all_dfs.items():
                run_df = run["df"] if isinstance(run, dict) and "df" in run else run
                badge = "🟢" if name==primary_name else "🔵"
                with st.expander(f"{badge} {name} — {len(run_df)} rows"):
                    st.dataframe(run_df.head(5), use_container_width=True)
        else: st.info("Upload multiple files to compare runs here.")
