"""
Constraint-based flux analysis driven by measured fermentation data.

Pipeline
--------
1. ``specific_rates``: from the exponential phase of a run, estimate the
   biomass-specific uptake/secretion rate q_i (mmol gDCW⁻¹ h⁻¹) of every
   measured metabolite as  q_i = μ · dC_i/dX  (slope of concentration vs
   biomass, which is robust to sampling noise and needs no derivatives),
   and q_O2 / q_CO2 from off-gas OUR/CER divided by biomass.
2. ``run_fba``: constrain a genome-scale model (iML1515 for E. coli,
   yeast-GEM for S. cerevisiae) with those rates, then
     a. maximise growth → model-predicted μ, compared with measured μ
        (a stoichiometric consistency check on the data),
     b. fix growth at the attainable μ and run parsimonious FBA for a
        flux distribution, with flux-variability ranges for central carbon.

This is constraint-based (FBA) flux estimation, not ¹³C-MFA: fluxes
inside the network are the most parsimonious distribution consistent with
the measured exchange rates, and FVA ranges show how well the data pin
them down.

Models
------
* iML1515 — Monk et al. 2017, Nat Biotechnol 35:904. doi:10.1038/nbt.3956
* yeast-GEM v9 — Lu et al. 2019, Nat Commun 10:3586. doi:10.1038/s41467-019-11581-3
"""
from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.stats import linregress

MODEL_DIR = Path(__file__).parent.parent / "models"

