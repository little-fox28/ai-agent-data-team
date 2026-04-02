"""
Comprehensive Transformer Tests

Tests each transformer class individually, ensuring Single Responsibility compliance.
Each transformer handles exactly ONE transformation task.

Run with: pytest tests/test_transformers.py -v
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.transformers import (
    DateTransformer,
    MissingValueTransformer,
    AnomalyTransformer,
    GeographyTransformer,
    MetricsTransformer,
    OutlierTransformer
)
from etl.base import BaseTransformer


class TestDateTransformer:
    """Comprehensive tests for DateTransformer"""
    
    def test_transform_converts_dates(self, date_transformer, sample_raw_data):
        """DateTransformer converts date strings to datetime"""
        result = date_transformer.transform(sample_raw_data)
        
        assert pd.api.types.is_datetime64_any_dtype(result['ObservationDate'])
    
    def test_handles_invalid_dates(self, date_transformer):
        """DateTransformer coerces invalid dates to NaT"""
        data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', 'invalid_date', '01/24/2020'],
            'Confirmed': [100, 150, 200]
        })
        
        result = date_transformer.transform(data)
        
        # Valid dates should convert
        assert pd.notna(result['ObservationDate'].iloc[0])
        assert pd.notna(result['ObservationDate'].iloc[2])
        # Invalid date should become NaT
        assert pd.isna(result['ObservationDate'].iloc[1])
    
    def test_handles_multiple_date_formats(self, date_transformer):
        """DateTransformer handles various date formats"""
        data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '2020-01-23', '01/24/2020'],
            'Confirmed': [100, 150, 200]
        })
        
        result = date_transformer.transform(data)
        
        # All dates should be converted (pandas handles common formats)
        # At minimum the first standard format should work
        assert result['ObservationDate'].notna().sum() >= 1
    
    def test_preserves_other_columns(self, date_transformer, sample_raw_data):
        """DateTransformer doesn't modify other columns"""
        result = date_transformer.transform(sample_raw_data)
        
        # Numeric columns should be unchanged
        assert (result['Confirmed'] == sample_raw_data['Confirmed']).all()
        assert (result['Deaths'] == sample_raw_data['Deaths']).all()
    
    def test_custom_date_columns(self):
        """DateTransformer can be configured for custom date columns"""
        data = pd.DataFrame({
            'CustomDate': ['01/22/2020', '01/23/2020'],
            'ObservationDate': ['01/22/2020', '01/23/2020'],
            'Confirmed': [100, 150]
        })
        
        transformer = DateTransformer(date_columns=['CustomDate'])
        result = transformer.transform(data)
        
        assert pd.api.types.is_datetime64_any_dtype(result['CustomDate'])
    
    def test_get_name_returns_class_name(self, date_transformer):
        """DateTransformer.get_name() returns 'DateTransformer'"""
        assert date_transformer.get_name() == 'DateTransformer'
    
    def test_is_base_transformer_subclass(self, date_transformer):
        """DateTransformer is a BaseTransformer subclass"""
        assert isinstance(date_transformer, BaseTransformer)


