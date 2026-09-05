"""Validate scale-up engine against literature datasets."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from modules.calcs import ScaleUpEngine, ScaleUpParameters


def validate():
    df = pd.read_csv("scale_up_validation_dataset.csv")
    engine = ScaleUpEngine()
    results = []

    for _, row in df.iterrows():
        lab_params = ScaleUpParameters(
            volume_L=row['lab_volume_L'],
            mu_max_h=row['lab_mu_max_h'],
            yield_g_g=row['lab_yield_g_g'],
            max_od=row['lab_max_od'],
            agitation_rpm=row['lab_agitation_rpm'],
            aeration_vvm=max(row['lab_aeration_vvm'], 0.01),
            power_input_W_m3=row['lab_power_input_W_m3'],
            kLa_h=row['lab_kLa_h'],
            vessel_diameter_m=row['lab_vessel_diameter_m'],
            impeller_diameter_m=row['lab_impeller_diameter_m'],
            aspect_ratio=row['lab_aspect_ratio'],
            OUR=8.5,
        )

        pred = engine.calculate_scale_up(
            lab_params,
            row['target_volume_L'],
            row['scaling_criterion']
        )

        mu_pred = pred['biological_performance']['mu_max_h']
        yield_pred = pred['biological_performance']['yield_g_g']
        max_od_pred = pred['biological_performance']['max_od']
        ag_pred = pred['operational_parameters']['agitation_rpm']
        kLa_pred = pred['oxygen_transfer']['kLa_predicted_h']

        def error(actual, expected):
            if expected == 0:
                return 0 if actual == 0 else np.inf
            return abs(actual - expected) / expected * 100

        entry = {
            'scenario': row['scenario_name'],
            'mu_pred': mu_pred,
            'mu_exp': row['expected_mu_max_h'],
            'mu_error_%': error(mu_pred, row['expected_mu_max_h']),
            'yield_pred': yield_pred,
            'yield_exp': row['expected_yield_g_g'],
            'yield_error_%': error(yield_pred, row['expected_yield_g_g']),
            'od_pred': max_od_pred,
            'od_exp': row['expected_max_od'],
            'od_error_%': error(max_od_pred, row['expected_max_od']),
            'ag_pred': ag_pred,
            'kLa_pred': kLa_pred,
        }
        # Optional expected columns (may not be in all CSVs)
        if 'expected_agitation_rpm' in row.index:
            entry['ag_exp'] = row['expected_agitation_rpm']
            entry['ag_error_%'] = error(ag_pred, row['expected_agitation_rpm'])
        if 'expected_kLa_h' in row.index:
            entry['kLa_exp'] = row['expected_kLa_h']
            entry['kLa_error_%'] = error(kLa_pred, row['expected_kLa_h'])
        results.append(entry)

    df_results = pd.DataFrame(results)

    print("\nScale-Up Validation Results")
    print("=" * 100)
    bio_cols = ['scenario', 'mu_pred', 'mu_exp', 'mu_error_%',
                'yield_pred', 'yield_exp', 'yield_error_%',
                'od_pred', 'od_exp', 'od_error_%']
    print(df_results[bio_cols].round(1).to_string(index=False))

    print("\n\nOperational Parameters")
    print("=" * 80)
    op_cols = ['scenario', 'ag_pred', 'kLa_pred']
    if 'ag_exp' in df_results.columns:
        op_cols.insert(2, 'ag_exp')
        op_cols.insert(3, 'ag_error_%')
    if 'kLa_exp' in df_results.columns:
        op_cols.append('kLa_exp')
        op_cols.append('kLa_error_%')
    print(df_results[[c for c in op_cols if c in df_results.columns]].round(1).to_string(index=False))

    print("\n\nSummary Statistics (errors in %):")
    print("-" * 60)
    for col in ['mu_error_%', 'yield_error_%', 'od_error_%', 'ag_error_%', 'kLa_error_%']:
        if col not in df_results.columns:
            continue
        values = df_results[col].replace([np.inf], np.nan).dropna()
        if values.empty:
            continue
        label = col.replace('_error_%', '')
        print(f"  {label:>8s}: mean={values.mean():5.1f}%  max={values.max():5.1f}%  "
              f"{'PASS' if values.max() < 30 else 'CHECK'}")

    bio_errors = df_results[['mu_error_%', 'yield_error_%', 'od_error_%']]
    n_pass = (bio_errors < 25).sum().sum()
    n_total = bio_errors.notna().sum().sum()
    print(f"\n  Biological predictions: {n_pass}/{n_total} within 25% tolerance")


if __name__ == "__main__":
    validate()