# ── Organism → model and reaction vocabulary ─────────────────────────────────
MODELS = {
    "E. coli (iML1515)": {
        "file": "iML1515.xml.gz",
        "citation": "Monk et al. 2017, Nat Biotechnol 35:904 (doi:10.1038/nbt.3956)",
        "o2": "EX_o2_e", "co2": "EX_co2_e",
        "trace": ["EX_meoh_e"],          # cofactor-synthesis side products
        "exchange": {
            "glucose": "EX_glc__D_e", "glycerol": "EX_glyc_e", "xylose": "EX_xyl__D_e",
            "lactose": "EX_lcts_e", "galactose": "EX_gal_e", "fructose": "EX_fru_e",
            "sucrose": "EX_sucr_e", "arabinose": "EX_arab__L_e",
            "acetate": "EX_ac_e", "lactate": "EX_lac__D_e", "formate": "EX_for_e",
            "succinate": "EX_succ_e", "ethanol": "EX_etoh_e", "pyruvate": "EX_pyr_e",
        },
        # display name → (reaction id, pathway)
        "central": {
            "Glucose PTS uptake":           ("GLCptspp", "Uptake"),
            "Phosphoglucose isomerase":     ("PGI", "Glycolysis"),
            "Phosphofructokinase":          ("PFK", "Glycolysis"),
            "GAPDH":                        ("GAPD", "Glycolysis"),
            "Pyruvate kinase":              ("PYK", "Glycolysis"),
            "G6P dehydrogenase (oxPPP)":    ("G6PDH2r", "Pentose phosphate"),
            "Pyruvate dehydrogenase":       ("PDH", "Pyruvate node"),
            "Pyruvate formate-lyase":       ("PFL", "Pyruvate node"),
            "Lactate dehydrogenase":        ("LDH_D", "Fermentation"),
            "Phosphotransacetylase":        ("PTAr", "Overflow (acetate)"),
            "Acetate kinase":               ("ACKr", "Overflow (acetate)"),
            "Citrate synthase":             ("CS", "TCA cycle"),
            "Isocitrate dehydrogenase":     ("ICDHyr", "TCA cycle"),
            "2-Oxoglutarate dehydrogenase": ("AKGDH", "TCA cycle"),
            "Succinate dehydrogenase":      ("SUCDi", "TCA cycle"),
            "Malate dehydrogenase":         ("MDH", "TCA cycle"),
            "Isocitrate lyase (glyoxylate)": ("ICL", "Glyoxylate shunt"),
            "PEP carboxylase":              ("PPC", "Anaplerosis"),
            "PEP carboxykinase":            ("PPCK", "Anaplerosis"),
            "Malic enzyme (NADP)":          ("ME2", "Anaplerosis"),
            "ATP synthase":                 ("ATPS4rpp", "Energy"),
            "O2 uptake":                    ("EX_o2_e", "Exchange"),
            "CO2 release":                  ("EX_co2_e", "Exchange"),
        },
    },
    "S. cerevisiae (yeast-GEM)": {
        "file": "yeast-GEM.xml.gz",
        "citation": "Lu et al. 2019, Nat Commun 10:3586 (doi:10.1038/s41467-019-11581-3)",
        "o2": "r_1992", "co2": "r_1672",
        "trace": ["r_1810", "r_1814"],   # glycine, glycolaldehyde
        "exchange": {
            "glucose": "r_1714", "fructose": "r_1709", "galactose": "r_1710",
            "sucrose": "r_2058", "maltose": "r_1931", "xylose": "r_1718",
            "ethanol": "r_1761", "glycerol": "r_1808", "acetate": "r_1634",
            "succinate": "r_2056", "lactate": "r_1551", "pyruvate": "r_2033",
            "acetaldehyde": "r_1631",
        },
        "central": {
            "Phosphoglucose isomerase":       ("r_0467", "Glycolysis"),
            "Phosphofructokinase":            ("r_0886", "Glycolysis"),
            "GAPDH":                          ("r_0486", "Glycolysis"),
            "Pyruvate kinase":                ("r_0962", "Glycolysis"),
            "G6P dehydrogenase (oxPPP)":      ("r_0466", "Pentose phosphate"),
            "Pyruvate decarboxylase":         ("r_0959", "Fermentation"),
            "Alcohol dehydrogenase (→ ethanol)": ("r_2115", "Fermentation"),
            "G3P dehydrogenase (glycerol)":   ("r_0491", "Redox balance"),
            "Acetaldehyde dehydrogenase":     ("r_0173", "PDH bypass"),
            "Acetyl-CoA synthetase":          ("r_0112", "PDH bypass"),
            "Pyruvate dehydrogenase (mito)":  ("r_0961", "Pyruvate node"),
            "Pyruvate carboxylase":           ("r_0958", "Anaplerosis"),
            "Citrate synthase (mito)":        ("r_0300", "TCA cycle"),
            "Isocitrate DH, NAD (mito)":      ("r_0658", "TCA cycle"),
            "2-Oxoglutarate DH (mito)":       ("r_0832", "TCA cycle"),
            "Malate dehydrogenase (mito)":    ("r_0713", "TCA cycle"),
            "Isocitrate lyase (glyoxylate)":  ("r_0662", "Glyoxylate shunt"),
            "ATP synthase":                   ("r_0226", "Energy"),
            "O2 uptake":                      ("r_1992", "Exchange"),
            "CO2 release":                    ("r_1672", "Exchange"),
        },
    },
}

# name → (molar mass g/mol, carbon atoms). Keys are matched against column names.
METABOLITES = {
    "glucose": (180.16, 6), "fructose": (180.16, 6), "galactose": (180.16, 6),
    "glycerol": (92.09, 3), "xylose": (150.13, 5), "arabinose": (150.13, 5),
    "lactose": (342.30, 12), "sucrose": (342.30, 12), "maltose": (342.30, 12),
    "acetate": (59.04, 2), "lactate": (89.07, 3), "formate": (45.02, 1),
    "succinate": (117.08, 4), "ethanol": (46.07, 2), "pyruvate": (87.05, 3),
    "acetaldehyde": (44.05, 2),
}
SUBSTRATES = {"glucose", "fructose", "galactose", "glycerol", "xylose",
              "arabinose", "lactose", "sucrose", "maltose"}

TRACE_MAX = 0.05   # mmol/gDCW/h allowed for unavoidable trace side products
BIOMASS_C_MMOL_PER_G = 1000 / 24.6   # ~CH1.8O0.5N0.2 → 24.6 g/C-mol (Roels 1983)


