"""
Date Transformer - Clean and convert date columns

Single Responsibility: Only handles date cleaning and conversion.
"""

import pandas as pd
import logging

from ..base.transformer import BaseTransformer

logger = logging.getLogger(__name__)


class DateTransformer(BaseTransformer):
    """
    Transforms date columns to proper datetime format.
    
    Handles:
        - ObservationDate conversion
        - Last Update conversion (with error handling)
        - Invalid date detection
    """
    
    def __init__(self, date_columns: list = None):
        """
        Initialize DateTransformer.
        
        Args:
            date_columns: List of date columns to transform 
                         (default: ['ObservationDate', 'Last Update'])
        """
        self._date_columns = date_columns or ['ObservationDate', 'Last Update']
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert date columns to datetime format.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with converted date columns
        """
        logger.info(f"{self.get_name()}: Converting date columns...")
        df = df.copy()
        
        for col in self._date_columns:
            if col in df.columns:
                original_nulls = df[col].isna().sum()
                df[col] = pd.to_datetime(df[col], errors='coerce')
                new_nulls = df[col].isna().sum()
                
                invalid_count = new_nulls - original_nulls
                if invalid_count > 0:
                    logger.warning(f"  {col}: {invalid_count} invalid dates coerced to NaT")
                else:
                    logger.info(f"  {col}: Successfully converted")
        
        logger.info(f"{self.get_name()}: Date conversion complete")
        return df
