# COVID-19 Data Dictionary & Cleaning Documentation

## Dataset Overview
- **Source File:** data/raw/covid_19_data.csv (18.3 MB)
- **Processed File:** data/processed/covid_cleaned.csv (28.0 MB)
- **Records:** 306,429 observations
- **Date Range:** January 22, 2020 to May 29, 2021
- **Geographic Coverage:** 226 countries/regions, 736 provinces/states
- **Observation Period:** 493 days

---

## Column Definitions

### Original Columns
| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| SNo | int | Serial number | Record identifier (not used in analysis) |
| ObservationDate | datetime | Date of observation | Converted from string to datetime |
| Province/State | string | State/province name | 74.5% populated; 78,103 missing filled with 'Unknown' |
| Country/Region | string | Country name | Standardized (e.g., "Mainland China" → "China") |
| Last Update | datetime | Last update timestamp | 7,155 invalid dates (coerced to NaT) |
| Confirmed | int | Cumulative confirmed cases | Count of identified COVID-19 cases |
| Deaths | int | Cumulative deaths | Count of deaths attributed to COVID-19 |
| Recovered | int | Cumulative recovered cases | Count of cases marked as recovered |

### Derived Columns (Added During Cleaning)
| Column | Type | Calculation | Purpose |
|--------|------|-----------|---------|
| Active | int | Confirmed - Deaths - Recovered | Currently active cases |
| Death_Rate | float | (Deaths / Confirmed) × 100 | Percentage of deaths among confirmed |
| Recovery_Rate | float | (Recovered / Confirmed) × 100 | Percentage of recoveries among confirmed |
| Active_Rate | float | (Active / Confirmed) × 100 | Percentage of active cases |
| Is_Outlier | bool | Confirmed > 95th percentile | Flag for high-value records |

---

## Data Cleaning Steps

### 1. Date Standardization
- Converted `ObservationDate` from string format (MM/DD/YYYY) to Python datetime objects
- Converted `Last Update` timestamp to datetime (7,155 invalid dates set to NaT)
- Enables proper time-series analysis and sorting

### 2. Missing Value Handling
- **Province/State:** 78,103 missing values (25.5% of records)
  - Filled with "Unknown" (indicates country-level aggregates without state/province detail)
  - Preserves all records while clearly marking incomplete geographic detail
- No other missing values in key metrics

### 3. Anomaly Detection & Correction

#### Negative Values
- Found: 1 negative Confirmed case, 2 negative Deaths, 3 negative Recovered cases
- **Action:** Set all negative values to 0 (most conservative approach for count data)
- **Rationale:** Negative cases impossible; zero is most defensible assumption

#### Illogical Records (Deaths + Recovered > Confirmed)
- Found: 2,685 records violating basic logic
- **Action:** Reduced Recovered count to: Confirmed - Deaths
- **Rationale:** Deaths are typically more reliable; adjusted Recovered downward to maintain consistency
- **Impact:** Ensures all metrics remain logically valid

### 4. Geographic Standardization
- Standardized 16,253 country names to consistent formats:
  - "Mainland China" → "China"
  - "Korea" → "South Korea"
  - "Hong Kong SAR" → "Hong Kong"
  - Ensures consistent geographic grouping and analysis

### 5. Derived Metrics Calculation
- **Active Cases:** = Confirmed - Deaths - Recovered
  - Clipped to 0 (cannot be negative)
  - Represents currently infected cases
- **Death Rate (%):** = Deaths / Confirmed × 100
  - Handled division by zero (set to 0 when Confirmed = 0)
  - Indicates case fatality rate
- **Recovery Rate (%):** = Recovered / Confirmed × 100
  - Similar division-by-zero handling
  - Indicates proportion of confirmed cases that recovered
- **Active Rate (%):** = Active / Confirmed × 100
  - Proportion of cases still active

### 6. Outlier Detection
- Used Interquartile Range (IQR) method: 1.5 × IQR above Q3
- **Confirmed cases:** 43,977 outliers (high-case-count regions)
- **Deaths:** 42,102 outliers (high-mortality records)
- **Recovered:** 46,366 outliers (high-recovery records)
- **Flag:** Is_Outlier = True for records with Confirmed > 95th percentile (15,322 records)
- **Use:** Outliers are legitimate (major outbreaks) but flagged for analysis awareness

---

## Data Quality Summary

### Issues Found & Fixed
✓ **6 negative values** → Corrected to 0
✓ **2,685 illogical records** → Adjusted Recovered values
✓ **78,103 missing provinces** → Filled with "Unknown"
✓ **16,253 geographic inconsistencies** → Standardized country names
✓ **7,155 invalid timestamps** → Marked as missing

