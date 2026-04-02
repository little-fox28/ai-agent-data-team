"""
Abstract Base Class for Data Extractors

Implements Interface Segregation and Dependency Inversion principles.
Each extractor must implement extract() and validate() methods.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseExtractor(ABC):
    """
    Abstract base class for data extraction.
    
    Subclasses must implement:
        - extract(): Load data from source and return DataFrame
        - validate(): Validate loaded data and return validation results
    """
    
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """
        Extract data from the source.
        
        Returns:
            pd.DataFrame: Extracted data as a pandas DataFrame
        """
        pass
    
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the extracted data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            dict: Validation results containing metrics and flags
        """
        pass
