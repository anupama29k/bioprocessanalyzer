"""Data Import page — universal parser for all instrument formats."""
import streamlit as st
import pandas as pd
import numpy as np
import io, json, re
from modules import session

ASSAY_METHODS = ["HPLC-RI (Aminex)", "HPLC-UV/DAD", "GC-FID", "GC-MS",
                 "Enzymatic", "DNS colorimetric", "Refractometer", "Other"]

TEMPLATES = {
    "Full profile (CSV)": "Time,OD600,Glucose,Product,Acetate,pH,DO\n0,0.05,20.0,0.00,0.00,7.00,100\n2,0.15,18.2,0.00,0.00,7.00,95\n4,0.55,14.5,0.02,0.05,6.98,80\n6,1.40,9.3,0.10,0.15,6.95,55\n8,2.80,4.1,0.35,0.30,6.90,32\n10,4.20,1.5,0.80,0.50,6.88,28\n12,5.50,0.4,1.40,0.70,6.85,30\n16,6.80,0.08,2.20,0.80,6.80,30\n20,7.20,0.03,2.75,0.80,6.78,30\n24,7.40,0.01,3.10,0.80,6.75,30",
    "OD only": "Time,OD600\n0,0.05\n2,0.15\n4,0.55\n6,1.40\n8,2.80\n12,5.50\n16,6.80\n20,7.20\n24,7.40",
    "Sartorius MFCS": "Batch ID:,BATCH_001\n\nTime [h],pH [-],pO2 [%],Temperature [°C],Stirrer speed [rpm]\n0.000,7.002,100.0,37.01,200\n0.500,6.995,95.2,37.00,210\n1.000,6.985,88.1,37.01,220\n4.000,6.930,45.2,37.01,280\n8.000,6.898,30.5,37.01,290\n12.000,6.880,30.0,37.00,290\n16.000,6.862,30.2,37.01,290\n24.000,6.848,30.0,37.00,290",
    "Eppendorf DASware": "Run Name:\tECOLI_001\n\nDate\tTime\tV1_pH_Value\tV1_DO_Value\tV1_Temp_Value\tV1_Stirrer_Value\n15.03.2024\t09:00:00\t7.002\t100.0\t37.01\t200\n15.03.2024\t09:30:00\t6.998\t94.5\t37.00\t210\n15.03.2024\t11:00:00\t6.965\t70.1\t37.00\t255\n15.03.2024\t13:00:00\t6.940\t44.8\t37.01\t283\n15.03.2024\t15:00:00\t6.918\t31.5\t37.00\t293\n16.03.2024\t09:00:00\t6.855\t30.0\t37.00\t295",
    "Infors HT eve": "Run_ID;LABFORS5_001\n\nTime[h];pH;DO[%];T[°C];N[rpm]\n0.000;7.001;100.0;37.00;200\n0.500;6.996;95.0;37.01;212\n1.000;6.986;87.8;37.00;228\n4.000;6.932;44.1;37.00;282\n8.000;6.900;30.3;37.00;293\n12.000;6.882;30.1;37.01;293\n24.000;6.850;30.1;37.01;293",
    "JSON export": '{"time":[0,2,4,6,8,10,12,16,20,24],"od":[0.05,0.15,0.55,1.40,2.80,4.20,5.50,6.80,7.20,7.40],"glucose":[20.0,18.2,14.5,9.3,4.1,1.5,0.4,0.08,0.03,0.01],"product":[0,0,0.02,0.10,0.35,0.80,1.40,2.20,2.75,3.10],"ph":[7.0,7.0,6.98,6.95,6.90,6.88,6.85,6.80,6.78,6.75],"do":[100,95,80,55,32,28,30,30,30,30],"our":8.5,"cer":9.2}',
}