def guess_metabolite(column: str) -> str | None:
    """Map a column name like 'Glucose_gL' or 'acetate (g/L)' to a metabolite key."""
    c = column.lower()
    for key in sorted(METABOLITES, key=len, reverse=True):
        if key in c:
            return key
    return None


# ── 1. Specific rates from data ──────────────────────────────────────────────
@dataclass
class RateEstimate:
    metabolite: str
    q: float                 # mmol/gDCW/h; negative = uptake
    q_se: float              # standard error, propagated from the regression
    r2: float
    n: int
    source: str              # "concentration" or "off-gas"

    @property
    def kind(self) -> str:
        return "uptake" if self.q < 0 else "secretion"


def specific_rates(time_h, od, concentrations: dict, mu: float, mu_se: float,
                   window: tuple[float, float], dcw_factor: float = 0.4,
                   our=None, cer=None) -> list[RateEstimate]:
    """Biomass-specific rates in the exponential window.

    concentrations : {metabolite_key: array of g/L, aligned with time_h}
    our / cer      : arrays in mmol L⁻¹ h⁻¹ (optional)
    """
    t = np.asarray(time_h, float)
    X = np.asarray(od, float) * dcw_factor
    m = (t >= window[0]) & (t <= window[1]) & np.isfinite(X)
    out: list[RateEstimate] = []

    for key, conc in concentrations.items():
        if key not in METABOLITES:
            continue
        c = np.asarray(conc, float)
        mm = m & np.isfinite(c)
        if mm.sum() < 3 or np.ptp(X[mm]) <= 0:
            continue
        reg = linregress(X[mm], c[mm])                 # g metabolite per g DCW
        mw = METABOLITES[key][0]
        q = mu * reg.slope / mw * 1000                 # mmol/gDCW/h
        # relative errors of μ and slope add in quadrature
        rel = np.hypot(mu_se / mu if mu else 0, reg.stderr / abs(reg.slope) if reg.slope else 0)
        out.append(RateEstimate(key, float(q), float(abs(q) * rel), float(reg.rvalue ** 2),
                                int(mm.sum()), "concentration"))

    for key, arr, sign in (("oxygen", our, -1), ("carbon dioxide", cer, +1)):
        if arr is None:
            continue
        a = np.asarray(arr, float)
        mm = m & np.isfinite(a) & (X > 0)
        if mm.sum() < 3:
            continue
        qs = a[mm] / X[mm]
        out.append(RateEstimate(key, float(sign * np.median(qs)),
                                float(np.std(qs) / np.sqrt(mm.sum())), float("nan"),
                                int(mm.sum()), "off-gas"))
    return out


# ── 2. FBA ───────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=4)
def load_model(name: str):
    import cobra
    cfg = MODELS[name]
    model = cobra.io.read_sbml_model(str(MODEL_DIR / cfg["file"]))
    model.solver = "glpk"
    return model


@dataclass
class FluxResult:
    model_name: str
    status: str                       # "ok" | "infeasible" | "no_substrate"
    mu_measured: float
    mu_predicted: float | None = None          # from point-estimate exchange rates
    substrate: str | None = None               # primary substrate key
    q_substrate_measured: float | None = None  # mmol/gDCW/h (negative = uptake)
    q_substrate_se: float | None = None
    q_substrate_required: float | None = None  # minimum uptake for measured μ
    gas_check: list = field(default_factory=list)   # dicts: gas, measured, model
    band: float | None = None
    used_gases: bool = False
    constraints: list = field(default_factory=list)   # (metabolite, rxn, lb, ub)
    central: list = field(default_factory=list)       # dicts: Reaction, Pathway, Flux, Min, Max
    exchanges: list = field(default_factory=list)
    carbon_recovery: float | None = None
    messages: list = field(default_factory=list)


def _bounds(q, q_se, band):
    """Interval for a measured rate: max(2·SE, relative band)."""
    half = max(2 * q_se, abs(q) * band)
    return q - half, q + half


def _rid(cfg, metabolite):
    if metabolite == "oxygen":
        return cfg["o2"]
    if metabolite == "carbon dioxide":
        return cfg["co2"]
    return cfg["exchange"].get(metabolite)


