"""
gem_app.py -- Interactive GEM Map Explorer (Streamlit)
Written by: Anu Kozhiyalam
Purpose: Visual interface for organism-aware metabolic pathway mapping
         powered by gem_map.py -- no database, pure GEM logic
         Dual-column comparison: Current Run vs Reference Run
"""

import streamlit as st
import csv
import os
from datetime import datetime
from gem_map import (
    get_all_pathway_states, list_organisms, list_strains,
    get_strain_info, STRAIN_REGISTRY,
)
from test_literature import LITERATURE_DATASETS

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GEM Map Explorer",
    page_icon="<",
    layout="wide",
)

# ── Severity helpers ─────────────────────────────────────────────────────
CRITICAL_STATES = {
    "critical", "toxic", "inhibitory", "lysis", "autolysis",
}
WARNING_STATES = {
    "acidosis", "acidic", "very_acidic", "above_optimum", "hypoxic", "microaerobic", "anaerobic",
    "heat_shock", "heat_stress", "overflow_risk", "overflow",
    "crabtree_overflow", "flux_limited", "carbon_starved", "carbon_limited",
    "depleted", "nitrogen_limited", "oxygen_depleted", "high_OUR",
    "hypercapnia", "high_respiration", "high_fermentation",
    "shear_risk", "foam_risk", "poor_mixing",
    "low_production", "low_expression", "slow_growth", "lag_or_slow",
    "low_density", "below_setpoint", "sub_induction", "overgrown",
    "alkalosis", "alkaline", "neutral_high", "high_for_yeast",
    "moderate", "moderate_stress", "cold_shift", "reduced_temp",
    "excess", "low_demand", "low_metabolism", "low_respiration",
    "high_shear", "extreme",
}


def severity(state_name):
    if state_name in CRITICAL_STATES:
        return "CRITICAL"
    if state_name in WARNING_STATES:
        return "WARNING"
    return "OK"


def severity_color(sev):
    return {"CRITICAL": "#FF4444", "WARNING": "#FFA500", "OK": "#22C55E"}[sev]


def severity_emoji(sev):
    return {"CRITICAL": "\U0001f534", "WARNING": "\U0001f7e1", "OK": "\U0001f7e2"}[sev]


def health_score(states):
    """Weighted health score with high-impact parameter multipliers.

    Key metabolic parameters (glucose, DO, ammonia, VCD/OD600) count 2x
    because they are primary carbon/oxygen/nitrogen sources and affect
    all downstream metabolism. A WARNING on glucose has more impact
    than a WARNING on agitation.

    Scoring: OK=100, WARNING=40, CRITICAL=0 per unit weight, averaged.
    Multiplicative penalty: 0.75^n_crit compounds for multiple criticals.
    """
    if not states:
        return 100

    # Two-layer scoring:
    # Layer 1: Base average (OK=100, WARNING=40, CRITICAL=0).
    # Layer 2: Direct deductions for high-impact params in SEVERE warning
    #   states (flux_limited, hypoxic, nitrogen_limited, slow_growth, etc.)
    #   but NOT for mild warnings (moderate, excess, cold_shift).
    #   High-impact CRITICAL always gets a deduction.
    # Layer 3: Multiplicative penalty (0.75^n_crit).
    HIGH_IMPACT = {"glucose", "DO", "ammonia", "OD600", "VCD"}
    SEVERE_WARNINGS = {
        "flux_limited", "carbon_starved", "carbon_limited", "depleted",
        "hypoxic", "microaerobic", "anaerobic",
        "nitrogen_limited", "toxic",
        "slow_growth", "lag_or_slow", "low_density", "below_setpoint",
        "acidosis", "acidic", "very_acidic",
        "heat_shock", "heat_stress",
        "oxygen_depleted", "high_OUR",
        "poor_mixing", "shear_risk",
    }

    total = len(states)
    n_crit = 0
    base_sum = 0
    deductions = 0

    for param, info in states.items():
        sev = severity(info["state"])
        is_high = param in HIGH_IMPACT
        state_name = info["state"]

        if sev == "CRITICAL":
            base_sum += 0
            n_crit += 1
            if is_high:
                deductions += 20
        elif sev == "WARNING":
            base_sum += 40
            if is_high and state_name in SEVERE_WARNINGS:
                deductions += 15
                # Carbon/oxygen depletion is existential — extra penalty
                if param == "glucose" and state_name in ("flux_limited", "carbon_starved", "depleted"):
                    deductions += 15
                elif param == "DO" and state_name in ("hypoxic", "microaerobic", "anaerobic"):
                    deductions += 10
        else:
            base_sum += 100

    base = base_sum / total if total > 0 else 100
    score = base - deductions
    penalty = 0.75 ** n_crit if n_crit > 0 else 1.0
    return max(0, int(score * penalty))


