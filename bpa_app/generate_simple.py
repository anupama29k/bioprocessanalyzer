import pandas as pd
import numpy as np

print('Generating validation datasets...')

# Standard E. coli
time = np.arange(0, 24, 0.5)
od = 0.05 * np.exp(0.45 * time)
od = np.minimum(od, 8.5) + np.random.normal(0, 0.03, len(od))
glucose = 10 - (od - 0.05) / 0.85
acetate = np.maximum(0, 0.12 * (od - 2) * (time - 1.5) / 10)

df = pd.DataFrame({'Time_h': time, 'OD_600nm': od, 'Glucose_gL': glucose, 'Acetate_gL': acetate})
df.to_csv('standard_ecoli_product.csv', index=False)
print('✅ standard_ecoli_product.csv created')

# Fast growth
time2 = np.arange(0, 16, 0.5)
od2 = 0.08 * np.exp(0.92 * time2)
od2 = np.minimum(od2, 11.5) + np.random.normal(0, 0.05, len(od2))
protein = 0.15 * od2 * (1 - np.exp(-0.5 * time2))

df2 = pd.DataFrame({'Time_h': time2, 'OD_600nm': od2, 'Protein_gL': protein})
df2.to_csv('fast_growth_product.csv', index=False)
print('✅ fast_growth_product.csv created')

print('\n✅ All datasets generated!')
print('Run: streamlit run app.py')
