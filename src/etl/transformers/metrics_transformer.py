"""
Metrics Transformer - Create derived metrics

Single Responsibility: Only handles metric calculations and derivations.
"""

import pandas as pd
import numpy as np
import logging

from ..base.transformer import BaseTransformer

logger = logging.getLogger(__name__)


class MetricsTransformer(BaseTransformer):
    """
    Creates derived metrics for analysis.
    
    Generates:
        - Active cases (Confirmed - Deaths - Recovered)
        - Death Rate (Deaths / Confirmed * 100)
        - Recovery Rate (Recovered / Confirmed * 100)
        - Active Rate (Active / Confirmed * 100)
        - Daily changes (difference from previous day)
    """
    
    def __init__(self, calculate_daily: bool = True):
        """
        Initialize MetricsTransformer.
        
        Args:
            calculate_daily: Whether to calculate daily changes (default: True)
        """
        self._calculate_daily = calculate_daily
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with derived metrics
        """
        logger.info(f"{self.get_name()}: Creating derived metrics...")
        df = df.copy()
        
        # Sort for proper calculation
        if 'ObservationDate' in df.columns:
            sort_cols = ['Country/Region']
            if 'Province/State' in df.columns:
                sort_cols.append('Province/State')
            sort_cols.append('ObservationDate')
            df = df.sort_values(sort_cols)
        
        # Calculate Active cases
        df = self._calculate_active(df)
        
        # Calculate rates
        df = self._calculate_rates(df)
        
        # Calculate daily changes
        if self._calculate_daily:
            df = self._calculate_daily_changes(df)
        
        logger.info(f"{self.get_name()}: Metrics creation complete")
        return df
    
    def _calculate_active(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate active cases."""
        if all(col in df.columns for col in ['Confirmed', 'Deaths', 'Recovered']):
            df['Active'] = (df['Confirmed'] - df['Deaths'] - df['Recovered']).clip(lower=0)
            logger.info("  Created: Active cases")
        return df
    
    def _calculate_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate death rate, recovery rate, and active rate."""
        if 'Confirmed' in df.columns:
            # Death Rate
            if 'Deaths' in df.columns:
                df['DeathRate'] = np.where(
                    df['Confirmed'] > 0,
                    (df['Deaths'] / df['Confirmed'] * 100).round(2),
                    0
                )
                logger.info("  Created: DeathRate")
            
            # Recovery Rate
            if 'Recovered' in df.columns:
                df['RecoveryRate'] = np.where(
                    df['Confirmed'] > 0,
                    (df['Recovered'] / df['Confirmed'] * 100).round(2),
                    0
                )
                logger.info("  Created: RecoveryRate")
            
            # Active Rate
            if 'Active' in df.columns:
                df['ActiveRate'] = np.where(
                    df['Confirmed'] > 0,
                    (df['Active'] / df['Confirmed'] * 100).round(2),
                    0
                )
                logger.info("  Created: ActiveRate")
        
        return df
    
    def _calculate_daily_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily changes for key metrics."""
        if 'ObservationDate' not in df.columns:
            return df
            
        group_cols = ['Country/Region']
        if 'Province/State' in df.columns:
            group_cols.append('Province/State')
        
        for col in ['Confirmed', 'Deaths', 'Recovered']:
            if col in df.columns:
                daily_col = f'Daily{col}'
                df[daily_col] = df.groupby(group_cols)[col].diff().fillna(0).clip(lower=0)
                logger.info(f"  Created: {daily_col}")
        
        return df
