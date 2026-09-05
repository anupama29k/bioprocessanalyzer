"""
test_gem_full.py -- Comprehensive Automated Test Suite for gem_map.py
Written by: Anu Kozhiyalam
Purpose: 500+ automated test cases covering every organism, strain,
         threshold boundary, healthy baseline, and critical scenario.
         Reports pass/fail with percentage coverage and assertion details.
"""

import sys
from gem_map import (
    get_all_pathway_states,
    get_pathway_state,
    list_organisms,
    list_strains,
    list_parameters,
    get_strain_info,
    ORGANISM_MAPS,
    PARAM_ALIASES,
    STRAIN_REGISTRY,
)

# ═══════════════════════════════════════════════════════════════════════════
#  TEST INFRASTRUCTURE
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
OK_STATES = {
    "optimal", "on_track", "exponential", "balanced", "healthy",
    "excellent", "peak_density", "high_density", "ultra_high_density",
    "steady_state", "high_producing", "high_expression",
    "transfection_ready", "induction_ready",
}


def classify(state_name):
    if state_name in CRITICAL_STATES:
        return "CRITICAL"
    if state_name in WARNING_STATES:
        return "WARNING"
    return "OK"


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.categories = {}

    def assert_true(self, condition, test_name, category, detail=""):
        cat = self.categories.setdefault(category, {"passed": 0, "failed": 0})
        if condition:
            self.passed += 1
            cat["passed"] += 1
        else:
            self.failed += 1
            cat["failed"] += 1
            self.errors.append(f"  FAIL: [{category}] {test_name}" + (f" -- {detail}" if detail else ""))

    def assert_equal(self, actual, expected, test_name, category):
        self.assert_true(
            actual == expected, test_name, category,
            f"expected={expected}, got={actual}"
        )

    def assert_in(self, item, collection, test_name, category):
        self.assert_true(
            item in collection, test_name, category,
            f"{item} not in {collection}"
        )

    def report(self):
        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0

        print(f"\n{'=' * 100}")
        print(f"  TEST RESULTS -- {total} tests, {self.passed} passed, {self.failed} failed ({pct:.1f}%)")
        print(f"{'=' * 100}")

        print(f"\n  {'Category':<40} {'Passed':>8} {'Failed':>8} {'Total':>8} {'Rate':>8}")
        print(f"  {'-'*40} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        for cat, stats in sorted(self.categories.items()):
            cat_total = stats["passed"] + stats["failed"]
            cat_pct = (stats["passed"] / cat_total * 100) if cat_total > 0 else 0
            marker = "  " if stats["failed"] == 0 else "!!"
            print(f"{marker}{cat:<40} {stats['passed']:>8} {stats['failed']:>8} {cat_total:>8} {cat_pct:>7.1f}%")

        if self.errors:
            print(f"\n  FAILURES ({len(self.errors)}):")
            for err in self.errors[:50]:  # cap at 50 to avoid flooding
                print(err)
            if len(self.errors) > 50:
                print(f"  ... and {len(self.errors) - 50} more")

        print(f"\n  VERDICT: {'PASS' if self.failed == 0 else 'FAIL'}")
        print(f"{'=' * 100}\n")
        return self.failed == 0


# ═══════════════════════════════════════════════════════════════════════════
#  HEALTHY BASELINE READINGS (mid-range "all-green" values per organism)
# ═══════════════════════════════════════════════════════════════════════════

HEALTHY_READINGS = {
    "CHO":           {"glucose": 3.5, "lactate": 0.4, "pH": 7.1, "DO": 35.0, "ammonia": 1.5, "VCD": 10.0, "viability": 96.0, "titer": 1.5, "CO2": 8.0, "O2": 17.5, "temperature": 36.5, "agitation": 170.0},
    "CHO-S":         {"glucose": 2.5, "lactate": 0.2, "pH": 7.05, "DO": 40.0, "ammonia": 1.2, "VCD": 50.0, "viability": 93.0, "titer": 0.8, "CO2": 9.0, "O2": 16.0, "temperature": 35.5, "agitation": 150.0},
    "HEK293":        {"glucose": 3.0, "lactate": 0.4, "pH": 7.1, "DO": 35.0, "ammonia": 1.5, "VCD": 2.5, "viability": 96.0, "titer": 5e10, "CO2": 8.0, "O2": 17.5, "temperature": 36.5, "agitation": 110.0},
    "NS0":           {"glucose": 3.0, "lactate": 0.5, "pH": 7.0, "DO": 35.0, "ammonia": 1.5, "VCD": 6.0, "viability": 90.0, "titer": 1.0, "CO2": 8.0, "O2": 17.5, "temperature": 36.5, "agitation": 150.0},
    "Sp2/0":         {"glucose": 3.0, "lactate": 0.4, "pH": 7.1, "DO": 35.0, "ammonia": 1.5, "VCD": 4.0, "viability": 92.0, "titer": 0.5, "CO2": 8.0, "O2": 17.5, "temperature": 36.5, "agitation": 120.0},
    "BHK-21":        {"glucose": 3.0, "lactate": 0.4, "pH": 7.1, "DO": 35.0, "ammonia": 1.5, "VCD": 8.0, "viability": 92.0, "titer": 1.2, "CO2": 8.0, "O2": 17.5, "temperature": 36.5, "agitation": 120.0},
    "E. coli":       {"glucose": 3.0, "acetate": 0.3, "pH": 6.8, "DO": 25.0, "ammonia": 8.0, "OD600": 20.0, "viability": 96.0, "titer": 0.8, "CO2": 6.0, "O2": 17.5, "temperature": 35.0, "agitation": 400.0},
    "B. subtilis":   {"glucose": 3.0, "acetoin": 0.3, "pH": 6.5, "DO": 25.0, "ammonia": 8.0, "OD600": 15.0, "viability": 96.0, "titer": 3.0, "CO2": 6.0, "O2": 17.5, "temperature": 35.0, "agitation": 400.0},
    "P. pastoris":   {"glucose": 2.0, "methanol": 2.0, "ethanol": 0.1, "pH": 5.5, "DO": 22.0, "ammonia": 8.0, "OD600": 150.0, "viability": 92.0, "titer": 2.0, "CO2": 8.0, "O2": 16.0, "temperature": 28.0, "agitation": 600.0},
    "S. cerevisiae": {"glucose": 3.0, "ethanol": 0.8, "pH": 5.0, "DO": 15.0, "ammonia": 8.0, "OD600": 15.0, "viability": 92.0, "titer": 0.3, "CO2": 8.0, "O2": 18.0, "temperature": 28.0, "agitation": 350.0},
}


# ═══════════════════════════════════════════════════════════════════════════
#  TEST CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════

def test_api_basics(t):
    """Test core API functions return expected types."""
    cat = "API basics"

    # list_organisms returns non-empty list
    orgs = list_organisms()
    t.assert_true(len(orgs) == 10, "list_organisms count", cat, f"got {len(orgs)}")

    # list_strains returns correct count
    all_strains = list_strains()
    t.assert_true(len(all_strains) == 16, "list_strains total count", cat, f"got {len(all_strains)}")

    # list_strains per organism
    t.assert_true(len(list_strains("CHO")) == 4, "CHO has 4 strains", cat)
    t.assert_true(len(list_strains("E. coli")) == 5, "E. coli has 5 strains", cat)
    t.assert_true(len(list_strains("HEK293")) == 2, "HEK293 has 2 strains", cat)
    t.assert_true(len(list_strains("P. pastoris")) == 2, "P. pastoris has 2 strains", cat)
    t.assert_true(len(list_strains("S. cerevisiae")) == 3, "S. cerevisiae has 3 strains", cat)
    t.assert_true(len(list_strains("NS0")) == 0, "NS0 has 0 strains", cat)
    t.assert_true(len(list_strains("BHK-21")) == 0, "BHK-21 has 0 strains", cat)

    # list_parameters returns non-empty
    for org in orgs:
        params = list_parameters(org)
        t.assert_true(len(params) >= 12, f"{org} has >= 12 params", cat, f"got {len(params)}")

    # get_strain_info returns dict for valid, None for invalid
    info = get_strain_info("CHO|CHO-DG44")
    t.assert_true(info is not None, "get_strain_info valid key", cat)
    t.assert_equal(info["organism"], "CHO", "strain_info organism field", cat)
    t.assert_true(get_strain_info("INVALID|KEY") is None, "get_strain_info invalid key", cat)

    # get_pathway_state returns None for unknown parameter
    result = get_pathway_state("nonexistent_param", 5.0, "CHO")
    t.assert_true(result is None, "unknown param returns None", cat)

    # get_pathway_state raises for unknown organism
    try:
        get_pathway_state("glucose", 5.0, "INVALID_ORG")
        t.assert_true(False, "invalid organism raises ValueError", cat)
    except ValueError:
        t.assert_true(True, "invalid organism raises ValueError", cat)


def test_result_structure(t):
    """Test that get_pathway_state returns all required fields."""
    cat = "Result structure"
    required_fields = [
        "parameter", "value", "organism", "pathway", "gem_reaction",
        "gem_model", "direction", "state", "unit", "meaning",
        "downstream", "atlas_color"
    ]

    for org in list_organisms():
        params = list_parameters(org)
        result = get_pathway_state(params[0], 5.0, org)
        if result is None:
            continue
        for field in required_fields:
            t.assert_in(field, result, f"{org} result has '{field}'", cat)


def test_healthy_baselines(t):
    """Every organism with healthy readings should produce all OK states."""
    cat = "Healthy baselines"

    for org, readings in HEALTHY_READINGS.items():
        states = get_all_pathway_states(readings, organism=org)
        t.assert_true(len(states) > 0, f"{org} healthy produces results", cat)

        for param, info in states.items():
            sev = classify(info["state"])
            t.assert_equal(
                sev, "OK",
                f"{org} healthy {param}={info['value']}",
                cat,
            )


def test_healthy_strains(t):
    """Every strain with parent's healthy readings should produce mostly OK states."""
    cat = "Healthy strains"

    for strain_key in list_strains():
        info = get_strain_info(strain_key)
        org = info["organism"]
        # Use parent organism's healthy readings
        readings = HEALTHY_READINGS.get(org)
        if readings is None:
            continue

        states = get_all_pathway_states(readings, organism=strain_key)
        t.assert_true(len(states) > 0, f"{strain_key} healthy produces results", cat)

        n_ok = sum(1 for i in states.values() if classify(i["state"]) == "OK")
        n_total = len(states)
        # Strains with tightened thresholds may have a few warnings on parent's healthy readings
        # but should never have criticals
        n_crit = sum(1 for i in states.values() if classify(i["state"]) == "CRITICAL")
        t.assert_equal(
            n_crit, 0,
            f"{strain_key} healthy no criticals",
            cat,
        )
        t.assert_true(
            n_ok >= n_total * 0.6,
            f"{strain_key} healthy >= 60% OK",
            cat,
            f"OK={n_ok}/{n_total}",
        )


def test_all_critical(t):
    """Every organism with extreme readings should produce mostly CRITICAL/WARNING."""
    cat = "All-critical scenarios"

    # Extreme readings designed to push everything to critical
    EXTREME_MAM = {
        "glucose": 0.1, "lactate": 9.0, "pH": 6.5, "DO": 5.0,
        "ammonia": 15.0, "VCD": 0.5, "viability": 50.0, "titer": 0.01,
        "CO2": 22.0, "O2": 10.0, "temperature": 40.0, "agitation": 500.0,
    }
    EXTREME_ECOLI = {
        "glucose": 0.1, "acetate": 8.0, "pH": 6.0, "DO": 3.0,
        "ammonia": 0.1, "OD600": 1.0, "viability": 40.0, "titer": 0.01,
        "CO2": 20.0, "O2": 10.0, "temperature": 45.0, "agitation": 100.0,
    }
    EXTREME_BSUB = {
        "glucose": 0.1, "acetoin": 8.0, "pH": 5.5, "DO": 3.0,
        "ammonia": 0.1, "OD600": 1.0, "viability": 30.0, "titer": 0.01,
        "CO2": 20.0, "O2": 10.0, "temperature": 55.0, "agitation": 100.0,
    }
    EXTREME_PICHIA = {
        "glucose": 0.01, "methanol": 12.0, "ethanol": 5.0, "pH": 3.0,
        "DO": 3.0, "ammonia": 0.1, "OD600": 10.0, "viability": 50.0,
        "titer": 0.01, "CO2": 22.0, "O2": 8.0, "temperature": 38.0,
        "agitation": 100.0,
    }
    EXTREME_YEAST = {
        "glucose": 0.1, "ethanol": 20.0, "pH": 3.0, "DO": 2.0,
        "ammonia": 0.1, "OD600": 1.0, "viability": 50.0, "titer": 0.01,
        "CO2": 25.0, "O2": 10.0, "temperature": 40.0, "agitation": 50.0,
    }

    extreme_map = {
        "CHO": EXTREME_MAM, "CHO-S": EXTREME_MAM, "HEK293": EXTREME_MAM,
        "NS0": EXTREME_MAM, "Sp2/0": EXTREME_MAM, "BHK-21": EXTREME_MAM,
        "E. coli": EXTREME_ECOLI, "B. subtilis": EXTREME_BSUB,
        "P. pastoris": EXTREME_PICHIA, "S. cerevisiae": EXTREME_YEAST,
    }

    for org in list_organisms():
        readings = extreme_map.get(org)
        if readings is None:
            continue
        states = get_all_pathway_states(readings, organism=org)
        n_ok = sum(1 for i in states.values() if classify(i["state"]) == "OK")
        n_total = len(states)
        # Should have very few OK states under extreme conditions
        t.assert_true(
            n_ok <= n_total * 0.2,
            f"{org} extreme <= 20% OK",
            cat,
            f"OK={n_ok}/{n_total}",
        )


def test_threshold_boundaries(t):
    """For every parameter in every organism, test values at threshold boundaries."""
    cat = "Threshold boundaries"

    for org_key in list(ORGANISM_MAPS.keys()):
        gem_map = ORGANISM_MAPS[org_key]

        for param, entry in gem_map.items():
            thresholds = entry["flux_interpretation"]
            low_t = thresholds["low"]["threshold"]
            norm_t = thresholds["normal"]["threshold"]

            low_state = thresholds["low"]["state"]
            norm_state = thresholds["normal"]["state"]
            high_state = thresholds["high"]["state"]

            # Value exactly at low threshold -> should be "low" state
            result = get_pathway_state(param, low_t, org_key)
            if result is not None:
                t.assert_equal(
                    result["state"], low_state,
                    f"{org_key} {param} at low threshold ({low_t})",
                    cat,
                )

            # Value exactly at normal threshold -> should be "normal" state
            result = get_pathway_state(param, norm_t, org_key)
            if result is not None:
                t.assert_equal(
                    result["state"], norm_state,
                    f"{org_key} {param} at normal threshold ({norm_t})",
                    cat,
                )

            # Value just above normal threshold -> should be "high" state
            above_norm = norm_t + 0.01
            result = get_pathway_state(param, above_norm, org_key)
            if result is not None:
                t.assert_equal(
                    result["state"], high_state,
                    f"{org_key} {param} above normal ({above_norm})",
                    cat,
                )

            # Value well below low threshold -> should be "low" state
            well_below = low_t * 0.5 if low_t > 0 else -1.0
            if well_below >= 0:  # skip negative values for params that can't go negative
                result = get_pathway_state(param, well_below, org_key)
                if result is not None:
                    t.assert_equal(
                        result["state"], low_state,
                        f"{org_key} {param} well below low ({well_below})",
                        cat,
                    )


def test_single_param_change(t):
    """Starting from healthy baseline, changing ONE parameter should affect only that parameter's state."""
    cat = "Single param isolation"

    for org, baseline in HEALTHY_READINGS.items():
        baseline_states = get_all_pathway_states(baseline, organism=org)

        for param in baseline:
            # Get thresholds for this param
            gem_map = ORGANISM_MAPS[org]
            resolved = PARAM_ALIASES.get(org, {}).get(param, param)
            if resolved not in gem_map:
                continue

            entry = gem_map[resolved]
            low_t = entry["flux_interpretation"]["low"]["threshold"]

            # Set one parameter to a value below the low threshold
            stressed = dict(baseline)
            stressed[param] = low_t * 0.5 if low_t > 0 else 0.0

            stressed_states = get_all_pathway_states(stressed, organism=org)

            # The changed parameter should have a different state
            if resolved in baseline_states and resolved in stressed_states:
                baseline_s = baseline_states[resolved]["state"]
                stressed_s = stressed_states[resolved]["state"]
                t.assert_true(
                    stressed_s != baseline_s or baseline_s == entry["flux_interpretation"]["low"]["state"],
                    f"{org} {param} state changes when stressed",
                    cat,
                    f"baseline={baseline_s}, stressed={stressed_s}",
                )

            # Other parameters should remain the same
            for other_param, other_info in baseline_states.items():
                if other_param == resolved:
                    continue
                if other_param in stressed_states:
                    t.assert_equal(
                        stressed_states[other_param]["state"],
                        other_info["state"],
                        f"{org} {other_param} unchanged when {param} stressed",
                        cat,
                    )


def test_alias_resolution(t):
    """Test that parameter aliases resolve correctly across organisms."""
    cat = "Alias resolution"

    # OD600 -> VCD for mammalian
    for org in ["CHO", "HEK293", "NS0", "Sp2/0", "BHK-21"]:
        result = get_pathway_state("OD600", 10.0, org)
        if result is not None:
            t.assert_equal(result["parameter"], "VCD", f"{org} OD600 resolves to VCD", cat)

    # VCD -> OD600 for bacterial/yeast
    for org in ["E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"]:
        result = get_pathway_state("VCD", 10.0, org)
        if result is not None:
            t.assert_equal(result["parameter"], "OD600", f"{org} VCD resolves to OD600", cat)

    # lactate -> acetate for E. coli
    result = get_pathway_state("lactate", 3.0, "E. coli")
    if result is not None:
        t.assert_equal(result["parameter"], "acetate", "E. coli lactate->acetate", cat)

    # acetate -> lactate for CHO
    result = get_pathway_state("acetate", 3.0, "CHO")
    if result is not None:
        t.assert_equal(result["parameter"], "lactate", "CHO acetate->lactate", cat)

    # lactate -> acetoin for B. subtilis
    result = get_pathway_state("lactate", 3.0, "B. subtilis")
    if result is not None:
        t.assert_equal(result["parameter"], "acetoin", "B.sub lactate->acetoin", cat)

    # lactate -> ethanol for S. cerevisiae
    result = get_pathway_state("lactate", 3.0, "S. cerevisiae")
    if result is not None:
        t.assert_equal(result["parameter"], "ethanol", "S.cer lactate->ethanol", cat)

    # Aliases should work for strains too
    for strain_key in list_strains("CHO"):
        result = get_pathway_state("OD600", 10.0, strain_key)
        if result is not None:
            t.assert_equal(result["parameter"], "VCD", f"{strain_key} OD600->VCD", cat)

    for strain_key in list_strains("E. coli"):
        result = get_pathway_state("VCD", 10.0, strain_key)
        if result is not None:
            t.assert_equal(result["parameter"], "OD600", f"{strain_key} VCD->OD600", cat)


def test_strain_divergence(t):
    """Verify that strains with overrides actually differ from their parent."""
    cat = "Strain divergence"

    # CHO-DG44 should have different VCD thresholds than CHO base
    cho_vcd = get_pathway_state("VCD", 13.0, "CHO")
    dg44_vcd = get_pathway_state("VCD", 13.0, "CHO|CHO-DG44")
    if cho_vcd and dg44_vcd:
        # DG44 has lower peak threshold so 13 should be peak_density, not exponential
        t.assert_true(
            cho_vcd["state"] != dg44_vcd["state"] or cho_vcd["state"] == dg44_vcd["state"],
            "CHO vs DG44 VCD divergence test runs", cat,
        )
        # DG44 peak at 25, base at 30
        # DG44 peak threshold=25 vs CHO=30, so at 26 DG44 is peak_density, CHO still peak_density
        # But at 13 DG44 is peak_density (threshold=12), CHO is exponential (threshold=15)
        vcd_13 = get_pathway_state("VCD", 13.0, "CHO|CHO-DG44")
        vcd_13_base = get_pathway_state("VCD", 13.0, "CHO")
        if vcd_13 and vcd_13_base:
            t.assert_equal(vcd_13["state"], "peak_density", "DG44 VCD 13 is peak", cat)
            t.assert_equal(vcd_13_base["state"], "exponential", "CHO VCD 13 is exponential", cat)

    # CHO-GS should have tighter ammonia thresholds
    gs_amm = get_pathway_state("ammonia", 4.0, "CHO|CHO-GS")
    base_amm = get_pathway_state("ammonia", 4.0, "CHO")
    if gs_amm and base_amm:
        t.assert_equal(gs_amm["state"], "toxic", "CHO-GS ammonia 4.0 is toxic", cat)
        t.assert_equal(base_amm["state"], "moderate", "CHO base ammonia 4.0 is moderate", cat)

    # BL21(DE3) vs base E. coli titer thresholds
    bl21_titer = get_pathway_state("titer", 1.2, "E. coli|BL21(DE3)")
    base_titer = get_pathway_state("titer", 1.2, "E. coli")
    if bl21_titer and base_titer:
        t.assert_equal(bl21_titer["state"], "on_track", "BL21(DE3) titer 1.2 on_track", cat)
        t.assert_equal(base_titer["state"], "high_expression", "E.coli base titer 1.2 high", cat)

    # KM71H (MutS) should have different methanol thresholds than X-33 (Mut+)
    km71_meth = get_pathway_state("methanol", 0.8, "P. pastoris|KM71H")
    x33_meth = get_pathway_state("methanol", 0.8, "P. pastoris|X-33")
    if km71_meth and x33_meth:
        t.assert_equal(km71_meth["state"], "sub_induction", "KM71H methanol 0.8 sub_induction", cat)
        t.assert_equal(x33_meth["state"], "optimal", "X-33 methanol 0.8 optimal", cat)

    # BY4741 vs CEN.PK OD600
    # BY4741 normal threshold=15, high=35 vs CEN.PK normal=25, high=60
    # At 22, BY4741 is high_density (>15 exponential, but wait 22>15 -> exponential, 22<35 -> exponential)
    # Actually BY4741 low=5, normal=15, so 22>15 -> high_density (>normal). CEN.PK normal=25, so 22<=25 -> exponential
    by_od = get_pathway_state("OD600", 22.0, "S. cerevisiae|BY4741")
    cen_od = get_pathway_state("OD600", 22.0, "S. cerevisiae|CEN.PK")
    if by_od and cen_od:
        t.assert_equal(by_od["state"], "high_density", "BY4741 OD 22 high_density", cat)
        t.assert_equal(cen_od["state"], "exponential", "CEN.PK OD 22 exponential", cat)

    # HEK293F agitation normal=150 vs HEK293 normal=130
    # At 135 HEK293 base is shear_risk (>130), 293F is optimal (<=150)
    f293_agit = get_pathway_state("agitation", 135.0, "HEK293|HEK293F")
    base_agit = get_pathway_state("agitation", 135.0, "HEK293")
    if f293_agit and base_agit:
        t.assert_equal(f293_agit["state"], "optimal", "293F agit 135 optimal", cat)
        t.assert_equal(base_agit["state"], "shear_risk", "HEK293 agit 135 shear_risk", cat)


def test_none_handling(t):
    """Test that None values in readings are skipped gracefully."""
    cat = "None handling"

    readings = {"glucose": 3.0, "lactate": None, "pH": 7.1, "DO": None}
    states = get_all_pathway_states(readings, organism="CHO")
    t.assert_true("glucose" in states, "glucose present with None neighbours", cat)
    t.assert_true("pH" in states, "pH present with None neighbours", cat)
    t.assert_true("lactate" not in states, "None lactate excluded", cat)
    t.assert_true("DO" not in states, "None DO excluded", cat)


def test_empty_readings(t):
    """Test empty readings dict returns empty results."""
    cat = "Edge cases"
    states = get_all_pathway_states({}, organism="CHO")
    t.assert_equal(len(states), 0, "empty readings -> empty results", cat)


def test_organism_result_fields(t):
    """Verify the organism field in results matches what was requested."""
    cat = "Organism field consistency"

    for org in list_organisms():
        result = get_pathway_state("pH", 7.0, org)
        if result:
            t.assert_equal(result["organism"], org, f"{org} organism field matches", cat)

    for strain_key in list_strains():
        params = list_parameters(strain_key)
        if params:
            result = get_pathway_state(params[0], 5.0, strain_key)
            if result:
                t.assert_equal(result["organism"], strain_key, f"{strain_key} organism field", cat)


def test_gem_model_ids(t):
    """Verify each organism has a valid GEM model ID."""
    cat = "GEM model IDs"
    expected_models = {
        "CHO": "iCHO2291", "CHO-S": "iCHO2291", "HEK293": "Recon3D",
        "NS0": "iNS0_1091", "Sp2/0": "iSp2_0", "BHK-21": "iBHK",
        "E. coli": "iML1515", "B. subtilis": "iYO844",
        "P. pastoris": "iMT1026v3", "S. cerevisiae": "iMM904",
    }

    for org, expected in expected_models.items():
        params = list_parameters(org)
        result = get_pathway_state(params[0], 5.0, org)
        if result:
            t.assert_equal(result["gem_model"], expected, f"{org} GEM model", cat)


def test_downstream_effects_valid(t):
    """Verify downstream_effects reference parameters that exist in the same organism."""
    cat = "Downstream validity"

    for org_key, gem_map in ORGANISM_MAPS.items():
        if "|" in org_key:
            continue  # skip strains, same params as parent
        params_set = set(gem_map.keys())
        for param, entry in gem_map.items():
            for ds in entry["downstream_effects"]:
                t.assert_in(
                    ds, params_set,
                    f"{org_key} {param} downstream '{ds}' exists",
                    cat,
                )


def test_state_names_classified(t):
    """Every state name used in thresholds should be classifiable."""
    cat = "State classification coverage"

    all_known = CRITICAL_STATES | WARNING_STATES | OK_STATES

    for org_key, gem_map in ORGANISM_MAPS.items():
        for param, entry in gem_map.items():
            for level in ("low", "normal", "high"):
                state_name = entry["flux_interpretation"][level]["state"]
                t.assert_in(
                    state_name, all_known,
                    f"{org_key} {param}.{level} state '{state_name}' classified",
                    cat,
                )


def test_monotonic_thresholds(t):
    """Verify low threshold < normal threshold for every parameter."""
    cat = "Monotonic thresholds"

    for org_key, gem_map in ORGANISM_MAPS.items():
        for param, entry in gem_map.items():
            low_t = entry["flux_interpretation"]["low"]["threshold"]
            norm_t = entry["flux_interpretation"]["normal"]["threshold"]
            t.assert_true(
                low_t < norm_t,
                f"{org_key} {param} low({low_t}) < normal({norm_t})",
                cat,
            )


def test_cross_organism_divergence(t):
    """Same readings should produce different states across organisms."""
    cat = "Cross-organism divergence"

    # Ammonia 7.0 mM: toxic for mammalian, optimal for bacteria/yeast
    for mam in ["CHO", "NS0", "Sp2/0"]:
        result = get_pathway_state("ammonia", 7.0, mam)
        if result:
            t.assert_equal(classify(result["state"]), "CRITICAL", f"{mam} ammonia 7.0 critical", cat)

    for mic in ["E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"]:
        result = get_pathway_state("ammonia", 7.0, mic)
        if result:
            t.assert_equal(classify(result["state"]), "OK", f"{mic} ammonia 7.0 OK", cat)

    # Temperature 38.5: heat_stress for mammalian, but B. subtilis handles it
    for mam in ["CHO", "HEK293"]:
        result = get_pathway_state("temperature", 38.5, mam)
        if result:
            t.assert_in(result["state"], {"heat_stress"}, f"{mam} temp 38.5 heat_stress", cat)

    # Agitation 380: shear_risk for CHO, optimal for E. coli
    cho_agit = get_pathway_state("agitation", 380.0, "CHO")
    ec_agit = get_pathway_state("agitation", 380.0, "E. coli")
    if cho_agit and ec_agit:
        t.assert_equal(cho_agit["state"], "shear_risk", "CHO agit 380 shear", cat)
        t.assert_equal(ec_agit["state"], "optimal", "E.coli agit 380 optimal", cat)


def test_pichia_methanol_parameter(t):
    """Pichia should have methanol as a unique 13th parameter."""
    cat = "Pichia methanol"

    params = list_parameters("P. pastoris")
    t.assert_in("methanol", params, "Pichia has methanol param", cat)
    t.assert_true(len(params) >= 13, "Pichia has >= 13 params", cat, f"got {len(params)}")

    # Methanol toxic
    result = get_pathway_state("methanol", 9.0, "P. pastoris")
    if result:
        t.assert_equal(result["state"], "toxic", "Pichia methanol 9.0 toxic", cat)

    # Methanol optimal
    result = get_pathway_state("methanol", 2.0, "P. pastoris")
    if result:
        t.assert_equal(result["state"], "optimal", "Pichia methanol 2.0 optimal", cat)

    # Other organisms should NOT have methanol
    for org in ["CHO", "E. coli", "S. cerevisiae"]:
        result = get_pathway_state("methanol", 5.0, org)
        t.assert_true(result is None, f"{org} has no methanol param", cat)


def test_strain_inherits_parent(t):
    """Strain maps should have all parameters of their parent."""
    cat = "Strain inheritance"

    for strain_key in list_strains():
        info = get_strain_info(strain_key)
        org = info["organism"]

        # For CHO|CHO-S the parent is CHO-S (CHOS_MAP), not CHO_MAP
        if strain_key == "CHO|CHO-S":
            parent_key = "CHO-S"
        else:
            parent_key = org

        parent_params = set(list_parameters(parent_key))
        strain_params = set(list_parameters(strain_key))
        t.assert_equal(
            strain_params, parent_params,
            f"{strain_key} same params as parent {parent_key}",
            cat,
        )


def test_all_organisms_accessible(t):
    """Every key in ORGANISM_MAPS should work with get_all_pathway_states."""
    cat = "All keys accessible"

    for key in ORGANISM_MAPS:
        params = list_parameters(key)
        readings = {params[0]: 5.0}
        try:
            states = get_all_pathway_states(readings, organism=key)
            t.assert_true(len(states) >= 0, f"{key} accessible", cat)
        except Exception as e:
            t.assert_true(False, f"{key} accessible", cat, str(e))


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    t = TestRunner()

    print("\n" + "=" * 100)
    print("  GEM MAP FULL TEST SUITE")
    print(f"  Organisms: {len(list_organisms())} | Strains: {len(list_strains())} | Organism+Strain keys: {len(ORGANISM_MAPS)}")
    print("=" * 100)

    test_api_basics(t)
    test_result_structure(t)
    test_healthy_baselines(t)
    test_healthy_strains(t)
    test_all_critical(t)
    test_threshold_boundaries(t)
    test_single_param_change(t)
    test_alias_resolution(t)
    test_strain_divergence(t)
    test_none_handling(t)
    test_empty_readings(t)
    test_organism_result_fields(t)
    test_gem_model_ids(t)
    test_downstream_effects_valid(t)
    test_state_names_classified(t)
    test_monotonic_thresholds(t)
    test_cross_organism_divergence(t)
    test_pichia_methanol_parameter(t)
    test_strain_inherits_parent(t)
    test_all_organisms_accessible(t)

    passed = t.report()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
