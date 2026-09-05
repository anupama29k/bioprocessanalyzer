"""Full end-to-end integration test of the Bioprocess Analyser."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
import importlib

import modules.calcs as calcs; importlib.reload(calcs)
import views.data_import as di; importlib.reload(di)
import views.homepage as hp; importlib.reload(hp)
import views.scale_up as su; importlib.reload(su)
import data_manager as dmmod; importlib.reload(dmmod)

from modules.calcs import (compute_growth_kinetics, compute_productivity,
                            compute_mass_balance, check_carbon_balance,
                            ScaleUpEngine, ScaleUpParameters,
                            SUBSTRATE_DB, BIOMASS_DB, PRODUCT_DB)
from views.data_import import auto_detect_mapping
from data_manager import DataManager

passed = 0
total = 0

def check(name, condition):
    global passed, total
    total += 1
    if condition:
        passed += 1
        print(f"   PASS: {name}")
    else:
        print(f"   FAIL: {name}")

print("FULL APP INTEGRATION TEST")
print("=" * 70)

# 1. DATA IMPORT
print("\n1. DATA IMPORT")
df = pd.read_csv("s_cerevisiae_aerobic.csv")
cm = auto_detect_mapping(df.columns.tolist())
check("CSV loaded", df.shape[0] == 48)
check("time mapped", cm.get("time") == "Time_h")
check("od mapped", cm.get("od") == "OD_600nm")
check("substrate mapped", cm.get("substrate") == "Glucose_gL")
check("product mapped", cm.get("product") == "Ethanol_gL")

# 2. GROWTH KINETICS
print("\n2. GROWTH KINETICS")
t = df["Time_h"].values
od = df["OD_600nm"].values
gk = compute_growth_kinetics(t, od, dcw_factor=0.4)
check(f"mu = {gk['mu']:.4f} (expect ~0.40)", 0.30 < gk["mu"] < 0.50)
check(f"R2 = {gk['r2']:.4f}", gk["r2"] > 0.95)
check(f"quality = {gk['quality_score']}", gk["quality_score"] >= 70)
check(f"diauxic = {gk['is_diauxic']}", not gk["is_diauxic"])
check(f"phases = {len(gk['phases'])}", len(gk["phases"]) >= 1)

# 3. PRODUCTIVITY
print("\n3. PRODUCTIVITY")
prod = df["Ethanol_gL"].values
pr = compute_productivity(t, prod, gk["dcw"])
check(f"titer = {pr['titer']:.3f} g/L", pr["titer"] > 5.0)
check(f"STY = {pr['sty']:.4f} g/L/h", pr["sty"] > 0)

# 4. CARBON BALANCE (quick)
print("\n4. CARBON BALANCE")
r_cb = check_carbon_balance(df, "OD_600nm", "Glucose_gL", "Ethanol_gL",
                             conv_factor=0.4, sub_C=6, sub_MW=180.16,
                             prod_C=2, prod_MW=46.07, C_biomass=0.48)
check(f"recovery = {r_cb['recovery']:.1f}%", 40 < r_cb["recovery"] < 110)
check("C_substrate > 0", r_cb["C_substrate"] > 0)
check("C_products > 0", r_cb["C_products"] > 0)

# 5. FULL MASS BALANCE
print("\n5. FULL MASS BALANCE")
sdb = SUBSTRATE_DB["Glucose"]
bm = BIOMASS_DB["S. cerevisiae"]
pdb = PRODUCT_DB["Ethanol"]
sub = df["Glucose_gL"].values
tail = max(1, len(sub) // 10)
s0 = float(np.median(sub[:tail]))
sf = float(np.median(sub[-tail:]))
dx = max((od[-1] - od[0]) * 0.4, 0.001)
r_mb = compute_mass_balance(
    [{"name": "Glucose", "s0": s0, "sf": sf,
      "C": sdb["C"], "H": sdb["H"], "O": sdb["O"], "N": sdb["N"],
      "MW": sdb["MW"], "gamma": sdb["gamma"]}],
    [{"name": "Ethanol", "conc": max(float(prod[-1]), 0),
      "C": pdb["C"], "H": pdb.get("H", 6), "O": pdb.get("O", 1), "N": 0,
      "MW": pdb["MW"], "gamma": pdb["gamma"]}],
    {"dx": dx, "C": bm["C"], "H": bm["H"], "O": bm["O"], "N": bm["N"],
     "MW": bm["MW"], "gamma": bm["gamma"]},
    {"our": 5.0, "cer": 8.0, "tf": 23.5}, mode="Batch")
check(f"closure = {r_mb['closure']:.1f}%", r_mb["closure"] > 0)
check(f"RQ = {r_mb['RQ']:.2f}", r_mb["RQ"] > 0)
check("yields computed", r_mb.get("yields") is not None)

# 6. SCALE-UP ENGINE
print("\n6. SCALE-UP ENGINE")
engine = ScaleUpEngine()
lab = ScaleUpParameters(
    volume_L=2.5, mu_max_h=float(gk["mu"]),
    yield_g_g=0.42, max_od=float(gk["max_od"]),
    agitation_rpm=500, aeration_vvm=1.0, power_input_W_m3=1500,
    kLa_h=200, vessel_diameter_m=0.15, impeller_diameter_m=0.05,
    aspect_ratio=2.0, OUR=8.5)
r_su = engine.calculate_scale_up(lab, 1000, "power_per_volume")
bp = r_su["biological_performance"]
op = r_su["operational_parameters"]
ot = r_su["oxygen_transfer"]
check(f"mu_pred = {bp['mu_max_h']:.3f}", bp["mu_max_h"] > 0)
check(f"efficiency = {bp['scale_efficiency_percent']:.0f}%", bp["scale_efficiency_percent"] > 50)
check(f"rpm = {op['agitation_rpm']:.0f}", op["agitation_rpm"] > 0)
check(f"kLa = {ot['kLa_predicted_h']:.0f}", ot["kLa_predicted_h"] > 0)
check(f"risks = {len(r_su['risk_assessment'])}", isinstance(r_su["risk_assessment"], list))
check(f"recs = {len(r_su['recommendations'])}", isinstance(r_su["recommendations"], list))

# Multi-scale
df_su = engine.scale_multiple_sizes(lab, [10, 100, 1000, 5000])
check(f"multi-scale: {len(df_su)} rows", len(df_su) == 4)

# 7. LITERATURE VALIDATION
print("\n7. LITERATURE VALIDATION")
val_df = pd.read_csv("scale_up_validation_dataset.csv")
n_lit_pass = 0
n_lit_total = 0
for _, row in val_df.iterrows():
    lab_v = ScaleUpParameters(
        volume_L=row["lab_volume_L"], mu_max_h=row["lab_mu_max_h"],
        yield_g_g=row["lab_yield_g_g"], max_od=row["lab_max_od"],
        agitation_rpm=row["lab_agitation_rpm"],
        aeration_vvm=max(row["lab_aeration_vvm"], 0.01),
        power_input_W_m3=row["lab_power_input_W_m3"],
        kLa_h=row["lab_kLa_h"], vessel_diameter_m=row["lab_vessel_diameter_m"],
        impeller_diameter_m=row["lab_impeller_diameter_m"],
        aspect_ratio=row["lab_aspect_ratio"], OUR=8.5)
    r_v = engine.calculate_scale_up(lab_v, row["target_volume_L"], row["scaling_criterion"])
    vbp = r_v["biological_performance"]
    for exp, pred in [(row["expected_mu_max_h"], vbp["mu_max_h"]),
                      (row["expected_yield_g_g"], vbp["yield_g_g"]),
                      (row["expected_max_od"], vbp["max_od"])]:
        n_lit_total += 1
        if exp > 0 and abs(pred - exp) / exp < 0.25:
            n_lit_pass += 1
check(f"literature: {n_lit_pass}/{n_lit_total} within 25%", n_lit_pass >= 16)

# 8. SENSOR ALIASES
print("\n8. SENSOR ALIASES")
alias_tests = [
    (["Time_h", "OD_600nm", "Glucose_gL", "Ethanol_gL"], {"time", "od", "substrate", "product"}),
    (["Time_h", "OD_600nm", "Acetate_gL", "PHA_gL"], {"time", "od", "substrate", "product"}),
    (["Time_h", "OD_600nm", "Protein_gL"], {"time", "od", "product"}),
    (["Time_h", "OD_600nm", "Oil_gL", "PHB_gL"], {"time", "od", "substrate", "product"}),
    (["Time_h", "OD_600nm", "Glucose_gL", "Lipid_gL"], {"time", "od", "substrate", "product"}),
    (["Time_h", "VCD_1e6_per_mL", "Glucose_gL", "mAb_gL"], {"time", "vcd", "substrate", "product"}),
]
for cols, expected_keys in alias_tests:
    acm = auto_detect_mapping(cols)
    ok = expected_keys.issubset(set(acm.keys()))
    check(f"{cols[2]} -> {acm.get(list(expected_keys - {'time','od','vcd'})[0] if expected_keys - {'time','od','vcd'} else 'ok', '?')}", ok)

# 9. MODULES CHECK
print("\n9. MODULE INTEGRITY")
check("homepage.render", hasattr(hp, "render"))
check("homepage._render_run_row", hasattr(hp, "_render_run_row"))
check("scale_up.render", hasattr(su, "render"))
check("scale_up.ScaleUpVisualizer", hasattr(su, "ScaleUpVisualizer"))
check(f"scale_up.LITERATURE = {len(su.LITERATURE)} presets", len(su.LITERATURE) >= 6)
check("DataManager.get_runs_summary", hasattr(DataManager, "get_runs_summary"))
check("DataManager.search_runs", hasattr(DataManager, "search_runs"))

# ====================================================================
print("\n" + "=" * 70)
print(f"RESULT: {passed}/{total} PASSED")
if passed == total:
    print("ALL INTEGRATION TESTS PASSED")
    print("App is fully functional at http://localhost:8501")
else:
    print(f"{total - passed} FAILURES - investigate above")
