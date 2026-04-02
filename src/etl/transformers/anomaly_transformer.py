"""
Anomaly Transformer - Fix negative values and illogical data

Single Responsibility: Only handles data anomalies (negative values, illogical relationships).
"""

import pandas as pd
import logging

from ..base.transformer import BaseTransformer

logger = logging.getLogger(__name__)


class AnomalyTransformer(BaseTransformer):
    """
    Detects and fixes data anomalies.
    
    Handles:
        - Negative values in count columns (set to 0)
        - Illogical data: Deaths + Recovered > Confirmed
    """
    
    def __init__(self, count_columns: list = None):
        """
        Initialize AnomalyTransformer.
        
        Args:
            count_columns: List of columns that should be non-negative
                          (default: ['Confirmed', 'Deaths', 'Recovered'])
        """
        self._count_columns = count_columns or ['Confirmed', 'Deaths', 'Recovered']
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix data anomalies.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with anomalies fixed
        """
        logger.info(f"{self.get_name()}: Fixing data anomalies...")
        df = df.copy()
        
        # Fix negative values
        df = self._fix_negative_values(df)
        
        # Fix illogical relationships
        df = self._fix_illogical_data(df)
        
        logger.info(f"{self.get_name()}: Anomaly fixing complete")
        return df
    
    def _fix_negative_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Set negative values to 0 in count columns."""
        for col in self._count_columns:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    df.loc[df[col] < 0, col] = 0
                    logger.info(f"  {col}: Fixed {negative_count:,} negative values")
        return df
    
    def _fix_illogical_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix cases where Deaths + Recovered > Confirmed."""
        if not all(col in df.columns for col in ['Confirmed', 'Deaths', 'Recovered']):
            return df
            
        invalid_mask = df['Deaths'] + df['Recovered'] > df['Confirmed']
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            # Case 1: Deaths alone exceed Confirmed - reset both
            high_deaths = invalid_mask & (df['Deaths'] > df['Confirmed'])
            df.loc[high_deaths, 'Deaths'] = 0
            df.loc[high_deaths, 'Recovered'] = 0
            
            # Case 2: Only combined exceeds - adjust Recovered
            remaining_invalid = invalid_mask & ~high_deaths
            df.loc[remaining_invalid, 'Recovered'] = (
                df.loc[remaining_invalid, 'Confirmed'] - 
                df.loc[remaining_invalid, 'Deaths']
            ).clip(lower=0)
            
            logger.info(f"  Fixed {invalid_count:,} records with illogical data "
                       f"(Deaths + Recovered > Confirmed)")
        
        return df
