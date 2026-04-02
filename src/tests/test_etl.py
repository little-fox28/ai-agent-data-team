"""
Tests for OOP ETL Pipeline

Tests the new SOLID-compliant ETL architecture with:
- Abstract base classes (BaseExtractor, BaseTransformer, BaseLoader)
- Concrete implementations (CSVExtractor, transformers, loaders)
- Pipeline orchestration (ETLPipeline)

Run with: pytest tests/test_etl.py -v
"""

import pytest
import pandas as pd
import sys
import os
import tempfile
from pathlib import Path
from abc import ABC

# Add src directory to path
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


class TestBaseClasses:
    """Test that abstract base classes cannot be instantiated"""
    
    def test_base_extractor_cannot_be_instantiated(self):
        """BaseExtractor is abstract and should raise TypeError"""
        with pytest.raises(TypeError):
            BaseExtractor()
    
    def test_base_transformer_cannot_be_instantiated(self):
        """BaseTransformer is abstract and should raise TypeError"""
        with pytest.raises(TypeError):
            BaseTransformer()
    
    def test_base_loader_cannot_be_instantiated(self):
        """BaseLoader is abstract and should raise TypeError"""
        with pytest.raises(TypeError):
            BaseLoader()
    
    def test_base_classes_are_abc(self):
        """Base classes should be ABC subclasses"""
        assert issubclass(BaseExtractor, ABC)
        assert issubclass(BaseTransformer, ABC)
        assert issubclass(BaseLoader, ABC)


class TestCSVExtractor:
    """Tests for CSVExtractor"""
    
    def test_csv_extractor_requires_filepath(self):
        """CSVExtractor requires a filepath"""
        # Should work with filepath
        extractor = CSVExtractor("some/path.csv")
        assert extractor._filepath == "some/path.csv"
    
    def test_csv_extractor_extract_missing_file(self):
        """CSVExtractor.extract() raises FileNotFoundError for missing file"""
        extractor = CSVExtractor("nonexistent_file.csv")
        with pytest.raises(FileNotFoundError):
            extractor.extract()
    
    def test_csv_extractor_extract_with_valid_file(self, tmp_path):
        """CSVExtractor.extract() returns DataFrame from valid CSV"""
        # Create a temporary CSV file
        csv_file = tmp_path / "test_data.csv"
        test_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/23/2020'],
            'Country/Region': ['China', 'US'],
            'Province/State': ['Hubei', 'New York'],
            'Confirmed': [100, 50],
            'Deaths': [10, 5],
            'Recovered': [50, 20]
        })
        test_data.to_csv(csv_file, index=False)
        
        extractor = CSVExtractor(str(csv_file))
        result = extractor.extract()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'Confirmed' in result.columns
    
    def test_csv_extractor_validate(self, sample_raw_data):
        """CSVExtractor.validate() returns validation metrics"""
        extractor = CSVExtractor("dummy.csv")
        validation = extractor.validate(sample_raw_data)
        
        assert 'total_records' in validation
        assert 'total_columns' in validation
        assert 'null_countries' in validation
        assert 'null_dates' in validation
        assert 'is_valid' in validation
        assert validation['total_records'] == len(sample_raw_data)
    
    def test_csv_extractor_missing_columns_raises(self, tmp_path):
        """CSVExtractor raises ValueError for missing required columns"""
        csv_file = tmp_path / "incomplete.csv"
        test_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020'],
            'Country/Region': ['China']
            # Missing Confirmed, Deaths, Recovered
        })
        test_data.to_csv(csv_file, index=False)
        
        extractor = CSVExtractor(str(csv_file))
        with pytest.raises(ValueError, match="Missing required columns"):
            extractor.extract()


