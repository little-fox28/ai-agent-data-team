"""
CSV Extractor - Concrete implementation of BaseExtractor

Extracts COVID-19 data from CSV files with validation.
"""

import pandas as pd
import logging
from typing import Dict, Any

from ..base.extractor import BaseExtractor

logger = logging.getLogger(__name__)


class CSVExtractor(BaseExtractor):
    """
    Concrete extractor for CSV files.
    
    Implements:
        - extract(): Load CSV data into DataFrame
        - validate(): Validate schema and data quality
    """
    
    REQUIRED_COLUMNS = [
        'ObservationDate', 'Country/Region', 
        'Confirmed', 'Deaths', 'Recovered'
    ]
    
    def __init__(self, filepath: str, encoding: str = 'utf-8'):
        """
        Initialize CSV extractor.
        
        Args:
            filepath: Path to the CSV file
            encoding: File encoding (default: utf-8)
        """
        self._filepath = filepath
        self._encoding = encoding
    
    def extract(self) -> pd.DataFrame:
        """
        Extract data from CSV file.
        
        Returns:
            pd.DataFrame: Raw COVID-19 data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing
        """
        logger.info(f"Extracting data from {self._filepath}...")
        
        try:
            df = pd.read_csv(self._filepath, encoding=self._encoding)
            logger.info(f"Loaded {len(df):,} records with {len(df.columns)} columns")
            
            # Validate required columns exist
            missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            
            return df
            
        except FileNotFoundError:
            logger.error(f"File not found: {self._filepath}")
            raise
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            raise
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the extracted data quality.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            dict: Validation metrics and flags
        """
        logger.info("Validating extracted data...")
        
        validation = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'null_countries': int(df['Country/Region'].isnull().sum()),
            'null_dates': int(df['ObservationDate'].isnull().sum()),
            'null_confirmed': int(df['Confirmed'].isnull().sum()),
            'negative_confirmed': int((df['Confirmed'] < 0).sum()),
            'negative_deaths': int((df['Deaths'] < 0).sum()),
            'negative_recovered': int((df['Recovered'] < 0).sum()),
            'is_valid': True
        }
        
        # Check for critical issues
        if validation['null_countries'] > 0 or validation['null_dates'] > 0:
            validation['is_valid'] = False
            
        logger.info(f"Validation complete: {validation['total_records']} records, "
                   f"valid={validation['is_valid']}")
        
        return validation