def _opt(model):
    """Objective value, or None if infeasible/unbounded."""
    v = model.slim_optimize(error_value=float("nan"))
    return None if v != v else float(v)


def _close_carbon_uptake(model, cfg, measured=()):
    """No carbon uptake except what is measured, and no carbon secretion
    except measured products and CO2 — otherwise the model can dump excess
    substrate carbon into exchanges nobody measured, hiding data problems."""
    keep = {_rid(cfg, m) for m in measured} | {cfg["co2"]}
    for rx in model.exchanges:
        if rx.id in keep:
            continue
        if rx.id in cfg.get("trace", ()):
            rx.bounds = (0.0, TRACE_MAX)
            continue
        has_c = any(met.elements.get("C", 0) > 0 for met in rx.metabolites)
        if rx.id in cfg["exchange"].values() or has_c:
            rx.bounds = (0.0, 0.0) if has_c else (max(rx.lower_bound, 0.0), rx.upper_bound)


def _constrain(model, cfg, rates, band, gases, point=False):
    """Apply measured rates. point=True fixes metabolites at their estimate."""
    cons = []
    for r in rates:
        is_gas = r.metabolite in ("oxygen", "carbon dioxide")
        if is_gas and not gases:
            continue
        rid = _rid(cfg, r.metabolite)
        if rid is None:
            continue
        lo, hi = (r.q, r.q) if point else _bounds(r.q, r.q_se, band)
        if r.q > 0:
            lo = max(lo, 0.0)
        else:
            hi = min(hi, 0.0)
        model.reactions.get_by_id(rid).bounds = (min(lo, hi), max(lo, hi))
        cons.append((r.metabolite, rid, lo, hi))
    return cons


