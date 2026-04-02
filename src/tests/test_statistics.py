"""
Statistical Calculation Tests

Tests to validate statistical calculations, aggregations, and derived metrics
using the OOP MetricsTransformer and other transformers.

Run with: pytest tests/test_statistics.py -v
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import OOP ETL components
from etl.transformers import MetricsTransformer, DateTransformer
from etl.loaders import CountryAggregateLoader


class TestRateCalculations:
    """Tests for rate calculations (CFR, Recovery Rate) using MetricsTransformer"""
    
    def test_case_fatality_rate_calculation(self, metrics_transformer):
        """Test Case Fatality Rate (CFR) calculation via MetricsTransformer"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23']),
            'Country/Region': ['China', 'China'],
            'Province/State': ['Hubei', 'Hubei'],
            'Confirmed': [100, 200],
            'Deaths': [10, 30],
            'Recovered': [20, 50]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # DeathRate = (Deaths / Confirmed) * 100
        expected_rate_1 = (10 / 100) * 100  # 10%
        expected_rate_2 = (30 / 200) * 100  # 15%
        
        assert enriched.iloc[0]['DeathRate'] == expected_rate_1, \
            f"Expected DeathRate {expected_rate_1}, got {enriched.iloc[0]['DeathRate']}"
        assert enriched.iloc[1]['DeathRate'] == expected_rate_2, \
            f"Expected DeathRate {expected_rate_2}, got {enriched.iloc[1]['DeathRate']}"
    
    def test_recovery_rate_calculation(self, metrics_transformer):
        """Test Recovery Rate calculation via MetricsTransformer"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23']),
            'Country/Region': ['China', 'China'],
            'Province/State': ['Hubei', 'Hubei'],
            'Confirmed': [100, 200],
            'Deaths': [10, 20],
            'Recovered': [50, 120]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # Recovery Rate = (Recovered / Confirmed) * 100
        expected_rr_1 = (50 / 100) * 100  # 50%
        expected_rr_2 = (120 / 200) * 100  # 60%
        
        assert enriched.iloc[0]['RecoveryRate'] == expected_rr_1, \
            f"Expected Recovery Rate {expected_rr_1}, got {enriched.iloc[0]['RecoveryRate']}"
        assert enriched.iloc[1]['RecoveryRate'] == expected_rr_2, \
            f"Expected Recovery Rate {expected_rr_2}, got {enriched.iloc[1]['RecoveryRate']}"
    
    def test_zero_division_handling(self, metrics_transformer):
        """Test that MetricsTransformer handles division by zero gracefully"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['New Country'],
            'Province/State': ['Region'],
            'Confirmed': [0],
            'Deaths': [0],
            'Recovered': [0]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # When Confirmed = 0, rates should be 0 (not NaN or inf)
        assert enriched.iloc[0]['DeathRate'] == 0, "DeathRate should be 0 when confirmed is 0"
        assert enriched.iloc[0]['RecoveryRate'] == 0, "Recovery Rate should be 0 when confirmed is 0"