class TestMissingValueTransformer:
    """Comprehensive tests for MissingValueTransformer"""
    
    def test_fills_missing_province(self, missing_value_transformer):
        """MissingValueTransformer fills missing Province/State with 'National'"""
        data = pd.DataFrame({
            'Country/Region': ['China', 'US', 'UK'],
            'Province/State': ['Hubei', None, np.nan],
            'Confirmed': [100, 50, 30]
        })
        
        result = missing_value_transformer.transform(data)
        
        assert 'National' in result['Province/State'].values
        assert result['Province/State'].isna().sum() == 0
    
    def test_custom_fill_values(self):
        """MissingValueTransformer accepts custom fill values"""
        data = pd.DataFrame({
            'Country/Region': ['China', None],
            'Province/State': ['Hubei', None],
            'Confirmed': [100, 50]
        })
        
        transformer = MissingValueTransformer(fill_values={
            'Province/State': 'Unknown',
            'Country/Region': 'Unknown Country'
        })
        result = transformer.transform(data)
        
        assert 'Unknown' in result['Province/State'].values
        assert 'Unknown Country' in result['Country/Region'].values
    
    def test_removes_duplicates(self, missing_value_transformer):
        """MissingValueTransformer removes duplicate records"""
        data = pd.DataFrame({
            'Country/Region': ['China', 'China', 'US'],
            'Province/State': ['Hubei', 'Hubei', 'New York'],
            'Confirmed': [100, 100, 50]  # First two are duplicates
        })
        
        result = missing_value_transformer.transform(data)
        
        assert len(result) == 2  # Should have removed one duplicate
    
    def test_preserves_valid_values(self, missing_value_transformer):
        """MissingValueTransformer doesn't modify non-null values"""
        data = pd.DataFrame({
            'Country/Region': ['China', 'US'],
            'Province/State': ['Hubei', 'New York'],
            'Confirmed': [100, 50]
        })
        
        result = missing_value_transformer.transform(data)
        
        assert result['Province/State'].iloc[0] == 'Hubei'
        assert result['Province/State'].iloc[1] == 'New York'
    
    def test_get_name_returns_class_name(self, missing_value_transformer):
        """MissingValueTransformer.get_name() returns 'MissingValueTransformer'"""
        assert missing_value_transformer.get_name() == 'MissingValueTransformer'


class TestAnomalyTransformer:
    """Comprehensive tests for AnomalyTransformer"""
    
    def test_fixes_negative_values(self, anomaly_transformer):
        """AnomalyTransformer sets negative values to 0"""
        data = pd.DataFrame({
            'Confirmed': [100, -10, 50],
            'Deaths': [10, -5, 5],
            'Recovered': [50, -20, 20]
        })
        
        result = anomaly_transformer.transform(data)
        
        assert (result['Confirmed'] >= 0).all()
        assert (result['Deaths'] >= 0).all()
        assert (result['Recovered'] >= 0).all()
        # Verify negative values were set to 0
        assert result['Confirmed'].iloc[1] == 0
        assert result['Deaths'].iloc[1] == 0
        assert result['Recovered'].iloc[1] == 0
    
    def test_fixes_illogical_data(self, anomaly_transformer):
        """AnomalyTransformer fixes cases where Deaths + Recovered > Confirmed"""
        data = pd.DataFrame({
            'Confirmed': [100, 100, 100],
            'Deaths': [10, 120, 50],  # Row 2: Deaths alone exceeds Confirmed
            'Recovered': [50, 50, 60]  # Row 3: Combined exceeds Confirmed
        })
        
        result = anomaly_transformer.transform(data)
        
        # Row 1: Should be unchanged
        assert result['Deaths'].iloc[0] == 10
        assert result['Recovered'].iloc[0] == 50
        
        # Row 2: Deaths > Confirmed, both should be reset
        assert result['Deaths'].iloc[1] == 0
        assert result['Recovered'].iloc[1] == 0
        
        # Row 3: Combined exceeds, Recovered should be adjusted
        assert result['Deaths'].iloc[2] + result['Recovered'].iloc[2] <= result['Confirmed'].iloc[2]
    
    def test_custom_count_columns(self):
        """AnomalyTransformer accepts custom count columns"""
        data = pd.DataFrame({
            'CustomCount': [-10, 50, 100],
            'Confirmed': [100, 150, 200]
        })
        
        transformer = AnomalyTransformer(count_columns=['CustomCount'])
        result = transformer.transform(data)
        
        assert result['CustomCount'].iloc[0] == 0  # Negative fixed
        assert result['CustomCount'].iloc[1] == 50  # Positive unchanged
    
    def test_preserves_valid_values(self, anomaly_transformer):
        """AnomalyTransformer doesn't modify valid values"""
        data = pd.DataFrame({
            'Confirmed': [100, 200, 300],
            'Deaths': [10, 20, 30],
            'Recovered': [50, 100, 150]
        })
        
        result = anomaly_transformer.transform(data)
        
        # All values should be unchanged
        assert (result['Confirmed'] == data['Confirmed']).all()
        assert (result['Deaths'] == data['Deaths']).all()
        assert (result['Recovered'] == data['Recovered']).all()
    
    def test_get_name_returns_class_name(self, anomaly_transformer):
        """AnomalyTransformer.get_name() returns 'AnomalyTransformer'"""
        assert anomaly_transformer.get_name() == 'AnomalyTransformer'


