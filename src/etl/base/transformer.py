"""
Abstract Base Class for Data Transformers

Implements Single Responsibility and Open/Closed principles.
Each transformer handles ONE specific transformation task.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseTransformer(ABC):
    """
    Abstract base class for data transformation.
    
    Single Responsibility: Each transformer handles exactly one transformation.
    Open/Closed: New transformers extend this class without modifying it.
    Liskov Substitution: All transformers can be used interchangeably.
    
    Subclasses must implement:
        - transform(): Apply transformation and return modified DataFrame
    """
    
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply transformation to the DataFrame.
        
        Args:
            df: Input DataFrame to transform
            
        Returns:
            pd.DataFrame: Transformed DataFrame
        """
        pass
    
    def get_name(self) -> str:
        """
        Get the transformer name for logging purposes.
        
        Returns:
            str: Name of the transformer class
        """
        return self.__class__.__name__