class TestDailyCaseCalculations:
    """Tests for daily new cases calculations using MetricsTransformer"""
    
    def test_daily_confirmed_calculation(self, metrics_transformer):
        """Test daily new confirmed cases calculation"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23', '2020-01-24']),
            'Country/Region': ['China', 'China', 'China'],
            'Province/State': ['Hubei', 'Hubei', 'Hubei'],
            'Confirmed': [100, 150, 200],
            'Deaths': [10, 15, 20],
            'Recovered': [20, 30, 50]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # First day should be 0 (no previous day)
        assert enriched.iloc[0]['DailyConfirmed'] == 0, \
            "First day DailyConfirmed should be 0"
        
        # Second day: 150 - 100 = 50
        assert enriched.iloc[1]['DailyConfirmed'] == 50, \
            f"Expected 50 daily confirmed, got {enriched.iloc[1]['DailyConfirmed']}"
        
        # Third day: 200 - 150 = 50
        assert enriched.iloc[2]['DailyConfirmed'] == 50, \
            f"Expected 50 daily confirmed, got {enriched.iloc[2]['DailyConfirmed']}"
    
    def test_daily_deaths_calculation(self, metrics_transformer):
        """Test daily new deaths calculation"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23', '2020-01-24']),
            'Country/Region': ['US', 'US', 'US'],
            'Province/State': ['New York', 'New York', 'New York'],
            'Confirmed': [100, 150, 200],
            'Deaths': [5, 10, 18],
            'Recovered': [20, 30, 40]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # First day should be 0
        assert enriched.iloc[0]['DailyDeaths'] == 0
        
        # Second day: 10 - 5 = 5
        assert enriched.iloc[1]['DailyDeaths'] == 5
        
        # Third day: 18 - 10 = 8
        assert enriched.iloc[2]['DailyDeaths'] == 8
    
    def test_negative_daily_values_handling(self, metrics_transformer):
        """Test that negative daily values (from data corrections) are clipped to 0"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23', '2020-01-24']),
            'Country/Region': ['Italy', 'Italy', 'Italy'],
            'Province/State': ['National', 'National', 'National'],
            'Confirmed': [100, 150, 140],  # Day 3 has correction (decrease)
            'Deaths': [10, 12, 11],
            'Recovered': [20, 30, 35]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # Daily values should be clipped to 0 (no negative daily cases)
        assert (enriched['DailyConfirmed'] >= 0).all(), \
            "DailyConfirmed contains negative values"
        assert (enriched['DailyDeaths'] >= 0).all(), \
            "DailyDeaths contains negative values"
        assert (enriched['DailyRecovered'] >= 0).all(), \
            "DailyRecovered contains negative values"


class TestActiveCasesCalculation:
    """Tests for active cases calculation using MetricsTransformer"""
    
    def test_active_cases_formula(self, metrics_transformer):
        """Test Active = Confirmed - Deaths - Recovered"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23']),
            'Country/Region': ['Spain', 'Spain'],
            'Province/State': ['National', 'National'],
            'Confirmed': [1000, 1500],
            'Deaths': [100, 150],
            'Recovered': [600, 900]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # Active = 1000 - 100 - 600 = 300
        expected_active_1 = 1000 - 100 - 600
        assert enriched.iloc[0]['Active'] == expected_active_1, \
            f"Expected {expected_active_1} active cases, got {enriched.iloc[0]['Active']}"
        
        # Active = 1500 - 150 - 900 = 450
        expected_active_2 = 1500 - 150 - 900
        assert enriched.iloc[1]['Active'] == expected_active_2, \
            f"Expected {expected_active_2} active cases, got {enriched.iloc[1]['Active']}"
    
    def test_active_cases_non_negative(self, metrics_transformer):
        """Test that active cases are clipped to 0 (never negative)"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['Germany'],
            'Province/State': ['National'],
            'Confirmed': [100],
            'Deaths': [50],
            'Recovered': [60]  # Deaths + Recovered > Confirmed
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # Active should be clipped to 0, not negative
        assert enriched.iloc[0]['Active'] >= 0, \
            "Active cases should not be negative"


class TestAggregationFunctions:
    """Tests for data aggregation using CountryAggregateLoader"""
    
    def test_sum_aggregation(self, tmp_path):
        """Test summation across provinces using CountryAggregateLoader"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-22', '2020-01-22']),
            'Country/Region': ['China', 'China', 'China'],
            'Province/State': ['Hubei', 'Guangdong', 'Beijing'],
            'Confirmed': [100, 50, 30],
            'Deaths': [10, 5, 3],
            'Recovered': [20, 10, 5],
            'DailyConfirmed': [100, 50, 30],
            'DailyDeaths': [10, 5, 3],
            'DailyRecovered': [20, 10, 5],
            'Active': [70, 35, 22]
        })
        
        loader = CountryAggregateLoader(str(tmp_path), 'by_country.csv')
        output_path = loader.load(sample_data)
        
        # Load and verify
        country_agg = pd.read_csv(output_path)
        
        # Should have one record for China on this date
        assert len(country_agg) == 1
        
        # Total confirmed should be sum of provinces
        expected_total = 100 + 50 + 30
        assert country_agg.iloc[0]['Confirmed'] == expected_total, \
            f"Expected {expected_total} confirmed, got {country_agg.iloc[0]['Confirmed']}"
    
    def test_mean_calculation(self):
        """Test mean calculation"""
        values = pd.Series([10, 20, 30, 40, 50])
        
        mean_value = values.mean()
        expected_mean = 30.0
        
        assert mean_value == expected_mean, \
            f"Expected mean {expected_mean}, got {mean_value}"
    
    def test_median_calculation(self):
        """Test median calculation"""
        # Odd number of values
        values_odd = pd.Series([10, 20, 30, 40, 50])
        median_odd = values_odd.median()
        assert median_odd == 30.0
        
        # Even number of values
        values_even = pd.Series([10, 20, 30, 40])
        median_even = values_even.median()
        assert median_even == 25.0


