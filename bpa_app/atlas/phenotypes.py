"""
Per-run phenotypes and per-perturbation effects.

Phenotypes are computed only from the phase where runs in a campaign share
the same conditions (the batch phase), unless marked otherwise, so a
difference between conditions is attributable to the perturbation and not to
a different feed. Each phenotype records how it was obtained.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import linregress

from modules.calcs import compute_growth_kinetics

DEPLETED_GL = 0.10      # glucose below this = depleted

PHENOTYPES = {
    # name: (unit, description, confounded_by_feed)
    "mu_batch_h":            ("h⁻¹", "specific growth rate in the batch phase (until glucose depletion)", False),
    "mu_batch_se_h":         ("h⁻¹", "standard error of mu_batch_h", False),
    "glucose_depletion_h":   ("h", "first sample with glucose < 0.1 g/L (resolution = sampling interval)", False),
    "acetate_peak_gL":       ("g/L", "highest acetate up to 0.5 h after glucose depletion (overflow)", False),
    "acetate_reconsumed_frac": ("–", "fraction of peak acetate consumed 0.75–2.5 h after glucose depletion", False),
    "Yxs_batch_gg":          ("g/g", "biomass yield on glucose in the batch phase (only if glucose falls monotonically)", False),
    "mu_fedbatch_h":         ("h⁻¹", "mean growth rate after glucose depletion (fed-batch); depends on the feed", True),
    "biomass_final_gL":      ("g/L", "last measured biomass", True),
}


def _series(obs, var):
    s = obs[obs.variable == var].sort_values("time_h")
    return s.time_h.to_numpy(float), s.value.to_numpy(float)


def run_phenotypes(run: dict, obs: pd.DataFrame) -> dict:
    """obs = observations of this run only."""
    out = {"run_id": run["run_id"]}
    tx, x = _series(obs, "biomass_gL")
    if len(tx) == 0:
        tx, od = _series(obs, "od600")
        x = od * (run.get("dcw_per_od") or 0.4)
    tg, g = _series(obs, "glucose_gL")
    ta, a = _series(obs, "acetate_gL")
    if len(tx) < 3:
        return out

    # batch end = glucose depletion, else the whole run is batch-like
    t_dep = None
    if len(tg):
        # first depleted sample that follows a sample with glucose present (> 0.5 g/L);
        # later fed-batch spikes (overfeeding, flagged outliers) must not reset it.
        # If the first sample is already (nearly) depleted, the first depleted time is an upper bound.
        for i in range(len(g)):
            if g[i] < DEPLETED_GL and (i == 0 or g[:i].max() > 0.5 or g[0] < 0.5):
                t_dep = float(tg[i])
                break
    out["glucose_depletion_h"] = t_dep

    in_batch = tx <= (t_dep if t_dep is not None else tx.max())
    if in_batch.sum() >= 3:
        if in_batch.sum() >= 5:
            k = compute_growth_kinetics(tx[in_batch], x[in_batch], dcw_factor=1.0)
            mu, se = k.get("mu"), k.get("mu_se")
        else:   # sparse batch phase: plain log-linear fit over it
            r = linregress(tx[in_batch], np.log(np.clip(x[in_batch], 1e-9, None)))
            mu, se = float(r.slope), float(r.stderr)
        out["mu_batch_h"], out["mu_batch_se_h"] = mu, se

    if len(ta):
        lim = (t_dep + 0.5) if t_dep is not None else ta.max()
        pk = a[ta <= lim]
        if len(pk):
            out["acetate_peak_gL"] = float(pk.max())
        if t_dep is not None:
            late = a[(ta >= t_dep + 0.75) & (ta <= t_dep + 2.5)]
            if len(late) and out.get("acetate_peak_gL", 0) > 0.05:
                out["acetate_reconsumed_frac"] = float(
                    np.clip(1 - late.mean() / out["acetate_peak_gL"], -1, 1))

    if len(tg) and t_dep is not None:
        m = tg <= t_dep
        gx = np.interp(tg[m], tx, x) if m.sum() else []
        if m.sum() >= 3 and np.all(np.diff(g[m]) < 0):
            r = linregress(g[m], gx)
            out["Yxs_batch_gg"] = float(-r.slope)

    if t_dep is not None and run.get("mode") == "Fed-batch":
        fb = tx > t_dep
        if fb.sum() >= 3:
            out["mu_fedbatch_h"] = float(linregress(tx[fb], np.log(x[fb])).slope)
    out["biomass_final_gL"] = float(x[-1])
    return out


def effects(runs: pd.DataFrame, pheno: pd.DataFrame) -> pd.DataFrame:
    """Each perturbed condition vs its campaign's reference condition."""
    df = runs[["run_id", "campaign", "condition", "reference_condition",
               "perturbation_type", "perturbation"]].merge(pheno, on="run_id")
    rows = []
    names = [p for p in PHENOTYPES if not p.endswith("_se_h")]
    for (camp, cond), g in df.groupby(["campaign", "condition"]):
        refc = g.reference_condition.iloc[0]
        if cond == refc:
            continue
        ref = df[(df.campaign == camp) & (df.condition == refc)]
        for p in names:
            a, b = g[p].dropna().to_numpy(float), ref[p].dropna().to_numpy(float)
            if len(a) < 2 or len(b) < 2:
                continue
            t, pval = stats.ttest_ind(a, b, equal_var=False)
            sd = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
            rows.append({
                "campaign": camp, "condition": cond, "reference": refc,
                "perturbation_type": g.perturbation_type.iloc[0],
                "perturbation": g.perturbation.iloc[0] or cond,
                "phenotype": p, "unit": PHENOTYPES[p][0],
                "mean": a.mean(), "sd": a.std(ddof=1), "n": len(a),
                "ref_mean": b.mean(), "ref_sd": b.std(ddof=1), "ref_n": len(b),
                "difference": a.mean() - b.mean(),
                "pct_change": (a.mean() / b.mean() - 1) * 100 if b.mean() else np.nan,
                "effect_size_d": (a.mean() - b.mean()) / sd if sd > 0 else np.nan,
                "p_welch": float(pval),
                "confounded_by_feed": PHENOTYPES[p][2],
            })
    return pd.DataFrame(rows)