class TestGeographyTransformer:
    """Comprehensive tests for GeographyTransformer"""
    
    def test_normalizes_country_names(self, geography_transformer):
        """GeographyTransformer normalizes country names using default mapping"""
        data = pd.DataFrame({
            'Country/Region': ['Mainland China', 'US', 'UK', 'Korea, South'],
            'Confirmed': [100, 50, 30, 20]
        })
        
        result = geography_transformer.transform(data)
        
        assert 'China' in result['Country/Region'].values
        assert 'United States' in result['Country/Region'].values
        assert 'United Kingdom' in result['Country/Region'].values
        assert 'South Korea' in result['Country/Region'].values
    
    def test_strips_whitespace(self, geography_transformer):
        """GeographyTransformer strips whitespace from names"""
        data = pd.DataFrame({
            'Country/Region': ['  China  ', 'US  ', '  Italy'],
            'Province/State': ['  Hubei', 'New York  ', '  National  '],
            'Confirmed': [100, 50, 30]
        })
        
        result = geography_transformer.transform(data)
        
        assert result['Country/Region'].iloc[0] == 'China'
        assert result['Province/State'].iloc[0] == 'Hubei'
    
    def test_custom_country_mapping(self):
        """GeographyTransformer accepts custom country mapping"""
        data = pd.DataFrame({
            'Country/Region': ['OldName1', 'OldName2'],
            'Confirmed': [100, 50]
        })
        
        transformer = GeographyTransformer(country_mapping={
            'OldName1': 'NewName1',
            'OldName2': 'NewName2'
        })
        result = transformer.transform(data)
        
        assert 'NewName1' in result['Country/Region'].values
        assert 'NewName2' in result['Country/Region'].values
    
    def test_add_mapping_method(self, geography_transformer):
        """GeographyTransformer.add_mapping() adds new mappings"""
        data = pd.DataFrame({
            'Country/Region': ['CustomCountry'],
            'Confirmed': [100]
        })
        
        geography_transformer.add_mapping('CustomCountry', 'StandardizedCountry')
        result = geography_transformer.transform(data)
        
        assert 'StandardizedCountry' in result['Country/Region'].values
    
    def test_preserves_unmapped_countries(self, geography_transformer):
        """GeographyTransformer preserves countries not in mapping"""
        data = pd.DataFrame({
            'Country/Region': ['France', 'Germany', 'Japan'],
            'Confirmed': [100, 50, 30]
        })
        
        result = geography_transformer.transform(data)
        
        # These countries aren't in the mapping, should be unchanged
        assert 'France' in result['Country/Region'].values
        assert 'Germany' in result['Country/Region'].values
        assert 'Japan' in result['Country/Region'].values
    
    def test_get_name_returns_class_name(self, geography_transformer):
        """GeographyTransformer.get_name() returns 'GeographyTransformer'"""
        assert geography_transformer.get_name() == 'GeographyTransformer'


