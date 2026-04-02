"""
ETL Script: COVID-19 Data Cleaning and Preprocessing
======================================================

This script loads raw COVID-19 data, performs data quality checks,
cleaning, and preprocessing to prepare data for visualization and analysis.

Data Quality Issues Handled:
- Negative values in Confirmed, Deaths, Recovered columns
- Invalid logic: Deaths + Recovered > Confirmed
- Missing values in Province/State (will be filled with 'Unknown')
- Date format standardization
- Outlier detection and documentation
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_raw_data(filepath):
    """Load raw COVID-19 dataset."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df):,} records with {len(df.columns)} columns")
    return df

def clean_dates(df):
    """Convert date columns to datetime format."""
    print("\nCleaning date columns...")
    df['ObservationDate'] = pd.to_datetime(df['ObservationDate'])
    df['Last Update'] = pd.to_datetime(df['Last Update'], errors='coerce')
    
    # Log any issues
    missing_update_dates = df['Last Update'].isna().sum()
    if missing_update_dates > 0:
        print(f"  Warning: {missing_update_dates} records with invalid 'Last Update' dates")
    
    return df

def handle_missing_values(df):
    """Handle missing values appropriately."""
    print("\nHandling missing values...")
    
    # Fill missing Province/State with 'Unknown'
    missing_province = df['Province/State'].isna().sum()
    df['Province/State'] = df['Province/State'].fillna('Unknown')
    print(f"  Filled {missing_province:,} missing Province/State values with 'Unknown'")
    
    return df

def fix_data_anomalies(df):
    """Detect and fix data anomalies."""
    print("\nFixing data anomalies...")
    
    # Track anomalies for reporting
    anomalies = []
    
    # Issue 1: Negative values
    negative_confirmed = (df['Confirmed'] < 0).sum()
    negative_deaths = (df['Deaths'] < 0).sum()
    negative_recovered = (df['Recovered'] < 0).sum()
    
    if negative_confirmed > 0 or negative_deaths > 0 or negative_recovered > 0:
        print(f"  Found {negative_confirmed} negative Confirmed, {negative_deaths} Deaths, {negative_recovered} Recovered")
        
        # Option: Set negative values to 0 (most conservative approach for counts)
        df.loc[df['Confirmed'] < 0, 'Confirmed'] = 0
        df.loc[df['Deaths'] < 0, 'Deaths'] = 0
        df.loc[df['Recovered'] < 0, 'Recovered'] = 0
        
        print(f"  -> Corrected all negative values to 0")
        anomalies.append(f"Fixed {negative_confirmed + negative_deaths + negative_recovered} negative values")
    
    # Issue 2: Illogical data (Deaths + Recovered > Confirmed)
    invalid_logic_mask = df['Deaths'] + df['Recovered'] > df['Confirmed']
    invalid_logic = df[invalid_logic_mask].copy()
    if len(invalid_logic) > 0:
        print(f"  Found {len(invalid_logic)} records where Deaths + Recovered > Confirmed")
        
        # Adjust Recovered downward to maintain logic
        # If Deaths already exceed Confirmed, set both Deaths and Recovered to 0
        high_deaths = df.loc[invalid_logic_mask, 'Deaths'] > df.loc[invalid_logic_mask, 'Confirmed']
        
        df.loc[invalid_logic_mask & high_deaths, 'Deaths'] = 0
        df.loc[invalid_logic_mask & high_deaths, 'Recovered'] = 0
        
        # For others, adjust Recovered = Confirmed - Deaths
        df.loc[invalid_logic_mask & ~high_deaths, 'Recovered'] = (
            df.loc[invalid_logic_mask & ~high_deaths, 'Confirmed'] - 
            df.loc[invalid_logic_mask & ~high_deaths, 'Deaths']
        )
        print(f"  -> Adjusted Recovered and Deaths values to maintain logical consistency")
        anomalies.append(f"Fixed {len(invalid_logic)} illogical records")
    
    # Ensure all metrics are >= 0 after adjustments
    df['Recovered'] = df['Recovered'].clip(lower=0)
    
    return df, anomalies

def standardize_geography(df):
    """Standardize country/region names."""
    print("\nStandardizing geographic data...")
    
    # Fix known inconsistencies
    replacements = {
        'Mainland China': 'China',
        'Korea': 'South Korea',
        'North Ireland': 'Northern Ireland',
        'Hong Kong SAR': 'Hong Kong',
        'Taiwan': 'Taiwan',
        'Macau SAR': 'Macau',
    }
    
    changes = 0
    for old, new in replacements.items():
        mask = df['Country/Region'] == old
        changes += mask.sum()
        df.loc[mask, 'Country/Region'] = new
    
    if changes > 0:
        print(f"  Standardized {changes:,} country/region names")
    
    return df

