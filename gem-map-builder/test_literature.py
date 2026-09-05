"""
test_literature.py -- 32 Literature-Referenced Bioprocess Datasets
Written by: Anu Kozhiyalam
Purpose: Validates gem_map.py against published experimental data from
         peer-reviewed bioprocess literature across all 10 organisms.
         Each dataset includes citation, culture phase, and real readings.
"""

from gem_map import get_all_pathway_states, list_organisms

# ═══════════════════════════════════════════════════════════════════════════
#  32 LITERATURE DATASETS
# ═══════════════════════════════════════════════════════════════════════════

LITERATURE_DATASETS = [

    # ── CHO fed-batch mAb (8 datasets) ────────────────────────────────────

    {
        "id": 1,
        "organism": "CHO",
        "citation": "Xu et al. 2011 Biotechnol Bioeng",
        "context": "CHO fed-batch mAb -- Day 7 peak",
        "readings": {
            "VCD": 12.0, "viability": 92.0, "glucose": 2.1, "lactate": 3.2,
            "ammonia": 4.1, "pH": 7.05, "DO": 35.0, "titer": 2.8,
            "temperature": 37.0, "agitation": 180.0,
        }
    },
    {
        "id": 2,
        "organism": "CHO",
        "citation": "Jiang et al. 2018 Biotechnol Prog",
        "context": "CHO fed-batch mAb -- Day 10 declining",
        "readings": {
            "VCD": 8.0, "viability": 78.0, "glucose": 1.4, "lactate": 4.8,
            "ammonia": 6.2, "pH": 6.92, "DO": 22.0, "titer": 3.1,
            "temperature": 37.0, "agitation": 180.0,
        }
    },
    {
        "id": 3,
        "organism": "CHO",
        "citation": "Reinhart et al. 2019 Biotechnol J",
        "context": "CHO fed-batch -- Day 5 optimal",
        "readings": {
            "VCD": 9.0, "viability": 96.0, "glucose": 3.8, "lactate": 1.1,
            "ammonia": 2.8, "pH": 7.18, "DO": 48.0, "titer": 1.2,
            "temperature": 37.0, "agitation": 200.0,
        }
    },
    {
        "id": 4,
        "organism": "CHO",
        "citation": "Huang et al. 2010 Biotechnol Bioeng",
        "context": "CHO high density",
        "readings": {
            "VCD": 22.0, "viability": 88.0, "glucose": 2.8, "lactate": 2.9,
            "ammonia": 5.1, "pH": 7.08, "DO": 30.0, "titer": 4.2,
            "temperature": 37.0, "agitation": 220.0,
        }
    },
    {
        "id": 5,
        "organism": "CHO",
        "citation": "Torkashvand et al. 2015 Iran Biomed J",
        "context": "CHO mAb low producer",
        "readings": {
            "VCD": 6.0, "viability": 85.0, "glucose": 3.2, "lactate": 1.8,
            "ammonia": 3.4, "pH": 7.12, "DO": 42.0, "titer": 0.6,
            "temperature": 37.0, "agitation": 160.0,
        }
    },
    {
        "id": 6,
        "organism": "CHO",
        "citation": "Li et al. 2010 MAbs",
        "context": "CHO fed-batch day 12",
        "readings": {
            "VCD": 5.0, "viability": 71.0, "glucose": 0.8, "lactate": 5.1,
            "ammonia": 7.8, "pH": 6.88, "DO": 18.0, "titer": 3.8,
            "temperature": 37.0, "agitation": 180.0,
        }
    },
    {
        "id": 7,
        "organism": "CHO",
        "citation": "Nienow et al. 2013 Biochem Eng J",
        "context": "CHO scale-up 200L",
        "readings": {
            "VCD": 10.0, "viability": 91.0, "glucose": 2.4, "lactate": 2.1,
            "ammonia": 3.9, "pH": 7.1, "DO": 38.0, "titer": 2.1,
            "temperature": 37.0, "agitation": 150.0,
        }
    },
    {
        "id": 8,
        "organism": "CHO",
        "citation": "Gagnon et al. 2018 Biotechnol Bioeng",
        "context": "CHO temperature shift",
        "readings": {
            "VCD": 14.0, "viability": 94.0, "glucose": 2.9, "lactate": 1.6,
            "ammonia": 3.1, "pH": 7.15, "DO": 45.0, "titer": 3.6,
            "temperature": 33.0, "agitation": 200.0,
        }
    },

    # ── CHO-S perfusion (3 datasets) ──────────────────────────────────────

    {
        "id": 9,
        "organism": "CHO-S",
        "citation": "Clincke et al. 2013 Biotechnol Prog",
        "context": "CHO-S perfusion steady state",
        "readings": {
            "VCD": 80.0, "viability": 95.0, "glucose": 3.5, "lactate": 0.9,
            "ammonia": 2.1, "pH": 7.2, "DO": 50.0, "titer": 0.8,
            "temperature": 36.5, "agitation": 250.0,
        }
    },
    {
        "id": 10,
        "organism": "CHO-S",
        "citation": "Pohlscheidt et al. 2013 Biotechnol Prog",
        "context": "CHO-S perfusion high density",
        "readings": {
            "VCD": 120.0, "viability": 92.0, "glucose": 2.8, "lactate": 1.2,
            "ammonia": 2.8, "pH": 7.18, "DO": 45.0, "titer": 1.1,
            "temperature": 36.5, "agitation": 280.0,
        }
    },
    {
        "id": 11,
        "organism": "CHO-S",
        "citation": "Bielser et al. 2018 Biotechnol Adv",
        "context": "CHO-S perfusion bleed optimization",
        "readings": {
            "VCD": 95.0, "viability": 89.0, "glucose": 3.1, "lactate": 1.4,
            "ammonia": 3.2, "pH": 7.15, "DO": 42.0, "titer": 0.9,
            "temperature": 36.5, "agitation": 260.0,
        }
    },

    # ── HEK293 AAV (3 datasets) ──────────────────────────────────────────

    {
        "id": 12,
        "organism": "HEK293",
        "citation": "Grieger et al. 2016 Nat Protoc",
        "context": "HEK293 AAV2 transient",
        "titer_unit": "vg/mL",
        "readings": {
            "VCD": 8.0, "viability": 88.0, "glucose": 2.1, "lactate": 3.8,
            "ammonia": 4.2, "pH": 7.05, "DO": 35.0, "titer": 1e10,
            "temperature": 37.0, "agitation": 130.0,
        }
    },
    {
        "id": 13,
        "organism": "HEK293",
        "citation": "Blessing et al. 2019 Mol Ther",
        "context": "HEK293 AAV8 suspension",
        "titer_unit": "vg/mL",
        "readings": {
            "VCD": 10.0, "viability": 82.0, "glucose": 1.8, "lactate": 4.1,
            "ammonia": 5.1, "pH": 6.98, "DO": 28.0, "titer": 2.4e11,
            "temperature": 37.0, "agitation": 140.0,
        }
    },
    {
        "id": 14,
        "organism": "HEK293",
        "citation": "Naso et al. 2017 BioDrugs",
        "context": "HEK293 AAV production stress",
        "titer_unit": "vg/mL",
        "readings": {
            "VCD": 6.0, "viability": 74.0, "glucose": 1.2, "lactate": 5.2,
            "ammonia": 6.8, "pH": 6.91, "DO": 20.0, "titer": 8e10,
            "temperature": 37.0, "agitation": 120.0,
        }
    },

    # ── E. coli recombinant protein (5 datasets) ─────────────────────────

    {
        "id": 15,
        "organism": "E. coli",
        "citation": "Shiloach & Fass 2005 Biotechnol Adv",
        "context": "E. coli fed-batch optimal",
        "readings": {
            "OD600": 45.0, "glucose": 2.2, "acetate": 0.8, "ammonia": 18.0,
            "pH": 7.0, "DO": 35.0, "temperature": 37.0, "agitation": 500.0,
            "titer": 2.1,
        }
    },
    {
        "id": 16,
        "organism": "E. coli",
        "citation": "Korz et al. 1995 J Biotechnol",
        "context": "E. coli high density",
        "titer_context": "biomass_dcw_g_per_L",
        "readings": {
            "OD600": 85.0, "glucose": 1.8, "acetate": 2.1, "ammonia": 22.0,
            "pH": 6.95, "DO": 28.0, "temperature": 37.0, "agitation": 600.0,
            "titer": 3.8,
        }
    },
    {
        "id": 17,
        "organism": "E. coli",
        "citation": "Lee 1996 Trends Biotechnol",
        "context": "E. coli acetate overflow",
        "readings": {
            "OD600": 38.0, "glucose": 4.2, "acetate": 5.8, "ammonia": 15.0,
            "pH": 6.88, "DO": 22.0, "temperature": 37.0, "agitation": 450.0,
            "titer": 1.2,
        }
    },
    {
        "id": 18,
        "organism": "E. coli",
        "citation": "Riesenberg et al. 1991 J Biotechnol",
        "context": "E. coli HCDC",
        "readings": {
            "OD600": 148.0, "glucose": 1.1, "acetate": 1.4, "ammonia": 28.0,
            "pH": 6.9, "DO": 25.0, "temperature": 37.0, "agitation": 700.0,
            "titer": 8.2,
        }
    },
    {
        "id": 19,
        "organism": "E. coli",
        "citation": "Yee & Blanch 1992 Biotechnol Bioeng",
        "context": "E. coli inclusion body",
        "readings": {
            "OD600": 52.0, "glucose": 2.8, "acetate": 3.2, "ammonia": 19.0,
            "pH": 6.92, "DO": 30.0, "temperature": 42.0, "agitation": 520.0,
            "titer": 4.1,
        }
    },

    # ── Pichia pastoris (3 datasets) ─────────────────────────────────────

    {
        "id": 20,
        "organism": "P. pastoris",
        "citation": "Cos et al. 2006 Biotechnol Bioeng",
        "context": "Pichia methanol fed-batch",
        "readings": {
            "OD600": 180.0, "glucose": 0.1, "methanol": 3.2, "ammonia": 8.2,
            "pH": 5.8, "DO": 28.0, "temperature": 30.0, "agitation": 600.0,
            "titer": 1.8,
        }
    },
    {
        "id": 21,
        "organism": "P. pastoris",
        "citation": "Looser et al. 2015 Biotechnol Adv",
        "context": "Pichia mixed feed",
        "readings": {
            "OD600": 220.0, "glucose": 0.2, "methanol": 2.1, "ammonia": 9.1,
            "pH": 5.9, "DO": 32.0, "temperature": 28.0, "agitation": 580.0,
            "titer": 3.2,
        }
    },
    {
        "id": 22,
        "organism": "P. pastoris",
        "citation": "Potvin et al. 2012 Biotechnol Adv",
        "context": "Pichia oxygen limited",
        "readings": {
            "OD600": 160.0, "glucose": 0.3, "methanol": 1.8, "ammonia": 7.4,
            "pH": 5.75, "DO": 15.0, "temperature": 30.0, "agitation": 550.0,
            "titer": 1.1,
        }
    },

    # ── S. cerevisiae VLP (2 datasets) ───────────────────────────────────

    {
        "id": 23,
        "organism": "S. cerevisiae",
        "citation": "Ferreira et al. 2012 Vaccine",
        "context": "S. cerevisiae HBsAg",
        "readings": {
            "OD600": 28.0, "glucose": 1.8, "ethanol": 4.2, "ammonia": 12.0,
            "pH": 5.5, "DO": 35.0, "temperature": 30.0, "agitation": 400.0,
            "titer": 0.8,
        }
    },
    {
        "id": 24,
        "organism": "S. cerevisiae",
        "citation": "Castan et al. 2002 Biotechnol Bioeng",
        "context": "S. cerevisiae fed-batch",
        "readings": {
            "OD600": 42.0, "glucose": 0.8, "ethanol": 2.1, "ammonia": 15.0,
            "pH": 5.4, "DO": 28.0, "temperature": 28.0, "agitation": 380.0,
            "titer": 1.4,
        }
    },

    # ── NS0 mAb (2 datasets) ────────────────────────────────────────────

    {
        "id": 25,
        "organism": "NS0",
        "citation": "Mostafa & Gu 2003 Biotechnol Prog",
        "context": "NS0 fed-batch",
        "readings": {
            "VCD": 4.0, "viability": 88.0, "glucose": 2.8, "lactate": 1.9,
            "ammonia": 3.8, "pH": 7.1, "DO": 40.0, "titer": 1.1,
            "temperature": 37.0, "agitation": 150.0,
        }
    },
    {
        "id": 26,
        "organism": "NS0",
        "citation": "Schneider et al. 1996 J Biotechnol",
        "context": "NS0 glutamine depleted",
        "readings": {
            "VCD": 2.0, "viability": 68.0, "glucose": 3.1, "lactate": 2.8,
            "ammonia": 8.2, "pH": 6.95, "DO": 32.0, "titer": 0.4,
            "temperature": 37.0, "agitation": 140.0,
        }
    },

    # ── BHK-21 vaccine (2 datasets) ─────────────────────────────────────

    {
        "id": 27,
        "organism": "BHK-21",
        "citation": "Merten et al. 1994 Cytotechnology",
        "context": "BHK-21 FMDV",
        "titer_unit": "log10_TCID50_per_mL",
        "readings": {
            "VCD": 3.0, "viability": 91.0, "glucose": 3.2, "lactate": 2.1,
            "ammonia": 2.8, "pH": 7.15, "DO": 45.0, "titer": 7.2,
            "temperature": 37.0, "agitation": 120.0,
        }
    },
    {
        "id": 28,
        "organism": "BHK-21",
        "citation": "Telling & Elsworth 1965 Biotechnol Bioeng",
        "context": "BHK-21 suspension classic",
        "readings": {
            "VCD": 2.0, "viability": 94.0, "glucose": 4.1, "lactate": 1.2,
            "ammonia": 1.8, "pH": 7.2, "DO": 50.0, "titer": 4.8,
            "temperature": 37.0, "agitation": 100.0,
        }
    },

    # ── B. subtilis enzyme (2 datasets) ─────────────────────────────────

    {
        "id": 29,
        "organism": "B. subtilis",
        "citation": "Hahne et al. 2010 J Proteome Res",
        "context": "B. subtilis secretion",
        "readings": {
            "OD600": 32.0, "glucose": 1.8, "acetoin": 1.2, "ammonia": 14.0,
            "pH": 7.0, "DO": 38.0, "temperature": 37.0, "agitation": 450.0,
            "titer": 2.1,
        }
    },
    {
        "id": 30,
        "organism": "B. subtilis",
        "citation": "Westers et al. 2004 Biochim Biophys Acta",
        "context": "B. subtilis stress",
        "readings": {
            "OD600": 18.0, "glucose": 0.8, "acetoin": 3.8, "ammonia": 22.0,
            "pH": 6.88, "DO": 20.0, "temperature": 42.0, "agitation": 500.0,
            "titer": 0.6,
        }
    },

    # ── Sp2/0 hybridoma (2 datasets) ────────────────────────────────────

    {
        "id": 31,
        "organism": "Sp2/0",
        "citation": "Ljunggren & Haggstrom 1994 Biotechnol Bioeng",
        "context": "Sp2/0 fed-batch",
        "readings": {
            "VCD": 3.5, "viability": 86.0, "glucose": 2.1, "lactate": 2.8,
            "ammonia": 4.2, "pH": 7.08, "DO": 38.0, "titer": 0.8,
            "temperature": 37.0, "agitation": 130.0,
        }
    },
    {
        "id": 32,
        "organism": "Sp2/0",
        "citation": "Europa et al. 2000 Biotechnol Bioeng",
        "context": "Sp2/0 glutamine effect",
        "readings": {
            "VCD": 2.8, "viability": 79.0, "glucose": 2.4, "lactate": 3.1,
            "ammonia": 6.8, "pH": 6.98, "DO": 32.0, "titer": 0.5,
            "temperature": 37.0, "agitation": 120.0,
        }
    },
]