class TestTimeSeriesAggregations:
    """Tests for time series aggregations"""
    
    def test_daily_aggregation(self):
        """Test aggregation by date"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-22', '2020-01-23', '2020-01-23']),
            'Country/Region': ['China', 'US', 'China', 'US'],
            'Province/State': ['Hubei', 'New York', 'Hubei', 'New York'],
            'Confirmed': [100, 50, 150, 75],
            'Deaths': [10, 5, 15, 8],
            'Recovered': [20, 10, 30, 15]
        })
        
        # Group by date and sum
        daily_totals = sample_data.groupby('ObservationDate').agg({
            'Confirmed': 'sum',
            'Deaths': 'sum',
            'Recovered': 'sum'
        })
        
        # Day 1: 100 + 50 = 150
        assert daily_totals.iloc[0]['Confirmed'] == 150
        
        # Day 2: 150 + 75 = 225
        assert daily_totals.iloc[1]['Confirmed'] == 225
    
    def test_cumulative_calculation(self):
        """Test cumulative sum calculation"""
        daily_cases = pd.Series([10, 20, 15, 30, 25])
        
        cumulative = daily_cases.cumsum()
        
        expected = [10, 30, 45, 75, 100]
        assert cumulative.tolist() == expected, \
            f"Expected {expected}, got {cumulative.tolist()}"
    
    def test_moving_average(self):
        """Test rolling average calculation"""
        daily_cases = pd.Series([10, 20, 30, 40, 50])
        
        # 3-day moving average
        rolling_avg = daily_cases.rolling(window=3).mean()
        
        # First two values will be NaN
        assert pd.isna(rolling_avg.iloc[0])
        assert pd.isna(rolling_avg.iloc[1])
        
        # Third value: (10 + 20 + 30) / 3 = 20.0
        assert rolling_avg.iloc[2] == 20.0


class TestStatisticalAccuracy:
    """Tests to verify statistical accuracy with known results using MetricsTransformer"""
    
    def test_known_sample_statistics(self, metrics_transformer):
        """Test calculations against known correct results"""
        # Known dataset with verified statistics
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23', '2020-01-24']),
            'Country/Region': ['TestCountry', 'TestCountry', 'TestCountry'],
            'Province/State': ['Region1', 'Region1', 'Region1'],
            'Confirmed': [100, 150, 200],
            'Deaths': [10, 15, 25],
            'Recovered': [30, 50, 80]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # Verify final day statistics
        final_row = enriched.iloc[2]
        
        # DeathRate = 25 / 200 * 100 = 12.5%
        assert final_row['DeathRate'] == 12.5
        
        # Recovery Rate = 80 / 200 * 100 = 40%
        assert final_row['RecoveryRate'] == 40.0
        
        # Active = 200 - 25 - 80 = 95
        assert final_row['Active'] == 95
        
        # Daily Confirmed = 200 - 150 = 50
        assert final_row['DailyConfirmed'] == 50
    
    def test_edge_case_all_zeros(self, metrics_transformer):
        """Test calculations with all zero values"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['NoData'],
            'Province/State': ['Region'],
            'Confirmed': [0],
            'Deaths': [0],
            'Recovered': [0]
        })
        
        enriched = metrics_transformer.transform(sample_data)
        
        # All rates should be 0
        assert enriched.iloc[0]['DeathRate'] == 0
        assert enriched.iloc[0]['RecoveryRate'] == 0
        assert enriched.iloc[0]['Active'] == 0


class TestMetricsTransformerSingleResponsibility:
    """Tests to verify MetricsTransformer adheres to Single Responsibility Principle"""
    
    def test_metrics_transformer_only_adds_metrics(self, metrics_transformer):
        """MetricsTransformer should only add metric columns, not modify original data"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22']),
            'Country/Region': ['China'],
            'Province/State': ['Hubei'],
            'Confirmed': [100],
            'Deaths': [10],
            'Recovered': [50]
        })
        
        original_cols = set(sample_data.columns)
        result = metrics_transformer.transform(sample_data)
        
        # Original columns should still be present
        assert original_cols.issubset(set(result.columns))
        
        # Original values should be unchanged
        assert result.iloc[0]['Confirmed'] == 100
        assert result.iloc[0]['Deaths'] == 10
        assert result.iloc[0]['Recovered'] == 50
    
    def test_metrics_transformer_adds_expected_columns(self, metrics_transformer):
        """MetricsTransformer should add specific metric columns"""
        sample_data = pd.DataFrame({
            'ObservationDate': pd.to_datetime(['2020-01-22', '2020-01-23']),
            'Country/Region': ['China', 'China'],
            'Province/State': ['Hubei', 'Hubei'],
            'Confirmed': [100, 150],
            'Deaths': [10, 15],
            'Recovered': [50, 80]
        })
        
        result = metrics_transformer.transform(sample_data)
        
        # Should have added these metric columns
        expected_new_cols = ['Active', 'DeathRate', 'RecoveryRate', 
                           'DailyConfirmed', 'DailyDeaths', 'DailyRecovered']
        
        for col in expected_new_cols:
            assert col in result.columns, f"Missing expected column: {col}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
