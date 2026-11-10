# Published (measured) datasets

Real fermentation data from open-access papers, each in its own folder with the
citation, license, conditions, unit conversions and known caveats. These are the
datasets to quote when describing validation; the CSVs elsewhere in `bpa_app/`
are simulated.

| Dataset | Organism / mode | Measured | Source |
|---|---|---|---|
| [`hans2020_ecoli_keio_fedbatch`](hans2020_ecoli_keio_fedbatch/) | 8 E. coli K-12 strains (6 Keio knockouts) × 3, parallel fed-batch, mL scale | biomass, glucose, acetate, DO | Hans et al. 2020, Bioengineering, [doi:10.3390/bioengineering7040145](https://doi.org/10.3390/bioengineering7040145) (CC BY 4.0) |
| [`simensen2022_ecoli_mg1655_batch`](simensen2022_ecoli_mg1655_batch/) | E. coli K-12 MG1655, aerobic batch, glucose M9, 1 L | OD, glucose, acetate, lactate, succinate, formate, CER/OUR, DO, pH | Simensen et al. 2022, PLOS ONE, [doi:10.1371/journal.pone.0262450](https://doi.org/10.1371/journal.pone.0262450) (CC BY 4.0) |

`python validate_published.py` checks the engine against the value each paper reports
(`manifest.json`). To add a dataset: create a folder with the data and a README,
then add an entry to `manifest.json`.
