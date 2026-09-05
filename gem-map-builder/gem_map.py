"""
gem_map.py -- Organism-Aware Parameter to Metabolic Pathway Mapping
Written by: Anu Kozhiyalam
Purpose: Maps bioprocess analyzer readings to genome-scale metabolic model
         pathways for ATLAS overlay -- supports 10 production organisms
         across mammalian, yeast, and bacterial platforms

Organisms:
  CHO        (iCHO2291)   -- fed-batch mAb production
  CHO-S      (iCHO2291)   -- suspension perfusion high-density mAb
  HEK293     (Recon3D)    -- viral vector / gene therapy (AAV, lentivirus)
  NS0        (iNS0_1091)  -- murine myeloma, glutamine-dependent mAb
  Sp2/0      (iSp2_0)     -- murine hybridoma mAb
  BHK-21     (iBHK)       -- baby hamster kidney, vaccine / coag factors
  E. coli    (iML1515)    -- recombinant protein, batch/fed-batch
  B. subtilis(iYO844)     -- gram-positive, secreted enzyme
  P. pastoris(iMT1026v3)  -- yeast, methanol-induced secreted protein
  S. cerevisiae(iMM904)   -- yeast, VLP / vaccine antigen
"""

# ═══════════════════════════════════════════════════════════════════════════
#  MAMMALIAN HOSTS
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
#  CHO  --  Chinese Hamster Ovary  (fed-batch, mAb production)
# ---------------------------------------------------------------------------
CHO_MAP = {

    "glucose": {
        "pathway": "Glycolysis",
        "gem_reaction": "HEX1",
        "gem_model": "iCHO2291",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "g/L",   "state": "flux_limited",
                       "meaning": "Glycolytic flux restricted -- ATP generation declining -- growth rate will drop within 24h"},
            "normal": {"threshold": 4.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glycolysis running at design rate"},
            "high":   {"threshold": 6.0,  "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Excess glucose -- risk of lactate overflow metabolism via Warburg effect"}
        },
        "downstream_effects": ["lactate", "ammonia", "VCD"],
        "atlas_color": "amber"
    },

    "lactate": {
        "pathway": "Overflow metabolism / Warburg effect",
        "gem_reaction": "LDH_L",
        "gem_model": "iCHO2291",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Minimal overflow -- cells running oxidative metabolism cleanly"},
            "normal": {"threshold": 2.0,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Some glycolytic overflow -- monitor glucose feed rate"},
            "high":   {"threshold": 4.0,  "unit": "g/L",   "state": "critical",
                       "meaning": "High lactate -- pH will drop -- osmolality rising -- productivity risk"}
        },
        "downstream_effects": ["pH", "VCD", "viability"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Metabolic acid-base balance",
        "gem_reaction": "ATPM",
        "gem_model": "iCHO2291",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.9,  "unit": "",       "state": "acidosis",
                       "meaning": "Metabolic acidosis -- lactate or CO2 accumulation -- cells stressed"},
            "normal": {"threshold": 7.2,  "unit": "",       "state": "optimal",
                       "meaning": "pH in target range -- metabolic balance maintained"},
            "high":   {"threshold": 7.4,  "unit": "",       "state": "alkalosis",
                       "meaning": "Possible CO2 stripping or base overcorrection"}
        },
        "downstream_effects": ["lactate", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "iCHO2291",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 20.0, "unit": "%",      "state": "hypoxic",
                       "meaning": "Oxygen limiting -- OXPHOS flux dropping -- cells shifting to anaerobic glycolysis"},
            "normal": {"threshold": 40.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen -- oxidative phosphorylation running efficiently"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "High DO -- check agitation and sparging -- possible shear stress risk"}
        },
        "downstream_effects": ["lactate", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Amino acid metabolism / Glutamine pathway",
        "gem_reaction": "GLNS",
        "gem_model": "iCHO2291",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "mM",    "state": "optimal",
                       "meaning": "Normal glutamine catabolism -- ammonia clearance adequate"},
            "normal": {"threshold": 5.0,  "unit": "mM",    "state": "moderate",
                       "meaning": "Ammonia accumulating -- monitor glutamine feed and cell health"},
            "high":   {"threshold": 8.0,  "unit": "mM",    "state": "toxic",
                       "meaning": "Ammonia toxicity -- glycosylation quality at risk -- productivity declining"}
        },
        "downstream_effects": ["VCD", "viability", "titer"],
        "atlas_color": "red"
    },

    "VCD": {
        "pathway": "Cell growth / Biomass accumulation",
        "gem_reaction": "BIOMASS_cho",
        "gem_model": "iCHO2291",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 5.0,  "unit": "e6/mL", "state": "slow_growth",
                       "meaning": "Growth below target -- check nutrient levels and metabolic state"},
            "normal": {"threshold": 15.0, "unit": "e6/mL", "state": "exponential",
                       "meaning": "Healthy exponential growth -- productivity window approaching"},
            "high":   {"threshold": 30.0, "unit": "e6/mL", "state": "peak_density",
                       "meaning": "Peak density reached -- shift to production phase -- monitor nutrients carefully"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell health / Apoptosis",
        "gem_reaction": "APOPTOSIS",
        "gem_model": "iCHO2291",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 75.0, "unit": "%",      "state": "critical",
                       "meaning": "High cell death -- culture failing -- consider harvest or investigate root cause"},
            "normal": {"threshold": 90.0, "unit": "%",      "state": "healthy",
                       "meaning": "Good culture viability -- maintain current conditions"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability -- culture in optimal state"}
        },
        "downstream_effects": ["titer", "VCD"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Secretory pathway / Product synthesis",
        "gem_reaction": "IgG_production",
        "gem_model": "iCHO2291",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "low_production",
                       "meaning": "Product titre below target -- check VCD, viability, and metabolic state"},
            "normal": {"threshold": 2.0,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Titre accumulating on target trajectory"},
            "high":   {"threshold": 4.0,  "unit": "g/L",   "state": "high_producing",
                       "meaning": "High titre -- excellent productivity -- maintain conditions"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Cellular respiration",
        "gem_reaction": "CS",
        "gem_model": "iCHO2291",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 5.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low CO2 production -- TCA cycle flux reduced -- check glucose and oxygen"},
            "normal": {"threshold": 10.0, "unit": "%",      "state": "optimal",
                       "meaning": "Normal respiratory activity -- TCA cycle running efficiently"},
            "high":   {"threshold": 15.0, "unit": "%",      "state": "hypercapnia",
                       "meaning": "CO2 accumulating -- pH dropping -- increase stripping or check agitation"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Oxidative phosphorylation / Electron transport",
        "gem_reaction": "CYTBD",
        "gem_model": "iCHO2291",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 15.0, "unit": "%",      "state": "oxygen_depleted",
                       "meaning": "O2 in off-gas dropping -- cells consuming more than supplied -- increase sparging"},
            "normal": {"threshold": 18.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal O2 consumption -- OXPHOS flux adequate"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "O2 passing through unused -- cells in low metabolic state or density low"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate",
        "gem_reaction": "TEMP_SHIFT",
        "gem_model": "iCHO2291",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 35.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Temperature shifted down -- metabolic rate slowing -- used to boost titer in production phase"},
            "normal": {"threshold": 37.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard CHO culture temperature -- full metabolic rate"},
            "high":   {"threshold": 38.0, "unit": "C",      "state": "heat_stress",
                       "meaning": "Above target -- heat stress -- viability and glycosylation at risk"}
        },
        "downstream_effects": ["VCD", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / Oxygen delivery",
        "gem_reaction": "kLa",
        "gem_model": "iCHO2291",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 100.0,"unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Insufficient mixing -- oxygen gradients forming -- DO will drop in dense cultures"},
            "normal": {"threshold": 200.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Good bulk mixing -- adequate oxygen and nutrient distribution"},
            "high":   {"threshold": 350.0,"unit": "rpm",    "state": "shear_risk",
                       "meaning": "High agitation -- shear stress risk -- monitor viability closely"}
        },
        "downstream_effects": ["DO", "VCD", "viability"],
        "atlas_color": "gray"
    }
}

# ---------------------------------------------------------------------------
#  CHO-S  --  Suspension-adapted CHO  (high-density perfusion, mAb)
# ---------------------------------------------------------------------------
CHOS_MAP = {

    "glucose": {
        "pathway": "Glycolysis / Continuous nutrient supply",
        "gem_reaction": "HEX1",
        "gem_model": "iCHO2291",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.5,  "unit": "g/L",   "state": "flux_limited",
                       "meaning": "Glucose low in perfusion -- increase perfusion rate or bolus -- cell-specific consumption rising at high density"},
            "normal": {"threshold": 3.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose balanced with perfusion rate -- steady-state metabolism"},
            "high":   {"threshold": 5.0,  "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Glucose accumulating -- perfusion oversupply or consumption drop -- lactate overflow likely"}
        },
        "downstream_effects": ["lactate", "ammonia", "VCD"],
        "atlas_color": "amber"
    },

    "lactate": {
        "pathway": "Overflow metabolism / Warburg effect",
        "gem_reaction": "LDH_L",
        "gem_model": "iCHO2291",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.3,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Perfusion clearing lactate efficiently -- oxidative metabolism dominant"},
            "normal": {"threshold": 1.5,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Lactate rising -- check perfusion rate and cell-specific glucose uptake"},
            "high":   {"threshold": 3.0,  "unit": "g/L",   "state": "critical",
                       "meaning": "Lactate accumulating despite perfusion -- filter fouling or pump failure suspected"}
        },
        "downstream_effects": ["pH", "VCD", "viability"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Metabolic acid-base balance / Perfusion homeostasis",
        "gem_reaction": "ATPM",
        "gem_model": "iCHO2291",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.85, "unit": "",       "state": "acidosis",
                       "meaning": "pH dropping -- lactate and CO2 accumulation in high-density perfusion -- check filter and base addition"},
            "normal": {"threshold": 7.15, "unit": "",       "state": "optimal",
                       "meaning": "pH controlled -- perfusion maintaining metabolic balance"},
            "high":   {"threshold": 7.35, "unit": "",       "state": "alkalosis",
                       "meaning": "pH elevated -- base overcorrection or CO2 stripping at high sparge rates"}
        },
        "downstream_effects": ["lactate", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "iCHO2291",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 25.0, "unit": "%",      "state": "hypoxic",
                       "meaning": "DO critically low at high density -- oxygen transfer rate insufficient -- increase sparge or reduce density"},
            "normal": {"threshold": 45.0, "unit": "%",      "state": "optimal",
                       "meaning": "DO maintained -- OTR matching OUR at current cell density"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "DO excess -- cell density may be below target or bleed rate too high"}
        },
        "downstream_effects": ["lactate", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Glutamine catabolism / Perfusion clearance",
        "gem_reaction": "GLNS",
        "gem_model": "iCHO2291",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 1.5,  "unit": "mM",    "state": "optimal",
                       "meaning": "Perfusion clearing ammonia -- glutamine metabolism balanced"},
            "normal": {"threshold": 4.0,  "unit": "mM",    "state": "moderate",
                       "meaning": "Ammonia accumulating -- perfusion not fully clearing at this density -- check filter"},
            "high":   {"threshold": 7.0,  "unit": "mM",    "state": "toxic",
                       "meaning": "Ammonia toxic -- perfusion failure or excessive glutamine feed -- glycosylation at risk"}
        },
        "downstream_effects": ["VCD", "viability", "titer"],
        "atlas_color": "red"
    },

    "VCD": {
        "pathway": "Cell growth / Steady-state density control",
        "gem_reaction": "BIOMASS_cho",
        "gem_model": "iCHO2291",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 20.0, "unit": "e6/mL", "state": "below_setpoint",
                       "meaning": "Density below perfusion setpoint -- reduce bleed rate -- allow cells to accumulate"},
            "normal": {"threshold": 60.0, "unit": "e6/mL", "state": "steady_state",
                       "meaning": "Operating at target perfusion density -- bleed rate balancing growth"},
            "high":   {"threshold": 100.0,"unit": "e6/mL", "state": "ultra_high_density",
                       "meaning": "Extremely high density -- filter capacity and O2 transfer rate-limiting -- increase bleed"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell health / Apoptosis / Perfusion stress",
        "gem_reaction": "APOPTOSIS",
        "gem_model": "iCHO2291",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 75.0, "unit": "%",      "state": "critical",
                       "meaning": "Viability crashing -- filter fouling with debris -- product quality declining -- harvest or reduce density"},
            "normal": {"threshold": 88.0, "unit": "%",      "state": "healthy",
                       "meaning": "Viable culture -- perfusion maintaining cell health"},
            "high":   {"threshold": 96.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability -- perfusion culture in prime condition"}
        },
        "downstream_effects": ["titer", "VCD"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Secretory pathway / Continuous harvest",
        "gem_reaction": "IgG_production",
        "gem_model": "iCHO2291",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.3,  "unit": "g/L",   "state": "low_production",
                       "meaning": "Permeate titre low -- cell-specific productivity (qP) below target -- check metabolic state"},
            "normal": {"threshold": 1.0,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Permeate titre on target -- continuous harvest collecting product"},
            "high":   {"threshold": 2.5,  "unit": "g/L",   "state": "high_producing",
                       "meaning": "High permeate titre -- excellent qP at this density -- maintain conditions"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Cellular respiration",
        "gem_reaction": "CS",
        "gem_model": "iCHO2291",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 4.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low CO2 -- metabolic rate declining or cell density dropped"},
            "normal": {"threshold": 12.0, "unit": "%",      "state": "optimal",
                       "meaning": "CO2 evolution matches high-density respiration rate"},
            "high":   {"threshold": 18.0, "unit": "%",      "state": "hypercapnia",
                       "meaning": "CO2 very high -- stripping inadequate at this density -- pH and viability at risk"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Oxidative phosphorylation / Electron transport",
        "gem_reaction": "CYTBD",
        "gem_model": "iCHO2291",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 13.0, "unit": "%",      "state": "oxygen_depleted",
                       "meaning": "O2 consumed heavily at high density -- OTR at limit -- increase sparge or reduce density"},
            "normal": {"threshold": 17.0, "unit": "%",      "state": "balanced",
                       "meaning": "O2 consumption balanced with supply at current density"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Low O2 demand -- density below target or cells metabolically quiescent"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate",
        "gem_reaction": "TEMP_SHIFT",
        "gem_model": "iCHO2291",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 34.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Temperature reduced -- common in perfusion to slow growth and boost qP -- monitor density setpoint"},
            "normal": {"threshold": 36.5, "unit": "C",      "state": "optimal",
                       "meaning": "Standard perfusion temperature -- balancing growth and productivity"},
            "high":   {"threshold": 37.5, "unit": "C",      "state": "heat_stress",
                       "meaning": "Above perfusion target -- metabolic rate too high for filter capacity -- viability risk"}
        },
        "downstream_effects": ["VCD", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / Oxygen delivery / Filter protection",
        "gem_reaction": "kLa",
        "gem_model": "iCHO2291",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 80.0, "unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Mixing inadequate -- settling and DO gradients at high density -- filter fouling risk"},
            "normal": {"threshold": 180.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Mixing balanced -- adequate for perfusion without excessive shear"},
            "high":   {"threshold": 300.0,"unit": "rpm",    "state": "shear_risk",
                       "meaning": "High shear -- cell damage increasing -- debris will foul ATF/TFF filter"}
        },
        "downstream_effects": ["DO", "VCD", "viability"],
        "atlas_color": "gray"
    }
}

