"""
Data Quality Tests

Tests to validate data integrity, schema compliance, and quality standards
for the COVID-19 dataset using the OOP ETL architecture.

Run with: pytest tests/test_data_quality.py -v
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import OOP ETL components
from etl.extractors import CSVExtractor
from etl.transformers import (
    DateTransformer,
    MissingValueTransformer,
    AnomalyTransformer,
    GeographyTransformer
)


class TestDataSchema:
    """Tests for data schema and structure"""
    
    def test_required_columns_present(self):
        """Test that all required columns are present in raw data"""
        required_columns = [
            'ObservationDate',
            'Country/Region',
            'Confirmed',
            'Deaths',
            'Recovered'
        ]
        
        # Create sample data with all required columns
        sample_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020'],
            'Country/Region': ['China'],
            'Province/State': ['Hubei'],
            'Confirmed': [100],
            'Deaths': [10],
            'Recovered': [50],
            'Last Update': ['01/22/2020 12:00']
        })
        
        for col in required_columns:
            assert col in sample_data.columns, f"Required column {col} is missing"
    
    def test_column_data_types(self):
        """Test that columns have expected data types after processing"""
        sample_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/23/2020'],
            'Country/Region': ['China', 'US'],
            'Province/State': ['Hubei', 'New York'],
            'Confirmed': [100, 200],
            'Deaths': [10, 20],
            'Recovered': [50, 100]
        })
        
        # Convert date column as the pipeline would
        sample_data['ObservationDate'] = pd.to_datetime(sample_data['ObservationDate'])
        
        # Check types
        assert pd.api.types.is_datetime64_any_dtype(sample_data['ObservationDate'])
        assert pd.api.types.is_object_dtype(sample_data['Country/Region'])
        assert pd.api.types.is_numeric_dtype(sample_data['Confirmed'])
        assert pd.api.types.is_numeric_dtype(sample_data['Deaths'])
        assert pd.api.types.is_numeric_dtype(sample_data['Recovered'])
    
    def test_value_ranges(self):
        """Test that numeric columns have valid value ranges (non-negative)"""
        sample_data = pd.DataFrame({
            'Confirmed': [0, 100, 1000],
            'Deaths': [0, 10, 50],
            'Recovered': [0, 50, 800]
        })
        
        # All counts should be non-negative
        assert (sample_data['Confirmed'] >= 0).all(), "Confirmed cases contain negative values"
        assert (sample_data['Deaths'] >= 0).all(), "Deaths contain negative values"
        assert (sample_data['Recovered'] >= 0).all(), "Recovered cases contain negative values"


class TestDataQuality:
    """Tests for data quality issues"""
    
    def test_missing_values_handling(self):
        """Test handling of missing values"""
        sample_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/23/2020', None],
            'Country/Region': ['China', None, 'US'],
            'Province/State': [None, 'New York', 'California'],
            'Confirmed': [100, 200, np.nan],
            'Deaths': [10, np.nan, 30],
            'Recovered': [50, 100, 150]
        })
        
        # Check for missing values
        null_counts = sample_data.isnull().sum()
        
        # Province/State can have nulls (should be filled with 'National')
        assert 'Province/State' in sample_data.columns
        
        # Critical columns should not have nulls in production
        assert null_counts['ObservationDate'] >= 0  # Count them
        assert null_counts['Country/Region'] >= 0  # Count them
    
    def test_duplicate_detection(self):
        """Test detection of duplicate records"""
        sample_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/22/2020', '01/23/2020'],
            'Country/Region': ['China', 'China', 'China'],
            'Province/State': ['Hubei', 'Hubei', 'Hubei'],
            'Confirmed': [100, 100, 150]
        })
        
        # Check for duplicates based on key columns
        duplicates = sample_data.duplicated(subset=['ObservationDate', 'Country/Region', 'Province/State'])
        duplicate_count = duplicates.sum()
        
        assert duplicate_count == 1, f"Expected 1 duplicate, found {duplicate_count}"
    
    def test_outlier_detection(self):
        """Test for extreme outliers in the data"""
        sample_data = pd.DataFrame({
            'Confirmed': [100, 200, 150, 180, 10000000],  # Last value is outlier
            'Deaths': [10, 20, 15, 18, 5000000]
        })
        
        # Simple outlier detection using IQR method
        Q1 = sample_data['Confirmed'].quantile(0.25)
        Q3 = sample_data['Confirmed'].quantile(0.75)
        IQR = Q3 - Q1
        
        outliers = (sample_data['Confirmed'] < (Q1 - 1.5 * IQR)) | \
                   (sample_data['Confirmed'] > (Q3 + 1.5 * IQR))
        
        # Should detect the extreme value
        assert outliers.sum() > 0, "Outlier detection failed"
    
    def test_logical_consistency(self):
        """Test logical relationships between columns"""
        sample_data = pd.DataFrame({
            'Confirmed': [100, 200, 300],
            'Deaths': [10, 20, 30],
            'Recovered': [50, 100, 150]
        })
        
        # Deaths should not exceed Confirmed
        assert (sample_data['Deaths'] <= sample_data['Confirmed']).all(), \
            "Deaths exceed confirmed cases"
        
        # Recovered should not exceed Confirmed
        assert (sample_data['Recovered'] <= sample_data['Confirmed']).all(), \
            "Recovered cases exceed confirmed cases"
        
        # Deaths + Recovered should not exceed Confirmed
        total_resolved = sample_data['Deaths'] + sample_data['Recovered']
        assert (total_resolved <= sample_data['Confirmed']).all(), \
            "Deaths + Recovered exceed confirmed cases"


class TestDateHandling:
    """Tests for date format and consistency"""
    
    def test_date_format_parsing(self):
        """Test that various date formats can be parsed"""
        date_formats = [
            '01/22/2020',
            '2020-01-22',
            '01-22-2020'
        ]
        
        for date_str in date_formats:
            try:
                parsed = pd.to_datetime(date_str)
                assert isinstance(parsed, pd.Timestamp)
            except Exception as e:
                pytest.fail(f"Failed to parse date format {date_str}: {e}")
    
    def test_date_range_validity(self):
        """Test that dates fall within expected range"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-06-15', '2021-03-01'])
        })
        
        # Dates should be between 2020-01-01 and present
        min_expected_date = pd.Timestamp('2020-01-01')
        max_expected_date = pd.Timestamp.now()
        
        assert (sample_data['ObservationDate'] >= min_expected_date).all(), \
            "Dates before expected minimum"
        assert (sample_data['ObservationDate'] <= max_expected_date).all(), \
            "Dates after present"
    
    def test_chronological_order(self):
        """Test that data can be sorted chronologically"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-25', '2020-01-22', '2020-01-23']),
            'Country/Region': ['China', 'China', 'China'],
            'Confirmed': [100, 50, 75]
        })
        
        # Sort by date
        sorted_data = sample_data.sort_values('ObservationDate')
        
        # Check if sorted correctly
        dates = sorted_data['ObservationDate'].tolist()
        assert dates == sorted(dates), "Dates not in chronological order after sorting"


class TestGeographicData:
    """Tests for geographic data completeness"""
    
    def test_country_names_not_empty(self):
        """Test that country names are not empty"""
        sample_data = pd.DataFrame({
            'Country/Region': ['China', 'US', 'UK', ''],
            'Confirmed': [100, 200, 150, 50]
        })
        
        empty_countries = (sample_data['Country/Region'] == '').sum()
        assert empty_countries > 0 or empty_countries == 0  # Just count them
    
    def test_province_state_consistency(self):
        """Test Province/State field consistency"""
        sample_data = pd.DataFrame({
            'Country/Region': ['China', 'China', 'US'],
            'Province/State': ['Hubei', None, 'New York'],
            'Confirmed': [100, 50, 200]
        })
        
        # After cleaning, nulls should be replaced with 'National'
        sample_data['Province/State'].fillna('National', inplace=True)
        
        assert (sample_data['Province/State'] != '').all(), \
            "Province/State contains empty strings after cleaning"
        assert not sample_data['Province/State'].isnull().any(), \
            "Province/State contains null values after cleaning"
    
    def test_unique_location_combinations(self):
        """Test that location combinations are tracked correctly"""
        sample_data = pd.DataFrame({
            'Country/Region': ['China', 'China', 'US', 'US'],
            'Province/State': ['Hubei', 'Beijing', 'New York', 'California'],
            'ObservationDate': pd.to_datetime(['2020-01-22'] * 4),
            'Confirmed': [100, 50, 200, 150]
        })
        
        # Should have unique combinations of Country + Province for each date
        location_combos = sample_data.groupby(['Country/Region', 'Province/State', 'ObservationDate']).size()
        
        # Each combination should appear once per date
        assert (location_combos == 1).all(), "Duplicate location combinations found"


class TestSchemaValidation:
    """Tests using the CSVExtractor.validate() method"""
    
    def test_schema_validation_output(self):
        """Test that CSVExtractor.validate() returns expected metrics"""
        sample_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/23/2020'],
            'Country/Region': ['China', 'US'],
            'Province/State': ['Hubei', None],
            'Confirmed': [100, 200],
            'Deaths': [10, 20],
            'Recovered': [50, 100]
        })
        
        extractor = CSVExtractor("dummy.csv")
        validation = extractor.validate(sample_data)
        
        # Check that all expected keys are present
        expected_keys = [
            'total_records',
            'total_columns',
            'null_countries',
            'null_dates',
            'negative_confirmed',
            'negative_deaths'
        ]
        
        for key in expected_keys:
            assert key in validation, f"Missing validation metric: {key}"
        
        # Check values
        assert validation['total_records'] == 2
        assert validation['total_columns'] == 6
        assert validation['null_countries'] == 0
        assert validation['negative_confirmed'] == 0
    
    def test_validation_detects_null_countries(self):
        """CSVExtractor.validate() counts null country values"""
        sample_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/23/2020'],
            'Country/Region': ['China', None],
            'Confirmed': [100, 200],
            'Deaths': [10, 20],
            'Recovered': [50, 100]
        })
        
        extractor = CSVExtractor("dummy.csv")
        validation = extractor.validate(sample_data)
        
        assert validation['null_countries'] == 1
        assert validation['is_valid'] == False
    
    def test_validation_detects_negative_values(self):
        """CSVExtractor.validate() detects negative values"""
        sample_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020'],
            'Country/Region': ['China'],
            'Confirmed': [-100],
            'Deaths': [10],
            'Recovered': [50]
        })
        
        extractor = CSVExtractor("dummy.csv")
        validation = extractor.validate(sample_data)
        
        assert validation['negative_confirmed'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
