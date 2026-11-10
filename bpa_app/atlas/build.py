"""
Build the Bioprocess Atlas release from the ingested datasets.

    python -m atlas.build            (from bpa_app/)

Writes atlas_release/: runs.csv, observations.csv.gz, phenotypes.csv,
effects.csv, datasets.csv and manifest.json. Every table is regenerated from
published_data/, so a release is reproducible from the repo alone.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from .ingest import INGESTERS
from .phenotypes import PHENOTYPES, effects, run_phenotypes
from .schema import SCHEMA_VERSION, VARIABLES

OUT = Path(__file__).parent.parent / "atlas_release"


def build(datasets=None, out: Path = OUT) -> dict:
    runs, obs, meta, contrasts = [], [], [], []
    for name in datasets or INGESTERS:
        ds = INGESTERS[name]()
        unknown = {o[2] for o in ds.observations} - set(VARIABLES)
        if unknown:
            raise ValueError(f"{name}: variables outside the vocabulary: {sorted(unknown)}")
        runs += [r.row() for r in ds.runs]
        obs += ds.observations
        contrasts += [{**c, "dataset_id": ds.dataset_id} for c in ds.contrasts]
        meta.append({"dataset_id": ds.dataset_id, "title": ds.title, "citation": ds.citation,
                     "doi": ds.doi, "license": ds.license, "measured": ds.measured,
                     "n_runs": len(ds.runs), "n_observations": len(ds.observations)})
    runs = pd.DataFrame(runs)
    obs = pd.DataFrame(obs, columns=["run_id", "time_h", "variable", "value"])
    by_run = dict(tuple(obs.groupby("run_id")))
    pheno = pd.DataFrame([run_phenotypes(r, by_run.get(r["run_id"], obs.iloc[:0]))
                          for r in runs.to_dict("records")])
    eff = effects(runs, pheno, contrasts)

    out.mkdir(exist_ok=True)
    runs.to_csv(out / "runs.csv", index=False)
    obs.to_csv(out / "observations.csv.gz", index=False, compression="gzip")
    pheno.to_csv(out / "phenotypes.csv", index=False)
    eff.to_csv(out / "effects.csv", index=False)
    pd.DataFrame(meta).to_csv(out / "datasets.csv", index=False)
    pd.DataFrame([{**{k: v for k, v in c.items() if k not in ("runs", "reference_runs")},
                   "runs": ";".join(c["runs"]), "reference_runs": ";".join(c["reference_runs"])}
                  for c in contrasts]).to_csv(out / "contrasts.csv", index=False)
    digest = hashlib.sha256(pd.util.hash_pandas_object(obs, index=False).values.tobytes()).hexdigest()[:16]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "datasets": len(meta), "runs": len(runs), "observations": len(obs),
        "conditions": int(runs.condition.nunique()),
        "contrasts": len(contrasts),
        "organisms": sorted(runs.organism.unique().tolist()),
        "perturbations": int((~runs.is_reference).groupby(runs.condition).first().sum()),
        "observations_sha256_16": digest,
        "variables": {k: {"unit": u, "description": d} for k, (u, d) in VARIABLES.items()},
        "phenotypes": {k: {"unit": u, "description": d, "confounded_by_feed": c}
                       for k, (u, d, c) in PHENOTYPES.items()},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return {"runs": runs, "observations": obs, "phenotypes": pheno, "effects": eff,
            "datasets": pd.DataFrame(meta), "manifest": manifest}


if __name__ == "__main__":
    r = build()
    m = r["manifest"]
    print(f"Atlas v{m['schema_version']}: {m['datasets']} datasets, {m['runs']} runs, "
          f"{m['conditions']} conditions, {m['contrasts']} explicit contrasts, "
          f"{len(m['organisms'])} organisms, {m['observations']:,} observations")
    e = r["effects"]
    if len(e):
        sig = e[(e.p_welch < 0.05) & ~e.confounded_by_feed].sort_values("p_welch")
        print(f"{len(sig)} batch-phase effects with p < 0.05:")
        print(sig[["perturbation", "phenotype", "mean", "ref_mean", "pct_change", "p_welch"]]
              .round(3).to_string(index=False))
