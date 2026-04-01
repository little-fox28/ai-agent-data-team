# Skill: Data Validation Testing

## Overview
Comprehensive testing patterns for validating data quality, statistical calculations, and ETL pipelines in data science projects.

## When to Use
- Setting up quality assurance for data pipelines
- Validating statistical calculations and aggregations
- Testing data transformations and cleaning operations
- Ensuring data integrity in visualization projects

## Prerequisites
- Python with pandas and numpy
- pytest framework
- Basic understanding of data validation concepts

## Implementation

### 1. Test Structure Setup

Create a well-organized test directory:
```
tests/
├── conftest.py              # Shared fixtures
├── pytest.ini               # Configuration
├── test_data_quality.py     # Data validation tests
├── test_statistics.py       # Statistical calculation tests
├── test_etl.py              # ETL pipeline tests
└── README.md                # Documentation
```

### 2. Pytest Configuration (pytest.ini)

```ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v
    --strict-markers
    --tb=short

testpaths = tests

markers =
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    slow: marks tests as slow
```

### 3. Shared Fixtures (conftest.py)

```python
import pytest
import pandas as pd

@pytest.fixture
def sample_raw_data():
    """Fixture providing sample raw data"""
    return pd.DataFrame({
        'Date': ['2020-01-22', '2020-01-23'],
        'Country': ['China', 'US'],
        'Confirmed': [100, 50],
        'Deaths': [10, 5],
        'Recovered': [30, 10]
    })

@pytest.fixture
def sample_with_issues():
    """Fixture with data quality issues"""
    return pd.DataFrame({
        'Date': ['2020-01-22', None, '2020-01-23'],
        'Country': ['China', 'US', 'UK'],
        'Confirmed': [100, -10, 200],  # Negative value
        'Deaths': [10, 5, 250],  # Deaths > Confirmed
        'Recovered': [30, 0, 50]
    })
```

### 4. Data Schema Validation Tests

```python
class TestDataSchema:
    """Tests for data schema and structure"""
    
    def test_required_columns_present(self, sample_raw_data):
        """Test all required columns exist"""
        required = ['Date', 'Country', 'Confirmed', 'Deaths', 'Recovered']
        for col in required:
            assert col in sample_raw_data.columns, f"Missing column: {col}"
    
    def test_column_data_types(self, sample_raw_data):
        """Test columns have expected data types"""
        assert pd.api.types.is_numeric_dtype(sample_raw_data['Confirmed'])
        assert pd.api.types.is_numeric_dtype(sample_raw_data['Deaths'])
    
    def test_value_ranges(self, sample_raw_data):
        """Test numeric values are non-negative"""
        assert (sample_raw_data['Confirmed'] >= 0).all()
        assert (sample_raw_data['Deaths'] >= 0).all()
```

### 5. Data Quality Tests

```python
class TestDataQuality:
    """Tests for data quality issues"""
    
    def test_missing_values_handling(self, sample_with_issues):
        """Test detection of missing values"""
        null_counts = sample_with_issues.isnull().sum()
        assert null_counts['Date'] > 0  # Should detect null date
    
    def test_duplicate_detection(self):
        """Test identification of duplicate records"""
        data = pd.DataFrame({
            'Date': ['2020-01-22', '2020-01-22'],
            'Country': ['China', 'China'],
            'Value': [100, 100]
        })
        duplicates = data.duplicated(subset=['Date', 'Country'])
        assert duplicates.sum() == 1
    
    def test_outlier_detection(self):
        """Test outlier identification using IQR"""
        values = pd.Series([10, 20, 15, 18, 10000000])
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        outliers = (values < (Q1 - 1.5 * IQR)) | (values > (Q3 + 1.5 * IQR))
        assert outliers.sum() > 0
    
    def test_logical_consistency(self, sample_raw_data):
        """Test logical relationships between columns"""
        # Deaths should not exceed Confirmed
        assert (sample_raw_data['Deaths'] <= sample_raw_data['Confirmed']).all()
```

### 6. Statistical Calculation Tests

