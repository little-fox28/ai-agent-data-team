# Test Suite Documentation

## Overview

This test suite provides comprehensive quality assurance for the COVID-19 data visualization project. It validates data integrity, ETL pipeline correctness, and statistical calculations.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration
├── test_data_quality.py     # Data validation tests
├── test_etl.py              # ETL pipeline tests
├── test_statistics.py       # Statistical calculation tests
└── README.md                # This file
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_data_quality.py -v
pytest tests/test_etl.py -v
pytest tests/test_statistics.py -v
```

### Run Tests by Category
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=etl --cov-report=html
```

### Run Specific Test Class or Function
```bash
pytest tests/test_data_quality.py::TestDataSchema::test_required_columns_present -v
pytest tests/test_statistics.py::TestRateCalculations -v
```

## Test Categories

### 1. Data Quality Tests (`test_data_quality.py`)

Validates data integrity and quality standards:

- **TestDataSchema**: Verifies required columns, data types, and value ranges
  - `test_required_columns_present`: Ensures all required columns exist
  - `test_column_data_types`: Validates data types after processing
  - `test_value_ranges`: Checks for valid numeric ranges (non-negative)

- **TestDataQuality**: Checks for common data quality issues
  - `test_missing_values_handling`: Tests null value handling
  - `test_duplicate_detection`: Identifies duplicate records
  - `test_outlier_detection`: Detects extreme outliers using IQR method
  - `test_logical_consistency`: Validates relationships (Deaths ≤ Confirmed, etc.)

- **TestDateHandling**: Validates date formats and consistency
  - `test_date_format_parsing`: Tests various date format parsing
  - `test_date_range_validity`: Ensures dates fall within expected range
  - `test_chronological_order`: Verifies data can be sorted by date

- **TestGeographicData**: Checks geographic data completeness
  - `test_country_names_not_empty`: Ensures country names are populated
  - `test_province_state_consistency`: Validates Province/State field handling
  - `test_unique_location_combinations`: Checks for duplicate locations

- **TestSchemaValidation**: Tests the validate_schema function
  - `test_schema_validation_output`: Verifies validation metrics

### 2. ETL Pipeline Tests (`test_etl.py`)

Validates the Extract, Transform, Load pipeline:

- **TestExtract**: Tests data extraction functions
  - `test_load_covid_data`: Validates raw data loading
  - `test_validate_schema`: Tests schema validation function

- **TestTransform**: Tests data transformation functions
  - `test_clean_data`: Validates data cleaning (duplicates, nulls, types)
  - `test_normalize_countries`: Tests country name normalization
  - `test_derive_metrics`: Validates derived column calculations

- **TestLoad**: Tests data output functions
  - `test_directory_creation`: Ensures output directories are created

### 3. Statistical Calculation Tests (`test_statistics.py`)

Validates statistical accuracy and calculations:

- **TestRateCalculations**: Tests rate calculations
  - `test_case_fatality_rate_calculation`: Validates CFR = (Deaths/Confirmed) × 100
  - `test_recovery_rate_calculation`: Validates Recovery Rate = (Recovered/Confirmed) × 100
  - `test_zero_division_handling`: Tests division by zero handling

- **TestDailyCaseCalculations**: Tests daily incremental calculations
  - `test_daily_confirmed_calculation`: Validates daily new cases
  - `test_daily_deaths_calculation`: Validates daily new deaths
  - `test_negative_daily_values_handling`: Tests handling of data corrections

- **TestActiveCasesCalculation**: Tests active cases calculation
  - `test_active_cases_formula`: Validates Active = Confirmed - Deaths - Recovered
  - `test_active_cases_non_negative`: Ensures active cases are never negative

- **TestAggregationFunctions**: Tests aggregation operations
  - `test_sum_aggregation`: Validates summation across provinces
  - `test_mean_calculation`: Tests mean calculation
  - `test_median_calculation`: Tests median calculation

