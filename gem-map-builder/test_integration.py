"""
test_integration.py -- Cross-Organism Integration Readiness Test
Written by: Anu Kozhiyalam
Purpose: Feeds IDENTICAL readings to all 10 organisms simultaneously
         to prove organism-aware divergence in a single summary table
"""

from gem_map import get_all_pathway_states, list_organisms

# ---------------------------------------------------------------------------
#  Universal stressed readings -- same values for all organisms
# ---------------------------------------------------------------------------
UNIVERSAL_READINGS = {
    "glucose":     1.5,
    "lactate":     4.5,    # maps to acetate/acetoin/ethanol via aliases
    "pH":          6.9,
    "DO":          18.0,
    "ammonia":     7.0,
    "VCD":         25.0,   # maps to OD600 via aliases
    "viability":   72.0,
    "titer":       1.8,
    "CO2":         14.0,
    "O2":          16.0,
    "temperature": 38.5,
    "agitation":   380.0,
}

# Pichia gets methanol as 13th parameter
PICHIA_READINGS = {**UNIVERSAL_READINGS, "methanol": 2.5}

# ---------------------------------------------------------------------------
#  Severity classification
# ---------------------------------------------------------------------------
STATE_SEVERITY = {
    "critical": "CRITICAL", "toxic": "CRITICAL", "inhibitory": "CRITICAL",
    "lysis": "CRITICAL", "autolysis": "CRITICAL",
    "acidosis": "WARNING", "acidic": "WARNING", "very_acidic": "WARNING",
    "above_optimum": "WARNING", "hypoxic": "WARNING",
    "microaerobic": "WARNING", "anaerobic": "WARNING", "heat_shock": "WARNING",
    "heat_stress": "WARNING", "overflow_risk": "WARNING", "overflow": "WARNING",
    "crabtree_overflow": "WARNING", "flux_limited": "WARNING",
    "carbon_starved": "WARNING", "carbon_limited": "WARNING",
    "depleted": "WARNING", "nitrogen_limited": "WARNING",
    "oxygen_depleted": "WARNING", "high_OUR": "WARNING",
    "hypercapnia": "WARNING", "high_respiration": "WARNING",
    "high_fermentation": "WARNING", "shear_risk": "WARNING",
    "foam_risk": "WARNING", "poor_mixing": "WARNING",
    "low_production": "WARNING", "low_expression": "WARNING",
    "slow_growth": "WARNING", "lag_or_slow": "WARNING",
    "low_density": "WARNING", "below_setpoint": "WARNING",
    "sub_induction": "WARNING", "overgrown": "WARNING",
    "alkalosis": "WARNING", "alkaline": "WARNING",
    "neutral_high": "WARNING", "high_for_yeast": "WARNING",
    "moderate": "WARNING", "moderate_stress": "WARNING",
    "cold_shift": "WARNING", "reduced_temp": "WARNING",
    "excess": "WARNING", "low_demand": "WARNING",
    "low_metabolism": "WARNING", "low_respiration": "WARNING",
    "high_shear": "WARNING", "extreme": "WARNING",
}


def classify(state_name):
    return STATE_SEVERITY.get(state_name, "OK")