COL_ALIASES = {
    "time":     ["time","t","h","hours","elapsed","zeit","t_h","time_h","process_time",
                 "elapsed time_h","elapsed_time_h","elapsedtime_h"],
    "od":       ["od","od600","od_600","abs","absorbance","od600nm","biomass_od"],
    "glucose":  ["glucose","glc","substrate","carbon","sugar","s","csource"],
    "product":  ["product","prod","titer","mva","ethanol","succinate","lactate","target","compound",
                 "nh3","nh3,g/l"],
    "acetate":  ["acetate","ac","ace","acoh"],
    "ethanol":  ["ethanol","etoh","etol"],
    "ph":       ["ph","ph_value","ph[-]","ph_actual","v1_ph_value"],
    "do":       ["do","do%","po2","pO2","do_value","dissolved_o2","do_pct","v1_do_value"],
    "temp":     ["temp","temperature","t[c]","t[°c]","tic","v1_temp_value","temperature_value"],
    "rpm":      ["rpm","stirrer","agitation","stirrerspeed","stirrer_speed","n[rpm]","v1_stirrer_value"],
    "our":      ["our","o2_uptake","oxygen_uptake_rate","o2,slpm","o2slpm"],
    "cer":      ["cer","co2_evolution","co2_evolution_rate","co2,slpm","co2slpm"],
    "dcm":      ["manualdcm","manual dcm","manualdcm,g/l","dcm","drycellweight"],
    "mu":       ["specificgrowthratesinastart","specificgrowthrate","mu","growthrate"],
}

def _detect_sep(line):
    if "\t" in line: return "\t"
    if ";" in line:  return ";"
    return ","

def _parse_datetime_eppendorf(date_str, time_str):
    try:
        parts = date_str.strip().split(".")
        if len(parts)==3:
            dd,mm,yyyy = parts
            return pd.Timestamp(f"{yyyy}-{mm}-{dd} {time_str.strip()}")
    except: pass
    return None

def _match_col(header, field):
    h = header.lower().strip().replace(" ","").replace("_","").replace("-","").replace("[","").replace("]","")
    for alias in COL_ALIASES.get(field, []):
        a = alias.lower().replace("_","").replace("[","").replace("]","")
        if h == a or h.startswith(a) or a in h:
            return True
    return False

def _find_col(headers, field):
    for i, h in enumerate(headers):
        if _match_col(h, field):
            return i
    return -1

def _is_float(s):
    try: float(s); return True
    except: return False


def parse_raw(raw: str):
    raw = raw.strip()
    if not raw:
        return None, "Empty input"

    # Strip BOM
    if raw.startswith("\ufeff"):
        raw = raw[1:]

    # JSON
    try:
        j = json.loads(raw)
        return parse_json(j), None
    except:
        pass

    # Detect separator from first non-empty line
    first_line = next((l for l in raw.splitlines() if l.strip()), "")
    sep = _detect_sep(first_line)

    # Find the header row — skip metadata lines at the top
    # (lines with fewer than 2 sep-separated cells or that look like key:value pairs)
    lines = raw.splitlines()
    header_idx = 0
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        cells = line.split(sep)
        if len(cells) < 2:
            continue
        # Check if next non-empty line is mostly numeric — if so this is our header
        next_data = next((l for l in lines[i+1:] if l.strip()), "")
        next_cells = next_data.split(sep)
        nums = sum(1 for c in next_cells if _is_float(c.strip()))
        if nums >= max(1, len(next_cells) // 2):
            header_idx = i
            break

    # Reconstruct from header row onwards for pandas to parse
    body = "\n".join(lines[header_idx:])

    try:
        df = pd.read_csv(
            io.StringIO(body),
            sep=sep,
            encoding_errors="replace",
            on_bad_lines="skip",
        )
    except Exception as e:
        return None, f"CSV parse error: {e}"

    if df.empty:
        return None, "No data found"

    # Clean column names (strip BOM, whitespace, quotes)
    df.columns = [str(c).lstrip("\ufeff").strip().strip('"').strip("'") for c in df.columns]

    # Deduplicate column names
    seen = {}
    new_cols = []
    for col in df.columns:
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    df.columns = new_cols

    # Drop fully empty columns (trailing commas etc.)
    df = df.dropna(axis=1, how="all")

    # Drop rows that are entirely NaN
    df = df.dropna(how="all").reset_index(drop=True)

    # Convert numeric columns
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="ignore")
        except Exception:
            pass

    # Eppendorf wall-clock: Date + Time columns
    headers = list(df.columns)
    date_idx = -1
    for i, h in enumerate(headers):
        if h.lower() in ["date", "datum"]:
            date_idx = i
            break
    if date_idx >= 0:
        time_idx2 = -1
        for i, h in enumerate(headers):
            if h.lower() in ["time", "zeit"] and i != date_idx:
                time_idx2 = i
                break
        if time_idx2 >= 0:
            stamps = []
            for _, row in df.iterrows():
                ts = _parse_datetime_eppendorf(
                    str(row.iloc[date_idx]), str(row.iloc[time_idx2])
                )
                stamps.append(ts)
            stamps = [s for s in stamps if s is not None]
            if len(stamps) == len(df):
                t0 = stamps[0]
                df["time"] = [(s - t0).total_seconds() / 3600 for s in stamps]

    # Infors: time in seconds → convert to hours
    time_col = next((c for c in df.columns if _match_col(c, "time")), None)
    if time_col and time_col in df.columns:
        tv = pd.to_numeric(df[time_col], errors="coerce").dropna()
        if len(tv) > 0 and tv.max() > 500:
            df[time_col] = pd.to_numeric(df[time_col], errors="coerce") / 3600

    return build_result(df, list(df.columns)), None