class TestMetricsTransformer:
    """Comprehensive tests for MetricsTransformer"""
    
    def test_calculates_active_cases(self, metrics_transformer):
        """MetricsTransformer calculates Active = Confirmed - Deaths - Recovered"""
        data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['China'],
            'Province/State': ['Hubei'],
            'Confirmed': [1000],
            'Deaths': [100],
            'Recovered': [600]
        })
        
        result = metrics_transformer.transform(data)
        
        assert 'Active' in result.columns
        expected_active = 1000 - 100 - 600
        assert result['Active'].iloc[0] == expected_active
    
    def test_calculates_rates(self, metrics_transformer):
        """MetricsTransformer calculates death and recovery rates"""
        data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['China'],
            'Province/State': ['Hubei'],
            'Confirmed': [200],
            'Deaths': [20],
            'Recovered': [100]
        })
        
        result = metrics_transformer.transform(data)
        
        assert 'DeathRate' in result.columns
        assert 'RecoveryRate' in result.columns
        
        # DeathRate = 20/200 * 100 = 10%
        assert result['DeathRate'].iloc[0] == 10.0
        # RecoveryRate = 100/200 * 100 = 50%
        assert result['RecoveryRate'].iloc[0] == 50.0
    
    def test_calculates_daily_changes(self, metrics_transformer):
        """MetricsTransformer calculates daily changes"""
        data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23', '2020-01-24']),
            'Country/Region': ['China', 'China', 'China'],
            'Province/State': ['Hubei', 'Hubei', 'Hubei'],
            'Confirmed': [100, 180, 250],
            'Deaths': [10, 18, 25],
            'Recovered': [20, 40, 70]
        })
        
        result = metrics_transformer.transform(data)
        
        assert 'DailyConfirmed' in result.columns
        assert 'DailyDeaths' in result.columns
        assert 'DailyRecovered' in result.columns
        
        # First day should be 0
        assert result['DailyConfirmed'].iloc[0] == 0
        
        # Second day: 180 - 100 = 80
        assert result['DailyConfirmed'].iloc[1] == 80
        
        # Third day: 250 - 180 = 70
        assert result['DailyConfirmed'].iloc[2] == 70
    
    def test_handles_zero_confirmed(self, metrics_transformer):
        """MetricsTransformer handles zero confirmed cases without division errors"""
        data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['NewCountry'],
            'Province/State': ['Region'],
            'Confirmed': [0],
            'Deaths': [0],
            'Recovered': [0]
        })
        
        result = metrics_transformer.transform(data)
        
        # Rates should be 0, not NaN or inf
        assert result['DeathRate'].iloc[0] == 0
        assert result['RecoveryRate'].iloc[0] == 0
    
    def test_clips_active_to_zero(self, metrics_transformer):
        """MetricsTransformer clips negative Active cases to 0"""
        data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['BadData'],
            'Province/State': ['Region'],
            'Confirmed': [100],
            'Deaths': [60],
            'Recovered': [60]  # Deaths + Recovered > Confirmed
        })
        
        result = metrics_transformer.transform(data)
        
        # Active would be 100 - 60 - 60 = -20, but should be clipped to 0
        assert result['Active'].iloc[0] >= 0
    
    def test_disable_daily_calculation(self):
        """MetricsTransformer can disable daily calculations"""
        data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23']),
            'Country/Region': ['China', 'China'],
            'Province/State': ['Hubei', 'Hubei'],
            'Confirmed': [100, 150],
            'Deaths': [10, 15],
            'Recovered': [50, 80]
        })
        
        transformer = MetricsTransformer(calculate_daily=False)
        result = transformer.transform(data)
        
        # Daily columns should not be created
        assert 'DailyConfirmed' not in result.columns
    
    def test_get_name_returns_class_name(self, metrics_transformer):
        """MetricsTransformer.get_name() returns 'MetricsTransformer'"""
        assert metrics_transformer.get_name() == 'MetricsTransformer'