# ═══════════════════════════════════════════════════════════════════════════
#  SEVERITY HELPERS
# ═══════════════════════════════════════════════════════════════════════════

CRITICAL_STATES = {
    "critical", "toxic", "inhibitory", "lysis", "autolysis",
}
WARNING_STATES = {
    "acidosis", "acidic", "very_acidic", "above_optimum", "hypoxic", "microaerobic", "anaerobic",
    "heat_shock", "heat_stress", "overflow_risk", "overflow",
    "crabtree_overflow", "flux_limited", "carbon_starved", "carbon_limited",
    "depleted", "nitrogen_limited", "oxygen_depleted", "high_OUR",
    "hypercapnia", "high_respiration", "high_fermentation",
    "shear_risk", "foam_risk", "poor_mixing",
    "low_production", "low_expression", "slow_growth", "lag_or_slow",
    "low_density", "below_setpoint", "sub_induction", "overgrown",
    "alkalosis", "alkaline", "neutral_high", "high_for_yeast",
    "moderate", "moderate_stress", "cold_shift", "reduced_temp",
    "excess", "low_demand", "low_metabolism", "low_respiration",
    "high_shear", "extreme",
}


def classify(state_name):
    if state_name in CRITICAL_STATES:
        return "CRITICAL"
    if state_name in WARNING_STATES:
        return "WARNING"
    return "OK"


