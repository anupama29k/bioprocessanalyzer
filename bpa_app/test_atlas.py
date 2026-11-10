"""Tests for the Bioprocess Atlas build.   python test_atlas.py"""
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from atlas.build import build          # noqa: E402
from atlas.schema import VARIABLES     # noqa: E402

res = []
def check(name, cond, detail=""):
    res.append(bool(cond)); print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")

with tempfile.TemporaryDirectory() as d:
    r = build(out=Path(d))
    runs, obs, ph, eff = r["runs"], r["observations"], r["phenotypes"], r["effects"]
    check("77 runs from 3 measured datasets, 3 organisms",
          len(runs) == 77 and len(r["datasets"]) == 3 and r["datasets"].measured.all()
          and runs.organism.nunique() == 3)
    check("11 explicit yeast contrasts", r["manifest"]["contrasts"] == 11)
    check("every observation uses the controlled vocabulary", set(obs.variable) <= set(VARIABLES))
    check("every run has a DOI and license", runs.source_doi.str.len().gt(0).all() and runs.license.str.len().gt(0).all())
    check("one reference condition per campaign",
          runs[runs.is_reference].groupby("campaign").condition.nunique().eq(1).all())
    m = runs.merge(ph, on="run_id")
    hans = m[m.dataset_id == "hans2020"]
    check("glucose depletion found in the batch phase for every Hans run",
          hans.glucose_depletion_h.between(0, 3.5).all(), f"max {hans.glucose_depletion_h.max():.2f} h")
    sim = m[m.dataset_id == "simensen2022"].iloc[0]
    check("Simensen μ within 10 % of the paper's 0.71 h⁻¹", abs(sim.mu_batch_h / 0.71 - 1) < 0.10,
          f"{sim.mu_batch_h:.3f}")
    aceA = hans[hans.condition == "BW25113 ΔaceA"].acetate_reconsumed_frac.mean()
    par = hans[hans.condition == "BW25113"].acetate_reconsumed_frac.mean()
    check("ΔaceA (no glyoxylate shunt) barely reconsumes acetate vs parent", aceA < 0.2 and par > 0.5,
          f"{aceA:.2f} vs {par:.2f}")
    e = eff[(eff.perturbation == "ΔaceA") & (eff.phenotype == "acetate_reconsumed_frac")].iloc[0]
    check("ΔaceA acetate effect is large", e.effect_size_d < -3, f"d = {e.effect_size_d:.1f}, p = {e.p_welch:.2f}")
    y = eff[eff.campaign == "uhlendorff2026 · W-68"]
    t37 = y[(y.perturbation.str.startswith("37")) & (y.phenotype == "vcd_max_1e6_mL")].iloc[0]
    check("S. cerevisiae W-68 at 37 °C reaches far fewer cells than same-day 22 °C controls",
          t37["pct_change"] < -50 and t37.p_welch < 0.05, f"{t37["pct_change"]:.0f} %, p = {t37.p_welch:.3f}")
    l37 = eff[(eff.campaign == "uhlendorff2026 · W-34/70") & eff.perturbation.str.startswith("37")
              & (eff.phenotype == "vcd_max_1e6_mL")].iloc[0]
    check("lager strain W-34/70 keeps its peak cell density at 37 °C", abs(l37["pct_change"]) < 10,
          f"{l37["pct_change"]:+.0f} %")
    pre = eff[(eff.perturbation == "3 h vs 24 h pre-culture") & (eff.phenotype == "vcd_max_1e6_mL")]
    check("short 3 h pre-culture lowers peak VCD in both strains",
          (pre["pct_change"] < -30).all() and (pre.p_welch < 0.01).all(), ", ".join(f"{v:.0f} %" for v in pre["pct_change"]))
    check("feed-dependent phenotypes are flagged",
          eff[eff.phenotype == "mu_fedbatch_h"].confounded_by_feed.all())

print(f"\n{sum(res)}/{len(res)} passed"); sys.exit(0 if all(res) else 1)
