"""
Run-specific scale-up: will *this* process work in *that* vessel?

Takes the oxygen demand, growth rate and biomass measured in a run and checks
a target stirred tank against the three constraints that usually break first
on scale-up — oxygen transfer, heat removal and mixing — then derives the
operating window (agitation, maximum biomass, fed-batch μ setpoint).

Correlations (SI units inside, results reported in process units)
----------------------------------------------------------------
* Ungassed power      P = Np ρ N³ Di⁵ per impeller; gassed P_g = f_g · P
* kLa (van't Riet 1979, Ind Eng Chem Process Des Dev 18:357)
      coalescing        kLa = 0.026 (P_g/V)^0.4  v_s^0.5      [s⁻¹]
      non-coalescing    kLa = 0.002 (P_g/V)^0.7  v_s^0.2      [s⁻¹]
  Fermentation broths fall between the two; both are reported.
* O₂ solubility       c* ∝ O₂ partial pressure (Henry): air at 1 atm, 37 °C
                      ≈ 0.21 mmol/L, scaled by headspace pressure, mean
                      hydrostatic head and O₂ enrichment.
* Metabolic heat      460 kJ per mol O₂ consumed (Cooney, Wang & Wang 1969,
                      Biotechnol Bioeng 11:269)
* Jacket cooling      Q = U·A·ΔT, A = wetted wall + bottom
* Mixing time         t_m = 5.9 T^(2/3) ε^(-1/3) (Di/T)^(-1/3)
                      (Nienow 1997, Chem Eng Sci 52:2557; single impeller,
                      H/T = 1; scaled by (H/T)^1 for taller tanks as an
                      approximation)
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

RHO = 1000.0               # kg/m³
G = 9.81
HEAT_PER_O2 = 460.0        # kJ/mol O₂  (Cooney 1969)
CSTAR_AIR_37C = 0.21       # mmol/L at 1 atm air, 37 °C


@dataclass
class ProcessData:
    """What the run tells us (per litre of broth)."""
    mu_h: float                    # specific growth rate in exponential phase
    x_max_gL: float                # highest biomass reached (g DCW/L)
    our_peak: float                # mmol O₂ L⁻¹ h⁻¹, highest measured (or estimated)
    q_o2: float                    # mmol O₂ gDCW⁻¹ h⁻¹ during exponential growth
    temp_C: float = 37.0
    source: str = "measured"       # how q_O2 was obtained


@dataclass
class Vessel:
    volume_L: float = 1000.0       # working volume
    hd: float = 2.5                # liquid height / tank diameter
    di_dt: float = 0.33            # impeller / tank diameter
    n_imp: int = 2
    Np: float = 5.0                # Rushton ~5, pitched blade ~1.3, hydrofoil ~0.3–0.8
    gassed_factor: float = 0.6     # P_g / P
    vvm: float = 1.0
    max_PV_W_m3: float = 3000.0    # motor / design limit
    max_tip_m_s: float = 6.0
    do_setpoint_pct: float = 30.0
    head_pressure_bar_g: float = 0.0
    o2_fraction: float = 0.21      # inlet gas O₂ mole fraction (enrichment)
    U_W_m2K: float = 400.0         # jacket overall heat-transfer coefficient
    coolant_C: float = 15.0
    coalescing: bool = True

    @property
    def V(self):  # m³
        return self.volume_L / 1000

    @property
    def T(self):  # tank diameter, m
        return (4 * self.V / (np.pi * self.hd)) ** (1 / 3)

    @property
    def H(self):
        return self.hd * self.T

    @property
    def Di(self):
        return self.di_dt * self.T


def cstar(v: Vessel, temp_C: float = 37.0) -> float:
    """O₂ saturation (mmol/L) at mean liquid pressure and inlet O₂ fraction."""
    p_head = 1.01325 + v.head_pressure_bar_g
    p_mean = p_head + RHO * G * v.H / 2 / 1e5          # bar, mid-depth
    t_corr = 1 + 0.0125 * (37.0 - temp_C)             # ~1.25 %/°C solubility change
    return CSTAR_AIR_37C * (p_mean / 1.01325) * (v.o2_fraction / 0.21) * t_corr


def superficial_velocity(v: Vessel) -> float:
    """m/s"""
    return v.vvm * v.V / 60 / (np.pi / 4 * v.T ** 2)


def gassed_PV(v: Vessel, N_rps: float) -> float:
    """W/m³"""
    return v.gassed_factor * v.Np * RHO * N_rps ** 3 * v.Di ** 5 * v.n_imp / v.V


def kla_from_PV(PgV: float, vs: float, coalescing: bool = True) -> float:
    """h⁻¹"""
    if coalescing:
        return 0.026 * PgV ** 0.4 * vs ** 0.5 * 3600
    return 0.002 * PgV ** 0.7 * vs ** 0.2 * 3600


def PV_for_kla(kla_h: float, vs: float, coalescing: bool = True) -> float:
    """Gassed W/m³ needed for a kLa (inverse of van't Riet)."""
    k = kla_h / 3600
    if coalescing:
        return (k / (0.026 * vs ** 0.5)) ** (1 / 0.4)
    return (k / (0.002 * vs ** 0.2)) ** (1 / 0.7)


def N_for_PV(v: Vessel, PgV: float) -> float:
    """rev/s for a gassed P/V"""
    return (PgV * v.V / (v.gassed_factor * v.Np * RHO * v.Di ** 5 * v.n_imp)) ** (1 / 3)


def mixing_time(v: Vessel, PgV: float) -> float:
    """s — Nienow correlation, scaled linearly with H/T for multi-impeller tanks."""
    eps = PgV / RHO                                     # W/kg
    return 5.9 * v.T ** (2 / 3) * eps ** (-1 / 3) * v.di_dt ** (-1 / 3) * max(v.hd, 1.0)


def evaluate(p: ProcessData, v: Vessel, x_target_gL: float | None = None) -> dict:
    """Full operating-window assessment for one vessel.

    x_target_gL: biomass the scaled process should reach (default: the run's).
    Peak O₂ demand is the larger of the run's measured peak and q_O2 · x_target.
    """
    x_t = x_target_gL or p.x_max_gL
    our_peak = max(p.our_peak, p.q_o2 * x_t)
    cs = cstar(v, p.temp_C)
    drive = cs * (1 - v.do_setpoint_pct / 100)          # mmol/L
    vs = superficial_velocity(v)

    # Agitation ceiling: the lower of P/V limit and tip-speed limit
    N_tip = v.max_tip_m_s / (np.pi * v.Di)
    N_pv = N_for_PV(v, v.max_PV_W_m3)
    N_max = min(N_tip, N_pv)
    limit_by = "tip speed" if N_tip < N_pv else "P/V"
    PgV_max = gassed_PV(v, N_max)
    kla_max = kla_from_PV(PgV_max, vs, v.coalescing)
    kla_max_alt = kla_from_PV(PgV_max, vs, not v.coalescing)
    otr_max = kla_max * drive

    # Requirement at the run's peak OUR
    kla_req = our_peak / drive
    PgV_req = PV_for_kla(kla_req, vs, v.coalescing)
    N_req = N_for_PV(v, PgV_req)
    o2_ok = kla_req <= kla_max

    # Biomass ceiling from O₂ transfer while growing at μ
    x_o2_lim = otr_max / p.q_o2 if p.q_o2 > 0 else float("inf")
    # Fed-batch: highest μ setpoint at x_max that O₂ transfer supports,
    # assuming q_O2 ∝ μ (Y_X/O constant, maintenance neglected)
    y_xo = p.mu_h / p.q_o2 if p.q_o2 > 0 else None     # g DCW per mmol O₂
    mu_fb_max = y_xo * otr_max / x_t if (y_xo and x_t > 0) else None
    if mu_fb_max is not None:
        mu_fb_max = min(mu_fb_max, p.mu_h)   # cannot exceed the strain's μ_max

    # Heat at peak OUR (operating at the required agitation, capped at max)
    PgV_op = min(PgV_req, PgV_max)
    q_bio = our_peak * HEAT_PER_O2 / 3600 * 1000      # W/m³  (mmol/L/h → W/m³)
    q_total = q_bio + PgV_op
    A = np.pi * v.T * v.H + np.pi / 4 * v.T ** 2        # wetted wall + bottom, m²
    q_cool = v.U_W_m2K * A * (p.temp_C - v.coolant_C) / v.V   # W/m³
    heat_ok = q_total <= q_cool

    # Mixing vs O₂ depletion time
    tm = mixing_time(v, PgV_op)
    t_o2 = drive / max(our_peak, 1e-9) * 3600         # s for culture to consume dissolved O₂
    mix_ok = tm < t_o2

    tip = np.pi * v.Di * min(N_req, N_max)

    r = {
        "Volume (L)": v.volume_L, "Tank diameter (m)": v.T, "Liquid height (m)": v.H,
        "Impeller diameter (m)": v.Di,
        "c* at mean depth (mmol/L)": cs, "O₂ driving force (mmol/L)": drive,
        "Superficial gas velocity (cm/s)": vs * 100,
        "kLa required (h⁻¹)": kla_req, "kLa max achievable (h⁻¹)": kla_max,
        "kLa max, other broth type (h⁻¹)": kla_max_alt,
        "Agitation limited by": limit_by,
        "OTR max (mmol/L/h)": otr_max, "Peak OUR (mmol/L/h)": our_peak,
        "Target biomass (g/L)": x_t,
        "Agitation required (rpm)": N_req * 60, "Agitation max (rpm)": N_max * 60,
        "Gassed P/V required (W/m³)": PgV_req, "Tip speed at operating point (m/s)": tip,
        "Max biomass before O₂ limitation (g/L)": x_o2_lim,
        "Fed-batch μ max at target X (h⁻¹)": mu_fb_max,
        "Metabolic heat (W/m³)": q_bio, "Agitation heat (W/m³)": PgV_op,
        "Jacket cooling capacity (W/m³)": q_cool,
        "Mixing time (s)": tm, "O₂ depletion time (s)": t_o2,
        "o2_ok": o2_ok, "heat_ok": heat_ok, "mix_ok": mix_ok,
    }
    r["verdict"] = _verdict(p, v, r)
    return r


def _verdict(p, v, r) -> list[tuple[str, str]]:
    """(severity, message) — severity in {ok, warn, fail}."""
    out = []
    if r["o2_ok"]:
        out.append(("ok", f"Oxygen: peak OUR ({r['Peak OUR (mmol/L/h)']:.0f} mmol/L/h) needs kLa "
                          f"{r['kLa required (h⁻¹)']:.0f} h⁻¹; this vessel reaches "
                          f"{r['kLa max achievable (h⁻¹)']:.0f} h⁻¹ at "
                          f"{r['Agitation required (rpm)']:.0f} of {r['Agitation max (rpm)']:.0f} rpm."))
    else:
        fixes = []
        if v.o2_fraction < 0.3:
            fixes.append("O₂-enriched air")
        if v.head_pressure_bar_g < 0.5:
            fixes.append("0.5–1 bar back-pressure")
        fixes.append(f"cap biomass near {r['Max biomass before O₂ limitation (g/L)']:.0f} g/L")
        mu_fb = r["Fed-batch μ max at target X (h⁻¹)"]
        if mu_fb and mu_fb < p.mu_h * 0.99:
            fixes.append(f"fed-batch at μ ≤ {mu_fb:.2f} h⁻¹")
        out.append(("fail", f"Oxygen limited: needs kLa {r['kLa required (h⁻¹)']:.0f} h⁻¹ but the "
                            f"vessel maxes out at {r['kLa max achievable (h⁻¹)']:.0f} h⁻¹ "
                            f"(limited by {r['Agitation limited by']}). Options: " + ", ".join(fixes) + "."))
    if r["heat_ok"]:
        out.append(("ok", f"Heat: {r['Metabolic heat (W/m³)'] + r['Agitation heat (W/m³)']:.0f} W/m³ "
                          f"generated vs {r['Jacket cooling capacity (W/m³)']:.0f} W/m³ jacket capacity."))
    else:
        out.append(("fail", f"Heat removal limited: {r['Metabolic heat (W/m³)'] + r['Agitation heat (W/m³)']:.0f} W/m³ "
                            f"generated vs {r['Jacket cooling capacity (W/m³)']:.0f} W/m³ jacket capacity. "
                            "Add internal coils, colder coolant, or lower the peak OUR (fed-batch)."))
    sev = "ok" if r["mix_ok"] else "warn"
    out.append((sev, f"Mixing: {r['Mixing time (s)']:.0f} s vs {r['O₂ depletion time (s)']:.0f} s for the "
                     "culture to consume the dissolved O₂" +
                ("" if r["mix_ok"] else " — expect DO gradients away from the sparger; "
                                        "consider more impellers or feeding near the impeller.")))
    if v.volume_L < 20:
        out.append(("warn", "The kLa and mixing correlations are fitted on vessels from roughly "
                            "20 L up; at bench scale they usually under-predict kLa, so treat "
                            "this row as indicative only."))
    if r["Tip speed at operating point (m/s)"] > 5:
        out.append(("warn", f"Tip speed {r['Tip speed at operating point (m/s)']:.1f} m/s — fine for "
                            "bacteria and yeast, too high for mammalian or filamentous cultures."))
    return out


def scan_volumes(p: ProcessData, v: Vessel, volumes, x_target_gL=None) -> list[dict]:
    rows = []
    for V in volumes:
        vv = Vessel(**{**asdict(v), "volume_L": float(V)})
        r = evaluate(p, vv, x_target_gL)
        rows.append({k: r[k] for k in (
            "Volume (L)", "kLa required (h⁻¹)", "kLa max achievable (h⁻¹)",
            "OTR max (mmol/L/h)", "Max biomass before O₂ limitation (g/L)",
            "Agitation required (rpm)", "Agitation max (rpm)", "Mixing time (s)",
            "Metabolic heat (W/m³)", "Jacket cooling capacity (W/m³)")})
        rows[-1].update(o2_ok=r["o2_ok"], heat_ok=r["heat_ok"], mix_ok=r["mix_ok"])
    return rows


def process_from_run(time_h, od, mu, dcw_factor, our=None, q_o2=None,
                     y_xo_default=0.033, window=None):
    """Build ProcessData from a run.

    q_O2 priority: explicit value (e.g. from Flux Analysis) → OUR/X over the
    exponential window → μ / Y_X/O with a default yield
    (0.033 g DCW per mmol O₂ ≈ 1.05 g/g, typical aerobic growth on glucose).
    """
    t = np.asarray(time_h, float)
    X = np.asarray(od, float) * dcw_factor
    ok = np.isfinite(t) & np.isfinite(X)
    x_max = float(np.nanmax(X[ok]))
    source = "flux analysis" if q_o2 else None
    our_peak = None
    if our is not None:
        o = np.asarray(our, float)
        if np.isfinite(o).any():
            our_peak = float(np.nanmax(o))
            if not q_o2:
                m = ok & np.isfinite(o) & (X > 0)
                if window is not None:
                    m &= (t >= window[0]) & (t <= window[1])
                if m.sum() >= 3:
                    q_o2 = float(np.median(o[m] / X[m]))
                    source = "measured OUR ÷ biomass"
    if not q_o2:
        q_o2 = mu / y_xo_default
        source = f"μ ÷ default Y_X/O ({y_xo_default} g/mmol)"
    # OD and off-gas may stop at different times: take the larger demand estimate
    our_peak = max(our_peak or 0.0, q_o2 * x_max)
    return ProcessData(mu_h=float(mu), x_max_gL=x_max, our_peak=our_peak, q_o2=float(q_o2),
                       source=source)