# ---------------------------------------------------------------------------
#  HEK293  --  Human Embryonic Kidney  (viral vector / gene therapy)
# ---------------------------------------------------------------------------
HEK293_MAP = {

    "glucose": {
        "pathway": "Glycolysis",
        "gem_reaction": "HEX1",
        "gem_model": "Recon3D",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.5,  "unit": "g/L",   "state": "flux_limited",
                       "meaning": "Glucose depleted -- HEK293 highly glycolytic -- transfection efficiency will drop if starved"},
            "normal": {"threshold": 3.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose adequate for growth and vector production"},
            "high":   {"threshold": 6.0,  "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Glucose excess -- lactate overflow -- HEK293 very prone to Warburg overflow"}
        },
        "downstream_effects": ["lactate", "ammonia", "VCD"],
        "atlas_color": "amber"
    },

    "lactate": {
        "pathway": "Overflow metabolism / Aerobic glycolysis",
        "gem_reaction": "LDH_L",
        "gem_model": "Recon3D",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Low lactate -- oxidative metabolism -- ideal for transfection window"},
            "normal": {"threshold": 2.5,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Moderate lactate -- HEK293 tolerates this but monitor pH"},
            "high":   {"threshold": 5.0,  "unit": "g/L",   "state": "critical",
                       "meaning": "High lactate -- pH acidosis -- transfection efficiency dropping -- vector yield at risk"}
        },
        "downstream_effects": ["pH", "VCD", "viability"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Metabolic acid-base balance",
        "gem_reaction": "ATPM",
        "gem_model": "Recon3D",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.9,  "unit": "",       "state": "acidosis",
                       "meaning": "Acidosis -- lactate accumulation -- DNA-lipid complex uptake impaired -- poor transfection"},
            "normal": {"threshold": 7.2,  "unit": "",       "state": "optimal",
                       "meaning": "pH optimal for HEK293 -- transfection and viral packaging efficient"},
            "high":   {"threshold": 7.5,  "unit": "",       "state": "alkalosis",
                       "meaning": "pH too high -- calcium phosphate precipitation if using CaPO4 transfection -- adjust CO2"}
        },
        "downstream_effects": ["lactate", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "Recon3D",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 20.0, "unit": "%",      "state": "hypoxic",
                       "meaning": "Hypoxic -- HEK293 shifts to glycolysis -- viral replication may actually increase under mild hypoxia"},
            "normal": {"threshold": 40.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen -- normal respiration and vector production"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "Excess DO -- HEK293 sensitive to oxidative stress -- ROS may damage viral capsids"}
        },
        "downstream_effects": ["lactate", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Glutamine catabolism / Amino acid metabolism",
        "gem_reaction": "GLNS",
        "gem_model": "Recon3D",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonia low -- glutamine metabolism balanced"},
            "normal": {"threshold": 5.0,  "unit": "mM",    "state": "moderate",
                       "meaning": "Ammonia rising -- may interfere with viral vector assembly"},
            "high":   {"threshold": 8.0,  "unit": "mM",    "state": "toxic",
                       "meaning": "Ammonia toxic -- AAV capsid assembly impaired -- empty:full ratio worsening"}
        },
        "downstream_effects": ["VCD", "viability", "titer"],
        "atlas_color": "red"
    },

    "VCD": {
        "pathway": "Cell growth / Biomass",
        "gem_reaction": "BIOMASS_hek293",
        "gem_model": "Recon3D",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "e6/mL", "state": "slow_growth",
                       "meaning": "Low density -- not yet at transfection threshold (typically 1.5-2.5e6/mL for AAV)"},
            "normal": {"threshold": 3.0,  "unit": "e6/mL", "state": "transfection_ready",
                       "meaning": "Density in optimal transfection window -- proceed with plasmid addition"},
            "high":   {"threshold": 6.0,  "unit": "e6/mL", "state": "overgrown",
                       "meaning": "Overgrown -- contact inhibition effects -- transfection efficiency dropping -- dilute or passage"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell health / Apoptosis",
        "gem_reaction": "APOPTOSIS",
        "gem_model": "Recon3D",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 65.0, "unit": "%",      "state": "critical",
                       "meaning": "High death -- viral burst releasing product but also HCP and DNA impurities -- harvest now"},
            "normal": {"threshold": 80.0, "unit": "%",      "state": "healthy",
                       "meaning": "Acceptable viability -- post-transfection drop is normal for HEK293 vector production"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability -- ideal pre-transfection state"}
        },
        "downstream_effects": ["titer", "VCD"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Viral vector production / Capsid assembly",
        "gem_reaction": "AAV_assembly",
        "gem_model": "Recon3D",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 1e10, "unit": "vg/mL",  "state": "low_production",
                       "meaning": "Vector yield low -- check transfection efficiency, plasmid ratio, and harvest timing"},
            "normal": {"threshold": 1e11, "unit": "vg/mL",  "state": "on_track",
                       "meaning": "Vector production on target -- monitor full:empty capsid ratio"},
            "high":   {"threshold": 1e12, "unit": "vg/mL",  "state": "high_producing",
                       "meaning": "Excellent vector yield -- verify potency and capsid integrity"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Cellular respiration",
        "gem_reaction": "CS",
        "gem_model": "Recon3D",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 4.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low respiration -- cells quiescent or density low"},
            "normal": {"threshold": 10.0, "unit": "%",      "state": "optimal",
                       "meaning": "Normal respiratory activity"},
            "high":   {"threshold": 15.0, "unit": "%",      "state": "hypercapnia",
                       "meaning": "CO2 high -- pH dropping -- transfection efficiency at risk"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Oxidative phosphorylation / Electron transport",
        "gem_reaction": "CYTBD",
        "gem_model": "Recon3D",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 15.0, "unit": "%",      "state": "oxygen_depleted",
                       "meaning": "O2 depleted -- high cell-specific consumption post-transfection"},
            "normal": {"threshold": 18.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal O2 consumption"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Low consumption -- density low or cells metabolically inactive"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate / Vector production",
        "gem_reaction": "TEMP_SHIFT",
        "gem_model": "Recon3D",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 35.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Temperature reduced -- may slow vector production but improve capsid quality"},
            "normal": {"threshold": 37.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard HEK293 temperature -- optimal for transfection and vector production"},
            "high":   {"threshold": 38.5, "unit": "C",      "state": "heat_stress",
                       "meaning": "Heat stress -- HEK293 very sensitive -- viability and vector quality declining"}
        },
        "downstream_effects": ["VCD", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / Gentle mixing",
        "gem_reaction": "kLa",
        "gem_model": "Recon3D",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 60.0, "unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Mixing too gentle -- settling and DO gradients -- HEK293 aggregation risk"},
            "normal": {"threshold": 130.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Gentle mixing appropriate for HEK293 -- shear-sensitive cells well-mixed"},
            "high":   {"threshold": 200.0,"unit": "rpm",    "state": "shear_risk",
                       "meaning": "HEK293 very shear-sensitive -- viability dropping -- reduce agitation immediately"}
        },
        "downstream_effects": ["DO", "VCD", "viability"],
        "atlas_color": "gray"
    }
}