### Data Validation
- ✓ No negative values after cleaning
- ✓ Deaths + Recovered ≤ Confirmed (all records)
- ✓ All dates within valid range
- ✓ Geographic entities properly standardized
- ✓ Derived rates bounded [0, 100]

---

## Key Statistics (After Cleaning)

### Confirmed Cases
- **Total:** 26.3 billion (aggregate across all records)
- **Mean per record:** 85,672
- **Median per record:** 10,375
- **Range:** 0 to 5,863,138

### Deaths
- **Total:** 624 million
- **Mean per record:** 2,036
- **Median per record:** 192
- **Range:** 0 to 112,385

### Recovered Cases
- **Total:** 14.3 billion
- **Mean per record:** 46,754
- **Median per record:** 1,678
- **Range:** 0 to 5,339,838

### Active Cases
- **Total:** 11.3 billion
- **Mean per record:** 36,886
- **Median per record:** 1,593
- **Range:** 0 to 5,431,304

---

## Top 10 Most Affected Countries (by May 29, 2021)

| Country | Confirmed | Deaths | Recovered | Death Rate |
|---------|-----------|--------|-----------|-----------|
| US | 6,376,499 | 191,012 | 2,387,479 | 3.0% |
| India | 4,465,863 | 75,062 | 3,471,783 | 1.7% |
| Brazil | 4,197,889 | 128,539 | 3,611,632 | 3.1% |
| Russia | 1,037,526 | 18,080 | 854,069 | 1.7% |
| Peru | 696,190 | 30,123 | 536,959 | 4.3% |
| Colombia | 686,851 | 22,053 | 552,885 | 3.2% |
| Mexico | 647,321 | 69,049 | 538,514 | 10.7% |
| South Africa | 642,431 | 15,168 | 569,935 | 2.4% |
| Spain | 543,379 | 29,628 | 150,376 | 5.5% |
| Argentina | 512,293 | 10,658 | 382,490 | 2.1% |

---

## Data Characteristics for Visualization

### Temporal Characteristics
- **Granularity:** Daily observations (multiple records per day for different regions)
- **Time Series:** Progressive accumulation (cumulative counts, never decrease)
- **Period:** 16+ months of pandemic data (initial spread through peak phases)
- **Seasonality:** Possible waves/variants showing in trends

### Geographic Characteristics
- **Hierarchical:** Country level with state/province breakdowns
- **Coverage:** Global (226 countries/regions)
- **Granularity:** 736 unique province/state entities
- **Distribution:** Uneven (major outbreaks concentrated in specific regions)

### Metric Characteristics
- **Nature:** Cumulative counts (monotonically non-decreasing)
- **Distribution:** Right-skewed (few high-case areas, many low-case areas)
- **Variance:** High standard deviation relative to mean
- **Correlation:** Confirmed > Deaths > Active > Recovered (generally)

---

## Known Limitations & Recommendations

### Data Collection Issues
1. **Reporting Delays:** Different countries have different reporting schedules
2. **Definition Changes:** COVID-19 definitions evolved over time (e.g., recovered criteria)
3. **Testing Capacity:** Confirmed cases depend on testing availability
4. **Geographic Granularity:** Province/State data quality varies by country

### Analysis Recommendations
1. **Smoothing:** Use rolling averages for trend visualization (daily volatility exists)
2. **Per-Capita:** Calculate rates per 100,000 population for fair comparison
3. **Lagging Effects:** Death rates lag confirmed cases by 1-2 weeks
4. **Regional Grouping:** Group by continent/WHO region for broader patterns
5. **Outlier Treatment:** Don't remove outliers; they represent real major outbreaks

---

## Usage for Downstream Analysis

### Ready for Visualization
- Time series plots (daily/weekly trends)
- Geographic heatmaps (choropleth maps)
- Scatter plots (Confirmed vs Deaths by country)
- Distribution histograms (log-scale for skewed data)
- Trend analysis with moving averages

### Ready for Statistical Analysis
- Correlation analysis (metrics and geographic regions)
- Hypothesis testing (difference between countries/continents)
- Outbreak detection (anomaly identification in time series)
- Forecasting (ARIMA, Prophet for future projections)

### Ready for Exploratory Data Analysis
- Distribution shapes and patterns
- Top/bottom countries/regions
- Critical dates/events (peaks, plateaus)
- Recovery vs mortality patterns
- Geographic clustering analysis

---

## Processing Script

**Location:** etl/clean_data.py

**Usage:**
```bash
python etl/clean_data.py
```

**Output:**
- `data/processed/covid_cleaned.csv` - Cleaned dataset (306,429 records × 13 columns)

**Reproducibility:**
- All transformations are deterministic
- Script can be rerun with updated raw data
- No random sampling or data loss (only corrections)

---

**Last Updated:** 2024
**Data Dictionary Version:** 1.0
