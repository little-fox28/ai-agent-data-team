"""
Abstract Base Class for Data Loaders

Implements Interface Segregation and Dependency Inversion principles.
Each loader handles saving data to a specific destination.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Any


class BaseLoader(ABC):
    """
    Abstract base class for data loading.
    
    Single Responsibility: Each loader saves to one specific destination.
    Open/Closed: New loaders extend this class without modifying it.
    
    Subclasses must implement:
        - load(): Save data to destination and return result path/info
    """
    
    @abstractmethod
    def load(self, df: pd.DataFrame) -> str:
        """
        Load (save) the DataFrame to the destination.
        
        Args:
            df: DataFrame to save
            
        Returns:
            str: Path or identifier of the saved data
        """
        pass
    
    def get_name(self) -> str:
        """
        Get the loader name for logging purposes.
        
        Returns:
            str: Name of the loader class
        """
        return self.__class__.__name__
