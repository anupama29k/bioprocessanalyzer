"""
test_gem.py -- Stressed-culture scenarios for ALL 10 organisms
Written by: Anu Kozhiyalam
Purpose: Validates gem_map.py by running realistic "things going wrong"
         readings through every organism map and printing full biological
         interpretations plus a cross-organism comparison table
"""

from gem_map import get_all_pathway_states, list_organisms

# ---------------------------------------------------------------------------
#  Stressed-culture scenarios -- one per organism
# ---------------------------------------------------------------------------

SCENARIOS = {

    "CHO": {
        "label": "CHO (iCHO2291) -- fed-batch mAb Day 8, lactate spike",
        "readings": {
            "glucose":     1.5,
            "lactate":     4.8,
            "pH":          6.72,
            "DO":          15.0,
            "ammonia":     7.5,
            "VCD":         28.0,
            "viability":   74.0,
            "titer":       1.8,
            "CO2":         16.0,
            "O2":          14.0,
            "temperature": 36.8,
            "agitation":   180.0,
        }
    },

    "CHO-S": {
        "label": "CHO-S (iCHO2291) -- perfusion Day 30, filter fouling, density crash",
        "readings": {
            "glucose":     0.8,
            "lactate":     3.5,
            "pH":          6.80,
            "DO":          18.0,
            "ammonia":     6.5,
            "VCD":         95.0,
            "viability":   72.0,
            "titer":       0.2,
            "CO2":         19.0,
            "O2":          12.0,
            "temperature": 36.0,
            "agitation":   120.0,
        }
    },

    "HEK293": {
        "label": "HEK293 (Recon3D) -- post-transfection Day 3, AAV production stressed",
        "readings": {
            "glucose":     1.0,
            "lactate":     5.5,
            "pH":          6.85,
            "DO":          18.0,
            "ammonia":     8.5,
            "VCD":         5.5,
            "viability":   62.0,
            "titer":       5e9,
            "CO2":         16.0,
            "O2":          14.0,
            "temperature": 38.8,
            "agitation":   210.0,
        }
    },

    "NS0": {
        "label": "NS0 (iNS0_1091) -- fed-batch Day 7, glutamine-depleted, ammonia toxic",
        "readings": {
            "glucose":     1.0,
            "lactate":     5.5,
            "pH":          6.75,
            "DO":          18.0,
            "ammonia":     7.5,
            "VCD":         14.0,
            "viability":   63.0,
            "titer":       0.2,
            "CO2":         16.0,
            "O2":          14.0,
            "temperature": 38.2,
            "agitation":   310.0,
        }
    },

    "Sp2/0": {
        "label": "Sp2/0 (iSp2_0) -- batch Day 5, hybridoma crashing, ammonia toxic",
        "readings": {
            "glucose":     1.0,
            "lactate":     5.0,
            "pH":          6.75,
            "DO":          18.0,
            "ammonia":     6.5,
            "VCD":         11.0,
            "viability":   58.0,
            "titer":       0.15,
            "CO2":         15.0,
            "O2":          14.0,
            "temperature": 38.5,
            "agitation":   260.0,
        }
    },

    "BHK-21": {
        "label": "BHK-21 (iBHK) -- post-infection Day 2, FMDV vaccine production",
        "readings": {
            "glucose":     1.2,
            "lactate":     5.5,
            "pH":          6.75,
            "DO":          15.0,
            "ammonia":     8.5,
            "VCD":         18.0,
            "viability":   55.0,
            "titer":       0.2,
            "CO2":         16.0,
            "O2":          14.0,
            "temperature": 39.0,
            "agitation":   260.0,
        }
    },

    "E. coli": {
        "label": "E. coli (iML1515) -- post-IPTG induction, acetate spike, heat shock",
        "readings": {
            "glucose":     12.0,
            "acetate":     6.2,
            "pH":          6.3,
            "DO":          8.0,
            "ammonia":     0.5,
            "OD600":       45.0,
            "viability":   62.0,
            "titer":       0.15,
            "CO2":         16.0,
            "O2":          12.0,
            "temperature": 42.5,
            "agitation":   400.0,
        }
    },

    "B. subtilis": {
        "label": "B. subtilis (iYO844) -- late stationary, sporulating, autolysis",
        "readings": {
            "glucose":     0.3,
            "acetoin":     6.0,
            "pH":          5.8,
            "DO":          8.0,
            "ammonia":     0.5,
            "OD600":       48.0,
            "viability":   45.0,
            "titer":       0.3,
            "CO2":         15.0,
            "O2":          13.0,
            "temperature": 52.0,
            "agitation":   850.0,
        }
    },

    "P. pastoris": {
        "label": "P. pastoris (iMT1026v3) -- methanol phase, O2 crash, formaldehyde stress",
        "readings": {
            "glucose":     0.1,
            "methanol":    9.0,
            "ethanol":     0.1,
            "pH":          3.5,
            "DO":          5.0,
            "ammonia":     0.5,
            "OD600":       420.0,
            "viability":   68.0,
            "titer":       0.3,
            "CO2":         20.0,
            "O2":          10.0,
            "temperature": 36.0,
            "agitation":   250.0,
        }
    },

    "S. cerevisiae": {
        "label": "S. cerevisiae (iMM904) -- batch VLP production, Crabtree overflow, ethanol",
        "readings": {
            "glucose":     18.0,
            "ethanol":     16.0,
            "pH":          3.2,
            "DO":          3.0,
            "ammonia":     0.5,
            "OD600":       48.0,
            "viability":   68.0,
            "titer":       0.08,
            "CO2":         22.0,
            "O2":          14.0,
            "temperature": 38.0,
            "agitation":   120.0,
        }
    },
}

