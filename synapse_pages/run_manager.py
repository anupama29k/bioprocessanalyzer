"""
Run Manager — Unified module replacing Live Run + Batch History.

Seven horizontal tabs:
  1. Setup        — create a new run
  2. Live Acquisition — Pulse + offline entry + timeline
  3. Analysis     — growth kinetics, yields, soft sensors
  4. Comparison   — overlay runs, divergence, radar, multi-run
  5. Scale-Up     — pre-populated from live data
  6. Digital Twin — ODE fitting from Supabase
  7. Archive      — full record, export, notes, outcome
"""
import json, io, math
from datetime import datetime, date, timedelta, timezone

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Constants ────────────────────────────────────────────────────────────────
ORGANISMS = [
    "CHO", "CHO-S", "HEK293", "E. coli",
    "Pichia pastoris", "S. cerevisiae", "NS0", "Sp2/0", "BHK-21",
]

ONLINE_PARAMS = {
    "pH":          ("pH",          ""),
    "DO":          ("DO",          "%"),
    "Temperature": ("temperature", "°C"),
    "Agitation":   ("agitation",   "rpm"),
    "OD600":       ("OD600",       "AU"),
    "DCM":         ("DCM",         "g/L"),
    "VCD":         ("VCD",         "x10^6 cells/mL"),
    "Glucose":     ("glucose",     "g/L"),
    "Titer":       ("titer",       "g/L"),
    "Ammonia":     ("ammonia",     "mM"),
    "Air Flow":    ("air_flow",    "SLPM"),
    "O2 Flow":     ("O2_flow",     "SLPM"),
    "CO2 Flow":    ("CO2_flow",    "SLPM"),
    "Off-gas O2":  ("offgas_O2",   "%"),
    "Off-gas CO2": ("offgas_CO2",  "%"),
    "Weight":      ("weight",      "g"),
    "Base Vol":    ("base_vol",    "mL"),
    "Acid Vol":    ("acid_vol",    "mL"),
    "Pressure":    ("pressure",    "bar"),
    "Conductivity":("conductivity","mS/cm"),
    "pCO2":        ("pCO2",        "mmHg"),
    "Raman Glucose":   ("raman_glucose",   "g/L"),
    "Raman Lactate":   ("raman_lactate",   "g/L"),
    "Raman Glutamine": ("raman_glutamine", "g/L"),
    "NIR Conc":        ("NIR_conc",        "g/L"),
}

OFFLINE_PARAMS = {
    "pH":          ("pH",          ""),
    "DO":          ("DO",          "%"),
    "Glucose":     ("glucose",     "g/L"),
    "Lactate":     ("lactate",     "g/L"),
    "Ammonia":     ("ammonia",     "mM"),
    "VCD":         ("VCD",         "x10^6 cells/mL"),
    "Viability":   ("viability",   "%"),
    "Titer":       ("titer",       "g/L"),
    "CO2":         ("CO2",         "%"),
    "O2":          ("O2",          "%"),
    "Temperature": ("temperature", "°C"),
    "Agitation":   ("agitation",   "rpm"),
}

SCALING_CRITERIA = ["Constant P/V", "Constant Tip Speed", "Constant kLa",
                    "Constant Re", "Constant Mixing Time"]


# ═══════════════════════════════════════════════════════════════════════════════
#  SUPABASE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def _sb():
    return st.session_state.get("supabase")


@st.cache_data(ttl=15)
def _fetch_all_batches(_sb_id):
    sb = _sb()
    if sb is None:
        return []
    return sb.table("batches").select("*").order("created_at", desc=True).execute().data or []


def _fetch_measurements(batch_id):
    sb = _sb()
    if sb is None:
        return pd.DataFrame()
    data = (
        sb.table("process_measurements")
        .select("*")
        .eq("batch_id", batch_id)
        .order("day_of_run")
        .execute()
        .data or []
    )
    return pd.DataFrame(data) if data else pd.DataFrame()


def _invalidate():
    _fetch_all_batches.clear()


