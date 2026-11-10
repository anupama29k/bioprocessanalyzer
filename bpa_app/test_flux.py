"""Tests for modules/flux.py.   python test_flux.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from modules import flux                                    # noqa: E402
from modules.calcs import compute_growth_kinetics            # noqa: E402

R = flux.RateEstimate
ECOLI, YEAST = "E. coli (iML1515)", "S. cerevisiae (yeast-GEM)"
results = []


def check(name, cond, detail=""):
    results.append(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


# 1. Rate estimation recovers known q from noise-free exponential data
t = np.linspace(0, 5, 11); mu = 0.5; X0 = 0.05
X = X0 * np.exp(mu * t); od = X / 0.4
Y = 0.5                                     # g DCW / g glucose
glc = 10 - (X - X0) / Y
rates = flux.specific_rates(t, od, {"glucose": glc}, mu, 0.0, (0, 5), 0.4)
q_expected = -mu / Y / 180.16 * 1000
check("specific rate q = μ/Y", abs(rates[0].q - q_expected) < 1e-6,
      f"{rates[0].q:.3f} vs {q_expected:.3f} mmol/gDCW/h")

# 2. FBA sanity: iML1515 on 10 mmol/gDCW/h glucose grows at its published 0.877 h⁻¹
res = flux.run_fba(ECOLI, [R("glucose", -10.0, 0.1, 1, 10, "c")], 0.877)
check("iML1515 μ at q_glc = 10", abs(res.mu_predicted - 0.877) < 0.002, f"{res.mu_predicted:.4f}")
check("required uptake inverts prediction", abs(res.q_substrate_required + 10.0) < 0.01,
      f"{res.q_substrate_required:.3f}")
check("carbon recovery ~100 %", abs(res.carbon_recovery - 1) < 0.05, f"{res.carbon_recovery:.3f}")

# 3. Unmeasured by-products cannot hide excess carbon: lower μ than observed is flagged
res = flux.run_fba(ECOLI, [R("glucose", -5.0, 0.1, 1, 10, "c")], 0.877)
check("under-supplied growth flagged", res.mu_predicted < 0.877 * 0.9
      and any("can only explain" in m for m in res.messages), f"{res.mu_predicted:.3f}")

# 4. Yeast Crabtree overflow is feasible and reported
rates = [R("glucose", -18.0, 0.9, .99, 8, "c"), R("ethanol", 28.0, 1.4, .99, 8, "c"),
         R("glycerol", 2.0, 0.2, .98, 8, "c")]
res = flux.run_fba(YEAST, rates, 0.38)
check("yeast-GEM overflow feasible", res.status == "ok" and res.mu_predicted > 0.2,
      f"μ_pred {res.mu_predicted:.3f}")
check("overflow message", any("Overflow" in m for m in res.messages))
adh = next(c for c in res.central if c["ID"] == "r_2115")
check("ADH carries ethanol flux", adh["Flux"] > 20, f"{adh['Flux']:.1f}")

# 5. Real data (Simensen 2022): required glucose uptake in the E. coli range
d = pd.read_csv(Path(__file__).parent / "published_data/simensen2022_ecoli_mg1655_batch/sampling_with_offgas.csv")
dd = d.dropna(subset=["OD_600nm"])
k = compute_growth_kinetics(dd.Time_h.values, dd.OD_600nm.values, dcw_factor=0.5)
conc = {flux.guess_metabolite(c): d[c].values for c in d.columns if c.endswith("_gL")}
rates = flux.specific_rates(d.Time_h.values, d.OD_600nm.values, conc, k["mu"], k["mu_se"],
                            (k["exp_t"][0], k["exp_t"][-1]), 0.5,
                            our=d.OUR_mmol_Lh.values, cer=d.CER_mmol_Lh.values)
res = flux.run_fba(ECOLI, rates, k["mu"])
check("Simensen 2022 flux map solves", res.status == "ok")
check("required q_glc 7–12 mmol/gDCW/h", 7 < -res.q_substrate_required < 12,
      f"{-res.q_substrate_required:.2f}")

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