def find_top_concern(states):
    """Return the single most critical parameter and its meaning."""
    # Priority: CRITICAL first, then WARNING
    for sev in ("CRITICAL", "WARNING"):
        for param, info in states.items():
            if classify(info["state"]) == sev:
                return param, info["state"], info["meaning"]
    return "-", "-", "All parameters nominal"


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------
def main():
    organisms = list_organisms()

    print("")
    print("=" * 130)
    print("  INTEGRATION READINESS TEST -- Identical Readings Across All 10 Organisms")
    print("=" * 130)
    print("")
    print("  Input readings (same for all):")
    print(f"    glucose=1.5 g/L | lactate/acetate=4.5 g/L | pH=6.9 | DO=18%")
    print(f"    ammonia=7.0 mM  | VCD/OD600=25            | viability=72% | titer=1.8 g/L")
    print(f"    CO2=14%         | O2=16%                  | temp=38.5C    | agitation=380 rpm")
    print(f"    methanol=2.5 g/L (Pichia only)")
    print("")
    print("=" * 130)
    print(f"  {'Organism':<16} {'GEM Model':<14} {'CRIT':>5} {'WARN':>5} {'OK':>5} {'Total':>5}  {'Top Concern'}")
    print(f"  {'-'*16} {'-'*14} {'-'*5} {'-'*5} {'-'*5} {'-'*5}  {'-'*60}")

    all_results = {}
    for org in organisms:
        readings = PICHIA_READINGS if org == "P. pastoris" else UNIVERSAL_READINGS
        states = get_all_pathway_states(readings, organism=org)
        all_results[org] = states

        c = sum(1 for i in states.values() if classify(i["state"]) == "CRITICAL")
        w = sum(1 for i in states.values() if classify(i["state"]) == "WARNING")
        o = sum(1 for i in states.values() if classify(i["state"]) == "OK")
        total = c + w + o

        gem_model = next(iter(states.values()))["gem_model"] if states else "?"
        top_param, top_state, top_meaning = find_top_concern(states)

        # Truncate meaning for table fit
        meaning_short = top_meaning[:58] + ".." if len(top_meaning) > 60 else top_meaning
        print(f"  {org:<16} {gem_model:<14} {c:>5} {w:>5} {o:>5} {total:>5}  {top_param}: {meaning_short}")

    print("=" * 130)

    # --- Detailed divergence table ---
    print(f"\n{'=' * 130}")
    print("  PARAMETER-BY-PARAMETER STATE DIVERGENCE")
    print(f"{'=' * 130}")

    # Build parameter list (all resolved names across all organisms)
    # Use display order
    display_params = [
        "glucose", "lactate", "acetate", "acetoin", "ethanol", "methanol",
        "pH", "DO", "ammonia", "VCD", "OD600",
        "viability", "titer", "CO2", "O2", "temperature", "agitation",
    ]

    header = f"  {'Param':<13}"
    for org in organisms:
        header += f" {org[:7]:<10}"
    print(header)
    print(f"  {'-'*13}" + f" {'-'*10}" * len(organisms))

    for param in display_params:
        states_for_param = []
        any_found = False
        for org in organisms:
            info = all_results[org].get(param)
            if info:
                any_found = True
                sev = classify(info["state"])
                marker = "!!!" if sev == "CRITICAL" else ("! " if sev == "WARNING" else "   ")
                states_for_param.append(f"{marker}{info['state'][:7]}")
            else:
                states_for_param.append("   ---")
        if any_found:
            row = f"  {param:<13}"
            for s in states_for_param:
                row += f" {s:<10}"
            print(row)

    print(f"{'=' * 130}")

    # --- Final verdict ---
    print(f"\n{'=' * 130}")
    print("  INTEGRATION READINESS VERDICT")
    print(f"{'=' * 130}")

    total_organisms = len(all_results)
    unique_states_per_param = {}
    for param in display_params:
        states_set = set()
        for org in organisms:
            info = all_results[org].get(param)
            if info:
                states_set.add(info["state"])
        if states_set:
            unique_states_per_param[param] = states_set

    divergent = {p: s for p, s in unique_states_per_param.items() if len(s) > 1}
    uniform = {p: s for p, s in unique_states_per_param.items() if len(s) == 1}

    print(f"\n  Organisms tested:     {total_organisms}")
    print(f"  Parameters divergent: {len(divergent)}  (same reading -> different biological state)")
    print(f"  Parameters uniform:   {len(uniform)}  (same reading -> same state across all)")

    if divergent:
        print(f"\n  DIVERGENT PARAMETERS (proves organism-aware mapping):")
        for p, states_set in divergent.items():
            print(f"    {p:<13} -> {len(states_set)} unique states: {', '.join(sorted(states_set))}")

    if uniform:
        print(f"\n  UNIFORM PARAMETERS:")
        for p, states_set in uniform.items():
            print(f"    {p:<13} -> {next(iter(states_set))}")

    print(f"\n  RESULT: {'PASS' if len(divergent) >= 6 else 'FAIL'} -- "
          f"{'Organism-aware divergence confirmed across all platforms' if len(divergent) >= 6 else 'Insufficient divergence'}")
    print(f"{'=' * 130}\n")


if __name__ == "__main__":
    main()