def _safe_col(sb, table, col, val):
    """Try to write a column; return True if it exists."""
    try:
        sb.table(table).select(col).limit(0).execute()
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — SETUP
# ═══════════════════════════════════════════════════════════════════════════════
def _tab_setup(batches):
    st.subheader("Create New Run")

    # Golden batch reference options
    golden_opts = ["— None —"] + [b["batch_code"] for b in batches]

    with st.form("rm_setup_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            batch_code = st.text_input("Batch Code *", placeholder="BX-2026-042")
            organism = st.selectbox("Organism *", ORGANISMS)
            product_type = st.text_input("Product Type", placeholder="mAb, Vaccine, Enzyme")
        with c2:
            scale = st.number_input("Scale (L)", min_value=0.0, step=0.1, format="%.1f")
            vessel = st.text_input("Vessel", placeholder="2L STR, 50L SUB")
            operator = st.text_input("Operator", placeholder="Name")
        with c3:
            start_date = st.date_input("Start Date", value=date.today())
            golden_ref = st.selectbox("Golden Batch Reference", golden_opts)
            protocol_notes = st.text_area("Protocol Notes", height=80)

        submitted = st.form_submit_button("Create Run", type="primary", use_container_width=True)

    if submitted:
        sb = _sb()
        if sb is None:
            st.error("Supabase not connected.")
            return
        if not batch_code.strip():
            st.warning("Batch Code is required.")
            return

        row = {
            "batch_code": batch_code.strip(),
            "organism": organism,
            "product_type": product_type.strip(),
            "scale_liters": scale if scale > 0 else None,
            "start_date": start_date.isoformat(),
        }
        # Pack extended fields into notes as JSON (until migration adds columns)
        extra = {}
        if vessel.strip():
            extra["vessel"] = vessel.strip()
        if operator.strip():
            extra["operator"] = operator.strip()
        if golden_ref != "— None —":
            extra["golden_batch_ref"] = golden_ref
        if protocol_notes.strip():
            extra["protocol_notes"] = protocol_notes.strip()
        row["notes"] = json.dumps(extra) if extra else ""

        row = {k: v for k, v in row.items() if v is not None and v != ""}
        try:
            resp = sb.table("batches").insert(row).execute()
            new_id = resp.data[0]["id"]
            st.session_state["rm_active_batch_id"] = new_id
            st.success(f"Run **{batch_code}** created. Switch to **Live Acquisition** to start logging.")
            _invalidate()
        except Exception as exc:
            msg = str(exc)
            if "duplicate" in msg.lower() or "unique" in msg.lower():
                st.error(f"Batch **{batch_code}** already exists.")
            else:
                st.error(f"Failed: {msg}")

    # Quick-view existing batches
    if batches:
        st.divider()
        st.caption("Recent runs")
        cols_map = {"batch_code": "Batch", "organism": "Organism", "product_type": "Product",
                    "scale_liters": "Scale (L)", "start_date": "Start", "created_at": "Created"}
        rows = [{v: b.get(k, "") for k, v in cols_map.items()} for b in batches[:10]]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — LIVE ACQUISITION  (charts + Pulse + offline entry)
# ═══════════════════════════════════════════════════════════════════════════════

# Threshold definitions: (low_critical, low_ok, high_ok, high_critical)
# Values inside ok range → green, between ok and critical → amber, outside → red
_THRESHOLDS = {
    "VCD":         (3.0,  8.0,  18.0, 25.0),
    "viability":   (75,   85,   100,  100),
    "glucose":     (0.5,  1.0,  6.0,  8.0),
    "lactate":     (0,    0,    3.0,  5.0),
    "ammonia":     (0,    0,    5.0,  7.0),
    "titer":       (0,    0,    999,  999),
    "pH":          (6.85, 6.9,  7.2,  7.4),
    "DO":          (20,   30,   50,   65),
    "temperature": (35.5, 36.5, 37.5, 38.5),
    "agitation":   (80,   100,  300,  400),
    "CO2":         (0,    0,    60,   80),
    "O2":          (10,   15,   30,   35),
}


def _badge_state(param, value, context=None):
    """Return (label, color_hex) for a value.

    context is an optional dict with sibling parameter values for
    cross-parameter logic (e.g. VCD declining detection).
    """
    ctx = context or {}

    # ── VCD context-aware logic ──
    if param == "VCD":
        if value < 3.0:
            return "critical", "#F44336"
        titer_val = ctx.get("titer")
        if value < 8.0 and titer_val is not None and titer_val > 2.0:
            return "declining", "#FF9800"

    t = _THRESHOLDS.get(param)
    if t is None:
        return "optimal", "#4CAF50"
    low_crit, low_ok, high_ok, high_crit = t
    if low_ok <= value <= high_ok:
        return "optimal", "#4CAF50"
    if low_crit <= value <= high_crit:
        return "warning", "#FF9800"
    return "critical", "#F44336"


def _badge_html(param, value, unit, context=None):
    """Render a small colored badge for a parameter."""
    state, color = _badge_state(param, value, context)
    return (
        f'<span style="display:inline-block;padding:2px 10px;margin:2px;'
        f'border-radius:12px;background:{color};color:#fff;font-size:13px;'
        f'font-weight:600;">{param}: {value:.2f} {unit} — {state}</span>'
    )


def _get_series(df, param):
    """Extract sorted day vs value for a parameter."""
    s = df[df["parameter_name"] == param][["day_of_run", "value"]].dropna()
    return s.sort_values("day_of_run").reset_index(drop=True)


def _chart_layout(fig, height=300):
    """Apply shared clean layout to a Plotly figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=5, r=5, t=30, b=5),
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font_size=11),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eee", title_text="Day of Run", dtick=1)
    fig.update_yaxes(showgrid=True, gridcolor="#eee")
    return fig


def _add_current_day_line(fig, current_day):
    """Add a thin vertical red dashed line at the current day."""
    fig.add_vline(x=current_day, line_dash="dash", line_color="red", line_width=1,
                  annotation_text="now", annotation_position="top right",
                  annotation_font_size=10, annotation_font_color="red")


def _render_badges(df, params_with_units):
    """Render status badges for the latest value of each parameter."""
    # Build context dict with latest values for cross-parameter logic
    context = {}
    for param, _unit in params_with_units:
        s = _get_series(df, param)
        if not s.empty:
            context[param] = s["value"].iloc[-1]

    badges = []
    for param, unit in params_with_units:
        if param in context:
            badges.append(_badge_html(param, context[param], unit, context))
    if badges:
        st.markdown(" ".join(badges), unsafe_allow_html=True)


def _render_dashboard_charts(df, current_day):
    """Render the 6-chart dashboard: Cell Health (left) + Process Conditions (right)."""

    # Divider CSS: thin vertical line between columns
    st.markdown(
        """<style>
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
            border-left: 1px solid #ddd;
            padding-left: 1rem;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 1 — CELL HEALTH
    # ══════════════════════════════════════════════════════════════════════
    with left:
        st.markdown("**Cell Health Monitor**")
        _render_badges(df, [
            ("VCD", "e6/mL"), ("viability", "%"), ("glucose", "g/L"),
            ("lactate", "g/L"), ("ammonia", "mM"), ("titer", "g/L"),
        ])

        # ── Chart 1: VCD + Viability (dual Y) ──
        vcd = _get_series(df, "VCD")
        viab = _get_series(df, "viability")
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        if not vcd.empty:
            fig1.add_trace(go.Scatter(
                x=vcd["day_of_run"], y=vcd["value"], name="VCD",
                line=dict(color="#1976D2", width=2), mode="lines+markers", marker_size=5,
            ), secondary_y=False)
        if not viab.empty:
            fig1.add_trace(go.Scatter(
                x=viab["day_of_run"], y=viab["value"], name="Viability",
                line=dict(color="#43A047", width=2, dash="dot"), mode="lines+markers", marker_size=5,
            ), secondary_y=True)
        fig1.update_yaxes(title_text="VCD (×10⁶ cells/mL)", secondary_y=False, color="#1976D2")
        fig1.update_yaxes(title_text="Viability (%)", secondary_y=True, color="#43A047", range=[0, 105])
        _add_current_day_line(fig1, current_day)
        _chart_layout(fig1)
        st.plotly_chart(fig1, use_container_width=True)

        # ── Chart 2: Glucose + Lactate (same axis) ──
        glc = _get_series(df, "glucose")
        lac = _get_series(df, "lactate")
        fig2 = go.Figure()
        if not glc.empty:
            fig2.add_trace(go.Scatter(
                x=glc["day_of_run"], y=glc["value"], name="Glucose",
                line=dict(color="#1976D2", width=2), mode="lines+markers", marker_size=5,
            ))
        if not lac.empty:
            fig2.add_trace(go.Scatter(
                x=lac["day_of_run"], y=lac["value"], name="Lactate",
                line=dict(color="#E53935", width=2), mode="lines+markers", marker_size=5,
            ))
        fig2.update_yaxes(title_text="Concentration (g/L)")
        _add_current_day_line(fig2, current_day)
        _chart_layout(fig2)
        st.plotly_chart(fig2, use_container_width=True)

        # ── Chart 3: Ammonia + Titer (dual Y) ──
        nh3 = _get_series(df, "ammonia")
        tit = _get_series(df, "titer")
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        if not nh3.empty:
            fig3.add_trace(go.Scatter(
                x=nh3["day_of_run"], y=nh3["value"], name="Ammonia",
                line=dict(color="#E53935", width=2), mode="lines+markers", marker_size=5,
            ), secondary_y=False)
        if not tit.empty:
            fig3.add_trace(go.Scatter(
                x=tit["day_of_run"], y=tit["value"], name="Titer",
                line=dict(color="#43A047", width=2), mode="lines+markers", marker_size=5,
            ), secondary_y=True)
        fig3.update_yaxes(title_text="Ammonia (mM)", secondary_y=False, color="#E53935")
        fig3.update_yaxes(title_text="Titer (g/L)", secondary_y=True, color="#43A047")
        _add_current_day_line(fig3, current_day)
        _chart_layout(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 2 — PROCESS CONDITIONS
    # ══════════════════════════════════════════════════════════════════════
    with right:
        st.markdown("**Process Conditions**")
        _render_badges(df, [
            ("pH", ""), ("DO", "%"), ("temperature", "°C"),
            ("agitation", "rpm"), ("CO2", "mmHg"), ("O2", "mmHg"),
        ])

        # ── Chart 4: pH with 6.9-7.2 target band ──
        ph = _get_series(df, "pH")
        fig4 = go.Figure()
        fig4.add_hrect(y0=6.9, y1=7.2, fillcolor="#C8E6C9", opacity=0.4,
                       line_width=0, annotation_text="Target", annotation_position="top left",
                       annotation_font_size=10, annotation_font_color="#388E3C")
        if not ph.empty:
            fig4.add_trace(go.Scatter(
                x=ph["day_of_run"], y=ph["value"], name="pH",
                line=dict(color="#7B1FA2", width=2), mode="lines+markers", marker_size=5,
            ))
        fig4.update_yaxes(title_text="pH")
        _add_current_day_line(fig4, current_day)
        _chart_layout(fig4)
        st.plotly_chart(fig4, use_container_width=True)

        # ── Chart 5: DO with 30-50% target band ──
        do_s = _get_series(df, "DO")
        fig5 = go.Figure()
        fig5.add_hrect(y0=30, y1=50, fillcolor="#BBDEFB", opacity=0.4,
                       line_width=0, annotation_text="Target", annotation_position="top left",
                       annotation_font_size=10, annotation_font_color="#1565C0")
        if not do_s.empty:
            fig5.add_trace(go.Scatter(
                x=do_s["day_of_run"], y=do_s["value"], name="DO",
                line=dict(color="#0288D1", width=2), mode="lines+markers", marker_size=5,
            ))
        fig5.update_yaxes(title_text="Dissolved O₂ (%)")
        _add_current_day_line(fig5, current_day)
        _chart_layout(fig5)
        st.plotly_chart(fig5, use_container_width=True)

        # ── Chart 6: Temperature + Agitation (dual Y) ──
        temp = _get_series(df, "temperature")
        agit = _get_series(df, "agitation")
        fig6 = make_subplots(specs=[[{"secondary_y": True}]])
        if not temp.empty:
            fig6.add_trace(go.Scatter(
                x=temp["day_of_run"], y=temp["value"], name="Temperature",
                line=dict(color="#E53935", width=2), mode="lines+markers", marker_size=5,
            ), secondary_y=False)
        if not agit.empty:
            fig6.add_trace(go.Scatter(
                x=agit["day_of_run"], y=agit["value"], name="Agitation",
                line=dict(color="#1976D2", width=2, dash="dot"), mode="lines+markers", marker_size=5,
            ), secondary_y=True)
        fig6.update_yaxes(title_text="Temperature (°C)", secondary_y=False, color="#E53935")
        fig6.update_yaxes(title_text="Agitation (rpm)", secondary_y=True, color="#1976D2")
        _add_current_day_line(fig6, current_day)
        _chart_layout(fig6)
        st.plotly_chart(fig6, use_container_width=True)


def _tab_live_acquisition(batch, all_batches):
    if batch is None:
        st.info("Select or create a run first.")
        return

    batch_id = batch["id"]
    st.session_state["pulse_batch_id"] = batch_id

    # ── Fetch data and render dashboard ──
    df = _fetch_measurements(batch_id)
    if not df.empty:
        current_day = df["day_of_run"].max()
        source_counts = df.get("instrument_source", pd.Series(dtype=str)).value_counts()
        online_n = source_counts.get("online", 0)
        offline_n = source_counts.get("offline", 0)
        other_n = len(df) - online_n - offline_n
        st.caption(f"{len(df)} measurements — Online: {online_n} | Offline: {offline_n} | Other: {other_n}")
        _render_dashboard_charts(df, current_day)
    else:
        st.info("No measurements yet. Use the forms below to start logging.")

    st.divider()

    # ── Two columns: Pulse status (left) + Offline entry (right) ──
    left, right = st.columns(2)

    # LEFT — Pulse live feed status
    with left:
        st.subheader("Online — Pulse Sensor Feed")

        pulse_err = st.session_state.get("_pulse_last_error")
        pulse_last = st.session_state.get("_pulse_last_write")
        pulse_count = st.session_state.get("_pulse_last_count", 0)

        if pulse_err:
            st.error(f"Pulse error: {pulse_err}")
        elif pulse_last:
            try:
                ts = datetime.fromisoformat(pulse_last).astimezone().strftime("%H:%M:%S")
            except Exception:
                ts = pulse_last
            st.success(f"Pulse active — last write: {ts} ({pulse_count} params)")
        else:
            st.warning("Pulse waiting — load a data file in the sensor sidebar to start.")

        run_data = st.session_state.get("run_data")
        col_map = st.session_state.get("col_map", {})
        if run_data is not None and col_map:
            mapped = [k for k, v in col_map.items() if v]
            st.caption(f"Mapped sensors: {', '.join(mapped)}")
            st.caption(f"Data rows: {len(run_data)} | Writing every 60s")
        else:
            st.caption("No sensor data loaded. Use **Data Import** sidebar to upload a file.")

    # RIGHT — Offline measurement entry
    with right:
        st.subheader("Offline — Manual Entry")
        param_names = list(OFFLINE_PARAMS.keys())

        with st.form("rm_offline_form", clear_on_submit=True):
            param_display = st.selectbox("Parameter *", param_names)
            db_name, default_unit = OFFLINE_PARAMS[param_display]
            c1, c2 = st.columns(2)
            with c1:
                value = st.number_input("Value *", format="%.4f")
                unit = st.text_input("Unit", value=default_unit)
            with c2:
                day_of_run = st.number_input("Day of Run *", min_value=0.0, step=0.5, format="%.2f")
                instrument = st.text_input("Instrument", placeholder="BioProfile FLEX2")

            submitted = st.form_submit_button("Log Measurement", type="primary", use_container_width=True)

        if submitted:
            sb = _sb()
            if sb is None:
                st.error("Supabase not connected.")
                return
            row = {
                "batch_id": batch_id,
                "parameter_name": db_name,
                "value": value,
                "unit": unit.strip() if unit.strip() else None,
                "day_of_run": day_of_run,
                "instrument": instrument.strip() if instrument.strip() else None,
            }
            if _safe_col(sb, "process_measurements", "instrument_source", "offline"):
                row["instrument_source"] = "offline"
            row = {k: v for k, v in row.items() if v is not None}
            try:
                sb.table("process_measurements").insert(row).execute()
                st.success(f"Logged **{param_display} = {value} {unit}** at day {day_of_run}")
            except Exception as exc:
                st.error(f"Failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
def _get_param_series(df, param_name):
    """Extract day_of_run vs value for a single parameter, sorted."""
    sub = df[df["parameter_name"] == param_name][["day_of_run", "value"]].dropna()
    sub = sub.sort_values("day_of_run").reset_index(drop=True)
    sub.columns = ["day", "value"]
    return sub


def _compute_mu_max(biomass_df):
    """Estimate mu_max from the true exponential phase only.

    Strategy:
    1. Find peak VCD day — everything after is decline.
    2. Within day 0 → peak, progressively fit ln(VCD) vs time.
       Start with the first 3 points and extend one point at a time.
       Stop extending when R² drops below 0.97 — that marks the
       transition from exponential to deceleration phase.
    3. Use the best (longest) window that still has R² ≥ 0.97.

    Returns dict with: mu_h, mu_day, td_h, r_squared, exp_end_day,
    peak_day, peak_value, n_fit, n_total, n_decline.
    Returns None if not enough data.
    """
    if len(biomass_df) < 3:
        return None
    d = biomass_df.copy()
    d = d[d["value"] > 0].reset_index(drop=True)
    if len(d) < 3:
        return None

    # Step 1 — find peak VCD day
    peak_idx = d["value"].idxmax()
    peak_day = d.loc[peak_idx, "day"]
    peak_value = d.loc[peak_idx, "value"]

    pre_peak = d[d["day"] <= peak_day].reset_index(drop=True)
    n_decline = len(d[d["day"] > peak_day])

    if len(pre_peak) < 2:
        return None

    pre_peak["ln_val"] = np.log(pre_peak["value"])

    # Step 2 — progressive fit: extend window while R² stays high
    best = None
    R2_THRESHOLD = 0.99

    for end_idx in range(2, len(pre_peak) + 1):  # at least 3 points (idx 0..2)
        subset = pre_peak.iloc[:end_idx]
        t_h = subset["day"].values * 24.0
        y = subset["ln_val"].values

        if len(t_h) < 2:
            continue

        coeffs = np.polyfit(t_h, y, 1)
        y_pred = np.polyval(coeffs, t_h)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        if r_sq >= R2_THRESHOLD or best is None:
            best = {
                "coeffs": coeffs, "r_sq": r_sq,
                "n_fit": len(subset),
                "end_day": subset["day"].iloc[-1],
            }
        # Once R² drops below threshold and we have a good fit, stop
        if r_sq < R2_THRESHOLD and best is not None and best["r_sq"] >= R2_THRESHOLD:
            break

    if best is None:
        return None

    mu_h = best["coeffs"][0]
    mu_day = mu_h * 24.0
    td_h = math.log(2) / mu_h if mu_h > 0 else None

    return {
        "mu_h": mu_h, "mu_day": mu_day, "td_h": td_h,
        "r_squared": best["r_sq"],
        "exp_end_day": best["end_day"],
        "peak_day": peak_day, "peak_value": peak_value,
        "n_fit": best["n_fit"],
        "n_total": len(d),
        "n_decline": n_decline,
    }


def _tab_analysis(batch):
    if batch is None:
        st.info("Select a run first.")
        return

    df = _fetch_measurements(batch["id"])
    if df.empty:
        st.info("No measurements for this run yet.")
        return

    st.subheader("Growth Kinetics")

    # Try VCD first, then OD600
    biomass_param = None
    for p in ["VCD", "OD600"]:
        s = _get_param_series(df, p)
        if len(s) >= 2:
            biomass_param = p
            biomass = s
            break

    mu_result = None
    if biomass_param is None:
        st.warning("Need at least 2 VCD or OD600 data points for kinetics.")
    else:
        mu_result = _compute_mu_max(biomass)

        if mu_result is not None:
            mu_h = mu_result["mu_h"]
            td_h = mu_result["td_h"]
            r_sq = mu_result["r_squared"]
            exp_end = mu_result["exp_end_day"]
            n_fit = mu_result["n_fit"]
            n_total = mu_result["n_total"]
            n_decline = mu_result["n_decline"]
            n_excluded = n_total - n_fit

            # Metrics row
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("μ_max (h⁻¹)", f"{mu_h:.4f}")
            c2.metric("Doubling Time", f"{td_h:.1f} h" if td_h else "—")
            c3.metric("R²", f"{r_sq:.4f}")
            c4.metric(f"Peak {biomass_param}", f"{mu_result['peak_value']:.1f}")

            st.caption(
                f"Exponential phase: **Day 0 → Day {exp_end:.0f}** — "
                f"{n_fit} points fitted, {n_excluded} excluded "
                f"({n_total - n_fit - n_decline} deceleration + {n_decline} decline)"
            )
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("μ_max (h⁻¹)", "—")
            c2.metric("Doubling Time", "—")
            c3.metric("R²", "—")
            c4.metric(f"Max {biomass_param}", f"{biomass['value'].max():.2f}")

        # Biomass chart
        st.line_chart(biomass.rename(columns={"day": "Day", "value": biomass_param}).set_index("Day"))

    # ── Substrate consumption ──
    glucose = _get_param_series(df, "glucose")
    if len(glucose) >= 2:
        st.subheader("Substrate Consumption")
        c1, c2, c3 = st.columns(3)
        c1.metric("Initial Glucose (g/L)", f"{glucose['value'].iloc[0]:.2f}")
        c2.metric("Final Glucose (g/L)", f"{glucose['value'].iloc[-1]:.2f}")
        delta_s = glucose['value'].iloc[0] - glucose['value'].iloc[-1]
        c3.metric("ΔS Consumed (g/L)", f"{delta_s:.2f}")

        # Yx/s — convert VCD (e6 cells/mL) to g/L using CHO dry weight 375 pg/cell
        # 375 pg/cell = 3.75e-10 g/cell; VCD is in 1e6 cells/mL = 1e9 cells/L
        # biomass_gL = VCD * 1e6 * 3.75e-10 * 1000 = VCD * 0.375
        CHO_DW_FACTOR = 0.375  # g/L per 1e6 cells/mL
        if biomass_param and mu_result is not None and delta_s > 0:
            peak_gL = mu_result["peak_value"] * CHO_DW_FACTOR
            init_gL = biomass['value'].iloc[0] * CHO_DW_FACTOR
            delta_x_gL = peak_gL - init_gL
            yxs = delta_x_gL / delta_s if delta_s != 0 else None
            if yxs is not None:
                st.metric("Yx/s (g biomass / g glucose)", f"{yxs:.3f}")
                st.caption(
                    f"VCD→biomass conversion: {CHO_DW_FACTOR} g/L per 1×10⁶ cells/mL "
                    f"(375 pg/cell dry weight)"
                )

        st.line_chart(glucose.rename(columns={"day": "Day", "value": "Glucose (g/L)"}).set_index("Day"))

    # ── Product / Titer ──
    titer = _get_param_series(df, "titer")
    if len(titer) >= 2:
        st.subheader("Product & Productivity")
        c1, c2, c3 = st.columns(3)
        max_titer = titer["value"].max()
        c1.metric("Max Titer (g/L)", f"{max_titer:.3f}")

        # STY = titer / time
        duration_h = (titer["day"].iloc[-1] - titer["day"].iloc[0]) * 24
        sty = max_titer / duration_h if duration_h > 0 else None
        c2.metric("STY (g/L/h)", f"{sty:.4f}" if sty else "—")

        # Yp/s = final titer / total glucose consumed
        if len(glucose) >= 2:
            delta_s = glucose['value'].iloc[0] - glucose['value'].iloc[-1]
            final_titer = titer["value"].iloc[-1]
            yps = final_titer / delta_s if delta_s > 0 else None
            c3.metric("Yp/s (g product / g glucose)", f"{yps:.4f}" if yps else "—")

        st.line_chart(titer.rename(columns={"day": "Day", "value": "Titer (g/L)"}).set_index("Day"))

    # ── OUR / CER / RQ from off-gas ──
    # Try offgas_O2/offgas_CO2 first, fall back to O2/CO2
    o2_series = _get_param_series(df, "offgas_O2")
    o2_source = "offgas_O2"
    if len(o2_series) < 2:
        o2_series = _get_param_series(df, "O2")
        o2_source = "O2"
    co2_series = _get_param_series(df, "offgas_CO2")
    co2_source = "offgas_CO2"
    if len(co2_series) < 2:
        co2_series = _get_param_series(df, "CO2")
        co2_source = "CO2"

    # Debug: show what parameters exist for this batch
    all_params = sorted(df["parameter_name"].dropna().unique().tolist())
    st.subheader("Off-Gas Analysis")
    st.caption(f"Parameters in database: {', '.join(all_params)}")
    st.caption(f"O₂ source: **{o2_source}** ({len(o2_series)} pts) | CO₂ source: **{co2_source}** ({len(co2_series)} pts)")

    if len(o2_series) >= 2 and len(co2_series) >= 2:
        # Merge on nearest day
        merged = pd.merge_asof(
            o2_series.rename(columns={"value": "O2_val"}),
            co2_series.rename(columns={"value": "CO2_val"}),
            on="day", direction="nearest",
        )

        # Compute rates as change per hour (derivative of time-series)
        dt_h = np.gradient(merged["day"].values) * 24.0
        dt_h[dt_h == 0] = np.nan

        # CER = rate of CO2 evolution (CO2 increasing → positive CER)
        cer = np.gradient(merged["CO2_val"].values) / dt_h

        # OUR = rate of O2 consumption
        # If O2 data increases over time (e.g. off-gas O2 enrichment or
        # dissolved O2 demand proxy), use the absolute rate of change.
        # For standard off-gas: OUR = -(dO2/dt). For dissolved/demand
        # signals where O2 rises with metabolic load: OUR = dO2/dt.
        raw_dO2 = np.gradient(merged["O2_val"].values) / dt_h
        net_o2_trend = merged["O2_val"].iloc[-1] - merged["O2_val"].iloc[0]
        if net_o2_trend > 0:
            # O2 signal rises over time — treat as demand / enrichment proxy
            our = raw_dO2
        else:
            # Standard off-gas: O2 decreases as culture consumes it
            our = -raw_dO2

        merged["OUR"] = our
        merged["CER"] = cer
        merged["RQ"] = merged["CER"] / merged["OUR"].replace(0, np.nan)
        merged["RQ"] = merged["RQ"].replace([np.inf, -np.inf], np.nan)

        c1, c2, c3 = st.columns(3)
        c1.metric("Avg OUR (mmol/L/h)", f"{merged['OUR'].dropna().mean():.3f}")
        c2.metric("Avg CER (mmol/L/h)", f"{merged['CER'].dropna().mean():.3f}")
        rq_mean = merged["RQ"].dropna().mean()
        c3.metric("Avg RQ", f"{rq_mean:.2f}" if pd.notna(rq_mean) and np.isfinite(rq_mean) else "—")
        st.line_chart(merged[["day", "OUR", "CER", "RQ"]].set_index("day"))
    else:
        st.info("Need at least 2 data points for both O₂ and CO₂ to calculate OUR/CER/RQ.")

    # ── Derived / Soft Sensors ──
    st.subheader("Derived Variables — Soft Sensors")
    if biomass_param and len(biomass) >= 2 and mu_result is not None:
        bio = biomass.copy()
        bio["X"] = bio["value"]

        derivations = {}

        # qGlc — specific glucose consumption rate
        if len(glucose) >= 2:
            glu_interp = np.interp(bio["day"], glucose["day"], glucose["value"])
            dS = -np.gradient(glu_interp, bio["day"] * 24)  # g/L/h
            bio["qGlc"] = dS / bio["X"].replace(0, np.nan)
            derivations["qGlc (g/g/h)"] = f"{bio['qGlc'].dropna().mean():.4f}"

        # qLac — specific lactate production rate
        lactate = _get_param_series(df, "lactate")
        if len(lactate) >= 2:
            lac_interp = np.interp(bio["day"], lactate["day"], lactate["value"])
            dL = np.gradient(lac_interp, bio["day"] * 24)
            bio["qLac"] = dL / bio["X"].replace(0, np.nan)
            derivations["qLac (g/g/h)"] = f"{bio['qLac'].dropna().mean():.4f}"

        # qP — specific productivity
        if len(titer) >= 2:
            tit_interp = np.interp(bio["day"], titer["day"], titer["value"])
            dP = np.gradient(tit_interp, bio["day"] * 24)
            bio["qP"] = dP / bio["X"].replace(0, np.nan)
            derivations["qP (g/g/h)"] = f"{bio['qP'].dropna().mean():.4f}"

        if derivations:
            cols = st.columns(len(derivations))
            for i, (name, val) in enumerate(derivations.items()):
                cols[i].metric(name, val)
        else:
            st.caption("Need glucose, lactate, or titer data alongside biomass for soft sensors.")

    # ── Luedeking-Piret ──
    if biomass_param and len(biomass) >= 3 and len(titer) >= 3:
        st.subheader("Luedeking-Piret Productivity Model")
        bio = biomass.copy()
        tit = titer.copy()
        # Interpolate titer onto biomass time axis
        tit_interp = np.interp(bio["day"], tit["day"], tit["value"])
        dP = np.gradient(tit_interp, bio["day"] * 24)  # g/L/h
        dX = np.gradient(bio["value"], bio["day"] * 24)
        mu_local = dX / bio["value"].replace(0, np.nan)

        # qp = alpha * mu + beta
        valid = np.isfinite(mu_local) & np.isfinite(dP / bio["value"].replace(0, np.nan))
        if valid.sum() >= 2:
            qp = (dP / bio["value"].replace(0, np.nan)).values[valid]
            mu_loc = mu_local.values[valid]
            try:
                coeffs = np.polyfit(mu_loc, qp, 1)
                alpha, beta = coeffs[0], coeffs[1]
                c1, c2 = st.columns(2)
                c1.metric("α (growth-associated)", f"{alpha:.4f}")
                c2.metric("β (non-growth-associated)", f"{beta:.4f}")
            except Exception:
                st.caption("Could not fit LP model.")


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════
def _tab_comparison(batch, all_batches):
    if batch is None:
        st.info("Select a run first.")
        return

    df_current = _fetch_measurements(batch["id"])

    # ── Pairwise comparison ──
    st.subheader("Compare Current Run to a Previous Run")
    other_batches = [b for b in all_batches if b["id"] != batch["id"]]
    if not other_batches:
        st.info("No other runs to compare against.")
    else:
        labels = [b["batch_code"] for b in other_batches]
        sel = st.selectbox("Compare against", labels, key="rm_comp_sel")
        comp_batch = next(b for b in other_batches if b["batch_code"] == sel)
        df_comp = _fetch_measurements(comp_batch["id"])

        if df_current.empty or df_comp.empty:
            st.warning("Need measurements in both runs to compare.")
        else:
            # Divergence table
            st.markdown("**Divergence Table**")
            params_curr = set(df_current["parameter_name"].dropna().unique())
            params_comp = set(df_comp["parameter_name"].dropna().unique())
            common = sorted(params_curr & params_comp)

            if common:
                rows = []
                for p in common:
                    curr_mean = df_current[df_current["parameter_name"] == p]["value"].mean()
                    comp_mean = df_comp[df_comp["parameter_name"] == p]["value"].mean()
                    delta = curr_mean - comp_mean
                    pct = (delta / comp_mean * 100) if comp_mean != 0 else 0
                    rows.append({
                        "Parameter": p,
                        f"Current ({batch['batch_code']})": f"{curr_mean:.3f}",
                        f"Reference ({sel})": f"{comp_mean:.3f}",
                        "Δ": f"{delta:+.3f}",
                        "Δ%": f"{pct:+.1f}%",
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.caption("No common parameters between runs.")

    # ── Golden Batch Radar ──
    st.divider()
    st.subheader("Golden Batch Radar")
    golden_ref = None
    try:
        notes = json.loads(batch.get("notes", "{}"))
        golden_ref = notes.get("golden_batch_ref")
    except Exception:
        pass

    if golden_ref:
        golden_batch = next((b for b in all_batches if b["batch_code"] == golden_ref), None)
    else:
        golden_batch = None

    if golden_batch is None:
        golden_opts = [b["batch_code"] for b in all_batches if b["id"] != batch["id"]]
        if golden_opts:
            golden_sel = st.selectbox("Select golden batch for radar", golden_opts, key="rm_golden_sel")
            golden_batch = next(b for b in all_batches if b["batch_code"] == golden_sel)

    if golden_batch:
        df_golden = _fetch_measurements(golden_batch["id"])
        if not df_current.empty and not df_golden.empty:
            common = sorted(
                set(df_current["parameter_name"].dropna().unique())
                & set(df_golden["parameter_name"].dropna().unique())
            )
            if common:
                curr_vals = [df_current[df_current["parameter_name"] == p]["value"].mean() for p in common]
                gold_vals = [df_golden[df_golden["parameter_name"] == p]["value"].mean() for p in common]
                # Normalize to golden
                ratios_curr = [c / g if g != 0 else 0 for c, g in zip(curr_vals, gold_vals)]
                ratios_gold = [1.0] * len(common)
                radar_df = pd.DataFrame({
                    "Parameter": common + common,
                    "Ratio": ratios_curr + ratios_gold,
                    "Run": [batch["batch_code"]] * len(common) + [golden_batch["batch_code"]] * len(common),
                })
                st.bar_chart(
                    radar_df.pivot(index="Parameter", columns="Run", values="Ratio"),
                )
                st.caption("Values normalized to golden batch (1.0 = match)")

    # ── Multi-run overlay ──
    st.divider()
    st.subheader("Multi-Run Parameter Overlay")
    if len(all_batches) < 2:
        st.info("Need at least 2 runs for overlay.")
        return

    overlay_batches = st.multiselect(
        "Select up to 5 runs",
        [b["batch_code"] for b in all_batches],
        default=[batch["batch_code"]],
        max_selections=5,
        key="rm_overlay_runs",
    )
    # Get all params across selected runs
    all_params = set()
    run_dfs = {}
    for bc in overlay_batches:
        b = next(x for x in all_batches if x["batch_code"] == bc)
        d = _fetch_measurements(b["id"])
        run_dfs[bc] = d
        if not d.empty:
            all_params.update(d["parameter_name"].dropna().unique())

    if all_params:
        overlay_param = st.selectbox("Parameter to overlay", sorted(all_params), key="rm_overlay_param")
        chart_data = pd.DataFrame()
        for bc, d in run_dfs.items():
            sub = d[d["parameter_name"] == overlay_param][["day_of_run", "value"]].dropna()
            sub = sub.sort_values("day_of_run").rename(columns={"value": bc, "day_of_run": "Day"})
            if chart_data.empty:
                chart_data = sub.set_index("Day")
            else:
                chart_data = chart_data.join(sub.set_index("Day"), how="outer")

        if not chart_data.empty:
            st.line_chart(chart_data)
        else:
            st.caption("No data for this parameter in selected runs.")


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — SCALE-UP
# ═══════════════════════════════════════════════════════════════════════════════
def _tab_scaleup(batch):
    if batch is None:
        st.info("Select a run first.")
        return

    df = _fetch_measurements(batch["id"])

    st.subheader("Scale-Up Predictions")

    # Pre-populate from live data
    agitation = _get_param_series(df, "agitation") if not df.empty else pd.DataFrame()
    do_data = _get_param_series(df, "DO") if not df.empty else pd.DataFrame()
    scale_liters = batch.get("scale_liters", 2.0) or 2.0

    current_rpm = agitation["value"].mean() if len(agitation) > 0 else 150.0
    current_do = do_data["value"].mean() if len(do_data) > 0 else 40.0

    st.markdown(f"**Current run:** {batch['batch_code']} at {scale_liters:.1f} L")

    c1, c2, c3 = st.columns(3)
    with c1:
        lab_vol = st.number_input("Lab Volume (L)", value=float(scale_liters), min_value=0.01, format="%.2f")
        impeller_d = st.number_input("Impeller Dia (m)", value=0.05, min_value=0.001, format="%.3f")
    with c2:
        rpm = st.number_input("Agitation (RPM)", value=float(current_rpm), min_value=1.0)
        kla = st.number_input("kLa (h⁻¹)", value=150.0, min_value=1.0)
    with c3:
        criterion = st.selectbox("Scaling Criterion", SCALING_CRITERIA)

    # Derived lab-scale parameters
    tip_speed = math.pi * impeller_d * rpm / 60  # m/s
    vessel_d = (4 * lab_vol * 1e-3 / (math.pi * 2.5)) ** (1/3)  # approx vessel dia (m), H/D~2.5
    pv_lab = (rpm ** 3) * (impeller_d ** 5) * 1000 / (lab_vol * 1e-3)  # simplified P/V proxy
    re_lab = rpm * impeller_d ** 2 * 1000 / 60 / 1e-3  # simplified Re

    st.divider()
    st.markdown("**Lab-Scale Derived Parameters**")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Tip Speed (m/s)", f"{tip_speed:.2f}")
    mc2.metric("P/V (proxy)", f"{pv_lab:.0f}")
    mc3.metric("Re (proxy)", f"{re_lab:.0f}")
    mc4.metric("DO avg (%)", f"{current_do:.1f}")

    # ── Scale Translation Table ──
    st.divider()
    st.subheader("Scale Translation Table")
    scale_factors = [1, 10, 100, 1000]
    target_vols = [lab_vol * f for f in scale_factors]

    rows = []
    for f, vol in zip(scale_factors, target_vols):
        d_vessel = vessel_d * (f ** (1/3))
        d_imp = impeller_d * (f ** (1/3))

        if criterion == "Constant P/V":
            n = rpm / (f ** (2/9))
            ts = math.pi * d_imp * n / 60
            pv = pv_lab
        elif criterion == "Constant Tip Speed":
            n = rpm * impeller_d / d_imp
            ts = tip_speed
            pv = pv_lab * (n / rpm) ** 3 * (d_imp / impeller_d) ** 5 / f
        elif criterion == "Constant kLa":
            n = rpm * (f ** 0.1)  # empirical approximation
            ts = math.pi * d_imp * n / 60
            pv = pv_lab * (n / rpm) ** 3 * (d_imp / impeller_d) ** 5 / f
        elif criterion == "Constant Re":
            n = rpm * (impeller_d / d_imp) ** 2
            ts = math.pi * d_imp * n / 60
            pv = pv_lab * (n / rpm) ** 3 * (d_imp / impeller_d) ** 5 / f
        else:  # Constant Mixing Time
            n = rpm * (f ** (1/3))
            ts = math.pi * d_imp * n / 60
            pv = pv_lab * (n / rpm) ** 3 * (d_imp / impeller_d) ** 5 / f

        rows.append({
            "Scale": f"{f}x",
            "Volume (L)": f"{vol:.0f}",
            "Vessel Dia (m)": f"{d_vessel:.3f}",
            "Impeller Dia (m)": f"{d_imp:.3f}",
            "RPM": f"{n:.0f}",
            "Tip Speed (m/s)": f"{ts:.2f}",
            "P/V (proxy)": f"{pv:.0f}",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Show all 5 criteria side-by-side for target
    st.divider()
    st.subheader("Criteria Comparison at 1000x")
    comp_rows = []
    f = 1000
    vol = lab_vol * f
    d_v = vessel_d * (f ** (1/3))
    d_i = impeller_d * (f ** (1/3))
    for crit in SCALING_CRITERIA:
        if crit == "Constant P/V":
            n = rpm / (f ** (2/9))
        elif crit == "Constant Tip Speed":
            n = rpm * impeller_d / d_i
        elif crit == "Constant kLa":
            n = rpm * (f ** 0.1)
        elif crit == "Constant Re":
            n = rpm * (impeller_d / d_i) ** 2
        else:
            n = rpm * (f ** (1/3))
        ts = math.pi * d_i * n / 60
        comp_rows.append({"Criterion": crit, "RPM": f"{n:.0f}", "Tip Speed (m/s)": f"{ts:.2f}"})
    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 6 — DIGITAL TWIN
# ═══════════════════════════════════════════════════════════════════════════════
def _monod_odes(t, y, mu_max, Ks, Yxs, alpha, beta, feed_rate, Sf):
    """Monod kinetics + Luedeking-Piret ODE system."""
    X, S, P = y
    if S < 0:
        S = 0
    mu = mu_max * S / (Ks + S)
    dXdt = mu * X
    dSdt = -mu * X / Yxs + feed_rate * Sf  # simplified
    dPdt = alpha * mu * X + beta * X
    return [dXdt, dSdt, dPdt]


def _tab_digital_twin(batch):
    if batch is None:
        st.info("Select a run first.")
        return

    df = _fetch_measurements(batch["id"])
    if df.empty:
        st.info("No data for this run yet.")
        return

    st.subheader("ODE Parameter Fitting")

    # Get experimental data
    biomass = None
    bio_label = None
    for p in ["VCD", "OD600"]:
        s = _get_param_series(df, p)
        if len(s) >= 3:
            biomass = s
            bio_label = p
            break

    substrate = _get_param_series(df, "glucose")
    product = _get_param_series(df, "titer")

    if biomass is None or len(biomass) < 3:
        st.warning("Need at least 3 biomass (VCD/OD600) data points for fitting.")
        return

    if len(substrate) < 2:
        st.warning("Need at least 2 glucose data points for fitting.")
        return

    # Display what we have
    c1, c2, c3 = st.columns(3)
    c1.metric(f"{bio_label} points", len(biomass))
    c2.metric("Glucose points", len(substrate))
    c3.metric("Titer points", len(product) if len(product) >= 2 else 0)

    # Fit button
    if st.button("Fit ODE Parameters", type="primary"):
        from scipy.integrate import solve_ivp
        from scipy.optimize import minimize

        # Align data: interpolate all to biomass timepoints (in hours)
        t_h = biomass["day"].values * 24
        X_exp = biomass["value"].values
        S_exp = np.interp(biomass["day"].values, substrate["day"].values, substrate["value"].values)
        P_exp = np.interp(biomass["day"].values, product["day"].values, product["value"].values) if len(product) >= 2 else np.zeros_like(t_h)

        X0, S0, P0 = X_exp[0], S_exp[0], P_exp[0]

        def objective(params):
            mu_m, Ks, Yxs, alpha, beta = params
            if mu_m <= 0 or Ks <= 0 or Yxs <= 0:
                return 1e12
            try:
                sol = solve_ivp(
                    _monod_odes, [t_h[0], t_h[-1]], [X0, S0, P0],
                    args=(mu_m, Ks, Yxs, alpha, beta, 0, 0),
                    t_eval=t_h, method="RK45",
                )
                if not sol.success:
                    return 1e12
                X_pred, S_pred, P_pred = sol.y
                loss = (np.sum((X_pred - X_exp) ** 2) / np.mean(X_exp ** 2)
                        + np.sum((S_pred - S_exp) ** 2) / max(np.mean(S_exp ** 2), 1e-6))
                if len(product) >= 2:
                    loss += np.sum((P_pred - P_exp) ** 2) / max(np.mean(P_exp ** 2), 1e-6)
                return loss
            except Exception:
                return 1e12

        # Initial guesses
        mu_guess = 0.03  # h^-1
        result = minimize(
            objective, [mu_guess, 0.5, 0.5, 0.01, 0.001],
            method="Nelder-Mead",
            options={"maxiter": 5000, "xatol": 1e-8},
        )

        if result.success or result.fun < 1e6:
            mu_m, Ks, Yxs, alpha, beta = result.x
            st.success(f"Converged — loss: {result.fun:.4f}")

            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
            mc1.metric("μ_max (h⁻¹)", f"{mu_m:.4f}")
            mc2.metric("Ks (g/L)", f"{Ks:.3f}")
            mc3.metric("Yx/s", f"{Yxs:.3f}")
            mc4.metric("LP α", f"{alpha:.4f}")
            mc5.metric("LP β", f"{beta:.5f}")

            # Solve with fitted params for plotting
            sol = solve_ivp(
                _monod_odes, [t_h[0], t_h[-1]], [X0, S0, P0],
                args=(mu_m, Ks, Yxs, alpha, beta, 0, 0),
                t_eval=np.linspace(t_h[0], t_h[-1], 200), method="RK45",
            )
            if sol.success:
                st.subheader("Fit vs Experimental")
                t_days = sol.t / 24
                chart_df = pd.DataFrame({
                    "Day": t_days,
                    f"{bio_label} (twin)": sol.y[0],
                    "Glucose (twin)": sol.y[1],
                    "Titer (twin)": sol.y[2],
                })
                st.line_chart(chart_df.set_index("Day"))

                # Overlay experimental points as metrics
                st.caption(f"Experimental: {bio_label} ({len(X_exp)} pts), Glucose ({len(S_exp)} pts), Titer ({len(P_exp)} pts)")

            # Store for prediction
            st.session_state["_twin_params"] = (mu_m, Ks, Yxs, alpha, beta, X_exp[-1], S_exp[-1], P_exp[-1], t_h[-1])
        else:
            st.error("Fitting did not converge. Try adding more data points.")

    # ── Prediction section ──
    if "_twin_params" in st.session_state:
        st.divider()
        st.subheader("Predict Extended Run")
        mu_m, Ks, Yxs, alpha, beta, X_last, S_last, P_last, t_last = st.session_state["_twin_params"]

        pred_hours = st.number_input("Prediction horizon (hours)", value=48.0, min_value=1.0, step=6.0)

        if st.button("Run Prediction"):
            from scipy.integrate import solve_ivp
            t_span = [t_last, t_last + pred_hours]
            sol = solve_ivp(
                _monod_odes, t_span, [X_last, S_last, P_last],
                args=(mu_m, Ks, Yxs, alpha, beta, 0, 0),
                t_eval=np.linspace(t_span[0], t_span[1], 200), method="RK45",
            )
            if sol.success:
                t_days = sol.t / 24
                pred_df = pd.DataFrame({
                    "Day": t_days,
                    f"{bio_label} (pred)": sol.y[0],
                    "Glucose (pred)": sol.y[1],
                    "Titer (pred)": sol.y[2],
                })
                st.line_chart(pred_df.set_index("Day"))
                c1, c2, c3 = st.columns(3)
                c1.metric("Predicted Titer (g/L)", f"{sol.y[2][-1]:.3f}")
                c2.metric("Predicted Biomass", f"{sol.y[0][-1]:.2f}")
                c3.metric("Predicted Glucose (g/L)", f"{max(sol.y[1][-1], 0):.2f}")


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 7 — ARCHIVE
# ═══════════════════════════════════════════════════════════════════════════════
def _tab_archive(batch, all_batches):
    if batch is None:
        st.info("Select a run first.")
        return

    sb = _sb()
    batch_id = batch["id"]

    # ── Run Summary ──
    st.subheader(f"Run: {batch['batch_code']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Organism", batch.get("organism", "—"))
    c2.metric("Product", batch.get("product_type", "—"))
    c3.metric("Scale (L)", batch.get("scale_liters", "—"))
    c4.metric("Start Date", batch.get("start_date", "—"))

    # Notes / extra fields
    extra = {}
    try:
        extra = json.loads(batch.get("notes", "{}"))
    except Exception:
        extra = {"notes": batch.get("notes", "")}
    if extra:
        with st.expander("Run metadata"):
            for k, v in extra.items():
                st.markdown(f"**{k}:** {v}")

    # ── Full measurements table ──
    st.divider()
    st.subheader("All Measurements")
    df = _fetch_measurements(batch_id)
    if df.empty:
        st.info("No measurements recorded.")
    else:
        display_cols = ["parameter_name", "value", "unit", "day_of_run", "instrument"]
        if "instrument_source" in df.columns:
            display_cols.append("instrument_source")
        show_df = df[display_cols].copy() if all(c in df.columns for c in display_cols) else df
        st.dataframe(show_df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} measurement(s)")

        # Summary statistics
        st.subheader("Summary Statistics")
        stats = df.groupby("parameter_name")["value"].agg(["count", "mean", "std", "min", "max"])
        stats = stats.round(3).reset_index()
        stats.columns = ["Parameter", "Count", "Mean", "Std", "Min", "Max"]
        st.dataframe(stats, use_container_width=True, hide_index=True)

    # ── Export ──
    st.divider()
    st.subheader("Export")
    c1, c2 = st.columns(2)
    if not df.empty:
        with c1:
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, f"{batch['batch_code']}_measurements.csv", "text/csv")
        with c2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Measurements")
                stats.to_excel(writer, index=False, sheet_name="Summary")
            st.download_button("Download Excel", buf.getvalue(),
                               f"{batch['batch_code']}_measurements.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ── Notes editor ──
    st.divider()
    st.subheader("Run Notes")
    current_notes = batch.get("notes", "")
    new_notes = st.text_area("Edit notes", value=current_notes, height=100, key="rm_notes_editor")
    if st.button("Save Notes"):
        if sb:
            try:
                sb.table("batches").update({"notes": new_notes}).eq("id", batch_id).execute()
                st.success("Notes saved.")
                _invalidate()
            except Exception as exc:
                st.error(f"Failed to save: {exc}")

    # ── Outcome classification ──
    st.divider()
    st.subheader("Outcome Classification")
    outcomes = ["—", "Success", "Partial Success", "Failure", "Incomplete", "Aborted"]
    current_outcome = batch.get("outcome", "—") or "—"
    idx = outcomes.index(current_outcome) if current_outcome in outcomes else 0
    new_outcome = st.selectbox("Outcome", outcomes, index=idx, key="rm_outcome")
    if st.button("Save Outcome"):
        if sb:
            # Store in notes JSON since outcome column may not exist yet
            try:
                notes_data = json.loads(batch.get("notes", "{}"))
            except Exception:
                notes_data = {}
            notes_data["outcome"] = new_outcome
            try:
                sb.table("batches").update({"notes": json.dumps(notes_data)}).eq("id", batch_id).execute()
                st.success(f"Outcome set to **{new_outcome}**.")
                _invalidate()
            except Exception as exc:
                st.error(f"Failed: {exc}")

    # ── Timeline of all runs ──
    st.divider()
    st.subheader("Project Run Timeline")
    if all_batches:
        timeline_rows = []
        for b in reversed(all_batches):
            outcome = "—"
            try:
                n = json.loads(b.get("notes", "{}"))
                outcome = n.get("outcome", "—")
            except Exception:
                pass
            timeline_rows.append({
                "Date": b.get("start_date", b.get("created_at", "")[:10] if b.get("created_at") else ""),
                "Batch": b["batch_code"],
                "Organism": b.get("organism", ""),
                "Product": b.get("product_type", ""),
                "Outcome": outcome,
            })
        st.dataframe(pd.DataFrame(timeline_rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN RENDER
# ═══════════════════════════════════════════════════════════════════════════════
def render():
    st.title("Run Manager")
    st.caption("Unified bioprocess run lifecycle — setup, acquisition, analysis, comparison, scale-up, digital twin, archive")

    sb = _sb()
    if sb is None:
        st.error("Supabase not connected. Set `SUPABASE_URL` and `SUPABASE_KEY` in `.env`.")
        return

    # ── Fetch all batches ──
    all_batches = _fetch_all_batches(id(sb))

    # ── Active batch selector (sidebar) ──
    with st.sidebar:
        st.markdown("---")
        st.subheader("Active Run")
        if not all_batches:
            st.caption("No runs yet. Use Setup tab to create one.")
            active_batch = None
        else:
            labels = [b["batch_code"] for b in all_batches]
            # Default to session state if set
            default_idx = 0
            saved_id = st.session_state.get("rm_active_batch_id")
            if saved_id:
                for i, b in enumerate(all_batches):
                    if b["id"] == saved_id:
                        default_idx = i
                        break
            sel_idx = st.selectbox(
                "Select run", range(len(labels)),
                format_func=lambda i: labels[i],
                index=default_idx, key="rm_batch_sel",
            )
            active_batch = all_batches[sel_idx]
            st.session_state["rm_active_batch_id"] = active_batch["id"]
            st.caption(f"{active_batch['organism']} | {active_batch.get('product_type', '')} | {active_batch.get('scale_liters', '')} L")

    # ── Horizontal tab bar ──
    tabs = st.tabs(["Setup", "Live Acquisition", "Analysis", "Comparison", "Scale-Up", "Digital Twin", "Archive"])

    with tabs[0]:
        _tab_setup(all_batches)
    with tabs[1]:
        _tab_live_acquisition(active_batch, all_batches)
    with tabs[2]:
        _tab_analysis(active_batch)
    with tabs[3]:
        _tab_comparison(active_batch, all_batches)
    with tabs[4]:
        _tab_scaleup(active_batch)
    with tabs[5]:
        _tab_digital_twin(active_batch)
    with tabs[6]:
        _tab_archive(active_batch, all_batches)
