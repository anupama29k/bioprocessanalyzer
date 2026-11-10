"""Tests for modules/process_scaleup.py.   python test_scaleup.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modules import process_scaleup as ps  # noqa: E402

res = []
def check(name, cond, detail=""):
    res.append(cond); print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")

v = ps.Vessel(volume_L=1000)
vs = ps.superficial_velocity(v)
for coal in (True, False):
    k = ps.kla_from_PV(1500, vs, coal)
    check(f"kLa ↔ P/V round trip ({'coalescing' if coal else 'non-coalescing'})",
          abs(ps.PV_for_kla(k, vs, coal) - 1500) < 1e-6, f"kLa {k:.0f} h⁻¹")
N = ps.N_for_PV(v, 1200)
check("N ↔ P/V round trip", abs(ps.gassed_PV(v, N) - 1200) < 1e-6, f"{N*60:.0f} rpm")

c0 = ps.cstar(ps.Vessel(volume_L=1))
c1 = ps.cstar(ps.Vessel(volume_L=1, head_pressure_bar_g=1.01325))
c2 = ps.cstar(ps.Vessel(volume_L=1, o2_fraction=0.42))
check("c* ≈ 0.21 mmol/L at bench scale, air, 37 °C", abs(c0 - 0.21) < 0.005, f"{c0:.3f}")
check("c* doubles with +1 atm back-pressure", abs(c1 / c0 - 2) < 0.02, f"×{c1/c0:.2f}")
check("c* doubles with 42 % O₂", abs(c2 / c0 - 2) < 1e-9)

p = ps.ProcessData(mu_h=0.5, x_max_gL=10, our_peak=100, q_o2=10)
r = ps.evaluate(p, v)
check("metabolic heat: 100 mmol O₂/L/h ≈ 12.8 kW/m³", abs(r["Metabolic heat (W/m³)"] - 12778) < 5,
      f"{r['Metabolic heat (W/m³)']:.0f} W/m³")
check("biomass ceiling = OTR_max / q_O2",
      abs(r["Max biomass before O₂ limitation (g/L)"] - r["OTR max (mmol/L/h)"] / 10) < 1e-9)
check("fed-batch μ never exceeds μ_max", r["Fed-batch μ max at target X (h⁻¹)"] <= 0.5)

lo = ps.evaluate(p, v, x_target_gL=5); hi = ps.evaluate(p, v, x_target_gL=80)
check("raising target biomass raises required kLa",
      hi["kLa required (h⁻¹)"] > lo["kLa required (h⁻¹)"])
check("80 g/L at q_O2 10 fails O₂ in 1 m³", not hi["o2_ok"])
check("mixing time grows with scale",
      ps.evaluate(p, ps.Vessel(volume_L=10000))["Mixing time (s)"] > ps.evaluate(p, ps.Vessel(volume_L=100))["Mixing time (s)"])

print(f"\n{sum(res)}/{len(res)} passed"); sys.exit(0 if all(res) else 1)
