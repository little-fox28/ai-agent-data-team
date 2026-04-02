"""
COVID-19 Data ETL Pipeline (OOP with SOLID Principles)

This script runs the full Extract, Transform, Load pipeline for COVID-19 data
using an object-oriented design following SOLID principles.

SOLID Compliance:
- Single Responsibility: Each transformer handles ONE transformation
- Open/Closed: New transformers extend base class, don't modify pipeline
- Liskov Substitution: All transformers are interchangeable
- Interface Segregation: Small focused interfaces (extract, transform, load)
- Dependency Inversion: Pipeline depends on abstractions, not concretions

Usage:
    python src/etl/run_pipeline.py
"""

import logging
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import OOP components
from etl.pipeline import ETLPipeline
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

# Ensure log directory exists
log_dir = Path('src/outputs/reports')
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'etl_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def create_pipeline(raw_data_path: str, output_dir: str) -> ETLPipeline:
    """
    Factory function to create and configure the ETL pipeline.
    
    Demonstrates Dependency Injection: concrete implementations are created here
    and injected into the pipeline, which only knows about abstractions.
    
    Args:
        raw_data_path: Path to raw COVID-19 CSV file
        output_dir: Directory for output files
    
    Returns:
        ETLPipeline: Configured pipeline ready to run
    """
    # EXTRACTOR: CSV file extractor
    extractor = CSVExtractor(filepath=raw_data_path)
    
    # TRANSFORMERS: Chain of responsibility - each handles one concern
    transformers = [
        DateTransformer(),                  # S: Only handles date conversion
        MissingValueTransformer(),          # S: Only handles missing values
        AnomalyTransformer(),               # S: Only handles anomalies
        GeographyTransformer(),             # S: Only handles geography
        MetricsTransformer(),               # S: Only handles metric derivation
        OutlierTransformer(),               # S: Only handles outlier detection
    ]
    
    # LOADERS: Multiple output formats
    loaders = [
        CSVLoader(output_dir, 'covid_cleaned.csv'),           # Full dataset
        LatestSnapshotLoader(output_dir, 'covid_latest.csv'), # Latest per location
        CountryAggregateLoader(output_dir, 'covid_by_country.csv'),  # Country level
    ]
    
    # Create pipeline with dependency injection
    return ETLPipeline(
        extractor=extractor,
        transformers=transformers,
        loaders=loaders
    )


def run_pipeline(raw_data_path: str = 'src/data/raw/covid_19_data.csv') -> dict:
    """
    Run the complete ETL pipeline.
    
    Args:
        raw_data_path: Path to raw COVID-19 CSV file
    
    Returns:
        dict: Pipeline results including validation and output paths
    """
    logger.info("\n" + "=" * 60)
    logger.info("COVID-19 ETL Pipeline (OOP/SOLID)")
    logger.info("=" * 60)
    
    # Configuration
    output_dir = 'src/data/processed'
    
    try:
        # Create pipeline using factory function
        pipeline = create_pipeline(raw_data_path, output_dir)
        
        # Run the pipeline
        results = pipeline.run()
        
        # Log summary
        logger.info("\n" + "-" * 40)
        logger.info("PIPELINE SUMMARY")
        logger.info("-" * 40)
        logger.info(f"Records processed: {results.get('final_record_count', 'N/A'):,}")
        logger.info(f"Transformations applied: {len(results.get('transformations', []))}")
        logger.info(f"Output files created: {len(results.get('outputs', {}))}")
        
        logger.info("\nGenerated files:")
        for loader_name, filepath in results.get('outputs', {}).items():
            logger.info(f"  [{loader_name}] {filepath}")
        
        return results
        
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        results = run_pipeline()
        if results.get('success'):
            logger.info("\n[SUCCESS] Pipeline completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n[ERROR] Pipeline completed with errors")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n[ERROR] Pipeline execution failed: {e}")
        sys.exit(1)
