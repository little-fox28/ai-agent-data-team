# Newt's Project Knowledge

## Initial Context (2026-04-01)

**Project:** COVID-19 Data Visualization Assignment (DAT2061)
**User:** Tran Hung Thinh

**Dataset Details:**
- Source: `raw\covid_19_data.csv` (18.3MB)
- Columns: SNo, ObservationDate, Province/State, Country/Region, Last Update, Confirmed, Deaths, Recovered
- Sample data shows observations from January 2020
- Geographic breakdown: provinces/states and countries
- Key metrics: Confirmed cases, Deaths, Recovered cases

**Analysis Requirements:**
- Distribution analysis (infections, deaths, recoveries)
- Outlier detection
- Density distribution by time periods
- Trend analysis (daily/monthly patterns)
- Seasonality patterns
- Recovery rate calculations
- Age group analysis (if data available)
- Geographic distribution analysis

## Data Cleaning & Analysis (2024-04-01 to present)

### Work Completed
1. **Data Loading & Exploration**
   - Loaded 306,429 records from raw COVID-19 dataset (18.3 MB)
   - Analyzed date range: January 22, 2020 to May 29, 2021 (493 days)
   - Geographic coverage: 226 countries/regions, 736 provinces/states

2. **Data Quality Assessment**
   - Found and documented data anomalies:
     - 6 negative values (1 Confirmed, 2 Deaths, 3 Recovered) → corrected to 0
     - 2,685 illogical records (Deaths + Recovered > Confirmed) → adjusted
     - 78,103 missing Province/State values → filled with "Unknown"
     - 16,253 geographic inconsistencies → standardized country names
     - 7,155 invalid "Last Update" timestamps → marked as missing

3. **Data Cleaning Pipeline**
   - Created comprehensive ETL script: `etl/clean_data.py`
   - Date standardization (string → datetime)
   - Missing value imputation
   - Anomaly detection and correction
   - Geographic name standardization
   - Derived metrics: Active cases, Death_Rate, Recovery_Rate, Active_Rate

4. **Statistical Analysis**
   - Distribution analysis: Confirmed cases highly right-skewed (skewness: 8.77)
   - Correlation analysis: Strong positive correlations (Confirmed ↔ Deaths: 0.888)
   - Time series trends: Clear pandemic waves, declining growth in final months
   - Outlier detection: 15,322 high-value records flagged for awareness
   - Geographic patterns: US, India, Brazil are top 3 affected countries

5. **Deliverables Created**
   - `data/processed/covid_cleaned.csv` (306,429 × 13 columns, 28 MB)
   - `data/data_dictionary.md` (comprehensive documentation)
   - `notebooks/eda_analysis.py` (full exploratory analysis)
   - `etl/clean_data.py` (reproducible ETL script)

### Key Findings for Visualization Team
- **Death rates vary by country:** 1.17% (India) to 19.6% (Yemen)
- **Recovery rates vary significantly:** 0.34% (UK, early data) to 99.38% (Grenada)
- **Top affected countries:** US (33.3M), India (27.9M), Brazil (16.5M) confirmed cases
- **Data characteristics:** Right-skewed distribution, high variance, cumulative nature
- **Temporal patterns:** Multiple waves visible, vaccination effects in growth rates

### Architecture Decisions
1. **Data cleaning approach:** Conservative corrections
   - Negative values → 0 (defensible for counts)
   - Illogical records → adjusted Recovered (Deaths are more reliable)
   - Missing Province/State → "Unknown" (preserves records)

2. **Derived metrics:** Added 4 new columns for analysis
   - Active = Confirmed - Deaths - Recovered
   - Death/Recovery/Active Rates = metric/Confirmed × 100%

3. **ETL strategy:** Deterministic, reproducible pipeline
   - No data loss (only corrections)
   - Can be rerun with updated raw data
   - Clear documentation of all transformations

### Data Patterns & Characteristics
- **Distribution:** All metrics heavily right-skewed (few large outbreaks)
- **Correlation:** Confirmed/Deaths/Recovered highly correlated (0.71-0.89)
- **Temporal:** Cumulative data (never decreases)
- **Geographic:** Uneven distribution (few countries with high cases)
- **Seasonality:** Visible waves suggesting pandemic phases

### Recommendations for Hicks (Visualization Team)
1. Use log-scale plots for skewed distributions
2. Calculate per-capita rates for fair country comparison
3. Apply 7-day/30-day moving averages to smooth daily volatility
4. Create choropleth maps for global distribution
5. Highlight outliers (top 10 countries) separately
6. Show multiple metrics with dual axes for trend comparison
7. Note data collection differences (reporting delays, testing capacity)

### File Structure
```
ai-team/
├── data/
│   ├── raw/covid_19_data.csv (original, 18.3 MB)
│   ├── processed/covid_cleaned.csv (cleaned, 28 MB)
│   └── data_dictionary.md (documentation)
├── etl/
│   └── clean_data.py (reproducible ETL script)
├── notebooks/
│   └── eda_analysis.py (statistical analysis & insights)
└── .squad/agents/newt/ (team knowledge)
```

