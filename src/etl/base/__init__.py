"""
ETL Base classes module

Provides abstract base classes for the ETL pipeline following SOLID principles:
- BaseExtractor: Abstract class for data extraction
- BaseTransformer: Abstract class for data transformation
- BaseLoader: Abstract class for data loading
"""

from .extractor import BaseExtractor
from .transformer import BaseTransformer
from .loader import BaseLoader

__all__ = ['BaseExtractor', 'BaseTransformer', 'BaseLoader']
