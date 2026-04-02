"""
Missing Value Transformer - Handle missing values appropriately

Single Responsibility: Only handles missing value imputation.
"""

import pandas as pd
import logging
from typing import Dict, Any

from ..base.transformer import BaseTransformer

logger = logging.getLogger(__name__)


class MissingValueTransformer(BaseTransformer):
    """
    Handles missing values in the dataset.
    
    Strategies:
        - Province/State: Fill with 'National' (for national-level data)
        - Numeric columns: Can be configured for different strategies
    """
    
    def __init__(self, fill_values: Dict[str, Any] = None):
        """
        Initialize MissingValueTransformer.
        
        Args:
            fill_values: Dictionary mapping column names to fill values
                        (default: {'Province/State': 'National'})
        """
        self._fill_values = fill_values or {
            'Province/State': 'National'
        }
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values based on configured strategy.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with missing values handled
        """
        logger.info(f"{self.get_name()}: Handling missing values...")
        df = df.copy()
        
        for col, fill_value in self._fill_values.items():
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df[col] = df[col].fillna(fill_value)
                    logger.info(f"  {col}: Filled {missing_count:,} missing values with '{fill_value}'")
        
        # Remove duplicates while we're at it
        initial_count = len(df)
        df = df.drop_duplicates()
        duplicates_removed = initial_count - len(df)
        if duplicates_removed > 0:
            logger.info(f"  Removed {duplicates_removed:,} duplicate records")
        
        logger.info(f"{self.get_name()}: Missing value handling complete")
        return df