```python
class TestStatisticalCalculations:
    """Tests for statistical accuracy"""
    
    def test_rate_calculation(self):
        """Test percentage/rate calculation"""
        data = pd.DataFrame({
            'Confirmed': [100, 200],
            'Deaths': [10, 30]
        })
        data['CFR'] = (data['Deaths'] / data['Confirmed'] * 100).round(2)
        
        assert data.iloc[0]['CFR'] == 10.0
        assert data.iloc[1]['CFR'] == 15.0
    
    def test_zero_division_handling(self):
        """Test division by zero is handled"""
        import numpy as np
        data = pd.DataFrame({'Confirmed': [0], 'Deaths': [0]})
        data['CFR'] = np.where(data['Confirmed'] > 0, 
                               data['Deaths'] / data['Confirmed'] * 100, 
                               0)
        assert data.iloc[0]['CFR'] == 0
    
    def test_aggregation(self):
        """Test aggregation functions"""
        data = pd.DataFrame({
            'Country': ['China', 'China', 'US'],
            'Province': ['Hubei', 'Beijing', 'NY'],
            'Confirmed': [100, 50, 75]
        })
        country_total = data.groupby('Country')['Confirmed'].sum()
        assert country_total['China'] == 150
        assert country_total['US'] == 75
```

### 7. Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
pytest tests/test_data_quality.py -v

# Run with coverage
pytest tests/ --cov=etl --cov-report=html

# Run by marker
pytest -m unit

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

## Key Patterns

### 1. Arrange-Act-Assert Pattern
```python
def test_something(self):
    # Arrange: Set up test data
    data = create_test_data()
    
    # Act: Perform operation
    result = process_data(data)
    
    # Assert: Verify result
    assert result == expected_value
```

### 2. Descriptive Assertion Messages
```python
# Good: Clear error message
assert result['CFR'] == 10.0, f"Expected CFR 10.0, got {result['CFR']}"

# Bad: No context
assert result['CFR'] == 10.0
```

### 3. Edge Case Testing
```python
def test_edge_cases(self):
    """Test with zero values"""
    data = pd.DataFrame({'Confirmed': [0], 'Deaths': [0]})
    result = calculate_rate(data)
    assert result >= 0  # Should handle gracefully
```

### 4. Parametrized Tests
```python
@pytest.mark.parametrize("confirmed,deaths,expected_cfr", [
    (100, 10, 10.0),
    (200, 30, 15.0),
    (0, 0, 0.0)
])
def test_cfr_calculation(confirmed, deaths, expected_cfr):
    result = (deaths / confirmed * 100) if confirmed > 0 else 0
    assert result == expected_cfr
```

## Common Validation Checks

1. **Schema Validation:** Required columns, data types, value ranges
2. **Missing Values:** Null detection and handling
3. **Duplicates:** Duplicate record identification
4. **Outliers:** IQR method or z-score detection
5. **Logical Consistency:** Relationship validation (Deaths ≤ Confirmed)
6. **Date Validation:** Format, range, chronological order
7. **Geographic Data:** Country/region completeness
8. **Statistical Accuracy:** Rate calculations, aggregations

## Best Practices

1. **Test Independence:** Each test should run independently
2. **Deterministic:** Same input → same output
3. **Clear Names:** Descriptive test and function names
4. **Documentation:** Docstrings explaining what is tested
5. **Fixtures:** Reusable test data in conftest.py
6. **Markers:** Organize tests by category (unit, integration, slow)
7. **Coverage:** Aim for high code coverage but focus on critical paths
8. **Edge Cases:** Test boundary conditions and unusual inputs

## Troubleshooting

### Import Errors
Add parent directory to path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Fixture Not Found
Ensure conftest.py is in the tests/ directory.

### Tests Pass But Code Fails
- Verify test data matches production data structure
- Check for environment-specific issues
- Review edge cases not covered by tests

## Examples

See the complete implementation in the COVID-19 project:
- `tests/test_data_quality.py` - 14 data validation tests
- `tests/test_statistics.py` - 16 statistical calculation tests
- `tests/test_etl.py` - 6 ETL pipeline tests
- `tests/conftest.py` - Shared fixtures
- `tests/README.md` - Comprehensive documentation

## References

- pytest documentation: https://docs.pytest.org/
- pandas testing: https://pandas.pydata.org/docs/reference/api/pandas.testing.html
- Data validation best practices: https://en.wikipedia.org/wiki/Data_validation

## Version History

- **v1.0.0** (2026-04-01): Initial skill documentation based on COVID-19 project test suite
