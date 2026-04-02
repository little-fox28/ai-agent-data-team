"""
CSV Loaders - Concrete implementations of BaseLoader

Provides multiple CSV output formats for different use cases.
"""

import pandas as pd
import numpy as np
import logging
import os
from typing import Optional

from ..base.loader import BaseLoader

logger = logging.getLogger(__name__)


class CSVLoader(BaseLoader):
    """
    Saves processed data to CSV file.
    
    Primary loader for the full cleaned dataset.
    """
    
    def __init__(self, output_dir: str, filename: str = 'covid_cleaned.csv'):
        """
        Initialize CSVLoader.
        
        Args:
            output_dir: Directory to save the CSV file
            filename: Name of the output file
        """
        self._output_dir = output_dir
        self._filename = filename
    
    def load(self, df: pd.DataFrame) -> str:
        """
        Save DataFrame to CSV.
        
        Args:
            df: DataFrame to save
            
        Returns:
            str: Path to saved file
        """
        logger.info(f"{self.get_name()}: Saving to CSV...")
        
        # Ensure directory exists
        os.makedirs(self._output_dir, exist_ok=True)
        
        filepath = os.path.join(self._output_dir, self._filename)
        df.to_csv(filepath, index=False)
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"  Saved {len(df):,} records to {filepath} ({file_size:.2f} MB)")
        
        return filepath


class LatestSnapshotLoader(BaseLoader):
    """
    Saves the latest snapshot (most recent date per location).
    
    Useful for dashboards showing current state.
    """
    
    def __init__(self, output_dir: str, filename: str = 'covid_latest.csv'):
        """
        Initialize LatestSnapshotLoader.
        
        Args:
            output_dir: Directory to save the CSV file
            filename: Name of the output file
        """
        self._output_dir = output_dir
        self._filename = filename
    
    def load(self, df: pd.DataFrame) -> str:
        """
        Save latest snapshot to CSV.
        
        Args:
            df: DataFrame to save
            
        Returns:
            str: Path to saved file
        """
        logger.info(f"{self.get_name()}: Creating latest snapshot...")
        
        # Ensure directory exists
        os.makedirs(self._output_dir, exist_ok=True)
        
        # Get most recent record per location
        group_cols = ['Country/Region']
        if 'Province/State' in df.columns:
            group_cols.append('Province/State')
        
        latest = df.groupby(group_cols).last().reset_index()
        
        filepath = os.path.join(self._output_dir, self._filename)
        latest.to_csv(filepath, index=False)
        
        logger.info(f"  Saved {len(latest):,} location snapshots to {filepath}")
        
        return filepath


class CountryAggregateLoader(BaseLoader):
    """
    Saves country-level aggregated data.
    
    Aggregates provincial data to country level.
    """
    
    def __init__(self, output_dir: str, filename: str = 'covid_by_country.csv'):
        """
        Initialize CountryAggregateLoader.
        
        Args:
            output_dir: Directory to save the CSV file
            filename: Name of the output file
        """
        self._output_dir = output_dir
        self._filename = filename
    
    def load(self, df: pd.DataFrame) -> str:
        """
        Save country-level aggregate to CSV.
        
        Args:
            df: DataFrame to save
            
        Returns:
            str: Path to saved file
        """
        logger.info(f"{self.get_name()}: Creating country aggregate...")
        
        # Ensure directory exists
        os.makedirs(self._output_dir, exist_ok=True)
        
        # Define aggregation columns
        agg_cols = {
            'Confirmed': 'sum',
            'Deaths': 'sum',
            'Recovered': 'sum',
            'Active': 'sum'
        }
        
        # Add daily columns if they exist
        for col in ['DailyConfirmed', 'DailyDeaths', 'DailyRecovered']:
            if col in df.columns:
                agg_cols[col] = 'sum'
        
        # Filter to columns that exist
        agg_cols = {k: v for k, v in agg_cols.items() if k in df.columns}
        
        # Aggregate
        if 'ObservationDate' in df.columns:
            country_df = df.groupby(['Country/Region', 'ObservationDate']).agg(agg_cols).reset_index()
        else:
            country_df = df.groupby(['Country/Region']).agg(agg_cols).reset_index()
        
        # Recalculate rates
        if 'Confirmed' in country_df.columns and country_df['Confirmed'].sum() > 0:
            if 'Deaths' in country_df.columns:
                country_df['DeathRate'] = np.where(
                    country_df['Confirmed'] > 0,
                    (country_df['Deaths'] / country_df['Confirmed'] * 100).round(2),
                    0
                )
            if 'Recovered' in country_df.columns:
                country_df['RecoveryRate'] = np.where(
                    country_df['Confirmed'] > 0,
                    (country_df['Recovered'] / country_df['Confirmed'] * 100).round(2),
                    0
                )
        
        filepath = os.path.join(self._output_dir, self._filename)
        country_df.to_csv(filepath, index=False)
        
        logger.info(f"  Saved {len(country_df):,} country-level records to {filepath}")
        
        return filepath