def health_score(states):
    if not states:
        return 100
    HIGH_IMPACT = {"glucose", "DO", "ammonia", "OD600", "VCD"}
    SEVERE_WARNINGS = {
        "flux_limited", "carbon_starved", "carbon_limited", "depleted",
        "hypoxic", "microaerobic", "anaerobic",
        "nitrogen_limited", "toxic",
        "slow_growth", "lag_or_slow", "low_density", "below_setpoint",
        "acidosis", "acidic", "very_acidic",
        "heat_shock", "heat_stress",
        "oxygen_depleted", "high_OUR",
        "poor_mixing", "shear_risk",
    }
    total = len(states)
    n_crit = 0
    base_sum = 0
    deductions = 0
    for param, info in states.items():
        sev = classify(info["state"])
        is_high = param in HIGH_IMPACT
        state_name = info["state"]
        if sev == "CRITICAL":
            base_sum += 0
            n_crit += 1
            if is_high:
                deductions += 20
        elif sev == "WARNING":
            base_sum += 40
            if is_high and state_name in SEVERE_WARNINGS:
                deductions += 15
                if param == "glucose" and state_name in ("flux_limited", "carbon_starved", "depleted"):
                    deductions += 15
                elif param == "DO" and state_name in ("hypoxic", "microaerobic", "anaerobic"):
                    deductions += 10
        else:
            base_sum += 100
    base = base_sum / total if total > 0 else 100
    score = base - deductions
    penalty = 0.75 ** n_crit if n_crit > 0 else 1.0
    return max(0, int(score * penalty))