- **TestTimeSeriesAggregations**: Tests time-based aggregations
  - `test_daily_aggregation`: Validates aggregation by date
  - `test_cumulative_calculation`: Tests cumulative sum
  - `test_moving_average`: Validates rolling average

- **TestStatisticalAccuracy**: Validates against known results
  - `test_known_sample_statistics`: Tests with verified sample data
  - `test_edge_case_all_zeros`: Tests calculations with zero values

## Test Fixtures

Shared test fixtures are defined in `conftest.py`:

- `sample_raw_data`: Raw COVID-19 data with typical structure
- `sample_cleaned_data`: Cleaned data with datetime and no nulls
- `sample_multi_country_data`: Multi-country/province data for aggregation
- `sample_time_series_data`: Time series for trend analysis
- `sample_data_with_issues`: Data with common quality issues
- `sample_edge_cases`: Edge case data for robustness testing

## Test Coverage

Current test coverage includes:

- ✅ Data schema validation
- ✅ Data type checking
- ✅ Missing value handling
- ✅ Duplicate detection
- ✅ Outlier identification
- ✅ Logical consistency checks
- ✅ Date format validation
- ✅ Geographic data completeness
- ✅ ETL pipeline operations
- ✅ Rate calculations (CFR, Recovery Rate)
- ✅ Daily case calculations
- ✅ Active cases calculation
- ✅ Aggregation functions
- ✅ Time series operations
- ✅ Edge case handling

## Adding New Tests

### 1. Choose the Appropriate Test File

- Data validation → `test_data_quality.py`
- ETL operations → `test_etl.py`
- Statistical calculations → `test_statistics.py`

### 2. Follow Naming Conventions

```python
class TestFeatureName:
    """Description of what this test class covers"""
    
    def test_specific_behavior(self):
        """Description of what this test validates"""
        # Arrange
        sample_data = ...
        
        # Act
        result = function_under_test(sample_data)
        
        # Assert
        assert result == expected_value, "Error message"
```

### 3. Use Fixtures for Common Data

```python
def test_with_fixture(sample_raw_data):
    """Test using a shared fixture"""
    result = process_data(sample_raw_data)
    assert len(result) > 0
```

### 4. Add Descriptive Assertions

```python
# Good: Clear error message
assert result['CFR'] == 10.0, f"Expected CFR 10.0, got {result['CFR']}"

# Bad: No context
assert result['CFR'] == 10.0
```

## Test Execution Tips

### Verbose Output
```bash
pytest -v  # Verbose
pytest -vv # Extra verbose
```

### Stop on First Failure
```bash
pytest -x
```

### Run Last Failed Tests
```bash
pytest --lf
```

### Show Local Variables on Failure
```bash
pytest -l
```

### Generate HTML Report
```bash
pytest --html=report.html --self-contained-html
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Recommended workflow:

1. Run unit tests on every commit
2. Run integration tests on pull requests
3. Generate coverage reports
4. Fail build if coverage drops below threshold

## Quality Standards

All tests should:

- ✅ Be independent (no dependencies between tests)
- ✅ Be deterministic (same input → same output)
- ✅ Have clear, descriptive names
- ✅ Include docstrings explaining what they test
- ✅ Use fixtures for common setup
- ✅ Include meaningful assertions with error messages
- ✅ Cover both success and failure cases
- ✅ Test edge cases and boundary conditions

## Known Limitations

1. Some tests assume raw data exists at `data/raw/covid_19_data.csv`
2. Integration tests may be slow with full dataset (~18MB)
3. Statistical tests use simplified methods (not production-grade)

## Troubleshooting

### Import Errors
Ensure parent directory is in Python path:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Fixture Not Found
Check that `conftest.py` is in the `tests/` directory.

### Tests Pass But Code Fails
- Verify test data matches production data structure
- Check for environment-specific issues
- Review edge cases not covered by tests

## Contact

For questions or issues with the test suite, contact the Testing Team.

## Version History

- **v1.0.0** (2026-04-01): Initial test suite with comprehensive coverage
