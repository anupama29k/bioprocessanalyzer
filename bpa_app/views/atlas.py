"""Bioprocess Atlas — browse runs, perturbation effects and replicate time courses."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# The atlas lives in its own repository; this page only reads its release tables.
ATLAS_REPO = "https://github.com/anupama29k/Bioprocess-Atlas"
REMOTE = "https://raw.githubusercontent.com/anupama29k/bioprocess-atlas/main/release/"
REL = Path(__file__).parent.parent / "atlas_release"   # bundled snapshot, used offline
FILES = ["runs.csv", "observations.csv.gz", "phenotypes.csv", "effects.csv", "datasets.csv",
         "contrasts.csv", "manifest.json"]


def _read(base, remote):
    import json
    import urllib.request
    def get(name):
        return base + name if remote else base / name
    tables = [pd.read_csv(get(f)) for f in FILES[:6]]
    if remote:
        with urllib.request.urlopen(get("manifest.json"), timeout=15) as r:
            man = json.loads(r.read().decode())
    else:
        man = json.loads((base / "manifest.json").read_text())
    return (*tables, man)


@st.cache_data(show_spinner="Loading the atlas release…", ttl=3600)
def _load(source):
    """Latest release from GitHub; falls back to the bundled snapshot."""
    if source == "latest":
        try:
            return (*_read(REMOTE, True), "latest release on GitHub")
        except Exception:
            pass
    return (*_read(REL, False), "bundled snapshot (offline)")


def render():
    st.title("🗺️ Bioprocess Atlas")
    st.caption("Measured cultivations from published studies, one perturbation at a time, "
               "turned into comparable phenotypes")
    latest = st.toggle("Use the latest release from GitHub", value=True,
                       help="Off: use the snapshot bundled with this app (works offline).")
    runs, obs, pheno, eff, dsets, contrasts, man, where = _load("latest" if latest else "bundled")
    st.caption(f"Loaded: {where} · schema v{man['schema_version']} · [atlas repository]({ATLAS_REPO})")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Datasets", man["datasets"])
    c2.metric("Runs", man["runs"])
    c3.metric("Conditions", man["conditions"])
    c4.metric("Observations", f"{man['observations']:,}")

    tab_eff, tab_runs, tab_data = st.tabs(["Perturbation effects", "Time courses", "Datasets & runs"])

    with tab_eff:
        e = eff[~eff.confounded_by_feed].copy()
        if e.empty:
            st.info("No perturbation campaigns with replicates yet.")
        else:
            camp = st.selectbox("Campaign", sorted(e.campaign.unique()))
            e = e[e.campaign == camp]
            refs_ = e.reference.unique()
            ref = refs_[0] if len(refs_) == 1 else "its reference"
            st.caption(f"Each cell: effect size d = (perturbed − {ref}) / pooled SD; colour needs ≥ 2 runs "
                       "per arm, the % change is shown either way. Only phenotypes measured under the same "
                       "conditions are compared; • p < 0.05, ◦ p < 0.15 (Welch t-test).")
            piv = e.pivot(index="perturbation", columns="phenotype", values="effect_size_d")
            pv = e.pivot(index="perturbation", columns="phenotype", values="p_welch")
            pct = e.pivot(index="perturbation", columns="phenotype", values="pct_change")
            txt = [[(f"{pct.loc[r, c]:+.0f}%" + (" •" if pv.loc[r, c] < 0.05 else " ◦" if pv.loc[r, c] < 0.15 else ""))
                    if pd.notna(piv.loc[r, c]) else "" for c in piv.columns] for r in piv.index]
            lim = float(np.nanpercentile(np.abs(piv.values), 90)) if np.isfinite(piv.values).any() else 1
            fig = go.Figure(go.Heatmap(
                z=piv.values, x=list(piv.columns), y=list(piv.index), text=txt, texttemplate="%{text}",
                colorscale="RdBu", zmid=0, zmin=-lim, zmax=lim, colorbar=dict(title="d"),
                hovertemplate="%{y} · %{x}<br>d = %{z:.2f}<br>%{text}<extra></extra>"))
            fig.update_layout(height=60 + 44 * len(piv), margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, width="stretch")
            for ph_name, grp in e[e.perturbation_type == "gene_knockout"].groupby("phenotype"):
                chg = grp["pct_change"].dropna()
                sig = (grp["p_welch"] < 0.05).mean()
                if len(chg) >= 4 and sig >= 0.75 and (np.sign(chg).nunique() == 1):
                    lo_, hi_ = chg.min(), chg.max()
                    st.warning(f"Every knockout shifts {ph_name} the same direction ({lo_:+.0f} to {hi_:+.0f} %), most of them significantly. "
                               "A uniform shift across unrelated genes points to something they share "
                               "(e.g. the Keio kanamycin cassette, plate position or assay batch) rather "
                               "than gene function.")
            st.dataframe(e[["perturbation", "phenotype", "unit", "mean", "sd", "ref_mean", "ref_sd",
                            "n", "ref_n", "pct_change", "effect_size_d", "p_welch"]].round(3),
                         hide_index=True, width="stretch")

    with tab_runs:
        r = runs.copy()
        dsid = st.selectbox("Dataset", sorted(r.dataset_id.unique()), key="atl_camp",
                            format_func=lambda d: dsets.set_index("dataset_id").title.get(d, d))
        r = r[r.dataset_id == dsid]
        conds = sorted(r.condition.unique())
        refs = [c for c in conds if c in set(r[r.is_reference].condition)]
        others = [c for c in conds if c not in refs]
        default = (refs[:1] + others[:1]) or conds[:2]
        if len(contrasts):
            cc = contrasts[contrasts.dataset_id == dsid] if "dataset_id" in contrasts else contrasts.iloc[:0]
            if len(cc):
                first = cc.iloc[0]
                pair = [r.set_index("run_id").condition.get(first.reference_runs.split(";")[0]),
                        r.set_index("run_id").condition.get(first.runs.split(";")[0])]
                if all(p in conds for p in pair):
                    default = pair
        pick = st.multiselect("Conditions", conds, default=default)
        vars_ = sorted(obs[obs.run_id.isin(r.run_id)].variable.unique())
        var = st.selectbox("Variable", vars_, index=vars_.index("biomass_gL") if "biomass_gL" in vars_ else 0)
        fig = go.Figure()
        palette = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#be185d", "#4d7c0f"]
        for i, c in enumerate(pick):
            for j, rid in enumerate(r[r.condition == c].run_id):
                s = obs[(obs.run_id == rid) & (obs.variable == var)].sort_values("time_h")
                mode = "lines" if len(s) > 200 else "lines+markers"
                fig.add_trace(go.Scatter(x=s.time_h, y=s.value, mode=mode, name=c,
                                         legendgroup=c, showlegend=(j == 0),
                                         line=dict(color=palette[i % 8], width=1.2),
                                         marker=dict(size=5), opacity=0.85))
        fig.update_layout(height=420, xaxis_title="time (h)", yaxis_title=f"{var} ({man['variables'][var]['unit']})",
                          margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, width="stretch")
        st.caption("Each line is one bioreactor (biological replicate). Analytical duplicates are averaged.")
        ph = r[["run_id", "condition", "replicate"]].merge(pheno, on="run_id")
        st.dataframe(ph[ph.condition.isin(pick)].round(3), hide_index=True, width="stretch")

    with tab_data:
        st.dataframe(dsets.assign(doi=lambda d: "https://doi.org/" + d.doi), hide_index=True, width="stretch",
                     column_config={"doi": st.column_config.LinkColumn("DOI")})
        st.dataframe(runs, hide_index=True, width="stretch")
        st.markdown("**Phenotype definitions**")
        st.dataframe(pd.DataFrame([{"phenotype": k, **v} for k, v in man["phenotypes"].items()]),
                     hide_index=True, width="stretch")
        st.caption(f"Schema v{man['schema_version']} · observations checksum {man['observations_sha256_16']} · "
                   f"engine {man.get('engine', '?')} · built in the [bioprocess-atlas repository]({ATLAS_REPO})")
