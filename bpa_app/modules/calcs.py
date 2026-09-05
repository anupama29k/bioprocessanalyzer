"""
Core bioprocess calculations.
Batch, fed-batch, continuous modes.
Multiple substrates, multiple products.
No company names.
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress
from scipy.optimize import minimize
from scipy.integrate import solve_ivp

# ── Substrate database ────────────────────────────────────────────────────────
SUBSTRATE_DB = {
    "Glucose":  {"formula":"C6H12O6",   "C":6,  "H":12,"O":6, "N":0,"MW":180.16,"gamma":4.00},
    "Glycerol": {"formula":"C3H8O3",    "C":3,  "H":8, "O":3, "N":0,"MW":92.09, "gamma":4.67},
    "Sucrose":  {"formula":"C12H22O11", "C":12, "H":22,"O":11,"N":0,"MW":342.30,"gamma":4.00},
    "Acetate":  {"formula":"C2H4O2",    "C":2,  "H":4, "O":2, "N":0,"MW":60.05, "gamma":4.00},
    "Xylose":   {"formula":"C5H10O5",   "C":5,  "H":10,"O":5, "N":0,"MW":150.13,"gamma":4.00},
    "Methanol": {"formula":"CH4O",      "C":1,  "H":4, "O":1, "N":0,"MW":32.04, "gamma":6.00},
    "Fructose": {"formula":"C6H12O6",   "C":6,  "H":12,"O":6, "N":0,"MW":180.16,"gamma":4.00},
    "Lactose":  {"formula":"C12H22O11", "C":12, "H":22,"O":11,"N":0,"MW":342.30,"gamma":4.00},
    "Custom":   {"formula":"",          "C":6,  "H":12,"O":6, "N":0,"MW":180.16,"gamma":4.00},
}

# ── Biomass database ──────────────────────────────────────────────────────────
BIOMASS_DB = {
    "E. coli":           {"C":1,"H":1.77,"O":0.49,"N":0.24,"MW":24.6,"gamma":4.07},
    "S. cerevisiae":     {"C":1,"H":1.82,"O":0.56,"N":0.17,"MW":25.1,"gamma":4.12},
    "B. subtilis":       {"C":1,"H":1.73,"O":0.46,"N":0.22,"MW":24.0,"gamma":4.17},
    "K. phaffii":        {"C":1,"H":1.80,"O":0.52,"N":0.20,"MW":24.7,"gamma":4.12},
    "C. glutamicum":     {"C":1,"H":1.74,"O":0.45,"N":0.22,"MW":24.1,"gamma":4.20},
    "C. acetobutylicum": {"C":1,"H":1.75,"O":0.50,"N":0.22,"MW":24.3,"gamma":4.05},
    "A. terreus":        {"C":1,"H":1.72,"O":0.55,"N":0.18,"MW":24.8,"gamma":3.98},
    "Streptomyces sp.":  {"C":1,"H":1.76,"O":0.47,"N":0.23,"MW":24.4,"gamma":4.10},
    "Custom":            {"C":1,"H":1.77,"O":0.49,"N":0.24,"MW":24.6,"gamma":4.07},
}

# ── Literature reference database ─────────────────────────────────────────────
LBIO = {
    "E. coli":{
        "M9 minimal glucose":  {"mu_min":0.6,"mu_max":1.0,"td_min":42,"td_max":70, "Yxs":0.45,"Yxs_r":"0.38–0.52"},
        "LB rich":             {"mu_min":1.0,"mu_max":1.7,"td_min":24,"td_max":42, "Yxs":0.45,"Yxs_r":"0.38–0.52"},
        "Defined industrial":  {"mu_min":0.5,"mu_max":0.9,"td_min":46,"td_max":83, "Yxs":0.45,"Yxs_r":"0.38–0.52"},
        "Terrific broth (TB)": {"mu_min":0.8,"mu_max":1.5,"td_min":28,"td_max":52, "Yxs":0.45,"Yxs_r":"0.38–0.52"},
    },
    "S. cerevisiae":{
        "M9 minimal glucose":  {"mu_min":0.25,"mu_max":0.45,"td_min":92, "td_max":166,"Yxs":0.50,"Yxs_r":"0.40–0.55"},
        "LB rich":             {"mu_min":0.20,"mu_max":0.38,"td_min":109,"td_max":208,"Yxs":0.50,"Yxs_r":"0.40–0.55"},
        "Defined industrial":  {"mu_min":0.22,"mu_max":0.40,"td_min":104,"td_max":189,"Yxs":0.50,"Yxs_r":"0.40–0.55"},
        "Terrific broth (TB)": {"mu_min":0.20,"mu_max":0.38,"td_min":109,"td_max":208,"Yxs":0.50,"Yxs_r":"0.40–0.55"},
    },
    "B. subtilis":{
        "M9 minimal glucose":  {"mu_min":0.5,"mu_max":0.9,"td_min":46,"td_max":83, "Yxs":0.42,"Yxs_r":"0.35–0.50"},
        "LB rich":             {"mu_min":0.7,"mu_max":1.2,"td_min":35,"td_max":60, "Yxs":0.42,"Yxs_r":"0.35–0.50"},
        "Defined industrial":  {"mu_min":0.4,"mu_max":0.8,"td_min":52,"td_max":104,"Yxs":0.42,"Yxs_r":"0.35–0.50"},
        "Terrific broth (TB)": {"mu_min":0.6,"mu_max":1.1,"td_min":38,"td_max":69, "Yxs":0.42,"Yxs_r":"0.35–0.50"},
    },
    "K. phaffii":{
        "M9 minimal glucose":  {"mu_min":0.18,"mu_max":0.35,"td_min":119,"td_max":231,"Yxs":0.48,"Yxs_r":"0.38–0.55"},
        "LB rich":             {"mu_min":0.15,"mu_max":0.30,"td_min":139,"td_max":277,"Yxs":0.48,"Yxs_r":"0.38–0.55"},
        "Defined industrial":  {"mu_min":0.16,"mu_max":0.32,"td_min":130,"td_max":260,"Yxs":0.48,"Yxs_r":"0.38–0.55"},
        "Terrific broth (TB)": {"mu_min":0.15,"mu_max":0.30,"td_min":139,"td_max":277,"Yxs":0.48,"Yxs_r":"0.38–0.55"},
    },
    "C. glutamicum":{
        "M9 minimal glucose":  {"mu_min":0.30,"mu_max":0.55,"td_min":75,"td_max":138,"Yxs":0.40,"Yxs_r":"0.33–0.48"},
        "LB rich":             {"mu_min":0.38,"mu_max":0.65,"td_min":64,"td_max":109,"Yxs":0.40,"Yxs_r":"0.33–0.48"},
        "Defined industrial":  {"mu_min":0.28,"mu_max":0.52,"td_min":80,"td_max":148,"Yxs":0.40,"Yxs_r":"0.33–0.48"},
        "Terrific broth (TB)": {"mu_min":0.35,"mu_max":0.60,"td_min":69,"td_max":118,"Yxs":0.40,"Yxs_r":"0.33–0.48"},
    },
    "C. acetobutylicum":{
        "M9 minimal glucose":  {"mu_min":0.4,"mu_max":0.8,"td_min":52,"td_max":104,"Yxs":0.30,"Yxs_r":"0.25–0.40"},
        "LB rich":             {"mu_min":0.5,"mu_max":1.0,"td_min":42,"td_max":83, "Yxs":0.30,"Yxs_r":"0.25–0.40"},
        "Defined industrial":  {"mu_min":0.35,"mu_max":0.7,"td_min":59,"td_max":118,"Yxs":0.30,"Yxs_r":"0.25–0.40"},
        "Terrific broth (TB)": {"mu_min":0.45,"mu_max":0.9,"td_min":46,"td_max":92, "Yxs":0.30,"Yxs_r":"0.25–0.40"},
    },
    "A. terreus":{
        "M9 minimal glucose":  {"mu_min":0.05,"mu_max":0.15,"td_min":277,"td_max":831, "Yxs":0.38,"Yxs_r":"0.30–0.45"},
        "LB rich":             {"mu_min":0.06,"mu_max":0.18,"td_min":231,"td_max":693, "Yxs":0.38,"Yxs_r":"0.30–0.45"},
        "Defined industrial":  {"mu_min":0.04,"mu_max":0.12,"td_min":346,"td_max":1040,"Yxs":0.38,"Yxs_r":"0.30–0.45"},
        "Terrific broth (TB)": {"mu_min":0.06,"mu_max":0.18,"td_min":231,"td_max":693, "Yxs":0.38,"Yxs_r":"0.30–0.45"},
    },
    "Streptomyces sp.":{
        "M9 minimal glucose":  {"mu_min":0.03,"mu_max":0.10,"td_min":416,"td_max":1386,"Yxs":0.35,"Yxs_r":"0.28–0.42"},
        "LB rich":             {"mu_min":0.04,"mu_max":0.12,"td_min":346,"td_max":1040,"Yxs":0.35,"Yxs_r":"0.28–0.42"},
        "Defined industrial":  {"mu_min":0.03,"mu_max":0.09,"td_min":462,"td_max":1386,"Yxs":0.35,"Yxs_r":"0.28–0.42"},
        "Terrific broth (TB)": {"mu_min":0.04,"mu_max":0.12,"td_min":346,"td_max":1040,"Yxs":0.35,"Yxs_r":"0.28–0.42"},
    },
}

def get_lit(organism, medium):
    org = LBIO.get(organism, LBIO["E. coli"])
    return org.get(medium, org.get("M9 minimal glucose",
           {"mu_min":0.3,"mu_max":1.0,"td_min":40,"td_max":150,"Yxs":0.40,"Yxs_r":"0.35–0.50"}))

# ── Product database (no company names) ───────────────────────────────────────
PRODUCT_DB = {
    "Mevalonic acid (MVA)":{"formula":"C6H12O4","C":6,"H":12,"O":4,"N":0,"MW":148.16,"gamma":3.00,
        "tmin":5,"tmax":50,"sty_min":0.05,"sty_max":1.5,"lp_al":"0.05–0.30","lp_be":"0.001–0.015",
        "cat":"terpenoid","notes":"Platform for isoprenoids. ~35 g/L pilot scale.","ref":"Martin et al 2003"},
    "Isoprene":{"formula":"C5H8","C":5,"H":8,"O":0,"N":0,"MW":68.12,"gamma":3.60,
        "tmin":0.5,"tmax":5,"sty_min":0.01,"sty_max":0.15,"lp_al":"0.1–0.5","lp_be":"0.0001–0.001",
        "cat":"terpenoid","notes":"Volatile C5. Capture from off-gas.","ref":"Cao et al 2016"},
    "Farnesene":{"formula":"C15H24","C":15,"H":24,"O":0,"N":0,"MW":204.35,"gamma":3.60,
        "tmin":0.5,"tmax":10,"sty_min":0.01,"sty_max":0.30,"lp_al":"0.05–0.2","lp_be":"0.001–0.008",
        "cat":"terpenoid","notes":"FPP-derived C15. Cosmetics, SAF, polymers.","ref":"Meadows et al 2016"},
    "Limonene":{"formula":"C10H16","C":10,"H":16,"O":0,"N":0,"MW":136.23,"gamma":3.60,
        "tmin":0.001,"tmax":0.5,"sty_min":0.0001,"sty_max":0.02,"lp_al":"0.01–0.1","lp_be":"0.0001–0.001",
        "cat":"terpenoid","notes":"Volatile. Toxic >0.1 g/L.","ref":"Cao et al 2016"},
    "Lycopene":{"formula":"C40H56","C":40,"H":56,"O":0,"N":0,"MW":536.87,"gamma":3.73,
        "tmin":0.001,"tmax":0.5,"sty_min":0.0001,"sty_max":0.02,"lp_al":"0.001–0.05","lp_be":"0.0001–0.005",
        "cat":"terpenoid","notes":"C40 carotenoid. Intracellular.","ref":"Ye et al 2020"},
    "3-Hydroxypropionic acid":{"formula":"C3H6O3","C":3,"H":6,"O":3,"N":0,"MW":90.08,"gamma":4.00,
        "tmin":10,"tmax":80,"sty_min":0.3,"sty_max":3.0,"lp_al":"0.05–0.25","lp_be":"0.005–0.02",
        "cat":"polymer_precursor","notes":"DOE top-12. Fed-batch up to 53.7 g/L.","ref":"Kumar et al 2013"},
    "Bio-acrylic acid":{"formula":"C3H4O2","C":3,"H":4,"O":2,"N":0,"MW":72.06,"gamma":3.33,
        "tmin":5,"tmax":50,"sty_min":0.1,"sty_max":2.0,"lp_al":"0.05–0.2","lp_be":"0.002–0.01",
        "cat":"polymer_precursor","notes":"SAP precursor.","ref":"Kumar et al 2013"},
    "PHA/PHB":{"formula":"C4H6O2","C":4,"H":6,"O":2,"N":0,"MW":86.09,"gamma":4.50,
        "tmin":5,"tmax":80,"sty_min":0.1,"sty_max":2.0,"lp_al":"0.1–0.4","lp_be":"0.005–0.03",
        "cat":"polymer_precursor","notes":"N-limited accumulation. Intracellular.","ref":"Reddy et al 2003"},
    "1,4-Butanediol (BDO)":{"formula":"C4H10O2","C":4,"H":10,"O":2,"N":0,"MW":90.12,"gamma":5.50,
        "tmin":10,"tmax":100,"sty_min":0.5,"sty_max":4.0,"lp_al":"0.1–0.4","lp_be":"0.005–0.02",
        "cat":"polymer_precursor","notes":"Polyesters, polyurethanes.","ref":"Yim et al 2011"},
    "Succinic acid":{"formula":"C4H6O4","C":4,"H":6,"O":4,"N":0,"MW":118.09,"gamma":3.50,
        "tmin":5,"tmax":100,"sty_min":0.1,"sty_max":3.5,"lp_al":"0.05–0.3","lp_be":"0.002–0.02",
        "cat":"organic_acid","notes":"Anaerobic preferred.","ref":"Jantama et al 2008"},
    "L-Lactic acid":{"formula":"C3H6O3","C":3,"H":6,"O":3,"N":0,"MW":90.08,"gamma":4.00,
        "tmin":10,"tmax":150,"sty_min":0.5,"sty_max":8.0,"lp_al":"0.1–0.5","lp_be":"0.005–0.05",
        "cat":"organic_acid","notes":"PLA precursor. Up to 150 g/L.","ref":"Hofvendahl 2000"},
    "Itaconic acid":{"formula":"C5H6O4","C":5,"H":6,"O":4,"N":0,"MW":130.10,"gamma":3.20,
        "tmin":40,"tmax":100,"sty_min":0.5,"sty_max":2.0,"lp_al":"0.1–0.3","lp_be":"0.01–0.05",
        "cat":"organic_acid","notes":"A. terreus natural producer up to 80+ g/L.","ref":"Steiger et al 2013"},
    "Glucaric acid":{"formula":"C6H10O8","C":6,"H":10,"O":8,"N":0,"MW":210.14,"gamma":2.67,
        "tmin":1,"tmax":30,"sty_min":0.02,"sty_max":0.5,"lp_al":"0.05–0.2","lp_be":"0.001–0.01",
        "cat":"organic_acid","notes":"DOE platform chemical.","ref":"Moon et al 2009"},
    "Ethanol":{"formula":"C2H6O","C":2,"H":6,"O":1,"N":0,"MW":46.07,"gamma":6.00,
        "tmin":20,"tmax":120,"sty_min":0.5,"sty_max":8.0,"lp_al":"0.2–0.6","lp_be":"0.001–0.01",
        "cat":"alcohol","notes":"Most established bioprocess.","ref":"Standard"},
    "n-Butanol":{"formula":"C4H10O","C":4,"H":10,"O":1,"N":0,"MW":74.12,"gamma":6.00,
        "tmin":5,"tmax":25,"sty_min":0.05,"sty_max":0.8,"lp_al":"0.05–0.2","lp_be":"0.005–0.03",
        "cat":"alcohol","notes":"Strict anaerobe. Toxic ~2% v/v.","ref":"Dürre 2007"},
    "Isopropanol":{"formula":"C3H8O","C":3,"H":8,"O":1,"N":0,"MW":60.10,"gamma":6.00,
        "tmin":5,"tmax":50,"sty_min":0.2,"sty_max":2.0,"lp_al":"0.1–0.4","lp_be":"0.005–0.02",
        "cat":"alcohol","notes":"~50 g/L in engineered E. coli.","ref":"Hanai et al 2007"},
    "Collagen (recombinant)":{"formula":"(Gly-X-Y)n","C":1,"H":1.55,"O":0.31,"N":0.25,"MW":15000,"gamma":4.00,
        "tmin":0.1,"tmax":5,"sty_min":0.001,"sty_max":0.05,"lp_al":"0.05–0.2","lp_be":"0.002–0.01",
        "cat":"protein","notes":"Animal-free recombinant collagen.","ref":"Brodsky 2005"},
    "Elastin (recombinant)":{"formula":"(VPGXG)n","C":1,"H":1.6,"O":0.3,"N":0.26,"MW":8000,"gamma":4.10,
        "tmin":0.05,"tmax":3,"sty_min":0.0005,"sty_max":0.05,"lp_al":"0.05–0.2","lp_be":"0.001–0.008",
        "cat":"protein","notes":"ELP-based elastin.","ref":"Urry et al 1992"},
    "Spider silk protein":{"formula":"(GPGGX)n","C":1,"H":1.55,"O":0.3,"N":0.27,"MW":25000,"gamma":4.05,
        "tmin":0.05,"tmax":5,"sty_min":0.001,"sty_max":0.1,"lp_al":"0.05–0.2","lp_be":"0.001–0.01",
        "cat":"protein","notes":"Repetitive sequence.","ref":"Teule et al 2009"},
    "Hyaluronic acid":{"formula":"(C14H21NO11)n","C":1,"H":1.79,"O":0.85,"N":0.08,"MW":2000000,"gamma":3.50,
        "tmin":5,"tmax":20,"sty_min":0.05,"sty_max":0.5,"lp_al":"0.05–0.2","lp_be":"0.005–0.02",
        "cat":"protein","notes":"Non-Newtonian broth at scale.","ref":"Liu et al 2011"},
    "Cannabigerol (CBG)":{"formula":"C21H32O2","C":21,"H":32,"O":2,"N":0,"MW":316.48,"gamma":5.43,
        "tmin":0.1,"tmax":5,"sty_min":0.001,"sty_max":0.05,"lp_al":"0.02–0.1","lp_be":"0.001–0.005",
        "cat":"cannabinoid","notes":"THC-free biosynthesis via yeast olivetol pathway.","ref":"Luo et al 2019"},
    "Cannabidiol (CBD)":{"formula":"C21H30O2","C":21,"H":30,"O":2,"N":0,"MW":314.46,"gamma":5.43,
        "tmin":0.05,"tmax":3,"sty_min":0.0005,"sty_max":0.03,"lp_al":"0.02–0.1","lp_be":"0.001–0.005",
        "cat":"cannabinoid","notes":"Pharma grade THC-free.","ref":"Luo et al 2019"},
    "L-Lysine":{"formula":"C6H14N2O2","C":6,"H":14,"O":2,"N":2,"MW":146.19,"gamma":4.67,
        "tmin":50,"tmax":150,"sty_min":1.0,"sty_max":5.0,"lp_al":"0.05–0.2","lp_be":"0.01–0.05",
        "cat":"amino_acid","notes":"Aspartate pathway. Largest AA market.","ref":"Leuchtenberger 2005"},
    "L-Glutamate":{"formula":"C5H9NO4","C":5,"H":9,"O":4,"N":1,"MW":147.13,"gamma":3.60,
        "tmin":50,"tmax":100,"sty_min":0.5,"sty_max":3.0,"lp_al":"0.05–0.2","lp_be":"0.01–0.04",
        "cat":"amino_acid","notes":"Biotin-limited trigger.","ref":"Kinoshita 1957"},
    "L-Threonine":{"formula":"C4H9NO3","C":4,"H":9,"O":3,"N":1,"MW":119.12,"gamma":4.00,
        "tmin":30,"tmax":100,"sty_min":0.5,"sty_max":2.5,"lp_al":"0.05–0.2","lp_be":"0.005–0.03",
        "cat":"amino_acid","notes":"ThrA desensitisation key target.","ref":"Lee et al 2003"},
    "Riboflavin":{"formula":"C17H20N4O6","C":17,"H":20,"O":6,"N":4,"MW":376.36,"gamma":3.53,
        "tmin":5,"tmax":30,"sty_min":0.1,"sty_max":1.0,"lp_al":"0.02–0.1","lp_be":"0.005–0.02",
        "cat":"other","notes":"Ashbya gossypii up to 15 g/L.","ref":"Stahmann 2000"},
    "Shikimic acid":{"formula":"C7H10O5","C":7,"H":10,"O":5,"N":0,"MW":174.15,"gamma":3.43,
        "tmin":1,"tmax":30,"sty_min":0.05,"sty_max":0.8,"lp_al":"0.05–0.2","lp_be":"0.002–0.01",
        "cat":"other","notes":"Tamiflu precursor. ΔaroL + PTS-neg.","ref":"Kramer 2003"},
    "Custom":{"formula":"","C":1,"H":0,"O":0,"N":0,"MW":100,"gamma":4.00,
        "tmin":0,"tmax":100,"sty_min":0,"sty_max":10,"lp_al":"—","lp_be":"—",
        "cat":"other","notes":"User-defined.","ref":"—"},
}


# ── Growth kinetics ────────────────────────────────────────────────────────────

def _detect_growth_changepoints(t, ln_od, min_seg=None, penalty_factor=None,
                                 _depth=0, _max_depth=3):
    """Detect changepoints in ln(OD) where the growth rate shifts.

    Uses penalised piecewise-linear regression: tries every candidate split
    and keeps those that reduce total RSS by more than a noise-based penalty.
    Returns a sorted list of changepoint indices (excluding endpoints).

    Guards against over-segmentation via:
    - Adaptive min_seg based on data density (at least 8 points or 10 %)
    - Adaptive penalty: tighter for short/noisy data, relaxed for long runs
    - Minimum slope ratio: slopes must differ by >= 40 % relative
    - Max recursion depth of 3 (max 4 segments)
    """
    n = len(t)
    if min_seg is None:
        min_seg = max(8, n // 10)
    if penalty_factor is None:
        # Longer datasets are more likely to contain true phase shifts,
        # so use a lower penalty. Short/noisy data gets a higher penalty
        # to prevent noise-driven splits.
        penalty_factor = 0.20 if n >= 40 else 0.40
    if n < 2 * min_seg or _depth >= _max_depth:
        return []

    # Single-segment baseline RSS
    sl0, ic0, _, _, _ = linregress(t, ln_od)
    rss0 = float(np.sum((ln_od - (sl0 * t + ic0)) ** 2))
    noise_var = rss0 / max(n - 2, 1)
    penalty = penalty_factor * n * noise_var

    best_gain, best_cp = -np.inf, None

    for cp in range(min_seg, n - min_seg):
        sl_l, ic_l, _, _, _ = linregress(t[:cp], ln_od[:cp])
        rss_l = float(np.sum((ln_od[:cp] - (sl_l * t[:cp] + ic_l)) ** 2))
        sl_r, ic_r, _, _, _ = linregress(t[cp:], ln_od[cp:])
        rss_r = float(np.sum((ln_od[cp:] - (sl_r * t[cp:] + ic_r)) ** 2))

        gain = rss0 - (rss_l + rss_r) - penalty
        # Slopes must differ by >= 40 % relative to the steeper one
        max_slope = max(abs(sl_l), abs(sl_r), 1e-9)
        slope_ratio = abs(sl_l - sl_r) / max_slope
        if gain > best_gain and slope_ratio > 0.40:
            best_gain = gain
            best_cp = cp

    if best_cp is not None and best_gain > 0:
        left_cps  = _detect_growth_changepoints(
            t[:best_cp], ln_od[:best_cp], min_seg, penalty_factor,
            _depth + 1, _max_depth)
        right_cps = _detect_growth_changepoints(
            t[best_cp:], ln_od[best_cp:], min_seg, penalty_factor,
            _depth + 1, _max_depth)
        right_cps = [cp + best_cp for cp in right_cps]
        return left_cps + [best_cp] + right_cps

    return []


def _fit_phase(t, od, ln_od, phase_start, phase_end, min_pts=5):
    """Fit a single growth phase using sliding-window regression.

    Returns dict with mu, r2, etc. for this phase, or None if no fit.
    """
    n_ph = phase_end - phase_start
    t_ph = t[phase_start:phase_end]
    od_ph = od[phase_start:phase_end]
    ln_ph = ln_od[phase_start:phase_end]
    max_od_ph = float(np.max(od_ph))

    if n_ph < min_pts:
        return None

    span_ph = float(t_ph[-1] - t_ph[0])
    min_span = max(2.0, span_ph * 0.15)
    best_score, best = -np.inf, None

    for i in range(n_ph - min_pts + 1):
        if i > 0 and od_ph[i] < od_ph[0] * 0.40:
            continue
        for j in range(i + min_pts, n_ph + 1):
            span = t_ph[j-1] - t_ph[i]
            if span < min_span:
                continue
            if od_ph[i:j].max() > max_od_ph * 0.92:
                continue
            sl, ic, r, _, _ = linregress(t_ph[i:j], ln_ph[i:j])
            if sl <= 0:
                continue
            r2 = r ** 2
            # Noise-penalised scoring: R²² down-weights windows with
            # marginal fit; rstd penalty discourages absorbing noisy
            # low-OD tails that bias the slope downward.
            resids = ln_ph[i:j] - (sl * t_ph[i:j] + ic)
            rstd = float(np.std(resids))
            score = sl * r2 ** 2 * np.sqrt(span) / (1.0 + 4.0 * rstd)
            if score > best_score:
                best_score = score
                best = (i, j, sl, ic, r2)

    if best is None:
        return None

    i0, j, sl, ic, r2 = best

    # Post-selection trim
    _resids = ln_ph[i0:j] - (sl * t_ph[i0:j] + ic)
    _rstd = max(float(np.std(_resids)), 0.10)
    if _resids[0] < -1.5 * _rstd and (j - i0 - 1) >= min_pts:
        sl2, ic2, r2_2, _, _ = linregress(t_ph[i0+1:j], ln_ph[i0+1:j])
        if sl2 > 0 and r2_2 >= r2 * 0.97:
            i0, sl, ic, r2 = i0 + 1, float(sl2), float(ic2), float(r2_2)

    _, _, _, _, mu_se = linregress(t_ph[i0:j], ln_ph[i0:j])
    n_exp = j - i0

    return {
        "mu":       float(sl),
        "mu_se":    float(mu_se),
        "r2":       float(r2),
        "n_exp":    int(n_exp),
        "td_min":   float(np.log(2) / sl * 60),
        "t_start":  float(t_ph[0]),
        "t_end":    float(t_ph[-1]),
        "exp_t":    t_ph[i0:j],
        "bgr_sl":   float(sl),
        "bgr_ic":   float(ic),
        "i0_global": phase_start + i0,
        "j_global":  phase_start + j,
    }


def compute_growth_kinetics(time_h, od, dcw_factor=0.4):
    t  = np.asarray(time_h, float)
    od = np.asarray(od, float)
    dcw    = od * dcw_factor
    max_od = float(np.max(od))
    res    = {"dcw": dcw, "max_od": max_od, "max_dcw": float(np.max(dcw))}

    n          = len(t)
    total_span = float(t[-1] - t[0])
    ln_od      = np.log(np.clip(od, 1e-9, None))
    MIN_PTS    = 5

    # ── Diauxic / multi-phase detection ──────────────────────────────────────
    # Detect changepoints where growth rate shifts significantly, then fit
    # each segment independently.  The primary μ is the fastest phase.
    changepoints = _detect_growth_changepoints(t, ln_od)
    boundaries = [0] + changepoints + [n]

    phases = []
    for seg_idx in range(len(boundaries) - 1):
        seg_start = boundaries[seg_idx]
        seg_end   = boundaries[seg_idx + 1]
        phase = _fit_phase(t, od, ln_od, seg_start, seg_end, MIN_PTS)
        if phase is not None:
            phase["phase_idx"] = seg_idx
            phases.append(phase)

    # If segmented fitting yielded no phases, fall back to full-dataset fit
    if not phases:
        full_phase = _fit_phase(t, od, ln_od, 0, n, MIN_PTS)
        if full_phase is not None:
            full_phase["phase_idx"] = 0
            phases.append(full_phase)
        changepoints = []

    # Always also fit the full dataset: changepoint boundaries can clip
    # valid exponential data, so the unconstrained fit is a useful
    # competitor.  It's added as a hidden candidate — not a reported phase.
    full_fit = _fit_phase(t, od, ln_od, 0, n, MIN_PTS) if changepoints else None

    res["phases"] = phases
    res["changepoints"] = [float(t[cp]) for cp in changepoints]
    is_diauxic = len(phases) >= 2
    res["is_diauxic"] = is_diauxic

    # ── Select primary phase (fastest μ) for backward-compatible keys ────────
    if phases:
        primary = max(phases, key=lambda p: p["mu"])
        # If the full-dataset fit found a higher-R² result at similar μ,
        # prefer it (changepoint boundary may have clipped good data).
        if full_fit is not None and full_fit["r2"] > primary["r2"] + 0.005:
            # Only override if the mu values are reasonably close (within 30%)
            mu_ratio = abs(full_fit["mu"] - primary["mu"]) / max(primary["mu"], 1e-9)
            if mu_ratio < 0.30:
                primary = full_fit
        i_mu = primary["i0_global"]
        j    = primary["j_global"]
        sl   = primary["mu"]
        ic   = primary["bgr_ic"]
        r2   = primary["r2"]
        i0   = i_mu  # for lag estimation

        # Refit to get standard error
        _, _, _, _, mu_se = linregress(t[i_mu:j], ln_od[i_mu:j])
        n_exp = j - i_mu

        res["mu"]     = float(sl)
        res["mu_se"]  = float(mu_se)
        res["n_exp"]  = int(n_exp)
        res["td_min"] = float(np.log(2) / sl * 60)
        res["r2"]     = float(r2)
        res["exp_t"]  = t[i_mu:j]
        res["bgr_sl"] = float(sl)
        res["bgr_ic"] = float(ic)

        # ── Quality score (0–100) ────────────────────────────────────────────
        q_r2    = r2 * 40.0
        q_pts   = min(n_exp / 15.0, 1.0) * 30.0
        _resids_final = ln_od[i_mu:j] - (sl * t[i_mu:j] + ic)
        _rstd_final   = float(np.std(_resids_final))
        q_noise = max(0.0, 1.0 - _rstd_final / 0.30) * 20.0
        q_regime = 10.0 if 0.05 <= sl <= 2.0 else 5.0
        res["quality_score"] = int(round(q_r2 + q_pts + q_noise + q_regime))

        # ── Lag: piecewise regression (flat + exponential) breakpoint ────────
        def _detect_lag_piecewise(t_arr, ln_arr, mu_val, min_exp=5, min_lag=2):
            nn = len(t_arr)
            if nn < min_lag + min_exp:
                return None
            best_rss = np.inf
            best_tb  = None
            for bp in range(min_lag, nn - min_exp + 1):
                seg1 = ln_arr[:bp]
                mean1 = np.mean(seg1)
                rss1  = float(np.sum((seg1 - mean1) ** 2))
                seg2_t  = t_arr[bp:]
                seg2_ln = ln_arr[bp:]
                sl2, ic2, _, _, _ = linregress(seg2_t, seg2_ln)
                if sl2 < mu_val * 0.25:
                    continue
                rss2 = float(np.sum((seg2_ln - (sl2 * seg2_t + ic2)) ** 2))
                total_rss = rss1 + rss2
                if total_rss < best_rss:
                    best_rss = total_rss
                    best_tb  = float(t_arr[bp])
            return best_tb

        # For lag, use data up to the end of the primary phase's segment
        seg_end_idx = j
        lag_bp = _detect_lag_piecewise(t[:seg_end_idx], ln_od[:seg_end_idx], sl)

        if lag_bp is not None and lag_bp > t[0]:
            bp_idx = int(np.searchsorted(t[:seg_end_idx], lag_bp))

            flat_od = od[:bp_idx]
            flat_cv = float(np.std(flat_od) / max(np.mean(flat_od), 1e-9))
            is_flat = flat_cv < 0.30 and bp_idx >= 2

            if is_flat:
                res["lag_h"] = float(lag_bp)
            else:
                od_inoc = float(od[0])
                snr_threshold = max(od_inoc * 3.0, 0.3)
                snr_mask = (od[:seg_end_idx] >= snr_threshold)
                snr_idx  = np.where(snr_mask)[0]
                if len(snr_idx) >= MIN_PTS:
                    sl_clean, ic_clean, _, _, _ = linregress(
                        t[snr_idx], ln_od[snr_idx])
                    if sl_clean > 0:
                        od_inoc = max(od_inoc, 1e-9)
                        lag_t = (np.log(od_inoc) - ic_clean) / sl_clean
                        res["lag_h"] = float(max(lag_t, 0.0))
                    else:
                        res["lag_h"] = float(lag_bp)
                else:
                    res["lag_h"] = float(lag_bp)
        elif i0 > 0:
            od_ref = float(np.median(od[:i0]))
            od_ref = max(od_ref, 1e-9)
            lag_t  = (np.log(od_ref) - ic) / sl
            if lag_t > float(t[i0]) and od[i0] >= od[0] * 0.40:
                lag_t = float(t[i0])
            res["lag_h"] = float(max(lag_t, 0.0))
        else:
            od_ref = float(od[0])
            od_ref = max(od_ref, 1e-9)
            lag_t  = (np.log(od_ref) - ic) / sl
            if lag_t < 0:
                lag_t = 0.0
            res["lag_h"] = float(max(lag_t, 0.0))
    else:
        res["mu"] = res["td_min"] = res["r2"] = None
        res["exp_t"] = np.array([])
        res["bgr_sl"] = res["bgr_ic"] = None
        res["lag_h"]  = float(t[0])
        res["quality_score"] = 0
        res["mu_se"] = None
        res["n_exp"] = 0

    return res


def compute_productivity(time_h, product, dcw):
    t   = np.asarray(time_h, float)
    prd = np.asarray(product, float)
    dcw = np.asarray(dcw, float)
    n   = len(t)
    res = {}
    if n < 3: return res
    qp = np.zeros(n)
    for i in range(n):
        lo, hi = max(0,i-1), min(n-1,i+1)
        if hi > lo:
            qp[i] = max((prd[hi]-prd[lo])/(t[hi]-t[lo]), 0)
    res["qp"]      = qp
    res["qp_max"]  = float(np.max(qp))
    res["titer"]   = float(prd[-1])
    res["sty"]     = float(prd[-1]/t[-1]) if t[-1]>0 else 0.0
    sp = np.where(dcw>0.01, qp/dcw, 0.0)
    res["sp"] = sp
    mu_loc = np.zeros(n)
    for i in range(n):
        lo, hi = max(0,i-1), min(n-1,i+1)
        if hi > lo and dcw[lo]>0 and dcw[hi]>0:
            mu_loc[i] = max(np.log(dcw[hi]/dcw[lo])/(t[hi]-t[lo]), 0)
    v = (mu_loc>0)&(sp>0)
    if np.sum(v)>=4:
        sl,ic,r,_,_ = linregress(mu_loc[v], sp[v])
        res["lp_alpha"]=float(max(sl,0)); res["lp_beta"]=float(max(ic,0)); res["lp_r2"]=float(r**2)
    else:
        res["lp_alpha"]=res["lp_beta"]=res["lp_r2"]=None
    return res


def check_carbon_balance(df, od_col, substrate_col, product_col,
                         conv_factor=0.40,
                         sub_C=6, sub_MW=180.16,
                         prod_C=2, prod_MW=46.07,
                         C_biomass=0.48):
    """Quick carbon recovery check (without off-gas data).

    All terms in gC/L for consistent units.

    Parameters
    ----------
    df : DataFrame with time-series data.
    od_col, substrate_col, product_col : column names.
    conv_factor : OD-to-DCW conversion (g/L per OD unit), default 0.40.
        For VCD data (1e6 cells/mL), use ~0.15-0.20 instead of 0.40.
    sub_C, sub_MW : carbon atoms and molecular weight of the substrate.
    prod_C, prod_MW : carbon atoms and molecular weight of the product.
    C_biomass : carbon mass fraction of biomass (gC / g DCW), default 0.48.

    Returns
    -------
    dict with recovery (%), C_substrate, C_biomass, C_products (all gC/L).
    """
    C_per_g_sub  = sub_C  * 12.0 / sub_MW   # gC per g substrate
    C_per_g_prod = prod_C * 12.0 / prod_MW   # gC per g product

    delta_od   = float(df[od_col].iloc[-1] - df[od_col].iloc[0])
    biomass    = delta_od * conv_factor                          # g DCW / L
    delta_sub  = float(df[substrate_col].iloc[0] - df[substrate_col].iloc[-1])
    delta_prod = float(df[product_col].iloc[-1] - df[product_col].iloc[0])

    C_sub  = delta_sub  * C_per_g_sub       # gC/L in
    C_bio  = biomass    * C_biomass          # gC/L out (biomass)
    C_prod = delta_prod * C_per_g_prod       # gC/L out (product)

    recovery = (C_bio + C_prod) / max(C_sub, 1e-9) * 100

    return {
        "recovery": recovery,
        "C_substrate": C_sub,
        "C_biomass": C_bio,
        "C_products": C_prod,
        "C_unaccounted_pct": 100.0 - recovery,  # likely CO2
    }


def compute_mass_balance(substrates, products, biomass, gas, feed=None, mode="Batch"):
    """
    Full C/H/O/N + degree-of-reduction balance.
    mode: 'Batch' | 'Fed-batch' | 'Continuous'
    Continuous (chemostat): feed dict must contain D (dilution rate h⁻¹), V (L), tf (h).
      Substrate consumed = D * V * (sin - sout) * tf
    """
    res = {}
    C_in = dS = 0.0
    for s in substrates:
        if mode == "Continuous" and feed:
            # Chemostat: net substrate consumed per litre = D*(sin-sout)*tf
            D  = feed.get("D", 0.0)
            tf = gas.get("tf", 24.0)
            ds = D * (s.get("feed_conc", s["s0"]) - s["sf"]) * tf
        elif mode == "Fed-batch" and feed:
            ds = (s["s0"] - s["sf"]) + s.get("feed_conc", 0) * feed.get("vf", 0)
        else:
            ds = s["s0"] - s["sf"]
        C_in += ds * s["C"] * 12 / max(s["MW"], 1)
        dS   += ds
    # For continuous, also note steady-state dilution rate
    if mode == "Continuous" and feed:
        res["D"]  = feed.get("D", 0.0)
        res["mode_note"] = "Continuous (chemostat) — balances are per litre per process time"
    res["C_in"] = C_in; res["dS_total"] = dS
    dx = biomass["dx"]
    C_bio = dx * biomass["C"] * 12 / max(biomass["MW"],1)
    res["C_biomass"] = C_bio
    C_prod = 0.0; pd_list = []
    for p in products:
        cp = p["conc"] * p["C"] * 12 / max(p["MW"],1)
        C_prod += cp
        pd_list.append({"name":p["name"],"C_out":cp,"conc":p["conc"]})
    res["C_products"]=C_prod; res["prod_details"]=pd_list
    our=gas.get("our",0.); cer=gas.get("cer",0.); tf=gas.get("tf",24.)
    co2g = cer*tf*44/1000
    C_co2 = co2g*12/44
    res["C_CO2"]=C_co2; res["co2_g"]=co2g; res["RQ"]=cer/max(our,1e-3)
    C_out = C_bio+C_prod+C_co2
    res["C_out"]=C_out; res["C_unacc"]=C_in-C_out
    res["closure"]=C_out/max(C_in,1e-9)*100
    if substrates:
        s=substrates[0]; ds=s["s0"]-s["sf"]; mw=max(s["MW"],1); bmw=max(biomass["MW"],1)
        inC=ds/mw*s["C"]*1000; inH=ds/mw*s["H"]*1000; inO=ds/mw*s["O"]*1000+our*tf*2
        oC=dx/bmw*biomass["C"]*1000; oH=dx/bmw*biomass["H"]*1000
        oO=dx/bmw*biomass["O"]*1000+cer*tf*2; oN=dx/bmw*biomass["N"]*1000
        for p in products:
            mwp=max(p["MW"],1)
            oC+=p["conc"]/mwp*p["C"]*1000; oH+=p["conc"]/mwp*p.get("H",0)*1000
            oO+=p["conc"]/mwp*p.get("O",0)*1000; oN+=p["conc"]/mwp*p.get("N",0)*1000
        oC+=cer*tf
        res["elem"]={"inC":inC,"outC":oC,"inH":inH,"outH":oH,"H2O":(inH-oH)/2,
                     "inO":inO,"outO":oO,"outN":oN}
    if substrates:
        s=substrates[0]; ds=s["s0"]-s["sf"]
        gi=ds/max(s["MW"],1)*s["C"]*s.get("gamma",4.0)
        gb=dx/max(biomass["MW"],1)*biomass.get("gamma",4.07)
        gp=sum(p["conc"]/max(p["MW"],1)*p["C"]*p.get("gamma",4.0) for p in products)
        go=our*tf/1000*4; gout=gb+gp+go
        res["dor"]={"gin":gi,"gbio":gb,"gprod":gp,"gO2":go,"gout":gout,"cl":gout/max(gi,1e-9)*100}
    if substrates and dS>0 and products:
        s=substrates[0]; p=products[0]
        Yxs=dx/dS; Yps=p["conc"]/dS
        YxsMax=(s.get("gamma",4.0)/biomass.get("gamma",4.07))*(max(biomass["MW"],1)/max(s["MW"],1))*s["C"]
        YpsMax=(s["C"]/max(p["C"],1))*(max(p["MW"],1)/max(s["MW"],1))
        res["yields"]={"Yxs":Yxs,"Yps":Yps,"Yxp":p["conc"]/max(dx,1e-9),
                       "YxsMax":YxsMax,"YpsMax":YpsMax,"Ceff":Yps/max(YpsMax,1e-9)*100}
    return res


def scaleup_vessel(V_L, HD, didt, n_imp, vvm, N0_rps, Di0, criterion, Np, OUR,
                    cstar, do_sp, V0_L=None):
    """Scale-up engineering model for stirred-tank bioreactors.

    Parameters
    ----------
    V_L      : target vessel volume (L)
    HD       : height-to-diameter ratio
    didt     : impeller-to-tank diameter ratio (Di/Dt)
    n_imp    : number of impellers
    vvm      : gas flow (vol gas / vol liquid / min)
    N0_rps   : lab-scale agitation (rev/s)
    Di0      : lab-scale impeller diameter (m)
    criterion: "Constant P/V", "Constant kLa", "Constant tip speed", "Constant Re"
    Np       : power number (dimensionless)
    OUR      : oxygen uptake rate (mmol O2/L/h)
    cstar    : O2 saturation (mmol/L)
    do_sp    : dissolved oxygen setpoint (%)
    V0_L     : lab-scale vessel volume (L), for geometric scaling outputs
    """
    # ── Geometric scaling ────────────────────────────────────────────────
    # Dt from cylindrical volume: V = pi/4 * Dt^2 * H = pi/4 * Dt^2 * HD*Dt
    Dt = (4 * V_L / 1000 / (np.pi * HD)) ** (1 / 3)   # tank diameter (m)
    Di = Dt * didt                                       # impeller diameter (m)
    H  = HD * Dt                                         # liquid height (m)

    # ── Agitation scaling ────────────────────────────────────────────────
    # N2 = N1 * (D1/D2)^exponent
    #   Constant P/V:         exponent = 2/3
    #   Constant kLa:         exponent = 2/3  (kLa correlates with P/V)
    #   Constant tip speed:   exponent = 1
    #   Constant Re:          exponent = 2
    #   Constant mixing time: solve from tm ~ D^2/N => N2 = N1*(D2/D1)^2
    if criterion == "Constant tip speed":
        N = N0_rps * (Di0 / Di)
    elif criterion == "Constant Re":
        N = N0_rps * (Di0 / Di) ** 2
    elif criterion == "Constant mixing time":
        # tm = 5.9 * (Di/Dt)^-2 / N / n^0.5
        # With same Di/Dt ratio, tm = const / N
        # => N must stay the same to preserve mixing time
        # Note: this is impractical at large scale (very high P/V)
        N = N0_rps
    else:  # "Constant P/V" or "Constant kLa"
        N = N0_rps * (Di0 / Di) ** (2 / 3)

    # ── Power ────────────────────────────────────────────────────────────
    # P = Np * rho * N^3 * Di^5  (per impeller)
    P  = Np * 1000 * N ** 3 * Di ** 5 * n_imp   # total power (W)
    PV = P / (V_L / 1000)                         # power per volume (W/m3)

    # ── Aeration ─────────────────────────────────────────────────────────
    # Q = vvm * V_L  (L/min), Vs = Q / cross-section area
    Q_Lmin = vvm * V_L                                        # gas flow (L/min)
    Vs = Q_Lmin / 1000 / (np.pi / 4 * Dt ** 2) / 60          # superficial velocity (m/s)

    # ── kLa (van't Riet correlation) ─────────────────────────────────────
    kLa = 0.026 * max(PV, 0.01) ** 0.4 * max(Vs, 1e-4) ** 0.5 * 3600  # h-1

    # ── O2 transfer ──────────────────────────────────────────────────────
    driving_force = cstar * (1 - do_sp / 100)
    kLa_req = OUR / driving_force if OUR > 0 and driving_force > 0 else 200
    OTR = kLa * driving_force

    # ── Mixing time (Nienow) ─────────────────────────────────────────────
    tm = 5.9 * (Di / Dt) ** (-2) / N / n_imp ** 0.5    # seconds

    # ── Tip speed ────────────────────────────────────────────────────────
    tip = np.pi * Di * N    # m/s

    # ── Heat transfer ────────────────────────────────────────────────────
    # U proportional to N^0.7 * Vs^0.3, A proportional to Dt^2
    # Q_heat = U * A * dT;  relative U and A vs lab
    U_rel = (N / max(N0_rps, 1e-9)) ** 0.7 * (max(Vs, 1e-6) / 1e-3) ** 0.3
    A_rel = Dt ** 2   # jacket area scales with Dt^2
    # Normalised to lab later (in return dict)

    # ── Performance factors ──────────────────────────────────────────────
    fo = min(OTR / max(OUR, 1e-3), 1.0)                           # O2 transfer
    fm = max(0.0, 1 - (tm - 30) * 0.005) if tm > 30 else 1.0     # mixing
    fc = max(0.75, 1 - np.log10(max(V_L, 1.001)) * 0.05)         # CO2 removal

    # ── Aeration: constant-Vs alternative ────────────────────────────────
    # If the lab superficial velocity were maintained, what vvm would be needed?
    if V0_L and V0_L > 0:
        Dt0 = (4 * V0_L / 1000 / (np.pi * HD)) ** (1 / 3)
        Vs0_ref = vvm * V0_L / 1000 / (np.pi / 4 * Dt0 ** 2) / 60
        # Q2 = Vs0 * A2 * 60  =>  vvm_const_vs = Q2*1000 / V_L
        vvm_const_vs = Vs0_ref * (np.pi / 4 * Dt ** 2) * 60 * 1000 / max(V_L, 1e-9)
    else:
        Vs0_ref = Vs
        vvm_const_vs = vvm

    # ── Biological scale-down factors ────────────────────────────────────
    # mu_scaled  = mu_lab  * (1 - k_mu  * log10(V2/V1))   k_mu  ~ 0.07
    # Y_scaled   = Y_lab   * (1 - k_Y   * log10(V2/V1))   k_Y   ~ 0.05
    # OD_scaled  = OD_lab  * (1 - k_OD  * log10(V2/V1))   k_OD  ~ 0.06
    scale_ratio = V_L / V0_L if V0_L and V0_L > 0 else None
    if scale_ratio is not None and scale_ratio > 1:
        log_scale = np.log10(scale_ratio)
        mu_factor  = max(0.5, 1.0 - 0.07 * log_scale)
        Yxs_factor = max(0.6, 1.0 - 0.05 * log_scale)
        od_factor  = max(0.5, 1.0 - 0.06 * log_scale)
    else:
        log_scale = 0.0
        mu_factor = Yxs_factor = od_factor = 1.0

    # ── Risk assessment ──────────────────────────────────────────────────
    risks = []
    if fo < 1.0:
        risks.append(("O2 limitation", "High",
                       "Increase vvm or agitation; consider O2 enrichment"))
    if tip > 5.0:
        risks.append(("High shear", "Medium",
                       "Tip speed >5 m/s may damage shear-sensitive cells"))
    elif tip > 3.5:
        risks.append(("Moderate shear", "Low",
                       "Monitor cell viability at tip speed >3.5 m/s"))
    if tm > 60:
        risks.append(("Poor mixing", "High",
                       "Mixing time >60s; add impellers or increase agitation"))
    elif tm > 30:
        risks.append(("Moderate mixing", "Medium",
                       "Mixing time >30s; consider additional impeller"))
    if V0_L and V_L / V0_L > 100:
        av_drop = 1.0 - (Dt ** 2 / (V_L / 1000)) / (Dt0 ** 2 / (V0_L / 1000)) if V0_L else 0
        if av_drop > 0.5:
            risks.append(("Heat removal", "Medium",
                           f"A/V ratio dropped {av_drop*100:.0f}%; consider internal coils"))
    if mu_factor < 0.80:
        risks.append(("Biological performance", "Medium",
                       f"Predicted {(1-mu_factor)*100:.0f}% mu loss; optimise feeding"))

    # ── Recommendations ──────────────────────────────────────────────────
    recs = []
    if fo < 1.0:
        recs.append("Implement DO-stat feeding to maintain oxygen transfer")
    if tip > 5.0:
        recs.append(f"Reduce agitation or use low-shear impeller (tip={tip:.1f} m/s)")
    if tm > 60:
        recs.append("Add impellers for adequate mixing homogeneity")
    if Dt > 2.0:
        recs.append("Large vessel (>2 m) — multiple impellers recommended")
    if not risks and not recs:
        recs.append("Scale-up appears feasible with standard design practices")

    return {
        "Dt": Dt, "Di": Di, "H": H,
        "N_rps": N, "N_rpm": N * 60,
        "P": P, "PV": PV,
        "Q_Lmin": Q_Lmin, "Vs": Vs,
        "vvm_const_vs": vvm_const_vs,
        "kLa": kLa, "kLa_req": kLa_req,
        "OTR": OTR,
        "tm": tm, "tip": tip,
        "U_rel": U_rel, "A_rel": A_rel,
        "fo": fo, "fm": fm, "fc": fc,
        "perf": fo * fm * fc,
        "scale_ratio": scale_ratio,
        "mu_factor": mu_factor, "Yxs_factor": Yxs_factor, "od_factor": od_factor,
        "risks": risks, "recommendations": recs,
    }


# ── Scale-Up Engine (class-based API) ─────────────────────────────────────────

from dataclasses import dataclass, asdict

@dataclass
class ScaleUpParameters:
    """Parameters for scale-up calculations."""
    volume_L: float
    mu_max_h: float
    yield_g_g: float
    max_od: float
    agitation_rpm: float
    aeration_vvm: float
    power_input_W_m3: float
    kLa_h: float
    vessel_diameter_m: float
    impeller_diameter_m: float
    aspect_ratio: float = 2.0
    broth_viscosity_cP: float = 1.0
    broth_density_kg_m3: float = 1000.0
    temperature_C: float = 37.0
    DO_setpoint_percent: float = 30.0
    Np: float = 5.0
    OUR: float = 8.5
    cstar: float = 0.21

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ScaleUpEngine:
    """Class-based wrapper around scaleup_vessel for multi-scale analysis."""

    CRITERIA_MAP = {
        "power_per_volume": "Constant P/V",
        "tip_speed": "Constant tip speed",
        "kLa": "Constant kLa",
        "mixing_time": "Constant mixing time",
        "reynolds": "Constant Re",
    }

    def calculate_scale_up(self, lab: ScaleUpParameters, target_volume: float,
                           criterion: str = "power_per_volume"):
        crit_label = self.CRITERIA_MAP.get(criterion, criterion)
        N0 = lab.agitation_rpm / 60.0
        didt = lab.impeller_diameter_m / lab.vessel_diameter_m

        r = scaleup_vessel(
            target_volume, lab.aspect_ratio, didt, 1, lab.aeration_vvm,
            N0, lab.impeller_diameter_m, crit_label, lab.Np, lab.OUR,
            lab.cstar, lab.DO_setpoint_percent, V0_L=lab.volume_L)

        mu_pred = lab.mu_max_h * r["mu_factor"]
        Yxs_pred = lab.yield_g_g * r["Yxs_factor"]
        od_pred = lab.max_od * r["od_factor"]
        efficiency = r["mu_factor"] * 100

        return {
            "scale_up_summary": {
                "lab_volume_L": lab.volume_L,
                "target_volume_L": target_volume,
                "scale_factor": r.get("scale_ratio", target_volume / lab.volume_L),
                "scaling_criterion": criterion,
            },
            "geometric_parameters": {
                "vessel_diameter_m": r["Dt"],
                "vessel_height_m": r["H"],
                "impeller_diameter_m": r["Di"],
                "aspect_ratio": lab.aspect_ratio,
            },
            "operational_parameters": {
                "agitation_rpm": r["N_rpm"],
                "tip_speed_m_s": r["tip"],
                "power_per_volume_W_m3": r["PV"],
                "mixing_time_s": r["tm"],
            },
            "aeration_parameters": {
                "vvm": lab.aeration_vvm,
                "Q_Lmin": r["Q_Lmin"],
                "Vs_m_s": r["Vs"],
                "vvm_const_vs": r["vvm_const_vs"],
            },
            "oxygen_transfer": {
                "kLa_predicted_h": r["kLa"],
                "kLa_required_h": r["kLa_req"],
                "OTR_mmol_L_h": r["OTR"],
                "fo": r["fo"],
            },
            "biological_performance": {
                "mu_max_h": mu_pred,
                "yield_g_g": Yxs_pred,
                "max_od": od_pred,
                "scale_efficiency_percent": efficiency,
                "mu_factor": r["mu_factor"],
                "Yxs_factor": r["Yxs_factor"],
                "od_factor": r["od_factor"],
            },
            "performance_factors": {
                "fo": r["fo"], "fm": r["fm"], "fc": r["fc"],
                "overall": r["perf"],
            },
            "risk_assessment": [
                {"risk": risk, "severity": sev, "mitigation": mit}
                for risk, sev, mit in r["risks"]
            ],
            "recommendations": r["recommendations"],
            "_raw": r,
        }

    def scale_multiple_sizes(self, lab: ScaleUpParameters,
                             target_scales: list,
                             criterion: str = "power_per_volume"):
        rows = []
        for V in sorted(target_scales):
            res = self.calculate_scale_up(lab, V, criterion)
            rows.append({
                "Volume_L": V,
                "Scale_Factor": res["scale_up_summary"]["scale_factor"],
                "mu_max_h": res["biological_performance"]["mu_max_h"],
                "Yield_g_g": res["biological_performance"]["yield_g_g"],
                "Max_OD": res["biological_performance"]["max_od"],
                "Efficiency_%": res["biological_performance"]["scale_efficiency_percent"],
                "Agitation_rpm": res["operational_parameters"]["agitation_rpm"],
                "Tip_Speed_m_s": res["operational_parameters"]["tip_speed_m_s"],
                "kLa_h": res["oxygen_transfer"]["kLa_predicted_h"],
                "P_V_W_m3": res["operational_parameters"]["power_per_volume_W_m3"],
                "tm_s": res["operational_parameters"]["mixing_time_s"],
            })
        return pd.DataFrame(rows)


# ── Literature reference datasets ─────────────────────────────────────────────

def get_lab_data_korz_1995():
    """Korz et al. (1995) — E. coli fed-batch, 10L."""
    return ScaleUpParameters(
        volume_L=10, mu_max_h=0.45, yield_g_g=0.42, max_od=45,
        agitation_rpm=800, aeration_vvm=1.0, power_input_W_m3=2500,
        kLa_h=180, vessel_diameter_m=0.25, impeller_diameter_m=0.08,
        aspect_ratio=2.5, Np=5.0, OUR=26.5, cstar=0.21)

def get_lab_data_verduyn_1990():
    """Verduyn et al. (1990) — S. cerevisiae, 1L."""
    return ScaleUpParameters(
        volume_L=1, mu_max_h=0.48, yield_g_g=0.50, max_od=12,
        agitation_rpm=600, aeration_vvm=1.5, power_input_W_m3=1500,
        kLa_h=220, vessel_diameter_m=0.10, impeller_diameter_m=0.033,
        aspect_ratio=2.0, Np=5.0, OUR=15.0, cstar=0.21)

def get_lab_data_neuss_2025():
    """Neuss et al. (2025) J. Biol. Eng. — CHO DP12, microtiter to STR.
    OTRmax criterion for small vessels, P/V for stirred tank."""
    return ScaleUpParameters(
        volume_L=0.05, mu_max_h=0.032, yield_g_g=0.15, max_od=8,
        agitation_rpm=250, aeration_vvm=0.5, power_input_W_m3=500,
        kLa_h=50, vessel_diameter_m=0.04, impeller_diameter_m=0.013,
        aspect_ratio=1.5, Np=3.0, OUR=3.0, cstar=0.21,
        temperature_C=37.0, DO_setpoint_percent=40.0)

def get_lab_data_mohanty_2025():
    """Mohanty et al. (2025) Proc. Biochem. — E. coli Endo H, shake flask to 2.5L.
    Fed-batch, induction at OD=114, 26-fold yield increase."""
    return ScaleUpParameters(
        volume_L=0.25, mu_max_h=0.65, yield_g_g=0.40, max_od=114,
        agitation_rpm=200, aeration_vvm=1.0, power_input_W_m3=800,
        kLa_h=120, vessel_diameter_m=0.08, impeller_diameter_m=0.026,
        aspect_ratio=1.8, Np=5.0, OUR=20.0, cstar=0.21,
        temperature_C=37.0)

def get_lab_data_pichia_hfbi_2025():
    """Microorganisms (2025) — P. pastoris HFBI, shake flask to bench-top.
    Methanol-fed batch induction, 86.6 mg/L over 5 days."""
    return ScaleUpParameters(
        volume_L=0.05, mu_max_h=0.18, yield_g_g=0.35, max_od=25,
        agitation_rpm=250, aeration_vvm=1.0, power_input_W_m3=600,
        kLa_h=80, vessel_diameter_m=0.04, impeller_diameter_m=0.013,
        aspect_ratio=1.5, Np=3.0, OUR=8.0, cstar=0.21,
        temperature_C=30.0)


def detect_anomalies(time_h, od=None, ph=None, do_pct=None):
    flags=[]; t=np.asarray(time_h,float)
    if od is not None:
        od=np.asarray(od,float)
        for i in range(1,len(od)):
            if od[i-1]>0.1 and (od[i-1]-od[i])/od[i-1]>0.15:
                flags.append({"time":round(float(t[i]),2),"param":"OD",
                    "msg":f"OD dropped {(od[i-1]-od[i])/od[i-1]*100:.0f}% — contamination, sampling error, or foaming",
                    "sev":"high"})
        if len(od)>=6:
            sc=int(np.sum(np.diff(np.sign(np.diff(od)))!=0))
            if sc>len(od)*0.4:
                flags.append({"time":None,"param":"OD","msg":"OD oscillating — sensor fouling or contamination","sev":"medium"})
    if ph is not None:
        ph=np.asarray(ph,float)
        dr=float(np.max(ph)-np.min(ph))
        if dr>1.0:
            flags.append({"time":None,"param":"pH","msg":f"pH drifted {dr:.2f} units — check controller","sev":"medium"})
        for i in range(1,len(ph)):
            dt=t[i]-t[i-1]
            if dt>0 and (ph[i-1]-ph[i])/max(dt,0.01)>0.5:
                flags.append({"time":round(float(t[i]),2),"param":"pH",
                    "msg":"Rapid pH drop — organic acid accumulation or bacterial contamination","sev":"high"}); break
    if do_pct is not None:
        do_pct=np.asarray(do_pct,float); dm=float(np.min(do_pct))
        if dm<5:
            flags.append({"time":None,"param":"DO","msg":f"DO crashed to {dm:.0f}% — severe O₂ limitation","sev":"high"})
        elif dm<20:
            flags.append({"time":None,"param":"DO","msg":f"Min DO {dm:.0f}% — borderline O₂ limitation","sev":"medium"})
    return flags


def compare_to_golden(current, golden):
    meta={
        "mu":       ("Growth rate μ","h⁻¹",0.10),
        "titer":    ("Product titer","g/L",0.15),
        "sty":      ("STY","g/L/h",0.15),
        "yps":      ("Yps","g/g",0.15),
        "yxs":      ("Yxs","g/g",0.15),
        "closure":  ("C closure","%",5.0),
        "rq":       ("RQ","",0.20),
    }
    EXPLS={
        "mu":    {-1:"Lower μ — check inoculum health, lag phase, medium.",1:"Higher μ — confirm medium identical to golden."},
        "titer": {-1:"Lower titer — check substrate depletion time, pH, DO profiles.",1:"Higher titer — verify assay accuracy."},
        "yps":   {-1:"Lower Yps — more C to biomass/byproducts. Check acetate and C closure.",1:"Higher Yps — verify vs thermodynamic max."},
        "closure":{-1:"C closure <95% — unmeasured byproducts or CO₂ measurement error.",1:"C closure >105% — check initial substrate concentration."},
        "rq":    {-1:"Lower RQ — more oxidative metabolism.",1:"Higher RQ — possible overflow or C limitation."},
    }
    res={}
    for p,(label,unit,tol) in meta.items():
        cv=current.get(p); gv=golden.get(p)
        if cv is None or gv is None: continue
        d=cv-gv; dp=d/max(abs(gv),1e-9)*100
        st="ok" if abs(dp)<=tol*100 else ("warn" if abs(dp)<=tol*200 else "fail")
        ex=EXPLS.get(p,{}).get(1 if d>0 else -1,"") if st!="ok" else ""
        res[p]={"label":label,"unit":unit,"current":cv,"golden":gv,"delta":d,"delta_pct":dp,"status":st,"explanation":ex}
    return res


def _ode(t, y, p):
    X,S,P,V=y
    mu=p["mu_max"]*S/(p["Ks"]+S)
    F=p.get("F",0.); D=F/max(V,1e-9)
    dX=(mu-D)*X
    dS=-(mu/max(p["Yxs"],1e-9)+p.get("ms",0))*X+D*(p.get("Sin",0)-S)
    dP=(p.get("lp_alpha",0.1)*mu+p.get("lp_beta",0.01))*X-D*P
    dV=F
    return [dX,dS,dP,dV]


def run_digital_twin(params, t_span, t_eval):
    y0=[params["X0"],params["S0"],params["P0"],params["V0"]]
    sol=solve_ivp(_ode,t_span,y0,args=(params,),t_eval=t_eval,
                  method="RK45",rtol=1e-5,atol=1e-8,
                  max_step=(t_span[1]-t_span[0])/200)
    if sol.success:
        return pd.DataFrame({"time":sol.t,"X_twin":np.maximum(sol.y[0],0),
            "S_twin":np.maximum(sol.y[1],0),"P_twin":np.maximum(sol.y[2],0),"V_twin":sol.y[3]})
    return pd.DataFrame()


def fit_twin_to_data(time_h, od, substrate, product, dcw_factor, V0):
    t=np.asarray(time_h,float); dcw=np.asarray(od,float)*dcw_factor
    sub=np.asarray(substrate,float)
    prd=np.asarray(product,float) if product is not None else np.zeros_like(dcw)
    def obj(x):
        p={"mu_max":max(x[0],0.01),"Ks":max(x[1],0.001),"Yxs":max(x[2],0.01),
           "ms":0,"lp_alpha":max(x[3],0),"lp_beta":max(x[4],0),
           "X0":float(dcw[0]),"S0":float(sub[0]),"P0":float(prd[0]),"V0":float(V0),"F":0,"Sin":0}
        try:
            df=run_digital_twin(p,(t[0],t[-1]),t)
            if df.empty: return 1e6
            l=np.mean((df["X_twin"].values-dcw)**2)/max(np.var(dcw),1e-6)
            l+=np.mean((df["S_twin"].values-sub)**2)/max(np.var(sub),1e-6)
            l+=np.mean((df["P_twin"].values-prd)**2)/max(np.var(prd),1e-6)
            return float(l)
        except: return 1e6
    res=minimize(obj,[0.5,0.1,0.4,0.1,0.01],method="L-BFGS-B",
                 bounds=[(0.01,3),(0.001,5),(0.01,1),(0,2),(0,0.5)],
                 options={"maxiter":300,"ftol":1e-9})
    x=res.x
    return {"mu_max":float(max(x[0],0.01)),"Ks":float(max(x[1],0.001)),"Yxs":float(max(x[2],0.01)),
            "ms":0,"lp_alpha":float(max(x[3],0)),"lp_beta":float(max(x[4],0)),
            "X0":float(dcw[0]),"S0":float(sub[0]),"P0":float(prd[0]),"V0":float(V0),
            "F":0,"Sin":0,"fit_loss":float(res.fun),"converged":bool(res.success)}
