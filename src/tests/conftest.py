"""
Pytest configuration and shared fixtures

This file contains fixtures that are available to all test modules.
Supports the OOP/SOLID ETL pipeline architecture.
"""

import pytest
import pandas as pd
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import OOP ETL components
from etl.base import BaseExtractor, BaseTransformer, BaseLoader
from etl.extractors import CSVExtractor
from etl.transformers import (
    DateTransformer, 
    MissingValueTransformer, 
    AnomalyTransformer,
    GeographyTransformer, 
    MetricsTransformer, 
    OutlierTransformer
)
from etl.loaders import CSVLoader, LatestSnapshotLoader, CountryAggregateLoader
from etl.pipeline import ETLPipeline


# ============== Mock Classes for Testing ==============

class MockExtractor(BaseExtractor):
    """Mock extractor for testing that returns predefined data."""
    
    def __init__(self, data: pd.DataFrame = None):
        self._data = data
    
    def extract(self) -> pd.DataFrame:
        if self._data is not None:
            return self._data.copy()
        return pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/23/2020'],
            'Country/Region': ['China', 'China'],
            'Province/State': ['Hubei', 'Hubei'],
            'Confirmed': [100, 150],
            'Deaths': [10, 15],
            'Recovered': [50, 80]
        })
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'null_countries': int(df['Country/Region'].isnull().sum()) if 'Country/Region' in df.columns else 0,
            'null_dates': int(df['ObservationDate'].isnull().sum()) if 'ObservationDate' in df.columns else 0,
            'is_valid': True
        }


class MockLoader(BaseLoader):
    """Mock loader for testing that captures output without writing files."""
    
    def __init__(self):
        self.loaded_data = None
        self.load_count = 0
    
    def load(self, df: pd.DataFrame) -> str:
        self.loaded_data = df.copy()
        self.load_count += 1
        return f"mock://output_{self.load_count}"


class MockTransformer(BaseTransformer):
    """Mock transformer for testing pipeline behavior."""
    
    def __init__(self, name: str = "MockTransformer", modify: bool = False):
        self._name = name
        self._modify = modify
        self.transform_count = 0
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.transform_count += 1
        result = df.copy()
        if self._modify:
            result['mock_column'] = 'modified'
        return result
    
    def get_name(self) -> str:
        return self._name


# ============== Transformer Fixtures ==============

@pytest.fixture
def date_transformer():
    """Create a DateTransformer instance."""
    return DateTransformer()


@pytest.fixture
def missing_value_transformer():
    """Create a MissingValueTransformer instance."""
    return MissingValueTransformer()


@pytest.fixture
def anomaly_transformer():
    """Create an AnomalyTransformer instance."""
    return AnomalyTransformer()


@pytest.fixture
def geography_transformer():
    """Create a GeographyTransformer instance."""
    return GeographyTransformer()


@pytest.fixture
def metrics_transformer():
    """Create a MetricsTransformer instance."""
    return MetricsTransformer()


@pytest.fixture
def outlier_transformer():
    """Create an OutlierTransformer instance."""
    return OutlierTransformer()


@pytest.fixture
def all_transformers():
    """Create list of all default transformers in pipeline order."""
    return [
        DateTransformer(),
        MissingValueTransformer(),
        AnomalyTransformer(),
        GeographyTransformer(),
        MetricsTransformer(),
        OutlierTransformer()
    ]


# ============== Mock Component Fixtures ==============

@pytest.fixture
def mock_extractor():
    """Create a MockExtractor instance."""
    return MockExtractor()


@pytest.fixture
def mock_loader():
    """Create a MockLoader instance."""
    return MockLoader()


@pytest.fixture
def mock_pipeline(sample_raw_data):
    """Create a mock ETL pipeline for testing."""
    extractor = MockExtractor(sample_raw_data)
    transformers = [DateTransformer(), MetricsTransformer()]
    loaders = [MockLoader()]
    return ETLPipeline(extractor, transformers, loaders)


