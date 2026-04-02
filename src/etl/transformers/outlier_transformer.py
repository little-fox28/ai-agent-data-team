"""
Outlier Transformer - Detect and flag outliers

Single Responsibility: Only handles outlier detection and flagging.
"""

import pandas as pd
import numpy as np
import logging
from typing import List

from ..base.transformer import BaseTransformer

logger = logging.getLogger(__name__)


class OutlierTransformer(BaseTransformer):
    """
    Detects and flags outliers using IQR method.
    
    Strategy:
        - Uses Interquartile Range (IQR) for detection
        - Flags outliers rather than removing them (preserves data)
        - Also flags high-value records for awareness
    """
    
    def __init__(
        self, 
        columns: List[str] = None, 
        iqr_multiplier: float = 1.5,
        percentile_threshold: float = 0.95
    ):
        """
        Initialize OutlierTransformer.
        
        Args:
            columns: Columns to check for outliers (default: ['Confirmed', 'Deaths', 'Recovered'])
            iqr_multiplier: Multiplier for IQR bounds (default: 1.5)
            percentile_threshold: Percentile for high-value flagging (default: 0.95)
        """
        self._columns = columns or ['Confirmed', 'Deaths', 'Recovered']
        self._iqr_multiplier = iqr_multiplier
        self._percentile_threshold = percentile_threshold
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect and flag outliers.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with outlier flags
        """
        logger.info(f"{self.get_name()}: Detecting outliers...")
        df = df.copy()
        
        # Initialize outlier flag
        df['IsOutlier'] = False
        
        for col in self._columns:
            if col not in df.columns:
                continue
                
            # Calculate IQR bounds
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - self._iqr_multiplier * IQR
            upper_bound = Q3 + self._iqr_multiplier * IQR
            
            # Detect outliers
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                df.loc[outlier_mask, 'IsOutlier'] = True
                logger.info(f"  {col}: {outlier_count:,} outliers "
                           f"(bounds: {lower_bound:.0f} to {upper_bound:.0f})")
        
        # Flag high-value records
        if 'Confirmed' in df.columns:
            high_threshold = df['Confirmed'].quantile(self._percentile_threshold)
            high_mask = df['Confirmed'] > high_threshold
            high_count = high_mask.sum()
            
            # Create separate high-value flag
            df['IsHighValue'] = high_mask
            logger.info(f"  Flagged {high_count:,} high-value records "
                       f"(>{self._percentile_threshold*100}th percentile)")
        
        total_outliers = df['IsOutlier'].sum()
        logger.info(f"{self.get_name()}: Flagged {total_outliers:,} total outliers")
        
        return df