# ---------------------------------------------------------------------------
#  NS0  --  Murine Myeloma  (mAb, glutamine-dependent, cholesterol-req)
# ---------------------------------------------------------------------------
NS0_MAP = {

    "glucose": {
        "pathway": "Glycolysis",
        "gem_reaction": "HEX1",
        "gem_model": "iNS0_1091",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.5,  "unit": "g/L",   "state": "flux_limited",
                       "meaning": "Glucose depleted -- NS0 highly glycolytic and glutamine-dependent -- rapid decline imminent"},
            "normal": {"threshold": 4.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose adequate -- glycolysis fuelling NS0 growth"},
            "high":   {"threshold": 7.0,  "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Glucose excess -- NS0 prone to heavy lactate overflow -- reduce feed rate"}
        },
        "downstream_effects": ["lactate", "ammonia", "VCD"],
        "atlas_color": "amber"
    },

    "lactate": {
        "pathway": "Overflow metabolism / Heavy glycolytic phenotype",
        "gem_reaction": "LDH_L",
        "gem_model": "iNS0_1091",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.8,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Low lactate -- unusual for NS0 -- cells likely in stationary or production phase"},
            "normal": {"threshold": 3.0,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Typical NS0 lactate -- these cells produce more lactate than CHO at same glucose"},
            "high":   {"threshold": 5.0,  "unit": "g/L",   "state": "critical",
                       "meaning": "Very high lactate -- NS0 osmolality tolerance lower than CHO -- viability dropping"}
        },
        "downstream_effects": ["pH", "VCD", "viability"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Metabolic acid-base balance",
        "gem_reaction": "ATPM",
        "gem_model": "iNS0_1091",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.8,  "unit": "",       "state": "acidosis",
                       "meaning": "Acidosis -- NS0 lactate production driving pH down -- base addition may spike osmolality"},
            "normal": {"threshold": 7.1,  "unit": "",       "state": "optimal",
                       "meaning": "pH in NS0 optimal range"},
            "high":   {"threshold": 7.4,  "unit": "",       "state": "alkalosis",
                       "meaning": "pH high -- base overcorrection -- NS0 sensitive to osmolality from NaOH/NaHCO3"}
        },
        "downstream_effects": ["lactate", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "iNS0_1091",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 20.0, "unit": "%",      "state": "hypoxic",
                       "meaning": "Oxygen limiting -- NS0 shifts to lactate production even faster under hypoxia"},
            "normal": {"threshold": 40.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen for NS0 oxidative metabolism"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "DO excess -- low density or slow metabolism"}
        },
        "downstream_effects": ["lactate", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Glutamine dependency / GS pathway absent",
        "gem_reaction": "GLNS_absent",
        "gem_model": "iNS0_1091",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonia low -- glutamine catabolism controlled"},
            "normal": {"threshold": 5.0,  "unit": "mM",    "state": "moderate",
                       "meaning": "Ammonia rising -- NS0 lacks endogenous GS -- cannot recycle ammonia -- exogenous glutamine critical"},
            "high":   {"threshold": 7.0,  "unit": "mM",    "state": "toxic",
                       "meaning": "Ammonia toxic -- NS0 especially sensitive due to GS deficiency -- mAb quality degrading"}
        },
        "downstream_effects": ["VCD", "viability", "titer"],
        "atlas_color": "red"
    },

    "VCD": {
        "pathway": "Cell growth / Biomass",
        "gem_reaction": "BIOMASS_ns0",
        "gem_model": "iNS0_1091",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 3.0,  "unit": "e6/mL", "state": "slow_growth",
                       "meaning": "Low density -- NS0 grows slower than CHO -- check cholesterol and lipid supplements"},
            "normal": {"threshold": 8.0,  "unit": "e6/mL", "state": "exponential",
                       "meaning": "Good NS0 growth -- approaching production phase"},
            "high":   {"threshold": 15.0, "unit": "e6/mL", "state": "peak_density",
                       "meaning": "Peak density for NS0 -- lower than CHO -- shift to production phase"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell health / Apoptosis",
        "gem_reaction": "APOPTOSIS",
        "gem_model": "iNS0_1091",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 75.0, "unit": "%",      "state": "critical",
                       "meaning": "NS0 culture failing -- cholesterol auxotrophy makes recovery difficult -- harvest immediately"},
            "normal": {"threshold": 88.0, "unit": "%",      "state": "healthy",
                       "meaning": "Viable NS0 culture -- maintain cholesterol and lipid supplements"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability -- all supplements adequate"}
        },
        "downstream_effects": ["titer", "VCD"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Secretory pathway / mAb production",
        "gem_reaction": "IgG_production",
        "gem_model": "iNS0_1091",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.3,  "unit": "g/L",   "state": "low_production",
                       "meaning": "mAb titre low -- NS0 typically lower yielding than CHO -- check specific productivity"},
            "normal": {"threshold": 1.5,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Titre accumulating on NS0 target trajectory"},
            "high":   {"threshold": 3.0,  "unit": "g/L",   "state": "high_producing",
                       "meaning": "Good NS0 titre -- note: glycosylation profile differs from CHO (alpha-gal, NGNA)"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Cellular respiration",
        "gem_reaction": "CS",
        "gem_model": "iNS0_1091",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 4.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low respiration -- NS0 metabolic rate declining"},
            "normal": {"threshold": 10.0, "unit": "%",      "state": "optimal",
                       "meaning": "Normal NS0 respiratory activity"},
            "high":   {"threshold": 15.0, "unit": "%",      "state": "hypercapnia",
                       "meaning": "CO2 accumulating -- pH dropping -- NS0 sensitive to acid stress"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Oxidative phosphorylation / Electron transport",
        "gem_reaction": "CYTBD",
        "gem_model": "iNS0_1091",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 15.0, "unit": "%",      "state": "oxygen_depleted",
                       "meaning": "O2 depleted in off-gas -- increase sparging"},
            "normal": {"threshold": 18.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal O2 consumption for NS0"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Low O2 demand -- density low or cells in decline"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate",
        "gem_reaction": "TEMP_SHIFT",
        "gem_model": "iNS0_1091",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 35.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Temperature reduced -- NS0 cold shift less effective than CHO for productivity boost"},
            "normal": {"threshold": 37.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard mammalian culture temperature"},
            "high":   {"threshold": 38.0, "unit": "C",      "state": "heat_stress",
                       "meaning": "Heat stress -- NS0 temperature sensitive -- viability declining"}
        },
        "downstream_effects": ["VCD", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / Oxygen delivery",
        "gem_reaction": "kLa",
        "gem_model": "iNS0_1091",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 80.0, "unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Mixing insufficient -- NS0 are suspension cells but settle at low agitation"},
            "normal": {"threshold": 180.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Adequate mixing for NS0 culture"},
            "high":   {"threshold": 300.0,"unit": "rpm",    "state": "shear_risk",
                       "meaning": "Shear stress -- NS0 moderately shear sensitive -- reduce agitation"}
        },
        "downstream_effects": ["DO", "VCD", "viability"],
        "atlas_color": "gray"
    }
}

# ---------------------------------------------------------------------------
#  Sp2/0  --  Murine Hybridoma  (mAb production)
# ---------------------------------------------------------------------------
SP20_MAP = {

    "glucose": {
        "pathway": "Glycolysis",
        "gem_reaction": "HEX1",
        "gem_model": "iSp2_0",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.5,  "unit": "g/L",   "state": "flux_limited",
                       "meaning": "Glucose depleted -- Sp2/0 dies rapidly without carbon source -- very poor starvation tolerance"},
            "normal": {"threshold": 4.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose adequate for Sp2/0 growth and mAb production"},
            "high":   {"threshold": 7.0,  "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Glucose excess -- lactate overflow -- Sp2/0 even more glycolytic than CHO"}
        },
        "downstream_effects": ["lactate", "ammonia", "VCD"],
        "atlas_color": "amber"
    },

    "lactate": {
        "pathway": "Overflow metabolism / Glycolytic phenotype",
        "gem_reaction": "LDH_L",
        "gem_model": "iSp2_0",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Low lactate -- good metabolic state for hybridoma"},
            "normal": {"threshold": 2.5,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Typical Sp2/0 lactate production -- monitor but expected"},
            "high":   {"threshold": 4.5,  "unit": "g/L",   "state": "critical",
                       "meaning": "Lactate high -- Sp2/0 low osmolality tolerance -- culture decline imminent"}
        },
        "downstream_effects": ["pH", "VCD", "viability"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Metabolic acid-base balance",
        "gem_reaction": "ATPM",
        "gem_model": "iSp2_0",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.8,  "unit": "",       "state": "acidosis",
                       "meaning": "Acidosis -- Sp2/0 less acid-tolerant than CHO -- apoptosis accelerating"},
            "normal": {"threshold": 7.2,  "unit": "",       "state": "optimal",
                       "meaning": "pH in target range for Sp2/0"},
            "high":   {"threshold": 7.4,  "unit": "",       "state": "alkalosis",
                       "meaning": "pH elevated -- check base addition system"}
        },
        "downstream_effects": ["lactate", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "iSp2_0",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 20.0, "unit": "%",      "state": "hypoxic",
                       "meaning": "Oxygen limiting -- Sp2/0 shifts to glycolysis rapidly under hypoxia"},
            "normal": {"threshold": 40.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen for Sp2/0"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "DO excess -- low density or declining culture"}
        },
        "downstream_effects": ["lactate", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Glutamine catabolism / Amino acid metabolism",
        "gem_reaction": "GLNS",
        "gem_model": "iSp2_0",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonia low -- glutamine metabolism balanced"},
            "normal": {"threshold": 4.5,  "unit": "mM",    "state": "moderate",
                       "meaning": "Ammonia rising -- Sp2/0 more sensitive than CHO to ammonia"},
            "high":   {"threshold": 6.0,  "unit": "mM",    "state": "toxic",
                       "meaning": "Ammonia toxic -- Sp2/0 hybridoma highly sensitive -- growth arrest and mAb quality loss"}
        },
        "downstream_effects": ["VCD", "viability", "titer"],
        "atlas_color": "red"
    },

    "VCD": {
        "pathway": "Cell growth / Biomass",
        "gem_reaction": "BIOMASS_sp20",
        "gem_model": "iSp2_0",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "e6/mL", "state": "slow_growth",
                       "meaning": "Low density -- Sp2/0 grows slower than CHO -- check serum or supplement levels"},
            "normal": {"threshold": 6.0,  "unit": "e6/mL", "state": "exponential",
                       "meaning": "Good Sp2/0 growth -- approaching peak density"},
            "high":   {"threshold": 12.0, "unit": "e6/mL", "state": "peak_density",
                       "meaning": "Peak Sp2/0 density -- lower ceiling than CHO -- nutrients depleting fast"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell health / Apoptosis",
        "gem_reaction": "APOPTOSIS",
        "gem_model": "iSp2_0",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 60.0, "unit": "%",      "state": "critical",
                       "meaning": "Sp2/0 culture failing -- hybridomas fragile -- harvest product immediately"},
            "normal": {"threshold": 80.0, "unit": "%",      "state": "healthy",
                       "meaning": "Viable Sp2/0 culture -- maintain nutrient supply"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability for hybridoma"}
        },
        "downstream_effects": ["titer", "VCD"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Secretory pathway / mAb production",
        "gem_reaction": "IgG_production",
        "gem_model": "iSp2_0",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.2,  "unit": "g/L",   "state": "low_production",
                       "meaning": "mAb titre low -- Sp2/0 typically lower yielding -- check specific productivity"},
            "normal": {"threshold": 0.8,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Titre accumulating -- typical Sp2/0 range"},
            "high":   {"threshold": 2.0,  "unit": "g/L",   "state": "high_producing",
                       "meaning": "Good Sp2/0 titre -- note: murine glycosylation patterns (alpha-gal, NGNA)"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Cellular respiration",
        "gem_reaction": "CS",
        "gem_model": "iSp2_0",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 4.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low CO2 -- metabolic rate declining"},
            "normal": {"threshold": 10.0, "unit": "%",      "state": "optimal",
                       "meaning": "Normal respiratory activity for Sp2/0"},
            "high":   {"threshold": 14.0, "unit": "%",      "state": "hypercapnia",
                       "meaning": "CO2 accumulating -- pH stress -- Sp2/0 acid-sensitive"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "iSp2_0",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 15.0, "unit": "%",      "state": "oxygen_depleted",
                       "meaning": "O2 consumption high relative to Sp2/0 density"},
            "normal": {"threshold": 18.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal O2 consumption"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Low demand -- culture in decline or very low density"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate",
        "gem_reaction": "TEMP_SHIFT",
        "gem_model": "iSp2_0",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 35.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Temperature reduced -- Sp2/0 growth very sensitive to cold shift"},
            "normal": {"threshold": 37.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard mammalian temperature"},
            "high":   {"threshold": 38.0, "unit": "C",      "state": "heat_stress",
                       "meaning": "Heat stress -- hybridomas very temperature sensitive -- rapid viability loss"}
        },
        "downstream_effects": ["VCD", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / Gentle mixing",
        "gem_reaction": "kLa",
        "gem_model": "iSp2_0",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 60.0, "unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Mixing too low -- Sp2/0 settling"},
            "normal": {"threshold": 150.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Gentle mixing -- adequate for hybridoma culture"},
            "high":   {"threshold": 250.0,"unit": "rpm",    "state": "shear_risk",
                       "meaning": "Sp2/0 highly shear-sensitive -- viability dropping -- reduce immediately"}
        },
        "downstream_effects": ["DO", "VCD", "viability"],
        "atlas_color": "gray"
    }
}

# ---------------------------------------------------------------------------
#  BHK-21  --  Baby Hamster Kidney  (vaccine / coagulation factors)
# ---------------------------------------------------------------------------
BHK21_MAP = {

    "glucose": {
        "pathway": "Glycolysis",
        "gem_reaction": "HEX1",
        "gem_model": "iBHK",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.5,  "unit": "g/L",   "state": "flux_limited",
                       "meaning": "Glucose low -- BHK-21 growth slowing -- viral amplification will be impaired"},
            "normal": {"threshold": 4.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose adequate for BHK-21 growth and product expression"},
            "high":   {"threshold": 7.0,  "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Glucose excess -- BHK-21 lactate overflow -- similar overflow profile to CHO"}
        },
        "downstream_effects": ["lactate", "ammonia", "VCD"],
        "atlas_color": "amber"
    },

    "lactate": {
        "pathway": "Overflow metabolism",
        "gem_reaction": "LDH_L",
        "gem_model": "iBHK",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Minimal lactate -- oxidative metabolism"},
            "normal": {"threshold": 2.5,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Moderate lactate -- typical for BHK-21 cultures"},
            "high":   {"threshold": 5.0,  "unit": "g/L",   "state": "critical",
                       "meaning": "Lactate high -- pH dropping -- vaccine antigen quality at risk"}
        },
        "downstream_effects": ["pH", "VCD", "viability"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Metabolic acid-base balance",
        "gem_reaction": "ATPM",
        "gem_model": "iBHK",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.8,  "unit": "",       "state": "acidosis",
                       "meaning": "Acidosis -- viral replication may be pH-sensitive -- check product quality"},
            "normal": {"threshold": 7.2,  "unit": "",       "state": "optimal",
                       "meaning": "pH in BHK-21 target range"},
            "high":   {"threshold": 7.5,  "unit": "",       "state": "alkalosis",
                       "meaning": "pH elevated -- base overcorrection"}
        },
        "downstream_effects": ["lactate", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "iBHK",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 20.0, "unit": "%",      "state": "hypoxic",
                       "meaning": "Hypoxic -- BHK-21 shifts to glycolysis -- viral replication may be impacted"},
            "normal": {"threshold": 40.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen for BHK-21"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "DO excess -- low density or metabolic decline"}
        },
        "downstream_effects": ["lactate", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Glutamine catabolism",
        "gem_reaction": "GLNS",
        "gem_model": "iBHK",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonia low -- glutamine metabolism balanced"},
            "normal": {"threshold": 5.0,  "unit": "mM",    "state": "moderate",
                       "meaning": "Ammonia accumulating -- BHK-21 moderately sensitive"},
            "high":   {"threshold": 8.0,  "unit": "mM",    "state": "toxic",
                       "meaning": "Ammonia toxic -- coagulation factor post-translational modifications at risk"}
        },
        "downstream_effects": ["VCD", "viability", "titer"],
        "atlas_color": "red"
    },

    "VCD": {
        "pathway": "Cell growth / Biomass",
        "gem_reaction": "BIOMASS_bhk",
        "gem_model": "iBHK",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 3.0,  "unit": "e6/mL", "state": "slow_growth",
                       "meaning": "Low density -- BHK-21 adherent-adapted lines may need microcarriers"},
            "normal": {"threshold": 10.0, "unit": "e6/mL", "state": "exponential",
                       "meaning": "Good BHK-21 growth -- approaching infection or induction window"},
            "high":   {"threshold": 20.0, "unit": "e6/mL", "state": "peak_density",
                       "meaning": "Peak BHK-21 density -- proceed with viral infection for vaccine production"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell health / Apoptosis / Viral cytopathic effect",
        "gem_reaction": "APOPTOSIS",
        "gem_model": "iBHK",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 60.0, "unit": "%",      "state": "critical",
                       "meaning": "Viability low -- if viral production, CPE expected -- if not, investigate toxicity -- harvest timing critical"},
            "normal": {"threshold": 80.0, "unit": "%",      "state": "healthy",
                       "meaning": "Viable culture -- post-infection viability drop is normal for vaccine production"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability -- pre-infection state ideal"}
        },
        "downstream_effects": ["titer", "VCD"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Product synthesis / Viral antigen or coagulation factor",
        "gem_reaction": "PRODUCT_expression",
        "gem_model": "iBHK",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.3,  "unit": "g/L",   "state": "low_production",
                       "meaning": "Product low -- check MOI for viral, or expression construct for rFVIII"},
            "normal": {"threshold": 1.5,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Product accumulating on BHK-21 target trajectory"},
            "high":   {"threshold": 3.5,  "unit": "g/L",   "state": "high_producing",
                       "meaning": "Good BHK-21 productivity -- verify post-translational modifications"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Cellular respiration",
        "gem_reaction": "CS",
        "gem_model": "iBHK",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 4.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low CO2 -- metabolic rate declining"},
            "normal": {"threshold": 10.0, "unit": "%",      "state": "optimal",
                       "meaning": "Normal respiratory activity"},
            "high":   {"threshold": 15.0, "unit": "%",      "state": "hypercapnia",
                       "meaning": "CO2 accumulating -- pH dropping"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Oxidative phosphorylation",
        "gem_reaction": "CYTBD",
        "gem_model": "iBHK",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 15.0, "unit": "%",      "state": "oxygen_depleted",
                       "meaning": "O2 depleted -- increase sparging"},
            "normal": {"threshold": 18.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal O2 consumption"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Low O2 demand -- low density or declining culture"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate / Viral replication",
        "gem_reaction": "TEMP_SHIFT",
        "gem_model": "iBHK",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 33.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Temperature reduced -- slows BHK-21 growth -- some viruses replicate better at lower temp"},
            "normal": {"threshold": 37.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard BHK-21 culture temperature"},
            "high":   {"threshold": 38.5, "unit": "C",      "state": "heat_stress",
                       "meaning": "Heat stress -- BHK-21 temperature sensitive -- viability declining rapidly"}
        },
        "downstream_effects": ["VCD", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / Microcarrier culture considerations",
        "gem_reaction": "kLa",
        "gem_model": "iBHK",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 60.0, "unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Mixing too low -- microcarriers settling -- cells not uniformly suspended"},
            "normal": {"threshold": 150.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Adequate mixing -- microcarriers suspended without excessive bead-bead collisions"},
            "high":   {"threshold": 250.0,"unit": "rpm",    "state": "shear_risk",
                       "meaning": "High shear -- cells stripping from microcarriers -- viability dropping"}
        },
        "downstream_effects": ["DO", "VCD", "viability"],
        "atlas_color": "gray"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  BACTERIAL HOSTS
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
#  E. coli  --  BL21(DE3) / K-12  (batch / fed-batch, recombinant protein)
# ---------------------------------------------------------------------------
ECOLI_MAP = {

    "glucose": {
        "pathway": "PTS uptake / Glycolysis / EMP pathway",
        "gem_reaction": "GLCptspp",
        "gem_model": "iML1515",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "g/L",   "state": "carbon_starved",
                       "meaning": "Carbon source depleted -- stringent response activating -- ppGpp rising -- growth arrest imminent"},
            "normal": {"threshold": 5.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose feeding balanced -- PTS uptake at steady state"},
            "high":   {"threshold": 10.0, "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Glucose excess -- acetate overflow via Pta-AckA pathway -- growth inhibition above 5 g/L acetate"}
        },
        "downstream_effects": ["acetate", "ammonia", "OD600"],
        "atlas_color": "amber"
    },

    "acetate": {
        "pathway": "Acetate overflow / Pta-AckA pathway",
        "gem_reaction": "PTAr",
        "gem_model": "iML1515",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Minimal acetate -- carbon flux routed through TCA -- efficient metabolism"},
            "normal": {"threshold": 2.0,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Acetate accumulating -- reduce glucose feed rate or switch to glycerol co-feed"},
            "high":   {"threshold": 5.0,  "unit": "g/L",   "state": "inhibitory",
                       "meaning": "Acetate inhibition -- uncouples proton motive force -- recombinant protein yield dropping"}
        },
        "downstream_effects": ["pH", "OD600", "titer"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Organic acid excretion / Proton balance",
        "gem_reaction": "EX_h_e",
        "gem_model": "iML1515",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.5,  "unit": "",       "state": "acidosis",
                       "meaning": "Acid accumulation -- acetate and formate overflow -- porin expression altered -- nutrient uptake impaired"},
            "normal": {"threshold": 7.0,  "unit": "",       "state": "optimal",
                       "meaning": "pH in target range -- proton motive force stable -- transport systems nominal"},
            "high":   {"threshold": 7.5,  "unit": "",       "state": "alkalosis",
                       "meaning": "Base overcorrection -- lysine decarboxylase stress response may activate -- check acid feed"}
        },
        "downstream_effects": ["acetate", "CO2", "OD600"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Aerobic respiration / Electron transport chain",
        "gem_reaction": "CYTBO3_4pp",
        "gem_model": "iML1515",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 10.0, "unit": "%",      "state": "microaerobic",
                       "meaning": "O2 limiting -- shifting to mixed-acid fermentation -- formate, ethanol, succinate accumulating"},
            "normal": {"threshold": 30.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen -- cytochrome bo3 oxidase operating -- full aerobic respiration"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "DO excess -- culture density too low or demand dropping -- check OD600"}
        },
        "downstream_effects": ["acetate", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Nitrogen assimilation / GS-GOGAT pathway",
        "gem_reaction": "GLNS",
        "gem_model": "iML1515",
        "direction": "substrate_and_byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "mM",    "state": "nitrogen_limited",
                       "meaning": "Nitrogen starvation -- GlnB/GlnD signalling cascade activating -- growth will halt"},
            "normal": {"threshold": 10.0, "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonium at working concentration -- GS-GOGAT assimilation running"},
            "high":   {"threshold": 30.0, "unit": "mM",    "state": "excess",
                       "meaning": "Ammonia excess -- uncouples proton gradient at high pH -- moderate toxicity in E. coli"}
        },
        "downstream_effects": ["OD600", "pH", "titer"],
        "atlas_color": "red"
    },

    "OD600": {
        "pathway": "Cell growth / Biomass synthesis",
        "gem_reaction": "BIOMASS_Ec_iML1515_core_75p37M",
        "gem_model": "iML1515",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 5.0,  "unit": "OD",    "state": "lag_or_slow",
                       "meaning": "Low density -- still in lag or early exponential -- not yet at induction threshold"},
            "normal": {"threshold": 30.0, "unit": "OD",    "state": "exponential",
                       "meaning": "Healthy growth -- approaching induction window (typical IPTG induction at OD 20-40)"},
            "high":   {"threshold": 80.0, "unit": "OD",    "state": "high_density",
                       "meaning": "High cell density fed-batch -- oxygen and mixing limitations likely -- monitor DO closely"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Membrane integrity / Stress response",
        "gem_reaction": "STRESS_RESPONSE",
        "gem_model": "iML1515",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 60.0, "unit": "%",      "state": "lysis",
                       "meaning": "Extensive cell lysis -- proteases released -- product degradation risk -- harvest immediately"},
            "normal": {"threshold": 80.0, "unit": "%",      "state": "moderate_stress",
                       "meaning": "Some viability loss -- inclusion body burden or acetate stress -- reduce inducer if post-induction"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "healthy",
                       "meaning": "Membranes intact -- culture healthy -- proceed with induction or continue growth"}
        },
        "downstream_effects": ["titer", "OD600"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Recombinant protein expression / Inclusion body formation",
        "gem_reaction": "RECPROT_expression",
        "gem_model": "iML1515",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.2,  "unit": "g/L",   "state": "low_expression",
                       "meaning": "Low expression -- check inducer concentration, promoter leakiness, and codon usage"},
            "normal": {"threshold": 1.0,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Expression on target -- soluble vs inclusion body ratio should be checked"},
            "high":   {"threshold": 5.0,  "unit": "g/L",   "state": "high_expression",
                       "meaning": "High expression -- possible inclusion body load -- verify solubility if needed"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Pyruvate dehydrogenase",
        "gem_reaction": "PDH",
        "gem_model": "iML1515",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "%",      "state": "low_respiration",
                       "meaning": "Low CO2 evolution rate -- TCA flux reduced -- possible carbon starvation or anaerobic shift"},
            "normal": {"threshold": 8.0,  "unit": "%",      "state": "optimal",
                       "meaning": "Normal CER -- TCA cycle and PDH complex running efficiently"},
            "high":   {"threshold": 15.0, "unit": "%",      "state": "high_respiration",
                       "meaning": "Elevated CER -- high metabolic rate or overflow -- check RQ for fermentative shift"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Terminal oxidase / Electron transport",
        "gem_reaction": "CYTBO3_4pp",
        "gem_model": "iML1515",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 14.0, "unit": "%",      "state": "high_OUR",
                       "meaning": "High oxygen uptake rate -- cells consuming heavily -- sparging may be rate-limiting"},
            "normal": {"threshold": 18.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal OUR -- aerobic respiration via cytochrome oxidases balanced"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Minimal oxygen consumption -- low density or metabolically quiescent culture"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate / Heat-shock response",
        "gem_reaction": "TEMP_CONTROL",
        "gem_model": "iML1515",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 30.0, "unit": "C",      "state": "reduced_temp",
                       "meaning": "Lower temperature -- slower growth but improved soluble protein folding -- common for soluble expression"},
            "normal": {"threshold": 37.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard E. coli growth temperature -- maximum growth rate -- sigma-70 housekeeping"},
            "high":   {"threshold": 42.0, "unit": "C",      "state": "heat_shock",
                       "meaning": "Heat shock -- sigma-32 regulon activated -- DnaK/GroEL upregulated -- inclusion bodies likely increasing"}
        },
        "downstream_effects": ["OD600", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / kLa / Mixing",
        "gem_reaction": "kLa",
        "gem_model": "iML1515",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 200.0,"unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Insufficient mixing -- DO gradients in vessel -- acetate hot-spots forming near feed port"},
            "normal": {"threshold": 500.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Adequate mixing and kLa -- homogeneous environment for E. coli"},
            "high":   {"threshold": 800.0,"unit": "rpm",    "state": "high_shear",
                       "meaning": "Very high agitation -- E. coli tolerates shear well but foam and wall growth may increase"}
        },
        "downstream_effects": ["DO", "OD600"],
        "atlas_color": "gray"
    }
}

