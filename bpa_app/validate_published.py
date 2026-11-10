"""Validate the kinetics engine against measured, published datasets.

    python validate_published.py

Each entry in published_data/manifest.json names a dataset, the value the
paper reports, and a relative tolerance. Exit code 1 if any check fails.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from modules.calcs import compute_growth_kinetics  # noqa: E402

ROOT = Path(__file__).parent / "published_data"


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    failures = 0
    for name, cfg in manifest.items():
        df = pd.read_csv(ROOT / cfg["file"]).dropna(subset=[cfg["od_col"]])
        r = compute_growth_kinetics(df[cfg["time_col"]].values, df[cfg["od_col"]].values,
                                    dcw_factor=cfg.get("dcw_factor", 0.4))
        exp, tol = cfg["expected"]["mu_max"], cfg["tolerance"]["mu_max"]
        mu = r["mu"]
        err = abs(mu - exp) / exp if mu else float("inf")
        ok = err <= tol
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name}: μ {mu:.3f} ± {r['mu_se']:.3f} h⁻¹ "
              f"(paper {exp:.2f}, error {err:.1%}, tolerance {tol:.0%}) "
              f"doi:{cfg['doi']}")
    print(f"\n{len(manifest) - failures}/{len(manifest)} published datasets within tolerance")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