def create_derived_metrics(df):
    """Create derived columns for analysis."""
    print("\nCreating derived metrics...")
    
    # Active cases = Confirmed - Deaths - Recovered
    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']
    df['Active'] = df['Active'].clip(lower=0)  # Ensure non-negative
    
    # Calculate rates (avoid division by zero)
    df['Death_Rate'] = np.where(
        df['Confirmed'] > 0,
        (df['Deaths'] / df['Confirmed'] * 100).round(2),
        0
    )
    
    df['Recovery_Rate'] = np.where(
        df['Confirmed'] > 0,
        (df['Recovered'] / df['Confirmed'] * 100).round(2),
        0
    )
    
    df['Active_Rate'] = np.where(
        df['Confirmed'] > 0,
        (df['Active'] / df['Confirmed'] * 100).round(2),
        0
    )
    
    print(f"  Created 4 derived metrics: Active, Death_Rate, Recovery_Rate, Active_Rate")
    
    return df

def detect_outliers(df):
    """Detect and document outliers."""
    print("\nDetecting outliers...")
    
    # Using IQR method for each metric
    outliers_data = []
    
    for col in ['Confirmed', 'Deaths', 'Recovered']:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outlier_count = outlier_mask.sum()
        
        if outlier_count > 0:
            print(f"  {col}: {outlier_count:,} outliers (bounds: {lower_bound:.0f} to {upper_bound:.0f})")
    
    # Mark high-impact records (for awareness, not removal)
    df['Is_Outlier'] = False
    high_confirmed = df['Confirmed'] > df['Confirmed'].quantile(0.95)
    df.loc[high_confirmed, 'Is_Outlier'] = True
    
    print(f"  Flagged {high_confirmed.sum():,} high-value records for awareness")
    
    return df

def generate_data_quality_report(df, anomalies):
    """Generate a data quality report."""
    print("\n" + "=" * 80)
    print("DATA QUALITY REPORT")
    print("=" * 80)
    
    print(f"\nDataset Summary:")
    print(f"  Total Records: {len(df):,}")
    print(f"  Date Range: {df['ObservationDate'].min().date()} to {df['ObservationDate'].max().date()}")
    print(f"  Total Days: {(df['ObservationDate'].max() - df['ObservationDate'].min()).days}")
    print(f"  Unique Countries: {df['Country/Region'].nunique()}")
    print(f"  Unique Regions: {df['Province/State'].nunique()}")
    
    print(f"\nKey Metrics (after cleaning):")
    for col in ['Confirmed', 'Deaths', 'Recovered', 'Active']:
        print(f"\n  {col}:")
        print(f"    Total: {df[col].sum():,}")
        print(f"    Mean: {df[col].mean():,.0f}")
        print(f"    Median: {df[col].median():,.0f}")
        print(f"    Max: {df[col].max():,}")
    
    print(f"\nData Quality Issues Fixed:")
    for issue in anomalies:
        print(f"  [OK] {issue}")
    
    print(f"\nMissing Values:")
    print(f"  Province/State (now filled): 0")
    print(f"  Last Update dates (invalid): {df['Last Update'].isna().sum():,}")
    
    print("\n" + "=" * 80)

def save_processed_data(df, output_dir, output_file):
    """Save processed dataset."""
    print(f"\nSaving processed data...")
    
    # Create directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, output_file)
    df.to_csv(filepath, index=False)
    print(f"  Saved to: {filepath}")
    print(f"  File size: {os.path.getsize(filepath) / (1024*1024):.1f} MB")
    
    return filepath

def main():
    """Main ETL pipeline."""
    print("\n" + "=" * 80)
    print("COVID-19 DATA CLEANING AND PREPROCESSING")
    print("=" * 80)
    
    # Configuration
    raw_data_path = 'data/raw/covid_19_data.csv'
    output_dir = 'data/processed'
    output_file = 'covid_cleaned.csv'
    
    # Run pipeline
    df = load_raw_data(raw_data_path)
    df = clean_dates(df)
    df = handle_missing_values(df)
    df, anomalies = fix_data_anomalies(df)
    df = standardize_geography(df)
    df = create_derived_metrics(df)
    df = detect_outliers(df)
    
    # Generate report
    generate_data_quality_report(df, anomalies)
    
    # Save output
    output_path = save_processed_data(df, output_dir, output_file)
    
    print(f"\n[OK] Data cleaning completed successfully!")
    print(f"[OK] Processed data ready for visualization and analysis")
    
    return df

if __name__ == '__main__':
    df = main()