# ---------------------------------------------------------------------------
#  B. subtilis  --  Gram-positive  (secreted enzyme / protein production)
# ---------------------------------------------------------------------------
BSUBTILIS_MAP = {

    "glucose": {
        "pathway": "Glycolysis / PTS uptake",
        "gem_reaction": "GLCptspp",
        "gem_model": "iYO844",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "g/L",   "state": "carbon_starved",
                       "meaning": "Carbon depleted -- B. subtilis sporulation cascade initiating -- Spo0A phosphorylation rising"},
            "normal": {"threshold": 5.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose adequate -- vegetative growth sustained -- catabolite repression active"},
            "high":   {"threshold": 12.0, "unit": "g/L",   "state": "overflow_risk",
                       "meaning": "Glucose excess -- overflow to acetoin and 2,3-butanediol via alsSD operon"}
        },
        "downstream_effects": ["acetoin", "ammonia", "OD600"],
        "atlas_color": "amber"
    },

    "acetoin": {
        "pathway": "Overflow metabolism / alsSD pathway",
        "gem_reaction": "ACLDC",
        "gem_model": "iYO844",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Minimal overflow -- carbon efficiently routed through TCA -- no acetoin burden"},
            "normal": {"threshold": 2.0,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Acetoin accumulating -- B. subtilis overflow less toxic than E. coli acetate -- but wastes carbon"},
            "high":   {"threshold": 5.0,  "unit": "g/L",   "state": "overflow",
                       "meaning": "Heavy acetoin overflow -- carbon wasted -- reduce glucose feed -- may convert to 2,3-butanediol"}
        },
        "downstream_effects": ["pH", "OD600", "titer"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Organic acid / Alkaline protease regulation",
        "gem_reaction": "EX_h_e",
        "gem_model": "iYO844",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 6.0,  "unit": "",       "state": "acidosis",
                       "meaning": "Acid stress -- B. subtilis acid tolerance lower than E. coli -- sporulation may trigger"},
            "normal": {"threshold": 7.0,  "unit": "",       "state": "optimal",
                       "meaning": "pH in range -- protease secretion (subtilisin) optimal at neutral to slightly alkaline"},
            "high":   {"threshold": 8.0,  "unit": "",       "state": "alkaline",
                       "meaning": "Alkaline -- B. subtilis tolerates well -- alkaline proteases active -- product may be degraded by host proteases"}
        },
        "downstream_effects": ["acetoin", "CO2", "OD600"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Aerobic respiration / Cytochrome oxidase",
        "gem_reaction": "CYTBD",
        "gem_model": "iYO844",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 10.0, "unit": "%",      "state": "microaerobic",
                       "meaning": "O2 limiting -- B. subtilis can use nitrate as terminal electron acceptor but growth slows significantly"},
            "normal": {"threshold": 30.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen -- obligate aerobe running efficiently"},
            "high":   {"threshold": 80.0, "unit": "%",      "state": "excess",
                       "meaning": "DO excess -- low density or metabolic decline"}
        },
        "downstream_effects": ["acetoin", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Nitrogen assimilation / GlnA-GlnR regulon",
        "gem_reaction": "GLNS",
        "gem_model": "iYO844",
        "direction": "substrate_and_byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "mM",    "state": "nitrogen_limited",
                       "meaning": "Nitrogen depleted -- GlnR regulon derepressed -- sporulation signal strengthening"},
            "normal": {"threshold": 10.0, "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonium adequate -- vegetative growth and protein secretion sustained"},
            "high":   {"threshold": 25.0, "unit": "mM",    "state": "excess",
                       "meaning": "Ammonia excess -- moderate toxicity -- pH may rise as ammonium protonation shifts"}
        },
        "downstream_effects": ["OD600", "pH", "titer"],
        "atlas_color": "red"
    },

    "OD600": {
        "pathway": "Cell growth / Biomass / Sporulation decision",
        "gem_reaction": "BIOMASS_Bs",
        "gem_model": "iYO844",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 5.0,  "unit": "OD",    "state": "lag_or_slow",
                       "meaning": "Low density -- early growth -- secreted enzyme accumulation minimal"},
            "normal": {"threshold": 20.0, "unit": "OD",    "state": "exponential",
                       "meaning": "Healthy vegetative growth -- protease and enzyme secretion increasing"},
            "high":   {"threshold": 50.0, "unit": "OD",    "state": "high_density",
                       "meaning": "High density -- transition to stationary phase -- sporulation pressure increasing -- enzyme secretion peaks"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell integrity / Sporulation / Autolysis",
        "gem_reaction": "AUTOLYSIS",
        "gem_model": "iYO844",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 50.0, "unit": "%",      "state": "autolysis",
                       "meaning": "Extensive autolysis -- B. subtilis autolysin (LytC/LytD) active -- intracellular proteases released -- product degradation"},
            "normal": {"threshold": 75.0, "unit": "%",      "state": "moderate_stress",
                       "meaning": "Some cell lysis -- common in late stationary -- spore fraction increasing"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "healthy",
                       "meaning": "Healthy vegetative cells -- minimal sporulation -- optimal for secreted product"}
        },
        "downstream_effects": ["titer", "OD600"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Sec / Tat secretion pathway / Enzyme production",
        "gem_reaction": "ENZYME_secretion",
        "gem_model": "iYO844",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "low_expression",
                       "meaning": "Secreted enzyme titre low -- check promoter, signal peptide, and protease knockout strain background"},
            "normal": {"threshold": 5.0,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Good enzyme secretion -- B. subtilis can secrete 20-25 g/L of native enzymes -- recombinant lower"},
            "high":   {"threshold": 15.0, "unit": "g/L",   "state": "high_expression",
                       "meaning": "Excellent secretion titre -- B. subtilis workhorse performing well -- verify enzyme activity"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Pyruvate dehydrogenase",
        "gem_reaction": "PDH",
        "gem_model": "iYO844",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "%",      "state": "low_respiration",
                       "meaning": "Low CER -- metabolic slowdown or sporulation diverting carbon"},
            "normal": {"threshold": 8.0,  "unit": "%",      "state": "optimal",
                       "meaning": "Normal respiratory activity -- TCA cycle running"},
            "high":   {"threshold": 14.0, "unit": "%",      "state": "high_respiration",
                       "meaning": "Elevated CER -- high metabolic rate or overflow metabolism"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Terminal oxidase / Electron transport",
        "gem_reaction": "CYTBD",
        "gem_model": "iYO844",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 14.0, "unit": "%",      "state": "high_OUR",
                       "meaning": "High OUR -- B. subtilis is an obligate aerobe -- oxygen critical -- increase sparging immediately"},
            "normal": {"threshold": 18.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal O2 consumption -- aerobic metabolism sustained"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Low O2 demand -- low density or sporulated culture"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate / Sporulation control",
        "gem_reaction": "TEMP_CONTROL",
        "gem_model": "iYO844",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 30.0, "unit": "C",      "state": "reduced_temp",
                       "meaning": "Lower temperature -- slower growth -- may improve protein folding and reduce protease activity"},
            "normal": {"threshold": 37.0, "unit": "C",      "state": "optimal",
                       "meaning": "Optimal B. subtilis growth temperature -- maximum growth rate and enzyme secretion"},
            "high":   {"threshold": 50.0, "unit": "C",      "state": "heat_stress",
                       "meaning": "B. subtilis thermotolerant -- but above 50C protein denaturation risk -- sigB stress response active"}
        },
        "downstream_effects": ["OD600", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / kLa / Foam management",
        "gem_reaction": "kLa",
        "gem_model": "iYO844",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 200.0,"unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Insufficient mixing -- B. subtilis obligate aerobe -- DO will crash without adequate kLa"},
            "normal": {"threshold": 500.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Good mixing -- adequate kLa -- B. subtilis produces surfactin that causes foaming at high agitation"},
            "high":   {"threshold": 800.0,"unit": "rpm",    "state": "foam_risk",
                       "meaning": "High agitation -- surfactin-driven foaming extreme -- antifoam addition needed -- product loss through exhaust"}
        },
        "downstream_effects": ["DO", "OD600"],
        "atlas_color": "gray"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  YEAST HOSTS
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
#  Pichia pastoris (Komagataella phaffii)  --  Methanol-induced secretion
# ---------------------------------------------------------------------------
PICHIA_MAP = {

    "glucose": {
        "pathway": "Glycolysis / Carbon catabolite repression",
        "gem_reaction": "HEX1",
        "gem_model": "iMT1026v3",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "depleted",
                       "meaning": "Glucose depleted -- required for biomass growth phase -- switch to methanol induction if ready"},
            "normal": {"threshold": 3.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose feeding biomass accumulation phase -- AOX1 promoter repressed"},
            "high":   {"threshold": 8.0,  "unit": "g/L",   "state": "excess",
                       "meaning": "Glucose excess -- AOX1 promoter fully repressed -- no methanol utilisation possible -- ethanol overflow"}
        },
        "downstream_effects": ["ethanol", "ammonia", "OD600"],
        "atlas_color": "amber"
    },

    "methanol": {
        "pathway": "Methanol utilisation pathway / AOX1-AOX2",
        "gem_reaction": "AOX",
        "gem_model": "iMT1026v3",
        "direction": "substrate_and_inducer",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "sub_induction",
                       "meaning": "Methanol too low -- AOX1 promoter not fully induced -- product expression suboptimal"},
            "normal": {"threshold": 3.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Methanol in optimal induction range -- AOX pathway active -- protein being secreted"},
            "high":   {"threshold": 8.0,  "unit": "g/L",   "state": "toxic",
                       "meaning": "Methanol accumulating -- formaldehyde and H2O2 toxicity -- cell death -- reduce feed immediately"}
        },
        "downstream_effects": ["DO", "viability", "titer"],
        "atlas_color": "magenta"
    },

    "ethanol": {
        "pathway": "Overflow metabolism / Crabtree-negative overflow",
        "gem_reaction": "ALCD2x",
        "gem_model": "iMT1026v3",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 0.2,  "unit": "g/L",   "state": "optimal",
                       "meaning": "No overflow -- respiratory metabolism only -- Pichia is Crabtree-negative but overfeeding causes ethanol"},
            "normal": {"threshold": 1.0,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Ethanol detected -- glucose feed rate too high -- Pichia producing ethanol under excess carbon"},
            "high":   {"threshold": 3.0,  "unit": "g/L",   "state": "overflow",
                       "meaning": "Significant ethanol -- carbon wasted -- AOX promoter may be partially repressed by ethanol"}
        },
        "downstream_effects": ["pH", "OD600", "titer"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Organic acid balance / Secretion optimization",
        "gem_reaction": "EX_h_e",
        "gem_model": "iMT1026v3",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 5.0,  "unit": "",       "state": "acidic",
                       "meaning": "pH below Pichia target -- protein stability declining -- protease activity increasing below pH 5"},
            "normal": {"threshold": 6.2,  "unit": "",       "state": "optimal",
                       "meaning": "pH in target range for Pichia secretion and AOX1 expression -- protease activity minimised"},
            "high":   {"threshold": 6.8,  "unit": "",       "state": "above_optimum",
                       "meaning": "pH elevated above Pichia target range -- may reduce secretion efficiency -- protease activity increasing"}
        },
        "downstream_effects": ["ethanol", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Oxidative phosphorylation / Methanol oxidation",
        "gem_reaction": "CYTBD",
        "gem_model": "iMT1026v3",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 15.0, "unit": "%",      "state": "hypoxic",
                       "meaning": "DO critically low -- methanol oxidation requires enormous O2 -- formaldehyde accumulating if AOX limited"},
            "normal": {"threshold": 30.0, "unit": "%",      "state": "optimal",
                       "meaning": "DO adequate -- methanol utilisation pathway has very high oxygen demand -- monitor closely"},
            "high":   {"threshold": 70.0, "unit": "%",      "state": "excess",
                       "meaning": "DO excess -- methanol feed may have stopped or cells not consuming -- check methanol level"}
        },
        "downstream_effects": ["methanol", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Nitrogen assimilation",
        "gem_reaction": "GLNS",
        "gem_model": "iMT1026v3",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "mM",    "state": "nitrogen_limited",
                       "meaning": "Nitrogen depleted -- growth will halt -- protein expression continues briefly then stops"},
            "normal": {"threshold": 10.0, "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonium adequate -- Pichia using NH4+ as primary nitrogen source"},
            "high":   {"threshold": 30.0, "unit": "mM",    "state": "excess",
                       "meaning": "Ammonia excess -- pH will rise -- moderate toxicity at high concentrations"}
        },
        "downstream_effects": ["OD600", "pH", "titer"],
        "atlas_color": "red"
    },

    "OD600": {
        "pathway": "Cell growth / Biomass accumulation",
        "gem_reaction": "BIOMASS_Pp",
        "gem_model": "iMT1026v3",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 50.0, "unit": "OD",    "state": "low_density",
                       "meaning": "Density below methanol induction threshold -- continue glucose growth phase"},
            "normal": {"threshold": 200.0,"unit": "OD",    "state": "induction_ready",
                       "meaning": "Density at induction threshold -- switch to methanol feed -- Pichia achieves very high densities"},
            "high":   {"threshold": 400.0,"unit": "OD",    "state": "ultra_high_density",
                       "meaning": "Very high density -- oxygen transfer limiting -- viscosity increasing -- monitor DO carefully"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell integrity / Methanol toxicity response",
        "gem_reaction": "STRESS_RESPONSE",
        "gem_model": "iMT1026v3",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 70.0, "unit": "%",      "state": "critical",
                       "meaning": "Viability low -- methanol toxicity or oxygen starvation -- proteases released degrading product"},
            "normal": {"threshold": 85.0, "unit": "%",      "state": "healthy",
                       "meaning": "Good viability under methanol induction -- some stress expected"},
            "high":   {"threshold": 95.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability -- methanol adaptation successful"}
        },
        "downstream_effects": ["titer", "OD600"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Secretory pathway / Protein secretion",
        "gem_reaction": "RECPROT_secretion",
        "gem_model": "iMT1026v3",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "low_expression",
                       "meaning": "Secretion low -- check methanol level, AOX1 induction, signal peptide, and protein folding in ER"},
            "normal": {"threshold": 3.0,  "unit": "g/L",   "state": "on_track",
                       "meaning": "Good secreted protein titre -- Pichia excellent secretor -- monitor glycosylation (high-mannose risk)"},
            "high":   {"threshold": 10.0, "unit": "g/L",   "state": "high_expression",
                       "meaning": "Excellent secretion -- Pichia performing at top of range -- verify N-glycan profile"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Methanol dissimilation",
        "gem_reaction": "FDH",
        "gem_model": "iMT1026v3",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low CER -- methanol not being consumed or cell density low"},
            "normal": {"threshold": 10.0, "unit": "%",      "state": "optimal",
                       "meaning": "Normal CER -- methanol dissimilation through formate dehydrogenase pathway running"},
            "high":   {"threshold": 18.0, "unit": "%",      "state": "high_respiration",
                       "meaning": "Very high CER -- methanol oxidation consuming enormous O2 -- monitor DO and RQ"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Oxidative metabolism / Methanol oxidation demand",
        "gem_reaction": "AOX",
        "gem_model": "iMT1026v3",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 12.0, "unit": "%",      "state": "high_OUR",
                       "meaning": "Extreme O2 consumption -- methanol oxidation pathway has highest OUR of any bioprocess -- increase sparging"},
            "normal": {"threshold": 17.0, "unit": "%",      "state": "balanced",
                       "meaning": "O2 consumption manageable at current density and methanol feed"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Low O2 demand -- methanol feed may have stopped or density too low"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate / Protein folding",
        "gem_reaction": "TEMP_CONTROL",
        "gem_model": "iMT1026v3",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 25.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Low temperature -- slower methanol metabolism but improved protein folding and secretion for some products"},
            "normal": {"threshold": 30.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard Pichia growth temperature -- maximum methanol utilisation rate"},
            "high":   {"threshold": 35.0, "unit": "C",      "state": "heat_stress",
                       "meaning": "Heat stress -- Pichia upper limit ~35C -- viability dropping -- protein misfolding increasing"}
        },
        "downstream_effects": ["OD600", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / kLa / High-density mixing",
        "gem_reaction": "kLa",
        "gem_model": "iMT1026v3",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 300.0,"unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Mixing insufficient for Pichia high-density culture -- DO will crash during methanol phase"},
            "normal": {"threshold": 700.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Adequate kLa for methanol-phase oxygen demand -- Pichia tolerates high agitation well"},
            "high":   {"threshold": 1200.0,"unit": "rpm",   "state": "extreme",
                       "meaning": "Very high agitation -- needed for ultra-high density -- monitor foam and mechanical seals"}
        },
        "downstream_effects": ["DO", "OD600"],
        "atlas_color": "gray"
    }
}

