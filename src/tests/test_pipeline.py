"""
ETL Pipeline Tests

Tests for ETLPipeline orchestration following SOLID principles:
- Dependency Injection: Pipeline accepts abstractions, not concrete implementations
- Open/Closed: New components can be added without modifying the pipeline
- Single Responsibility: Pipeline only orchestrates, doesn't implement ETL logic

Run with: pytest tests/test_pipeline.py -v
"""

import pytest
import pandas as pd
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Import test fixtures
from conftest import MockExtractor, MockLoader, MockTransformer


class TestETLPipeline:
    """Core tests for ETLPipeline class"""
    
    def test_pipeline_runs_all_transformers(self, sample_raw_data):
        """Pipeline executes all transformers in sequence"""
        extractor = MockExtractor(sample_raw_data)
        t1 = MockTransformer("First")
        t2 = MockTransformer("Second")
        t3 = MockTransformer("Third")
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [t1, t2, t3], [loader])
        results = pipeline.run()
        
        assert results['success'] == True
        assert t1.transform_count == 1
        assert t2.transform_count == 1
        assert t3.transform_count == 1
        assert results['transformations'] == ['First', 'Second', 'Third']
    
    def test_pipeline_dependency_injection(self, sample_raw_data, tmp_path):
        """Pipeline accepts different implementations via dependency injection"""
        # Use mock extractor with real transformers and real loader
        extractor = MockExtractor(sample_raw_data)
        transformers = [DateTransformer(), MetricsTransformer()]
        loaders = [CSVLoader(str(tmp_path), 'di_test.csv')]
        
        pipeline = ETLPipeline(extractor, transformers, loaders)
        results = pipeline.run()
        
        assert results['success'] == True
        assert os.path.exists(tmp_path / 'di_test.csv')
        
        # Verify the file has expected columns
        loaded = pd.read_csv(tmp_path / 'di_test.csv')
        assert 'Active' in loaded.columns
    
    def test_pipeline_with_custom_transformers(self, sample_raw_data):
        """Pipeline works with custom transformer implementations"""
        class CountingTransformer(BaseTransformer):
            def __init__(self):
                self.row_count = 0
            
            def transform(self, df: pd.DataFrame) -> pd.DataFrame:
                self.row_count = len(df)
                df = df.copy()
                df['row_count'] = self.row_count
                return df
        
        extractor = MockExtractor(sample_raw_data)
        custom_t = CountingTransformer()
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [custom_t], [loader])
        results = pipeline.run()
        
        assert results['success'] == True
        assert custom_t.row_count == len(sample_raw_data)
        assert 'row_count' in loader.loaded_data.columns
    
    def test_pipeline_add_transformer(self, sample_raw_data):
        """Pipeline supports adding transformers dynamically"""
        extractor = MockExtractor(sample_raw_data)
        initial_t = MockTransformer("Initial")
        added_t = MockTransformer("Added")
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [initial_t], [loader])
        pipeline.add_transformer(added_t)
        
        results = pipeline.run()
        
        assert 'Initial' in results['transformations']
        assert 'Added' in results['transformations']
    
    def test_pipeline_add_transformer_at_position(self, sample_raw_data):
        """Pipeline can add transformer at specific position"""
        extractor = MockExtractor(sample_raw_data)
        t1 = MockTransformer("First")
        t3 = MockTransformer("Third")
        t2 = MockTransformer("Second")  # Will be inserted between
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [t1, t3], [loader])
        pipeline.add_transformer(t2, position=1)  # Insert at index 1
        
        results = pipeline.run()
        
        assert results['transformations'] == ['First', 'Second', 'Third']
    
    def test_pipeline_add_loader(self, sample_raw_data):
        """Pipeline supports adding loaders dynamically"""
        extractor = MockExtractor(sample_raw_data)
        transformer = DateTransformer()
        loader1 = MockLoader()
        loader2 = MockLoader()
        
        pipeline = ETLPipeline(extractor, [transformer], [loader1])
        pipeline.add_loader(loader2)
        
        results = pipeline.run()
        
        assert loader1.load_count == 1
        assert loader2.load_count == 1
        # Both loaders should have loaded data
        assert loader1.loaded_data is not None
        assert loader2.loaded_data is not None


