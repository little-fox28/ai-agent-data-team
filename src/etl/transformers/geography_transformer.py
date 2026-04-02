"""
Geography Transformer - Standardize country and region names

Single Responsibility: Only handles geographic data normalization.
"""

import pandas as pd
import logging
from typing import Dict

from ..base.transformer import BaseTransformer

logger = logging.getLogger(__name__)


class GeographyTransformer(BaseTransformer):
    """
    Standardizes geographic names for consistency.
    
    Handles:
        - Country name variations (e.g., 'Mainland China' -> 'China')
        - Whitespace trimming
        - Common misspellings
    """
    
    DEFAULT_COUNTRY_MAPPING = {
        'Mainland China': 'China',
        'US': 'United States',
        'UK': 'United Kingdom',
        'Korea, South': 'South Korea',
        'Korea': 'South Korea',
        ' Azerbaijan': 'Azerbaijan',
        'Gambia, The': 'Gambia',
        'Bahamas, The': 'Bahamas',
        'Hong Kong SAR': 'Hong Kong',
        'Macau SAR': 'Macau',
        'North Ireland': 'Northern Ireland',
        'Taiwan*': 'Taiwan',
    }
    
    def __init__(self, country_mapping: Dict[str, str] = None):
        """
        Initialize GeographyTransformer.
        
        Args:
            country_mapping: Dictionary mapping old names to standardized names
                           (default: DEFAULT_COUNTRY_MAPPING)
        """
        self._country_mapping = country_mapping or self.DEFAULT_COUNTRY_MAPPING.copy()
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize geographic names.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with standardized geography
        """
        logger.info(f"{self.get_name()}: Standardizing geographic data...")
        df = df.copy()
        
        if 'Country/Region' in df.columns:
            # Apply country mapping
            changes = 0
            for old_name, new_name in self._country_mapping.items():
                mask = df['Country/Region'] == old_name
                changes += mask.sum()
                df.loc[mask, 'Country/Region'] = new_name
            
            # Strip whitespace
            df['Country/Region'] = df['Country/Region'].str.strip()
            
            if changes > 0:
                logger.info(f"  Standardized {changes:,} country/region names")
        
        if 'Province/State' in df.columns:
            df['Province/State'] = df['Province/State'].str.strip()
        
        logger.info(f"{self.get_name()}: Geographic standardization complete")
        return df
    
    def add_mapping(self, old_name: str, new_name: str) -> None:
        """
        Add a new country name mapping.
        
        Args:
            old_name: Original name to replace
            new_name: Standardized name
        """
        self._country_mapping[old_name] = new_name