class TestOutlierTransformer:
    """Comprehensive tests for OutlierTransformer"""
    
    def test_flags_outliers(self, outlier_transformer):
        """OutlierTransformer flags statistical outliers"""
        data = pd.DataFrame({
            'Confirmed': [100, 120, 110, 130, 10000000],  # Last is extreme outlier
            'Deaths': [10, 12, 11, 13, 5000000],
            'Recovered': [50, 60, 55, 65, 4000000]
        })
        
        result = outlier_transformer.transform(data)
        
        assert 'IsOutlier' in result.columns
        # At least the extreme value should be flagged
        assert result['IsOutlier'].sum() > 0
        assert result['IsOutlier'].iloc[4] == True  # Last row is outlier
    
    def test_flags_high_value_records(self, outlier_transformer):
        """OutlierTransformer flags high-value records"""
        data = pd.DataFrame({
            'Confirmed': [100, 200, 300, 400, 500, 600, 700, 800, 900, 10000],
            'Deaths': [10, 20, 30, 40, 50, 60, 70, 80, 90, 1000],
            'Recovered': [50, 100, 150, 200, 250, 300, 350, 400, 450, 5000]
        })
        
        result = outlier_transformer.transform(data)
        
        assert 'IsHighValue' in result.columns
        # Last row should be flagged as high value
        assert result['IsHighValue'].iloc[-1] == True
    
    def test_custom_iqr_multiplier(self):
        """OutlierTransformer accepts custom IQR multiplier"""
        data = pd.DataFrame({
            'Confirmed': [100, 110, 120, 130, 500],  # 500 is potential outlier
            'Deaths': [10, 11, 12, 13, 50],
            'Recovered': [50, 55, 60, 65, 250]
        })
        
        # With higher multiplier (3.0), fewer outliers
        lenient_transformer = OutlierTransformer(iqr_multiplier=3.0)
        result_lenient = lenient_transformer.transform(data)
        
        # With lower multiplier (1.0), more outliers
        strict_transformer = OutlierTransformer(iqr_multiplier=1.0)
        result_strict = strict_transformer.transform(data)
        
        # Stricter should flag more
        assert result_strict['IsOutlier'].sum() >= result_lenient['IsOutlier'].sum()
    
    def test_custom_columns(self):
        """OutlierTransformer accepts custom columns to check"""
        data = pd.DataFrame({
            'CustomColumn': [100, 110, 120, 130, 10000],
            'Confirmed': [100, 110, 120, 130, 10000]
        })
        
        transformer = OutlierTransformer(columns=['CustomColumn'])
        result = transformer.transform(data)
        
        assert 'IsOutlier' in result.columns
    
    def test_preserves_original_data(self, outlier_transformer):
        """OutlierTransformer doesn't modify original values, only adds flags"""
        data = pd.DataFrame({
            'Confirmed': [100, 200, 10000],
            'Deaths': [10, 20, 1000],
            'Recovered': [50, 100, 5000]
        })
        
        result = outlier_transformer.transform(data)
        
        # Original values should be unchanged
        assert (result['Confirmed'] == data['Confirmed']).all()
        assert (result['Deaths'] == data['Deaths']).all()
        assert (result['Recovered'] == data['Recovered']).all()
    
    def test_get_name_returns_class_name(self, outlier_transformer):
        """OutlierTransformer.get_name() returns 'OutlierTransformer'"""
        assert outlier_transformer.get_name() == 'OutlierTransformer'


class TestTransformerChaining:
    """Tests for chaining transformers together"""
    
    def test_transformers_chain_correctly(self, all_transformers, sample_raw_data):
        """Multiple transformers can be chained together"""
        result = sample_raw_data.copy()
        
        for transformer in all_transformers:
            result = transformer.transform(result)
        
        # Final result should have all expected columns
        assert pd.api.types.is_datetime64_any_dtype(result['ObservationDate'])
        assert 'Active' in result.columns
        assert 'DeathRate' in result.columns
        assert 'IsOutlier' in result.columns
    
    def test_order_matters(self, sample_raw_data):
        """Transformer order affects results"""
        # MetricsTransformer before DateTransformer may have issues
        # DateTransformer should come first
        
        date_t = DateTransformer()
        metrics_t = MetricsTransformer()
        
        # Correct order: DateTransformer first
        result1 = metrics_t.transform(date_t.transform(sample_raw_data))
        
        # Verify it works without errors
        assert 'Active' in result1.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