# ---------------------------------------------------------------------------
#  Formatting helpers
# ---------------------------------------------------------------------------
SEPARATOR = "=" * 90
THIN_SEP  = "-" * 90

STATE_ICONS = {
    "critical":         "[!!!]",
    "toxic":            "[!!!]",
    "inhibitory":       "[!!!]",
    "lysis":            "[!!!]",
    "autolysis":        "[!!!]",
    "acidosis":         "[!! ]",
    "acidic":           "[!! ]",
    "above_optimum":    "[~  ]",
    "very_acidic":      "[!! ]",
    "hypoxic":          "[!! ]",
    "microaerobic":     "[!! ]",
    "anaerobic":        "[!! ]",
    "heat_shock":       "[!! ]",
    "heat_stress":      "[!! ]",
    "overflow_risk":    "[!  ]",
    "overflow":         "[!  ]",
    "crabtree_overflow":"[!  ]",
    "flux_limited":     "[!  ]",
    "carbon_starved":   "[!  ]",
    "carbon_limited":   "[!  ]",
    "depleted":         "[!  ]",
    "nitrogen_limited": "[!  ]",
    "oxygen_depleted":  "[!  ]",
    "high_OUR":         "[!  ]",
    "hypercapnia":      "[!  ]",
    "high_respiration": "[!  ]",
    "high_fermentation":"[!  ]",
    "shear_risk":       "[!  ]",
    "foam_risk":        "[!  ]",
    "poor_mixing":      "[!  ]",
    "low_production":   "[!  ]",
    "low_expression":   "[!  ]",
    "slow_growth":      "[!  ]",
    "lag_or_slow":      "[!  ]",
    "low_density":      "[!  ]",
    "below_setpoint":   "[!  ]",
    "sub_induction":    "[!  ]",
    "overgrown":        "[!  ]",
    "alkalosis":        "[~  ]",
    "alkaline":         "[~  ]",
    "neutral_high":     "[~  ]",
    "high_for_yeast":   "[~  ]",
    "moderate":         "[~  ]",
    "moderate_stress":  "[~  ]",
    "cold_shift":       "[~  ]",
    "reduced_temp":     "[~  ]",
    "optimal":          "[ OK]",
    "on_track":         "[ OK]",
    "exponential":      "[ OK]",
    "balanced":         "[ OK]",
    "healthy":          "[ OK]",
    "excellent":        "[ OK]",
    "peak_density":     "[ OK]",
    "high_density":     "[ OK]",
    "ultra_high_density":"[ OK]",
    "steady_state":     "[ OK]",
    "high_producing":   "[ OK]",
    "high_expression":  "[ OK]",
    "transfection_ready":"[ OK]",
    "induction_ready":  "[ OK]",
    "excess":           "[~  ]",
    "low_demand":       "[~  ]",
    "low_metabolism":   "[~  ]",
    "low_respiration":  "[~  ]",
    "high_shear":       "[~  ]",
    "extreme":          "[~  ]",
}


def classify_severity(state_name):
    """Return 'CRITICAL', 'WARNING', or 'OK' for a state name."""
    icon = STATE_ICONS.get(state_name, "[   ]")
    if "!!!" in icon:
        return "CRITICAL"
    elif "!" in icon or "~" in icon:
        return "WARNING"
    return "OK"


def print_organism_report(organism, scenario, states):
    """Print a formatted report for one organism."""
    print(f"\n{SEPARATOR}")
    print(f"  ORGANISM:   {organism}")
    print(f"  SCENARIO:   {scenario['label']}")
    print(f"  PARAMETERS: {len(states)}")
    print(SEPARATOR)

    for param, info in states.items():
        icon = STATE_ICONS.get(info["state"], "[   ]")
        unit = info["unit"] if info["unit"] else ""
        val_str = f"{info['value']:.4g}" if isinstance(info['value'], float) else str(info['value'])
        print(f"\n  {icon}  {param}  =  {val_str} {unit}")
        print(f"        State:     {info['state']}")
        print(f"        Pathway:   {info['pathway']}")
        print(f"        Reaction:  {info['gem_reaction']}  ({info['gem_model']})")
        print(f"        Meaning:   {info['meaning']}")
        if info["downstream"]:
            print(f"        Affects:   {', '.join(info['downstream'])}")
        print(f"        Color:     {info['atlas_color']}")

    print(f"\n{THIN_SEP}")

    critical = [p for p, i in states.items() if classify_severity(i["state"]) == "CRITICAL"]
    warning  = [p for p, i in states.items() if classify_severity(i["state"]) == "WARNING"]
    ok       = [p for p, i in states.items() if classify_severity(i["state"]) == "OK"]

    print(f"  SUMMARY:")
    if critical:
        print(f"    CRITICAL ({len(critical)}):  {', '.join(critical)}")
    if warning:
        print(f"    WARNING  ({len(warning)}):   {', '.join(warning)}")
    if ok:
        print(f"    OK       ({len(ok)}):        {', '.join(ok)}")
    print(SEPARATOR)