def run_fba(model_name: str, rates: list[RateEstimate], mu_measured: float,
            band: float = 0.10, constrain_gases: bool = True) -> FluxResult:
    """Three questions, answered with the genome-scale model:

    A. Given the measured exchange rates (point estimates, gases left free),
       what growth rate is stoichiometrically possible?  → mu_predicted
    B. What substrate uptake does the measured μ actually require?
       → q_substrate_required, and the O2/CO2 the model expects (vs off-gas)
    C. At the measured μ, what is the most parsimonious internal flux
       distribution consistent with all measurements (within their error)?
       → central fluxes with flux-variability ranges
    """
    import cobra.flux_analysis as fa
    cfg = MODELS[model_name]
    res = FluxResult(model_name=model_name, status="ok", mu_measured=mu_measured)
    base = load_model(model_name)
    rates = [r for r in rates if _rid(cfg, r.metabolite) is not None]

    subs = [r for r in rates if r.metabolite in SUBSTRATES and r.q < 0]
    if not subs:
        res.status = "no_substrate"
        res.messages.append("No consumed substrate with a model exchange reaction was "
                            "found — map at least one substrate column (e.g. glucose).")
        return res
    primary = min(subs, key=lambda r: r.q * METABOLITES[r.metabolite][1])  # most C
    res.substrate = primary.metabolite
    res.q_substrate_measured, res.q_substrate_se = primary.q, primary.q_se
    sub_rid = cfg["exchange"][primary.metabolite]
    bm_rxn = next(r for r in base.reactions if r.objective_coefficient)

    # A — predicted μ from point estimates (gases free)
    with base as m:
        _close_carbon_uptake(m, cfg, [r.metabolite for r in rates])
        _constrain(m, cfg, rates, 0, gases=False, point=True)
        v = _opt(m)
        if v is None:   # products exceed what the substrate allows: allow less product
            for r in rates:
                if r.q > 0 and r.metabolite not in ("carbon dioxide",):
                    rx = m.reactions.get_by_id(_rid(cfg, r.metabolite))
                    rx.bounds = (0.0, r.q)
            v = _opt(m)
            if v is not None:
                res.messages.append("Measured product secretion exceeds what the measured "
                                    "substrate uptake can supply; products were capped.")
        res.mu_predicted = v

    # B — minimum substrate uptake for the measured μ; expected O2 / CO2
    if mu_measured:
        with base as m:
            _close_carbon_uptake(m, cfg, [r.metabolite for r in rates])
            _constrain(m, cfg, [r for r in rates if r is not primary], 0, gases=False, point=True)
            m.reactions.get_by_id(sub_rid).bounds = (-1000.0, 0.0)
            bm_rxn_m = m.reactions.get_by_id(bm_rxn.id)
            bm_rxn_m.bounds = (mu_measured, mu_measured)
            m.objective = m.reactions.get_by_id(sub_rid)        # maximise (least negative)
            m.objective_direction = "max"
            v = _opt(m)
            if v is not None:
                res.q_substrate_required = float(v)
                m.reactions.get_by_id(sub_rid).bounds = (v * 1.001, v * 0.999)
                m.objective = bm_rxn_m
                try:
                    sol = fa.pfba(m)
                    for r in rates:
                        if r.metabolite in ("oxygen", "carbon dioxide"):
                            res.gas_check.append({"gas": r.metabolite, "measured": r.q,
                                                  "measured_se": r.q_se,
                                                  "model": float(sol.fluxes[_rid(cfg, r.metabolite)])})
                except Exception:
                    pass

    # C — flux map at measured μ within measurement error
    mu_fix = mu_measured or res.mu_predicted
    attempts = [(b, g) for b in (band, 0.25, 0.50) for g in ((True, False) if constrain_gases else (False,))]
    with base as m:
        _close_carbon_uptake(m, cfg, [r.metabolite for r in rates])
        for b, g in attempts:
            with m:
                _constrain(m, cfg, rates, b, gases=g)
                m.reactions.get_by_id(bm_rxn.id).bounds = (mu_fix * 0.995, mu_fix * 1.005)
                ok = _opt(m) is not None
            if ok:
                res.band, res.used_gases = b, g
                break
        else:
            res.status = "infeasible"
            res.messages.append(
                "No flux distribution matches the measured μ and rates even at ±50 % "
                "tolerance — check units, the OD→DCW factor, and that substrates and "
                "products are mapped the right way round.")
            res.messages[:0] = interpret(res, rates)
            return res

        res.constraints = _constrain(m, cfg, rates, res.band, gases=res.used_gases)
        m.reactions.get_by_id(bm_rxn.id).bounds = (mu_fix * 0.995, mu_fix * 1.005)
        pf = fa.pfba(m)
        ids = [rid for rid, _ in cfg["central"].values() if rid in m.reactions]
        # pfba_factor bounds total flux to 110 % of the parsimonious optimum,
        # which removes thermodynamically meaningless loops from the ranges.
        fva = fa.flux_variability_analysis(m, reaction_list=ids, fraction_of_optimum=0.0,
                                           pfba_factor=1.10, processes=1)
        for name, (rid, pathway) in cfg["central"].items():
            if rid in m.reactions:
                res.central.append({"Reaction": name, "Pathway": pathway, "ID": rid,
                                    "Flux": float(pf.fluxes[rid]),
                                    "Min": float(fva.loc[rid, "minimum"]),
                                    "Max": float(fva.loc[rid, "maximum"])})
        c_in = c_out = 0.0
        for key, rid in cfg["exchange"].items():
            v = float(pf.fluxes[rid]); nC = METABOLITES[key][1]
            if v < -1e-9:
                c_in += -v * nC
            elif v > 1e-9:
                c_out += v * nC
            if abs(v) > 1e-6:
                res.exchanges.append({"Metabolite": key, "Flux (mmol/gDCW/h)": v})
        co2, o2 = float(pf.fluxes[cfg["co2"]]), float(pf.fluxes[cfg["o2"]])
        res.exchanges += [{"Metabolite": "CO2", "Flux (mmol/gDCW/h)": co2},
                          {"Metabolite": "O2", "Flux (mmol/gDCW/h)": o2}]
        c_out += max(co2, 0) + mu_fix * BIOMASS_C_MMOL_PER_G
        res.carbon_recovery = c_out / c_in if c_in else None

    if res.band > band:
        res.messages.append(f"Measurement intervals had to be widened to ±{res.band:.0%} "
                            "to find a consistent flux distribution — treat fluxes as indicative.")
    if constrain_gases and any(r.metabolite in ("oxygen", "carbon dioxide") for r in rates) \
            and not res.used_gases:
        res.messages.append("Off-gas rates could not be matched together with the other "
                            "measurements and were left unconstrained in the flux map.")
    res.messages[:0] = interpret(res, rates)
    return res