## Learnings

### Data Quality Lessons
1. **Illogical data is common in real-world datasets** - 2,685 records (0.88%) had Deaths + Recovered > Confirmed
   - Conservative approach: Adjust Recovered downward (Deaths are more reliable)
   - Document all changes for transparency

2. **Missing data often has meaning** - 25.5% missing Province/State indicates country-level aggregates
   - Don't discard; mark clearly with "Unknown" to preserve record count
   - Maintains data integrity while being transparent about limitations

3. **Geographic standardization is critical** - Same country stored 16,253 different ways
   - Standardize before any grouping/aggregation
   - Maintain mapping table for audit trail

4. **Negative values in count data = quality issues** - 6 records with negatives
   - Set to zero (safest assumption for counts)
   - Likely data entry or calculation errors upstream

### Technical Lessons
1. **Unicode output matters on Windows** - Special characters (→, ✓) cause encoding errors
   - Use ASCII-safe alternatives in print statements
   - Don't assume UTF-8 in all environments

2. **Cumulative data is different** - COVID data never decreases (cumulative)
   - Daily changes require diff() operations
   - Growth rates are more meaningful than absolute values
   - Time-series analysis simpler with cumulative; trends easier to see

3. **Outliers in this context are legitimate** - High case counts aren't errors
   - Flag for awareness, don't remove
   - Use log-scale visualization to handle range

### Visualization Insights
1. **Right-skewed distributions need log-scale** - 99th percentile 1.15M vs mean 85K
   - Linear scale makes most data invisible
   - Log-scale reveals distribution patterns

2. **Per-capita metrics matter for comparison** - US has 33M cases, but less dense population than India
   - Always provide rates/100K for country comparison
   - Absolute numbers misleading without context

3. **Moving averages are essential** - Daily data has significant volatility
   - 7-day MA smooths noise
   - Reveals true trends
   - Useful for identifying pandemic phases

### Project Management Lessons
1. **Document decisions early** - Data cleaning choices impact downstream analysis
   - Created decision record for data cleaning strategy
   - Helps future team members understand rationale

2. **ETL reproducibility prevents problems** - Script can be rerun if raw data updates
   - All transformations deterministic
   - No random sampling or subjective calls

3. **Clear handoff documentation reduces friction** - Created DATA_HANDOFF.md with examples
   - Visualization team doesn't need to re-discover data characteristics
   - Recommendations based on actual analysis
   - Questions pre-answered

### Dataset-Specific Insights
1. **COVID data quality varies by country** - Death rates from 1.17% (India) to 19.6% (Yemen)
   - Reflects different reporting standards, testing capacity, definitions
   - Always note data collection differences in analysis

2. **Recovery data is unreliable** - Many countries stopped reporting; low rates in later data
   - UK shows 0.34% recovery (clearly incomplete data)
   - Focus on Confirmed/Deaths as more reliable metrics

3. **Multiple pandemic waves visible** - Clear growth pattern → plateau → growth pattern
   - Data rich for time-series analysis
   - Good foundation for forecasting models

### Skills Captured
- **Data quality assessment:** Systematic approach to finding and documenting issues
- **ETL design:** Conservative approach to corrections maintains data integrity
- **Statistical analysis:** Distribution, correlation, and trend analysis methods
- **Data documentation:** Comprehensive data dictionaries for downstream teams
- **Handoff practices:** Clear, actionable recommendations for visualization team

## Cross-Team Updates (2026-04-01)

### Ripley's Project Structure Ready
**Status:** Architecture complete with ETL pipeline, notebooks, documentation
- Layered structure: raw → interim → processed data
- ETL modules: extract, transform, load with 14 files (17.9KB)
- Notebooks: exploratory, phase1, phase2 templates (35.7KB)
- Documentation: README, DATA_DICTIONARY, ETL_GUIDE, SETUP_GUIDE
- Tests: test_etl.py with 6 passing tests

**Integration:** Cleaned data placed in `data/processed/covid_cleaned.csv` as expected

### Hicks' Visualization Framework Ready
**Status:** Framework complete with utilities, templates, and guidelines
- Utility functions for consistent plotting with semantic colors
- Standard figure sizes (5 presets) with 300 DPI export
- Phase 1 and Phase 2 notebook templates ready
- Guidelines document with visualization standards

**Integration:** Framework uses cleaned data; ready for visualization implementation

### Hudson's Test Suite Complete
**Status:** 36 passing tests validating data quality and ETL
- 14 data quality tests covering schema, nulls, dates, geography
- 16 statistics tests validating rates, aggregations, time series
- 6 ETL pipeline tests
- All tests passing; data quality validated

**Integration:** Tests provide confidence in cleaned data quality