class TestPipelineValidation:
    """Tests for pipeline validation behavior"""
    
    def test_pipeline_returns_validation_results(self, sample_raw_data):
        """Pipeline includes validation results from extractor"""
        extractor = MockExtractor(sample_raw_data)
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [], [loader])
        results = pipeline.run()
        
        assert 'validation' in results
        assert 'total_records' in results['validation']
    
    def test_pipeline_returns_final_record_count(self, sample_raw_data):
        """Pipeline returns final record count after processing"""
        extractor = MockExtractor(sample_raw_data)
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [], [loader])
        results = pipeline.run()
        
        assert 'final_record_count' in results
        assert results['final_record_count'] == len(sample_raw_data)


class TestPipelineOutputs:
    """Tests for pipeline output handling"""
    
    def test_pipeline_tracks_all_outputs(self, sample_raw_data, tmp_path):
        """Pipeline tracks outputs from all loaders"""
        extractor = MockExtractor(sample_raw_data)
        transformers = [DateTransformer(), MetricsTransformer()]
        loader1 = CSVLoader(str(tmp_path), 'full.csv')
        loader2 = LatestSnapshotLoader(str(tmp_path), 'latest.csv')
        
        pipeline = ETLPipeline(extractor, transformers, [loader1, loader2])
        results = pipeline.run()
        
        assert 'CSVLoader' in results['outputs']
        assert 'LatestSnapshotLoader' in results['outputs']
    
    def test_pipeline_creates_multiple_output_files(self, sample_raw_data, tmp_path):
        """Pipeline creates files for all loaders"""
        extractor = MockExtractor(sample_raw_data)
        transformers = [DateTransformer(), MetricsTransformer()]
        loaders = [
            CSVLoader(str(tmp_path), 'output1.csv'),
            CSVLoader(str(tmp_path), 'output2.csv')
        ]
        
        pipeline = ETLPipeline(extractor, transformers, loaders)
        results = pipeline.run()
        
        assert os.path.exists(tmp_path / 'output1.csv')
        assert os.path.exists(tmp_path / 'output2.csv')


class TestPipelineWithRealTransformers:
    """Tests for pipeline with real transformer implementations"""
    
    def test_full_pipeline_with_all_transformers(self, sample_raw_data, tmp_path):
        """Pipeline runs successfully with all real transformers"""
        extractor = MockExtractor(sample_raw_data)
        transformers = [
            DateTransformer(),
            MissingValueTransformer(),
            AnomalyTransformer(),
            GeographyTransformer(),
            MetricsTransformer(),
            OutlierTransformer()
        ]
        loaders = [CSVLoader(str(tmp_path), 'full_pipeline.csv')]
        
        pipeline = ETLPipeline(extractor, transformers, loaders)
        results = pipeline.run()
        
        assert results['success'] == True
        assert len(results['transformations']) == 6
        
        # Load and verify output
        output = pd.read_csv(tmp_path / 'full_pipeline.csv')
        assert 'Active' in output.columns
        assert 'DeathRate' in output.columns
        assert 'IsOutlier' in output.columns
    
    def test_pipeline_with_all_loaders(self, sample_raw_data, tmp_path):
        """Pipeline runs with all loader types"""
        extractor = MockExtractor(sample_raw_data)
        transformers = [DateTransformer(), MetricsTransformer()]
        loaders = [
            CSVLoader(str(tmp_path), 'full.csv'),
            LatestSnapshotLoader(str(tmp_path), 'latest.csv'),
            CountryAggregateLoader(str(tmp_path), 'by_country.csv')
        ]
        
        pipeline = ETLPipeline(extractor, transformers, loaders)
        results = pipeline.run()
        
        assert results['success'] == True
        assert os.path.exists(tmp_path / 'full.csv')
        assert os.path.exists(tmp_path / 'latest.csv')
        assert os.path.exists(tmp_path / 'by_country.csv')


class TestPipelineErrorHandling:
    """Tests for pipeline error handling"""
    
    def test_pipeline_propagates_extractor_error(self):
        """Pipeline propagates errors from extractor"""
        extractor = CSVExtractor("nonexistent_file.csv")
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [], [loader])
        
        with pytest.raises(FileNotFoundError):
            pipeline.run()
    
    def test_pipeline_propagates_transformer_error(self, sample_raw_data):
        """Pipeline propagates errors from transformers"""
        class FailingTransformer(BaseTransformer):
            def transform(self, df):
                raise ValueError("Intentional test error")
        
        extractor = MockExtractor(sample_raw_data)
        failing_t = FailingTransformer()
        loader = MockLoader()
        
        pipeline = ETLPipeline(extractor, [failing_t], [loader])
        
        with pytest.raises(ValueError, match="Intentional test error"):
            pipeline.run()


