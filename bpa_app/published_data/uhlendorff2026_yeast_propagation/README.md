# Yeast propagation — S. cerevisiae W-68 and S. pastorianus W-34/70, 52 bioreactor runs (measured)

**Source:** Uhlendorff S, Fulek R, Eimler J, Schneider J, Frahm B, Pein-Hackelbusch M (2026).
*Dataset Based on Inline Monitoring and Offline Analysis of Yeast Cultivations.* Zenodo,
https://doi.org/10.5281/zenodo.19690248 (v1, 2026-09-27). Data descriptor: Preprints.org 202611.0120.
OWL University of Applied Sciences and Arts, Lemgo, Germany.

**License:** CC BY 4.0 (Zenodo record). Values reproduced from the authors' time-aligned CSVs; please cite.

## Design
Brewing-style propagation in wort, 72–76 h, 400 rpm, pH and DO not controlled. 12 experiments × 4
parallel 0.7 L reactors + 4 single 10 L runs. Varied: strain, pre-culture (3 or 24 h), wort (12 or
24 °P), aeration (0.5 or 1 vvm), temperature (22, 30, 37 °C), scale.

## Files here
| File | Contents |
|---|---|
| `conditions.csv` | one row per run: experiment, strain, species, scale, reactor, pre-culture, wort, aeration, temperature (+ logged temperature), initial original gravity |
| `offline_all_runs.csv` | the authors' offline tables for all 52 runs: VCD, TCD, viability, cell diameter (mean ± SEM), density, refractive index, gravities, extract, alcohol, degree of fermentation, energy, osmolality |
| `inline_15min_medians.csv.gz` | 15-min medians of the 30-s inline log: dissolved CO₂, permittivity, conductivity, pH, DO, temperature, agitation (full-resolution files and dielectric spectra are on Zenodo) |

## How conditions were resolved
The design table is partly ambiguous in the descriptor text. Temperature per reactor is taken from the
logged temperature (nearest of 22/30/37 °C): EXP007/008 and EXP011/012 ran R01–R02 at 22 °C and R03–R04
at 37 °C and 30 °C. Wort strength is confirmed by original gravity (~1.053 for 12 °P, ~1.126 for 24 °P).
**Aeration for EXP009/EXP010 could not be resolved from the data** (1 or 0.5 vvm) and is left blank;
those runs are not used in aeration contrasts.

## Caveats
- Target inoculation (15 × 10⁶ viable cells/mL) was not always reached; 3 h pre-cultures of W-68 started near 30 × 10⁶.
- Offline samples fall in a daily ~8 h window, so the exponential phase has ~3 cell counts per run.
- Some DO traces read −1 % (sensor floor); the atlas clips them at 0.
