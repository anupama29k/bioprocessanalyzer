"""
Dataset ingesters: each turns one published dataset (as stored, unchanged,
under ``published_data/``) into atlas Runs + observations. Adding a dataset =
adding one function here and registering it in INGESTERS.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .schema import Dataset, Run

ROOT = Path(__file__).parent.parent / "published_data"


def simensen2022() -> Dataset:
    d = pd.read_csv(ROOT / "simensen2022_ecoli_mg1655_batch" / "sampling_with_offgas.csv")
    og = pd.read_csv(ROOT / "simensen2022_ecoli_mg1655_batch" / "offgas_and_control.csv")
    ds = Dataset(
        dataset_id="simensen2022",
        title="E. coli MG1655 aerobic batch on glucose M9, 1 L",
        citation="Simensen V et al. (2022) PLOS ONE 17:e0262450",
        doi="10.1371/journal.pone.0262450", license="CC BY 4.0", measured=True)
    rid = "simensen2022:batch1"
    ds.runs.append(Run(
        run_id=rid, dataset_id=ds.dataset_id, organism="Escherichia coli", strain="K-12 MG1655",
        mode="Batch", vessel="Eppendorf BioFlo 115, 3 L", working_volume_L=1.0,
        medium="modified M9, 2% glucose", temperature_C=37.0, pH_setpoint=7.0, replicate=1,
        campaign="simensen2022", reference_condition="MG1655", condition="MG1655",
        is_reference=True, dcw_per_od=0.5, source_doi=ds.doi, license=ds.license,
        notes="OD not recorded after 5.25 h; harvest at ~7.5 h"))
    cols = {"OD_600nm": "od600", "Glucose_gL": "glucose_gL", "Acetate_gL": "acetate_gL",
            "Lactate_gL": "lactate_gL", "Succinate_gL": "succinate_gL", "Formate_gL": "formate_gL"}
    for c, v in cols.items():
        for t, x in zip(d.Time_h, d[c]):
            if pd.notna(x):
                ds.observations.append((rid, float(t), v, float(x)))
    og = og[og.Time_h <= 7.35]   # after this the culture is being harvested
    for c, v in {"CER_mmol_Lh": "CER_mmol_Lh", "OUR_mmol_Lh": "OUR_mmol_Lh",
                 "DO_percent": "DO_percent", "pH": "pH", "Agitation_rpm": "agitation_rpm"}.items():
        for t, x in zip(og.Time_h, og[c]):
            if pd.notna(x):
                ds.observations.append((rid, float(t), v, float(x)))
    return ds


def hans2020() -> Dataset:
    m = pd.read_csv(ROOT / "hans2020_ecoli_keio_fedbatch" / "measurements_long.csv")
    ds = Dataset(
        dataset_id="hans2020",
        title="8 E. coli K-12 strains (Keio knockouts) in 24 parallel fed-batch mini-bioreactors",
        citation="Hans S et al. (2020) Bioengineering 7:145",
        doi="10.3390/bioengineering7040145", license="CC BY 4.0", measured=True)
    ref = "BW25113"
    for (strain, rep), g in m.groupby(["strain", "reactor_replicate"]):
        ko = strain.replace("BW25113 ", "") if strain.startswith("BW25113 Δ") else ""
        ptype = "gene_knockout" if ko else ("none" if strain == ref else "strain")
        rid = f"hans2020:{strain.replace(' ', '_')}:r{rep}"
        ds.runs.append(Run(
            run_id=rid, dataset_id=ds.dataset_id, organism="Escherichia coli", strain=f"K-12 {strain}",
            mode="Fed-batch", vessel="2mag bioREACTOR 48 on Tecan/Hamilton liquid handlers",
            working_volume_L=None,
            medium="defined medium; batch on 5 g/L glucose (+5 g/L pulse at 1 h), then 400 g/L "
                   "glucose pulses every 5 min",
            temperature_C=37.0, pH_setpoint=None, replicate=int(rep), campaign="hans2020",
            reference_condition=ref, condition=strain, perturbation_type=ptype,
            perturbation=ko or (strain if strain != ref else ""), is_reference=(strain == ref),
            dcw_per_od=None, source_doi=ds.doi, license=ds.license,
            notes="3000 rpm; feed rate adapted per strain by the model (fed-batch phase is "
                  "confounded by feed, batch phase is not); biomass = OD × 2.62 path × 0.33 g/L"))
        # analytical duplicates at the same time point are averaged
        gg = g.groupby(["variable", "time_h"], as_index=False)["value"].mean()
        for v, t, x in gg[["variable", "time_h", "value"]].itertuples(index=False):
            ds.observations.append((rid, float(t), v, float(x)))
    return ds


INGESTERS = {"simensen2022": simensen2022, "hans2020": hans2020}
