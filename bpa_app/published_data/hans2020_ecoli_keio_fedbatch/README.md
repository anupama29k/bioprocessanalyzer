# E. coli K-12: W3110, BW25113 and six Keio knockouts — 24 parallel fed-batch mini-bioreactors (measured)

**Source:** Hans S, Haby B, Krausch N, Barz T, Neubauer P, Cruz-Bournazou MN (2020).
*Automated Conditional Screening of Multiple Escherichia coli Strains in Parallel Adaptive
Fed-Batch Cultivations.* Bioengineering 7(4):145. https://doi.org/10.3390/bioengineering7040145 —
Supplementary Table S1 (all experimental measurements).

**License:** CC BY 4.0 (MDPI). Values reproduced unchanged except reshaping to long format; please cite the paper.

## Design
8 strains × biological triplicates = 24 runs in a 2mag bioREACTOR 48 on Tecan/Hamilton liquid
handlers, 37 °C, 3000 rpm. Batch on 5 g/L glucose (+5 g/L pulse at 1 h), then 400 g/L glucose pulses
every 5 min; the feed rate was adapted **per strain** by a model, so the fed-batch phase differs in
feed between strains — the batch phase is the like-for-like comparison.

Strains: W3110; BW25113 (Keio parent); BW25113 ΔompT, ΔaceA, ΔfliA, ΔgatC, ΔgatZ, ΔglcB (Keio collection).

## File
`measurements_long.csv` — strain, reactor_replicate (1–3), variable, time_h, value.
Variables: biomass_gL (OD₆₀₀ × 2.62 path correction × 0.33 g/L per OD, as reported), glucose_gL,
acetate_gL (enzymatic assays on a Hamilton Microlab Star), DO_percent (online). Analytical duplicates
appear as repeated rows at the same time.

## Caveats (from the authors' notes)
Nine glucose points at 6.14 and 7.14 h are possible outliers; one W3110 replicate had lower biomass
from oxygen limitation. All data are kept.
