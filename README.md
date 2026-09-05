# Bioprocess Analyzer

Python toolkit and Streamlit apps for fermentation analysis — growth kinetics, elemental mass balance, scale-up modeling, and a digital twin — validated against literature datasets spanning E. coli, B. subtilis, C. glutamicum, K. phaffii/P. pastoris, P. putida, L. lactis, C. necator and CHO.

## What's here

| Path | What it is |
|---|---|
| **`bpa_app/`** | The analyzer. Data import with universal parsing and column mapping; growth kinetics (μ, doubling time, lag, R², Luedeking–Piret); multi-substrate C/H/O/N elemental mass balance with degree-of-reduction checks; scale-up modeling (kLa by van't Riet, mixing time by Nienow, P/V, tip speed, Reynolds); a Monod-ODE digital twin (batch, fed-batch, continuous); run registry, golden-batch comparison, and an AI assistant grounded in the loaded run data. Ships with 30+ literature-derived organism datasets and a validation harness (`test_with_literature.py`, `auto_validate.py`). |
| **`analytical_databank/`** | Structured reference of biotech/biopharma analytical instruments — principle, real industry models, methods by product type (mAbs, vaccines, cell & gene therapy), report contents and acceptance criteria, ICH/USP/EP references. |
| **`synapse.py`** + **`synapse_pages/`** + **`pulse.py`** | SYNAPSE: the unified multi-page platform that merges the analyzer and the databank, adding a run manager, live-run telemetry, batch history and instrument reference. Uses Supabase for persistence (`.env` with `SUPABASE_URL`/`SUPABASE_KEY`; never committed). |
| **`gem-map-builder/`** | Genome-scale-model reaction-map tooling used by the metabolic views. |
| **`sample_data/`** | Small curated E. coli batch/fed-batch datasets for a quick first run. |

## Quick start

```bash
cd bpa_app
pip install -r requirements.txt
streamlit run app.py
```

Everything on this path runs fully offline — load any CSV from `sample_data/` or the organism datasets in `bpa_app/`. To run the full SYNAPSE platform instead: `pip install supabase python-dotenv`, add your Supabase credentials to `.env`, and `streamlit run synapse.py`. Set `ANTHROPIC_API_KEY` to enable the AI assistant.

## Why I built it

I spent nine years developing and scaling fermentation processes, including a 1,000 kg production campaign at a contract manufacturer. This is the analysis layer I always wanted at the bench: the calculations a process scientist actually runs — kinetics, mass balance, scale-down/scale-up criteria — with the sanity checks (elemental closure, thermodynamic yield limits) that catch bad data before it drives a bad decision.

— Anupama Kozhiyalam · [github.com/anupama29k](https://github.com/anupama29k)