def parse_json(j):
    AL = {"time":["time","t","hours"],"od":["od","od600"],"glucose":["glucose","glc","substrate"],
          "product":["product","prod","titer","mva"],"acetate":["acetate","ac"],
          "ph":["ph"],"do":["do","po2","dissolved_o2"],"our":["our"],"cer":["cer"]}
    found = {}
    for k, v in j.items():
        kl = k.lower()
        for field, alts in AL.items():
            if any(kl==a or kl.startswith(a) for a in alts):
                found[field] = v; break
    if "od" not in found and "time" not in found:
        return None
    n = len(found.get("time") or found.get("od",[]))
    if "time" not in found:
        found["time"] = list(range(n))
    df = pd.DataFrame({k: v for k,v in found.items() if isinstance(v, list)})
    scalars = {k:v for k,v in found.items() if not isinstance(v,list)}
    return {"df": df, "scalars": scalars, "col_map": {k:k for k in df.columns}, "source":"JSON"}

def build_result(df, headers):
    col_map = {}
    for field in ["time","od","glucose","product","acetate","ethanol","ph","do","temp","rpm","our","cer"]:
        idx = _find_col(headers, field)
        if idx >= 0 and idx < len(headers):
            col_map[field] = headers[idx]
    return {"df": df, "col_map": col_map, "scalars": {}, "source": "tabular"}


