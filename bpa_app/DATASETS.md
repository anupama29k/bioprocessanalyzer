# Dataset provenance

Every CSV bundled in `bpa_app/` and `sample_data/` is **simulated**: a growth
model with parameters set to typical published values, plus added noise. None
is measured data, and none should be cited as experimental. They exist to
exercise the engine across organisms, growth regimes and edge cases.

| Files | Generator | What the "literature" part means |
|---|---|---|
| `test_E_coli_*.csv`, `ALL_LITERATURE_VALIDATION_DATASETS.csv` | `test_with_literature.py --regenerate` | Target μ, lag and max OD taken from the cited paper (column `Literature_Reference`); the curve itself is simulated |
| `*_multiprobe.csv` | `generate_multiprobe_data.py [name]` | Kinetics typical of the cited work; all sensor channels simulated (see `MULTIPROBE_DATASET_README.md`) |
| `standard_ecoli_product.csv`, `fast_growth_product.csv` | `generate_simple.py` | Synthetic only |
| Organism files (`c_glutamicum`, `s_cerevisiae_aerobic`, `cho_mab_2025`, `k_phaffii_methanol`, …) | not in repo | Simulated with organism-typical parameters |
| `sample_data/ecoli_*.csv` | `sample_data/generate_ecoli_data.py` | Synthetic only |

## Regenerating
Generators are seeded, so output is reproducible. Running the validation
scripts **does not** overwrite bundled files; pass `--regenerate` to
`test_with_literature.py`, or name datasets explicitly to
`generate_multiprobe_data.py`.
