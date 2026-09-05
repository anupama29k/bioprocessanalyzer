"""
Generate realistic E. coli fermentation data based on published literature
References: Typical E. coli growth kinetics in batch fermentation
- Specific growth rate (μ): 0.3-0.8 h⁻¹ for glucose minimal medium
- Lag phase: 1-3 hours
- Stationary phase: OD ~ 5-10 depending on medium
"""

import pandas as pd
import numpy as np
from datetime import datetime

def generate_ecoli_batch_1():
    """Standard E. coli batch fermentation - Glucose minimal medium"""
    np.random.seed(42)
    
    # Time points (hours)
    time = np.arange(0, 24.5, 0.5)
    
    # Growth parameters (based on typical E. coli MG1655)
    lag_time = 2.0
    mu_max = 0.45  # h⁻¹ (typical for glucose minimal medium)
    initial_od = 0.05
    max_od = 8.5
    
    # Generate OD with realistic kinetics
    od = np.zeros_like(time)
    for i, t in enumerate(time):
        if t < lag_time:
            od[i] = initial_od + (initial_od * 0.1 * t)  # Slight increase during lag
        else:
            t_exp = t - lag_time
            od_exp = initial_od * np.exp(mu_max * t_exp)
            od[i] = min(od_exp, max_od)
    
    # Add realistic noise and measurement error
    od = od + np.random.normal(0, 0.05, len(od))
    od = np.maximum(od, 0.01)
    
    # Glucose consumption (typical yield: 0.5 g/g biomass)
    glucose_initial = 10.0  # g/L
    yield_od_glucose = 0.85  # OD per g/L glucose
    glucose = glucose_initial - (od - initial_od) / yield_od_glucose
    glucose = np.maximum(glucose, 0) + np.random.normal(0, 0.1, len(glucose))
    
    # Acetate production (overflow metabolism at high growth rates)
    acetate = np.zeros_like(time)
    for i in range(len(time)):
        if od[i] > 2.0 and glucose[i] > 2.0:
            acetate[i] = 0.15 * (od[i] - 2.0) + np.random.normal(0, 0.05)
        elif od[i] > 0.5:
            acetate[i] = 0.05 * od[i] + np.random.normal(0, 0.02)
    acetate = np.maximum(acetate, 0)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Time_h': time,
        'OD_600nm': np.round(od, 3),
        'Glucose_gL': np.round(glucose, 2),
        'Acetate_gL': np.round(acetate, 3),
        'Biomass_gL': np.round(od * 0.35, 3),  # Conversion factor: OD 1 = 0.35 g/L dry weight
        'GrowthRate_h': [0 if t < lag_time else mu_max * (1 - od[i]/max_od) for i, t in enumerate(time)]
    })
    
    return df

def generate_ecoli_batch_2():
    """E. coli batch fermentation - Rich medium (LB)"""
    np.random.seed(43)
    
    time = np.arange(0, 20, 0.5)
    lag_time = 1.0
    mu_max = 0.85  # h⁻¹ (higher in rich medium)
    initial_od = 0.08
    max_od = 12.0
    
    od = np.zeros_like(time)
    for i, t in enumerate(time):
        if t < lag_time:
            od[i] = initial_od + (initial_od * 0.2 * t)
        else:
            t_exp = t - lag_time
            od_exp = initial_od * np.exp(mu_max * t_exp)
            od[i] = min(od_exp, max_od)
    
    od = od + np.random.normal(0, 0.08, len(od))
    od = np.maximum(od, 0.01)
    
    # Complex medium - no defined substrate
    df = pd.DataFrame({
        'Time_h': time,
        'OD_600nm': np.round(od, 3),
        'Biomass_gL': np.round(od * 0.38, 3),
        'GrowthRate_h': [0 if t < lag_time else mu_max * (1 - od[i]/max_od) for i, t in enumerate(time)]
    })
    
    return df

def generate_ecoli_batch_3():
    """E. coli with substrate limitation and product formation"""
    np.random.seed(44)
    
    time = np.arange(0, 30, 0.5)
    lag_time = 2.5
    mu_max = 0.38  # h⁻¹
    initial_od = 0.04
    max_od = 6.5
    
    # Glycerol as carbon source (slower growth)
    od = np.zeros_like(time)
    for i, t in enumerate(time):
        if t < lag_time:
            od[i] = initial_od + (initial_od * 0.08 * t)
        else:
            t_exp = t - lag_time
            od_exp = initial_od * np.exp(mu_max * t_exp)
            od[i] = min(od_exp, max_od)
    
    od = od + np.random.normal(0, 0.04, len(od))
    od = np.maximum(od, 0.01)
    
    # Glycerol consumption
    glycerol_initial = 15.0
    yield_od_glycerol = 0.43
    glycerol = glycerol_initial - (od - initial_od) / yield_od_glycerol
    glycerol = np.maximum(glycerol, 0) + np.random.normal(0, 0.15, len(glycerol))
    
    # Recombinant protein production (induced at 8h)
    protein = np.zeros_like(time)
    induction_time = 8.0
    for i, t in enumerate(time):
        if t >= induction_time and od[i] > 1.0:
            protein[i] = 0.25 * (t - induction_time) * (od[i] / max_od) + np.random.normal(0, 0.05)
    protein = np.maximum(protein, 0)
    
    df = pd.DataFrame({
        'Time_h': time,
        'OD_600nm': np.round(od, 3),
        'Glycerol_gL': np.round(glycerol, 2),
        'Recombinant_Protein_gL': np.round(protein, 3),
        'Biomass_gL': np.round(od * 0.32, 3)
    })
    
    return df