def render():
    st.title("📥 Data Import")
    st.caption("Paste data from any instrument — auto-detected format with flexible column mapping")

    # ── Run metadata ──────────────────────────────────────────────────────────
    with st.expander("⚙️ Run setup", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        st.session_state.run_name = c1.text_input("Run name", value=st.session_state.run_name or "Run_001")
        st.session_state.run_mode = c2.selectbox("Process mode", ["Batch","Fed-batch","Continuous"],
                                                  index=["Batch","Fed-batch","Continuous"].index(st.session_state.run_mode))
        n_sub  = c3.number_input("# substrates", 1, 5, 1)
        n_prod = c4.number_input("# products / metabolites", 1, 8, 1)

        sub_names  = []
        prod_names = []
        if n_sub > 1:
            st.caption("Substrate names:")
            cols = st.columns(int(n_sub))
            for i, col in enumerate(cols):
                sub_names.append(col.text_input(f"Substrate {i+1}", value=f"Substrate {i+1}", key=f"sname_{i}"))
        else:
            sub_names = ["Glucose"]

        if n_prod > 1:
            st.caption("Product / metabolite names:")
            cols = st.columns(int(n_prod))
            for i, col in enumerate(cols):
                prod_names.append(col.text_input(f"Product {i+1}", value=f"Product {i+1}", key=f"pname_{i}"))
        else:
            prod_names = ["Product"]

        st.session_state.substrates = sub_names
        st.session_state.products   = prod_names

    # ── Paste / upload ────────────────────────────────────────────────────────
    tab_paste, tab_upload, tab_map = st.tabs(["Paste data", "Upload file", "Column mapper"])

    with tab_paste:
        tpl_key = st.selectbox("Load template", ["— select —"]+list(TEMPLATES.keys()))
        default_txt = TEMPLATES.get(tpl_key, "") if tpl_key != "— select —" else st.session_state.get("paste_text","")
        raw = st.text_area("Paste data here (CSV, TSV, semicolon, JSON, any format)",
                           value=default_txt, height=220, key="paste_area")
        if st.button("🔍 Auto-detect & parse", type="primary"):
            _run_parse(raw)

    with tab_upload:
        ufile = st.file_uploader("Drop file (.csv .tsv .txt .json)", type=["csv","tsv","txt","json"])
        if ufile:
            raw_u = ufile.read().decode("utf-8", errors="replace")
            st.text_area("File contents preview", raw_u[:1000], height=150)
            if st.button("Parse uploaded file", type="primary"):
                _run_parse(raw_u)

    with tab_map:
        _render_col_mapper()

    # ── Assay integration ─────────────────────────────────────────────────────
    with st.expander("🔬 Assay integration (HPLC, GC-MS, etc.)", expanded=False):
        c1, c2 = st.columns(2)
        st.session_state["assay_substrate"] = c1.selectbox("Substrate assay method", ASSAY_METHODS)
        st.session_state["assay_product"]   = c2.selectbox("Product assay method",   ASSAY_METHODS)
        st.session_state["assay_notes"]     = st.text_area("Assay notes / column IDs / retention times", height=70,
            placeholder="e.g. MVA RT=12.3min on Aminex HPX-87H; glucose enzymatic kit.")

    # ── Show parsed preview ───────────────────────────────────────────────────
    if st.session_state.run_data is not None:
        st.divider()
        st.success(f"✅ Run **{st.session_state.run_name}** loaded — {len(st.session_state.run_data)} rows")
        st.dataframe(st.session_state.run_data.head(10), use_container_width=True)


def _run_parse(raw):
    result, err = parse_raw(raw)
    if err or result is None:
        st.error(f"Parse failed: {err or 'unknown error'}")
        return
    df  = result["df"]
    cm  = result["col_map"]
    sca = result.get("scalars", {})
    if df is None or df.empty:
        st.error("No data extracted from input")
        return
    st.session_state.run_data = df
    st.session_state.col_map  = cm
    if "our" in sca: st.session_state["our_val"] = sca["our"]
    if "cer" in sca: st.session_state["cer_val"] = sca["cer"]
    found = ", ".join(f"{f}→{c}" for f,c in cm.items())
    st.success(f"Parsed {len(df)} rows. Mapped: {found}")
    st.session_state["paste_text"] = raw


def _render_col_mapper():
    df = st.session_state.run_data
    if df is None:
        st.info("Parse data first to see column mapper.")
        return
    st.caption("Remap columns if auto-detection was wrong:")
    cols_available = ["— none —"] + list(df.columns)
    cm = st.session_state.col_map.copy()
    new_cm = {}
    fields = ["time","od","glucose","product","acetate","ethanol","ph","do","temp","rpm","our","cer"]
    rows = [fields[:4], fields[4:8], fields[8:]]
    for row_fields in rows:
        cols = st.columns(len(row_fields))
        for col, field in zip(cols, row_fields):
            cur = cm.get(field, "— none —")
            if cur not in cols_available: cur = "— none —"
            sel = col.selectbox(field, cols_available,
                                index=cols_available.index(cur) if cur in cols_available else 0,
                                key=f"cm_{field}")
            if sel != "— none —":
                new_cm[field] = sel
    if st.button("Apply column mapping"):
        st.session_state.col_map = new_cm
        st.success("Column mapping applied.")