# ---------------------------------------------------------------------------
#  S. cerevisiae  --  Baker's yeast  (VLP / vaccine antigen production)
# ---------------------------------------------------------------------------
SCEREVISIAE_MAP = {

    "glucose": {
        "pathway": "Glycolysis / Crabtree effect",
        "gem_reaction": "HEX1",
        "gem_model": "iMM904",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 0.5,  "unit": "g/L",   "state": "carbon_limited",
                       "meaning": "Glucose depleted -- diauxic shift -- cells switching to ethanol consumption if ethanol present"},
            "normal": {"threshold": 5.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Glucose adequate -- note: S. cerevisiae is Crabtree-positive -- ethanol at any glucose concentration"},
            "high":   {"threshold": 15.0, "unit": "g/L",   "state": "crabtree_overflow",
                       "meaning": "High glucose -- heavy ethanol overflow via Crabtree effect -- cannot be avoided -- use fed-batch to limit"}
        },
        "downstream_effects": ["ethanol", "ammonia", "OD600"],
        "atlas_color": "amber"
    },

    "ethanol": {
        "pathway": "Crabtree overflow / PDC-ADH pathway",
        "gem_reaction": "ALCD2x",
        "gem_model": "iMM904",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "g/L",   "state": "optimal",
                       "meaning": "Low ethanol -- fed-batch glucose limitation working -- respiratory metabolism dominant"},
            "normal": {"threshold": 5.0,  "unit": "g/L",   "state": "moderate",
                       "meaning": "Ethanol accumulating -- Crabtree effect active -- carbon being wasted -- reduce glucose feed"},
            "high":   {"threshold": 15.0, "unit": "g/L",   "state": "inhibitory",
                       "meaning": "Ethanol inhibitory -- growth slowing -- membrane fluidity disrupted -- VLP assembly may be impaired"}
        },
        "downstream_effects": ["pH", "OD600", "titer"],
        "atlas_color": "coral"
    },

    "pH": {
        "pathway": "Organic acid balance",
        "gem_reaction": "EX_h_e",
        "gem_model": "iMM904",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 4.5,  "unit": "",       "state": "very_acidic",
                       "meaning": "pH below yeast target -- VLP stability compromised -- acid stress response activating"},
            "normal": {"threshold": 5.5,  "unit": "",       "state": "optimal",
                       "meaning": "pH in optimal S. cerevisiae range -- VLP assembly and protein folding proceeding normally"},
            "high":   {"threshold": 6.5,  "unit": "",       "state": "high_for_yeast",
                       "meaning": "pH above yeast target -- bacterial contamination risk increasing -- reduce base addition"}
        },
        "downstream_effects": ["ethanol", "CO2", "viability"],
        "atlas_color": "blue"
    },

    "DO": {
        "pathway": "Aerobic respiration / Crabtree regulation",
        "gem_reaction": "CYTBD",
        "gem_model": "iMM904",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 5.0,  "unit": "%",      "state": "anaerobic",
                       "meaning": "Anaerobic -- full fermentative metabolism -- ethanol production maximised -- bad for VLP/protein yield"},
            "normal": {"threshold": 20.0, "unit": "%",      "state": "optimal",
                       "meaning": "Adequate oxygen -- respiratory-fermentative balance -- keep glucose low to favour respiration"},
            "high":   {"threshold": 70.0, "unit": "%",      "state": "excess",
                       "meaning": "High DO -- low density or culture in stationary phase"}
        },
        "downstream_effects": ["ethanol", "CO2", "O2"],
        "atlas_color": "teal"
    },

    "ammonia": {
        "pathway": "Nitrogen assimilation / NCR regulation",
        "gem_reaction": "GLNS",
        "gem_model": "iMM904",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 1.0,  "unit": "mM",    "state": "nitrogen_limited",
                       "meaning": "Nitrogen depleted -- nitrogen catabolite repression (NCR) derepressed -- autophagy initiating"},
            "normal": {"threshold": 10.0, "unit": "mM",    "state": "optimal",
                       "meaning": "Ammonium adequate for yeast growth and VLP/antigen production"},
            "high":   {"threshold": 30.0, "unit": "mM",    "state": "excess",
                       "meaning": "Ammonia excess -- pH rising -- moderate stress"}
        },
        "downstream_effects": ["OD600", "pH", "titer"],
        "atlas_color": "red"
    },

    "OD600": {
        "pathway": "Cell growth / Biomass",
        "gem_reaction": "BIOMASS_SC5_notrace",
        "gem_model": "iMM904",
        "direction": "output",
        "flux_interpretation": {
            "low":    {"threshold": 5.0,  "unit": "OD",    "state": "lag_or_slow",
                       "meaning": "Low density -- early growth phase -- VLP accumulation minimal"},
            "normal": {"threshold": 20.0, "unit": "OD",    "state": "exponential",
                       "meaning": "Healthy growth -- galactose induction window for GAL promoter systems approaching"},
            "high":   {"threshold": 50.0, "unit": "OD",    "state": "high_density",
                       "meaning": "High density -- stationary phase approaching -- VLP accumulation should be near peak"}
        },
        "downstream_effects": ["glucose", "DO", "ammonia"],
        "atlas_color": "green"
    },

    "viability": {
        "pathway": "Cell integrity / Stress response",
        "gem_reaction": "STRESS_RESPONSE",
        "gem_model": "iMM904",
        "direction": "indicator",
        "flux_interpretation": {
            "low":    {"threshold": 70.0, "unit": "%",      "state": "critical",
                       "meaning": "Viability low -- yeast autolysis releasing proteases -- VLP degradation -- harvest immediately"},
            "normal": {"threshold": 85.0, "unit": "%",      "state": "healthy",
                       "meaning": "Good viability -- S. cerevisiae robust -- VLP integrity maintained"},
            "high":   {"threshold": 96.0, "unit": "%",      "state": "excellent",
                       "meaning": "Excellent viability -- optimal for intracellular VLP accumulation"}
        },
        "downstream_effects": ["titer", "OD600"],
        "atlas_color": "green"
    },

    "titer": {
        "pathway": "Intracellular VLP accumulation / Secreted antigen",
        "gem_reaction": "VLP_assembly",
        "gem_model": "iMM904",
        "direction": "product",
        "flux_interpretation": {
            "low":    {"threshold": 0.1,  "unit": "g/L",   "state": "low_expression",
                       "meaning": "VLP/antigen titre low -- check promoter induction (GAL/AOX), codon optimization, and copy number"},
            "normal": {"threshold": 0.5,  "unit": "g/L",   "state": "on_track",
                       "meaning": "VLP accumulating -- intracellular product -- cell lysis method will be critical for recovery"},
            "high":   {"threshold": 2.0,  "unit": "g/L",   "state": "high_expression",
                       "meaning": "Good VLP titre -- verify particle assembly and antigen display by EM or DLS"}
        },
        "downstream_effects": [],
        "atlas_color": "purple"
    },

    "CO2": {
        "pathway": "TCA cycle / Fermentation",
        "gem_reaction": "PDC",
        "gem_model": "iMM904",
        "direction": "byproduct",
        "flux_interpretation": {
            "low":    {"threshold": 2.0,  "unit": "%",      "state": "low_metabolism",
                       "meaning": "Low CER -- culture in stationary or density very low"},
            "normal": {"threshold": 10.0, "unit": "%",      "state": "optimal",
                       "meaning": "Normal CER -- respiratory-fermentative metabolism running"},
            "high":   {"threshold": 20.0, "unit": "%",      "state": "high_fermentation",
                       "meaning": "Very high CER -- heavy fermentation (Crabtree) -- ethanol production dominant -- switch to fed-batch"}
        },
        "downstream_effects": ["pH", "DO"],
        "atlas_color": "amber"
    },

    "O2": {
        "pathway": "Respiratory chain / Cytochrome oxidase",
        "gem_reaction": "CYTBD",
        "gem_model": "iMM904",
        "direction": "substrate",
        "flux_interpretation": {
            "low":    {"threshold": 15.0, "unit": "%",      "state": "high_OUR",
                       "meaning": "High O2 consumption -- increase sparging -- yeast has high respiratory capacity when not Crabtree-limited"},
            "normal": {"threshold": 19.0, "unit": "%",      "state": "balanced",
                       "meaning": "Normal O2 consumption"},
            "high":   {"threshold": 21.0, "unit": "%",      "state": "low_demand",
                       "meaning": "Minimal O2 consumption -- fermentative or low density"}
        },
        "downstream_effects": ["DO", "CO2"],
        "atlas_color": "teal"
    },

    "temperature": {
        "pathway": "Global metabolic rate / Stress response",
        "gem_reaction": "TEMP_CONTROL",
        "gem_model": "iMM904",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 25.0, "unit": "C",      "state": "cold_shift",
                       "meaning": "Lower temperature -- slower growth but improved protein folding -- VLP assembly may benefit"},
            "normal": {"threshold": 30.0, "unit": "C",      "state": "optimal",
                       "meaning": "Standard S. cerevisiae growth temperature -- optimal for most expression systems"},
            "high":   {"threshold": 37.0, "unit": "C",      "state": "heat_stress",
                       "meaning": "Heat stress for yeast -- Hsf1/Msn2/4 heat shock response -- trehalose accumulating -- growth impaired"}
        },
        "downstream_effects": ["OD600", "titer", "viability"],
        "atlas_color": "coral"
    },

    "agitation": {
        "pathway": "Mass transfer / kLa",
        "gem_reaction": "kLa",
        "gem_model": "iMM904",
        "direction": "control",
        "flux_interpretation": {
            "low":    {"threshold": 150.0,"unit": "rpm",    "state": "poor_mixing",
                       "meaning": "Mixing insufficient -- yeast settling -- DO gradients forming"},
            "normal": {"threshold": 400.0,"unit": "rpm",    "state": "optimal",
                       "meaning": "Adequate mixing for yeast -- good kLa -- S. cerevisiae tolerates moderate shear"},
            "high":   {"threshold": 700.0,"unit": "rpm",    "state": "high_shear",
                       "meaning": "High agitation -- yeast tolerates well but foam may increase -- add antifoam if needed"}
        },
        "downstream_effects": ["DO", "OD600"],
        "atlas_color": "gray"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  POST-PROCESSING: Reaction corrections & reaction_type annotation
#  (Runs BEFORE strain building so all strains inherit these fixes)
# ═══════════════════════════════════════════════════════════════════════════

# Reaction type classification for every gem_reaction used in the maps
_REACTION_TYPE_MAP = {
    # Real GEM stoichiometric reactions (in published models)
    "HEX1": "metabolic",  "LDH_L": "metabolic",  "ATPM": "metabolic",
    "CYTBD": "metabolic", "COXE": "metabolic",    "CYTB_B2": "metabolic",
    "CYOOm": "metabolic", "GLNS": "metabolic",
    "CS": "metabolic",    "PDH": "metabolic",     "GLCptspp": "metabolic",
    "PTAr": "metabolic",  "EX_h_e": "metabolic",  "CYTBO3_4pp": "metabolic",
    "ACLDC": "metabolic", "AOX": "metabolic",     "AOX2": "metabolic",
    "ALCD2x": "metabolic","FDH": "metabolic",     "PDC": "metabolic",
    "GLNS_absent": "metabolic", "GLNS_knockout": "metabolic",
    # Custom exchange / product sinks (added to model for bioprocess context)
    "IgG_production": "custom_exchange",
    "AAV_assembly": "custom_exchange",
    "LV_production": "custom_exchange",
    "RECPROT_expression": "custom_exchange",
    "RECPROT_secretion": "custom_exchange",
    "ENZYME_secretion": "custom_exchange",
    "VLP_assembly": "custom_exchange",
    "PRODUCT_expression": "custom_exchange",
    "BIOMASS_cho": "custom_exchange",
    "BIOMASS_hek293": "custom_exchange",
    "BIOMASS_ns0": "custom_exchange",
    "BIOMASS_sp20": "custom_exchange",
    "BIOMASS_bhk": "custom_exchange",
    "BIOMASS_Ec_iML1515_core_75p37M": "custom_exchange",
    "BIOMASS_Bs": "custom_exchange",
    "BIOMASS_Pp": "custom_exchange",
    "BIOMASS_SC5_notrace": "custom_exchange",
    # Control placeholders (process engineering variables, not in GEM)
    "kLa": "control_placeholder",
    "TEMP_SHIFT": "control_placeholder",
    "TEMP_CONTROL": "control_placeholder",
    # Biological state indicators (not stoichiometric reactions)
    "APOPTOSIS": "biological_state",
    "STRESS_RESPONSE": "biological_state",
    "AUTOLYSIS": "biological_state",
}

_MAMMALIAN_BASE_MAPS = [CHO_MAP, CHOS_MAP, HEK293_MAP, NS0_MAP, SP20_MAP, BHK21_MAP]
_ALL_BASE_MAPS = _MAMMALIAN_BASE_MAPS + [ECOLI_MAP, BSUBTILIS_MAP, PICHIA_MAP, SCEREVISIAE_MAP]

# Fix 1: CYTBD -> COXE in mammalian maps only
# CYTBD (cytochrome bd ubiquinol oxidase) is prokaryotic.
# Mammalian cells use cytochrome c oxidase (Complex IV) = COXE.
for _m in _MAMMALIAN_BASE_MAPS:
    for _entry in _m.values():
        if _entry.get("gem_reaction") == "CYTBD":
            _entry["gem_reaction"] = "COXE"

# Fix 5: CYTBD -> CYTB_B2 in B. subtilis (iYO844)
# CYTBD does not exist in iYO844. B. subtilis uses menaquinol oxidases.
# CYTB_B2 = menaquinol:O2 oxidoreductase (cytochrome bd, cydAB operon).
for _entry in BSUBTILIS_MAP.values():
    if _entry.get("gem_reaction") == "CYTBD":
        _entry["gem_reaction"] = "CYTB_B2"

# Fix 6: CYTBD -> CYOOm in S. cerevisiae (iMM904)
# CYTBD does not exist in iMM904. S. cerevisiae uses mitochondrial
# cytochrome c oxidase (Complex IV) = CYOOm.
for _entry in SCEREVISIAE_MAP.values():
    if _entry.get("gem_reaction") == "CYTBD":
        _entry["gem_reaction"] = "CYOOm"

# Fix 6b: CYTBD -> CYOOm in P. pastoris (iMT1026v3) DO parameter only
# iMT1026v3 cytochrome c oxidase confirmed in SBML as UUID ca2f164e...
# Using CYOOm as human-readable ID consistent with iMM904 convention.
# AOX kept for O2 parameter (primary O2 consumer during methanol phase).
if PICHIA_MAP["DO"].get("gem_reaction") == "CYTBD":
    PICHIA_MAP["DO"]["gem_reaction"] = "CYOOm"

# Fix 2: Add reaction_type field to every parameter entry in all base maps
for _m in _ALL_BASE_MAPS:
    for _entry in _m.values():
        _rxn = _entry.get("gem_reaction", "")
        _entry["reaction_type"] = _REACTION_TYPE_MAP.get(_rxn, "metabolic")


# ═══════════════════════════════════════════════════════════════════════════
#  STRAIN SYSTEM  --  Inheritance-based strain overrides
# ═══════════════════════════════════════════════════════════════════════════

import copy


def _build_strain_map(parent_map, overrides):
    """Deep-copy a parent organism map and apply strain-specific overrides.

    overrides is a dict of { parameter: { field: value, ... } }
    where field can be dotted like "flux_interpretation.low.threshold"
    or top-level like "gem_model", "pathway", etc.
    """
    strain_map = copy.deepcopy(parent_map)
    for param, changes in overrides.items():
        if param not in strain_map:
            continue
        for field, value in changes.items():
            parts = field.split(".")
            target = strain_map[param]
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = value
    return strain_map


# ---------------------------------------------------------------------------
#  STRAIN REGISTRY -- each entry: description, parent map, overrides
# ---------------------------------------------------------------------------

STRAIN_REGISTRY = {

    # ── CHO STRAINS ──────────────────────────────────────────────────────
    "CHO": {
        "CHO-K1": {
            "description": "Standard CHO-K1 -- ATCC CCL-61 -- baseline workhorse for mAb production",
            "parent": "CHO_MAP",
            "overrides": {}  # CHO-K1 IS the baseline -- no overrides needed
        },
        "CHO-DG44": {
            "description": "DHFR-deficient -- requires thymidine/hypoxanthine -- MTX amplification for gene copy number",
            "parent": "CHO_MAP",
            "overrides": {
                "glucose": {
                    "flux_interpretation.low.threshold": 1.8,
                    "flux_interpretation.low.meaning": "Glucose depleted -- CHO-DG44 has higher glycolytic flux than K1 due to DHFR-MTX metabolic burden -- feed immediately",
                    "flux_interpretation.high.threshold": 5.5,
                    "flux_interpretation.high.meaning": "Excess glucose -- CHO-DG44 more prone to lactate overflow under MTX selection pressure",
                },
                "lactate": {
                    "flux_interpretation.low.threshold": 0.8,
                    "flux_interpretation.normal.threshold": 2.5,
                    "flux_interpretation.normal.meaning": "Moderate lactate -- CHO-DG44 typically produces 20-30% more lactate than K1 at same glucose",
                    "flux_interpretation.high.threshold": 4.5,
                },
                "VCD": {
                    "flux_interpretation.low.threshold": 4.0,
                    "flux_interpretation.low.meaning": "Growth below target -- check thymidine/hypoxanthine supplementation and MTX concentration",
                    "flux_interpretation.normal.threshold": 12.0,
                    "flux_interpretation.normal.meaning": "Healthy growth -- MTX-amplified cells growing at expected rate",
                    "flux_interpretation.high.threshold": 25.0,
                    "flux_interpretation.high.meaning": "Peak density -- DG44 typically reaches lower peak than K1 due to metabolic burden of amplified gene copies",
                },
                "titer": {
                    "flux_interpretation.normal.threshold": 2.5,
                    "flux_interpretation.high.threshold": 5.0,
                    "flux_interpretation.high.meaning": "High titre -- MTX amplification yielding high gene copy number -- verify stability without MTX pressure",
                },
                "ammonia": {
                    "flux_interpretation.high.threshold": 7.0,
                    "flux_interpretation.high.meaning": "Ammonia toxic -- DG44 slightly more ammonia-sensitive than K1 -- glycosylation heterogeneity increasing",
                },
            }
        },
        "CHO-S": {
            "description": "Suspension-adapted -- optimised for serum-free high-density perfusion culture",
            "parent": "CHOS_MAP",
            "overrides": {}  # CHO-S already has its own full map
        },
        "CHO-GS": {
            "description": "Glutamine synthetase deficient -- MSX selection -- no exogenous glutamine needed post-selection",
            "parent": "CHO_MAP",
            "overrides": {
                "ammonia": {
                    "pathway": "GS-knockout metabolism / MSX selection",
                    "gem_reaction": "GLNS_knockout",
                    "flux_interpretation.low.threshold": 1.0,
                    "flux_interpretation.low.meaning": "Ammonia very low -- GS-knockout cells cannot recycle ammonia -- glutamine supply adequate",
                    "flux_interpretation.normal.threshold": 3.0,
                    "flux_interpretation.normal.meaning": "Ammonia rising -- CHO-GS lacks glutamine synthetase -- cannot assimilate NH4+ -- monitor closely",
                    "flux_interpretation.high.threshold": 5.0,
                    "flux_interpretation.high.meaning": "Ammonia toxic -- CHO-GS MORE sensitive than wild-type due to GS deficiency -- cannot detoxify via glutamine synthesis -- reduce glutamine feed",
                },
                "VCD": {
                    "flux_interpretation.low.threshold": 4.0,
                    "flux_interpretation.low.meaning": "Growth slow -- check MSX concentration not inhibiting -- verify glutamine-free media adapted",
                    "flux_interpretation.normal.threshold": 14.0,
                    "flux_interpretation.high.threshold": 28.0,
                },
                "titer": {
                    "flux_interpretation.normal.threshold": 2.5,
                    "flux_interpretation.high.threshold": 6.0,
                    "flux_interpretation.high.meaning": "Excellent titre -- GS system often yields higher specific productivity than DHFR -- maintain MSX selection",
                },
                "lactate": {
                    "flux_interpretation.normal.threshold": 1.8,
                    "flux_interpretation.normal.meaning": "Moderate lactate -- CHO-GS typically produces less lactate than DG44 -- cleaner metabolism",
                    "flux_interpretation.high.threshold": 3.5,
                    "flux_interpretation.high.meaning": "Lactate elevated -- unusual for GS system -- check glucose feed rate and DO",
                },
            }
        },
    },

    # ── E. COLI STRAINS ──────────────────────────────────────────────────
    "E. coli": {
        "BL21(DE3)": {
            "description": "T7 expression -- lon/ompT protease-deficient -- standard for inclusion body production",
            "parent": "ECOLI_MAP",
            "overrides": {
                "titer": {
                    "pathway": "T7 RNAP expression / Inclusion body formation",
                    "flux_interpretation.normal.threshold": 1.5,
                    "flux_interpretation.high.threshold": 8.0,
                    "flux_interpretation.high.meaning": "Very high expression -- BL21(DE3) T7 system at full power -- mostly inclusion bodies -- plan refolding",
                },
                "viability": {
                    "flux_interpretation.low.threshold": 55.0,
                    "flux_interpretation.low.meaning": "Extensive lysis -- BL21 lon-protease deficient -- less intracellular degradation but more lysis under T7 overexpression burden",
                    "flux_interpretation.normal.threshold": 75.0,
                    "flux_interpretation.normal.meaning": "Moderate stress -- T7 overexpression metabolic burden causing growth arrest -- typical post-IPTG",
                },
                "temperature": {
                    "flux_interpretation.low.threshold": 25.0,
                    "flux_interpretation.low.meaning": "Low temp -- reduces T7 RNAP activity -- shifts product toward soluble fraction -- slower but better folding",
                },
            }
        },
        "BL21 Star": {
            "description": "rne131 mutation -- stabilised mRNA -- higher expression from same IPTG induction",
            "parent": "ECOLI_MAP",
            "overrides": {
                "titer": {
                    "pathway": "T7 expression / mRNA-stabilised (rne131)",
                    "flux_interpretation.low.threshold": 0.3,
                    "flux_interpretation.low.meaning": "Expression low despite rne131 -- check IPTG concentration -- mRNA stable but translation may be limiting",
                    "flux_interpretation.normal.threshold": 2.0,
                    "flux_interpretation.normal.meaning": "Good expression -- rne131 stabilising mRNA -- 2-5x more protein than standard BL21(DE3)",
                    "flux_interpretation.high.threshold": 10.0,
                    "flux_interpretation.high.meaning": "Very high expression -- Star strain at maximum -- toxicity risk from protein burden -- reduce IPTG",
                },
                "viability": {
                    "flux_interpretation.low.threshold": 50.0,
                    "flux_interpretation.low.meaning": "Severe lysis -- BL21 Star overexpression burden even higher than DE3 due to mRNA stability -- harvest immediately",
                    "flux_interpretation.normal.threshold": 72.0,
                    "flux_interpretation.normal.meaning": "Stress expected -- rne131 increases metabolic burden -- Star strain has faster viability decline post-induction",
                },
            }
        },
        "HMS174(DE3)": {
            "description": "recA- K-12 derivative -- reduced recombination -- stable for repetitive sequences and plasmids with direct repeats",
            "parent": "ECOLI_MAP",
            "overrides": {
                "OD600": {
                    "flux_interpretation.normal.threshold": 25.0,
                    "flux_interpretation.normal.meaning": "Healthy growth -- HMS174 grows slightly slower than BL21 -- K-12 derived with full restriction systems",
                    "flux_interpretation.high.threshold": 60.0,
                    "flux_interpretation.high.meaning": "High density -- HMS174 does not reach BL21-level densities -- adequate for most expression",
                },
                "titer": {
                    "pathway": "Recombinant expression / Plasmid-stable (recA-)",
                    "flux_interpretation.low.threshold": 0.15,
                    "flux_interpretation.low.meaning": "Expression lower than BL21 -- HMS174 has active restriction -- transformation efficiency lower -- but plasmid is stable",
                    "flux_interpretation.normal.threshold": 0.8,
                    "flux_interpretation.high.threshold": 3.0,
                    "flux_interpretation.high.meaning": "Good titre for recA- strain -- plasmid structural integrity maintained -- no recombination-driven loss",
                },
                "acetate": {
                    "flux_interpretation.normal.threshold": 1.5,
                    "flux_interpretation.normal.meaning": "Acetate accumulating -- HMS174 (K-12) has slightly different acetate metabolism than BL21 (B-strain)",
                },
            }
        },
        "K-12 MG1655": {
            "description": "Wild-type K-12 reference -- fully sequenced -- no lambda phage -- complete restriction systems",
            "parent": "ECOLI_MAP",
            "overrides": {
                "OD600": {
                    "flux_interpretation.normal.threshold": 20.0,
                    "flux_interpretation.normal.meaning": "Normal K-12 growth -- MG1655 is the reference wild-type -- has all restriction enzymes active",
                    "flux_interpretation.high.threshold": 50.0,
                    "flux_interpretation.high.meaning": "High density for K-12 -- MG1655 typically lower max density than B-strains",
                },
                "titer": {
                    "pathway": "Native expression / Reference strain",
                    "flux_interpretation.low.threshold": 0.1,
                    "flux_interpretation.low.meaning": "Low expression expected -- MG1655 has active proteases (lon, ompT) -- recombinant protein may be degraded",
                    "flux_interpretation.normal.threshold": 0.5,
                    "flux_interpretation.high.threshold": 2.0,
                    "flux_interpretation.high.meaning": "Surprisingly high for wild-type -- verify protein not being degraded -- check lon protease activity",
                },
                "acetate": {
                    "flux_interpretation.low.threshold": 0.3,
                    "flux_interpretation.normal.threshold": 1.5,
                    "flux_interpretation.normal.meaning": "K-12 acetate metabolism -- MG1655 has efficient acs (acetyl-CoA synthetase) for acetate reassimilation",
                    "flux_interpretation.high.threshold": 4.0,
                },
            }
        },
        "W3110": {
            "description": "FDA-approved K-12 lineage -- used in commercial biologics (insulin, hGH) -- regulatory track record",
            "parent": "ECOLI_MAP",
            "overrides": {
                "OD600": {
                    "flux_interpretation.normal.threshold": 25.0,
                    "flux_interpretation.high.threshold": 65.0,
                    "flux_interpretation.high.meaning": "High density -- W3110 well-characterised at scale -- FDA-approved lineage for commercial production",
                },
                "titer": {
                    "pathway": "Recombinant expression / FDA-lineage",
                    "flux_interpretation.normal.threshold": 1.0,
                    "flux_interpretation.high.threshold": 6.0,
                    "flux_interpretation.high.meaning": "High expression -- W3110 proven at commercial scale -- Humulin (insulin) produced in this lineage",
                },
                "acetate": {
                    "flux_interpretation.normal.threshold": 1.8,
                    "flux_interpretation.normal.meaning": "Moderate acetate -- W3110 has well-characterised overflow profile -- extensive fed-batch protocols available",
                },
                "temperature": {
                    "flux_interpretation.low.threshold": 28.0,
                    "flux_interpretation.low.meaning": "Reduced temperature -- W3110 commonly run at 28-30C for soluble expression in commercial processes",
                },
            }
        },
    },

    # ── HEK293 STRAINS ───────────────────────────────────────────────────
    "HEK293": {
        "HEK293T": {
            "description": "SV40 large T antigen -- episomal replication of SV40-ori plasmids -- lentivirus production workhorse",
            "parent": "HEK293_MAP",
            "overrides": {
                "titer": {
                    "pathway": "Lentivirus production / SV40 T-antigen amplification",
                    "gem_reaction": "LV_production",
                    "flux_interpretation.low.threshold": 1e5,
                    "flux_interpretation.low.state": "low_production",
                    "flux_interpretation.low.unit": "TU/mL",
                    "flux_interpretation.low.meaning": "Lentivirus titre low -- check plasmid ratio (transfer:packaging:envelope) -- SV40 T amplification should boost yield",
                    "flux_interpretation.normal.threshold": 1e7,
                    "flux_interpretation.normal.unit": "TU/mL",
                    "flux_interpretation.normal.meaning": "Lentivirus production on target -- SV40-ori episomal replication amplifying plasmid copy number",
                    "flux_interpretation.high.threshold": 1e9,
                    "flux_interpretation.high.unit": "TU/mL",
                    "flux_interpretation.high.meaning": "Excellent lentivirus titre -- verify functional titre vs physical particles",
                },
                "VCD": {
                    "flux_interpretation.normal.threshold": 2.5,
                    "flux_interpretation.normal.meaning": "Optimal transfection density for 293T -- SV40 T antigen does not significantly alter growth rate",
                    "flux_interpretation.high.threshold": 5.0,
                    "flux_interpretation.high.meaning": "High density -- 293T tolerates higher density than 293 for lentivirus -- but transfect before confluence",
                },
                "viability": {
                    "flux_interpretation.low.threshold": 60.0,
                    "flux_interpretation.low.meaning": "Viability low -- lentiviral budding causing membrane damage -- harvest supernatant now -- 293T fragile",
                    "flux_interpretation.normal.threshold": 75.0,
                    "flux_interpretation.normal.meaning": "Expected post-transfection drop -- 293T slightly more fragile than parental 293 due to SV40 T expression",
                },
            }
        },
        "HEK293F": {
            "description": "FreeStyle suspension-adapted -- serum-free -- optimised for transient transfection at scale",
            "parent": "HEK293_MAP",
            "overrides": {
                "VCD": {
                    "flux_interpretation.low.threshold": 0.8,
                    "flux_interpretation.low.meaning": "Low density -- 293F suspension culture may need adaptation period from thaw",
                    "flux_interpretation.normal.threshold": 2.5,
                    "flux_interpretation.normal.meaning": "Optimal transfection window for 293F suspension -- typically 1.5-2.5e6 for PEI transfection",
                    "flux_interpretation.high.threshold": 5.0,
                    "flux_interpretation.high.meaning": "High density for 293F -- dilute before transfection -- PEI efficiency drops above 3e6/mL",
                },
                "agitation": {
                    "flux_interpretation.low.threshold": 80.0,
                    "flux_interpretation.low.meaning": "Mixing too low -- 293F suspension cells will settle and clump -- increase to 125+ rpm",
                    "flux_interpretation.normal.threshold": 150.0,
                    "flux_interpretation.normal.meaning": "Optimal for 293F suspension -- orbital shaker or spinner flask -- cells in single-cell suspension",
                    "flux_interpretation.high.threshold": 220.0,
                    "flux_interpretation.high.meaning": "Shear risk -- 293F very shear-sensitive in suspension -- reduce agitation -- cell damage increasing",
                },
                "lactate": {
                    "flux_interpretation.normal.threshold": 2.0,
                    "flux_interpretation.normal.meaning": "Moderate lactate -- 293F serum-free metabolism produces slightly less lactate than adherent 293",
                    "flux_interpretation.high.threshold": 4.0,
                },
            }
        },
    },

    # ── PICHIA STRAINS ───────────────────────────────────────────────────
    "P. pastoris": {
        "X-33": {
            "description": "Mut+ wild-type methanol utilisation -- both AOX1 and AOX2 active -- fast methanol consumption",
            "parent": "PICHIA_MAP",
            "overrides": {
                "methanol": {
                    "flux_interpretation.low.meaning": "Methanol low -- X-33 (Mut+) consumes methanol rapidly -- increase feed rate -- both AOX1 and AOX2 active",
                    "flux_interpretation.normal.meaning": "Methanol optimal -- X-33 Mut+ full methanol utilisation -- high O2 demand -- monitor DO closely",
                    "flux_interpretation.high.threshold": 7.0,
                    "flux_interpretation.high.meaning": "Methanol accumulating -- even X-33 Mut+ cannot consume fast enough -- formaldehyde toxicity risk -- reduce feed",
                },
                "DO": {
                    "flux_interpretation.low.threshold": 18.0,
                    "flux_interpretation.low.meaning": "DO critical for X-33 Mut+ -- highest OUR of any Pichia strain -- both AOX1+AOX2 consuming O2 maximally",
                },
            }
        },
        "KM71H": {
            "description": "MutS (aox1::ARG4) -- AOX1 disrupted -- only AOX2 active -- slow methanol consumption -- easier DO control",
            "parent": "PICHIA_MAP",
            "overrides": {
                "methanol": {
                    "pathway": "Methanol utilisation pathway / AOX2 only (MutS)",
                    "gem_reaction": "AOX2",
                    "flux_interpretation.low.threshold": 1.0,
                    "flux_interpretation.low.meaning": "Methanol low -- KM71H (MutS) uses only AOX2 -- slower consumption -- lower feed rate needed than Mut+",
                    "flux_interpretation.normal.threshold": 5.0,
                    "flux_interpretation.normal.meaning": "Methanol adequate for KM71H MutS -- AOX2 only -- expression slower but DO easier to control",
                    "flux_interpretation.high.threshold": 10.0,
                    "flux_interpretation.high.meaning": "Methanol accumulating -- KM71H MutS metabolises slowly -- formaldehyde building up -- reduce feed significantly",
                },
                "DO": {
                    "flux_interpretation.low.threshold": 12.0,
                    "flux_interpretation.low.meaning": "DO low -- KM71H MutS has lower OUR than Mut+ -- if DO dropping at this rate, check other O2 consumers",
                    "flux_interpretation.normal.threshold": 25.0,
                    "flux_interpretation.normal.meaning": "DO adequate -- KM71H MutS much easier to oxygenate than X-33 Mut+ -- main advantage of MutS phenotype",
                },
                "titer": {
                    "flux_interpretation.low.threshold": 0.3,
                    "flux_interpretation.low.meaning": "Expression lower than Mut+ -- KM71H MutS trades expression speed for DO controllability -- expected",
                    "flux_interpretation.normal.threshold": 2.0,
                    "flux_interpretation.normal.meaning": "Good titre for MutS -- expression slower but protein quality often better due to lower metabolic stress",
                },
                "agitation": {
                    "flux_interpretation.low.threshold": 250.0,
                    "flux_interpretation.low.meaning": "Mixing low but KM71H MutS needs less O2 than Mut+ -- may be adequate if density not extreme",
                    "flux_interpretation.normal.threshold": 600.0,
                },
            }
        },
    },

    # ── S. CEREVISIAE STRAINS ────────────────────────────────────────────
    "S. cerevisiae": {
        "BY4741": {
            "description": "S288C derivative -- MATa his3 leu2 met15 ura3 -- standard lab reference -- complete deletion collection available",
            "parent": "SCEREVISIAE_MAP",
            "overrides": {
                "OD600": {
                    "flux_interpretation.normal.threshold": 15.0,
                    "flux_interpretation.normal.meaning": "Normal BY4741 growth -- auxotrophic markers (his3/leu2/met15/ura3) require supplementation or plasmid complementation",
                    "flux_interpretation.high.threshold": 35.0,
                    "flux_interpretation.high.meaning": "High density for BY4741 -- lab strain reaches lower density than industrial strains -- auxotrophies limit growth",
                },
                "titer": {
                    "flux_interpretation.low.meaning": "Expression low -- BY4741 not optimised for industrial production -- lab reference strain -- use CEN.PK for higher yields",
                    "flux_interpretation.normal.threshold": 0.3,
                    "flux_interpretation.high.threshold": 1.0,
                },
                "glucose": {
                    "flux_interpretation.high.threshold": 12.0,
                    "flux_interpretation.high.meaning": "BY4741 strong Crabtree -- S288C background has particularly high ethanol overflow -- more fermentative than CEN.PK",
                },
            }
        },
        "CEN.PK": {
            "description": "Industrial reference -- good growth on defined media -- moderate Crabtree -- preferred for metabolic engineering",
            "parent": "SCEREVISIAE_MAP",
            "overrides": {
                "OD600": {
                    "flux_interpretation.normal.threshold": 25.0,
                    "flux_interpretation.normal.meaning": "Good CEN.PK growth -- industrial strain grows well on defined media -- preferred for metabolic engineering",
                    "flux_interpretation.high.threshold": 60.0,
                    "flux_interpretation.high.meaning": "High density -- CEN.PK reaches higher densities than BY4741 -- robust industrial strain",
                },
                "ethanol": {
                    "flux_interpretation.normal.threshold": 4.0,
                    "flux_interpretation.normal.meaning": "Ethanol moderate -- CEN.PK has slightly lower Crabtree effect than S288C (BY4741) -- more respiratory",
                    "flux_interpretation.high.threshold": 12.0,
                },
                "titer": {
                    "flux_interpretation.normal.threshold": 0.8,
                    "flux_interpretation.normal.meaning": "Good VLP/protein production -- CEN.PK widely used for metabolic engineering and industrial production",
                    "flux_interpretation.high.threshold": 3.0,
                    "flux_interpretation.high.meaning": "Excellent titre -- CEN.PK performing at industrial level",
                },
                "glucose": {
                    "flux_interpretation.normal.threshold": 6.0,
                    "flux_interpretation.normal.meaning": "Glucose adequate -- CEN.PK better at respiratory growth than BY4741 when glucose kept moderate",
                },
            }
        },
        "W303": {
            "description": "Research strain -- MATa ade2 his3 leu2 trp1 ura3 -- widely used in cell biology -- ade2 gives red colour when starved",
            "parent": "SCEREVISIAE_MAP",
            "overrides": {
                "OD600": {
                    "flux_interpretation.normal.threshold": 18.0,
                    "flux_interpretation.normal.meaning": "Normal W303 growth -- ade2 mutant accumulates red pigment when adenine limited -- supplement adenine",
                    "flux_interpretation.high.threshold": 40.0,
                    "flux_interpretation.high.meaning": "High density for W303 -- research strain -- check adenine supplementation to avoid pigment accumulation",
                },
                "titer": {
                    "flux_interpretation.low.meaning": "Expression low -- W303 research strain -- not optimised for production -- ade2 mutation may affect folding of some proteins",
                    "flux_interpretation.normal.threshold": 0.4,
                    "flux_interpretation.high.threshold": 1.5,
                },
                "viability": {
                    "flux_interpretation.low.threshold": 65.0,
                    "flux_interpretation.low.meaning": "Viability dropping -- W303 less robust than CEN.PK under industrial stress conditions",
                    "flux_interpretation.normal.threshold": 82.0,
                },
            }
        },
    },
}

# ---------------------------------------------------------------------------
#  Build all strain maps from registry
# ---------------------------------------------------------------------------

# Map parent name strings to actual map objects
_PARENT_MAP_LOOKUP = {
    "CHO_MAP":          CHO_MAP,
    "CHOS_MAP":         CHOS_MAP,
    "HEK293_MAP":       HEK293_MAP,
    "NS0_MAP":          NS0_MAP,
    "SP20_MAP":         SP20_MAP,
    "BHK21_MAP":        BHK21_MAP,
    "ECOLI_MAP":        ECOLI_MAP,
    "BSUBTILIS_MAP":    BSUBTILIS_MAP,
    "PICHIA_MAP":       PICHIA_MAP,
    "SCEREVISIAE_MAP":  SCEREVISIAE_MAP,
}

# Built strain maps: { "CHO|CHO-K1": {...map...}, ... }
STRAIN_MAPS = {}
STRAIN_INFO = {}  # { "CHO|CHO-K1": { "organism", "strain", "description" } }

for organism, strains in STRAIN_REGISTRY.items():
    for strain_name, strain_def in strains.items():
        parent_map = _PARENT_MAP_LOOKUP[strain_def["parent"]]
        strain_key = f"{organism}|{strain_name}"
        STRAIN_MAPS[strain_key] = _build_strain_map(parent_map, strain_def["overrides"])
        STRAIN_INFO[strain_key] = {
            "organism": organism,
            "strain": strain_name,
            "description": strain_def["description"],
        }


# ═══════════════════════════════════════════════════════════════════════════
#  ORGANISM REGISTRY & ALIASES
# ═══════════════════════════════════════════════════════════════════════════

# Base organism maps (organism-level, no strain specified)
ORGANISM_MAPS = {
    "CHO":            CHO_MAP,
    "CHO-S":          CHOS_MAP,
    "HEK293":         HEK293_MAP,
    "NS0":            NS0_MAP,
    "Sp2/0":          SP20_MAP,
    "BHK-21":         BHK21_MAP,
    "E. coli":        ECOLI_MAP,
    "B. subtilis":    BSUBTILIS_MAP,
    "P. pastoris":    PICHIA_MAP,
    "S. cerevisiae":  SCEREVISIAE_MAP,
}

# Add all strain maps to ORGANISM_MAPS so they're accessible via get_pathway_state
ORGANISM_MAPS.update(STRAIN_MAPS)

# Canonical parameter aliases
_MAMMALIAN_ALIASES = {"OD600": "VCD", "acetate": "lactate", "ethanol": "lactate", "acetoin": "lactate"}
_ECOLI_ALIASES     = {"VCD": "OD600", "lactate": "acetate", "ethanol": "acetate", "acetoin": "acetate"}
_BSUB_ALIASES      = {"VCD": "OD600", "lactate": "acetoin", "acetate": "acetoin", "ethanol": "acetoin"}
_PICHIA_ALIASES    = {"VCD": "OD600", "lactate": "ethanol", "acetate": "ethanol", "acetoin": "ethanol"}
_YEAST_ALIASES     = {"VCD": "OD600", "lactate": "ethanol", "acetate": "ethanol", "acetoin": "ethanol"}

PARAM_ALIASES = {
    # Base organisms
    "CHO":            _MAMMALIAN_ALIASES,
    "CHO-S":          _MAMMALIAN_ALIASES,
    "HEK293":         _MAMMALIAN_ALIASES,
    "NS0":            _MAMMALIAN_ALIASES,
    "Sp2/0":          _MAMMALIAN_ALIASES,
    "BHK-21":         _MAMMALIAN_ALIASES,
    "E. coli":        _ECOLI_ALIASES,
    "B. subtilis":    _BSUB_ALIASES,
    "P. pastoris":    _PICHIA_ALIASES,
    "S. cerevisiae":  _YEAST_ALIASES,
}

# Auto-populate aliases for all strain keys
for strain_key, info in STRAIN_INFO.items():
    org = info["organism"]
    if org in ("CHO", "HEK293", "NS0", "Sp2/0", "BHK-21"):
        PARAM_ALIASES[strain_key] = _MAMMALIAN_ALIASES
    elif org == "CHO" and info["strain"] == "CHO-S":
        PARAM_ALIASES[strain_key] = _MAMMALIAN_ALIASES
    elif org == "E. coli":
        PARAM_ALIASES[strain_key] = _ECOLI_ALIASES
    elif org == "B. subtilis":
        PARAM_ALIASES[strain_key] = _BSUB_ALIASES
    elif org == "P. pastoris":
        PARAM_ALIASES[strain_key] = _PICHIA_ALIASES
    elif org == "S. cerevisiae":
        PARAM_ALIASES[strain_key] = _YEAST_ALIASES


# ═══════════════════════════════════════════════════════════════════════════
#  CORE LOOKUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_pathway_state(parameter, value, organism="CHO"):
    """Classify a single parameter reading for the given organism or strain.

    organism can be:
      - "CHO"           (base organism map)
      - "CHO|CHO-DG44"  (strain-specific map)
    """
    if organism not in ORGANISM_MAPS:
        raise ValueError(f"Unknown organism/strain '{organism}'. Choose from: {list(ORGANISM_MAPS)}")

    gem_map = ORGANISM_MAPS[organism]

    # resolve alias (e.g. "OD600" -> "VCD" when organism is CHO)
    resolved = PARAM_ALIASES.get(organism, {}).get(parameter, parameter)

    if resolved not in gem_map:
        return None

    entry = gem_map[resolved]
    thresholds = entry["flux_interpretation"]

    low_t = thresholds["low"]["threshold"]
    norm_t = thresholds["normal"]["threshold"]

    if value <= low_t:
        state = thresholds["low"]
        zone = "low"
    elif value <= norm_t:
        state = thresholds["normal"]
        zone = "normal"
    else:
        state = thresholds["high"]
        zone = "high"

    # Compute zone confidence: how far from the nearest boundary (0-100%)
    # 100% = deep in zone center, 0% = right on a boundary
    if zone == "low":
        # Zone spans [0, low_t]. Nearest boundary is low_t.
        zone_width = low_t if low_t > 0 else 1.0
        dist_to_boundary = low_t - value
        confidence = min(100, int(dist_to_boundary / zone_width * 100)) if zone_width > 0 else 50
    elif zone == "normal":
        # Zone spans (low_t, norm_t]. Boundaries at low_t and norm_t.
        zone_width = norm_t - low_t
        dist_to_low = value - low_t
        dist_to_high = norm_t - value
        dist_to_nearest = min(dist_to_low, dist_to_high)
        confidence = min(100, int(dist_to_nearest / (zone_width / 2) * 100)) if zone_width > 0 else 50
    else:  # high
        # Zone spans (norm_t, inf). Nearest boundary is norm_t.
        dist_to_boundary = value - norm_t
        # Use norm_t as scale reference (no upper bound)
        scale = norm_t if norm_t > 0 else 1.0
        confidence = min(100, int(dist_to_boundary / scale * 100))

    confidence = max(0, min(100, confidence))

    if confidence >= 70:
        confidence_label = "HIGH"
    elif confidence >= 30:
        confidence_label = "MED"
    else:
        confidence_label = "LOW"

    return {
        "parameter":        resolved,
        "value":            value,
        "organism":         organism,
        "pathway":          entry["pathway"],
        "gem_reaction":     entry["gem_reaction"],
        "gem_model":        entry["gem_model"],
        "reaction_type":    entry.get("reaction_type", "metabolic"),
        "direction":        entry["direction"],
        "state":            state["state"],
        "unit":             state["unit"],
        "meaning":          state["meaning"],
        "downstream":       entry["downstream_effects"],
        "atlas_color":      entry["atlas_color"],
        "zone_confidence":  confidence,
        "confidence_label": confidence_label,
        "nearest_boundary": low_t if zone == "low" else (norm_t if zone == "high" else min(abs(value - low_t), abs(value - norm_t))),
    }


def get_all_pathway_states(readings: dict, organism: str = "CHO") -> dict:
    """Evaluate a full set of bioreactor readings for one organism/strain.

    Parameters
    ----------
    readings : dict   e.g. {"glucose": 1.2, "pH": 6.7, ...}
    organism : str    "CHO", "CHO|CHO-DG44", "E. coli|BL21(DE3)", etc.

    Returns
    -------
    dict  parameter -> pathway-state dict (None values skipped)
    """
    results = {}
    for param, val in readings.items():
        if val is None:
            continue
        state = get_pathway_state(param, val, organism)
        if state is not None:
            results[state["parameter"]] = state
    return results


def list_organisms():
    """Return base organism keys (without strains)."""
    return [k for k in ORGANISM_MAPS if "|" not in k]


def list_strains(organism=None):
    """Return available strains for an organism, or all strain keys.

    Returns list of "Organism|Strain" keys.
    """
    if organism is None:
        return list(STRAIN_MAPS.keys())
    return [k for k in STRAIN_MAPS if k.startswith(f"{organism}|")]


def get_strain_info(strain_key):
    """Return strain metadata dict or None."""
    return STRAIN_INFO.get(strain_key)


def list_parameters(organism="CHO"):
    """Return parameter names available for an organism or strain."""
    if organism not in ORGANISM_MAPS:
        raise ValueError(f"Unknown organism '{organism}'.")
    return list(ORGANISM_MAPS[organism].keys())


def validate_gem_map():
    """Audit every organism/strain map for reaction_type classification.

    Returns a dict of { organism_key: { reaction_type: count } }
    and prints a formatted summary.
    """
    report = {}
    type_order = ["metabolic", "custom_exchange", "control_placeholder", "biological_state"]

    for org_key in ORGANISM_MAPS:
        gem_map = ORGANISM_MAPS[org_key]
        counts = {t: 0 for t in type_order}
        missing_type = []
        cytbd_in_mammalian = []

        for param, entry in gem_map.items():
            rt = entry.get("reaction_type")
            if rt is None:
                missing_type.append(param)
                continue
            if rt in counts:
                counts[rt] += 1
            else:
                counts[rt] = counts.get(rt, 0) + 1

            # Check CYTBD correction in mammalian maps
            is_mammalian = not any(org_key.startswith(p) for p in
                                  ["E. coli", "B. subtilis", "P. pastoris", "S. cerevisiae"])
            if is_mammalian and entry.get("gem_reaction") == "CYTBD":
                cytbd_in_mammalian.append(param)

        report[org_key] = {
            "counts": counts,
            "total": sum(counts.values()),
            "missing_type": missing_type,
            "cytbd_in_mammalian": cytbd_in_mammalian,
        }

    # Print summary
    header = f"  {'Organism/Strain':<30} {'Total':>5} {'Metab':>6} {'CustEx':>7} {'CtrlPH':>7} {'BioSt':>6} {'Issues'}"
    print("\n" + "=" * 100)
    print("  GEM MAP VALIDATION REPORT")
    print("=" * 100)
    print(header)
    print(f"  {'-'*30} {'-'*5} {'-'*6} {'-'*7} {'-'*7} {'-'*6} {'-'*20}")

    issues_total = 0
    for org_key, data in report.items():
        c = data["counts"]
        issues = []
        if data["missing_type"]:
            issues.append(f"missing_type:{data['missing_type']}")
        if data["cytbd_in_mammalian"]:
            issues.append(f"CYTBD_unfixed:{data['cytbd_in_mammalian']}")
        issues_total += len(issues)
        issue_str = "; ".join(issues) if issues else "OK"
        print(
            f"  {org_key:<30} {data['total']:>5} "
            f"{c.get('metabolic',0):>6} {c.get('custom_exchange',0):>7} "
            f"{c.get('control_placeholder',0):>7} {c.get('biological_state',0):>6} "
            f"{issue_str}"
        )

    # Totals
    total_params = sum(d["total"] for d in report.values())
    total_met = sum(d["counts"].get("metabolic", 0) for d in report.values())
    total_ce = sum(d["counts"].get("custom_exchange", 0) for d in report.values())
    total_cp = sum(d["counts"].get("control_placeholder", 0) for d in report.values())
    total_bs = sum(d["counts"].get("biological_state", 0) for d in report.values())

    print(f"\n  {'TOTAL':<30} {total_params:>5} {total_met:>6} {total_ce:>7} {total_cp:>7} {total_bs:>6}")
    print(f"\n  Maps validated: {len(report)} | Issues found: {issues_total}")
    print(f"  VERDICT: {'PASS' if issues_total == 0 else 'FAIL'}")
    print("=" * 100 + "\n")

    return report