# ── Default healthy values per organism ──────────────────────────────────
HEALTHY_DEFAULTS = {
    "CHO": {
        "glucose": 4.0, "lactate": 1.0, "pH": 7.1, "DO": 40.0,
        "ammonia": 3.0, "VCD": 12.0, "viability": 92.0, "titer": 1.5,
        "CO2": 8.0, "O2": 18.0, "temperature": 37.0, "agitation": 180.0,
    },
    "CHO-S": {
        "glucose": 3.0, "lactate": 0.8, "pH": 7.05, "DO": 40.0,
        "ammonia": 2.5, "VCD": 50.0, "viability": 92.0, "titer": 0.8,
        "CO2": 10.0, "O2": 16.0, "temperature": 36.5, "agitation": 150.0,
    },
    "HEK293": {
        "glucose": 3.5, "lactate": 1.5, "pH": 7.15, "DO": 35.0,
        "ammonia": 3.0, "VCD": 2.5, "viability": 93.0, "titer": 5e10,
        "CO2": 8.0, "O2": 18.0, "temperature": 37.0, "agitation": 110.0,
    },
    "NS0": {
        "glucose": 4.0, "lactate": 1.5, "pH": 7.0, "DO": 35.0,
        "ammonia": 3.0, "VCD": 6.0, "viability": 90.0, "titer": 1.0,
        "CO2": 8.0, "O2": 18.0, "temperature": 37.0, "agitation": 150.0,
    },
    "Sp2/0": {
        "glucose": 4.0, "lactate": 1.5, "pH": 7.1, "DO": 35.0,
        "ammonia": 2.5, "VCD": 5.0, "viability": 90.0, "titer": 0.5,
        "CO2": 8.0, "O2": 18.0, "temperature": 37.0, "agitation": 120.0,
    },
    "BHK-21": {
        "glucose": 4.0, "lactate": 1.5, "pH": 7.1, "DO": 35.0,
        "ammonia": 3.0, "VCD": 8.0, "viability": 92.0, "titer": 1.0,
        "CO2": 8.0, "O2": 18.0, "temperature": 37.0, "agitation": 120.0,
    },
    "E. coli": {
        "glucose": 4.0, "acetate": 0.8, "pH": 7.0, "DO": 30.0,
        "ammonia": 8.0, "OD600": 20.0, "viability": 92.0, "titer": 0.8,
        "CO2": 6.0, "O2": 18.0, "temperature": 37.0, "agitation": 450.0,
    },
    "B. subtilis": {
        "glucose": 4.0, "acetoin": 1.0, "pH": 7.0, "DO": 30.0,
        "ammonia": 8.0, "OD600": 15.0, "viability": 92.0, "titer": 3.0,
        "CO2": 6.0, "O2": 18.0, "temperature": 37.0, "agitation": 450.0,
    },
    "P. pastoris": {
        "glucose": 2.0, "methanol": 2.0, "ethanol": 0.1, "pH": 5.5,
        "DO": 25.0, "ammonia": 8.0, "OD600": 150.0, "viability": 90.0,
        "titer": 2.0, "CO2": 8.0, "O2": 17.0, "temperature": 30.0,
        "agitation": 600.0,
    },
    "S. cerevisiae": {
        "glucose": 3.0, "ethanol": 2.0, "pH": 5.0, "DO": 15.0,
        "ammonia": 8.0, "OD600": 15.0, "viability": 92.0, "titer": 0.3,
        "CO2": 8.0, "O2": 19.0, "temperature": 30.0, "agitation": 350.0,
    },
}

# Slider ranges per parameter
PARAM_RANGES = {
    "glucose":     (0.0, 20.0, 0.1, "g/L"),
    "lactate":     (0.0, 10.0, 0.1, "g/L"),
    "acetate":     (0.0, 10.0, 0.1, "g/L"),
    "acetoin":     (0.0, 10.0, 0.1, "g/L"),
    "ethanol":     (0.0, 20.0, 0.1, "g/L"),
    "methanol":    (0.0, 15.0, 0.1, "g/L"),
    "pH":          (3.0, 9.0, 0.05, ""),
    "DO":          (0.0, 100.0, 1.0, "%"),
    "ammonia":     (0.0, 40.0, 0.5, "mM"),
    "VCD":         (0.0, 120.0, 0.5, "e6/mL"),
    "OD600":       (0.0, 500.0, 1.0, "OD"),
    "viability":   (0.0, 100.0, 1.0, "%"),
    "titer":       (0.0, 20.0, 0.1, "g/L"),
    "CO2":         (0.0, 25.0, 0.5, "%"),
    "O2":          (0.0, 21.0, 0.5, "%"),
    "temperature": (20.0, 55.0, 0.5, "C"),
    "agitation":   (0.0, 1500.0, 10.0, "rpm"),
}

PARAM_RANGES_OVERRIDES = {
    "HEK293": {
        "titer": (0.0, 1e13, 1e9, "vg/mL"),
    }
}

TREND_ICONS = {"stable": "--", "rising": "\u2191", "falling": "\u2193"}

# Which direction is "toward danger" for each parameter direction type
# substrate/indicator falling = running out; byproduct rising = accumulating
_DANGER_DIRECTION = {
    "substrate":            "falling",
    "byproduct":            "rising",
    "indicator":            None,       # pH is bidirectional — handled specially
    "output":               "falling",
    "product":              "falling",
    "control":              None,       # temp/agitation — both directions can be bad
    "substrate_and_inducer":"falling",
    "substrate_and_byproduct": None,
}

# Trend-aware meaning overlays keyed by (current_severity, trend_toward_danger)
# These prepend urgency language to the base meaning
_TREND_WARNINGS = {
    # Currently OK but trending toward danger
    ("OK", True):       "{param} {trend_verb} -- approaching {next_zone} zone -- intervene within 2-4 hours",
    # Currently WARNING and getting worse
    ("WARNING", True):  "{param} {trend_verb} and already in warning -- will reach critical if uncorrected -- act now",
    # Currently CRITICAL and still getting worse
    ("CRITICAL", True): "{param} {trend_verb} deeper into critical -- immediate intervention required",
    # Currently bad but trend is improving
    ("CRITICAL", False): "{param} {trend_verb} -- recovery trend detected -- monitor closely",
    ("WARNING", False):  "{param} {trend_verb} -- improving toward optimal -- maintain current action",
}

# Human-readable zone names for "approaching X zone"
_NEXT_ZONE = {
    "OK":       "warning",
    "WARNING":  "critical",
    "CRITICAL": "critical",
}


def get_trend_meaning(param, state_info, trend):
    """Generate trend-aware meaning overlay. Returns (trend_meaning, urgency_level)."""
    if trend == "stable" or not state_info:
        return None, None

    direction = state_info.get("direction", "")
    danger_dir = _DANGER_DIRECTION.get(direction)
    cur_sev = severity(state_info["state"])

    # For indicator/control params, determine danger contextually
    if danger_dir is None:
        # pH: falling toward acidosis is dangerous, rising toward alkalosis is dangerous
        # Temperature: both directions can be bad
        # Treat any movement away from optimal as toward danger
        if cur_sev == "OK":
            toward_danger = True  # moving away from OK in either direction
        else:
            # Already in warning/critical — any movement is concerning
            toward_danger = True
    else:
        toward_danger = (trend == danger_dir)

    # Improving = trending opposite to danger direction
    if not toward_danger:
        # Only generate recovery messages when currently in bad state
        if cur_sev in ("CRITICAL", "WARNING"):
            key = (cur_sev, False)
        else:
            return None, None  # OK and stable/improving — nothing to add
    else:
        key = (cur_sev, True)

    template = _TREND_WARNINGS.get(key)
    if template is None:
        return None, None

    trend_verb = "declining" if trend == "falling" else "rising"
    next_zone = _NEXT_ZONE.get(cur_sev, "warning")

    trend_meaning = template.format(
        param=param,
        trend_verb=trend_verb,
        next_zone=next_zone,
    )

    # Urgency: high if toward danger and already WARNING+, medium if OK trending bad
    if toward_danger and cur_sev == "CRITICAL":
        urgency = "URGENT"
    elif toward_danger and cur_sev == "WARNING":
        urgency = "HIGH"
    elif toward_danger:
        urgency = "WATCH"
    else:
        urgency = "RECOVERING"

    return trend_meaning, urgency