class TestTransformers:
    """Tests for individual transformer classes"""
    
    def test_date_transformer_converts_dates(self, sample_raw_data, date_transformer):
        """DateTransformer converts date strings to datetime"""
        result = date_transformer.transform(sample_raw_data)
        
        assert pd.api.types.is_datetime64_any_dtype(result['ObservationDate'])
    
    def test_missing_value_transformer_fills_province(self, missing_value_transformer):
        """MissingValueTransformer fills missing Province/State"""
        data = pd.DataFrame({
            'Country/Region': ['China', 'US'],
            'Province/State': ['Hubei', None],
            'Confirmed': [100, 50]
        })
        
        result = missing_value_transformer.transform(data)
        
        assert 'National' in result['Province/State'].values
        assert result['Province/State'].isna().sum() == 0
    
    def test_anomaly_transformer_fixes_negative_values(self, anomaly_transformer):
        """AnomalyTransformer fixes negative values"""
        data = pd.DataFrame({
            'Confirmed': [100, -10, 50],
            'Deaths': [10, -5, 5],
            'Recovered': [50, -20, 20]
        })
        
        result = anomaly_transformer.transform(data)
        
        assert (result['Confirmed'] >= 0).all()
        assert (result['Deaths'] >= 0).all()
        assert (result['Recovered'] >= 0).all()
    
    def test_geography_transformer_normalizes_countries(self, geography_transformer):
        """GeographyTransformer normalizes country names"""
        data = pd.DataFrame({
            'Country/Region': ['Mainland China', 'US', 'UK'],
            'Confirmed': [100, 50, 30]
        })
        
        result = geography_transformer.transform(data)
        
        assert 'China' in result['Country/Region'].values
        assert 'United States' in result['Country/Region'].values
        assert 'United Kingdom' in result['Country/Region'].values
    
    def test_metrics_transformer_calculates_active(self, metrics_transformer, sample_cleaned_data):
        """MetricsTransformer calculates active cases"""
        result = metrics_transformer.transform(sample_cleaned_data)
        
        assert 'Active' in result.columns
        # Active = Confirmed - Deaths - Recovered
        expected = sample_cleaned_data['Confirmed'] - sample_cleaned_data['Deaths'] - sample_cleaned_data['Recovered']
        assert (result['Active'] == expected).all()
    
    def test_metrics_transformer_calculates_rates(self, metrics_transformer, sample_cleaned_data):
        """MetricsTransformer calculates rates"""
        result = metrics_transformer.transform(sample_cleaned_data)
        
        assert 'DeathRate' in result.columns
        assert 'RecoveryRate' in result.columns
    
    def test_outlier_transformer_flags_outliers(self, outlier_transformer):
        """OutlierTransformer flags statistical outliers"""
        data = pd.DataFrame({
            'Confirmed': [100, 200, 150, 180, 10000000],  # Last is outlier
            'Deaths': [10, 20, 15, 18, 5000000],
            'Recovered': [50, 100, 75, 90, 4000000]
        })
        
        result = outlier_transformer.transform(data)
        
        assert 'IsOutlier' in result.columns
        assert result['IsOutlier'].sum() > 0
    
    def test_transformer_get_name(self, date_transformer, metrics_transformer):
        """Transformers return their class name via get_name()"""
        assert date_transformer.get_name() == 'DateTransformer'
        assert metrics_transformer.get_name() == 'MetricsTransformer'


