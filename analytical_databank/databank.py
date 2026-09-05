"""
Analytical Data Bank — Complete instrument database for Biotech & Biopharma.
Each instrument entry contains:
  - principle: How the technique works
  - industry_models: Real instrument models used in industry (vendor, model, key specs)
  - methods_by_product: Methods/protocols mapped to product types (mAbs, vaccines, cell/gene therapy, etc.)
  - data_reporting: What a typical analytical report contains (parameters, acceptance criteria, outputs)
  - regulatory_references: Relevant ICH, USP, EP guidelines
"""

ANALYTICAL_DATABANK = {
    # =========================================================================
    # CHROMATOGRAPHY
    # =========================================================================
    "Chromatography": {
        "HPLC": {
            "full_name": "High-Performance Liquid Chromatography",
            "principle": (
                "A sample dissolved in a liquid mobile phase is pumped at high pressure through a column packed with "
                "a stationary phase. Compounds separate based on differential interactions (hydrophobicity, charge, size, "
                "or affinity) with the stationary phase. Detection is typically by UV/Vis absorbance, fluorescence, "
                "refractive index, or charged aerosol detection. Resolution depends on column chemistry, particle size, "
                "flow rate, gradient profile, and temperature."
            ),
            "industry_models": [
                {"vendor": "Waters", "model": "Alliance e2695", "type": "Quaternary HPLC", "use": "QC labs, routine testing"},
                {"vendor": "Waters", "model": "Arc HPLC", "type": "Quaternary HPLC", "use": "Method transfer from legacy systems"},
                {"vendor": "Agilent", "model": "1260 Infinity II", "type": "Quaternary/Binary HPLC", "use": "General purpose, IPC testing"},
                {"vendor": "Agilent", "model": "1290 Infinity II", "type": "UHPLC-capable", "use": "High-throughput QC, R&D"},
                {"vendor": "Shimadzu", "model": "Nexera XR", "type": "UHPLC", "use": "Fast method development"},
                {"vendor": "Shimadzu", "model": "Prominence-i LC-2030C", "type": "Integrated HPLC", "use": "Compact QC labs"},
                {"vendor": "Thermo Fisher", "model": "Vanquish Core", "type": "HPLC/UHPLC", "use": "Versatile R&D and QC"},
                {"vendor": "Thermo Fisher", "model": "UltiMate 3000", "type": "Nano/Standard HPLC", "use": "LC-MS workflows"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "SEC-HPLC", "purpose": "Size variant analysis (aggregates, fragments)", "column": "TSKgel G3000SWxl or Acquity BEH SEC 200A", "mobile_phase": "Phosphate buffer pH 6.8 with 200 mM NaCl", "detection": "UV 280 nm", "run_time": "30 min"},
                    {"method": "IEX-HPLC (CEX)", "purpose": "Charge variant analysis (acidic/basic species)", "column": "ProPac WCX-10 or MAbPac SCX-10", "mobile_phase": "MES buffer pH 5.6 with NaCl gradient", "detection": "UV 280 nm", "run_time": "60 min"},
                    {"method": "RP-HPLC", "purpose": "Reduced/non-reduced purity, clipping", "column": "PLRP-S or Zorbax 300SB-C8", "mobile_phase": "Water/ACN with 0.1% TFA", "detection": "UV 214 nm", "run_time": "45 min"},
                    {"method": "HIC-HPLC", "purpose": "Oxidation variant analysis, ADC DAR", "column": "TSKgel Butyl-NPR", "mobile_phase": "Ammonium sulfate gradient", "detection": "UV 280 nm", "run_time": "30 min"},
                    {"method": "Protein A HPLC", "purpose": "Titer determination in harvest", "column": "POROS A 20 or Applied Biosystems Protein A", "mobile_phase": "PBS / Glycine-HCl pH 2.5", "detection": "UV 280 nm", "run_time": "10 min"},
                ],
                "Vaccines": [
                    {"method": "SEC-HPLC", "purpose": "Antigen aggregation and integrity", "column": "TSKgel G4000SWxl", "mobile_phase": "PBS pH 7.4", "detection": "UV 280 nm / Fluorescence", "run_time": "30 min"},
                    {"method": "RP-HPLC", "purpose": "Adjuvant quantification (squalene, lipids)", "column": "C18 column", "mobile_phase": "MeOH/Water gradient", "detection": "CAD or ELSD", "run_time": "25 min"},
                ],
                "Recombinant Proteins": [
                    {"method": "SEC-HPLC", "purpose": "Monomer purity and aggregation", "column": "Superdex 200 Increase or BEH SEC", "mobile_phase": "Phosphate buffer", "detection": "UV 280 nm", "run_time": "30 min"},
                    {"method": "RP-HPLC", "purpose": "Identity and purity", "column": "C4 or C8 wide-pore", "mobile_phase": "Water/ACN + 0.1% TFA", "detection": "UV 214/280 nm", "run_time": "40 min"},
                    {"method": "IEX-HPLC", "purpose": "Charge heterogeneity", "column": "Mono Q or Mono S", "mobile_phase": "Tris or Bis-Tris buffer with NaCl gradient", "detection": "UV 280 nm", "run_time": "45 min"},
                ],
                "Small Molecule APIs": [
                    {"method": "RP-HPLC", "purpose": "Assay and related substances", "column": "C18 (ODS) 5 \u00b5m", "mobile_phase": "Buffer/Organic solvent per monograph", "detection": "UV at specific wavelength", "run_time": "20-60 min"},
                    {"method": "Chiral HPLC", "purpose": "Enantiomeric purity", "column": "Chiralpak AD-H or Chiralcel OD-H", "mobile_phase": "Hexane/IPA", "detection": "UV", "run_time": "30 min"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "IEX-HPLC", "purpose": "Capsid full/empty ratio (AAV)", "column": "CIMac AAV or POROS HQ", "mobile_phase": "Bis-Tris with NaCl gradient pH 9", "detection": "UV 260/280 nm", "run_time": "20 min"},
                    {"method": "SEC-HPLC", "purpose": "AAV aggregate analysis", "column": "SRT SEC-1000", "mobile_phase": "PBS + 200 mM NaCl", "detection": "UV 260/280 nm + MALS", "run_time": "25 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Sample identification and preparation details",
                    "Instrument and column details (ID, lot, usage count)",
                    "Method parameters (gradient, flow rate, temperature, injection volume)",
                    "System suitability results (plates, tailing, resolution, %RSD of replicates)",
                    "Chromatogram(s) with labeled peaks",
                    "Integration parameters and peak table",
                    "Quantitative results (area %, mg/mL, or titer)",
                    "Acceptance criteria and pass/fail determination",
                    "Analyst signature and review signature",
                ],
                "key_parameters": {
                    "System Suitability": ["Theoretical plates (N > 2000)", "Tailing factor (0.8-1.5)", "Resolution (Rs > 1.5)", "Injection repeatability (%RSD < 1.0%)", "Retention time %RSD < 1.0%"],
                    "Quantitative Output": ["Retention time (min)", "Peak area / peak height", "Relative area %", "Concentration (mg/mL or \u00b5g/mL)", "Signal-to-noise ratio (S/N > 10 for quantitation)"],
                },
                "acceptance_criteria_examples": {
                    "SEC-HPLC (mAb)": {"Monomer": "\u2265 95.0%", "HMW aggregates": "\u2264 5.0%", "LMW fragments": "\u2264 2.0%"},
                    "IEX-HPLC (mAb)": {"Main peak": "Report result", "Acidic species": "\u2264 specification", "Basic species": "\u2264 specification"},
                    "RP-HPLC assay": {"Assay": "95.0 - 105.0% of label claim", "Any single impurity": "\u2264 0.5%", "Total impurities": "\u2264 2.0%"},
                },
            },
            "regulatory_references": ["ICH Q2(R2) Validation of Analytical Procedures", "ICH Q6B Specifications for Biologicals", "USP <621> Chromatography", "Ph. Eur. 2.2.29 Liquid Chromatography"],
        },

        "UPLC / UHPLC": {
            "full_name": "Ultra-High Performance Liquid Chromatography",
            "principle": (
                "Operates on the same principles as HPLC but uses sub-2 \u00b5m particle columns and pressures up to 15,000-22,000 psi. "
                "This provides significantly higher resolution, sensitivity, and speed compared to conventional HPLC. "
                "Reduces solvent consumption and run times by 5-10x while maintaining or improving separation quality."
            ),
            "industry_models": [
                {"vendor": "Waters", "model": "ACQUITY UPLC H-Class PLUS", "type": "Quaternary UPLC", "use": "QC method transfer, GMP labs"},
                {"vendor": "Waters", "model": "ACQUITY UPLC I-Class PLUS", "type": "Binary UPLC", "use": "High-sensitivity R&D, peptide mapping"},
                {"vendor": "Agilent", "model": "1290 Infinity II LC", "type": "UHPLC", "use": "High-throughput QC, method development"},
                {"vendor": "Shimadzu", "model": "Nexera LC-2040C", "type": "i-Series UHPLC", "use": "Integrated compact systems"},
                {"vendor": "Thermo Fisher", "model": "Vanquish Horizon", "type": "UHPLC", "use": "LC-MS front-end, peptide mapping"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "Peptide Mapping (UPLC-UV/MS)", "purpose": "Primary sequence confirmation, PTM identification", "column": "Acquity BEH C18 1.7 \u00b5m, 300A", "mobile_phase": "Water/ACN + 0.1% FA", "detection": "UV 214 nm + MS", "run_time": "90-120 min"},
                    {"method": "Glycan Mapping (HILIC-UPLC)", "purpose": "N-linked glycan profiling", "column": "Acquity BEH Amide 1.7 \u00b5m", "mobile_phase": "Ammonium formate/ACN", "detection": "Fluorescence (2-AB/2-AA label)", "run_time": "50 min"},
                    {"method": "Disulfide Bond Mapping", "purpose": "Disulfide linkage confirmation", "column": "BEH C18 1.7 \u00b5m", "mobile_phase": "Water/ACN + 0.1% TFA", "detection": "UV + MS/MS", "run_time": "90 min"},
                ],
                "Oligonucleotides / mRNA": [
                    {"method": "IP-RP-UPLC", "purpose": "Purity and identity of oligos", "column": "Acquity BEH C18 1.7 \u00b5m", "mobile_phase": "TEAA buffer/ACN or HFIP/TEA/MeOH", "detection": "UV 260 nm", "run_time": "20 min"},
                    {"method": "AEX-UPLC", "purpose": "Charge-based impurity analysis", "column": "DNAPac PA200", "mobile_phase": "NaCl gradient in Tris buffer", "detection": "UV 260 nm", "run_time": "30 min"},
                ],
                "ADCs (Antibody-Drug Conjugates)": [
                    {"method": "HIC-UPLC", "purpose": "Drug-to-antibody ratio (DAR)", "column": "MAbPac HIC-Butyl", "mobile_phase": "Ammonium sulfate / phosphate gradient", "detection": "UV 280 nm + 248 nm", "run_time": "25 min"},
                    {"method": "RP-UPLC (reduced)", "purpose": "Positional DAR isomer analysis", "column": "BEH C4 1.7 \u00b5m, 300A", "mobile_phase": "Water/ACN + 0.1% TFA", "detection": "UV 280 nm", "run_time": "30 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "All HPLC report sections apply",
                    "Column pressure and backpressure monitoring",
                    "Sub-2 \u00b5m column lot and usage tracking",
                    "Comparison to HPLC reference method (if applicable)",
                ],
                "key_parameters": {
                    "System Suitability": ["Same as HPLC but typically tighter criteria", "Peak capacity > 200 for peptide mapping", "Column pressure < max rated pressure"],
                    "Quantitative Output": ["Same as HPLC", "Peak identification by retention time matching to reference standard", "MS confirmation of peak identity (when coupled)"],
                },
            },
            "regulatory_references": ["ICH Q2(R2)", "USP <621>", "ICH Q6B", "FDA Guidance: Analytical Procedures and Methods Validation (Biologics)"],
        },

        "GC": {
            "full_name": "Gas Chromatography",
            "principle": (
                "Volatile analytes are vaporized in a heated injection port and carried by an inert gas (He, N2, H2) "
                "through a capillary column coated with a liquid stationary phase. Separation occurs based on boiling "
                "point and polarity differences. Detection by FID (universal for organics), TCD (universal), "
                "ECD (halogenated compounds), or coupled with MS."
            ),
            "industry_models": [
                {"vendor": "Agilent", "model": "8890 GC", "type": "Capillary GC", "use": "Residual solvent, headspace analysis"},
                {"vendor": "Agilent", "model": "8860 GC", "type": "Standard GC", "use": "Routine QC testing"},
                {"vendor": "Shimadzu", "model": "Nexis GC-2030", "type": "Capillary GC", "use": "General purpose, E&L studies"},
                {"vendor": "Thermo Fisher", "model": "TRACE 1310", "type": "GC", "use": "GC-MS workflows"},
                {"vendor": "PerkinElmer", "model": "Clarus 690 GC", "type": "GC", "use": "Petrochemical / biotech QC"},
            ],
            "methods_by_product": {
                "Small Molecule APIs": [
                    {"method": "Headspace GC-FID", "purpose": "Residual solvent analysis (ICH Q3C)", "column": "DB-624 30m x 0.53mm", "mobile_phase": "Helium carrier 35 cm/s", "detection": "FID", "run_time": "30-45 min"},
                    {"method": "GC-FID Direct Injection", "purpose": "Organic volatile impurities", "column": "DB-WAX or HP-5", "mobile_phase": "Helium carrier", "detection": "FID", "run_time": "25 min"},
                ],
                "Biologics (General)": [
                    {"method": "Headspace GC-FID", "purpose": "Residual solvents in lyophilized products", "column": "DB-624", "mobile_phase": "Helium", "detection": "FID", "run_time": "30 min"},
                ],
                "Fermentation Products": [
                    {"method": "GC-FID", "purpose": "Ethanol, acetic acid, glycerol quantification", "column": "HP-FFAP or Carbowax", "mobile_phase": "Nitrogen or Helium", "detection": "FID", "run_time": "20 min"},
                    {"method": "GC-TCD", "purpose": "Off-gas analysis (CO2, O2, N2)", "column": "Molecular sieve / Porapak Q", "mobile_phase": "Helium", "detection": "TCD", "run_time": "15 min"},
                    {"method": "GC-FID (FAME)", "purpose": "Fatty acid methyl ester profiling", "column": "SP-2560 or BPX70", "mobile_phase": "Helium", "detection": "FID", "run_time": "40 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Sample preparation (dilution, headspace equilibration conditions)",
                    "Column and carrier gas details",
                    "Oven temperature program",
                    "Detector type and parameters",
                    "System suitability (resolution, S/N, repeatability)",
                    "Chromatogram with identified peaks",
                    "Quantification against standards (external or internal standard method)",
                    "Results vs. ICH Q3C limits (for residual solvents)",
                ],
                "key_parameters": {
                    "System Suitability": ["Resolution between critical pairs > 1.5", "S/N of LOQ standard > 10", "Injection repeatability %RSD < 5%"],
                    "Quantitative Output": ["Retention time", "Peak area", "Concentration (ppm or mg/day)", "LOD and LOQ values"],
                },
            },
            "regulatory_references": ["ICH Q3C(R8) Residual Solvents", "USP <467> Residual Solvents", "USP <621> Chromatography", "Ph. Eur. 2.4.24 Residual Solvents"],
        },

        "FPLC": {
            "full_name": "Fast Protein Liquid Chromatography",
            "principle": (
                "Low-to-medium pressure liquid chromatography specifically designed for protein purification. "
                "Uses biocompatible flow paths and large-bead resins optimized for biomolecules. Separations based on "
                "size exclusion, ion exchange, hydrophobic interaction, or affinity. Preparative scale from mg to kg."
            ),
            "industry_models": [
                {"vendor": "Cytiva", "model": "AKTA pure 25", "type": "Lab-scale FPLC", "use": "R&D protein purification, resin screening"},
                {"vendor": "Cytiva", "model": "AKTA avant 150", "type": "Method development FPLC", "use": "Design of experiments, scale-down models"},
                {"vendor": "Cytiva", "model": "AKTA pilot 600", "type": "Pilot scale", "use": "Process development, scale-up"},
                {"vendor": "Cytiva", "model": "AKTA ready", "type": "Single-use FPLC", "use": "GMP manufacturing"},
                {"vendor": "Bio-Rad", "model": "NGC Quest 10 Plus", "type": "FPLC", "use": "Academic and R&D labs"},
                {"vendor": "Knauer", "model": "AZURA Bio", "type": "Bio-HPLC", "use": "Flexible bio-purification"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "Protein A Affinity Chromatography", "purpose": "Capture step (primary purification)", "column": "MabSelect SuRe / MabSelect PrismA", "mobile_phase": "PBS load / Citrate pH 3.5 elution", "detection": "UV 280 nm", "run_time": "60-120 min"},
                    {"method": "CEX Chromatography", "purpose": "Intermediate polishing", "column": "Capto SP ImpRes", "mobile_phase": "Acetate buffer / NaCl gradient", "detection": "UV 280 nm", "run_time": "90 min"},
                    {"method": "AEX Chromatography (flow-through)", "purpose": "Polishing (HCP, DNA removal)", "column": "Capto Q ImpRes", "mobile_phase": "Tris buffer pH 8.0", "detection": "UV 280 nm", "run_time": "45 min"},
                    {"method": "SEC (preparative)", "purpose": "Final polishing, buffer exchange", "column": "Superdex 200 pg", "mobile_phase": "Formulation buffer", "detection": "UV 280 nm", "run_time": "120 min"},
                ],
                "Recombinant Proteins": [
                    {"method": "IMAC (Ni-NTA)", "purpose": "His-tag capture", "column": "HisTrap Excel or Ni Sepharose 6 FF", "mobile_phase": "Imidazole gradient in phosphate buffer", "detection": "UV 280 nm", "run_time": "60 min"},
                    {"method": "IEX Chromatography", "purpose": "Polishing after tag removal", "column": "HiTrap Q/SP HP", "mobile_phase": "Salt gradient", "detection": "UV 280 nm", "run_time": "60 min"},
                ],
                "Viral Vectors (AAV)": [
                    {"method": "Affinity Chromatography", "purpose": "AAV capture", "column": "POROS CaptureSelect AAVX / AVB Sepharose", "mobile_phase": "PBS / Glycine-HCl pH 2.5", "detection": "UV 260/280 nm", "run_time": "60 min"},
                    {"method": "AEX Chromatography", "purpose": "Full/empty capsid separation", "column": "CIMmultus QA monolith", "mobile_phase": "Bis-Tris pH 9 / TMAC gradient", "detection": "UV 260/280 nm", "run_time": "30 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Run parameters (flow rate, gradient, column volume)",
                    "Chromatogram overlay (UV 280, conductivity, pH)",
                    "Fraction collection log",
                    "Step yield and recovery calculations",
                    "Pool volume and concentration",
                    "Column HETP and asymmetry (qualification)",
                    "Resin lifetime and cleaning validation data",
                ],
                "key_parameters": {
                    "Process Performance": ["Step yield (%)", "HCP clearance (log reduction)", "DNA clearance (log reduction)", "Aggregate removal (%)", "Endotoxin clearance"],
                    "Column Qualification": ["HETP (< 2x particle diameter)", "Asymmetry factor (0.8 - 1.4)", "Pressure over column life", "Capacity (DBC at 10% breakthrough)"],
                },
            },
            "regulatory_references": ["ICH Q5A Viral Safety", "ICH Q5B Expression Constructs", "ICH Q11 Development and Manufacture of Drug Substances"],
        },

        "HILIC": {
            "full_name": "Hydrophilic Interaction Liquid Chromatography",
            "principle": (
                "A variant of normal-phase chromatography that uses a polar stationary phase (amide, diol, or zwitterionic) "
                "with a predominantly organic mobile phase (typically 60-95% acetonitrile). Polar analytes partition into "
                "a water-enriched layer on the stationary phase surface. Elution is achieved by increasing the aqueous content "
                "of the mobile phase. Particularly suited for separating highly polar compounds that are poorly retained on "
                "reversed-phase columns, including released N-glycans, glycopeptides, polar metabolites, and oligosaccharides."
            ),
            "industry_models": [
                {"vendor": "Waters", "model": "ACQUITY UPLC Glycan BEH Amide Column", "type": "HILIC UPLC column (1.7 µm)", "use": "N-glycan profiling of mAbs and glycoproteins"},
                {"vendor": "Waters", "model": "ACQUITY UPLC H-Class PLUS (with HILIC column)", "type": "Quaternary UPLC", "use": "Routine glycan mapping in QC"},
                {"vendor": "Agilent", "model": "1290 Infinity II with AdvanceBio Glycan Mapping column", "type": "UHPLC", "use": "High-resolution glycan analysis"},
                {"vendor": "Thermo Fisher", "model": "Vanquish Horizon with GlycanPac AXH-1", "type": "UHPLC", "use": "Charged glycan separation"},
                {"vendor": "Shimadzu", "model": "Nexera with HILIC column", "type": "UHPLC", "use": "Glycan and polar metabolite analysis"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "HILIC-UPLC N-glycan profiling", "purpose": "Released glycan identification and quantification (G0F, G1F, G2F, Man5, sialylated species)", "column": "BEH Amide 1.7 µm, 2.1 x 150 mm", "mobile_phase": "50 mM ammonium formate pH 4.4 / ACN gradient", "detection": "Fluorescence (2-AB or RFMS label, Ex 265/Em 425 nm)", "run_time": "30-55 min"},
                    {"method": "HILIC glycopeptide mapping", "purpose": "Site-specific glycosylation analysis", "column": "ZIC-HILIC or BEH Amide", "mobile_phase": "TFA/ACN gradient", "detection": "FLR + MS", "run_time": "45-60 min"},
                ],
                "Fusion Proteins / Fc-Fusion": [
                    {"method": "HILIC-UPLC released glycan analysis", "purpose": "Glycan profile comparison, glycoform consistency", "column": "BEH Amide 1.7 µm", "mobile_phase": "Ammonium formate / ACN gradient", "detection": "Fluorescence (2-AB or RFMS label)", "run_time": "35-55 min"},
                ],
                "Biosimilars": [
                    {"method": "HILIC glycan fingerprinting", "purpose": "Comparative glycan profiling vs. reference product", "column": "BEH Amide 1.7 µm", "mobile_phase": "Ammonium formate / ACN gradient", "detection": "Fluorescence + MS for peak assignment", "run_time": "40-55 min"},
                ],
                "Vaccines (Glycoconjugates)": [
                    {"method": "HILIC saccharide profiling", "purpose": "Polysaccharide identity and integrity after conjugation", "column": "BEH Amide or GlycanPac AXH-1", "mobile_phase": "Ammonium formate / ACN gradient", "detection": "FLR or CAD", "run_time": "30-45 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Chromatogram with labeled glycan peaks (GU index or retention time)",
                    "Glycan identification table (peak assignment by GU value or MS confirmation)",
                    "Relative area % for each glycan species",
                    "System suitability (dextran ladder resolution, retention time %RSD)",
                    "Overlay with reference standard or reference product",
                    "Total afucosylation %, galactosylation %, sialylation % summary",
                ],
                "key_parameters": {
                    "System Suitability": ["Dextran ladder resolution (adjacent peaks baseline resolved)", "Retention time %RSD < 0.5%", "Peak area %RSD < 5%"],
                    "Quantitative Output": ["Relative area % per glycan species", "GU (glucose unit) index", "Total afucosylation %", "% High-mannose (Man5, Man6, etc.)", "% Galactosylation (G0F, G1F, G2F ratios)", "% Sialylation"],
                },
                "acceptance_criteria_examples": {
                    "mAb N-glycan profile": {"G0F": "Report result (typically 40-70%)", "Afucosylation": "≤ specification (impacts ADCC)", "High mannose": "≤ specification (impacts PK)", "Sialylation": "Report result"},
                },
            },
            "regulatory_references": ["ICH Q6B Specifications for Biologicals", "ICH Q5E Comparability of Biotechnological Products", "USP <1084> Glycoprotein and Glycan Analysis", "EMA Guideline on Similar Biological Medicinal Products (glycosylation comparability)"],
        },
    },

    # =========================================================================
    # MASS SPECTROMETRY
    # =========================================================================
    "Mass Spectrometry": {
        "LC-MS / LC-MS/MS": {
            "full_name": "Liquid Chromatography\u2013Mass Spectrometry",
            "principle": (
                "Combines LC separation with mass-to-charge (m/z) detection. The LC eluent is ionized (ESI or APCI), "
                "and ions are separated in a mass analyzer (quadrupole, TOF, Orbitrap, or ion trap). MS/MS (tandem MS) "
                "provides structural information by fragmenting precursor ions and analyzing product ions. Enables "
                "identification, quantification, and structural characterization at femtomole sensitivity."
            ),
            "industry_models": [
                {"vendor": "Thermo Fisher", "model": "Q Exactive Plus", "type": "Q-Orbitrap", "use": "Peptide mapping, HCP ID, metabolomics"},
                {"vendor": "Thermo Fisher", "model": "Orbitrap Exploris 480", "type": "Q-Orbitrap", "use": "High-res intact mass, top-down proteomics"},
                {"vendor": "Thermo Fisher", "model": "TSQ Fortis Plus", "type": "Triple Quad", "use": "Targeted quantitation, MRM assays"},
                {"vendor": "Waters", "model": "Xevo G2-XS QTof", "type": "Q-TOF", "use": "Intact mass, peptide mapping"},
                {"vendor": "Waters", "model": "Xevo TQ-XS", "type": "Triple Quad", "use": "Small molecule quantitation, E&L"},
                {"vendor": "Sciex", "model": "TripleTOF 6600+", "type": "Q-TOF", "use": "SWATH proteomics, DIA"},
                {"vendor": "Sciex", "model": "7500 QTRAP", "type": "Triple Quad / Ion Trap", "use": "Bioanalytical, PK studies"},
                {"vendor": "Bruker", "model": "timsTOF Pro 2", "type": "TIMS-Q-TOF", "use": "4D proteomics, trapped ion mobility"},
                {"vendor": "Agilent", "model": "6546 LC/Q-TOF", "type": "Q-TOF", "use": "Metabolomics, impurity ID"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "Intact Mass Analysis", "purpose": "MW confirmation, glycoform distribution", "column": "BEH C4 1.7 \u00b5m, 300A", "mobile_phase": "Water/ACN + 0.1% FA", "detection": "ESI-QTOF or Orbitrap", "run_time": "10 min"},
                    {"method": "Subunit Analysis (IdeS digest)", "purpose": "Fc/2, LC, Fd mass confirmation", "column": "BEH C4 1.7 \u00b5m", "mobile_phase": "Water/ACN + 0.1% FA", "detection": "ESI-QTOF", "run_time": "15 min"},
                    {"method": "Peptide Mapping (LC-MS/MS)", "purpose": "Sequence coverage, PTM identification", "column": "BEH C18 1.7 \u00b5m, 300A", "mobile_phase": "Water/ACN + 0.1% FA", "detection": "Orbitrap or QTOF (DDA mode)", "run_time": "120 min"},
                    {"method": "Multi-Attribute Method (MAM)", "purpose": "Simultaneous monitoring of multiple CQAs", "column": "CSH C18 1.7 \u00b5m", "mobile_phase": "Water/ACN + 0.1% FA", "detection": "Orbitrap (PRM mode)", "run_time": "60 min"},
                    {"method": "HCP-ID (LC-MS/MS)", "purpose": "Host cell protein identification", "column": "nanoLC C18", "mobile_phase": "Water/ACN + 0.1% FA", "detection": "Orbitrap (DDA)", "run_time": "120 min"},
                ],
                "Oligonucleotides / mRNA": [
                    {"method": "Intact mass (IP-RP-LC-MS)", "purpose": "Molecular weight confirmation, capping efficiency", "column": "Acquity BEH C18", "mobile_phase": "HFIP/TEA/MeOH", "detection": "Q-TOF (negative mode)", "run_time": "15 min"},
                    {"method": "Oligonucleotide impurity profiling", "purpose": "Shortmers, longmers, modifications", "column": "Acquity BEH C18", "mobile_phase": "HFIP/TEA/MeOH", "detection": "Q-TOF", "run_time": "30 min"},
                ],
                "Cell & Gene Therapy (AAV)": [
                    {"method": "Capsid protein LC-MS", "purpose": "VP1/VP2/VP3 identity and ratio", "column": "C4 or C8 column", "mobile_phase": "Water/ACN + 0.1% FA", "detection": "Q-TOF or Orbitrap", "run_time": "20 min"},
                    {"method": "Residual HCP-ID", "purpose": "Identify process-related impurities", "column": "nanoLC C18", "mobile_phase": "Standard proteomics gradient", "detection": "Orbitrap DDA", "run_time": "120 min"},
                ],
                "Small Molecule APIs": [
                    {"method": "LC-MS/MS (MRM)", "purpose": "Quantitative assay, impurity ID", "column": "C18 column", "mobile_phase": "Compound-specific", "detection": "Triple quad MRM", "run_time": "5-15 min"},
                    {"method": "Metabolite ID", "purpose": "In vitro / in vivo metabolite identification", "column": "C18 column", "mobile_phase": "Water/ACN + ammonium formate", "detection": "Q-TOF or Orbitrap", "run_time": "30 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Instrument tune and calibration verification",
                    "Mass accuracy (ppm error for intact mass)",
                    "Deconvoluted mass spectrum (intact mass)",
                    "Sequence coverage map (peptide mapping)",
                    "PTM summary table with site localization confidence",
                    "Extracted ion chromatograms (XICs)",
                    "Protein identification list with scores (HCP-ID)",
                    "Raw data file references",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Mass accuracy (< 5 ppm external, < 2 ppm internal)", "Sequence coverage (> 95% for mAb mapping)", "Resolution (> 30,000 for intact, > 60,000 for peptide mapping)"],
                    "Quantitative Output": ["Relative abundance (%)", "Absolute quantification via MRM (ng/mL)", "XIC peak area ratios"],
                },
            },
            "regulatory_references": ["ICH Q6B Specifications: Biologicals", "USP <1084> Pharm Applications of MS", "FDA MAM guidance (draft)", "EMA Guideline on development of mAb biosimilars"],
        },

        "GC-MS": {
            "full_name": "Gas Chromatography\u2013Mass Spectrometry",
            "principle": (
                "Combines GC separation of volatile compounds with mass spectrometric detection. After GC separation, "
                "compounds are ionized by electron ionization (EI) at 70 eV producing characteristic fragmentation patterns. "
                "Identification by matching to NIST spectral libraries. Chemical ionization (CI) provides molecular ion information."
            ),
            "industry_models": [
                {"vendor": "Agilent", "model": "7010D Triple Quad GC-MS", "type": "GC-QQQ", "use": "Targeted E&L, pesticide residues"},
                {"vendor": "Agilent", "model": "5977C GC-MSD", "type": "Single Quad GC-MS", "use": "Residual solvents, routine screening"},
                {"vendor": "Thermo Fisher", "model": "ISQ 7610 GC-MS", "type": "Single Quad", "use": "Routine QC"},
                {"vendor": "Shimadzu", "model": "GCMS-QP2020 NX", "type": "Single Quad", "use": "General purpose"},
                {"vendor": "Waters", "model": "Xevo TQ-GC", "type": "GC-QQQ", "use": "Ultra-trace E&L studies"},
            ],
            "methods_by_product": {
                "Drug Product & Packaging": [
                    {"method": "Headspace GC-MS", "purpose": "Extractables & Leachables screening", "column": "DB-5ms 30m x 0.25mm", "mobile_phase": "Helium", "detection": "EI full scan + SIM", "run_time": "45 min"},
                    {"method": "Direct injection GC-MS", "purpose": "Semi-volatile E&L compounds", "column": "DB-5ms", "mobile_phase": "Helium", "detection": "EI full scan", "run_time": "50 min"},
                ],
                "Small Molecule APIs": [
                    {"method": "Headspace GC-MS", "purpose": "Residual solvent confirmation (ICH Q3C)", "column": "DB-624 30m", "mobile_phase": "Helium", "detection": "EI scan/SIM", "run_time": "35 min"},
                    {"method": "GC-MS/MS (MRM)", "purpose": "Genotoxic impurity testing (nitrosamines)", "column": "DB-WAX or DB-1701", "mobile_phase": "Helium", "detection": "CI/EI MRM", "run_time": "25 min"},
                ],
                "Fermentation Products": [
                    {"method": "GC-MS (derivatized)", "purpose": "Metabolite profiling (TMS derivatives)", "column": "DB-5ms", "mobile_phase": "Helium", "detection": "EI full scan", "run_time": "40 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Sample preparation and extraction method",
                    "GC conditions (oven program, carrier gas, split ratio)",
                    "MS tune verification (PFTBA or BFB for EPA methods)",
                    "Library search results with match quality scores",
                    "Total ion chromatogram (TIC) and extracted ion chromatograms",
                    "Quantification report (against calibration curve)",
                    "Identification confidence (library match > 80%)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["NIST library match quality (> 80%)", "Retention index (RI) match", "Ion ratio confirmation for MRM"],
                    "Quantitative Output": ["Concentration (ppm, ppb, \u00b5g/L)", "AET (Analytical Evaluation Threshold) comparison", "LOD/LOQ in matrix"],
                },
            },
            "regulatory_references": ["ICH Q3C(R8) Residual Solvents", "ICH M7 Mutagenic Impurities", "USP <1663> E&L", "PQRI recommendations for E&L"],
        },

        "MALDI-TOF MS": {
            "full_name": "Matrix-Assisted Laser Desorption/Ionization\u2013Time of Flight Mass Spectrometry",
            "principle": (
                "Sample is co-crystallized with a UV-absorbing matrix on a metal plate. A pulsed laser irradiates the "
                "matrix, causing desorption and ionization of analyte molecules. Ions are accelerated in an electric field "
                "and separated by their time of flight to the detector, which is proportional to the square root of m/z. "
                "Primarily produces singly charged ions, making it ideal for large biomolecules."
            ),
            "industry_models": [
                {"vendor": "Bruker", "model": "MALDI Biotyper sirius", "type": "MALDI-TOF", "use": "Microbial identification (gold standard)"},
                {"vendor": "Bruker", "model": "rapifleX MALDI-TOF/TOF", "type": "MALDI-TOF/TOF", "use": "Imaging, top-down proteomics"},
                {"vendor": "Bruker", "model": "ultrafleXtreme", "type": "MALDI-TOF/TOF", "use": "Protein characterization"},
                {"vendor": "Shimadzu", "model": "MALDI-8030", "type": "MALDI-TOF", "use": "Polymer and clinical analysis"},
                {"vendor": "bioMerieux", "model": "VITEK MS", "type": "MALDI-TOF", "use": "Clinical microbial ID"},
            ],
            "methods_by_product": {
                "Microbial QC": [
                    {"method": "MALDI Biotyper", "purpose": "Species-level microbial identification", "column": "N/A (direct target plate)", "mobile_phase": "Matrix: HCCA in ACN/TFA", "detection": "Linear TOF 2-20 kDa", "run_time": "< 1 min/spot"},
                    {"method": "MALDI subtyping", "purpose": "Strain-level differentiation", "column": "N/A", "mobile_phase": "HCCA", "detection": "Reflector TOF", "run_time": "< 1 min/spot"},
                ],
                "Biologics (General)": [
                    {"method": "Intact protein MALDI", "purpose": "Molecular weight confirmation", "column": "N/A", "mobile_phase": "Sinapinic acid matrix", "detection": "Linear TOF 10-200 kDa", "run_time": "< 1 min/spot"},
                    {"method": "Peptide mass fingerprinting", "purpose": "Protein identification by tryptic digest masses", "column": "N/A", "mobile_phase": "HCCA matrix", "detection": "Reflector TOF", "run_time": "< 1 min/spot + digestion"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Target plate layout and calibrant positions",
                    "Calibration verification (mass accuracy)",
                    "Mass spectrum with annotated peaks",
                    "Biotyper score (for microbial ID): > 2.0 = reliable ID",
                    "Database version used for identification",
                    "Molecular weight results with mass accuracy",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Mass accuracy (0.01-0.1% for proteins)", "Biotyper score (> 2.0 for species, > 1.7 for genus)", "S/N ratio"],
                    "Quantitative Output": ["Qualitative identification only (for Biotyper)", "Approximate MW for intact proteins", "Relative peak intensities"],
                },
            },
            "regulatory_references": ["FDA cleared for IVD (MALDI Biotyper)", "USP <1113> Microbial Characterization", "Ph. Eur. 2.7.1 (microbial methods)"],
        },

        "ICP-MS": {
            "full_name": "Inductively Coupled Plasma\u2013Mass Spectrometry",
            "principle": (
                "Sample is nebulized into an argon plasma at ~6000-10000 K, atomizing and ionizing all elements. "
                "Ions pass through an interface into a mass analyzer (quadrupole, TOF, or sector field) for element-specific, "
                "isotope-specific detection. Offers sub-ppt detection limits for most elements. Collision/reaction cells "
                "eliminate polyatomic interferences."
            ),
            "industry_models": [
                {"vendor": "Agilent", "model": "7850 ICP-MS", "type": "Single Quad with CRC", "use": "Routine elemental impurity testing"},
                {"vendor": "Agilent", "model": "7900 ICP-MS", "type": "Single Quad with ORS", "use": "High-matrix samples, trace metals"},
                {"vendor": "Thermo Fisher", "model": "iCAP RQ", "type": "Single Quad", "use": "Pharmaceutical QC"},
                {"vendor": "Thermo Fisher", "model": "iCAP TQ", "type": "Triple Quad ICP-MS", "use": "Ultra-trace, interference-free analysis"},
                {"vendor": "PerkinElmer", "model": "NexION 5000", "type": "Multi-quad ICP-MS", "use": "Complex matrices, semiconductor-grade purity"},
            ],
            "methods_by_product": {
                "Drug Products (All Types)": [
                    {"method": "ICH Q3D Elemental Impurities", "purpose": "24 elemental impurity screen (Cd, Pb, As, Hg, etc.)", "column": "N/A (direct nebulization)", "mobile_phase": "Dilute HNO3/HCl matrix", "detection": "ICP-MS with He collision mode", "run_time": "5-10 min/sample"},
                    {"method": "USP <232>/<233>", "purpose": "Elemental impurity limits for pharmaceuticals", "column": "N/A", "mobile_phase": "Closed-vessel microwave digestion in HNO3", "detection": "ICP-MS or ICP-OES", "run_time": "5-10 min/sample"},
                ],
                "Raw Materials & Excipients": [
                    {"method": "Multi-element screening", "purpose": "Certificate of analysis testing", "column": "N/A", "mobile_phase": "Matrix-matched standards in acid", "detection": "ICP-MS semi-quantitative scan", "run_time": "5 min/sample"},
                ],
                "Catalysts / ADCs": [
                    {"method": "Trace metal analysis", "purpose": "Pd, Pt, Ru residual catalyst metals", "column": "N/A", "mobile_phase": "Acid digestion", "detection": "ICP-MS with internal standard", "run_time": "5 min/sample"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Instrument tune verification (Ce/CeO < 2%, doubly charged < 3%)",
                    "Calibration curve with R\u00b2 > 0.999",
                    "Internal standard recovery (80-120%)",
                    "Spike recovery results (80-120%)",
                    "Element-by-element results table with PDE/concentration limits",
                    "Comparison to ICH Q3D Class 1/2A/2B/3 limits",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Oxide ratio (CeO/Ce < 2%)", "Doubly charged (Ba++/Ba < 3%)", "Background at mass 220 < 1 cps"],
                    "Quantitative Output": ["Concentration (\u00b5g/L or \u00b5g/g)", "PDE (\u00b5g/day)", "J-value (\u00b5g/g based on max daily dose)", "LOD/LOQ per element"],
                },
            },
            "regulatory_references": ["ICH Q3D(R2) Elemental Impurities", "USP <232> Elemental Impurities\u2014Limits", "USP <233> Elemental Impurities\u2014Procedures", "Ph. Eur. 2.4.20 Determination of Elemental Impurities"],
        },
    },

    # =========================================================================
    # SPECTROSCOPY
    # =========================================================================
    "Spectroscopy": {
        "UV-Vis": {
            "full_name": "UV-Visible Spectrophotometry",
            "principle": (
                "Measures the absorption of ultraviolet (190-400 nm) and visible (400-800 nm) light by a sample. "
                "Absorption follows Beer-Lambert Law: A = \u03b5lc, where \u03b5 is molar absorptivity, l is path length, "
                "and c is concentration. Provides quantitative concentration data and qualitative identity information. "
                "Tryptophan and tyrosine residues absorb at 280 nm; nucleic acids at 260 nm."
            ),
            "industry_models": [
                {"vendor": "Agilent", "model": "Cary 60 UV-Vis", "type": "Single-beam", "use": "Routine QC, enzyme assays"},
                {"vendor": "Agilent", "model": "Cary 3500 UV-Vis", "type": "Double-beam", "use": "High-accuracy pharma QC"},
                {"vendor": "Thermo Fisher", "model": "NanoDrop One", "type": "Microvolume", "use": "DNA/RNA/Protein concentration (1-2 \u00b5L)"},
                {"vendor": "Thermo Fisher", "model": "Evolution 350", "type": "Double-beam", "use": "Pharmacopeial testing"},
                {"vendor": "Shimadzu", "model": "UV-1900i", "type": "Double-beam", "use": "General purpose"},
                {"vendor": "PerkinElmer", "model": "LAMBDA 365+", "type": "Double-beam", "use": "Kinetic studies, dissolution"},
                {"vendor": "Molecular Devices", "model": "SpectraMax iD5", "type": "Microplate reader", "use": "High-throughput assays (ELISA, cell-based)"},
            ],
            "methods_by_product": {
                "Biologics (General)": [
                    {"method": "A280 Concentration", "purpose": "Protein concentration by UV absorption", "column": "N/A (cuvette or NanoDrop)", "mobile_phase": "Matched buffer blank", "detection": "UV 280 nm", "run_time": "< 1 min"},
                    {"method": "A260/A280 Ratio", "purpose": "Nucleic acid contamination check", "column": "N/A", "mobile_phase": "Buffer blank", "detection": "UV 260 + 280 nm", "run_time": "< 1 min"},
                    {"method": "Protein A280 with correction (Scopes method)", "purpose": "Protein concentration with light scattering correction", "column": "N/A", "mobile_phase": "Buffer", "detection": "UV 280, 320, 340 nm", "run_time": "< 1 min"},
                ],
                "Nucleic Acids (DNA/RNA/mRNA)": [
                    {"method": "A260 Concentration", "purpose": "Nucleic acid quantification", "column": "N/A (NanoDrop/cuvette)", "mobile_phase": "TE buffer or water", "detection": "UV 260 nm", "run_time": "< 1 min"},
                    {"method": "A260/A280 and A260/A230 Ratios", "purpose": "Purity assessment (protein and organic contamination)", "column": "N/A", "mobile_phase": "Buffer", "detection": "UV multi-wavelength", "run_time": "< 1 min"},
                ],
                "Cell Culture / Fermentation": [
                    {"method": "OD600 Measurement", "purpose": "Cell density / biomass estimation", "column": "N/A (cuvette)", "mobile_phase": "Media blank", "detection": "Vis 600 nm", "run_time": "< 1 min"},
                    {"method": "Bradford / BCA / Lowry Assay", "purpose": "Total protein quantification (colorimetric)", "column": "N/A (cuvette/plate)", "mobile_phase": "Assay reagent", "detection": "Vis 595/562/750 nm", "run_time": "5-30 min"},
                ],
                "Small Molecule APIs": [
                    {"method": "UV Assay", "purpose": "Content/assay per pharmacopeial monograph", "column": "N/A (cuvette)", "mobile_phase": "Specified solvent", "detection": "UV at \u03bbmax", "run_time": "< 5 min"},
                    {"method": "Dissolution Testing (UV detection)", "purpose": "Drug release from dosage forms", "column": "N/A (flow cell / cuvette)", "mobile_phase": "Dissolution medium", "detection": "UV at \u03bbmax", "run_time": "Continuous or timed sampling"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Instrument qualification status (PQ with NIST standards)",
                    "Baseline/blank verification",
                    "Wavelength accuracy and photometric accuracy checks",
                    "Sample absorbance spectrum or single-point reading",
                    "Dilution factor and extinction coefficient used",
                    "Calculated concentration result",
                    "Path length used (1 cm, 0.1 cm, or microvolume)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Wavelength accuracy (\u00b1 1 nm)", "Photometric accuracy (\u00b1 0.005 A)", "Stray light (< 0.01% at 198 nm)", "Noise level"],
                    "Quantitative Output": ["Absorbance (AU)", "Concentration (mg/mL, \u00b5g/mL)", "Purity ratios (A260/A280)", "OD600 value"],
                },
            },
            "regulatory_references": ["USP <857> UV-Visible Spectrophotometry", "Ph. Eur. 2.2.25 Absorption Spectrophotometry UV", "USP <1857> Performance Qualification"],
        },

        "FTIR": {
            "full_name": "Fourier-Transform Infrared Spectroscopy",
            "principle": (
                "Infrared radiation is passed through or reflected from a sample. Molecular bonds absorb IR at specific "
                "frequencies corresponding to their vibrational modes (stretching, bending). An interferometer measures "
                "all frequencies simultaneously; Fourier transform converts the interferogram into a spectrum. "
                "Each compound has a unique 'fingerprint' region (1500-500 cm\u207b\u00b9). ATR mode allows direct measurement "
                "without sample preparation."
            ),
            "industry_models": [
                {"vendor": "Thermo Fisher", "model": "Nicolet iS50", "type": "Research FTIR", "use": "Advanced characterization, microscopy"},
                {"vendor": "Thermo Fisher", "model": "Nicolet Summit", "type": "Routine FTIR", "use": "Raw material ID, QC"},
                {"vendor": "Bruker", "model": "ALPHA II", "type": "Compact ATR-FTIR", "use": "Raw material ID, incoming inspection"},
                {"vendor": "Bruker", "model": "INVENIO", "type": "Research FTIR", "use": "Protein HOS, advanced materials"},
                {"vendor": "Agilent", "model": "Cary 630 FTIR", "type": "Compact FTIR", "use": "Portable, at-line testing"},
                {"vendor": "PerkinElmer", "model": "Spectrum Two", "type": "Portable FTIR", "use": "Raw material verification, PAT"},
            ],
            "methods_by_product": {
                "Raw Materials & Excipients": [
                    {"method": "ATR-FTIR Identity Test", "purpose": "Incoming raw material identification", "column": "N/A (ATR crystal)", "mobile_phase": "N/A", "detection": "Diamond or ZnSe ATR, 4000-400 cm\u207b\u00b9", "run_time": "< 1 min"},
                    {"method": "Spectral library matching", "purpose": "Compare to reference spectra for identity confirmation", "column": "N/A", "mobile_phase": "N/A", "detection": "Correlation > 0.98", "run_time": "< 1 min"},
                ],
                "Biologics (Protein HOS)": [
                    {"method": "Second-derivative FTIR", "purpose": "Protein secondary structure (Amide I band 1700-1600 cm\u207b\u00b9)", "column": "N/A (ATR or transmission CaF2 cell)", "mobile_phase": "D2O or H2O buffer", "detection": "MCT detector, 2 cm\u207b\u00b9 resolution", "run_time": "5-10 min"},
                    {"method": "FTIR comparability", "purpose": "Biosimilar HOS comparison", "column": "N/A", "mobile_phase": "Matched buffer", "detection": "Spectral overlay and statistical comparison", "run_time": "10 min"},
                ],
                "Packaging & Container Closure": [
                    {"method": "ATR-FTIR polymer ID", "purpose": "Identify container materials (PE, PP, COC)", "column": "N/A (ATR)", "mobile_phase": "N/A", "detection": "ATR-FTIR", "run_time": "< 1 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Background spectrum and sample spectrum",
                    "Library search hit list with match scores",
                    "Pass/fail determination against threshold (e.g., correlation > 0.98)",
                    "Overlay with reference spectrum",
                    "For HOS: second-derivative spectra and statistical analysis",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Spectral resolution (typically 4 cm\u207b\u00b9 for ID, 2 cm\u207b\u00b9 for HOS)", "Number of scans (32-128)", "Library match score threshold"],
                    "Quantitative Output": ["Qualitative: Pass/Fail for identity", "Spectral correlation coefficient", "Amide I peak positions (\u03b1-helix ~1654, \u03b2-sheet ~1635 cm\u207b\u00b9)"],
                },
            },
            "regulatory_references": ["USP <197> Spectroscopic Identification Tests", "USP <854> Mid-Infrared Spectrophotometry", "Ph. Eur. 2.2.24 Absorption Spectrophotometry IR", "21 CFR Part 211.84 (incoming materials testing)"],
        },

        "NMR": {
            "full_name": "Nuclear Magnetic Resonance Spectroscopy",
            "principle": (
                "Nuclei with non-zero spin (1H, 13C, 15N, 31P) placed in a strong magnetic field absorb radiofrequency "
                "energy at characteristic frequencies (chemical shifts) dependent on their electronic environment. "
                "NMR provides detailed 3D structural information, dynamics, and interactions. Chemical shifts are reported "
                "in ppm relative to a reference (TMS for 1H/13C). 2D experiments (COSY, HSQC, NOESY) reveal connectivity "
                "and spatial proximity."
            ),
            "industry_models": [
                {"vendor": "Bruker", "model": "Avance Neo 400", "type": "400 MHz NMR", "use": "Routine structure confirmation, qNMR"},
                {"vendor": "Bruker", "model": "Avance Neo 600", "type": "600 MHz NMR", "use": "Protein NMR, metabolomics"},
                {"vendor": "Bruker", "model": "Avance Neo 800/900", "type": "Ultra-high field", "use": "Protein structure, biosimilar HOS"},
                {"vendor": "JEOL", "model": "ECZ 400S", "type": "400 MHz NMR", "use": "Routine small molecule analysis"},
                {"vendor": "JEOL", "model": "ECZ 600R", "type": "600 MHz NMR", "use": "Research, natural products"},
                {"vendor": "Thermo Fisher", "model": "picoSpin 80", "type": "Benchtop NMR (80 MHz)", "use": "At-line reaction monitoring, teaching"},
                {"vendor": "Nanalysis", "model": "100 MHz NMReady", "type": "Benchtop NMR", "use": "PAT, raw material ID, quick checks"},
            ],
            "methods_by_product": {
                "Small Molecule APIs": [
                    {"method": "1H-NMR Structure Confirmation", "purpose": "Identity confirmation, structure elucidation", "column": "N/A (5 mm NMR tube)", "mobile_phase": "CDCl3, DMSO-d6, or D2O", "detection": "1H at 400-600 MHz", "run_time": "5-15 min"},
                    {"method": "qNMR (Quantitative NMR)", "purpose": "Absolute purity determination without reference standard", "column": "N/A", "mobile_phase": "DMSO-d6 with internal standard (maleic acid, DMSO2)", "detection": "1H at 400+ MHz", "run_time": "15-30 min"},
                    {"method": "13C-NMR", "purpose": "Carbon framework confirmation", "column": "N/A", "mobile_phase": "CDCl3 or DMSO-d6", "detection": "13C at 100-150 MHz", "run_time": "1-12 hours"},
                    {"method": "2D NMR (COSY, HSQC, HMBC)", "purpose": "Full structural assignment, impurity identification", "column": "N/A", "mobile_phase": "Deuterated solvent", "detection": "2D correlation", "run_time": "1-4 hours per experiment"},
                ],
                "Biologics (Protein HOS)": [
                    {"method": "1D 1H NMR fingerprint", "purpose": "Higher-order structure (HOS) comparability", "column": "N/A (3 mm or 5 mm tube)", "mobile_phase": "D2O buffer or H2O/D2O 90:10", "detection": "1H at 600-800 MHz (cryoprobe)", "run_time": "30-60 min"},
                    {"method": "2D 1H-15N HSQC", "purpose": "Residue-level HOS comparison (biosimilars)", "column": "N/A", "mobile_phase": "Buffer in H2O/D2O", "detection": "15N-labeled protein at 600+ MHz", "run_time": "2-12 hours"},
                    {"method": "STD-NMR / WaterLOGSY", "purpose": "Ligand-protein binding screening", "column": "N/A", "mobile_phase": "D2O buffer", "detection": "1H", "run_time": "30-60 min"},
                ],
                "Metabolomics / Bioprocess": [
                    {"method": "1H-NMR metabolic profiling", "purpose": "Untargeted metabolomics of culture supernatant", "column": "N/A", "mobile_phase": "D2O + TSP reference", "detection": "1H at 600 MHz", "run_time": "10 min/sample"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Instrument and probe details (field strength, probe type)",
                    "Acquisition parameters (pulse sequence, number of scans, spectral width, temperature)",
                    "Processing parameters (line broadening, phasing, baseline correction)",
                    "Chemical shift table with assignments",
                    "Annotated spectrum",
                    "For qNMR: purity result with uncertainty",
                    "For HOS: overlay with reference, statistical similarity score",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Lineshape test (50%/0.55%/0.11% widths for CHCl3)", "S/N ratio (> 250:1 for 0.1% ethylbenzene)", "13C sensitivity"],
                    "Quantitative Output": ["Chemical shifts (ppm)", "Coupling constants (Hz)", "Integration ratios", "qNMR purity (% w/w)", "HOS similarity score (e.g., CSD < 1.0)"],
                },
            },
            "regulatory_references": ["USP <761> NMR Spectroscopy", "Ph. Eur. 2.2.33 NMR Spectrometry", "FDA Guidance on Biosimilar HOS Characterization", "EMA Guideline on Similar Biological Medicinal Products"],
        },

        "Raman": {
            "full_name": "Raman Spectroscopy",
            "principle": (
                "Monochromatic laser light interacts with molecular vibrations, causing inelastic (Raman) scattering. "
                "The frequency shift corresponds to vibrational energy levels. Complementary to IR (different selection rules). "
                "Water has weak Raman signal, making it ideal for aqueous biological samples. Can measure through glass/plastic "
                "containers without opening. Fiber-optic probes enable in-situ process monitoring."
            ),
            "industry_models": [
                {"vendor": "Kaiser Optical (Endress+Hauser)", "model": "RamanRxn2", "type": "Process Raman", "use": "In-situ fermentation/cell culture PAT"},
                {"vendor": "Thermo Fisher", "model": "DXR3 Raman Microscope", "type": "Confocal Raman", "use": "Material characterization, polymorphism"},
                {"vendor": "Renishaw", "model": "inVia Qontor", "type": "Research Raman", "use": "Imaging, materials research"},
                {"vendor": "Bruker", "model": "BRAVO", "type": "Handheld Raman", "use": "Raw material ID, incoming inspection"},
                {"vendor": "Metrohm", "model": "Mira DS", "type": "Handheld Raman", "use": "Identity verification, field use"},
                {"vendor": "Hamilton / 908 Devices", "model": "Maven", "type": "At-line Raman", "use": "Bioprocess analyte monitoring"},
            ],
            "methods_by_product": {
                "Cell Culture / Fermentation (PAT)": [
                    {"method": "In-situ Raman with chemometric model", "purpose": "Real-time monitoring of glucose, lactate, glutamine, ammonia, titer", "column": "N/A (immersion probe)", "mobile_phase": "N/A (in bioreactor)", "detection": "785 nm laser, 200-3200 cm\u207b\u00b9", "run_time": "Continuous (30-60 sec/scan)"},
                    {"method": "Off-line Raman calibration", "purpose": "Build PLS models for analyte prediction", "column": "N/A (vial holder)", "mobile_phase": "N/A", "detection": "785 nm laser", "run_time": "1 min/sample"},
                ],
                "Small Molecule APIs": [
                    {"method": "Raman polymorph ID", "purpose": "Solid-state form identification", "column": "N/A (powder on slide)", "mobile_phase": "N/A", "detection": "785 nm laser, Raman microscope", "run_time": "1-5 min"},
                    {"method": "Raman through-container ID", "purpose": "Non-invasive raw material identification", "column": "N/A (handheld through vial)", "mobile_phase": "N/A", "detection": "Handheld Raman", "run_time": "< 1 min"},
                ],
                "Drug Product & Packaging": [
                    {"method": "Container Closure Integrity Testing (CCIT)", "purpose": "Non-destructive seal verification", "column": "N/A", "mobile_phase": "N/A (headspace gas analysis)", "detection": "Raman microscopy", "run_time": "1-5 min/container"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Laser wavelength and power",
                    "Probe type and configuration",
                    "Spectral range and resolution",
                    "Chemometric model details (for PAT: PLS model, calibration R\u00b2, RMSECV)",
                    "Real-time trend data overlay with reference analyzer values",
                    "Library match result for ID applications",
                ],
                "key_parameters": {
                    "PAT Metrics": ["PLS model R\u00b2 (> 0.95)", "RMSECV and RMSEP", "Bias and slope", "Spectral preprocessing (SNV, derivative, baseline)"],
                    "ID Metrics": ["Spectral correlation / HQI score", "Pass/Fail determination"],
                },
            },
            "regulatory_references": ["ICH Q8/Q9/Q10 (PAT framework)", "FDA PAT Guidance (2004)", "USP <858> Raman Spectroscopy", "21 CFR 211.84 (raw material ID)"],
        },

        "Fluorescence": {
            "full_name": "Fluorescence Spectroscopy",
            "principle": (
                "Molecules absorb photons at an excitation wavelength and emit at a longer wavelength (Stokes shift). "
                "Intrinsic fluorescence of proteins comes from tryptophan (ex 295 nm), tyrosine (ex 275 nm), and phenylalanine (ex 257 nm). "
                "Extrinsic fluorescence uses dyes (ANS, SYPRO Orange, fluorescein). 10-1000x more sensitive than UV-Vis. "
                "Emission wavelength and intensity are sensitive to local environment (polarity, quenching)."
            ),
            "industry_models": [
                {"vendor": "Molecular Devices", "model": "SpectraMax iD5", "type": "Multi-mode plate reader", "use": "HTS, DSF, binding assays"},
                {"vendor": "PerkinElmer", "model": "EnSight", "type": "Multi-mode plate reader", "use": "Screening, cell-based assays"},
                {"vendor": "BMG Labtech", "model": "CLARIOstar Plus", "type": "Multi-mode reader", "use": "TR-FRET, fluorescence polarization"},
                {"vendor": "Horiba", "model": "FluoroMax Plus", "type": "Spectrofluorometer", "use": "Research characterization"},
                {"vendor": "Agilent", "model": "Cary Eclipse", "type": "Spectrofluorometer", "use": "Protein conformational studies"},
                {"vendor": "NanoTemper", "model": "Prometheus NT.48", "type": "nanoDSF", "use": "Thermal stability screening, formulation"},
                {"vendor": "Nanotemper", "model": "Monolith NT.115", "type": "MST", "use": "Binding affinity measurement"},
            ],
            "methods_by_product": {
                "Biologics (Protein Characterization)": [
                    {"method": "Intrinsic Fluorescence", "purpose": "Conformational state assessment", "column": "N/A (cuvette)", "mobile_phase": "Buffer", "detection": "Ex 280/295 nm, Em 300-400 nm", "run_time": "5 min"},
                    {"method": "nanoDSF (Differential Scanning Fluorimetry)", "purpose": "Thermal stability (Tm, Tonset), formulation screening", "column": "N/A (capillary)", "mobile_phase": "Formulation buffer", "detection": "Intrinsic fluorescence 330/350 nm ratio", "run_time": "60-90 min (thermal ramp)"},
                    {"method": "ANS Binding Assay", "purpose": "Exposed hydrophobic surface area", "column": "N/A (cuvette/plate)", "mobile_phase": "Buffer + ANS dye", "detection": "Ex 380 nm, Em 400-600 nm", "run_time": "15 min"},
                ],
                "Nucleic Acids": [
                    {"method": "PicoGreen / Qubit Assay", "purpose": "dsDNA quantification (ultra-sensitive)", "column": "N/A (plate/tube)", "mobile_phase": "Assay buffer + PicoGreen dye", "detection": "Ex 480 nm, Em 520 nm", "run_time": "5 min"},
                    {"method": "RiboGreen Assay", "purpose": "RNA quantification", "column": "N/A", "mobile_phase": "TE buffer + RiboGreen", "detection": "Ex 480 nm, Em 520 nm", "run_time": "5 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Excitation and emission wavelengths/slits",
                    "Emission spectrum (peak position, intensity, shape)",
                    "Tm / Tonset values from thermal melting curve",
                    "Binding curve and calculated KD (for interaction studies)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Emission peak position (nm)", "Ratio F350/F330 for nanoDSF", "Tm value (\u00b0C)", "LOD for fluorescent assays"],
                    "Quantitative Output": ["Fluorescence intensity (RFU)", "Tm / Tonset (\u00b0C)", "KD (nM or \u00b5M)", "Concentration from standard curve"],
                },
            },
            "regulatory_references": ["ICH Q6B", "USP <853> Fluorescence Spectrophotometry", "FDA Biosimilar HOS Guidance"],
        },

        "Circular Dichroism": {
            "full_name": "Circular Dichroism Spectroscopy",
            "principle": (
                "Measures the differential absorption of left- and right-circularly polarized light by chiral molecules. "
                "Proteins exhibit distinct CD signatures: far-UV (190-250 nm) reflects secondary structure (\u03b1-helix, \u03b2-sheet, "
                "random coil); near-UV (250-320 nm) reflects tertiary structure from aromatic residues and disulfide bonds. "
                "CD signals reported in mean residue ellipticity (deg\u00b7cm\u00b2/dmol)."
            ),
            "industry_models": [
                {"vendor": "JASCO", "model": "J-1500", "type": "CD Spectrometer", "use": "Protein HOS characterization, biosimilars"},
                {"vendor": "JASCO", "model": "J-1700", "type": "CD/LD/Fluorescence", "use": "Multimodal HOS analysis"},
                {"vendor": "Applied Photophysics", "model": "Chirascan V100", "type": "CD Spectrometer", "use": "High-throughput HOS, thermal stability"},
                {"vendor": "Applied Photophysics", "model": "Chirascan Q100", "type": "CD with SEC", "use": "Automated HOS with chromatography"},
                {"vendor": "Aviv Biomedical", "model": "Model 435", "type": "CD Spectrometer", "use": "Precision biophysics"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs) / Biosimilars": [
                    {"method": "Far-UV CD (190-250 nm)", "purpose": "Secondary structure content (\u03b1-helix, \u03b2-sheet)", "column": "N/A (0.1 cm cuvette)", "mobile_phase": "10-20 mM phosphate buffer (low UV absorbing)", "detection": "CD at 190-250 nm, 0.2 mg/mL", "run_time": "10-20 min"},
                    {"method": "Near-UV CD (250-320 nm)", "purpose": "Tertiary structure fingerprint", "column": "N/A (1 cm cuvette)", "mobile_phase": "Formulation buffer", "detection": "CD at 250-320 nm, 1-2 mg/mL", "run_time": "10-20 min"},
                    {"method": "CD thermal melt", "purpose": "Thermal stability (Tm by CD)", "column": "N/A", "mobile_phase": "Buffer", "detection": "CD at 218 nm vs temperature", "run_time": "60-120 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Instrument calibration (CSA or ACS standards)",
                    "Far-UV and/or near-UV CD spectrum",
                    "Overlay with reference material (for biosimilars)",
                    "Secondary structure estimation (from deconvolution software)",
                    "Thermal melting curve and Tm determination",
                    "Statistical comparison to reference (if applicable)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Wavelength accuracy (\u00b1 0.5 nm)", "Ellipticity accuracy (CSA standard)", "HT voltage < 600 V (adequate light throughput)"],
                    "Quantitative Output": ["Mean residue ellipticity [\u03b8] (deg\u00b7cm\u00b2/dmol)", "Secondary structure % (\u03b1-helix, \u03b2-sheet, turn, disorder)", "Tm from thermal melt (\u00b0C)"],
                },
            },
            "regulatory_references": ["ICH Q6B", "FDA Guidance on Biosimilar Quality", "USP <1048> Quality of Biotechnological/Biological Products"],
        },

        "NIR": {
            "full_name": "Near-Infrared Spectroscopy",
            "principle": (
                "Absorption of light in the 780-2500 nm (12,800-4,000 cm\u207b\u00b9) range by overtone and combination bands "
                "of O-H, N-H, C-H, and S-H vibrations. Spectra are broad and overlapping, requiring chemometric models "
                "(PLS, PCA) for interpretation. Non-destructive, fast, requires no sample preparation. "
                "Ideal for PAT and at-line applications."
            ),
            "industry_models": [
                {"vendor": "Bruker", "model": "MPA II", "type": "FT-NIR", "use": "Raw material ID, moisture, blend uniformity"},
                {"vendor": "FOSS", "model": "DS2500", "type": "Scanning NIR", "use": "Agriculture, food, biopharma raw materials"},
                {"vendor": "Thermo Fisher", "model": "Antaris II", "type": "FT-NIR", "use": "Pharma QC, raw material ID"},
                {"vendor": "Metrohm", "model": "NIRS XDS", "type": "Monochromator NIR", "use": "Pharmaceutical QC, GMP labs"},
                {"vendor": "ABB / FOSS", "model": "MB3600", "type": "FT-NIR", "use": "Process and lab analysis"},
                {"vendor": "Hamilton", "model": "VisiFerm NIR probes", "type": "In-situ NIR", "use": "Bioreactor process monitoring"},
            ],
            "methods_by_product": {
                "Raw Materials & Excipients": [
                    {"method": "NIR Identity Verification", "purpose": "100% incoming material ID testing", "column": "N/A (reflectance probe)", "mobile_phase": "N/A", "detection": "NIR 900-1700 nm", "run_time": "< 30 sec"},
                    {"method": "NIR Moisture Content", "purpose": "Water content in powders / granules", "column": "N/A", "mobile_phase": "N/A", "detection": "NIR with PLS calibration", "run_time": "< 30 sec"},
                ],
                "Cell Culture / Fermentation (PAT)": [
                    {"method": "In-situ NIR with PLS model", "purpose": "Real-time glucose, glutamine, lactate monitoring", "column": "N/A (in-line probe)", "mobile_phase": "N/A", "detection": "NIR 900-1700 nm", "run_time": "Continuous"},
                ],
                "Solid Dosage Forms": [
                    {"method": "NIR Blend Uniformity", "purpose": "Homogeneity verification during blending", "column": "N/A (through-wall probe or window)", "mobile_phase": "N/A", "detection": "NIR with PCA / PLS model", "run_time": "Continuous during blending"},
                    {"method": "NIR Content Uniformity", "purpose": "Tablet-to-tablet drug content", "column": "N/A (tablet holder)", "mobile_phase": "N/A", "detection": "NIR transmission/reflectance", "run_time": "< 10 sec/tablet"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Spectral preprocessing applied",
                    "Chemometric model details (type, calibration set size, R\u00b2, RMSECV)",
                    "Predicted vs. reference correlation plot",
                    "ID match result with threshold and score",
                    "Ongoing model maintenance records",
                ],
                "key_parameters": {
                    "Model Performance": ["R\u00b2 calibration and validation (> 0.95)", "RMSECV / RMSEP", "Bias and slope of validation", "Mahalanobis distance for outlier detection"],
                    "Quantitative Output": ["Predicted concentration or moisture %", "Pass/Fail for identity", "Spectral distance from library"],
                },
            },
            "regulatory_references": ["USP <856> Near-Infrared Spectrophotometry", "FDA PAT Guidance (2004)", "Ph. Eur. 2.2.40 NIR Spectrophotometry", "21 CFR 211.84"],
        },

        "AAS": {
            "full_name": "Atomic Absorption Spectroscopy",
            "principle": (
                "Ground-state atoms in a flame or graphite furnace absorb characteristic wavelengths of light from a "
                "hollow cathode lamp. Absorption is proportional to atom concentration (Beer-Lambert Law). "
                "Element-specific (one lamp per element). Flame AAS is simple and fast; graphite furnace (GFAAS) "
                "provides 10-100x better sensitivity for trace analysis."
            ),
            "industry_models": [
                {"vendor": "Agilent", "model": "280FS AA", "type": "Flame AAS", "use": "Routine metal analysis"},
                {"vendor": "Agilent", "model": "280Z AA", "type": "Graphite Furnace AAS", "use": "Trace heavy metals"},
                {"vendor": "PerkinElmer", "model": "PinAAcle 900H", "type": "Flame/Furnace AAS", "use": "Pharmaceutical trace metals"},
                {"vendor": "Shimadzu", "model": "AA-7000", "type": "Flame/Furnace AAS", "use": "General purpose"},
                {"vendor": "Analytik Jena", "model": "contrAA 800", "type": "HR-CS AAS", "use": "Multi-element, background correction"},
            ],
            "methods_by_product": {
                "Drug Products & Raw Materials": [
                    {"method": "Flame AAS", "purpose": "Ca, Mg, Na, K, Fe, Cu, Zn quantification", "column": "N/A (nebulizer)", "mobile_phase": "Dilute acid matrix", "detection": "Element-specific HCL", "run_time": "< 1 min/element"},
                    {"method": "GFAAS", "purpose": "Trace Pb, Cd, As determination", "column": "N/A (graphite tube)", "mobile_phase": "Acid-digested sample + matrix modifier", "detection": "Element-specific HCL", "run_time": "3-5 min/element"},
                ],
                "Water Systems": [
                    {"method": "AAS metals screen", "purpose": "Water for injection (WFI) heavy metals", "column": "N/A", "mobile_phase": "Acidified water sample", "detection": "Flame or GFAAS", "run_time": "1-5 min/element"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Lamp current and wavelength",
                    "Calibration curve with R\u00b2 > 0.995",
                    "Background correction method used",
                    "Spike recovery results (85-115%)",
                    "Concentration result per element",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Calibration linearity (R\u00b2 > 0.995)", "Characteristic concentration (sensitivity check)", "MDL / LOQ"],
                    "Quantitative Output": ["Concentration (mg/L or \u00b5g/L)", "Absorbance (AU)", "% Recovery"],
                },
            },
            "regulatory_references": ["USP <852> Atomic Absorption Spectroscopy", "Ph. Eur. 2.4.2 Heavy Metals", "USP <232>/<233> (ICP-MS preferred but AAS accepted)"],
        },

        "ITC": {
            "full_name": "Isothermal Titration Calorimetry",
            "principle": (
                "Directly measures the heat released or absorbed during a biomolecular binding event. A ligand solution "
                "is titrated into a sample cell containing the macromolecule, and the differential power required to maintain "
                "zero temperature difference between sample and reference cells is recorded. A single experiment yields the "
                "binding affinity (Kd), stoichiometry (n), enthalpy (ΔH), and entropy (ΔS) of the interaction without "
                "labeling or immobilization. Considered the gold standard for binding thermodynamics."
            ),
            "industry_models": [
                {"vendor": "Malvern Panalytical", "model": "MicroCal PEAQ-ITC", "type": "High-sensitivity ITC", "use": "Protein-ligand binding, antibody-antigen interactions"},
                {"vendor": "Malvern Panalytical", "model": "MicroCal PEAQ-ITC Automated", "type": "Automated ITC (96-well)", "use": "Medium-throughput screening of binding interactions"},
                {"vendor": "TA Instruments", "model": "Affinity ITC", "type": "ITC", "use": "General biomolecular interaction studies"},
                {"vendor": "TA Instruments", "model": "Nano ITC", "type": "Low-volume ITC", "use": "Low sample consumption studies"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "ITC antigen binding", "purpose": "Binding affinity (Kd), stoichiometry, and thermodynamics of mAb-antigen interaction", "column": "N/A (solution-based, cell volume 200-300 µL)", "mobile_phase": "Matched buffer (PBS, HEPES, or formulation buffer)", "detection": "Differential power compensation calorimetry", "run_time": "60-90 min per titration"},
                    {"method": "ITC FcRn binding", "purpose": "FcRn binding thermodynamics (relevant to half-life)", "column": "N/A", "mobile_phase": "Acetate buffer pH 6.0 (mimics endosomal pH)", "detection": "Calorimetry", "run_time": "60-90 min"},
                ],
                "Small Molecule APIs": [
                    {"method": "ITC drug-target binding", "purpose": "Binding affinity and thermodynamic signature for lead optimization", "column": "N/A", "mobile_phase": "Buffer matched to target stability", "detection": "Calorimetry", "run_time": "60-90 min"},
                ],
                "Biosimilars": [
                    {"method": "ITC comparative binding", "purpose": "Thermodynamic fingerprint comparison vs. reference product", "column": "N/A", "mobile_phase": "Matched buffer", "detection": "Calorimetry", "run_time": "60-90 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Raw thermogram (µcal/sec vs time)",
                    "Integrated isotherm (kcal/mol vs molar ratio)",
                    "Fitted binding model and residuals",
                    "Binding parameters: Kd, n, ΔH, ΔS, ΔG",
                    "Buffer mismatch / heat of dilution control",
                    "Protein concentration and purity verification",
                ],
                "key_parameters": {
                    "Performance Metrics": ["c-value (1 < c < 1000 for reliable fitting)", "Heat of dilution control (< 10% of binding signal)", "Baseline stability"],
                    "Quantitative Output": ["Kd (nM to mM)", "n (stoichiometry)", "ΔH (kcal/mol)", "TΔS (kcal/mol)", "ΔG (kcal/mol)"],
                },
            },
            "regulatory_references": ["ICH Q6B", "FDA Guidance on Biosimilar Analytical Studies (higher-order structure)", "EMA Guideline on Similar Biological Medicinal Products"],
        },

        "HDX-MS": {
            "full_name": "Hydrogen-Deuterium Exchange Mass Spectrometry",
            "principle": (
                "Probes protein higher-order structure and dynamics by measuring the rate of backbone amide hydrogen exchange "
                "with deuterium from D2O solvent. Solvent-exposed and flexible regions exchange rapidly; buried or hydrogen-bonded "
                "regions exchange slowly. After defined labeling times, exchange is quenched (pH 2.5, 0°C), the protein is digested "
                "with acid-stable protease (pepsin), and peptides are analyzed by LC-MS. The mass shift (+1 Da per exchanged amide) "
                "reveals conformational dynamics, ligand binding sites, and epitope/paratope mapping at peptide-level resolution."
            ),
            "industry_models": [
                {"vendor": "Waters", "model": "SYNAPT XS with HDX Manager", "type": "HDX-MS system (Q-TOF)", "use": "Epitope mapping, biosimilar HOS comparability"},
                {"vendor": "Waters", "model": "HDX-2 Automated System (LEAP/Trajan)", "type": "Automated HDX sample handling", "use": "Reproducible labeling and quench automation"},
                {"vendor": "Thermo Fisher", "model": "Orbitrap Eclipse + HDX PAL", "type": "HDX-MS (Orbitrap)", "use": "High-resolution HDX for complex biologics"},
                {"vendor": "Bruker", "model": "timsTOF Pro 2 with HDX", "type": "HDX-MS (trapped ion mobility)", "use": "HDX with ion mobility separation"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "HDX-MS epitope mapping", "purpose": "Identify antigen epitope and antibody paratope regions", "column": "Enzymate BEH pepsin column (2.1 x 30 mm)", "mobile_phase": "0.1% formic acid in water/ACN, 0°C", "detection": "ESI-MS (Q-TOF or Orbitrap)", "run_time": "10 min LC + multiple labeling times (10s, 1m, 10m, 60m, 240m)"},
                    {"method": "HDX-MS HOS comparability", "purpose": "Higher-order structure comparison (biosimilar vs. innovator)", "column": "Pepsin column, C18 trap + analytical", "mobile_phase": "0.1% FA in water/ACN at 0°C", "detection": "ESI-MS", "run_time": "Multiple labeling times, triplicate"},
                ],
                "Biosimilars": [
                    {"method": "HDX-MS structural fingerprinting", "purpose": "Conformational equivalence vs. reference product at peptide level", "column": "Pepsin column + C18", "mobile_phase": "0.1% FA, 0°C", "detection": "ESI-MS", "run_time": "Multiple labeling times, triplicate per condition"},
                ],
                "Vaccines / Recombinant Proteins": [
                    {"method": "HDX-MS conformational analysis", "purpose": "Structural integrity, conformational dynamics of antigens", "column": "Pepsin column + C18", "mobile_phase": "0.1% FA, 0°C", "detection": "ESI-MS", "run_time": "Multiple labeling times"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Peptide coverage map (> 90% sequence coverage preferred)",
                    "Deuterium uptake plots (Da vs labeling time) per peptide",
                    "Butterfly or mirror plots for comparative HDX",
                    "Difference map (ΔDeuterium) with significance thresholds",
                    "Heat map of exchange rates onto 3D structure (if available)",
                    "Back-exchange correction (< 30% recommended)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Sequence coverage (> 90%)", "Redundancy (> 3 overlapping peptides per region)", "Back-exchange (< 30%)", "Deuterium uptake reproducibility (< 0.3 Da SD)"],
                    "Quantitative Output": ["Deuterium uptake (Da) per peptide per time point", "ΔDeuterium (comparative)", "Protection factor estimates", "Fractional exchange (%)"],
                },
            },
            "regulatory_references": ["ICH Q6B", "FDA Guidance on Biosimilar Analytical Studies (HOS characterization)", "EMA Guideline on Similar Biological Medicinal Products", "ICH Q5E Comparability"],
        },
    },

    # =========================================================================
    # ELECTROPHORESIS & SEPARATION
    # =========================================================================
    "Electrophoresis & Separation": {
        "SDS-PAGE": {
            "full_name": "Sodium Dodecyl Sulfate\u2013Polyacrylamide Gel Electrophoresis",
            "principle": (
                "Proteins are denatured with SDS detergent, which coats them with uniform negative charge proportional "
                "to mass. Proteins migrate through a polyacrylamide gel matrix under electric field, separating by molecular "
                "weight. Reducing conditions (DTT/BME) break disulfide bonds. Staining with Coomassie Blue (1-10 \u00b5g detection) "
                "or silver stain (1-10 ng detection) visualizes bands."
            ),
            "industry_models": [
                {"vendor": "Bio-Rad", "model": "Mini-PROTEAN Tetra", "type": "Mini gel system", "use": "Routine lab-scale SDS-PAGE"},
                {"vendor": "Bio-Rad", "model": "Criterion Cell", "type": "Midi gel system", "use": "Higher throughput, more lanes"},
                {"vendor": "Thermo Fisher", "model": "Bolt Mini Gel System", "type": "Mini gel", "use": "Pre-cast Bis-Tris gels"},
                {"vendor": "Thermo Fisher", "model": "XCell SureLock", "type": "Mini gel", "use": "NuPAGE system"},
                {"vendor": "Bio-Rad", "model": "ChemiDoc MP", "type": "Gel imager", "use": "Stain-free, fluorescent, chemiluminescent imaging"},
                {"vendor": "Cytiva", "model": "ImageQuant 800", "type": "Gel/blot imager", "use": "Quantitative gel imaging"},
            ],
            "methods_by_product": {
                "Biologics (General)": [
                    {"method": "Reducing SDS-PAGE", "purpose": "Purity, MW of individual chains (HC, LC)", "column": "4-12% Bis-Tris gel", "mobile_phase": "MES or MOPS SDS running buffer", "detection": "Coomassie or silver stain", "run_time": "35-60 min"},
                    {"method": "Non-reducing SDS-PAGE", "purpose": "Intact molecule MW, fragmentation", "column": "3-8% Tris-Acetate gel", "mobile_phase": "Tris-Acetate SDS running buffer", "detection": "Coomassie stain", "run_time": "60-90 min"},
                    {"method": "Stain-free SDS-PAGE", "purpose": "Label-free protein visualization and quantification", "column": "Stain-free TGX precast gel", "mobile_phase": "Tris/Glycine/SDS buffer", "detection": "UV-activated fluorescence (ChemiDoc)", "run_time": "30 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Gel image with MW ladder annotation",
                    "Band identification and apparent MW",
                    "Densitometry results (% purity)",
                    "Gel lot number and staining protocol",
                ],
                "key_parameters": {
                    "Performance Metrics": ["MW ladder resolution", "Band sharpness and symmetry", "Staining sensitivity limit"],
                    "Quantitative Output": ["Apparent MW (kDa)", "Band purity (% by densitometry)", "Visual comparison to reference"],
                },
            },
            "regulatory_references": ["ICH Q6B", "USP <1056> Biotechnology-Derived Articles\u2014Polyacrylamide Gel Electrophoresis"],
        },

        "Capillary Electrophoresis": {
            "full_name": "Capillary Electrophoresis",
            "principle": (
                "Separation of analytes in a narrow fused-silica capillary (25-100 \u00b5m ID) under high voltage (10-30 kV). "
                "Separation modes include CZE (charge/size), CE-SDS (size-based like SDS-PAGE but automated), "
                "cIEF (isoelectric focusing in capillary), and CE-LIF (laser-induced fluorescence for glycans). "
                "Provides quantitative, reproducible, automatable alternatives to gel-based methods."
            ),
            "industry_models": [
                {"vendor": "Sciex", "model": "PA 800 Plus", "type": "Multi-mode CE", "use": "CE-SDS, cIEF, CZE for biologics QC"},
                {"vendor": "Agilent", "model": "7100 CE", "type": "CE system", "use": "Small molecule, oligonucleotide CE"},
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "Maurice", "type": "CE-SDS + cIEF", "use": "Automated mAb purity and charge variants"},
                {"vendor": "ProteinSimple", "model": "iCE3", "type": "Whole-column cIEF", "use": "High-resolution charge variant analysis"},
                {"vendor": "Agilent", "model": "Fragment Analyzer", "type": "CE for nucleic acids", "use": "DNA/RNA quality, mRNA integrity"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "CE-SDS (reduced)", "purpose": "Purity (HC, LC, non-glycosylated HC)", "column": "Bare fused silica 30 cm", "mobile_phase": "SDS-MW gel buffer + DTT", "detection": "UV 220 nm", "run_time": "30 min"},
                    {"method": "CE-SDS (non-reduced)", "purpose": "Intact IgG purity, fragments, aggregates", "column": "Bare fused silica 30 cm", "mobile_phase": "SDS-MW gel buffer + NEM", "detection": "UV 220 nm", "run_time": "30 min"},
                    {"method": "cIEF (imaged)", "purpose": "Charge variant profiling (acidic, main, basic)", "column": "Neutral-coated capillary or cartridge", "mobile_phase": "Ampholyte mixture (pH 3-10) + pI markers", "detection": "Whole-column UV imaging 280 nm", "run_time": "10-15 min"},
                    {"method": "CZE", "purpose": "Free-solution charge variant separation", "column": "Neutral or positive-coated capillary", "mobile_phase": "Acetate or phosphate buffer pH 5.7", "detection": "UV 214 nm", "run_time": "20-30 min"},
                ],
                "mRNA & Oligonucleotides": [
                    {"method": "CGE (Capillary Gel Electrophoresis)", "purpose": "mRNA integrity (% intact)", "column": "Gel-filled capillary", "mobile_phase": "RNA gel matrix", "detection": "UV or LIF", "run_time": "30-45 min"},
                    {"method": "CE for oligonucleotide purity", "purpose": "Full-length product purity", "column": "Coated capillary", "mobile_phase": "Urea + Tris-borate buffer", "detection": "UV 260 nm", "run_time": "30 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Electropherogram with labeled peaks",
                    "Migration time and corrected peak areas",
                    "Purity results (% main peak, % pre-peak, % post-peak)",
                    "pI values (for cIEF) from pI marker calibration",
                    "System suitability (resolution, migration time repeatability)",
                ],
                "key_parameters": {
                    "System Suitability": ["Migration time %RSD < 2%", "Peak area %RSD < 5%", "Resolution of critical pairs > 1.0"],
                    "Quantitative Output": ["Corrected peak area %", "pI values (for cIEF)", "% Purity (main peak)", "% Acidic/basic species"],
                },
            },
            "regulatory_references": ["ICH Q6B", "USP <1053> CE for Biotechnology-Derived Products", "Ph. Eur. 2.2.47 Capillary Electrophoresis"],
        },

        "iCE3 (icIEF)": {
            "full_name": "Imaged Capillary Isoelectric Focusing",
            "principle": (
                "A whole-column imaging variant of capillary isoelectric focusing. Carrier ampholytes and the protein sample "
                "fill a short capillary (5 cm) with a UV-transparent coating. Under an applied electric field, a pH gradient "
                "forms and proteins migrate to their isoelectric point (pI). The entire capillary is simultaneously imaged by "
                "a CCD detector at 280 nm, eliminating the need for mobilization. Provides high-resolution pI determination "
                "and charge variant quantification (acidic, main, and basic species). Increasingly replacing conventional "
                "IEF slab gels in GMP QC labs due to superior quantitation, automation, and reproducibility."
            ),
            "industry_models": [
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "iCE3", "type": "Imaged cIEF", "use": "Charge variant analysis, pI determination for mAbs and biologics"},
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "Maurice", "type": "Integrated CE (cIEF + CE-SDS)", "use": "Dual-mode platform — charge variants and purity on one instrument"},
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "Maurice C.", "type": "cIEF-only platform", "use": "Dedicated charge variant analysis"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "icIEF charge variant analysis", "purpose": "Quantification of acidic, main, and basic species; pI determination", "column": "FC-coated capillary cartridge (100 µm ID)", "mobile_phase": "Pharmalyte 3-10 carrier ampholytes + pI markers (4.65, 9.77)", "detection": "Whole-column UV imaging at 280 nm", "run_time": "10-15 min (focus + image)"},
                ],
                "Biosimilars": [
                    {"method": "icIEF comparative charge profile", "purpose": "Charge variant fingerprint comparison vs. reference product", "column": "FC-coated capillary cartridge", "mobile_phase": "Pharmalyte 3-10 + pI markers", "detection": "UV 280 nm whole-column imaging", "run_time": "10-15 min"},
                ],
                "Fusion Proteins / Fc-Fusion": [
                    {"method": "icIEF charge heterogeneity", "purpose": "pI and charge variant profiling", "column": "FC-coated capillary cartridge", "mobile_phase": "Pharmalyte + pI markers (adjusted for expected pI range)", "detection": "UV 280 nm", "run_time": "10-15 min"},
                ],
                "ADCs": [
                    {"method": "icIEF post-conjugation charge shift", "purpose": "Charge profile change after drug-linker conjugation", "column": "FC-coated capillary cartridge", "mobile_phase": "Pharmalyte 3-10 + pI markers", "detection": "UV 280 nm", "run_time": "10-15 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Electropherogram (absorbance vs. pI)",
                    "pI of main peak and range of charge variants",
                    "% Acidic species, % Main peak, % Basic species",
                    "pI marker verification (within ± 0.1 pI units)",
                    "System suitability (pI marker resolution, repeatability)",
                    "Overlay with reference standard or prior lot",
                ],
                "key_parameters": {
                    "System Suitability": ["pI marker accuracy (± 0.1 pI units)", "Peak area %RSD < 5% (replicate injections)", "Resolution of pI markers"],
                    "Quantitative Output": ["pI of main peak", "% Acidic species", "% Main peak", "% Basic species", "Number of resolved charge variants"],
                },
                "acceptance_criteria_examples": {
                    "mAb charge variants": {"Main peak": "≥ specification (e.g., ≥ 50%)", "Acidic species": "≤ specification", "Basic species": "≤ specification", "pI (main)": "Within ± 0.2 of reference standard"},
                },
            },
            "regulatory_references": ["ICH Q6B Specifications for Biologicals", "USP <1053> Capillary Electrophoresis", "Ph. Eur. 2.2.47 Capillary Electrophoresis", "FDA Guidance on Biosimilar Analytical Studies"],
        },

        "cSDS (CE-SDS)": {
            "full_name": "Capillary SDS Electrophoresis (CE-SDS)",
            "principle": (
                "An automated, quantitative replacement for traditional SDS-PAGE. Proteins are denatured with SDS (and "
                "optionally reduced with β-mercaptoethanol or DTT) to form SDS-protein complexes with uniform charge-to-mass "
                "ratio. Separation occurs by molecular sieving through a replaceable gel-filled capillary. Detection is by "
                "UV absorbance (220 nm) or laser-induced fluorescence (LIF) after fluorescent labeling. Provides precise "
                "molecular weight estimation and quantitative purity assessment (% main peak, fragments, aggregates) with "
                "superior reproducibility and throughput compared to slab gel SDS-PAGE."
            ),
            "industry_models": [
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "Maurice", "type": "Integrated CE (CE-SDS + cIEF)", "use": "Purity and charge variant analysis on one platform"},
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "Maurice S.", "type": "CE-SDS-only platform", "use": "Dedicated purity and MW analysis"},
                {"vendor": "SCIEX (Beckman Coulter)", "model": "PA 800 Plus", "type": "Multi-mode CE system", "use": "CE-SDS, cIEF, CZE — versatile CE platform"},
                {"vendor": "Agilent", "model": "7100 CE System", "type": "Multi-mode CE", "use": "CE-SDS and other CE modes"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "Non-reduced CE-SDS (NR-cSDS)", "purpose": "Intact IgG purity, detection of aggregates, fragments, half-antibody", "column": "Bare fused-silica capillary with SDS-MW gel buffer", "mobile_phase": "SDS-MW Gel Buffer (ProteinSimple) or SDS 14-200 Gel Buffer (SCIEX)", "detection": "UV 220 nm or LIF (after fluorescent labeling)", "run_time": "25-35 min"},
                    {"method": "Reduced CE-SDS (R-cSDS)", "purpose": "Heavy chain and light chain purity, clipping analysis", "column": "Bare fused-silica capillary with SDS-MW gel buffer", "mobile_phase": "SDS-MW gel buffer + β-mercaptoethanol reduction", "detection": "UV 220 nm or LIF", "run_time": "25-35 min"},
                ],
                "Biosimilars": [
                    {"method": "CE-SDS (reduced + non-reduced)", "purpose": "Purity profile comparison vs. reference product", "column": "SDS gel-filled capillary", "mobile_phase": "SDS-MW gel buffer", "detection": "UV 220 nm or LIF", "run_time": "25-35 min per mode"},
                ],
                "ADCs": [
                    {"method": "CE-SDS for ADC", "purpose": "Drug-loaded species, unconjugated antibody, free drug detection", "column": "SDS gel-filled capillary", "mobile_phase": "SDS-MW gel buffer", "detection": "UV 220 nm or LIF", "run_time": "30-40 min"},
                ],
                "Recombinant Proteins / Enzymes": [
                    {"method": "CE-SDS purity", "purpose": "% Main peak purity and MW estimation", "column": "SDS gel-filled capillary", "mobile_phase": "SDS-MW gel buffer", "detection": "UV 220 nm", "run_time": "25-35 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Electropherogram (absorbance/fluorescence vs. migration time)",
                    "MW calibration curve (internal standard or MW markers)",
                    "Peak table with corrected area %, migration time, and estimated MW",
                    "% Purity (main peak), % Pre-peaks (LMW), % Post-peaks (HMW)",
                    "System suitability (IgG control standard recovery, MW marker resolution)",
                    "Overlay with reference standard or prior lot (for trending)",
                ],
                "key_parameters": {
                    "System Suitability": ["IgG control purity ≥ 95% (non-reduced)", "Migration time %RSD < 2%", "MW marker resolution", "Peak area %RSD < 5%"],
                    "Quantitative Output": ["% Purity (main peak)", "% LMW species (fragments, clips)", "% HMW species (aggregates, non-covalent dimers)", "Estimated MW (kDa)", "% Heavy chain, % Light chain (reduced)"],
                },
                "acceptance_criteria_examples": {
                    "mAb NR-cSDS purity": {"Intact IgG (main peak)": "≥ 95.0%", "Total LMW": "≤ 3.0%", "Total HMW": "≤ 2.0%"},
                    "mAb R-cSDS purity": {"HC + LC (combined purity)": "≥ 95.0%", "Non-glycosylated HC (NGHC)": "≤ 2.0%"},
                },
            },
            "regulatory_references": ["ICH Q6B Specifications for Biologicals", "USP <1053> CE for Biotechnology-Derived Products", "Ph. Eur. 2.2.47 Capillary Electrophoresis", "FDA Guidance on Biosimilar Analytical Studies"],
        },
    },

    # =========================================================================
    # BIOANALYTICAL & IMMUNOASSAYS
    # =========================================================================
    "Bioanalytical & Immunoassays": {
        "ELISA": {
            "full_name": "Enzyme-Linked Immunosorbent Assay",
            "principle": (
                "Antibody-based assay where target analyte is captured on a solid phase (microplate), detected by an "
                "enzyme-conjugated antibody, and quantified via colorimetric, fluorescent, or chemiluminescent substrate. "
                "Sandwich ELISA uses capture + detection antibody pair. Highly specific (antibody recognition) and sensitive "
                "(pg/mL range with chemiluminescence). Standard curves with 4PL or 5PL regression."
            ),
            "industry_models": [
                {"vendor": "Molecular Devices", "model": "SpectraMax iD3/iD5", "type": "Microplate reader", "use": "ELISA, cell-based assays"},
                {"vendor": "BMG Labtech", "model": "FLUOstar Omega", "type": "Microplate reader", "use": "High-performance ELISA reading"},
                {"vendor": "BioTek (Agilent)", "model": "Synergy H1", "type": "Multi-mode reader", "use": "ELISA, fluorescence, luminescence"},
                {"vendor": "PerkinElmer", "model": "EnVision 2105", "type": "Multi-mode reader", "use": "HTS, alpha assays, ELISA"},
                {"vendor": "Meso Scale Discovery", "model": "MESO QuickPlex SQ 120", "type": "ECL immunoassay", "use": "Multiplex cytokine, ADA, PK assays"},
                {"vendor": "Gyros Protein Technologies", "model": "Gyrolab xPlore", "type": "Nanoliter immunoassay", "use": "Low-volume, high-throughput titer and PK"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "Product titer ELISA", "purpose": "IgG concentration in cell culture harvest", "column": "N/A (96-well plate)", "mobile_phase": "PBS/Tween wash, TMB substrate", "detection": "Absorbance 450 nm", "run_time": "4-5 hours"},
                    {"method": "HCP ELISA", "purpose": "Host cell protein quantification (process-specific)", "column": "N/A (plate)", "mobile_phase": "Kit-specific buffers", "detection": "Abs 450 nm", "run_time": "6-8 hours"},
                    {"method": "Residual Protein A ELISA", "purpose": "Leached Protein A quantification", "column": "N/A (plate)", "mobile_phase": "Kit buffers", "detection": "Abs 450 nm", "run_time": "5 hours"},
                    {"method": "Anti-Drug Antibody (ADA) assay", "purpose": "Immunogenicity testing", "column": "N/A (MSD plate)", "mobile_phase": "Assay diluent", "detection": "ECL (MSD) or bridging ELISA", "run_time": "6-8 hours"},
                ],
                "Vaccines": [
                    {"method": "Antigen content ELISA", "purpose": "Antigen quantification per dose", "column": "N/A (plate)", "mobile_phase": "Kit-specific", "detection": "Abs 450 nm", "run_time": "5 hours"},
                    {"method": "Potency ELISA", "purpose": "Functional antibody binding as potency measure", "column": "N/A", "mobile_phase": "Assay buffers", "detection": "Abs 450 nm", "run_time": "6 hours"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "Capsid titer ELISA (AAV)", "purpose": "Total capsid particles (vp/mL)", "column": "N/A (AAV Titration ELISA kit)", "mobile_phase": "Kit buffers", "detection": "Abs 450 nm", "run_time": "5 hours"},
                    {"method": "Transgene protein ELISA", "purpose": "Expressed protein from vector", "column": "N/A", "mobile_phase": "Product-specific", "detection": "Abs 450 nm", "run_time": "5 hours"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Plate layout diagram",
                    "Standard curve with 4PL/5PL fit and R\u00b2",
                    "Sample results (mean, %CV of replicates)",
                    "Dilution linearity and spike recovery",
                    "Assay controls (positive, negative, matrix)",
                    "Pass/fail for system suitability",
                ],
                "key_parameters": {
                    "System Suitability": ["Standard curve R\u00b2 > 0.99", "Back-calculated standard accuracy (80-120%)", "Replicate %CV < 20% (< 25% at LLOQ)", "Control within range"],
                    "Quantitative Output": ["Concentration (ng/mL, \u00b5g/mL, or ppm)", "Dilution-corrected result", "Mean and %CV of replicates"],
                },
            },
            "regulatory_references": ["ICH Q2(R2) Validation", "FDA Guidance: Bioanalytical Method Validation (2018)", "USP <1103> Immunological Test Methods\u2014ELISA"],
        },

        "SPR": {
            "full_name": "Surface Plasmon Resonance",
            "principle": (
                "One binding partner (ligand) is immobilized on a gold sensor chip. When analyte flows over the surface "
                "and binds, the local mass change alters the refractive index, shifting the SPR angle. Binding is monitored "
                "in real time as response units (RU). Association (ka), dissociation (kd), and equilibrium dissociation "
                "constant (KD = kd/ka) are determined from sensorgram kinetics. Label-free and real-time."
            ),
            "industry_models": [
                {"vendor": "Cytiva", "model": "Biacore 8K+", "type": "8-channel SPR", "use": "Kinetics, biosimilar comparability"},
                {"vendor": "Cytiva", "model": "Biacore T200", "type": "Research SPR", "use": "Detailed kinetics and affinity"},
                {"vendor": "Cytiva", "model": "Biacore 1 Series", "type": "QC SPR", "use": "GMP lot release testing"},
                {"vendor": "Carterra", "model": "LSA", "type": "High-throughput SPR array", "use": "Antibody screening, epitope binning (384-plex)"},
                {"vendor": "Bruker", "model": "Sierra SPR-32 Pro", "type": "32-channel SPR", "use": "Fragment screening, kinetics"},
                {"vendor": "Nicoya", "model": "Alto", "type": "Digital SPR", "use": "Cost-effective SPR for R&D"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs) / Biosimilars": [
                    {"method": "Antigen binding kinetics", "purpose": "ka, kd, KD determination for target antigen", "column": "CM5 or Series S CM5 chip", "mobile_phase": "HBS-EP+ running buffer", "detection": "SPR response (RU)", "run_time": "2-4 hours"},
                    {"method": "FcRn binding (pH-dependent)", "purpose": "Neonatal Fc receptor binding for PK prediction", "column": "CM5 chip with FcRn immobilized", "mobile_phase": "pH 6.0 binding / pH 7.4 elution", "detection": "SPR", "run_time": "2-3 hours"},
                    {"method": "Fc\u03b3 receptor binding panel", "purpose": "ADCC/CDC potential assessment", "column": "CM5 chip", "mobile_phase": "HBS-EP+", "detection": "SPR steady-state or kinetics", "run_time": "3-6 hours"},
                    {"method": "Concentration analysis", "purpose": "Active concentration by calibration-free method (CFCA)", "column": "CM5 chip with anti-target", "mobile_phase": "HBS-EP+", "detection": "SPR binding rate", "run_time": "1 hour"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Sensor chip type and immobilization method / level (RU)",
                    "Sensorgrams (overlay of concentrations)",
                    "Kinetic fitting model (1:1 Langmuir, bivalent, etc.)",
                    "Rate constants (ka, kd) and KD with chi\u00b2 / residuals",
                    "Steady-state analysis plot (if applicable)",
                    "Comparison to reference (for biosimilars)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Chi\u00b2 < 10% of Rmax", "Residuals < 2 RU", "Rmax within expected range", "Surface regeneration stability"],
                    "Quantitative Output": ["ka (1/Ms)", "kd (1/s)", "KD (nM or pM)", "Active concentration (nM)"],
                },
            },
            "regulatory_references": ["ICH Q6B", "FDA Biosimilar Guidance (binding kinetics as CQA)", "EMA Guideline on Similar Biological Medicinal Products"],
        },

        "Flow Cytometry": {
            "full_name": "Flow Cytometry / FACS",
            "principle": (
                "Single cells in suspension pass through one or more laser beams. Light scatter (forward scatter = size, "
                "side scatter = granularity) and fluorescence from bound antibodies or dyes are detected by photomultiplier tubes. "
                "Multi-parameter analysis (up to 40+ colors with spectral systems). FACS (Fluorescence-Activated Cell Sorting) "
                "physically sorts individual cells into collection tubes."
            ),
            "industry_models": [
                {"vendor": "BD Biosciences", "model": "FACSCanto II", "type": "2-laser, 8-color analyzer", "use": "Clinical immunophenotyping, QC"},
                {"vendor": "BD Biosciences", "model": "FACSLyric", "type": "3-laser, 12-color analyzer", "use": "GMP cell therapy QC"},
                {"vendor": "BD Biosciences", "model": "FACSAria III / Melody", "type": "Cell sorter", "use": "Single-cell cloning, FACS sorting"},
                {"vendor": "Beckman Coulter", "model": "CytoFLEX S", "type": "3-laser, 13-color analyzer", "use": "Research and process development"},
                {"vendor": "Cytek", "model": "Aurora (5-laser)", "type": "Spectral flow cytometer", "use": "Deep immunophenotyping, 40+ markers"},
                {"vendor": "Sony", "model": "ID7000", "type": "Spectral analyzer", "use": "High-parameter research"},
                {"vendor": "Miltenyi Biotec", "model": "MACSQuant Analyzer 16", "type": "3-laser, 16-color", "use": "Cell therapy process monitoring"},
            ],
            "methods_by_product": {
                "Cell & Gene Therapy": [
                    {"method": "T-cell immunophenotyping", "purpose": "CD3/CD4/CD8/CD45 subset analysis", "column": "N/A (tube/plate)", "mobile_phase": "Staining buffer (PBS + FBS)", "detection": "Multi-color fluorescence", "run_time": "1-2 hours (stain + acquire)"},
                    {"method": "Viability and apoptosis", "purpose": "Live/dead discrimination, early apoptosis", "column": "N/A", "mobile_phase": "Annexin V buffer", "detection": "7-AAD / Annexin V-FITC", "run_time": "30 min"},
                    {"method": "CAR expression", "purpose": "% CAR+ T cells", "column": "N/A", "mobile_phase": "Staining buffer + anti-CAR antibody or protein L", "detection": "Fluorescence", "run_time": "1 hour"},
                    {"method": "Intracellular cytokine staining", "purpose": "T-cell functionality (IFN-\u03b3, TNF-\u03b1, IL-2)", "column": "N/A", "mobile_phase": "Fix/Perm buffers + cytokine antibodies", "detection": "Multi-color fluorescence", "run_time": "6-8 hours (stimulation + staining)"},
                ],
                "Biologics Manufacturing": [
                    {"method": "Cell cycle analysis", "purpose": "Growth phase monitoring (G0/G1, S, G2/M)", "column": "N/A", "mobile_phase": "PI or DAPI staining solution", "detection": "DNA content fluorescence", "run_time": "1 hour"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Instrument configuration (lasers, filters, detectors)",
                    "Compensation matrix (for conventional flow cytometry)",
                    "Gating strategy with dot plots / histograms",
                    "Population statistics (% positive, MFI, cell count)",
                    "Viability results",
                    "QC bead results (daily instrument QC)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Laser alignment (QC beads CV < 3%)", "Sensitivity (MESF values)", "Compensation accuracy"],
                    "Quantitative Output": ["% Positive cells per marker", "Median Fluorescence Intensity (MFI)", "Absolute cell count (with counting beads)", "Viability %"],
                },
            },
            "regulatory_references": ["FDA Guidance on Potency Tests for Cell Therapy", "USP <1027> Flow Cytometry", "ISCT guidelines for cell therapy release testing"],
        },

        "qPCR / RT-qPCR": {
            "full_name": "Quantitative Real-Time PCR",
            "principle": (
                "PCR amplification of DNA/cDNA with real-time fluorescent detection each cycle. Fluorescence increases "
                "proportionally to amplicon amount. Quantification cycle (Cq or Ct) is inversely proportional to starting "
                "template amount. SYBR Green binds any dsDNA (non-specific). TaqMan probes are sequence-specific (hydrolysis "
                "probes with reporter + quencher). Standard curve or \u0394\u0394Ct methods for quantification."
            ),
            "industry_models": [
                {"vendor": "Thermo Fisher", "model": "QuantStudio 5", "type": "96/384-well qPCR", "use": "General qPCR, residual DNA"},
                {"vendor": "Thermo Fisher", "model": "QuantStudio 7 Pro", "type": "384-well qPCR", "use": "High-throughput, GMP-compatible"},
                {"vendor": "Bio-Rad", "model": "CFX96 Touch", "type": "96-well qPCR", "use": "Research and QC"},
                {"vendor": "Bio-Rad", "model": "CFX Opus 384", "type": "384-well qPCR", "use": "High-throughput screening"},
                {"vendor": "Roche", "model": "LightCycler 480 II", "type": "96/384-well qPCR", "use": "Clinical and pharma QC"},
                {"vendor": "Roche", "model": "LightCycler 96", "type": "96-well qPCR", "use": "Routine applications"},
            ],
            "methods_by_product": {
                "Biologics (General)": [
                    {"method": "Residual Host Cell DNA (qPCR)", "purpose": "Quantify residual CHO/E.coli/HEK DNA", "column": "N/A (PCR plate)", "mobile_phase": "TaqMan master mix + host-specific primers/probe", "detection": "FAM/VIC fluorescence", "run_time": "2 hours"},
                    {"method": "Mycoplasma Detection (qPCR)", "purpose": "Absence of mycoplasma contamination", "column": "N/A", "mobile_phase": "Commercial kit (MycoSEQ, Venor GeM)", "detection": "FAM fluorescence", "run_time": "2 hours"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "Vector Copy Number (VCN)", "purpose": "Transgene copies per cell genome", "column": "N/A", "mobile_phase": "TaqMan duplex (transgene + housekeeping gene)", "detection": "FAM + VIC", "run_time": "2 hours"},
                    {"method": "Replication-Competent Lentivirus (RCL)", "purpose": "Safety test for absence of RCL", "column": "N/A", "mobile_phase": "VSV-G-specific primers/probe", "detection": "TaqMan qPCR", "run_time": "2 hours (after cell culture amplification)"},
                    {"method": "Viral genome titer (qPCR)", "purpose": "vg/mL quantification for AAV", "column": "N/A", "mobile_phase": "ITR or transgene primers + DNase-treated sample", "detection": "SYBR Green or TaqMan", "run_time": "2 hours"},
                ],
                "Vaccines": [
                    {"method": "Residual DNA qPCR", "purpose": "Host cell DNA per dose", "column": "N/A", "mobile_phase": "Host-specific qPCR kit", "detection": "TaqMan", "run_time": "2 hours"},
                    {"method": "Viral clearance (spiking study)", "purpose": "Log reduction validation", "column": "N/A", "mobile_phase": "Virus-specific qPCR assay", "detection": "TaqMan", "run_time": "2 hours"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Standard curve (Ct vs log copy number/concentration)",
                    "Amplification efficiency (90-110%)",
                    "R\u00b2 of standard curve (> 0.99)",
                    "Melt curve analysis (SYBR Green)",
                    "Sample Ct values and calculated copy number/concentration",
                    "Positive and negative control results",
                    "NTC (no template control) result",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Efficiency: 90-110% (-3.6 < slope < -3.1)", "R\u00b2 > 0.99", "NTC: No amplification or Ct > 38", "Dynamic range (at least 5 logs)"],
                    "Quantitative Output": ["Ct (cycle threshold)", "Copy number (copies/\u00b5g DNA, copies/cell, vg/mL)", "pg DNA/dose", "Detected / Not Detected (qualitative)"],
                },
            },
            "regulatory_references": ["ICH Q6B", "WHO TRS 978 Annex 3 (residual DNA)", "USP <1130> Nucleic Acid-Based Techniques\u2014Amplification", "Ph. Eur. 2.6.21 NAT for Mycoplasma"],
        },

        "Octet BLI": {
            "full_name": "Bio-Layer Interferometry",
            "principle": (
                "A label-free optical technique that measures biomolecular interactions in real time. Biosensor tips coated "
                "with a capture molecule (e.g., Protein A, anti-human IgG Fc, streptavidin) are dipped into sample wells. "
                "Binding of analyte to the biosensor tip increases the optical thickness of the biolayer, causing a shift in "
                "the interference pattern of white light reflected from the tip surface. The wavelength shift (nm) is measured "
                "in real time to generate association and dissociation curves. Unlike SPR, BLI uses disposable tips and is "
                "insensitive to changes in refractive index of the bulk solution, making it ideal for crude samples."
            ),
            "industry_models": [
                {"vendor": "Sartorius", "model": "Octet RH16", "type": "16-channel high-throughput BLI", "use": "Kinetics, affinity, quantitation — mAb development and QC"},
                {"vendor": "Sartorius", "model": "Octet RH96", "type": "96-channel ultra-high-throughput BLI", "use": "Screening campaigns, titer determination at scale"},
                {"vendor": "Sartorius", "model": "Octet R8", "type": "8-channel BLI", "use": "Routine binding kinetics and concentration measurement"},
                {"vendor": "Sartorius", "model": "Octet R2", "type": "2-channel BLI", "use": "Low-throughput, dedicated kinetics studies"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "BLI kinetics (ka/kd/KD)", "purpose": "Binding affinity and kinetics of mAb-antigen interaction", "column": "N/A (biosensor tip: Anti-human IgG Fc, Protein A, or AHC)", "mobile_phase": "Kinetics buffer (PBS + 0.1% BSA + 0.02% Tween-20)", "detection": "White light interferometry (nm shift)", "run_time": "20-40 min per kinetic cycle"},
                    {"method": "BLI titer/concentration", "purpose": "Rapid IgG titer in cell culture harvest or in-process samples", "column": "N/A (Protein A biosensor tip)", "mobile_phase": "Sample diluted in kinetics buffer", "detection": "Initial binding rate correlated to concentration", "run_time": "3-5 min per sample"},
                    {"method": "BLI epitope binning", "purpose": "Competitive binding to classify mAbs into epitope bins", "column": "N/A (anti-human IgG Fc tips)", "mobile_phase": "Kinetics buffer", "detection": "BLI (sandwich or tandem format)", "run_time": "30-60 min per pair"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "BLI AAV receptor binding", "purpose": "Binding affinity of AAV capsid to cellular receptor", "column": "N/A (streptavidin or NiNTA tips with biotinylated/His-tagged receptor)", "mobile_phase": "Kinetics buffer", "detection": "BLI", "run_time": "30 min per cycle"},
                    {"method": "BLI AAV titer (AAVX biosensor)", "purpose": "Total capsid titer of AAV serotypes", "column": "N/A (AAV-X biosensor tips)", "mobile_phase": "Kinetics buffer", "detection": "BLI initial binding rate", "run_time": "5 min per sample"},
                ],
                "ADCs": [
                    {"method": "BLI antigen binding post-conjugation", "purpose": "Confirm antigen binding is retained after drug-linker conjugation", "column": "N/A (anti-human IgG Fc tips)", "mobile_phase": "Kinetics buffer", "detection": "BLI", "run_time": "30 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Sensorgrams (nm shift vs. time) for association and dissociation",
                    "Kinetic fit model (1:1, bivalent, heterogeneous ligand)",
                    "Kinetic constants: ka, kd, KD",
                    "Steady-state affinity plot (if equilibrium reached)",
                    "Standard curve for quantitation assays",
                    "R² of fit, chi² residuals",
                ],
                "key_parameters": {
                    "Performance Metrics": ["R² of kinetic fit (> 0.95)", "Residuals < 10% of max response", "Reference subtraction quality", "Positive control recovery"],
                    "Quantitative Output": ["ka (1/Ms)", "kd (1/s)", "KD (M)", "Concentration / titer (µg/mL or mg/mL)", "Epitope bin assignment"],
                },
            },
            "regulatory_references": ["ICH Q6B", "FDA Guidance on Biosimilar Analytical Studies", "ICH Q5E Comparability"],
        },

        "Cell-Based Potency Assay": {
            "full_name": "Cell-Based Potency / Bioassay",
            "principle": (
                "Measures the biological activity (potency) of a biologic drug product using living cells as the detection "
                "system. The assay quantifies a specific biological response — such as reporter gene activation, cell proliferation, "
                "cytotoxicity, neutralization, or signal transduction — induced by the drug product relative to a reference standard. "
                "Potency is expressed as a relative potency (%) compared to the reference standard using parallel line analysis (PLA) "
                "or four/five-parameter logistic (4PL/5PL) curve fitting. Cell-based bioassays are a regulatory requirement (ICH Q6B) "
                "for demonstrating that the drug product has the intended biological function."
            ),
            "industry_models": [
                {"vendor": "Promega", "model": "Lumit / GloResponse Reporter Cells", "type": "Bioluminescent reporter gene bioassays", "use": "MOA-reflective potency assays for mAbs, cytokines, checkpoint inhibitors"},
                {"vendor": "Eurofins DiscoverX", "model": "PathHunter / cAMP Hunter", "type": "Cell-based reporter assays", "use": "GPCR, kinase, and receptor signaling potency assays"},
                {"vendor": "ATCC / In-house", "model": "Custom cell lines (CHO, HEK293, TF-1, CTLL-2, A549)", "type": "Proliferation, cytotoxicity, neutralization assays", "use": "In-house validated GMP potency assays"},
                {"vendor": "Molecular Devices", "model": "SpectraMax iD5 / FlexStation 3", "type": "Multi-mode microplate reader", "use": "Luminescence, fluorescence, absorbance readout for bioassays"},
                {"vendor": "BMG Labtech", "model": "CLARIOstar Plus", "type": "Multi-mode microplate reader", "use": "High-sensitivity luminescence for reporter gene assays"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "Reporter gene bioassay (MOA-based)", "purpose": "Potency determination reflecting mechanism of action (e.g., target binding → NFAT/NF-κB/STAT reporter activation)", "column": "N/A (96-well or 384-well plate)", "mobile_phase": "Cell culture medium (RPMI/DMEM + FBS)", "detection": "Luminescence (luciferase reporter)", "run_time": "16-24 hours (overnight incubation)"},
                    {"method": "Proliferation bioassay", "purpose": "Potency via target cell growth inhibition or stimulation", "column": "N/A (96-well plate)", "mobile_phase": "Growth medium", "detection": "CellTiter-Glo (ATP luminescence) or MTT/MTS absorbance", "run_time": "48-72 hours"},
                ],
                "Vaccines": [
                    {"method": "Virus neutralization assay", "purpose": "Potency of vaccine-induced antibody response (or vaccine antigen activity)", "column": "N/A (96-well plate, Vero or MDCK cells)", "mobile_phase": "Cell culture medium + virus challenge", "detection": "CPE observation, plaque count, or reporter virus luminescence", "run_time": "48-120 hours"},
                    {"method": "Antigen potency (in vitro)", "purpose": "Antigen biological activity (e.g., receptor binding, hemagglutination inhibition)", "column": "N/A", "mobile_phase": "Appropriate buffer/medium", "detection": "ELISA, hemagglutination, or cell-based readout", "run_time": "4-24 hours"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "CAR-T cytotoxicity assay", "purpose": "Potency of CAR-T cells via target cell killing", "column": "N/A (96-well plate, co-culture format)", "mobile_phase": "T-cell medium + target cells (e.g., Raji, Nalm-6)", "detection": "Luminescence (luciferase-expressing target cells) or flow cytometry", "run_time": "4-24 hours"},
                    {"method": "Gene therapy transgene expression", "purpose": "Potency via functional transgene expression in target cells", "column": "N/A", "mobile_phase": "Cell culture medium + AAV/LV vector", "detection": "Reporter (GFP fluorescence, luciferase) or functional readout", "run_time": "48-72 hours"},
                ],
                "Cytokines / Growth Factors": [
                    {"method": "Proliferation bioassay", "purpose": "Potency via dose-dependent proliferation of factor-dependent cells (TF-1, CTLL-2)", "column": "N/A (96-well plate)", "mobile_phase": "Growth medium (factor-depleted)", "detection": "CellTiter-Glo or [³H]-thymidine incorporation", "run_time": "48-72 hours"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Dose-response curves (sample and reference standard)",
                    "4PL/5PL curve fit parameters and goodness-of-fit",
                    "Relative potency (%) with confidence interval",
                    "Parallelism assessment (F-test or equivalence test)",
                    "System suitability (reference standard EC50 range, Hill slope, max/min response)",
                    "Cell passage number and viability at plating",
                    "Plate layout and raw data",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Reference standard EC50 within historical range", "Hill slope consistency", "Parallelism (p-value or equivalence criteria)", "Assay signal window (S/B > 5)", "%CV of replicates < 20%"],
                    "Quantitative Output": ["Relative potency (%)", "95% confidence interval", "EC50 (ng/mL)", "Hill slope", "Upper/lower asymptote"],
                },
                "acceptance_criteria_examples": {
                    "mAb potency": {"Relative potency": "50-200% (typical lot release)", "Parallelism": "Met (F-test p > 0.05 or equivalence within ± 25%)", "Reference standard EC50": "Within ± 30% of historical mean"},
                },
            },
            "regulatory_references": ["ICH Q6B Specifications for Biologicals (potency requirement)", "USP <1032> Design and Development of Biological Assays", "USP <1033> Biological Assay Validation", "USP <1034> Analysis of Biological Assays", "Ph. Eur. 5.3 Statistical Analysis of Results of Biological Assays"],
        },

        "ADCC / CDC Bioassay": {
            "full_name": "Antibody-Dependent Cellular Cytotoxicity / Complement-Dependent Cytotoxicity Bioassay",
            "principle": (
                "ADCC: Measures the ability of an antibody to engage Fc gamma receptors (FcγRIIIa/CD16a) on effector cells "
                "(typically NK cells or engineered Jurkat reporter cells) after binding to antigen-expressing target cells, "
                "leading to target cell lysis or reporter gene activation. ADCC is critical for mAbs with Fc-mediated killing "
                "as part of their mechanism of action (e.g., anti-CD20, anti-HER2). "
                "CDC: Measures the ability of an antibody bound to target cells to activate the classical complement cascade "
                "(via C1q binding), resulting in membrane attack complex formation and target cell lysis. "
                "Both assays are required by ICH Q6B when Fc effector function is part of the mechanism of action."
            ),
            "industry_models": [
                {"vendor": "Promega", "model": "ADCC Reporter Bioassay (Jurkat/FcγRIIIa-NFAT-Luc)", "type": "Reporter gene ADCC assay", "use": "MOA-reflective ADCC potency — standardized, GMP-compatible"},
                {"vendor": "Promega", "model": "ADCC Reporter Bioassay, V158 (high affinity) variant", "type": "V158 FcγRIIIa reporter", "use": "Enhanced sensitivity for afucosylated mAbs"},
                {"vendor": "Promega", "model": "CDC Reporter Bioassay", "type": "Reporter gene CDC assay", "use": "C1q-dependent complement activation assay"},
                {"vendor": "In-house / CRO", "model": "PBMC-based ADCC (LDH release or Calcein AM)", "type": "Primary cell ADCC", "use": "Physiological ADCC with donor NK cells (higher variability)"},
                {"vendor": "In-house / CRO", "model": "CDC lysis assay (complement + target cells)", "type": "Complement-mediated lysis", "use": "Classical CDC assay with human serum complement"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "ADCC reporter bioassay", "purpose": "Fc effector function potency — FcγRIIIa engagement → NFAT-luciferase activation", "column": "N/A (96-well plate, target + effector cells)", "mobile_phase": "Assay medium (RPMI + low-IgG FBS)", "detection": "Luminescence (Bio-Glo luciferase)", "run_time": "6 hours (thaw effector cells, 6h co-culture)"},
                    {"method": "ADCC primary cell killing assay", "purpose": "Direct target cell lysis by NK cells (physiological ADCC)", "column": "N/A (96-well plate)", "mobile_phase": "RPMI + 10% FBS", "detection": "LDH release (absorbance 490 nm) or Calcein AM fluorescence", "run_time": "4-6 hours co-culture"},
                    {"method": "CDC cytotoxicity assay", "purpose": "Complement-dependent lysis of target cells", "column": "N/A (96-well plate, target cells + human complement)", "mobile_phase": "RPMI + human serum or purified complement", "detection": "CellTiter-Glo, LDH release, or PI uptake (flow cytometry)", "run_time": "1-4 hours"},
                ],
                "Biosimilars": [
                    {"method": "ADCC/CDC comparative potency", "purpose": "Demonstrate equivalent Fc effector function vs. reference product", "column": "N/A (96-well plate)", "mobile_phase": "Assay medium", "detection": "Luminescence (reporter) or LDH/ATP (killing)", "run_time": "4-6 hours"},
                ],
                "ADCs": [
                    {"method": "ADCC/CDC post-conjugation", "purpose": "Confirm Fc effector function is retained or intentionally ablated after conjugation", "column": "N/A", "mobile_phase": "Assay medium", "detection": "Luminescence or cytotoxicity readout", "run_time": "4-6 hours"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Dose-response curves (sample and reference standard)",
                    "Relative potency (%) with 95% confidence interval",
                    "Parallelism assessment (sample vs. reference curves)",
                    "Target cell antigen expression verification (flow cytometry)",
                    "Effector-to-target (E:T) ratio",
                    "System suitability (reference standard EC50, max fold induction, signal window)",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Reference standard EC50 within historical range", "Fold induction (reporter) or % max lysis (killing) > threshold", "Parallelism met", "%CV of replicates < 25%"],
                    "Quantitative Output": ["Relative potency (%)", "95% confidence interval", "EC50 (µg/mL)", "Max fold induction (reporter) or % max lysis (killing)", "Hill slope"],
                },
                "acceptance_criteria_examples": {
                    "mAb ADCC": {"Relative potency": "40-250% (lot release, wider range for cell-based)", "Reference EC50": "Within historical range", "Fold induction": "≥ 3-fold over no-antibody control"},
                    "mAb CDC": {"Relative potency": "50-200%", "Max lysis": "≥ 30% at saturating concentration"},
                },
            },
            "regulatory_references": ["ICH Q6B Specifications for Biologicals", "USP <1032>/<1033>/<1034> Biological Assay Design, Validation, and Analysis", "FDA Guidance on Biosimilar Analytical Studies (functional assays)", "EMA Guideline on Similar Biological Medicinal Products (Fc effector function)"],
        },
    },

    # =========================================================================
    # PARTICLE & PHYSICAL CHARACTERIZATION
    # =========================================================================
    "Particle & Physical Characterization": {
        "DLS": {
            "full_name": "Dynamic Light Scattering",
            "principle": (
                "Measures the Brownian motion of particles/macromolecules in solution by analyzing time-dependent fluctuations "
                "in scattered laser light intensity. The autocorrelation function is used to calculate diffusion coefficients, "
                "which are converted to hydrodynamic diameter via the Stokes-Einstein equation. Reports Z-average diameter "
                "and polydispersity index (PDI). Best for monodisperse particles 1 nm to 10 \u00b5m."
            ),
            "industry_models": [
                {"vendor": "Malvern Panalytical", "model": "Zetasizer Ultra", "type": "DLS + ELS + MADLS", "use": "Protein aggregation, nanoparticle sizing, zeta potential"},
                {"vendor": "Malvern Panalytical", "model": "Zetasizer Pro", "type": "DLS + ELS", "use": "Routine QC particle sizing"},
                {"vendor": "Wyatt Technology", "model": "DynaPro Plate Reader III", "type": "High-throughput DLS", "use": "384-well formulation screening"},
                {"vendor": "Wyatt Technology", "model": "DynaPro NanoStar", "type": "Batch DLS", "use": "Cuvette-based protein DLS"},
                {"vendor": "Anton Paar", "model": "Litesizer 500", "type": "DLS + ELS", "use": "General nanoparticle analysis"},
            ],
            "methods_by_product": {
                "Biologics (Protein Formulation)": [
                    {"method": "DLS batch measurement", "purpose": "Hydrodynamic size and polydispersity", "column": "N/A (cuvette)", "mobile_phase": "Formulation buffer", "detection": "633 nm laser, backscatter 173\u00b0", "run_time": "5-10 min"},
                    {"method": "DLS thermal ramp", "purpose": "Aggregation onset temperature (Tagg)", "column": "N/A", "mobile_phase": "Buffer", "detection": "DLS vs temperature", "run_time": "60-120 min"},
                ],
                "LNPs / Nanoparticles": [
                    {"method": "DLS size + PDI", "purpose": "Particle size distribution of LNPs, liposomes, VLPs", "column": "N/A (cuvette, diluted sample)", "mobile_phase": "PBS or water", "detection": "DLS + ELS (zeta potential)", "run_time": "5 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Z-average diameter (nm) and PDI",
                    "Size distribution by intensity (and volume/number if needed)",
                    "Correlogram quality check",
                    "Zeta potential (mV) if measured",
                    "Temperature and viscosity used in calculation",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Correlogram intercept (> 0.85)", "Baseline stability", "Repeat measurement %CV < 2%"],
                    "Quantitative Output": ["Z-average diameter (nm)", "PDI (< 0.1 monodisperse, < 0.3 moderate, > 0.5 polydisperse)", "Zeta potential (mV)", "Tagg (\u00b0C)"],
                },
            },
            "regulatory_references": ["ICH Q6B", "FDA Guidance on Liposome Drug Products", "ISO 22412 DLS", "USP <729> Globule Size Distribution (parenteral emulsions)"],
        },

        "DSC": {
            "full_name": "Differential Scanning Calorimetry",
            "principle": (
                "Measures the heat flow difference between sample and reference as a function of temperature. "
                "As a protein unfolds (endothermic transition), it absorbs heat, producing a peak in the thermogram. "
                "The melting temperature (Tm) is the peak maximum; the onset temperature (Tonset) indicates initial unfolding. "
                "Enthalpy of unfolding (\u0394H) reflects the degree of structural cooperativity. "
                "Multi-domain proteins (e.g., mAbs) show multiple Tm peaks (CH2, Fab, CH3)."
            ),
            "industry_models": [
                {"vendor": "Malvern Panalytical", "model": "MicroCal VP-Capillary DSC", "type": "Capillary DSC", "use": "Automated protein stability, biosimilar HOS"},
                {"vendor": "Malvern Panalytical", "model": "MicroCal PEAQ-DSC", "type": "Capillary DSC", "use": "Low volume, high sensitivity"},
                {"vendor": "TA Instruments", "model": "Nano DSC", "type": "Capillary DSC", "use": "Protein thermal stability"},
                {"vendor": "TA Instruments", "model": "DSC 2500", "type": "Standard DSC", "use": "Excipient, polymer, small molecule Tm/Tg"},
                {"vendor": "Mettler Toledo", "model": "DSC 3+", "type": "Standard DSC", "use": "Glass transition, melting, polymorphism of solids"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs) / Biosimilars": [
                    {"method": "DSC thermal scan", "purpose": "Tm determination, thermal stability ranking", "column": "N/A (capillary cell, ~300 \u00b5L)", "mobile_phase": "Formulation buffer", "detection": "Heat capacity vs temperature", "run_time": "60-90 min (25-95\u00b0C at 1\u00b0C/min)"},
                    {"method": "DSC comparability", "purpose": "Biosimilar HOS comparison (Tm overlay)", "column": "N/A", "mobile_phase": "Matched formulation buffer", "detection": "Overlay of thermograms", "run_time": "60-90 min"},
                ],
                "Small Molecule APIs": [
                    {"method": "DSC melting point / polymorphism", "purpose": "Melting point, polymorph screening, glass transition (Tg)", "column": "N/A (hermetic pan, 2-10 mg)", "mobile_phase": "N/A (solid sample)", "detection": "Heat flow vs temperature", "run_time": "30-60 min"},
                ],
                "Excipients / Formulation": [
                    {"method": "DSC Tg measurement", "purpose": "Glass transition of lyophilized cake", "column": "N/A (crimped pan)", "mobile_phase": "N/A", "detection": "Heat flow", "run_time": "30-60 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Thermogram (Cp vs Temperature)",
                    "Tm values (onset and peak maximum)",
                    "\u0394H (enthalpy of unfolding) in kcal/mol or kJ/mol",
                    "Reversibility assessment (rescan)",
                    "Overlay with reference (for comparability)",
                    "Baseline subtraction method",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Baseline stability", "Buffer-buffer reproducibility", "Scan rate consistency"],
                    "Quantitative Output": ["Tm1, Tm2, Tm3 (\u00b0C) for multi-domain proteins", "Tonset (\u00b0C)", "\u0394H (kcal/mol)", "Tg (\u00b0C) for amorphous solids"],
                },
            },
            "regulatory_references": ["ICH Q6B", "ICH Q6A (for polymorphism)", "FDA Biosimilar HOS Guidance", "USP <891> Thermal Analysis"],
        },

        "SEC-MALS": {
            "full_name": "Size-Exclusion Chromatography with Multi-Angle Light Scattering",
            "principle": (
                "SEC separates by hydrodynamic size. MALS detector measures scattered light at multiple angles simultaneously "
                "to determine absolute molar mass (independent of column calibration or shape). Combined with UV and RI detectors, "
                "enables characterization of conjugated proteins (PEGylated, ADCs, glycoproteins) where mass and elution volume "
                "are not simply correlated. Also determines Rg (radius of gyration) for larger particles."
            ),
            "industry_models": [
                {"vendor": "Wyatt Technology", "model": "DAWN MALS", "type": "18-angle MALS", "use": "Absolute MW determination, protein aggregation"},
                {"vendor": "Wyatt Technology", "model": "miniDAWN", "type": "3-angle MALS", "use": "Routine SEC-MALS"},
                {"vendor": "Wyatt Technology", "model": "Optilab RI detector", "type": "dRI detector", "use": "Paired with MALS for dn/dc-based mass"},
                {"vendor": "Malvern Panalytical", "model": "OMNISEC", "type": "Integrated SEC-MALS-Visc-RI", "use": "Complete polymer/protein characterization"},
                {"vendor": "Tosoh", "model": "LenS3 MALS", "type": "MALS detector", "use": "Inline with any HPLC/SEC"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "SEC-MALS", "purpose": "Absolute MW of monomer, dimer, HMW species", "column": "TSKgel G3000SWxl or Superose 6", "mobile_phase": "PBS + 200 mM NaCl", "detection": "UV 280 nm + MALS + dRI", "run_time": "30 min"},
                ],
                "ADCs / PEGylated Proteins": [
                    {"method": "SEC-MALS with UV/RI/MALS", "purpose": "Protein conjugate MW, DAR, PEG content", "column": "TSKgel G3000SWxl", "mobile_phase": "PBS", "detection": "UV + MALS + dRI (protein conjugate analysis)", "run_time": "30-45 min"},
                ],
                "Viral Vectors / VLPs / LNPs": [
                    {"method": "SEC-MALS for particle characterization", "purpose": "Particle MW, aggregation, Rg", "column": "SRT SEC-1000 or Superose 6 Increase", "mobile_phase": "PBS", "detection": "MALS + UV 260/280 + dRI", "run_time": "30-60 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Molar mass vs elution volume plot (Debye plot)",
                    "UV + MALS + RI chromatogram overlay",
                    "Calculated molar mass for each peak (monomer, dimer, HMW)",
                    "dn/dc value used (typically 0.185 for proteins)",
                    "Rg values for larger species",
                    "Mass recovery calculation",
                ],
                "key_parameters": {
                    "Performance Metrics": ["MALS detector normalization", "BSA check standard MW (66.5 kDa \u00b1 3%)", "RI and UV baseline stability"],
                    "Quantitative Output": ["Absolute Mw (Da)", "Mn, Mw, Mz", "Dispersity (Mw/Mn)", "Rg (nm) for particles > 10 nm"],
                },
            },
            "regulatory_references": ["ICH Q6B", "USP <621>", "FDA Guidance on Biosimilar Analytical Studies"],
        },

        "NTA": {
            "full_name": "Nanoparticle Tracking Analysis",
            "principle": (
                "Visualizes and tracks individual nanoparticles in solution using a laser-illuminated sample chamber and "
                "a high-sensitivity camera. Each particle scatters light and is tracked frame-by-frame to measure its Brownian "
                "motion. The Stokes-Einstein equation converts the diffusion coefficient of each tracked particle into its "
                "hydrodynamic diameter. Unlike DLS (which gives ensemble averages), NTA provides particle-by-particle sizing "
                "and direct concentration measurement (particles/mL). Scatter and fluorescence modes enable differentiation "
                "of labeled vs. unlabeled populations (e.g., AAV full vs. empty capsids with fluorescent DNA intercalators)."
            ),
            "industry_models": [
                {"vendor": "Malvern Panalytical", "model": "NanoSight Pro", "type": "NTA with fluorescence capability", "use": "AAV full/empty ratio, exosome sizing and counting, VLP characterization"},
                {"vendor": "Malvern Panalytical", "model": "NanoSight NS300", "type": "NTA (legacy, widely installed)", "use": "Nanoparticle sizing and concentration measurement"},
                {"vendor": "Particle Metrix", "model": "ZetaView TWIN", "type": "NTA + zeta potential", "use": "Size, concentration, and zeta potential of nanoparticles and EVs"},
                {"vendor": "Particle Metrix", "model": "ZetaView QUATT", "type": "4-laser NTA", "use": "Multi-wavelength fluorescence NTA for heterogeneous populations"},
            ],
            "methods_by_product": {
                "Cell & Gene Therapy (AAV)": [
                    {"method": "NTA scatter mode — total particle count", "purpose": "Total AAV capsid concentration (particles/mL)", "column": "N/A (flow cell, ~500 µL)", "mobile_phase": "PBS or formulation buffer (filtered 0.02 µm)", "detection": "Scatter mode (405, 488, or 532 nm laser)", "run_time": "5-10 min (5 x 60s captures)"},
                    {"method": "NTA fluorescence mode — full capsid counting", "purpose": "AAV full/empty ratio by fluorescent DNA labeling (SYBR Gold or SYTO dye)", "column": "N/A (flow cell)", "mobile_phase": "PBS + fluorescent DNA intercalator", "detection": "Fluorescence mode (488 or 532 nm excitation)", "run_time": "10-15 min"},
                ],
                "Vaccines / VLPs": [
                    {"method": "NTA VLP sizing and concentration", "purpose": "Particle size distribution and total particle count of VLP preparations", "column": "N/A (flow cell)", "mobile_phase": "PBS", "detection": "Scatter mode", "run_time": "5-10 min"},
                ],
                "Exosomes / Extracellular Vesicles": [
                    {"method": "NTA EV characterization", "purpose": "Size distribution and concentration of exosomes/EVs (50-200 nm range)", "column": "N/A (flow cell)", "mobile_phase": "Particle-free PBS", "detection": "Scatter ± fluorescence (labeled surface markers)", "run_time": "5-10 min"},
                ],
                "LNPs": [
                    {"method": "NTA LNP particle count", "purpose": "Total LNP particle concentration and size distribution", "column": "N/A (flow cell)", "mobile_phase": "PBS or Tris buffer", "detection": "Scatter mode", "run_time": "5-10 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Particle size distribution histogram (number-weighted)",
                    "Mean, mode, and D10/D50/D90 diameters (nm)",
                    "Total particle concentration (particles/mL)",
                    "Video screenshot showing tracked particles",
                    "Fluorescence vs. scatter particle counts (for full/empty ratio)",
                    "Camera level, detection threshold, and analysis settings",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Particles per frame (20-100 optimal)", "Minimum track length (≥ 5 frames)", "Concentration linearity range (10⁷ – 10⁹ particles/mL)", "Polystyrene bead size standard verification (100 nm ± 5 nm)"],
                    "Quantitative Output": ["Mean diameter (nm)", "Mode diameter (nm)", "D10, D50, D90 (nm)", "Particle concentration (particles/mL)", "Full/empty ratio (%) — fluorescence/scatter"],
                },
            },
            "regulatory_references": ["ICH Q6B", "FDA Guidance on AAV-Based Gene Therapy Products", "USP <788> Particulate Matter (sub-visible context)", "ISO 19430 NTA method"],
        },

        "MFI": {
            "full_name": "Micro-Flow Imaging",
            "principle": (
                "A flow imaging microscopy technique that captures digital images of every particle in a flowing sample as "
                "it passes through a precisely controlled flow cell illuminated by a high-intensity LED. Particles from "
                "approximately 1 µm to 300 µm are individually imaged, sized, and counted. Image analysis software classifies "
                "particles by morphological features (circularity, aspect ratio, intensity, transparency) to distinguish protein "
                "aggregates, silicone oil droplets, air bubbles, glass flakes, and fibers. Provides both particle counts (like "
                "light obscuration per USP <788>) and morphological identification in a single measurement."
            ),
            "industry_models": [
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "MFI 5200", "type": "Micro-Flow Imaging particle analyzer", "use": "Subvisible particle characterization for biologics, ICH Q6B"},
                {"vendor": "ProteinSimple (Bio-Techne)", "model": "MFI 5100", "type": "Micro-Flow Imaging (legacy)", "use": "Subvisible particle counting and morphology"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "MFI subvisible particle analysis", "purpose": "Count and characterize subvisible particles (2-100 µm), distinguish protein aggregates from extrinsic particles", "column": "N/A (flow cell, 100 µm or 400 µm depth)", "mobile_phase": "Formulation buffer (matched refractive index blank)", "detection": "Brightfield imaging (LED illumination, high-speed camera)", "run_time": "3-5 min per 0.5 mL sample"},
                    {"method": "MFI silicone oil differentiation", "purpose": "Distinguish silicone oil droplets (from PFS) from protein aggregates based on morphology", "column": "N/A (flow cell)", "mobile_phase": "Formulation buffer", "detection": "MFI image analysis (circularity, intensity)", "run_time": "3-5 min"},
                ],
                "Biologics (General Parenteral)": [
                    {"method": "MFI extended characterization", "purpose": "Comprehensive subvisible particle characterization as complement to USP <788> light obscuration", "column": "N/A (flow cell)", "mobile_phase": "Product buffer or particle-free water", "detection": "Brightfield imaging", "run_time": "3-5 min"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "MFI for vector/cell therapy products", "purpose": "Subvisible particle profiling in complex matrices", "column": "N/A (flow cell, 400 µm depth for viscous samples)", "mobile_phase": "Formulation buffer", "detection": "Brightfield imaging", "run_time": "5 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Particle count per mL in size bins (≥ 2 µm, ≥ 5 µm, ≥ 10 µm, ≥ 25 µm)",
                    "Particle images gallery (representative images per category)",
                    "Morphological classification (protein aggregate, silicone oil, air bubble, fiber, other)",
                    "Size distribution histogram (equivalent circular diameter)",
                    "Comparison to USP <788> / <787> limits",
                    "Buffer blank subtraction results",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Count accuracy (NIST traceable size standards)", "Buffer blank (< 50 particles/mL ≥ 2 µm)", "Flow cell cleanliness verification", "Optimize illumination (consistent image quality)"],
                    "Quantitative Output": ["Particles/mL (≥ 2 µm, ≥ 5 µm, ≥ 10 µm, ≥ 25 µm)", "ECD — equivalent circular diameter (µm)", "Circularity", "Aspect ratio", "Intensity mean/StdDev"],
                },
                "acceptance_criteria_examples": {
                    "Parenteral (per USP <788>)": {"≥ 10 µm": "≤ 6000 particles per container", "≥ 25 µm": "≤ 600 particles per container"},
                },
            },
            "regulatory_references": ["ICH Q6B", "USP <787> Subvisible Particulate Matter in Therapeutic Protein Injections", "USP <788> Particulate Matter in Injections", "USP <1787> Measurement of Subvisible Particulate Matter", "FDA Guidance on Immunogenicity of Therapeutic Protein Products (aggregates)"],
        },

        "AUC": {
            "full_name": "Analytical Ultracentrifugation",
            "principle": (
                "Applies centrifugal force to a solution containing macromolecules and monitors their sedimentation behavior "
                "in real time using absorbance or interference optics. Two primary modes: "
                "(1) Sedimentation Velocity (SV-AUC) — measures the rate of sedimentation to determine sedimentation coefficient (s), "
                "diffusion coefficient, and frictional ratio. Resolves distinct species (monomer, dimer, oligomers, aggregates) "
                "in a first-principles, matrix-free manner without columns or surfaces. "
                "(2) Sedimentation Equilibrium (SE-AUC) — at lower speeds, sedimentation and diffusion reach equilibrium; "
                "the concentration gradient yields absolute molar mass. "
                "Considered the gold standard for oligomeric state characterization because it operates in free solution "
                "without stationary phases, surfaces, or standards — no interaction artifacts."
            ),
            "industry_models": [
                {"vendor": "Beckman Coulter", "model": "Optima AUC", "type": "Analytical ultracentrifuge (absorbance + interference)", "use": "Gold standard for oligomeric state, aggregate quantification, biosimilar comparability"},
                {"vendor": "Beckman Coulter", "model": "ProteomeLab XL-I (legacy)", "type": "Analytical ultracentrifuge", "use": "Widely published reference instrument (predecessor to Optima AUC)"},
                {"vendor": "Nanolytics", "model": "multiwavelength AUC (MWL-AUC) upgrade", "type": "Multiwavelength detector for Optima AUC", "use": "Spectral deconvolution of complex mixtures (protein + DNA, ADCs)"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "SV-AUC", "purpose": "Quantify monomer, dimer, HMW aggregates, and fragments in free solution", "column": "N/A (12 mm double-sector centerpieces, sapphire/quartz windows)", "mobile_phase": "Formulation buffer or PBS", "detection": "Absorbance 280 nm and/or Rayleigh interference", "run_time": "6-10 hours (45,000 rpm, 200 scans)"},
                    {"method": "SE-AUC", "purpose": "Absolute molar mass and stoichiometry of self-association", "column": "N/A (6-channel equilibrium centerpieces)", "mobile_phase": "Formulation buffer", "detection": "Absorbance 280 nm and/or interference", "run_time": "24-72 hours (multi-speed)"},
                ],
                "Biosimilars": [
                    {"method": "SV-AUC comparative", "purpose": "Orthogonal aggregation comparison vs. reference product (matrix-free)", "column": "N/A", "mobile_phase": "Matched formulation buffer", "detection": "Absorbance + interference", "run_time": "6-10 hours"},
                ],
                "ADCs": [
                    {"method": "SV-AUC for ADC", "purpose": "Resolve drug-loaded species and aggregation state without column interactions", "column": "N/A (double-sector centerpieces)", "mobile_phase": "Formulation buffer", "detection": "Absorbance (280 nm protein + drug wavelength) or MWL-AUC", "run_time": "6-10 hours"},
                ],
                "Cell & Gene Therapy (AAV)": [
                    {"method": "SV-AUC full/empty capsid", "purpose": "Gold-standard quantification of full, partial, and empty AAV capsids based on sedimentation coefficient differences", "column": "N/A (double-sector centerpieces)", "mobile_phase": "PBS or formulation buffer", "detection": "Absorbance 260/280 nm (DNA/protein ratio per species)", "run_time": "4-6 hours (12,000-15,000 rpm for large particles)"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "c(s) distribution plot (sedimentation coefficient distribution)",
                    "Main species sedimentation coefficient (s₂₀,w in Svedbergs)",
                    "% Area of each resolved species (monomer, dimer, HMW, fragments)",
                    "Frictional ratio (f/f₀) indicating shape",
                    "Residual bitmap and RMSD of fit",
                    "Loading concentration and absorbance/interference raw data quality",
                    "For AAV: % Full, % Partial, % Empty based on s-value integration",
                ],
                "key_parameters": {
                    "Performance Metrics": ["RMSD of c(s) fit (< 0.005 OD for absorbance)", "Residual bitmap (random, no systematic patterns)", "BSA reference standard s₂₀,w = 4.3 S ± 0.1", "Loading concentration (OD 0.3-1.0 for absorbance)"],
                    "Quantitative Output": ["s₂₀,w (Svedbergs) per species", "% Monomer, % Dimer, % HMW, % LMW", "Frictional ratio (f/f₀)", "Molar mass from SE-AUC (Da)", "% Full / % Empty capsid (AAV)"],
                },
                "acceptance_criteria_examples": {
                    "mAb SV-AUC": {"Monomer (6.6 S)": "≥ 95%", "Dimer (~9 S)": "≤ 3%", "HMW (>10 S)": "≤ 2%"},
                    "AAV SV-AUC": {"Full capsid (≈ 60-80 S depending on serotype)": "Report %", "Empty capsid (≈ 50-65 S)": "Report %"},
                },
            },
            "regulatory_references": ["ICH Q6B Specifications for Biologicals", "FDA Guidance on Biosimilar Analytical Studies (orthogonal aggregation method)", "FDA Guidance on AAV-Based Gene Therapy Products", "ICH Q5E Comparability"],
        },
    },

    # =========================================================================
    # CELL-BASED & MICROBIOLOGICAL
    # =========================================================================
    "Cell-Based & Microbiological": {
        "Bioprocess Analyzers": {
            "full_name": "Bioprocess / Biochemistry Analyzers",
            "principle": (
                "Automated analysis of key metabolites and nutrients in cell culture and fermentation samples. "
                "Uses biosensor technology (enzyme electrodes) for glucose, lactate, glutamine, glutamate, ammonia, "
                "and others. Electrochemical detection via immobilized oxidase/dehydrogenase enzymes. "
                "Some systems include ion-selective electrodes (Na+, K+, Ca2+, pH, pCO2, pO2) and osmolality."
            ),
            "industry_models": [
                {"vendor": "Nova Biomedical", "model": "BioProfile FLEX2", "type": "Multi-analyte analyzer", "use": "CHO/HEK cell culture monitoring (gold standard)"},
                {"vendor": "Nova Biomedical", "model": "BioProfile CDV", "type": "Cell density + chemistry", "use": "Combined VCD and metabolite analysis"},
                {"vendor": "Roche (now Siemens)", "model": "Cedex Bio HT", "type": "Automated chemistry analyzer", "use": "High-throughput metabolite panels"},
                {"vendor": "YSI (Xylem)", "model": "YSI 2900D", "type": "Biochemistry analyzer", "use": "Glucose/lactate, simple and reliable"},
                {"vendor": "Beckman Coulter", "model": "Vi-CELL MetaFLEX", "type": "Metabolite + cell counter", "use": "Combined chemistry and cell counting"},
                {"vendor": "Randox", "model": "RX Imola", "type": "Clinical chemistry analyzer", "use": "Custom analyte panels for bioprocess"},
            ],
            "methods_by_product": {
                "Cell Culture (mAbs, Recombinant Proteins)": [
                    {"method": "Metabolite Panel", "purpose": "Glucose, lactate, glutamine, glutamate, NH4+", "column": "N/A (direct sample)", "mobile_phase": "N/A", "detection": "Biosensor (enzyme electrode)", "run_time": "2-5 min/sample"},
                    {"method": "Blood Gas Panel", "purpose": "pH, pCO2, pO2, Na+, K+, Ca2+, osmolality", "column": "N/A", "mobile_phase": "N/A", "detection": "Ion-selective electrode / osmometer", "run_time": "2 min/sample"},
                    {"method": "IgG titer (turbidimetric)", "purpose": "Quick IgG titer estimate", "column": "N/A", "mobile_phase": "Anti-human IgG reagent", "detection": "Turbidimetric / nephelometric", "run_time": "5 min"},
                ],
                "Fermentation (Microbial)": [
                    {"method": "Glucose + Ethanol + Acetate", "purpose": "Carbon source and metabolite tracking", "column": "N/A", "mobile_phase": "N/A", "detection": "Biosensor", "run_time": "2-5 min/sample"},
                    {"method": "Ammonia + Phosphate", "purpose": "Nitrogen and phosphorus depletion monitoring", "column": "N/A", "mobile_phase": "N/A", "detection": "Biosensor / colorimetric", "run_time": "3 min/sample"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Analyte concentrations at each time point",
                    "Trend plots (analyte vs. culture time)",
                    "Specific rates (qGlc, qLac, qGln, qNH4) when paired with VCD",
                    "Calibration verification (QC sample results)",
                    "Instrument maintenance / membrane replacement log",
                ],
                "key_parameters": {
                    "Performance Metrics": ["QC sample recovery (90-110%)", "Linearity of calibration", "Membrane/sensor lifetime tracking"],
                    "Quantitative Output": ["Glucose (g/L)", "Lactate (g/L)", "Glutamine (mmol/L)", "Glutamate (mmol/L)", "NH4+ (mmol/L)", "pH", "pCO2 (mmHg)", "Osmolality (mOsm/kg)"],
                },
            },
            "regulatory_references": ["ICH Q5E Comparability", "FDA Process Validation Guidance", "EMA Guideline on Process Validation"],
        },

        "Cell Counters": {
            "full_name": "Automated Cell Counters & Viability Analyzers",
            "principle": (
                "Automated systems for counting cells and determining viability. Trypan blue exclusion (dead cells stain blue, "
                "live cells exclude dye) is the most common method — automated image analysis replaces manual hemocytometer counting. "
                "Electrical impedance (Coulter principle) counts cells by resistance change as they pass through an aperture. "
                "Fluorescence-based methods use DNA-binding dyes for viability discrimination."
            ),
            "industry_models": [
                {"vendor": "Beckman Coulter", "model": "Vi-CELL BLU", "type": "Trypan blue image analysis", "use": "Industry standard for CHO/HEK VCD"},
                {"vendor": "Beckman Coulter", "model": "Vi-CELL MetaFLEX", "type": "Cell counter + metabolite", "use": "Combined VCD and chemistry"},
                {"vendor": "Chemometec", "model": "NucleoCounter NC-202", "type": "Fluorescence (AO/PI)", "use": "High-viability samples, cell therapy"},
                {"vendor": "Logos Biosystems", "model": "LUNA-FX7", "type": "Dual fluorescence + brightfield", "use": "Versatile R&D cell counting"},
                {"vendor": "Thermo Fisher", "model": "Countess 3 FL", "type": "Automated cell counter", "use": "Quick bench-top counting"},
                {"vendor": "Roche", "model": "Cedex HiRes", "type": "Trypan blue image analysis", "use": "Detailed morphology + VCD"},
                {"vendor": "Beckman Coulter", "model": "Multisizer 4e", "type": "Coulter counter", "use": "Precise cell size distribution"},
            ],
            "methods_by_product": {
                "Cell Culture (All)": [
                    {"method": "Trypan Blue Exclusion", "purpose": "Viable cell density (VCD) and % viability", "column": "N/A (cassette/slide)", "mobile_phase": "0.4% Trypan Blue", "detection": "Brightfield imaging", "run_time": "< 2 min"},
                    {"method": "AO/PI (Acridine Orange / Propidium Iodide)", "purpose": "Fluorescence-based VCD and viability", "column": "N/A (cassette)", "mobile_phase": "AO/PI reagent", "detection": "Dual fluorescence", "run_time": "< 2 min"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "Nucleocounter (Lysis-based)", "purpose": "Total nuclei count (for clumped cells)", "column": "N/A (Via2 cassette)", "mobile_phase": "Lysis buffer + AO/DAPI", "detection": "Fluorescence", "run_time": "< 2 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Viable Cell Density (VCD) in cells/mL",
                    "Total Cell Density (TCD) in cells/mL",
                    "Viability %",
                    "Average cell diameter (\u00b5m)",
                    "Cell size distribution histogram",
                    "Growth curve (VCD vs time)",
                    "Doubling time calculation",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Counting accuracy (vs hemocytometer reference)", "Repeatability %CV < 10%", "Linearity range (e.g., 1\u00d710\u2075 to 1\u00d710\u2077 cells/mL)"],
                    "Quantitative Output": ["VCD (cells/mL)", "Viability (%)", "Average diameter (\u00b5m)", "Aggregate %"],
                },
            },
            "regulatory_references": ["USP <1046> Cell and Gene Therapy Products", "FDA Guidance on Chemistry for Cell Therapy IND", "ISCT cell counting guidelines"],
        },

        "Endotoxin Testing": {
            "full_name": "Endotoxin / Pyrogen Testing (LAL / rFC / MAT)",
            "principle": (
                "Bacterial endotoxins (lipopolysaccharide from gram-negative bacteria) are detected using: "
                "(1) LAL (Limulus Amoebocyte Lysate) \u2014 horseshoe crab blood cell lysate that clots in the presence of endotoxin; "
                "(2) Recombinant Factor C (rFC) \u2014 recombinant version of the LAL cascade, animal-free; "
                "(3) Monocyte Activation Test (MAT) \u2014 detects all pyrogens via cytokine release from human monocytes. "
                "Endotoxin limits are set based on route of administration and maximum dose."
            ),
            "industry_models": [
                {"vendor": "Charles River", "model": "Endosafe nexgen-PTS", "type": "Portable LAL cartridge", "use": "Rapid endotoxin testing (15 min), in-process"},
                {"vendor": "Charles River", "model": "Endosafe nexgen-MCS", "type": "Multi-cartridge LAL", "use": "Higher throughput QC endotoxin testing"},
                {"vendor": "Lonza", "model": "PyroGene rFC Assay", "type": "Recombinant Factor C", "use": "Animal-free endotoxin testing"},
                {"vendor": "Associates of Cape Cod", "model": "Pyros Kinetix Flex", "type": "Kinetic LAL reader", "use": "Gel-clot / kinetic turbidimetric / chromogenic"},
                {"vendor": "bioMerieux", "model": "ENDONEXT", "type": "rFC cartridge system", "use": "Automated rFC testing"},
            ],
            "methods_by_product": {
                "All Parenteral Drug Products": [
                    {"method": "Kinetic Turbidimetric LAL (KTA)", "purpose": "Quantitative endotoxin determination", "column": "N/A (microplate or tube)", "mobile_phase": "LAL reagent water (LRW)", "detection": "Turbidity increase kinetics", "run_time": "60-90 min"},
                    {"method": "Kinetic Chromogenic LAL (KCA)", "purpose": "Quantitative endotoxin with chromogenic substrate", "column": "N/A (microplate)", "mobile_phase": "LRW + chromogenic substrate", "detection": "Absorbance 405 nm kinetics", "run_time": "60-90 min"},
                    {"method": "Gel-Clot LAL", "purpose": "Semi-quantitative limit test", "column": "N/A (tubes)", "mobile_phase": "LRW", "detection": "Visual clot formation", "run_time": "60 min"},
                    {"method": "rFC fluorescent assay", "purpose": "Quantitative, animal-free endotoxin test", "column": "N/A (microplate)", "mobile_phase": "rFC reagent + fluorescent substrate", "detection": "Fluorescence kinetics", "run_time": "60 min"},
                ],
                "Water Systems": [
                    {"method": "LAL for WFI / PW", "purpose": "Routine water system endotoxin monitoring", "column": "N/A (cartridge)", "mobile_phase": "Sample direct", "detection": "Portable LAL reader", "run_time": "15 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Standard curve (reaction time vs log EU/mL), R\u00b2 > 0.98",
                    "Positive product control (PPC) spike recovery (50-200%)",
                    "Negative control (LRW) result",
                    "Sample endotoxin result (EU/mL or EU/dose)",
                    "Maximum Valid Dilution (MVD) and dilution used",
                    "Pass/fail against endotoxin limit",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Standard curve R\u00b2 > 0.98", "PPC recovery 50-200%", "Coefficient of variation < 25%", "LRW negative control < LOD"],
                    "Quantitative Output": ["Endotoxin (EU/mL)", "Endotoxin per dose (EU/dose)", "Endotoxin limit (5 EU/kg for IV, 0.2 EU/kg for intrathecal)"],
                },
            },
            "regulatory_references": ["USP <85> Bacterial Endotoxins Test", "USP <1085> BET Guidelines", "Ph. Eur. 2.6.14 Bacterial Endotoxins", "FDA Guidance on Pyrogen and Endotoxin Testing", "Ph. Eur. 2.6.30 Monocyte Activation Test"],
        },

        "Mycoplasma PCR": {
            "full_name": "Mycoplasma Detection by PCR / qPCR",
            "principle": (
                "Detects mycoplasma contamination in cell cultures, biologics, and cell therapy products using nucleic acid "
                "amplification (PCR or qPCR) targeting conserved regions of the mycoplasma 16S rRNA gene. Primers are designed "
                "to detect a broad panel of Mycoplasma, Acholeplasma, Spiroplasma, and Ureaplasma species (>190 species). "
                "Rapid PCR methods (results in 3-5 hours) are accepted as alternatives to the traditional culture-based method "
                "(28-day incubation) for in-process and lot release testing per 21 CFR 610.30, Ph. Eur. 2.6.7, and USP <63>. "
                "Both qualitative (detected / not detected) and quantitative formats are available."
            ),
            "industry_models": [
                {"vendor": "Lonza", "model": "MycoAlert PLUS Mycoplasma Detection Kit", "type": "Bioluminescent enzymatic assay (biochemical, not PCR)", "use": "Rapid screening (< 30 min) of cell culture supernatants — not a PCR method but widely used in-process"},
                {"vendor": "Thermo Fisher", "model": "MycoSEQ Mycoplasma Detection System", "type": "qPCR (TaqMan, discriminatory)", "use": "GMP lot release testing, validated for biologics and cell therapy — FDA-referenced"},
                {"vendor": "Roche", "model": "MycoTOOL Mycoplasma Real-Time PCR Kit", "type": "qPCR", "use": "Rapid in-process and lot release mycoplasma testing"},
                {"vendor": "Sartorius", "model": "Microsart ATMP Mycoplasma Kit", "type": "qPCR (validated for ATMP)", "use": "Cell and gene therapy mycoplasma testing"},
                {"vendor": "Charles River", "model": "Mycoplasma Testing Service (PCR + culture)", "type": "PCR and 28-day culture", "use": "Full compendial testing with culture confirmation"},
            ],
            "methods_by_product": {
                "Cell & Gene Therapy": [
                    {"method": "Rapid qPCR mycoplasma detection", "purpose": "Same-day mycoplasma clearance for autologous CAR-T or cell therapy release", "column": "N/A (96-well qPCR plate or cartridge)", "mobile_phase": "DNA extraction from sample + qPCR master mix", "detection": "TaqMan probe fluorescence (real-time PCR)", "run_time": "3-5 hours (extraction + qPCR)"},
                    {"method": "MycoAlert rapid screen", "purpose": "In-process mycoplasma screening of cell culture supernatant", "column": "N/A (luminescence tube or microplate)", "mobile_phase": "MycoAlert substrate + sample supernatant", "detection": "Bioluminescence (ATP detection of mycoplasma enzymes)", "run_time": "25 min"},
                ],
                "Monoclonal Antibodies / Recombinant Proteins": [
                    {"method": "qPCR mycoplasma (lot release)", "purpose": "Mycoplasma testing of cell bank, harvest, or drug substance", "column": "N/A (96-well qPCR plate)", "mobile_phase": "DNA extraction + qPCR master mix", "detection": "TaqMan probe fluorescence", "run_time": "3-5 hours"},
                    {"method": "28-day culture method (compendial)", "purpose": "Gold-standard mycoplasma culture on agar and broth media", "column": "N/A (agar plates + broth)", "mobile_phase": "Friis broth / SP-4 medium / agar", "detection": "Colony observation (fried-egg morphology) + indicator broth color change", "run_time": "28 days"},
                ],
                "Vaccines": [
                    {"method": "qPCR mycoplasma testing", "purpose": "Mycoplasma freedom of vaccine production cell cultures", "column": "N/A", "mobile_phase": "DNA extraction + qPCR master mix", "detection": "TaqMan fluorescence", "run_time": "3-5 hours"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "qPCR result: Detected / Not Detected",
                    "Internal positive control (IPC) amplification confirmation (no inhibition)",
                    "Positive control (spiked mycoplasma DNA) Ct value",
                    "Negative control (NTC) result — no amplification",
                    "Sample Ct value (if detected)",
                    "For MycoAlert: ratio value (Sample/Background) and interpretation",
                    "For culture method: 28-day observation record and colony description",
                ],
                "key_parameters": {
                    "Performance Metrics": ["IPC Ct within acceptable range (confirms no inhibition)", "Positive control Ct within ± 2 of expected", "NTC: No amplification", "LOD: 10 CFU/mL (or 10 copies per reaction)"],
                    "Quantitative Output": ["Detected / Not Detected (qualitative)", "Ct value (if positive)", "MycoAlert ratio (< 0.9 = negative, 0.9-1.2 = borderline, > 1.2 = positive)", "CFU/mL (culture method, if positive)"],
                },
            },
            "regulatory_references": ["21 CFR 610.30 (Mycoplasma testing for biologics)", "Ph. Eur. 2.6.7 Mycoplasmas", "USP <63> Mycoplasma Tests", "FDA Points to Consider in the Characterization of Cell Lines", "Ph. Eur. 2.6.21 NAT for Detection of Mycoplasma"],
        },

        "rFC Endotoxin Assay": {
            "full_name": "Recombinant Factor C Endotoxin Assay",
            "principle": (
                "An animal-free alternative to the traditional LAL (Limulus Amoebocyte Lysate) endotoxin test. Uses recombinant "
                "Factor C (rFC), the endotoxin-sensing serine protease from the horseshoe crab coagulation cascade, produced in "
                "insect or mammalian cells. Endotoxin activates rFC, which cleaves a fluorogenic substrate (e.g., Boc-VPR-AMC), "
                "generating a fluorescent signal proportional to endotoxin concentration. The rFC assay provides equivalent "
                "sensitivity to LAL (LOD 0.005-0.01 EU/mL) with reduced interference from β-glucans (a known LAL false-positive "
                "trigger). Increasingly adopted as a sustainable replacement for animal-derived LAL per USP <85> and Ph. Eur. 2.6.32."
            ),
            "industry_models": [
                {"vendor": "Lonza", "model": "PyroGene Recombinant Factor C Endpoint Fluorescent Assay", "type": "rFC endpoint assay (microplate)", "use": "Animal-free endotoxin testing for biologics, water, and devices"},
                {"vendor": "Charles River", "model": "Endosafe Nexus (rFC cartridges)", "type": "Automated rFC cartridge reader", "use": "Rapid rFC endotoxin testing with walkaway automation"},
                {"vendor": "Charles River", "model": "Endosafe nexgen-MCS (with rFC cartridges)", "type": "Multi-cartridge rFC", "use": "Higher-throughput automated rFC testing"},
                {"vendor": "bioMérieux", "model": "ENDONEXT", "type": "rFC cartridge system", "use": "Automated rFC testing, compact footprint"},
                {"vendor": "Hyglos (bioMérieux)", "model": "EndoLISA", "type": "ELISA-based endotoxin (LPS capture + rFC detection)", "use": "Endotoxin measurement in complex matrices with LPS affinity capture"},
            ],
            "methods_by_product": {
                "All Parenteral Drug Products": [
                    {"method": "rFC endpoint fluorescent assay", "purpose": "Quantitative endotoxin determination — animal-free alternative to LAL", "column": "N/A (96-well microplate, black)", "mobile_phase": "rFC reagent + fluorogenic substrate in endotoxin-free water", "detection": "Fluorescence (Ex 380/Em 440 nm), endpoint at 60 min", "run_time": "60-75 min (incubation + read)"},
                    {"method": "rFC kinetic fluorescent assay", "purpose": "Kinetic endotoxin quantification with wider dynamic range", "column": "N/A (microplate or cartridge)", "mobile_phase": "rFC reagent + fluorogenic substrate", "detection": "Fluorescence kinetics (time to threshold)", "run_time": "60-90 min"},
                ],
                "Water Systems (WFI, PW)": [
                    {"method": "rFC cartridge — rapid water testing", "purpose": "Routine endotoxin monitoring of water systems", "column": "N/A (disposable rFC cartridge)", "mobile_phase": "Sample direct (no dilution needed for water)", "detection": "Fluorescence (cartridge reader)", "run_time": "15-20 min"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "rFC for CGT products", "purpose": "Endotoxin testing in complex cell therapy matrices (reduced β-glucan interference vs. LAL)", "column": "N/A (microplate or cartridge)", "mobile_phase": "rFC reagent + substrate", "detection": "Fluorescence", "run_time": "60-75 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Standard curve (endotoxin concentration vs. fluorescence, R² > 0.98)",
                    "Positive product control (PPC) spike recovery (50-200%)",
                    "Negative control (endotoxin-free water) result",
                    "Sample endotoxin result (EU/mL or EU/dose)",
                    "Maximum Valid Dilution (MVD) used",
                    "Pass/fail against product endotoxin limit",
                    "rFC lot number and expiry",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Standard curve R² > 0.98", "PPC recovery 50-200%", "CV < 25% between replicates", "Negative control < LOD (0.005 EU/mL)"],
                    "Quantitative Output": ["Endotoxin (EU/mL)", "Endotoxin per dose (EU/dose)", "LOD (typically 0.005-0.01 EU/mL)", "Endotoxin limit (5 EU/kg IV, 0.2 EU/kg intrathecal)"],
                },
            },
            "regulatory_references": ["USP <85> Bacterial Endotoxins Test (rFC accepted as alternative method)", "Ph. Eur. 2.6.32 Test for Bacterial Endotoxins Using Recombinant Factor C", "FDA Guidance on Pyrogen and Endotoxin Testing", "USP <1085> BET Guidelines"],
        },

        "Bioburden Testing": {
            "full_name": "Bioburden Testing (Microbial Enumeration and Identification)",
            "principle": (
                "Quantifies the total number of viable aerobic microorganisms (bacteria, yeasts, molds) present in or on "
                "a pharmaceutical product, raw material, or manufacturing environment. Two primary methods: "
                "(1) Membrane Filtration — the sample is filtered through a 0.45 µm membrane that retains microorganisms; "
                "the membrane is transferred to agar and incubated. Preferred for large-volume or low-bioburden liquid samples. "
                "(2) Direct Inoculation (Pour Plate / Spread Plate) — sample is mixed with or spread onto agar and incubated. "
                "Used when membrane filtration is not feasible (e.g., viscous or particulate-laden samples). "
                "Bioburden testing is required pre-sterilization to establish microbial load and as a GMP in-process control. "
                "Method suitability must be demonstrated per USP <61>/<62> to confirm no antimicrobial activity from the product."
            ),
            "industry_models": [
                {"vendor": "Merck Millipore", "model": "Steritest Symbio Pump", "type": "Closed-system membrane filtration", "use": "Sterility and bioburden testing with aseptic containment"},
                {"vendor": "Merck Millipore", "model": "Milliflex Oasis", "type": "Automated colony counter + membrane filtration", "use": "Automated bioburden enumeration with imaging"},
                {"vendor": "Sartorius", "model": "Microsart @vance", "type": "Membrane filtration system", "use": "Bioburden and sterility testing"},
                {"vendor": "bioMérieux", "model": "TEMPO System", "type": "Automated MPN (most probable number)", "use": "High-throughput bioburden enumeration for large sample volumes"},
                {"vendor": "Rapid Micro Biosystems", "model": "Growth Direct System", "type": "Automated rapid micro method", "use": "Rapid bioburden detection by autofluorescence imaging (compendial alternative)"},
            ],
            "methods_by_product": {
                "All Pharmaceutical Products (Drug Substance / Drug Product)": [
                    {"method": "Membrane filtration (TAMC / TYMC)", "purpose": "Total aerobic microbial count (TAMC) and total yeast/mold count (TYMC)", "column": "N/A (0.45 µm membrane filter, 47 mm)", "mobile_phase": "Sterile diluent (peptone water or PBS) for sample preparation", "detection": "Colony count after incubation (TSA 30-35°C / 3 days for TAMC; SDA 20-25°C / 5 days for TYMC)", "run_time": "3-5 days incubation"},
                    {"method": "Direct inoculation (pour plate)", "purpose": "Bioburden of viscous, turbid, or non-filterable samples", "column": "N/A (Petri dish)", "mobile_phase": "Molten agar (TSA for bacteria, SDA for fungi)", "detection": "Colony count after incubation", "run_time": "3-5 days incubation"},
                ],
                "Water Systems (WFI, PW, Process Water)": [
                    {"method": "Membrane filtration — water bioburden", "purpose": "Microbial monitoring of pharmaceutical water systems", "column": "N/A (0.45 µm membrane, 100-1000 mL sample volume)", "mobile_phase": "Direct filtration (no dilution)", "detection": "Colony count on R2A agar (30-35°C, 5 days)", "run_time": "5 days (R2A method for stressed/slow-growing organisms)"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "Rapid bioburden (Growth Direct or BacT/ALERT)", "purpose": "Rapid in-process bioburden for short-shelf-life products (CAR-T)", "column": "N/A (automated detection system)", "mobile_phase": "Culture medium (proprietary)", "detection": "Autofluorescence imaging (Growth Direct) or CO2 detection (BacT/ALERT)", "run_time": "24-48 hours (rapid) vs. 3-5 days (compendial)"},
                ],
                "Specified Microorganisms (USP <62>)": [
                    {"method": "Absence of specified organisms", "purpose": "Test for absence of E. coli, Salmonella, P. aeruginosa, S. aureus, bile-tolerant gram-negatives, Clostridia, Candida", "column": "N/A (enrichment broth + selective agar)", "mobile_phase": "TSB enrichment → selective media (MacConkey, Cetrimide, Baird-Parker, etc.)", "detection": "Growth / no growth on selective media + confirmatory tests", "run_time": "5-7 days"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "TAMC result (CFU/mL or CFU/g)",
                    "TYMC result (CFU/mL or CFU/g)",
                    "Method suitability (recovery ≥ 70% of inoculum for each challenge organism)",
                    "Positive control growth promotion (USP challenge organisms)",
                    "Negative control (sterile diluent) — no growth",
                    "Specified organism results (detected / not detected)",
                    "Incubation conditions and duration",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Method suitability: recovery ≥ 70% (per USP <61>)", "Growth promotion: colony count within 2x of inoculum", "Negative control: 0 CFU"],
                    "Quantitative Output": ["TAMC (CFU/mL or CFU/g)", "TYMC (CFU/mL or CFU/g)", "Specified organisms: Detected / Not Detected", "Alert and action limits (per in-house specification)"],
                },
                "acceptance_criteria_examples": {
                    "Non-sterile drug product (USP category)": {"TAMC": "≤ 10² CFU/mL (category 2)", "TYMC": "≤ 10¹ CFU/mL (category 2)", "E. coli": "Absent in 1 g or 1 mL"},
                    "Pre-sterilization bioburden": {"Bioburden": "≤ action limit (e.g., ≤ 10 CFU/100 mL for aseptic fill)"},
                },
            },
            "regulatory_references": ["USP <61> Microbiological Examination of Nonsterile Products: Microbial Enumeration Tests", "USP <62> Microbiological Examination of Nonsterile Products: Tests for Specified Microorganisms", "Ph. Eur. 2.6.12 Microbiological Examination of Non-Sterile Products: Microbial Enumeration", "Ph. Eur. 2.6.13 Microbiological Examination: Tests for Specified Microorganisms", "USP <1111> Microbiological Examination of Nonsterile Products: Acceptance Criteria"],
        },
    },

    # =========================================================================
    # IMAGING & MICROSCOPY
    # =========================================================================
    "Imaging & Microscopy": {
        "Light Microscopy": {
            "full_name": "Light / Phase-Contrast / Brightfield Microscopy",
            "principle": (
                "Visible light illuminates a specimen; transmitted or reflected light is magnified through objective and "
                "eyepiece lenses. Phase-contrast converts phase differences (from refractive index variations) into amplitude "
                "differences, allowing visualization of unstained transparent cells. Typical magnification 40x-1000x. "
                "Digital cameras enable quantitative image analysis."
            ),
            "industry_models": [
                {"vendor": "Olympus (Evident)", "model": "CKX53", "type": "Inverted microscope", "use": "Cell culture observation, routine QC"},
                {"vendor": "Nikon", "model": "Eclipse Ts2", "type": "Inverted microscope", "use": "Cell culture, transfection checks"},
                {"vendor": "Zeiss", "model": "Primovert", "type": "Inverted microscope", "use": "Compact cell culture microscopy"},
                {"vendor": "Leica", "model": "DMi1", "type": "Inverted microscope", "use": "Routine cell observation"},
                {"vendor": "Keyence", "model": "BZ-X810", "type": "All-in-one fluorescence/brightfield", "use": "Automated imaging, stitching, Z-stack"},
            ],
            "methods_by_product": {
                "Cell Culture (All)": [
                    {"method": "Phase-contrast cell observation", "purpose": "Morphology, confluence, contamination check", "column": "N/A", "mobile_phase": "N/A", "detection": "Phase-contrast optics, 10-20x objective", "run_time": "< 5 min"},
                    {"method": "Gram stain microscopy", "purpose": "Bacterial identification and contamination", "column": "N/A (slide)", "mobile_phase": "Crystal violet, iodine, safranin", "detection": "Brightfield 100x oil immersion", "run_time": "15 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Photomicrograph with scale bar",
                    "Magnification and objective used",
                    "Observations (morphology, confluence %, contamination)",
                    "Date and operator",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Optical resolution", "Image calibration (scale bar verification)"],
                    "Quantitative Output": ["Qualitative observations", "Confluence % (visual estimate or software)", "Cell morphology description"],
                },
            },
            "regulatory_references": ["USP <1058> Analytical Instrument Qualification", "21 CFR 211 GMP (environmental monitoring)"],
        },

        "Electron Microscopy": {
            "full_name": "Electron Microscopy (TEM / SEM / Cryo-EM)",
            "principle": (
                "Uses electron beams instead of light for imaging at nanometer to angstrom resolution. "
                "TEM: electrons transmit through ultra-thin specimens (~50-100 nm), forming high-resolution images of internal structure. "
                "SEM: electron beam scans the surface, detecting secondary/backscattered electrons for 3D surface topology. "
                "Cryo-EM: specimen is rapidly frozen (vitrification) and imaged in the native hydrated state; single-particle "
                "analysis enables 3D protein structure determination to near-atomic resolution."
            ),
            "industry_models": [
                {"vendor": "Thermo Fisher", "model": "Glacios 2", "type": "200 kV Cryo-TEM", "use": "Screening, single-particle cryo-EM"},
                {"vendor": "Thermo Fisher", "model": "Krios G4", "type": "300 kV Cryo-TEM", "use": "High-resolution structural biology"},
                {"vendor": "Thermo Fisher", "model": "Talos L120C", "type": "120 kV TEM", "use": "Routine TEM, negative stain, nanoparticles"},
                {"vendor": "JEOL", "model": "JEM-1400Flash", "type": "120 kV TEM", "use": "Negative stain TEM, viral morphology"},
                {"vendor": "JEOL", "model": "CRYO ARM 300 II", "type": "300 kV Cryo-TEM", "use": "High-end structural cryo-EM"},
                {"vendor": "Hitachi", "model": "SU9000", "type": "STEM/SEM", "use": "Ultra-high resolution surface imaging"},
                {"vendor": "Thermo Fisher", "model": "Phenom Pharos", "type": "Desktop SEM", "use": "QC particle morphology, filter integrity"},
            ],
            "methods_by_product": {
                "Viral Vectors / VLPs / Vaccines": [
                    {"method": "Negative Stain TEM", "purpose": "Particle morphology, integrity, aggregation", "column": "N/A (TEM grid)", "mobile_phase": "Uranyl acetate or phosphotungstic acid stain", "detection": "TEM 80-120 kV", "run_time": "1-2 hours (prep + imaging)"},
                    {"method": "Cryo-EM", "purpose": "Native-state particle structure, full/empty capsid ratio", "column": "N/A (vitrified grid)", "mobile_phase": "N/A (flash-frozen in liquid ethane)", "detection": "Cryo-TEM 200-300 kV", "run_time": "4-24 hours (data collection)"},
                ],
                "LNPs / Liposomes": [
                    {"method": "Cryo-TEM", "purpose": "LNP morphology, lamellarity, size", "column": "N/A", "mobile_phase": "Vitrification", "detection": "Cryo-TEM 200 kV", "run_time": "4-8 hours"},
                ],
                "Protein Structure": [
                    {"method": "Single-Particle Cryo-EM", "purpose": "3D structure determination (2-4 \u00c5 resolution)", "column": "N/A", "mobile_phase": "Vitrified protein sample (0.5-5 mg/mL)", "detection": "Cryo-TEM 300 kV + direct electron detector", "run_time": "24-72 hours (data collection + processing)"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Micrographs with scale bar (for TEM/SEM)",
                    "Particle morphology description (size, shape, integrity)",
                    "Particle size distribution (from image analysis)",
                    "Full/empty ratio (for AAV cryo-EM)",
                    "3D reconstruction and resolution (for single-particle)",
                    "Fourier Shell Correlation (FSC) plot and reported resolution",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Magnification calibration", "Defocus range", "Resolution (FSC 0.143 criterion for cryo-EM)"],
                    "Quantitative Output": ["Particle diameter (nm)", "Full/empty capsid ratio (%)", "Resolution (\u00c5) for 3D structures", "Particle count per field"],
                },
            },
            "regulatory_references": ["ICH Q6B (identity and purity characterization)", "FDA Guidance on AAV-based Gene Therapy", "WHO TRS 978 (vaccine characterization)"],
        },
    },

    # =========================================================================
    # FORMULATION ANALYTICS
    # =========================================================================
    "Formulation Analytics": {
        "Osmolality": {
            "full_name": "Osmolality Measurement",
            "principle": (
                "Measures the osmotic concentration (osmolality) of a solution — the total number of osmotically active "
                "solute particles per kilogram of solvent (mOsm/kg). Two primary methods: "
                "(1) Freezing Point Depression — the most common method; the sample is supercooled and nucleated, and the "
                "equilibrium freezing point is measured. Depression of the freezing point is proportional to osmolality "
                "(Raoult's law). Accurate, precise, and the USP/Ph. Eur. reference method. "
                "(2) Vapor Pressure Osmometry — measures the dew point depression of air equilibrated with the sample. "
                "Suitable for volatile-solute-containing samples where freezing point methods may be inaccurate. "
                "Osmolality is a critical quality attribute for parenteral formulations (target typically 250-400 mOsm/kg "
                "for IV products) to avoid hemolysis or pain on injection."
            ),
            "industry_models": [
                {"vendor": "ELITechGroup", "model": "Vapro 5600", "type": "Vapor pressure osmometer", "use": "Osmolality of small-volume samples (10 µL), low-viscosity formulations"},
                {"vendor": "Advanced Instruments", "model": "OsmoPRO Multi-Sample Micro-Osmometer", "type": "Freezing point depression (multi-sample)", "use": "High-throughput osmolality for QC labs, 20 µL sample"},
                {"vendor": "Advanced Instruments", "model": "Model 3320 Single-Sample Osmometer", "type": "Freezing point depression", "use": "Standard QC osmolality measurement, 20 µL sample"},
                {"vendor": "Gonotec", "model": "Osmomat 3000", "type": "Freezing point depression", "use": "Routine osmolality, GMP-compliant"},
                {"vendor": "Löser", "model": "Micro-Osmometer Type 15/15M", "type": "Freezing point depression", "use": "Small sample volume (50-150 µL), European labs"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs)": [
                    {"method": "Freezing point depression osmolality", "purpose": "Osmolality of final formulated drug product (critical for IV or SC administration)", "column": "N/A (20-250 µL sample in osmometer)", "mobile_phase": "N/A (neat sample)", "detection": "Freezing point depression (thermistor)", "run_time": "2-3 min per sample"},
                ],
                "Vaccines": [
                    {"method": "Osmolality — freezing point", "purpose": "Verify isotonicity of vaccine formulation", "column": "N/A", "mobile_phase": "N/A (neat sample)", "detection": "Freezing point depression", "run_time": "2-3 min"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "Osmolality of cryopreservation buffer", "purpose": "Ensure cryopreservation formulation osmolality is within cell tolerance range", "column": "N/A", "mobile_phase": "N/A (neat sample)", "detection": "Freezing point depression or vapor pressure", "run_time": "2-3 min"},
                    {"method": "Osmolality of infusion product", "purpose": "Verify final cell therapy product osmolality prior to infusion", "column": "N/A", "mobile_phase": "N/A", "detection": "Freezing point depression", "run_time": "2-3 min"},
                ],
                "Small Molecule APIs (Parenteral)": [
                    {"method": "Osmolality — parenteral formulation", "purpose": "Verify isotonicity or controlled hypertonicity for IV/IM/SC injectables", "column": "N/A", "mobile_phase": "N/A (neat sample)", "detection": "Freezing point depression", "run_time": "2-3 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Osmolality result (mOsm/kg)",
                    "Calibration verification (NaCl standards: 100, 290, 500 mOsm/kg)",
                    "Replicate measurements and %CV",
                    "Sample temperature and preparation details",
                    "Pass/fail against specification",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Calibration verification with NIST-traceable standards (± 2 mOsm/kg)", "Repeatability: %CV < 1% (replicates)", "Sample volume: 20-250 µL depending on instrument"],
                    "Quantitative Output": ["Osmolality (mOsm/kg)", "Mean ± SD of replicates"],
                },
                "acceptance_criteria_examples": {
                    "IV parenteral formulation": {"Osmolality": "240-400 mOsm/kg (approximately isotonic to slightly hypertonic)"},
                    "SC high-concentration mAb": {"Osmolality": "Report result (may be hypotonic to hypertonic depending on excipient design)"},
                },
            },
            "regulatory_references": ["USP <785> Osmolality and Osmolarity", "Ph. Eur. 2.2.35 Osmolality", "ICH Q6A Specifications for Chemical Substances", "ICH Q6B Specifications for Biologicals"],
        },

        "Viscosity": {
            "full_name": "Viscosity Measurement",
            "principle": (
                "Measures the resistance of a fluid to flow (dynamic viscosity, η, in mPa·s or cP). Critical for "
                "high-concentration protein formulations (>100 mg/mL mAbs) where viscosity directly impacts syringeability, "
                "manufacturability, and patient comfort during subcutaneous injection. Multiple measurement principles: "
                "(1) Microfluidic VROC (Viscometer-Rheometer on a Chip) — rectangular slit flow with MEMS pressure sensors; "
                "requires only 20-100 µL sample and provides accurate viscosity at defined shear rates. "
                "(2) Cone-and-plate rheometry — rotational measurement where fluid is sheared between a rotating cone and "
                "a flat plate at controlled shear rate or stress; provides full flow curves and viscoelastic properties. "
                "(3) Capillary viscometry — gravity-driven or pressure-driven flow through a calibrated capillary (Ubbelohde, "
                "Cannon-Fenske); measures kinematic viscosity. "
                "Target viscosity for SC injectables is typically <20-30 cP for acceptable syringe glide force."
            ),
            "industry_models": [
                {"vendor": "RheoSense", "model": "VROC initium one plus", "type": "Microfluidic viscometer (VROC chip)", "use": "Low-volume viscosity of high-concentration biologics (26 µL sample)"},
                {"vendor": "RheoSense", "model": "m-VROC", "type": "Pressure-driven microfluidic viscometer", "use": "Viscosity vs. shear rate profiles, small sample volumes"},
                {"vendor": "Anton Paar", "model": "MCR 72/92/302e", "type": "Rotational rheometer (cone-plate, parallel plate)", "use": "Full rheological characterization, viscosity, viscoelasticity"},
                {"vendor": "Anton Paar", "model": "Lovis 2000 ME", "type": "Rolling-ball microviscometer", "use": "Ultra-low volume viscosity (100 µL), high precision"},
                {"vendor": "Malvern Panalytical", "model": "Kinexus", "type": "Rotational rheometer", "use": "Viscosity and viscoelastic measurements for formulation development"},
                {"vendor": "Cannon Instrument (AMETEK)", "model": "Cannon-Fenske Routine Viscometer", "type": "Glass capillary viscometer", "use": "Kinematic viscosity per USP <911>, pharmacopeial reference method"},
            ],
            "methods_by_product": {
                "Monoclonal Antibodies (mAbs) — High Concentration": [
                    {"method": "VROC microfluidic viscosity", "purpose": "Dynamic viscosity of high-concentration (>100 mg/mL) mAb formulations at defined shear rate", "column": "N/A (VROC chip, A05 or B05)", "mobile_phase": "N/A (neat sample, 26-100 µL)", "detection": "MEMS pressure sensor array in rectangular slit", "run_time": "5 min per measurement (with rinse)"},
                    {"method": "Cone-plate rheometry — viscosity vs. shear rate", "purpose": "Full flow curve to assess Newtonian/non-Newtonian behavior of mAb formulations", "column": "N/A (cone-plate geometry, 50 µm gap)", "mobile_phase": "N/A (0.5-1 mL sample)", "detection": "Torque and angular velocity measurement", "run_time": "15-30 min (shear rate sweep 1-1000 s⁻¹)"},
                ],
                "Biologics (General Parenteral Formulation Development)": [
                    {"method": "Viscosity screening (formulation optimization)", "purpose": "Screen excipient combinations (arginine, proline, NaCl) to reduce viscosity of high-concentration formulations", "column": "N/A (VROC or cone-plate)", "mobile_phase": "N/A (multiple formulation variants)", "detection": "VROC or rotational rheometry", "run_time": "5 min per sample (high-throughput with VROC)"},
                ],
                "ADCs": [
                    {"method": "Viscosity post-conjugation", "purpose": "Assess viscosity impact of drug-linker conjugation on formulation", "column": "N/A", "mobile_phase": "N/A (neat ADC formulation)", "detection": "VROC or cone-plate", "run_time": "5-15 min"},
                ],
                "Cell & Gene Therapy": [
                    {"method": "Viscosity of cryopreservation media", "purpose": "Characterize viscosity of DMSO-containing cryopreservation formulations", "column": "N/A", "mobile_phase": "N/A (cryopreservation buffer)", "detection": "Cone-plate rheometry (temperature-controlled)", "run_time": "15-30 min"},
                ],
            },
            "data_reporting": {
                "report_sections": [
                    "Dynamic viscosity (mPa·s or cP) at specified shear rate and temperature",
                    "Viscosity vs. shear rate plot (if flow curve measured)",
                    "Temperature of measurement (typically 20°C or 25°C)",
                    "Protein concentration of sample",
                    "Instrument calibration with viscosity standard (NIST-traceable silicone oil or water)",
                    "For syringeability: glide force measurement correlation",
                ],
                "key_parameters": {
                    "Performance Metrics": ["Viscosity standard recovery (± 3% of certified value)", "Temperature control (± 0.1°C)", "Repeatability: %CV < 2%", "Sample volume: 26 µL (VROC) to 1 mL (cone-plate)"],
                    "Quantitative Output": ["Dynamic viscosity η (mPa·s or cP)", "Kinematic viscosity ν (mm²/s) — for capillary methods", "Shear rate (s⁻¹)", "Temperature (°C)"],
                },
                "acceptance_criteria_examples": {
                    "SC mAb formulation": {"Viscosity (25°C, 1000 s⁻¹)": "≤ 20 cP (preferred for 27G thin-wall needle)", "Viscosity (25°C)": "≤ 30 cP (maximum for acceptable syringe glide force)"},
                },
            },
            "regulatory_references": ["USP <911> Viscosity — Capillary Viscometer Methods", "USP <912> Viscosity — Rotational Viscometer Methods", "Ph. Eur. 2.2.8 Viscosity — Falling Ball Method", "Ph. Eur. 2.2.10 Viscosity — Capillary Viscometer Method", "ICH Q6B Specifications for Biologicals"],
        },
    },
}