class TestPipelineSOLIDPrinciples:
    """Tests verifying SOLID principle compliance"""
    
    def test_open_closed_principle(self, sample_raw_data):
        """New components can be added without modifying pipeline"""
        # Create a completely new transformer type
        class NewMetricTransformer(BaseTransformer):
            def transform(self, df):
                df = df.copy()
                df['NewMetric'] = 42
                return df
        
        extractor = MockExtractor(sample_raw_data)
        new_transformer = NewMetricTransformer()
        loader = MockLoader()
        
        # Pipeline works without modification
        pipeline = ETLPipeline(extractor, [new_transformer], [loader])
        results = pipeline.run()
        
        assert results['success'] == True
        assert 'NewMetric' in loader.loaded_data.columns
    
    def test_liskov_substitution_principle(self, sample_raw_data):
        """Any BaseTransformer subclass can be used interchangeably"""
        transformers = [
            DateTransformer(),
            MissingValueTransformer(),
            MetricsTransformer()
        ]
        
        # All are interchangeable in the pipeline
        extractor = MockExtractor(sample_raw_data)
        loader = MockLoader()
        
        # Can use any combination
        for t in transformers:
            pipeline = ETLPipeline(extractor, [t], [loader])
            results = pipeline.run()
            assert results['success'] == True
    
    def test_dependency_inversion_principle(self, sample_raw_data):
        """Pipeline depends on abstractions, not concretions"""
        # Pipeline accepts any BaseExtractor, BaseTransformer, BaseLoader
        # We can inject mocks or real implementations
        
        # With mocks
        pipeline_mock = ETLPipeline(
            MockExtractor(sample_raw_data),
            [MockTransformer("Mock")],
            [MockLoader()]
        )
        
        # With real implementations
        extractor = MockExtractor(sample_raw_data)  # Still mock for testing
        pipeline_real = ETLPipeline(
            extractor,
            [DateTransformer(), MetricsTransformer()],
            [MockLoader()]
        )
        
        # Both work the same way
        assert pipeline_mock.run()['success'] == True
        assert pipeline_real.run()['success'] == True


class TestPipelineIntegration:
    """Integration tests for the complete pipeline"""
    
    def test_end_to_end_pipeline(self, tmp_path):
        """Complete end-to-end pipeline test with temporary CSV"""
        # Create a temporary input CSV
        input_file = tmp_path / "input.csv"
        input_data = pd.DataFrame({
            'ObservationDate': ['01/22/2020', '01/23/2020', '01/24/2020'],
            'Country/Region': ['Mainland China', 'Mainland China', 'US'],
            'Province/State': ['Hubei', 'Hubei', None],
            'Confirmed': [100, 150, 50],
            'Deaths': [10, 15, 5],
            'Recovered': [50, 80, 20],
            'Last Update': ['01/22/2020', '01/23/2020', '01/24/2020']
        })
        input_data.to_csv(input_file, index=False)
        
        # Create full pipeline
        extractor = CSVExtractor(str(input_file))
        transformers = [
            DateTransformer(),
            MissingValueTransformer(),
            GeographyTransformer(),
            MetricsTransformer()
        ]
        loaders = [
            CSVLoader(str(tmp_path), 'cleaned.csv'),
            LatestSnapshotLoader(str(tmp_path), 'latest.csv')
        ]
        
        pipeline = ETLPipeline(extractor, transformers, loaders)
        results = pipeline.run()
        
        # Verify results
        assert results['success'] == True
        assert results['validation']['total_records'] == 3
        
        # Load and verify output
        cleaned = pd.read_csv(tmp_path / 'cleaned.csv')
        assert 'Active' in cleaned.columns
        assert 'DeathRate' in cleaned.columns
        assert 'China' in cleaned['Country/Region'].values  # Normalized from 'Mainland China'
        assert 'National' in cleaned['Province/State'].values  # Filled from None
        
        # Latest snapshot should have fewer records
        latest = pd.read_csv(tmp_path / 'latest.csv')
        assert len(latest) <= len(cleaned)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