def interpret(res: FluxResult, rates) -> list[str]:
    """Plain-language reading of predicted vs measured growth."""
    out = []
    if res.mu_predicted is None or not res.mu_measured:
        return out
    ratio = res.mu_predicted / res.mu_measured
    noisy = [r for r in rates if r.metabolite in SUBSTRATES and r.q < 0
             and r.q_se > 0.25 * abs(r.q)]
    if ratio > 1.15:
        out.append(
            f"The measured uptake could support μ = {res.mu_predicted:.3f} h⁻¹, "
            f"{ratio:.2f}× the observed {res.mu_measured:.3f} h⁻¹. Carbon or energy is "
            "going somewhere the data do not show: unmeasured by-products, higher "
            "maintenance (stress, plasmid/protein burden), or an over-estimated uptake rate.")
    elif ratio < 0.90:
        out.append(
            f"The measured uptake can only explain μ = {res.mu_predicted:.3f} h⁻¹, "
            f"below the observed {res.mu_measured:.3f} h⁻¹. Substrate uptake is probably "
            "under-estimated, or the medium contains an unmapped carbon source "
            "(yeast extract, peptone, a second sugar), or the OD→DCW factor is too high.")
    else:
        out.append(
            f"Measured rates are consistent with the observed growth: model μ "
            f"{res.mu_predicted:.3f} vs measured {res.mu_measured:.3f} h⁻¹ "
            f"({(ratio - 1) * 100:+.0f} %).")
    for r in noisy:
        out.append(f"The {r.metabolite} uptake rate is uncertain (±{r.q_se / abs(r.q):.0%}, "
                   f"{r.n} samples in the exponential window), so the predicted μ is too. "
                   "More substrate samples during exponential growth would tighten it.")
    if res.q_substrate_required is not None and res.q_substrate_measured:
        req, meas, se = -res.q_substrate_required, -res.q_substrate_measured, res.q_substrate_se or 0
        if abs(meas - req) > max(2 * se, 0.15 * req):
            word = "higher" if meas > req else "lower"
            out.append(f"Measured {res.substrate} uptake ({meas:.2f} ± {se:.2f} mmol/gDCW/h) is "
                       f"{word} than the {req:.2f} the model needs for μ {res.mu_measured:.3f} h⁻¹ "
                       "with the measured by-products.")
    gas_off = []
    for g in res.gas_check:
        meas, mod = abs(g["measured"]), abs(g["model"])
        if mod and abs(meas - mod) / mod > 0.25:
            gas_off.append(f"{g['gas']} {meas:.2f} vs {mod:.2f} ({(meas / mod - 1) * 100:+.0f} %)")
    if gas_off:
        out.append("Off-gas rates differ from what the model expects at the measured μ "
                   f"(mmol/gDCW/h, measured vs model): {'; '.join(gas_off)}. Common causes: "
                   "OD→DCW factor (biomass in the denominator), analyzer baseline offset or "
                   "delay, CO₂ retained as bicarbonate at pH ≥ 7, or working volume.")
    sub = [r for r in rates if r.metabolite in SUBSTRATES and r.q < 0]
    byp = [r for r in rates if r.metabolite in ("acetate", "ethanol") and r.q > 0]
    if sub and byp:
        cs = sum(-r.q * METABOLITES[r.metabolite][1] for r in sub)
        cb = sum(r.q * METABOLITES[r.metabolite][1] for r in byp)
        if cs > 0 and cb / cs > 0.10:
            names = " and ".join(r.metabolite for r in byp)
            out.append(f"Overflow metabolism: {cb / cs:.0%} of substrate carbon leaves as "
                       f"{names} during exponential growth.")
    return out
