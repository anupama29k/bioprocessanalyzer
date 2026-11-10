
    # MULTI-PROBE FERMENTATION DATASETS

    ## Overview
    Six comprehensive datasets with multiple sensor readings for testing bioprocess analyzers.

    ## Datasets

    ### 1. standard_multiprobe.csv
    **Standard E. coli batch fermentation**
    - **Time**: 0-24 hours (15 min intervals)
    - **Substrates**: Glucose (10→0 g/L)
    - **Products**: Acetate (0→1.2 g/L)
    - **Probes**: pH, DO, Temperature, CER, OUR, RQ, Agitation, Airflow, Pressure
    - **Reference**: Neidhardt, F.C. (1996)

    ### 2. fedbatch_multiprobe.csv
    **Fed-batch fermentation with controlled feeding**
    - **Time**: 0-72 hours (30 min intervals)
    - **Substrates**: Glucose (controlled feed)
    - **Products**: Minimal acetate
    - **Probes**: pH, DO, Temperature, CER, OUR, RQ, Agitation, Feed rate, Base addition, Off-gas CO2
    - **Reference**: Korz et al. (1995)

    ### 3. stress_multiprobe.csv
    **Osmotic stress conditions**
    - **Time**: 0-48 hours (30 min intervals)
    - **Stress markers**: Trehalose, Proline
    - **Probes**: pH, DO, Temperature, Osmolality, Viscosity
    - **Reference**: Record et al. (1998)

    ### 4. temperature_study_multiprobe.csv
    **Temperature shift study (37°C → 42°C → 37°C)**
    - **Time**: 0-36 hours (30 min intervals)
    - **Products**: Heat shock proteins
    - **Probes**: Temperature (controlled), DO, Heat shock proteins
    - **Reference**: Applied and Environmental Microbiology (2008)

    ### 5. diauxic_multiprobe.csv
    **Diauxic growth with substrate switching**
    - **Time**: 0-40 hours (30 min intervals)
    - **Substrates**: Glucose → Lactose
    - **Products**: β-galactosidase
    - **Probes**: DO, CO2, pH (shows diauxic shift)
    - **Reference**: Journal of Bacteriology (2004)

    ### 6. high_cell_density_multiprobe.csv
    **High cell density fermentation**
    - **Time**: 0-48 hours (1 hour intervals)
    - **Maximum OD**: 85-100
    - **Probes**: DO, pH, Temperature, CER, OUR, RQ, Agitation, Airflow, Foam, Oxygen transfer
    - **Reference**: Korz et al. (1995)

    ## Sensor Types Included

    | Sensor Type | Variables |
    |-------------|-----------|
    | **Biomass** | OD_600nm, Biomass_gL |
    | **Substrates** | Glucose_gL, Lactose_gL |
    | **Products** | Acetate_gL, HeatShockProteins_gL, Beta_Galactosidase_U, Trehalose_gL, Proline_gL |
    | **Physicochemical** | pH, Temperature_C, DO_percent, Osmolality_mOsm, Viscosity_cP |
    | **Gas Exchange** | CER_mmol_Lh, OUR_mmol_Lh, RQ, CO2_percent, Offgas_CO2_percent |
    | **Process** | Agitation_rpm, Airflow_vvm, Pressure_bar, FeedRate_mLh, BaseAddition_mLh, Foam_level_percent |
    | **Cumulative** | OxygenTransfer_mmol |

    ## Testing Your Bioprocess Analyzer

    ### What to Test:

    1. **Growth Kinetics**
       - μ_max calculation under different conditions
       - Phase detection (lag, exponential, stationary)
       - Diauxic shift detection

    2. **Substrate Utilization**
       - Glucose consumption profiles
       - Lactose utilization after diauxic shift
       - Yield calculations (Yx/s)

    3. **Product Formation**
       - Acetate production (overflow metabolism)
       - Heat shock protein induction
       - β-galactosidase expression

    4. **Process Parameters**
       - DO profiles during growth
       - pH control effectiveness
       - Temperature effects on growth
       - CER/OUR patterns

    5. **Advanced Features**
       - Fed-batch detection
       - Stress condition identification
       - Multi-parameter correlation
       - Time-series visualization

    ### Expected Results:

    | Dataset | Expected μ_max | Expected Features |
    |---------|---------------|-------------------|
    | Standard | 0.43-0.47 h⁻¹ | DO dip, acetate production |
    | Fed-batch | 0.43-0.47 (batch) | Controlled DO, feed profile |
    | Stress | 0.16-0.20 h⁻¹ | Extended lag, stress markers |
    | Temperature | 0.30-0.34 h⁻¹ | Heat shock response |
    | Diauxic | 0.52 (1st), 0.35 (2nd) | Two growth phases, DO spike |
    | High density | 0.43-0.47 (batch) | Multiple sensors, foam |

    ## Usage

    1. Upload any CSV to your bioprocess analyzer
    2. Map the columns correctly
    3. Analyze growth kinetics and process parameters
    4. Compare with expected values above

    Your app should handle all these sensor types and provide meaningful visualizations!
    