"""
Bioprocess Atlas data model.

Four tables, all keyed by ``run_id``:

runs          one row per cultivation (a single vessel). Who, what, where, how,
              and which perturbation it carries relative to its reference.
observations  long format: run_id, time_h, variable, value. Units are fixed by
              the variable name (see VARIABLES), so values are comparable
              across datasets without per-dataset unit columns.
phenotypes    one row per run: derived quantities (μ, yields, rates, …) with
              their uncertainty, computed by the Bioprocess Analyzer engine.
effects       one row per (perturbation, phenotype): mean of the perturbed
              runs vs the reference runs of the same campaign, with replicate
              statistics. The bioprocess analogue of a perturbation effect.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

SCHEMA_VERSION = "0.1"

# Controlled vocabulary: variable name → (unit, description). Names carry the unit.
VARIABLES = {
    "od600":           ("OD", "optical density at 600 nm, 1 cm path"),
    "biomass_gL":      ("g/L", "dry cell weight concentration"),
    "glucose_gL":      ("g/L", "glucose in broth"),
    "glycerol_gL":     ("g/L", "glycerol in broth"),
    "acetate_gL":      ("g/L", "acetate in broth"),
    "lactate_gL":      ("g/L", "lactate in broth"),
    "formate_gL":      ("g/L", "formate in broth"),
    "succinate_gL":    ("g/L", "succinate in broth"),
    "ethanol_gL":      ("g/L", "ethanol in broth"),
    "product_gL":      ("g/L", "target product titer"),
    "DO_percent":      ("% air sat.", "dissolved oxygen"),
    "pH":              ("pH", "broth pH"),
    "temperature_C":   ("°C", "broth temperature"),
    "OUR_mmol_Lh":     ("mmol/L/h", "oxygen uptake rate"),
    "CER_mmol_Lh":     ("mmol/L/h", "CO2 evolution rate"),
    "agitation_rpm":   ("rpm", "stirrer speed"),
}

PERTURBATION_TYPES = ("none", "gene_knockout", "strain", "medium", "feed",
                      "temperature", "pH", "DO", "scale", "induction", "other")


@dataclass
class Run:
    run_id: str                  # globally unique: <dataset_id>:<local id>
    dataset_id: str
    organism: str
    strain: str
    mode: str                    # Batch | Fed-batch | Continuous
    vessel: str
    working_volume_L: float | None
    medium: str
    temperature_C: float | None
    pH_setpoint: float | None
    replicate: int               # biological replicate number within its condition
    campaign: str                # runs that share a reference and a run date/platform
    reference_condition: str     # condition id this run is compared against
    condition: str               # condition id (shared by biological replicates)
    perturbation_type: str = "none"
    perturbation: str = ""       # e.g. "ΔaceA", "pH 6.5", "feed ×1.5"
    perturbation_dose: float | None = None   # continuous strength, when meaningful
    is_reference: bool = False
    dcw_per_od: float | None = None
    source_doi: str = ""
    license: str = ""
    notes: str = ""

    def row(self):
        return asdict(self)


@dataclass
class Dataset:
    dataset_id: str
    title: str
    citation: str
    doi: str
    license: str
    measured: bool               # True = real experiment, False = simulated
    runs: list = field(default_factory=list)          # list[Run]
    observations: list = field(default_factory=list)  # (run_id, time_h, variable, value)