def top_concern(states):
    for sev in ("CRITICAL", "WARNING"):
        for param, info in states.items():
            if classify(info["state"]) == sev:
                return param, info["state"], info["meaning"]
    return "-", "-", "All nominal"


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("")
    print("=" * 140)
    print("  LITERATURE VALIDATION -- 32 Peer-Reviewed Bioprocess Datasets")
    print("  Organisms covered:", ", ".join(list_organisms()))
    print("=" * 140)

    # ── Per-dataset detailed report ──────────────────────────────────────
    all_results = []

    for ds in LITERATURE_DATASETS:
        states = get_all_pathway_states(ds["readings"], organism=ds["organism"])
        c = sum(1 for i in states.values() if classify(i["state"]) == "CRITICAL")
        w = sum(1 for i in states.values() if classify(i["state"]) == "WARNING")
        o = len(states) - c - w
        score = health_score(states)
        tp, ts, tm = top_concern(states)

        all_results.append({
            "ds": ds,
            "states": states,
            "critical": c,
            "warning": w,
            "ok": o,
            "score": score,
            "top_param": tp,
            "top_state": ts,
            "top_meaning": tm,
        })

    # ── Summary table ────────────────────────────────────────────────────
    print(f"\n  {'#':<4} {'Organism':<15} {'Citation':<45} {'C':>3} {'W':>3} {'OK':>3} {'Score':>5}  {'Top Concern'}")
    print(f"  {'-'*4} {'-'*15} {'-'*45} {'-'*3} {'-'*3} {'-'*3} {'-'*5}  {'-'*50}")

    for r in all_results:
        ds = r["ds"]
        cite_short = ds["citation"][:43]
        meaning_short = r["top_meaning"][:48] + ".." if len(r["top_meaning"]) > 50 else r["top_meaning"]
        score_str = f"{r['score']:>3}/100"
        print(
            f"  {ds['id']:<4} {ds['organism']:<15} {cite_short:<45} "
            f"{r['critical']:>3} {r['warning']:>3} {r['ok']:>3} {score_str}  "
            f"{r['top_param']}: {meaning_short}"
        )

    # ── Per-organism summary ─────────────────────────────────────────────
    print(f"\n{'=' * 140}")
    print("  PER-ORGANISM SUMMARY")
    print(f"{'=' * 140}")

    org_stats = {}
    for r in all_results:
        org = r["ds"]["organism"]
        if org not in org_stats:
            org_stats[org] = {"count": 0, "scores": [], "criticals": 0, "warnings": 0, "oks": 0}
        org_stats[org]["count"] += 1
        org_stats[org]["scores"].append(r["score"])
        org_stats[org]["criticals"] += r["critical"]
        org_stats[org]["warnings"] += r["warning"]
        org_stats[org]["oks"] += r["ok"]

    print(f"\n  {'Organism':<16} {'Datasets':>8} {'Avg Score':>10} {'Total C':>8} {'Total W':>8} {'Total OK':>8}")
    print(f"  {'-'*16} {'-'*8} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")

    for org, stats in org_stats.items():
        avg = sum(stats["scores"]) / len(stats["scores"])
        print(
            f"  {org:<16} {stats['count']:>8} {avg:>9.1f} "
            f"{stats['criticals']:>8} {stats['warnings']:>8} {stats['oks']:>8}"
        )

    # ── Detailed breakdown for each dataset ──────────────────────────────
    print(f"\n{'=' * 140}")
    print("  DETAILED PARAMETER STATES PER DATASET")
    print(f"{'=' * 140}")

    for r in all_results:
        ds = r["ds"]
        print(f"\n  [{ds['id']}] {ds['citation']}")
        print(f"      Context: {ds['context']}")
        print(f"      Score: {r['score']}/100 | Critical: {r['critical']} | Warning: {r['warning']} | OK: {r['ok']}")

        for param, info in r["states"].items():
            sev = classify(info["state"])
            marker = "!!!" if sev == "CRITICAL" else ("! " if sev == "WARNING" else "   ")
            unit = info["unit"] if info["unit"] else ""
            val_str = f"{info['value']:.4g}" if isinstance(info["value"], float) else str(info["value"])
            meaning_short = info["meaning"][:80] + ".." if len(info["meaning"]) > 82 else info["meaning"]
            print(
                f"      {marker} {param:<13} = {val_str:>8} {unit:<6}  "
                f"[{info['state']:<16}] {info['pathway'][:35]:<35}  {meaning_short}"
            )

    # ── Final validation verdict ─────────────────────────────────────────
    print(f"\n{'=' * 140}")
    print("  LITERATURE VALIDATION VERDICT")
    print(f"{'=' * 140}")

    total_datasets = len(all_results)
    total_params = sum(len(r["states"]) for r in all_results)
    total_crit = sum(r["critical"] for r in all_results)
    total_warn = sum(r["warning"] for r in all_results)
    total_ok = total_params - total_crit - total_warn
    avg_score = sum(r["score"] for r in all_results) / total_datasets
    orgs_tested = len(org_stats)

    # Check: stressed cultures should have warnings/criticals, healthy should be mostly OK
    healthy_datasets = [r for r in all_results if r["score"] >= 75]
    stressed_datasets = [r for r in all_results if r["score"] < 75]

    print(f"\n  Datasets validated:    {total_datasets}")
    print(f"  Organisms covered:     {orgs_tested}")
    print(f"  Total parameters:      {total_params}")
    print(f"  Total CRITICAL:        {total_crit}")
    print(f"  Total WARNING:         {total_warn}")
    print(f"  Total OK:              {total_ok}")
    print(f"  Average health score:  {avg_score:.1f}/100")
    print(f"  Healthy cultures:      {len(healthy_datasets)} (score >= 75)")
    print(f"  Stressed cultures:     {len(stressed_datasets)} (score < 75)")

    # Biological plausibility checks
    checks_passed = 0
    checks_total = 0

    # Check 1: Day 12 CHO (Li et al.) should have critical lactate and toxic ammonia
    checks_total += 1
    li_result = all_results[5]  # dataset #6, index 5
    li_lactate = li_result["states"].get("lactate", {}).get("state", "")
    li_ammonia = li_result["states"].get("ammonia", {}).get("state", "")
    if li_lactate == "critical" and li_ammonia == "toxic":
        checks_passed += 1
        print(f"\n  CHECK 1 PASS: Li et al. Day 12 CHO -- lactate={li_lactate}, ammonia={li_ammonia}")
    else:
        print(f"\n  CHECK 1 FAIL: Li et al. Day 12 CHO -- lactate={li_lactate}, ammonia={li_ammonia}")

    # Check 2: E. coli acetate overflow (Lee 1996) should have inhibitory acetate
    checks_total += 1
    lee_result = all_results[16]  # dataset #17, index 16
    lee_acetate = lee_result["states"].get("acetate", {}).get("state", "")
    if lee_acetate == "inhibitory":
        checks_passed += 1
        print(f"  CHECK 2 PASS: Lee 1996 E. coli -- acetate={lee_acetate}")
    else:
        print(f"  CHECK 2 FAIL: Lee 1996 E. coli -- acetate={lee_acetate}")

    # Check 3: Reinhart Day 5 CHO should be mostly optimal (score >= 80)
    checks_total += 1
    reinhart = all_results[2]  # dataset #3, index 2
    if reinhart["score"] >= 80:
        checks_passed += 1
        print(f"  CHECK 3 PASS: Reinhart Day 5 optimal -- score={reinhart['score']}/100")
    else:
        print(f"  CHECK 3 FAIL: Reinhart Day 5 optimal -- score={reinhart['score']}/100")

    # Check 4: Yee & Blanch E. coli at 42C should show heat_shock
    checks_total += 1
    yee_result = all_results[18]  # dataset #19, index 18
    yee_temp = yee_result["states"].get("temperature", {}).get("state", "")
    if yee_temp == "heat_shock":
        checks_passed += 1
        print(f"  CHECK 4 PASS: Yee & Blanch E. coli 42C -- temperature={yee_temp}")
    else:
        print(f"  CHECK 4 FAIL: Yee & Blanch E. coli 42C -- temperature={yee_temp}")

    # Check 5: NS0 glutamine-depleted (Schneider) should have toxic ammonia
    checks_total += 1
    schneider = all_results[25]  # dataset #26, index 25
    sch_ammonia = schneider["states"].get("ammonia", {}).get("state", "")
    if sch_ammonia == "toxic":
        checks_passed += 1
        print(f"  CHECK 5 PASS: Schneider NS0 gln-depleted -- ammonia={sch_ammonia}")
    else:
        print(f"  CHECK 5 FAIL: Schneider NS0 gln-depleted -- ammonia={sch_ammonia}")

    # Check 6: Gagnon CHO temp shift to 33C should show cold_shift
    checks_total += 1
    gagnon = all_results[7]  # dataset #8, index 7
    gag_temp = gagnon["states"].get("temperature", {}).get("state", "")
    if gag_temp == "cold_shift":
        checks_passed += 1
        print(f"  CHECK 6 PASS: Gagnon CHO temp shift -- temperature={gag_temp}")
    else:
        print(f"  CHECK 6 FAIL: Gagnon CHO temp shift -- temperature={gag_temp}")

    # Check 7: Potvin Pichia O2-limited should show hypoxic DO
    checks_total += 1
    potvin = all_results[21]  # dataset #22, index 21
    pot_do = potvin["states"].get("DO", {}).get("state", "")
    if pot_do == "hypoxic":
        checks_passed += 1
        print(f"  CHECK 7 PASS: Potvin Pichia O2-limited -- DO={pot_do}")
    else:
        print(f"  CHECK 7 FAIL: Potvin Pichia O2-limited -- DO={pot_do}")

    # Check 8: Riesenberg HCDC E. coli should show high_density OD600
    checks_total += 1
    riesen = all_results[17]  # dataset #18, index 17
    ries_od = riesen["states"].get("OD600", {}).get("state", "")
    if ries_od == "high_density":
        checks_passed += 1
        print(f"  CHECK 8 PASS: Riesenberg HCDC -- OD600={ries_od}")
    else:
        print(f"  CHECK 8 FAIL: Riesenberg HCDC -- OD600={ries_od}")

    print(f"\n  BIOLOGICAL PLAUSIBILITY: {checks_passed}/{checks_total} checks passed")
    verdict = "PASS" if checks_passed == checks_total else "PARTIAL"
    print(f"  RESULT: {verdict} -- Literature validation {'complete' if verdict == 'PASS' else 'needs review'}")
    print(f"{'=' * 140}\n")


if __name__ == "__main__":
    main()
