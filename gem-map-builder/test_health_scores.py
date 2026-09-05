"""
test_health_scores.py -- Health Score Validation Across All 32 Literature Datasets
Written by: Anu Kozhiyalam
Purpose: Runs every literature dataset through health_score() and flags
         biologically implausible scores. Ensures stressed cultures score
         low and healthy cultures score high.
"""

from gem_map import get_all_pathway_states
from test_literature import LITERATURE_DATASETS, classify, health_score


# ═══════════════════════════════════════════════════════════════════════════
#  BIOLOGICAL EXPECTATIONS
#  Each entry: (dataset_id, operator, threshold, reason)
# ═══════════════════════════════════════════════════════════════════════════

EXPECTATIONS = [
    {
        "id": 6,
        "citation": "Li et al. 2010",
        "operator": "<",
        "threshold": 20,
        "reason": "Day 12 crashing culture -- glucose depleted, lactate critical, ammonia toxic, viability critical, DO hypoxic, pH acidosis",
    },
    {
        "id": 3,
        "citation": "Reinhart et al. 2019",
        "operator": ">",
        "threshold": 80,
        "reason": "Day 5 optimal -- all parameters near healthy baseline",
    },
    {
        "id": 1,
        "citation": "Xu et al. 2011",
        "operator": ">",
        "threshold": 60,
        "reason": "Day 7 peak -- culture at production peak, lactate elevated but otherwise healthy",
    },
    {
        "id": 19,
        "citation": "Yee & Blanch 1992",
        "operator": "<",
        "threshold": 55,
        "reason": "E. coli 42C heat shock -- acetate inhibitory (1 crit), heat_shock + high_shear + ammonia excess (3 warn), but 5 params still OK -- moderate stress not total failure",
    },
    {
        "id": 26,
        "citation": "Schneider et al. 1996",
        "operator": "<",
        "threshold": 40,
        "reason": "NS0 glutamine depleted -- ammonia toxic + viability critical (2 crit), VCD slow + lactate moderate (2 warn), but glucose/pH/DO/temp/agitation/titer all OK",
    },
]


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("")
    print("=" * 140)
    print("  HEALTH SCORE VALIDATION -- 32 Literature Datasets")
    print("=" * 140)

    # ── Compute all scores ───────────────────────────────────────────────
    results = []

    for ds in LITERATURE_DATASETS:
        states = get_all_pathway_states(ds["readings"], organism=ds["organism"])
        score = health_score(states)

        n_crit = sum(1 for i in states.values() if classify(i["state"]) == "CRITICAL")
        n_warn = sum(1 for i in states.values() if classify(i["state"]) == "WARNING")
        n_ok = len(states) - n_crit - n_warn

        param_states = {}
        for p, info in states.items():
            param_states[p] = {
                "state": info["state"],
                "severity": classify(info["state"]),
                "value": info["value"],
                "unit": info.get("unit", ""),
            }

        results.append({
            "ds": ds,
            "states": states,
            "score": score,
            "n_crit": n_crit,
            "n_warn": n_warn,
            "n_ok": n_ok,
            "param_states": param_states,
        })

    # ── Summary table ────────────────────────────────────────────────────
    print(f"\n  {'#':<4} {'Organism':<15} {'Citation':<42} {'Score':>5} {'C':>3} {'W':>3} {'OK':>3}  Parameter States")
    print(f"  {'-'*4} {'-'*15} {'-'*42} {'-'*5} {'-'*3} {'-'*3} {'-'*3}  {'-'*60}")

    for r in results:
        ds = r["ds"]
        cite = ds["citation"][:40]
        state_summary = "  ".join(
            f"{p}:{info['state'][:10]}" for p, info in r["param_states"].items()
        )
        print(
            f"  {ds['id']:<4} {ds['organism']:<15} {cite:<42} "
            f"{r['score']:>5} {r['n_crit']:>3} {r['n_warn']:>3} {r['n_ok']:>3}  "
            f"{state_summary[:60]}"
        )

    # ── Detailed per-dataset breakdown ───────────────────────────────────
    print(f"\n{'=' * 140}")
    print("  DETAILED PARAMETER STATES")
    print(f"{'=' * 140}")

    for r in results:
        ds = r["ds"]
        print(f"\n  [{ds['id']}] {ds['citation']}")
        print(f"      Organism: {ds['organism']}  |  Context: {ds['context']}")
        print(f"      Score: {r['score']}/100  |  Critical: {r['n_crit']}  |  Warning: {r['n_warn']}  |  OK: {r['n_ok']}")

        # Compute base and penalty for transparency
        n = len(r["states"])
        base = (r["n_ok"] * 100 + r["n_warn"] * 40 + r["n_crit"] * 0) / n if n > 0 else 100
        penalty = 0.7 ** r["n_crit"] if r["n_crit"] > 0 else 1.0
        print(f"      Scoring: base={base:.1f}  x  penalty(0.7^{r['n_crit']})={penalty:.3f}  =  {r['score']}")

        print(f"      {'Param':<14} {'Value':>8} {'Unit':<6} {'State':<20} {'Severity':<10} {'Points'}")
        print(f"      {'-'*14} {'-'*8} {'-'*6} {'-'*20} {'-'*10} {'-'*6}")

        for p, info in r["param_states"].items():
            sev = info["severity"]
            pts = 0 if sev == "CRITICAL" else (40 if sev == "WARNING" else 100)
            marker = "!!!" if sev == "CRITICAL" else ("! " if sev == "WARNING" else "   ")
            val_str = f"{info['value']:.4g}" if isinstance(info["value"], float) else str(info["value"])
            print(f"   {marker} {p:<14} {val_str:>8} {info['unit']:<6} {info['state']:<20} {sev:<10} {pts}")

    # ── Score distribution ───────────────────────────────────────────────
    print(f"\n{'=' * 140}")
    print("  SCORE DISTRIBUTION")
    print(f"{'=' * 140}")

    scores = [r["score"] for r in results]
    buckets = {
        "0-19 (failing)": sum(1 for s in scores if s < 20),
        "20-39 (poor)": sum(1 for s in scores if 20 <= s < 40),
        "40-59 (stressed)": sum(1 for s in scores if 40 <= s < 60),
        "60-79 (moderate)": sum(1 for s in scores if 60 <= s < 80),
        "80-100 (healthy)": sum(1 for s in scores if s >= 80),
    }

    for label, count in buckets.items():
        bar = "#" * (count * 3)
        print(f"  {label:<25} {count:>3}  {bar}")

    avg = sum(scores) / len(scores)
    print(f"\n  Average score: {avg:.1f}/100")
    print(f"  Min: {min(scores)}  Max: {max(scores)}")

    # ── Biological plausibility checks ───────────────────────────────────
    print(f"\n{'=' * 140}")
    print("  BIOLOGICAL PLAUSIBILITY CHECKS")
    print(f"{'=' * 140}")

    checks_passed = 0
    checks_total = len(EXPECTATIONS)

    # Build lookup by dataset ID
    result_by_id = {r["ds"]["id"]: r for r in results}

    for exp in EXPECTATIONS:
        r = result_by_id.get(exp["id"])
        if r is None:
            print(f"\n  SKIP: Dataset #{exp['id']} not found")
            continue

        score = r["score"]
        op = exp["operator"]
        thresh = exp["threshold"]

        if op == "<":
            passed = score < thresh
        elif op == ">":
            passed = score > thresh
        else:
            passed = False

        status = "EXPECTED" if passed else "SUSPICIOUS"
        checks_passed += 1 if passed else 0

        symbol = "PASS" if passed else "FAIL"
        print(f"\n  [{symbol}] {exp['citation']} (Dataset #{exp['id']})")
        print(f"        Score: {score}/100  |  Expected: {op} {thresh}")
        print(f"        Status: {status}")
        print(f"        Reason: {exp['reason']}")
        print(f"        Breakdown: C={r['n_crit']} W={r['n_warn']} OK={r['n_ok']}")
        if not passed:
            print(f"        >>> INVESTIGATE: score {score} does not match biological expectation {op}{thresh}")

    # ── Cross-dataset consistency checks ─────────────────────────────────
    print(f"\n{'=' * 140}")
    print("  CROSS-DATASET CONSISTENCY CHECKS")
    print(f"{'=' * 140}")

    consistency_passed = 0
    consistency_total = 0

    # Check: Day 12 CHO (Li) should score lower than Day 5 CHO (Reinhart)
    consistency_total += 1
    li_score = result_by_id[6]["score"]
    reinhart_score = result_by_id[3]["score"]
    if li_score < reinhart_score:
        consistency_passed += 1
        print(f"\n  [PASS] Li Day 12 ({li_score}) < Reinhart Day 5 ({reinhart_score})")
    else:
        print(f"\n  [FAIL] Li Day 12 ({li_score}) should be < Reinhart Day 5 ({reinhart_score})")

    # Check: Clincke CHO-S perfusion should score higher than Naso HEK293 stress
    consistency_total += 1
    clincke_score = result_by_id[9]["score"]
    naso_score = result_by_id[14]["score"]
    if clincke_score > naso_score:
        consistency_passed += 1
        print(f"  [PASS] Clincke CHO-S ({clincke_score}) > Naso HEK293 stress ({naso_score})")
    else:
        print(f"  [FAIL] Clincke CHO-S ({clincke_score}) should be > Naso HEK293 stress ({naso_score})")

    # Check: Shiloach E. coli optimal should score higher than Lee acetate overflow
    consistency_total += 1
    shiloach_score = result_by_id[15]["score"]
    lee_score = result_by_id[17]["score"]
    if shiloach_score > lee_score:
        consistency_passed += 1
        print(f"  [PASS] Shiloach optimal ({shiloach_score}) > Lee acetate overflow ({lee_score})")
    else:
        print(f"  [FAIL] Shiloach optimal ({shiloach_score}) should be > Lee acetate overflow ({lee_score})")

    # Check: Mostafa NS0 healthy should score higher than Schneider NS0 depleted
    consistency_total += 1
    mostafa_score = result_by_id[25]["score"]
    schneider_score = result_by_id[26]["score"]
    if mostafa_score > schneider_score:
        consistency_passed += 1
        print(f"  [PASS] Mostafa NS0 healthy ({mostafa_score}) > Schneider NS0 depleted ({schneider_score})")
    else:
        print(f"  [FAIL] Mostafa NS0 healthy ({mostafa_score}) should be > Schneider NS0 depleted ({schneider_score})")

    # Check: Telling BHK-21 classic should score higher or equal to Merten BHK-21 FMDV
    consistency_total += 1
    telling_score = result_by_id[28]["score"]
    merten_score = result_by_id[27]["score"]
    if telling_score >= merten_score:
        consistency_passed += 1
        print(f"  [PASS] Telling BHK classic ({telling_score}) >= Merten BHK FMDV ({merten_score})")
    else:
        print(f"  [FAIL] Telling BHK classic ({telling_score}) should be >= Merten BHK FMDV ({merten_score})")

    # ── Final verdict ────────────────────────────────────────────────────
    print(f"\n{'=' * 140}")
    print("  VERDICT")
    print(f"{'=' * 140}")

    print(f"\n  Biological plausibility:  {checks_passed}/{checks_total} passed")
    print(f"  Cross-dataset consistency: {consistency_passed}/{consistency_total} passed")
    total_checks = checks_passed + consistency_passed
    total_total = checks_total + consistency_total
    verdict = "PASS" if total_checks == total_total else "FAIL"
    print(f"  Overall: {total_checks}/{total_total} checks passed")
    print(f"  RESULT: {verdict}")
    print(f"{'=' * 140}\n")


if __name__ == "__main__":
    main()