class TestLoaders:
    """Tests for loader classes"""
    
    def test_csv_loader_saves_file(self, sample_cleaned_data, tmp_path):
        """CSVLoader saves data to CSV file"""
        loader = CSVLoader(str(tmp_path), 'output.csv')
        result_path = loader.load(sample_cleaned_data)
        
        assert os.path.exists(result_path)
        loaded = pd.read_csv(result_path)
        assert len(loaded) == len(sample_cleaned_data)
    
    def test_latest_snapshot_loader_saves_latest(self, sample_multi_country_data, tmp_path):
        """LatestSnapshotLoader saves only latest records per location"""
        loader = LatestSnapshotLoader(str(tmp_path), 'latest.csv')
        result_path = loader.load(sample_multi_country_data)
        
        assert os.path.exists(result_path)
        loaded = pd.read_csv(result_path)
        # Should have unique country/province combinations
        assert len(loaded) <= len(sample_multi_country_data)
    
    def test_country_aggregate_loader_aggregates(self, sample_multi_country_data, tmp_path):
        """CountryAggregateLoader aggregates by country"""
        loader = CountryAggregateLoader(str(tmp_path), 'by_country.csv')
        result_path = loader.load(sample_multi_country_data)
        
        assert os.path.exists(result_path)
        loaded = pd.read_csv(result_path)
        # Should aggregate to fewer records
        unique_countries = sample_multi_country_data['Country/Region'].nunique()
        assert len(loaded) == unique_countries
    
    def test_loader_creates_directory(self, sample_cleaned_data, tmp_path):
        """Loaders create output directory if it doesn't exist"""
        new_dir = tmp_path / "new_output_dir"
        assert not new_dir.exists()
        
        loader = CSVLoader(str(new_dir), 'test.csv')
        loader.load(sample_cleaned_data)
        
        assert new_dir.exists()
    
    def test_loader_get_name(self, tmp_path):
        """Loaders return their class name via get_name()"""
        loader = CSVLoader(str(tmp_path))
        assert loader.get_name() == 'CSVLoader'
        
        snapshot_loader = LatestSnapshotLoader(str(tmp_path))
        assert snapshot_loader.get_name() == 'LatestSnapshotLoader'


class TestPipeline:
    """Tests for ETLPipeline orchestration"""
    
    def test_pipeline_runs_successfully(self, mock_pipeline):
        """Pipeline executes all stages and returns results"""
        results = mock_pipeline.run()
        
        assert results['success'] == True
        assert 'validation' in results
        assert 'transformations' in results
        assert 'outputs' in results
    
    def test_pipeline_applies_all_transformers(self, sample_raw_data, mock_extractor, mock_loader):
        """Pipeline applies all transformers in order"""
        from conftest import MockTransformer
        
        extractor = mock_extractor
        extractor._data = sample_raw_data
        
        t1 = MockTransformer("First")
        t2 = MockTransformer("Second")
        t3 = MockTransformer("Third")
        
        pipeline = ETLPipeline(extractor, [t1, t2, t3], [mock_loader])
        results = pipeline.run()
        
        assert t1.transform_count == 1
        assert t2.transform_count == 1
        assert t3.transform_count == 1
        assert results['transformations'] == ['First', 'Second', 'Third']
    
    def test_pipeline_add_transformer(self, sample_raw_data, mock_loader):
        """Pipeline supports adding transformers dynamically"""
        from conftest import MockExtractor, MockTransformer
        
        extractor = MockExtractor(sample_raw_data)
        t1 = MockTransformer("Initial")
        t2 = MockTransformer("Added")
        
        pipeline = ETLPipeline(extractor, [t1], [mock_loader])
        pipeline.add_transformer(t2)
        
        results = pipeline.run()
        
        assert 'Added' in results['transformations']
    
    def test_pipeline_add_loader(self, sample_raw_data):
        """Pipeline supports adding loaders dynamically"""
        from conftest import MockExtractor, MockLoader
        
        extractor = MockExtractor(sample_raw_data)
        loader1 = MockLoader()
        loader2 = MockLoader()
        
        pipeline = ETLPipeline(extractor, [DateTransformer()], [loader1])
        pipeline.add_loader(loader2)
        
        results = pipeline.run()
        
        assert loader1.load_count == 1
        assert loader2.load_count == 1
    
    def test_pipeline_dependency_injection(self, sample_raw_data, tmp_path):
        """Pipeline accepts different implementations via DI"""
        from conftest import MockExtractor
        
        # Use mock extractor with real transformers and loader
        extractor = MockExtractor(sample_raw_data)
        transformers = [DateTransformer(), MetricsTransformer()]
        loaders = [CSVLoader(str(tmp_path), 'test.csv')]
        
        pipeline = ETLPipeline(extractor, transformers, loaders)
        results = pipeline.run()
        
        assert results['success'] == True
        assert os.path.exists(tmp_path / 'test.csv')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