# ---------------------------------------------------------------------------
#  Cross-organism comparison table
# ---------------------------------------------------------------------------
def print_comparison_table(all_results):
    """Print a comparison of key parameter states across all organisms."""
    organisms = list(all_results.keys())

    # Universal parameter equivalents across organisms
    universal_params = [
        "glucose", "pH", "DO", "ammonia", "viability", "titer",
        "CO2", "O2", "temperature", "agitation",
    ]
    # Organism-specific byproduct / biomass
    byproduct_map = {
        "CHO": "lactate", "CHO-S": "lactate", "HEK293": "lactate",
        "NS0": "lactate", "Sp2/0": "lactate", "BHK-21": "lactate",
        "E. coli": "acetate", "B. subtilis": "acetoin",
        "P. pastoris": "methanol", "S. cerevisiae": "ethanol",
    }
    biomass_map = {
        "CHO": "VCD", "CHO-S": "VCD", "HEK293": "VCD",
        "NS0": "VCD", "Sp2/0": "VCD", "BHK-21": "VCD",
        "E. coli": "OD600", "B. subtilis": "OD600",
        "P. pastoris": "OD600", "S. cerevisiae": "OD600",
    }

    print(f"\n{'=' * 120}")
    print("  CROSS-ORGANISM COMPARISON TABLE")
    print(f"{'=' * 120}")

    # Header
    header = f"  {'Parameter':<14}"
    for org in organisms:
        short = org[:8]
        header += f" {short:<12}"
    print(header)
    print(f"  {'-'*14}" + f" {'-'*12}" * len(organisms))

    # Universal parameters
    for param in universal_params:
        row = f"  {param:<14}"
        for org in organisms:
            results = all_results[org]
            state = results.get(param, {}).get("state", "-")
            sev = classify_severity(state)
            marker = "!!!" if sev == "CRITICAL" else ("! " if sev == "WARNING" else "  ")
            row += f" {marker}{state[:9]:<9}"
        print(row)

    # Byproduct row
    row = f"  {'byproduct':<14}"
    for org in organisms:
        bp = byproduct_map.get(org, "-")
        results = all_results[org]
        state = results.get(bp, {}).get("state", "-")
        sev = classify_severity(state)
        marker = "!!!" if sev == "CRITICAL" else ("! " if sev == "WARNING" else "  ")
        row += f" {marker}{state[:9]:<9}"
    print(row)

    # Biomass row
    row = f"  {'biomass':<14}"
    for org in organisms:
        bm = biomass_map.get(org, "-")
        results = all_results[org]
        state = results.get(bm, {}).get("state", "-")
        sev = classify_severity(state)
        marker = "!!!" if sev == "CRITICAL" else ("! " if sev == "WARNING" else "  ")
        row += f" {marker}{state[:9]:<9}"
    print(row)

    print(f"{'=' * 120}")

    # Severity summary
    print(f"\n  {'Organism':<16} {'Critical':>8} {'Warning':>8} {'OK':>8} {'Total':>8}")
    print(f"  {'-'*16} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for org in organisms:
        results = all_results[org]
        c = sum(1 for i in results.values() if classify_severity(i["state"]) == "CRITICAL")
        w = sum(1 for i in results.values() if classify_severity(i["state"]) == "WARNING")
        o = sum(1 for i in results.values() if classify_severity(i["state"]) == "OK")
        print(f"  {org:<16} {c:>8} {w:>8} {o:>8} {c+w+o:>8}")


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------
def main():
    print("\n" + "=" * 90)
    print("  GEM MAP TEST -- Full Organism Library Validation")
    print(f"  Organisms available ({len(list_organisms())}): {', '.join(list_organisms())}")
    print("=" * 90)

    all_results = {}

    for organism in list_organisms():
        if organism not in SCENARIOS:
            print(f"\n  [SKIP] No test scenario defined for {organism}")
            continue

        scenario = SCENARIOS[organism]
        states = get_all_pathway_states(scenario["readings"], organism=organism)
        all_results[organism] = states
        print_organism_report(organism, scenario, states)

    # Cross-organism comparison
    print_comparison_table(all_results)

    print(f"\n  NOTE: Each organism interprets the SAME parameter through its own metabolic lens.")
    print(f"        Glucose overflow -> lactate (mammalian), acetate (E. coli),")
    print(f"        acetoin (B. subtilis), ethanol (yeast).")
    print(f"        Temperature optimum: 37C (mammalian/bacterial), 30C (yeast).")
    print(f"        Pichia needs 700+ rpm; CHO dies above 350 rpm.\n")


if __name__ == "__main__":
    main()
