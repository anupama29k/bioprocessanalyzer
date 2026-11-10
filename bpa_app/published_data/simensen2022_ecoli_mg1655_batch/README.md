# E. coli K-12 MG1655 — aerobic batch, glucose minimal medium (measured)

**Source:** Simensen V, Schulz C, Karlsen E, Bråtelund S, Burgos I, Thorfinnsdottir LB,
García-Calvo L, Bruheim P, Almaas E (2022). *Experimental determination of Escherichia
coli biomass composition for constraint-based metabolic modeling.* PLOS ONE 17(1):
e0262450. https://doi.org/10.1371/journal.pone.0262450 — Supporting information **S4 File**.

**License:** CC BY 4.0 (PLOS ONE). Values are reproduced unchanged except for the unit
conversions below; please cite the paper when using this data.

## Conditions (from the paper)
3 L Eppendorf BioFlo 115, 1 L modified M9 with 2 % (w/v) glucose, 37 °C, pH 7.0
(4 M NaOH), DO ≥ 40 % via agitation cascade, ~0.5 L/min air, 1 % inoculum. Off-gas by
DASGIP GA4. Metabolites by ¹H-NMR. Cells harvested in exponential phase at ~7.5 h.

**Reported:** μ = 0.71 h⁻¹; 2.6 gDCW/L at sampling; OD→DCW factor 0.5 g/L/OD.

## Files
| File | Contents |
|---|---|
| `sampling_with_offgas.csv` | 7 samples: OD₆₀₀; glucose, acetate, lactate, succinate, formate (original mM and converted g/L); off-gas CER/OUR, DO and pH as the median within ±6 min of each sample |
| `offgas_and_control.csv` | Full ~1-min log: CER, OUR (mmol L⁻¹ h⁻¹), RQ, DO, pH, temperature, agitation, airflow |

## Conversions and caveats
- CER/OUR = reported mmol/min × 60 / 1.0 L working volume; OUR sign flipped to positive = uptake.
- OD was not recorded after 5.25 h (samples at 6.83 and 7.33 h have metabolites only).
- O₂ signal has a baseline offset of ≈0.5–1 mmol L⁻¹ h⁻¹ before inoculation (RQ < 1 early on); it is not corrected here.
- First glucose reading (3.17 h) is 74.5 mM vs ≈111 mM nominal for 2 % glucose — keep this in mind when computing yields.
- After ~7.4 h agitation drops and DO rises: harvest, not a metabolic event.

## Bioprocess Analyzer results (see `validate_published.py`)
| | Value |
|---|---|
| μ from OD (engine, 4-point window 2.05–5.25 h) | 0.768 ± 0.031 h⁻¹, R² 0.997 |
| μ from ln(CER), 3.5–7.2 h | 0.74 h⁻¹ |
| Paper | 0.71 h⁻¹ |