@pytest.fixture
def sample_raw_data():
    """
    Fixture providing sample raw COVID-19 data for testing
    
    Returns:
        pd.DataFrame: Sample raw data with typical structure
    """
    return pd.DataFrame({
        'ObservationDate': ['01/22/2020', '01/23/2020', '01/24/2020', '01/22/2020', '01/23/2020'],
        'Country/Region': ['China', 'China', 'China', 'US', 'US'],
        'Province/State': ['Hubei', 'Hubei', 'Hubei', 'New York', 'New York'],
        'Confirmed': [100, 150, 200, 50, 75],
        'Deaths': [10, 15, 20, 5, 8],
        'Recovered': [30, 50, 80, 10, 20],
        'Last Update': ['01/22/2020 12:00', '01/23/2020 12:00', '01/24/2020 12:00', 
                       '01/22/2020 12:00', '01/23/2020 12:00']
    })


@pytest.fixture
def sample_cleaned_data():
    """
    Fixture providing sample cleaned COVID-19 data
    
    Returns:
        pd.DataFrame: Sample cleaned data with datetime and filled nulls
    """
    return pd.DataFrame({
        'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23', '2020-01-24']),
        'Country/Region': ['China', 'China', 'China'],
        'Province/State': ['Hubei', 'Hubei', 'Hubei'],
        'Confirmed': [100, 150, 200],
        'Deaths': [10, 15, 20],
        'Recovered': [30, 50, 80]
    })


@pytest.fixture
def sample_multi_country_data():
    """
    Fixture providing sample data with multiple countries and provinces
    
    Returns:
        pd.DataFrame: Sample data for aggregation testing
    """
    return pd.DataFrame({
        'ObservationDate': pd.to_datetime(['2020-01-22'] * 6),
        'Country/Region': ['China', 'China', 'China', 'US', 'US', 'Italy'],
        'Province/State': ['Hubei', 'Guangdong', 'Beijing', 'New York', 'California', 'National'],
        'Confirmed': [100, 50, 30, 75, 60, 40],
        'Deaths': [10, 5, 3, 8, 6, 4],
        'Recovered': [20, 10, 5, 15, 12, 8],
        'DailyConfirmed': [100, 50, 30, 75, 60, 40],
        'DailyDeaths': [10, 5, 3, 8, 6, 4],
        'DailyRecovered': [20, 10, 5, 15, 12, 8],
        'Active': [70, 35, 22, 52, 42, 28]
    })


@pytest.fixture
def sample_time_series_data():
    """
    Fixture providing sample time series data for one location
    
    Returns:
        pd.DataFrame: Sample time series for trend analysis
    """
    dates = pd.date_range(start='2020-01-22', periods=10, freq='D')
    return pd.DataFrame({
        'ObservationDate': dates,
        'Country/Region': ['China'] * 10,
        'Province/State': ['Hubei'] * 10,
        'Confirmed': [100, 150, 220, 300, 400, 520, 650, 800, 950, 1100],
        'Deaths': [10, 15, 22, 30, 42, 55, 70, 88, 105, 125],
        'Recovered': [20, 35, 55, 80, 110, 145, 185, 230, 280, 335]
    })


@pytest.fixture
def sample_data_with_issues():
    """
    Fixture providing sample data with common quality issues
    
    Returns:
        pd.DataFrame: Sample data with nulls, duplicates, and inconsistencies
    """
    return pd.DataFrame({
        'ObservationDate': ['01/22/2020', '01/22/2020', None, '01/24/2020', '01/25/2020'],
        'Country/Region': ['China', 'China', 'US', None, 'UK'],
        'Province/State': [None, None, 'New York', 'California', None],
        'Confirmed': [100, 100, 50, -10, 200],  # Duplicate and negative value
        'Deaths': [10, 10, 5, 2, 250],  # Deaths > Confirmed for UK
        'Recovered': [20, 20, 10, 0, 50]
    })


@pytest.fixture
def sample_edge_cases():
    """
    Fixture providing edge case data for testing robustness
    
    Returns:
        pd.DataFrame: Sample data with edge cases
    """
    return pd.DataFrame({
        'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23', '2020-01-24']),
        'Country/Region': ['Zero', 'Large', 'Correction'],
        'Province/State': ['National', 'National', 'National'],
        'Confirmed': [0, 1000000, 150],
        'Deaths': [0, 50000, 180],  # Correction: deaths > confirmed
        'Recovered': [0, 800000, 100]
    })


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
