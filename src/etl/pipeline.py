"""
ETL Pipeline Orchestrator

Implements Dependency Inversion: depends on abstractions (BaseExtractor, BaseTransformer, BaseLoader)
not on concrete implementations. This allows easy swapping of components.

Design Pattern: Strategy + Chain of Responsibility
- Extractor strategy: different sources (CSV, API, Database)
- Transformer chain: each transformer processes data in sequence
- Loader strategy: different destinations (CSV, Database, API)
"""

import logging
from typing import List, Dict, Any

from .base.extractor import BaseExtractor
from .base.transformer import BaseTransformer
from .base.loader import BaseLoader

logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    ETL Pipeline orchestrator following SOLID principles.
    
    Dependency Inversion:
        - Accepts abstractions (BaseExtractor, BaseTransformer, BaseLoader)
        - Concrete implementations are injected at runtime
    
    Open/Closed:
        - New extractors/transformers/loaders can be added without modifying this class
        - Pipeline logic is closed for modification
    
    Single Responsibility:
        - Only orchestrates the ETL flow
        - Does not implement any extraction, transformation, or loading logic
    """
    
    def __init__(
        self,
        extractor: BaseExtractor,
        transformers: List[BaseTransformer],
        loaders: List[BaseLoader]
    ):
        """
        Initialize ETL Pipeline with components.
        
        Args:
            extractor: Data extractor instance
            transformers: List of transformers to apply in order
            loaders: List of loaders to save data
        """
        self._extractor = extractor
        self._transformers = transformers
        self._loaders = loaders
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the complete ETL pipeline.
        
        Returns:
            dict: Results including validation info and output paths
        """
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)
        
        results = {
            'validation': {},
            'transformations': [],
            'outputs': {},
            'success': False
        }
        
        try:
            # EXTRACT
            logger.info("\n[EXTRACT] Loading data...")
            df = self._extractor.extract()
            results['validation'] = self._extractor.validate(df)
            logger.info(f"Extracted {len(df):,} records")
            
            # TRANSFORM (Chain of Responsibility)
            logger.info("\n[TRANSFORM] Applying transformations...")
            for transformer in self._transformers:
                logger.info(f"  Running: {transformer.get_name()}")
                df = transformer.transform(df)
                results['transformations'].append(transformer.get_name())
            logger.info(f"Applied {len(self._transformers)} transformations")
            
            # LOAD
            logger.info("\n[LOAD] Saving data...")
            for loader in self._loaders:
                output_path = loader.load(df)
                results['outputs'][loader.get_name()] = output_path
            logger.info(f"Saved to {len(self._loaders)} destinations")
            
            results['success'] = True
            results['final_record_count'] = len(df)
            
            logger.info("\n" + "=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            results['error'] = str(e)
            raise
        
        return results
    
    def add_transformer(self, transformer: BaseTransformer, position: int = None) -> None:
        """
        Add a transformer to the pipeline.
        
        Args:
            transformer: Transformer to add
            position: Optional position in the chain (default: append to end)
        """
        if position is not None:
            self._transformers.insert(position, transformer)
        else:
            self._transformers.append(transformer)
        logger.info(f"Added transformer: {transformer.get_name()}")
    
    def add_loader(self, loader: BaseLoader) -> None:
        """
        Add a loader to the pipeline.
        
        Args:
            loader: Loader to add
        """
        self._loaders.append(loader)
        logger.info(f"Added loader: {loader.get_name()}")