# ═══════════════════════════════════════════════════════════════════════════
#  SESSION LOG -- CSV-based local logging
# ═══════════════════════════════════════════════════════════════════════════

SESSION_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gem_sessions.csv")

SESSION_HEADER = [
    "timestamp", "organism", "health_score", "n_critical", "n_warning", "n_ok",
    "top_concern_param", "top_concern_state", "top_concern_meaning",
    "readings_json",
]


def log_session(organism, score, states, readings):
    """Append one row to gem_sessions.csv."""
    file_exists = os.path.isfile(SESSION_CSV)

    n_crit = sum(1 for i in states.values() if severity(i["state"]) == "CRITICAL")
    n_warn = sum(1 for i in states.values() if severity(i["state"]) == "WARNING")
    n_ok = len(states) - n_crit - n_warn

    top_param, top_state, top_meaning = "-", "-", "All nominal"
    for sev_level in ("CRITICAL", "WARNING"):
        for p, info in states.items():
            if severity(info["state"]) == sev_level:
                top_param, top_state, top_meaning = p, info["state"], info["meaning"]
                break
        if top_param != "-":
            break

    import json
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        organism,
        score,
        n_crit,
        n_warn,
        n_ok,
        top_param,
        top_state,
        top_meaning[:120],
        json.dumps(readings),
    ]

    with open(SESSION_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(SESSION_HEADER)
        writer.writerow(row)


def load_sessions():
    """Load session log from CSV. Returns list of dicts."""
    if not os.path.isfile(SESSION_CSV):
        return []
    rows = []
    with open(SESSION_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["health_score"] = int(row.get("health_score", 0))
            row["n_critical"] = int(row.get("n_critical", 0))
            row["n_warning"] = int(row.get("n_warning", 0))
            row["n_ok"] = int(row.get("n_ok", 0))
            rows.append(row)
    return rows


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR -- Organism + Strain selection + Dual input columns
# ═══════════════════════════════════════════════════════════════════════════

st.sidebar.title("GEM Map Explorer")
st.sidebar.markdown("**Organism-Aware Metabolic Pathway Mapping**")

# ── Literature scenario selector ─────────────────────────────────────────
_lit_labels = ["(none -- manual input)"] + [
    f"{ds['citation']} -- {ds['context']}" for ds in LITERATURE_DATASETS
]
_lit_selection = st.sidebar.selectbox(
    "Load literature scenario",
    _lit_labels,
    index=0,
    key="lit_selector",
)

# Resolve selected literature dataset
_lit_dataset = None
_lit_organism = None
_lit_readings = None
if _lit_selection != "(none -- manual input)":
    _lit_idx = _lit_labels.index(_lit_selection) - 1  # offset for "(none)" entry
    _lit_dataset = LITERATURE_DATASETS[_lit_idx]
    _lit_organism = _lit_dataset["organism"]
    _lit_readings = _lit_dataset["readings"]

# Organism dropdown -- default to literature organism if one is loaded
_all_organisms = list_organisms()
_org_default_idx = 0
if _lit_organism and _lit_organism in _all_organisms:
    _org_default_idx = _all_organisms.index(_lit_organism)

base_organism = st.sidebar.selectbox(
    "Select Organism",
    _all_organisms,
    index=_org_default_idx,
)

# Strain dropdown
strain_keys = list_strains(base_organism)
if strain_keys:
    strain_names = ["(base organism)"] + [k.split("|")[1] for k in strain_keys]
    selected_strain = st.sidebar.selectbox(
        "Select Strain",
        strain_names,
        index=0,
    )
    if selected_strain == "(base organism)":
        organism = base_organism
        strain_desc = None
    else:
        organism = f"{base_organism}|{selected_strain}"
        info = get_strain_info(organism)
        strain_desc = info["description"] if info else None
else:
    organism = base_organism
    strain_desc = None

if strain_desc:
    st.sidebar.info(f"**{organism.split('|')[1]}**: {strain_desc}")

# Show literature dataset info if loaded
if _lit_dataset:
    st.sidebar.success(
        f"**Loaded:** {_lit_dataset['citation']}\n\n"
        f"{_lit_dataset['context']}"
    )

defaults = HEALTHY_DEFAULTS.get(base_organism, {})
params = list(defaults.keys())

st.sidebar.markdown("---")

# ── Dual input columns in sidebar ────────────────────────────────────────
st.sidebar.markdown("### Current Run")
show_trends = st.sidebar.checkbox("Show trend selectors", value=False, key="show_trends")
readings_current = {}
trends = {}
for param in params:
    rng = PARAM_RANGES_OVERRIDES.get(base_organism, {}).get(param, PARAM_RANGES.get(param))
    if rng is None:
        continue
    lo, hi, step, unit = rng

    # Use literature value if loaded and available, otherwise healthy default
    if _lit_readings and param in _lit_readings:
        default = float(_lit_readings[param])
    else:
        default = defaults.get(param, (lo + hi) / 2)

    # Clamp to slider range
    default = max(lo, min(hi, default))

    label = f"{param}" + (f" ({unit})" if unit else "")
    val = st.sidebar.slider(label, min_value=lo, max_value=hi, value=default, step=step, key=f"cur_{organism}_{_lit_selection}_{param}")
    readings_current[param] = val
    if show_trends:
        trend = st.sidebar.radio(
            f"{param} trend",
            ["stable", "rising", "falling"],
            index=0,
            horizontal=True,
            key=f"trend_{organism}_{_lit_selection}_{param}",
        )
        trends[param] = trend
    else:
        trends[param] = "stable"

st.sidebar.markdown("---")
st.sidebar.markdown("### Reference Run")
ref_mode = st.sidebar.radio(
    "Reference source",
    ["Healthy defaults", "Custom sliders"],
    index=0,
    key="ref_mode",
)

readings_ref = {}
if ref_mode == "Healthy defaults":
    readings_ref = dict(defaults)
    st.sidebar.caption("Using healthy defaults for this organism as reference.")
else:
    for param in params:
        rng = PARAM_RANGES_OVERRIDES.get(base_organism, {}).get(param, PARAM_RANGES.get(param))
        if rng is None:
            continue
        lo, hi, step, unit = rng
        default = defaults.get(param, (lo + hi) / 2)
        label = f"{param}" + (f" ({unit})" if unit else "")
        val = st.sidebar.slider(label, min_value=lo, max_value=hi, value=default, step=step, key=f"ref_{organism}_{_lit_selection}_{param}")
        readings_ref[param] = val


# ═══════════════════════════════════════════════════════════════════════════
#  COMPUTE STATES FOR BOTH RUNS
# ═══════════════════════════════════════════════════════════════════════════

states_cur = get_all_pathway_states(readings_current, organism=organism)
states_ref = get_all_pathway_states(readings_ref, organism=organism)

# Inject trend data into current states
for param, info in states_cur.items():
    # Resolve alias: the param key in states_cur is the resolved name (e.g. "VCD" not "OD600")
    # Trends dict uses the original input names, so check both
    trend = trends.get(param, "stable")
    if trend == "stable":
        # Try original input param names that may have been aliased
        for orig_p, t in trends.items():
            if t != "stable" and orig_p != param:
                from gem_map import PARAM_ALIASES
                resolved = PARAM_ALIASES.get(organism, {}).get(orig_p, orig_p)
                if resolved == param:
                    trend = t
                    break

    info["trend"] = trend
    info["trend_icon"] = TREND_ICONS.get(trend, "--")
    trend_meaning, urgency = get_trend_meaning(param, info, trend)
    info["trend_meaning"] = trend_meaning
    info["trend_urgency"] = urgency

score_cur = health_score(states_cur)
score_ref = health_score(states_ref)

# Compute divergence
all_params = list(dict.fromkeys(list(states_cur.keys()) + list(states_ref.keys())))
diverged = []
for p in all_params:
    s_cur = states_cur.get(p, {}).get("state", "")
    s_ref = states_ref.get(p, {}).get("state", "")
    if s_cur != s_ref:
        diverged.append(p)
divergence_count = len(diverged)
divergence_pct = (divergence_count / len(all_params) * 100) if all_params else 0


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════

st.title("GEM Map Explorer")
display_name = organism.replace("|", " > ") if "|" in organism else organism
st.markdown(f"### {display_name} -- Dual-Run Comparison")

# ── Health scores side by side ───────────────────────────────────────────
col_cur_score, col_div_score, col_ref_score = st.columns([2, 1, 2])


def render_score_card(col, score, label):
    color = "#22C55E" if score >= 75 else ("#FFA500" if score >= 50 else "#FF4444")
    with col:
        st.html(
            f"""
            <div style="text-align:center; padding:15px; background:{color}22;
                        border:2px solid {color}; border-radius:12px;">
                <div style="font-size:42px; font-weight:bold; color:{color};">{score}</div>
                <div style="font-size:12px; color:{color};">{label}</div>
            </div>
            """
        )


render_score_card(col_cur_score, score_cur, "CURRENT RUN")

with col_div_score:
    div_color = "#FF4444" if divergence_count > 4 else ("#FFA500" if divergence_count > 0 else "#22C55E")
    st.html(
        f"""
        <div style="text-align:center; padding:15px; background:{div_color}22;
                    border:2px solid {div_color}; border-radius:12px;">
            <div style="font-size:42px; font-weight:bold; color:{div_color};">{divergence_count}</div>
            <div style="font-size:12px; color:{div_color};">DIVERGED ({divergence_pct:.0f}%)</div>
        </div>
        """
    )

render_score_card(col_ref_score, score_ref, "REFERENCE RUN")

# ── Summary counts ───────────────────────────────────────────────────────
col_cur_sum, col_ref_sum = st.columns(2)
for col, states, label in [(col_cur_sum, states_cur, "Current"), (col_ref_sum, states_ref, "Reference")]:
    with col:
        nc = sum(1 for i in states.values() if severity(i["state"]) == "CRITICAL")
        nw = sum(1 for i in states.values() if severity(i["state"]) == "WARNING")
        no = len(states) - nc - nw
        st.markdown(
            f"**{label}:** "
            f"\U0001f534 {nc} Critical &nbsp; "
            f"\U0001f7e1 {nw} Warning &nbsp; "
            f"\U0001f7e2 {no} Optimal"
        )

# ── Log button ───────────────────────────────────────────────────────────
log_col1, log_col2 = st.columns([1, 3])
with log_col1:
    if st.button("Log this reading", type="primary"):
        log_session(organism, score_cur, states_cur, readings_current)
        st.success("Logged to gem_sessions.csv")
with log_col2:
    sessions = load_sessions()
    if sessions:
        st.caption(f"{len(sessions)} sessions logged")

# ── Critical alerts (current run only) ──────────────────────────────────
criticals = {p: i for p, i in states_cur.items() if severity(i["state"]) == "CRITICAL"}
if criticals:
    st.markdown("---")
    st.markdown("### \U0001f534 CRITICAL ALERTS (Current Run)")
    for param, info in criticals.items():
        unit = info["unit"] if info["unit"] else ""
        ref_state = states_ref.get(param, {}).get("state", "?")
        was_critical_in_ref = severity(ref_state) == "CRITICAL" if ref_state != "?" else False
        new_flag = "" if was_critical_in_ref else " **[NEW since reference]**"
        st.error(
            f"**{param}** = {info['value']} {unit} -- "
            f"State: `{info['state']}` | "
            f"Ref was: `{ref_state}`{new_flag}\n\n"
            f"{info['meaning']}"
        )
        if info["downstream"]:
            st.warning(
                f"**Downstream cascade from {param}:** "
                f"Will affect **{', '.join(info['downstream'])}** next"
            )

# ── Downstream cascade warnings (WARNING + CRITICAL states) ─────────────
cascade_params = {p: i for p, i in states_cur.items()
                  if severity(i["state"]) in ("CRITICAL", "WARNING") and i.get("downstream")}
# Exclude params already shown in critical alerts to avoid duplication
cascade_warnings_only = {p: i for p, i in cascade_params.items() if severity(i["state"]) == "WARNING"}
if cascade_warnings_only:
    st.markdown("---")
    st.markdown("### Downstream Cascade Warnings")

    # Contextual downstream messages for key parameters
    _CASCADE_CONTEXT = {
        "glucose": {
            "flux_limited": {
                "lactate": "Metabolism shifting -- monitor for lactate consumption reversal or continued production",
                "VCD": "Cell growth will slow within 12-24h at this glucose level",
                "OD600": "Biomass accumulation rate declining -- growth phase ending",
                "titer": "Specific productivity at risk if glucose remains below 1 g/L",
                "ammonia": "Amino acid catabolism may increase as cells scavenge alternative carbon",
            },
            "carbon_starved": {
                "lactate": "Cells may begin consuming lactate as carbon source -- lactate could drop",
                "VCD": "Growth arrest imminent -- ppGpp stringent response activating",
                "OD600": "Growth halting -- carbon starvation response",
                "titer": "Product synthesis stopping -- no carbon for amino acid synthesis",
                "ammonia": "Protein degradation releasing ammonia as cells catabolise reserves",
            },
        },
        "DO": {
            "hypoxic": {
                "lactate": "Anaerobic glycolysis increasing -- lactate production accelerating",
                "CO2": "Respiratory CO2 dropping as OXPHOS shuts down",
                "O2": "Off-gas O2 dropping -- OUR exceeding OTR",
            },
        },
        "ammonia": {
            "toxic": {
                "VCD": "Growth inhibition from ammonia -- doubling time increasing",
                "OD600": "Growth rate declining under ammonia stress",
                "viability": "Ammonia-induced apoptosis -- viability will decline",
                "titer": "Glycosylation quality degrading -- product heterogeneity increasing",
            },
        },
    }

    for param, info in cascade_warnings_only.items():
        unit = info["unit"] if info["unit"] else ""
        state = info["state"]
        context = _CASCADE_CONTEXT.get(param, {}).get(state, {})

        if context:
            # Rich contextual cascade
            cascade_lines = []
            for ds_param in info["downstream"]:
                msg = context.get(ds_param, f"{ds_param} may be affected")
                ds_state = states_cur.get(ds_param, {}).get("state", "?")
                ds_sev = severity(ds_state) if ds_state != "?" else "OK"
                emoji = severity_emoji(ds_sev)
                cascade_lines.append(f"- {emoji} **{ds_param}** ({ds_state}): {msg}")
            st.warning(
                f"**{param}** = {info['value']} {unit} [{state}] -- downstream cascade:\n\n"
                + "\n".join(cascade_lines)
            )
        else:
            # Generic cascade
            st.warning(
                f"**{param}** = {info['value']} {unit} [{state}] -- "
                f"will affect **{', '.join(info['downstream'])}**"
            )

# ── Trend alerts ─────────────────────────────────────────────────────────
trend_alerts = {p: i for p, i in states_cur.items() if i.get("trend_meaning")}
if trend_alerts:
    st.markdown("---")
    st.markdown("### Trend Alerts")
    urgency_order = {"URGENT": 0, "HIGH": 1, "WATCH": 2, "RECOVERING": 3}
    sorted_alerts = sorted(trend_alerts.items(), key=lambda x: urgency_order.get(x[1].get("trend_urgency", ""), 4))

    alert_html = """
    <style>
    .trend-table { width:100%; border-collapse:collapse; font-size:14px; }
    .trend-table th { background:#1a1a2e; color:#eee; padding:10px; text-align:left; border-bottom:2px solid #444; }
    .trend-table td { padding:8px 10px; border-bottom:1px solid #333; }
    .trend-urgent { background:#FF444425; }
    .trend-high { background:#FF660020; }
    .trend-watch { background:#FFA50015; }
    .trend-recovering { background:#22C55E15; }
    </style>
    <table class="trend-table">
    <tr><th>Urgency</th><th>Parameter</th><th>Value</th><th>State</th><th>Trend</th><th>Trend Interpretation</th></tr>
    """
    urgency_colors = {"URGENT": "#FF4444", "HIGH": "#FF6600", "WATCH": "#FFA500", "RECOVERING": "#22C55E"}
    urgency_icons = {"URGENT": "\u26a0\ufe0f", "HIGH": "\u2757", "WATCH": "\U0001f440", "RECOVERING": "\u2705"}
    for p, info in sorted_alerts:
        urg = info.get("trend_urgency", "")
        urg_color = urgency_colors.get(urg, "#888")
        urg_icon = urgency_icons.get(urg, "")
        row_class = f"trend-{urg.lower()}" if urg else ""
        unit = info["unit"] if info["unit"] else ""
        val_str = f"{info['value']:.4g}" if isinstance(info['value'], float) else str(info['value'])
        trend_icon = info.get("trend_icon", "--")
        trend_meaning = info.get("trend_meaning", "")
        sev_color = severity_color(severity(info["state"]))

        alert_html += f"""
        <tr class="{row_class}">
            <td><span style="color:{urg_color}; font-weight:bold;">{urg_icon} {urg}</span></td>
            <td><strong>{p}</strong></td>
            <td>{val_str} {unit}</td>
            <td><span style="color:{sev_color}; font-weight:bold;">{info['state']}</span></td>
            <td style="font-size:18px; text-align:center;">{trend_icon}</td>
            <td style="font-size:12px; color:{urg_color};">{trend_meaning}</td>
        </tr>
        """
    alert_html += "</table>"
    st.html(alert_html)

# ── Divergence detail ────────────────────────────────────────────────────
if diverged:
    st.markdown("---")
    st.markdown(f"### State Divergence -- {divergence_count} parameters changed")

    div_html = """
    <style>
    .div-table { width:100%; border-collapse:collapse; font-size:14px; }
    .div-table th { background:#1a1a2e; color:#eee; padding:10px; text-align:left; border-bottom:2px solid #444; }
    .div-table td { padding:8px 10px; border-bottom:1px solid #333; }
    .div-row { background:#FF444415; }
    </style>
    <table class="div-table">
    <tr>
        <th>Parameter</th>
        <th>Current Value</th>
        <th>Current State</th>
        <th>Reference Value</th>
        <th>Reference State</th>
        <th>Direction</th>
    </tr>
    """
    for p in diverged:
        ci = states_cur.get(p, {})
        ri = states_ref.get(p, {})
        c_state = ci.get("state", "-")
        r_state = ri.get("state", "-")
        c_sev = severity(c_state) if c_state != "-" else "OK"
        r_sev = severity(r_state) if r_state != "-" else "OK"
        c_color = severity_color(c_sev)
        r_color = severity_color(r_sev)
        c_val = ci.get("value", "-")
        r_val = ri.get("value", "-")
        c_unit = ci.get("unit", "") if ci else ""
        c_val_str = f"{c_val:.4g}" if isinstance(c_val, float) else str(c_val)
        r_val_str = f"{r_val:.4g}" if isinstance(r_val, float) else str(r_val)

        # Direction arrow
        sev_rank = {"OK": 0, "WARNING": 1, "CRITICAL": 2}
        if sev_rank.get(c_sev, 0) > sev_rank.get(r_sev, 0):
            direction = '<span style="color:#FF4444; font-weight:bold;">&#9660; WORSE</span>'
        elif sev_rank.get(c_sev, 0) < sev_rank.get(r_sev, 0):
            direction = '<span style="color:#22C55E; font-weight:bold;">&#9650; BETTER</span>'
        else:
            direction = '<span style="color:#FFA500;">&#9654; SHIFTED</span>'

        div_html += f"""
        <tr class="div-row">
            <td><strong>{p}</strong></td>
            <td>{c_val_str} {c_unit}</td>
            <td><span style="color:{c_color}; font-weight:bold;">{c_state}</span></td>
            <td>{r_val_str} {c_unit}</td>
            <td><span style="color:{r_color}; font-weight:bold;">{r_state}</span></td>
            <td>{direction}</td>
        </tr>
        """
    div_html += "</table>"
    st.html(div_html)


# ── Side-by-side parameter state tables ──────────────────────────────────
st.markdown("---")
st.markdown("### Full Parameter Comparison")

compare_html = """
<style>
.cmp-table { width:100%; border-collapse:collapse; font-size:13px; }
.cmp-table th { background:#1a1a2e; color:#eee; padding:8px; text-align:left; border-bottom:2px solid #444; }
.cmp-table td { padding:6px 8px; border-bottom:1px solid #333; }
.cmp-table tr:hover { background:#1a1a2e44; }
.cmp-diverged { background:#FF444418; }
</style>
<table class="cmp-table">
<tr>
    <th>Param</th>
    <th colspan="5" style="text-align:center; border-right:2px solid #444;">Current Run</th>
    <th colspan="3" style="text-align:center; border-right:2px solid #444;">Reference Run</th>
    <th>Match</th>
</tr>
<tr>
    <th></th>
    <th>Value</th><th>Trend</th><th>State</th><th>Zone Confidence</th><th style="border-right:2px solid #444;">Meaning</th>
    <th>Value</th><th>State</th><th style="border-right:2px solid #444;">Meaning</th>
    <th></th>
</tr>
"""

for p in all_params:
    ci = states_cur.get(p, {})
    ri = states_ref.get(p, {})
    c_state = ci.get("state", "-")
    r_state = ri.get("state", "-")
    is_div = p in diverged
    row_class = 'class="cmp-diverged"' if is_div else ""

    c_sev = severity(c_state) if c_state != "-" else "OK"
    r_sev = severity(r_state) if r_state != "-" else "OK"
    c_color = severity_color(c_sev)
    r_color = severity_color(r_sev)

    c_val = ci.get("value", "-")
    r_val = ri.get("value", "-")
    c_unit = ci.get("unit", "") if ci else ""
    c_val_str = f"{c_val:.4g}" if isinstance(c_val, float) else str(c_val)
    r_val_str = f"{r_val:.4g}" if isinstance(r_val, float) else str(r_val)

    # Use trend meaning if available, otherwise base meaning
    c_trend_meaning = ci.get("trend_meaning", "")
    c_meaning = c_trend_meaning[:55] if c_trend_meaning else ci.get("meaning", "")[:55]
    c_meaning_color = "color:#FFA500;" if c_trend_meaning else ""
    r_meaning = ri.get("meaning", "")[:55]

    c_trend_icon = ci.get("trend_icon", "--") if ci else "--"

    match_icon = '<span style="color:#FF4444; font-size:16px;">&#10008;</span>' if is_div else '<span style="color:#22C55E; font-size:16px;">&#10004;</span>'

    # Zone confidence bar
    c_conf = ci.get("zone_confidence", 50) if ci else 50
    c_conf_label = ci.get("confidence_label", "MED") if ci else "MED"
    conf_bar_color = "#22C55E" if c_conf >= 70 else ("#FFA500" if c_conf >= 30 else "#FF4444")
    conf_bar = (
        f'<div style="display:flex; align-items:center; gap:4px;">'
        f'<div style="width:50px; height:10px; background:#333; border-radius:5px; overflow:hidden;">'
        f'<div style="width:{c_conf}%; height:100%; background:{conf_bar_color};"></div></div>'
        f'<span style="font-size:10px; color:{conf_bar_color}; font-weight:bold;">{c_conf_label}</span></div>'
    )

    compare_html += f"""
    <tr {row_class}>
        <td><strong>{p}</strong></td>
        <td>{c_val_str} {c_unit}</td>
        <td style="font-size:16px; text-align:center;">{c_trend_icon}</td>
        <td><span style="color:{c_color}; font-weight:bold;">{c_state}</span></td>
        <td>{conf_bar}</td>
        <td style="font-size:11px; {c_meaning_color} border-right:2px solid #444;">{c_meaning}</td>
        <td>{r_val_str} {c_unit}</td>
        <td><span style="color:{r_color}; font-weight:bold;">{r_state}</span></td>
        <td style="font-size:11px; border-right:2px solid #444;">{r_meaning}</td>
        <td style="text-align:center;">{match_icon}</td>
    </tr>
    """

compare_html += "</table>"
st.html(compare_html)

# ── Session History ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Session History")

all_sessions = load_sessions()
if not all_sessions:
    st.info("No sessions logged yet. Click **Log this reading** to start tracking.")
else:
    # Health score trend chart
    import pandas as pd

    df = pd.DataFrame(all_sessions)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    st.markdown(f"**{len(df)} sessions logged** -- health score over time")

    chart_data = df[["timestamp", "health_score", "organism"]].copy()
    chart_data = chart_data.set_index("timestamp")

    st.line_chart(chart_data["health_score"], use_container_width=True, height=250)

    # Session log table
    with st.expander("Full session log", expanded=False):
        display_df = df[["timestamp", "organism", "health_score", "n_critical", "n_warning", "n_ok", "top_concern_param", "top_concern_state"]].copy()
        display_df.columns = ["Time", "Organism", "Score", "Crit", "Warn", "OK", "Top Concern", "State"]
        display_df = display_df.sort_values("Time", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Clear log button
    clear_col1, clear_col2 = st.columns([1, 5])
    with clear_col1:
        if st.button("Clear session log"):
            if os.path.isfile(SESSION_CSV):
                os.remove(SESSION_CSV)
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  STRESS SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("### Stress Simulator")
st.caption("Select a stress type and step through the metabolic cascade as it unfolds.")

# Stress profiles: each defines per-step deltas on the primary parameter,
# plus downstream cascade rules that fire when a parameter crosses a threshold.
# Deltas are applied cumulatively across 8 steps (step 0 = baseline).
STRESS_PROFILES = {
    "Glucose depletion": {
        "description": "Feed pump failure or underfeeding -- glucose drops over 8 hours",
        "primary": "glucose",
        "primary_deltas": [0, -0.4, -0.5, -0.5, -0.3, -0.2, -0.1, -0.05],
        "cascade_rules": [
            {"trigger_param": "glucose", "trigger_below": 2.0,
             "effects": {"lactate": -0.3, "VCD": -0.8, "OD600": -0.8, "viability": -1.0}},
            {"trigger_param": "glucose", "trigger_below": 1.0,
             "effects": {"lactate": -0.5, "VCD": -1.5, "OD600": -1.5, "viability": -3.0, "titer": -0.1, "DO": 3.0}},
        ],
        "applicable": ["CHO", "CHO-S", "HEK293", "NS0", "Sp2/0", "BHK-21", "E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"],
    },
    "Ammonia accumulation": {
        "description": "Glutamine catabolism drives ammonia rise -- toxicity cascade",
        "primary": "ammonia",
        "primary_deltas": [0, 0.5, 0.6, 0.8, 0.9, 1.0, 0.8, 0.5],
        "cascade_rules": [
            {"trigger_param": "ammonia", "trigger_above": 5.0,
             "effects": {"viability": -1.0, "VCD": -0.5, "OD600": -0.5}},
            {"trigger_param": "ammonia", "trigger_above": 7.0,
             "effects": {"viability": -2.5, "VCD": -1.0, "OD600": -1.0, "titer": -0.15, "pH": 0.03}},
        ],
        "applicable": ["CHO", "CHO-S", "HEK293", "NS0", "Sp2/0", "BHK-21", "E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"],
    },
    "Oxygen limitation": {
        "description": "Sparge failure or high density -- DO crashes, metabolism shifts anaerobic",
        "primary": "DO",
        "primary_deltas": [0, -4.0, -5.0, -5.0, -4.0, -3.0, -2.0, -1.0],
        "cascade_rules": [
            {"trigger_param": "DO", "trigger_below": 25.0,
             "effects": {"lactate": 0.4, "acetate": 0.3, "acetoin": 0.3, "ethanol": 0.3, "CO2": -0.5}},
            {"trigger_param": "DO", "trigger_below": 15.0,
             "effects": {"lactate": 0.8, "acetate": 0.6, "acetoin": 0.5, "ethanol": 0.5, "pH": -0.03, "viability": -1.5, "CO2": -1.0}},
        ],
        "applicable": ["CHO", "CHO-S", "HEK293", "NS0", "Sp2/0", "BHK-21", "E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"],
    },
    "Heat shock": {
        "description": "Temperature control failure -- metabolic rate spikes then viability crashes",
        "primary": "temperature",
        "primary_deltas": [0, 0.3, 0.5, 0.5, 0.3, 0.2, 0.1, 0.1],
        "cascade_rules": [
            {"trigger_param": "temperature", "trigger_above": 38.0,
             "effects": {"viability": -1.0, "glucose": -0.2, "lactate": 0.3, "DO": -2.0}},
            {"trigger_param": "temperature", "trigger_above": 40.0,
             "effects": {"viability": -3.0, "VCD": -1.0, "OD600": -1.0, "titer": -0.1, "lactate": 0.5}},
        ],
        "applicable": ["CHO", "CHO-S", "HEK293", "NS0", "Sp2/0", "BHK-21", "E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"],
    },
    "Acetate/lactate overflow": {
        "description": "Glucose overfeed driving overflow metabolite accumulation",
        "primary": "glucose",
        "primary_deltas": [0, 0.5, 0.6, 0.5, 0.3, 0.2, 0.1, 0.1],
        "cascade_rules": [
            {"trigger_param": "glucose", "trigger_above": 5.0,
             "effects": {"lactate": 0.5, "acetate": 0.4, "acetoin": 0.3, "ethanol": 0.4}},
            {"trigger_param": "glucose", "trigger_above": 7.0,
             "effects": {"lactate": 0.8, "acetate": 0.7, "acetoin": 0.5, "ethanol": 0.6, "pH": -0.04, "viability": -0.5}},
        ],
        "applicable": ["CHO", "CHO-S", "HEK293", "NS0", "Sp2/0", "BHK-21", "E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"],
    },
}

sim_col1, sim_col2 = st.columns([1, 1])
with sim_col1:
    sim_stress = st.selectbox("Stress type", list(STRESS_PROFILES.keys()), key="sim_stress")
with sim_col2:
    sim_start = st.selectbox("Starting scenario", ["Healthy baseline (current organism)"], key="sim_start")

profile = STRESS_PROFILES[sim_stress]
st.caption(f"**{sim_stress}:** {profile['description']}")

# Build simulation steps
n_steps = len(profile["primary_deltas"])
sim_readings_steps = []
base_readings = dict(defaults)  # healthy baseline for current organism

for step in range(n_steps):
    if step == 0:
        current = dict(base_readings)
    else:
        current = dict(sim_readings_steps[step - 1])

    # Apply primary delta
    primary = profile["primary"]
    if primary in current:
        current[primary] = current[primary] + profile["primary_deltas"][step]
        current[primary] = max(0.0, current[primary])

    # Apply cascade rules
    for rule in profile["cascade_rules"]:
        tp = rule["trigger_param"]
        if tp not in current:
            continue
        fire = False
        if "trigger_below" in rule and current[tp] <= rule["trigger_below"]:
            fire = True
        if "trigger_above" in rule and current[tp] >= rule["trigger_above"]:
            fire = True
        if fire:
            for effect_param, delta in rule["effects"].items():
                if effect_param in current:
                    current[effect_param] = max(0.0, current[effect_param] + delta)

    sim_readings_steps.append(current)

# Step selector
sim_step = st.slider("Simulation step (hours)", 0, n_steps - 1, 0, key="sim_step")

# Compute states for step 0 and current step
states_step0 = get_all_pathway_states(sim_readings_steps[0], organism=organism)
states_stepN = get_all_pathway_states(sim_readings_steps[sim_step], organism=organism)
score_step0 = health_score(states_step0)
score_stepN = health_score(states_stepN)

# Score cards for simulator
sim_sc1, sim_sc2 = st.columns(2)
with sim_sc1:
    sc0_color = "#22C55E" if score_step0 >= 75 else ("#FFA500" if score_step0 >= 50 else "#FF4444")
    st.html(
        f'<div style="text-align:center; padding:10px; background:{sc0_color}22; '
        f'border:2px solid {sc0_color}; border-radius:10px;">'
        f'<div style="font-size:32px; font-weight:bold; color:{sc0_color};">{score_step0}</div>'
        f'<div style="font-size:11px; color:{sc0_color};">STEP 0 (baseline)</div></div>'
    )
with sim_sc2:
    scN_color = "#22C55E" if score_stepN >= 75 else ("#FFA500" if score_stepN >= 50 else "#FF4444")
    st.html(
        f'<div style="text-align:center; padding:10px; background:{scN_color}22; '
        f'border:2px solid {scN_color}; border-radius:10px;">'
        f'<div style="font-size:32px; font-weight:bold; color:{scN_color};">{score_stepN}</div>'
        f'<div style="font-size:11px; color:{scN_color};">STEP {sim_step} (hour {sim_step})</div></div>'
    )

# Build simulation table
sim_all_params = list(dict.fromkeys(list(states_step0.keys()) + list(states_stepN.keys())))

sim_html = """
<style>
.sim-table { width:100%; border-collapse:collapse; font-size:13px; }
.sim-table th { background:#1a1a2e; color:#eee; padding:8px; text-align:left; border-bottom:2px solid #444; }
.sim-table td { padding:6px 8px; border-bottom:1px solid #333; }
.sim-changed { background:#FF444418; }
</style>
<table class="sim-table">
<tr>
    <th>Parameter</th>
    <th>Baseline Value</th>
    <th>Baseline State</th>
    <th>Step """ + str(sim_step) + """ Value</th>
    <th>Step """ + str(sim_step) + """ State</th>
    <th>Confidence</th>
    <th>Change</th>
    <th>Cascade</th>
</tr>
"""

for p in sim_all_params:
    s0 = states_step0.get(p, {})
    sN = states_stepN.get(p, {})
    s0_state = s0.get("state", "-")
    sN_state = sN.get("state", "-")
    changed = s0_state != sN_state
    row_class = 'class="sim-changed"' if changed else ""

    s0_sev = severity(s0_state) if s0_state != "-" else "OK"
    sN_sev = severity(sN_state) if sN_state != "-" else "OK"
    s0_color = severity_color(s0_sev)
    sN_color = severity_color(sN_sev)

    s0_val = s0.get("value", "-")
    sN_val = sN.get("value", "-")
    unit = s0.get("unit", "") or sN.get("unit", "")
    s0_str = f"{s0_val:.4g}" if isinstance(s0_val, float) else str(s0_val)
    sN_str = f"{sN_val:.4g}" if isinstance(sN_val, float) else str(sN_val)

    # Confidence bar
    sN_conf = sN.get("zone_confidence", 50) if sN else 50
    sN_conf_label = sN.get("confidence_label", "MED") if sN else "MED"
    conf_bar_color = "#22C55E" if sN_conf >= 70 else ("#FFA500" if sN_conf >= 30 else "#FF4444")
    conf_bar = (
        f'<div style="display:flex; align-items:center; gap:4px;">'
        f'<div style="width:40px; height:8px; background:#333; border-radius:4px; overflow:hidden;">'
        f'<div style="width:{sN_conf}%; height:100%; background:{conf_bar_color};"></div></div>'
        f'<span style="font-size:10px; color:{conf_bar_color}; font-weight:bold;">{sN_conf_label}</span></div>'
    )

    # Change indicator
    sev_rank = {"OK": 0, "WARNING": 1, "CRITICAL": 2}
    if not changed:
        change_cell = '<span style="color:#666;">--</span>'
    elif sev_rank.get(sN_sev, 0) > sev_rank.get(s0_sev, 0):
        change_cell = '<span style="color:#FF4444; font-weight:bold;">&#9660; WORSE</span>'
    elif sev_rank.get(sN_sev, 0) < sev_rank.get(s0_sev, 0):
        change_cell = '<span style="color:#22C55E; font-weight:bold;">&#9650; BETTER</span>'
    else:
        change_cell = '<span style="color:#FFA500;">&#9654; SHIFTED</span>'

    # Cascade indicator: is this parameter a downstream effect of the primary?
    is_primary = (p == profile["primary"] or
                  (p in ("VCD", "OD600") and profile["primary"] in ("VCD", "OD600")))
    is_cascade = changed and not is_primary
    cascade_cell = '<span style="color:#FFA500;">&#8618; cascade</span>' if is_cascade else (
        '<span style="color:#FF4444; font-weight:bold;">&#9733; primary</span>' if (is_primary and changed) else ""
    )

    sim_html += f"""
    <tr {row_class}>
        <td><strong>{p}</strong></td>
        <td>{s0_str} {unit}</td>
        <td><span style="color:{s0_color}; font-weight:bold;">{s0_state}</span></td>
        <td>{sN_str} {unit}</td>
        <td><span style="color:{sN_color}; font-weight:bold;">{sN_state}</span></td>
        <td>{conf_bar}</td>
        <td>{change_cell}</td>
        <td>{cascade_cell}</td>
    </tr>
    """

sim_html += "</table>"
st.html(sim_html)

# Cascade narrative
changed_params = [p for p in sim_all_params if states_step0.get(p, {}).get("state") != states_stepN.get(p, {}).get("state")]
if changed_params and sim_step > 0:
    st.markdown("**Cascade narrative:**")
    narrative_parts = []
    for p in changed_params:
        s0_state = states_step0.get(p, {}).get("state", "?")
        sN_state = states_stepN.get(p, {}).get("state", "?")
        sN_meaning = states_stepN.get(p, {}).get("meaning", "")[:80]
        narrative_parts.append(f"- **{p}**: `{s0_state}` -> `{sN_state}` -- {sN_meaning}")
    st.markdown("\n".join(narrative_parts))


# ── Footer ───────────────────────────────────────────────────────────────
st.markdown("---")
st.html(
    f"<div style='text-align:center; color:#888; font-size:12px;'>"
    f"GEM Map Explorer | {len(list_organisms())} organisms | "
    f"{len(list_strains())} strains | "
    f"Dual-run comparison mode | "
    f"Powered by gem_map.py | Synapse Build"
    f"</div>"
)