def generate_ecoli_batch_4():
    """E. coli with stress conditions (high osmotic pressure)"""
    np.random.seed(45)
    
    time = np.arange(0, 28, 0.5)
    lag_time = 4.0  # Extended lag due to stress
    mu_max = 0.25  # h⁻¹ (reduced growth rate)
    initial_od = 0.06
    max_od = 4.5  # Lower final OD
    
    od = np.zeros_like(time)
    for i, t in enumerate(time):
        if t < lag_time:
            od[i] = initial_od + (initial_od * 0.05 * t)
        else:
            t_exp = t - lag_time
            od_exp = initial_od * np.exp(mu_max * t_exp)
            od[i] = min(od_exp, max_od)
    
    od = od + np.random.normal(0, 0.03, len(od))
    od = np.maximum(od, 0.01)
    
    # Stress response metabolites
    trehalose = np.zeros_like(time)
    for i, t in enumerate(time):
        if t > lag_time and od[i] > 0.5:
            trehalose[i] = 0.08 * od[i] + np.random.normal(0, 0.02)
    
    df = pd.DataFrame({
        'Time_h': time,
        'OD_600nm': np.round(od, 3),
        'NaCl_gL': np.full(len(time), 10.0),  # High salt concentration
        'Trehalose_gL': np.round(trehalose, 3),
        'Biomass_gL': np.round(od * 0.30, 3)
    })
    
    return df

def generate_ecoli_fed_batch():
    """E. coli fed-batch fermentation simulation"""
    np.random.seed(46)
    
    time = np.arange(0, 48, 1.0)
    lag_time = 3.0
    mu_max = 0.55  # h⁻¹
    initial_od = 0.1
    max_od = 45.0  # High cell density
    
    # Feed profile (exponential feeding)
    feed_rate = np.zeros_like(time)
    od = np.zeros_like(time)
    od[0] = initial_od
    
    for i in range(1, len(time)):
        if time[i] < lag_time:
            od[i] = od[i-1] * (1 + 0.05)
        else:
            # Exponential growth with feeding
            growth_factor = mu_max * (1 - od[i-1]/max_od)
            od[i] = od[i-1] * (1 + growth_factor)
            feed_rate[i] = 0.5 * np.exp(0.1 * time[i])
    
    od = od + np.random.normal(0, 0.5, len(od))
    od = np.maximum(od, 0.01)
    
    df = pd.DataFrame({
        'Time_h': time,
        'OD_600nm': np.round(od, 2),
        'FeedRate_mLh': np.round(feed_rate, 2),
        'Biomass_gL': np.round(od * 0.35, 2)
    })
    
    return df

# Generate all datasets
print("Generating E. coli fermentation datasets...")

df1 = generate_ecoli_batch_1()
df2 = generate_ecoli_batch_2()
df3 = generate_ecoli_batch_3()
df4 = generate_ecoli_batch_4()
df5 = generate_ecoli_fed_batch()

# Save to CSV files
df1.to_csv('ecoli_glucose_batch.csv', index=False)
df2.to_csv('ecoli_LB_batch.csv', index=False)
df3.to_csv('ecoli_glycerol_batch.csv', index=False)
df4.to_csv('ecoli_stress_batch.csv', index=False)
df5.to_csv('ecoli_fedbatch.csv', index=False)

print("\n✅ All datasets generated successfully!")
print("\nFiles created:")
print("1. ecoli_glucose_batch.csv - Standard glucose minimal medium")
print("   - Time_h, OD_600nm, Glucose_gL, Acetate_gL, Biomass_gL")
print("\n2. ecoli_LB_batch.csv - Rich LB medium (faster growth)")
print("   - Time_h, OD_600nm, Biomass_gL")
print("\n3. ecoli_glycerol_batch.csv - Glycerol medium with protein production")
print("   - Time_h, OD_600nm, Glycerol_gL, Recombinant_Protein_gL, Biomass_gL")
print("\n4. ecoli_stress_batch.csv - High osmotic stress conditions")
print("   - Time_h, OD_600nm, NaCl_gL, Trehalose_gL, Biomass_gL")
print("\n5. ecoli_fedbatch.csv - Fed-batch fermentation (high cell density)")
print("   - Time_h, OD_600nm, FeedRate_mLh, Biomass_gL")

# Display sample of first dataset
print("\n📊 Sample of ecoli_glucose_batch.csv:")
print(df1.head(10))
print("\n...")
print(f"\n📈 Summary statistics for ecoli_glucose_batch.csv:")
print(f"Max OD: {df1['OD_600nm'].max():.2f}")
print(f"Max growth rate: {df1['GrowthRate_h'].max():.3f} h⁻¹")
print(f"Final glucose: {df1['Glucose_gL'].iloc[-1]:.2f} g/L")