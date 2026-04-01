# Ripley's Project Knowledge

## Initial Context (2026-04-01)

**Project:** COVID-19 Data Visualization Assignment (DAT2061)
**User:** Tran Hung Thinh
**Tech Stack:** Python, Pandas, Matplotlib, Seaborn, Plotly

**Dataset:** 
- COVID-19 global data (18.3MB CSV)
- Fields: SNo, ObservationDate, Province/State, Country/Region, Last Update, Confirmed, Deaths, Recovered
- Time range: January 2020 onwards
- Geographic coverage: Worldwide

**Assignment Structure:**
- **Phase 1 (Y1-01 to Y1-03):** Basic visualizations
  - Histogram, box plot, density plot for infection distribution
  - Time series plots for trends
  - Seasonality and trend analysis for deaths
  - Recovery rate analysis by country/region
  
- **Phase 2 (Y2-01 to Y2-02):** Advanced visualizations
  - Violin plots for distribution analysis
  - Heatmaps for spread rates
  - Radial plots for death rates by age
  - Interactive charts with region selection
  - Geographic maps showing global impact

## Learnings

### Project Structure Design (2026-04-01)

**Architecture Decision:**
Created a modular, layered project structure following data science best practices:

1. **ETL Pipeline Architecture**
   - Separation of concerns: Extract, Transform, Load as independent modules
   - Location: `etl/extract/`, `etl/transform/`, `etl/load/`
   - Orchestration: `etl/run_pipeline.py` coordinates the full pipeline
   - Pattern: Functional approach with clear input/output contracts

2. **Data Organization**
   - Raw data: `data/raw/` (immutable source)
   - Interim: `data/interim/` (temporary processing artifacts)
   - Processed: `data/processed/` (clean, analysis-ready data)
   - Principle: Never modify raw data, always preserve lineage

3. **Notebook Structure**
   - Exploratory: `notebooks/exploratory/` for initial data investigation
   - Phase 1: `notebooks/phase1/` for basic visualizations (Y1-01 to Y1-03)
   - Phase 2: `notebooks/phase2/` for advanced visualizations (Y2-01 to Y2-02)
   - Principle: Progressive complexity, clear phase separation

4. **Output Management**
   - Visualizations: `outputs/visualizations/phase1/` and `phase2/`
   - Reports: `outputs/reports/` for summaries and logs
   - Principle: Reproducible outputs, versioned by phase

**Key Files Created:**
- `README.md` - Comprehensive project overview and usage guide
- `requirements.txt` - All Python dependencies (pandas, matplotlib, seaborn, plotly, jupyter)
- `docs/DATA_DICTIONARY.md` - Complete dataset field documentation with examples
- `docs/ETL_GUIDE.md` - Detailed ETL pipeline documentation
- `docs/SETUP_GUIDE.md` - Quick start and troubleshooting guide
- `config/etl_config.yaml` - Centralized configuration for ETL pipeline
- `etl/run_pipeline.py` - Main ETL orchestrator with logging
- `tests/test_etl.py` - Unit tests for ETL components

**ETL Implementation Details:**
- Modular design with separate extract, transform, load modules
- Built-in data validation and quality checks
- Derived metrics: daily new cases, active cases, CFR, recovery rate
- Country name normalization for consistency
- Comprehensive logging to track pipeline execution
- Multiple output formats (full dataset, country aggregate, daily snapshot, latest)

**Notebook Templates:**
- Exploratory notebook with data profiling and quality assessment
- Phase 1 notebook with histogram, box plot, density, time series, trend analysis
- Phase 2 notebook with violin plots, heatmaps, radial charts, interactive Plotly visualizations
- All notebooks include proper setup, documentation, and output saving

**Design Patterns Applied:**
- Configuration as code (YAML config file)
- Separation of concerns (ETL modules)
- Test-driven development (pytest tests)
- Documentation-first approach (README, guides, data dictionary)
- Reproducibility (requirements.txt, clear workflow)

**Team Collaboration Features:**
- .gitkeep files in empty directories for version control
- Clear folder structure for team navigation
- Comprehensive documentation for AI team memory
- Step-by-step setup guide for onboarding

**Technical Decisions:**
- Python 3.8+ for modern features
- Pandas for data manipulation
- Matplotlib + Seaborn for static visualizations
- Plotly for interactive visualizations
- Jupyter for reproducible analysis
- pytest for testing
- YAML for configuration

**User Preferences Noted:**
- Wants clear structure for AI team to remember
- Needs comprehensive documentation
- Values modular, maintainable code
- Requires both static and interactive visualizations

## Cross-Team Updates (2026-04-01)

### Newt's Data Analysis Complete
**Status:** 306,429 records processed; cleaned dataset ready in `data/processed/covid_cleaned.csv`
- All data quality issues documented: 6 negative values, 2,685 illogical records, 78,103 missing provinces, 16,253 name inconsistencies
- Derived metrics added: Active cases, Death Rate, Recovery Rate, Active Rate
- Key findings: Death rates 1.17%-19.6%, top countries US/India/Brazil
- Recommendations: Use log-scale, apply moving averages, calculate per-capita rates

**Integration:** Cleaned data ready for visualization pipeline

### Hicks' Visualization Framework Ready
**Status:** Framework complete with utilities, templates, and guidelines
- Utilities module created with reusable plotting functions
- Semantic color scheme: Red (infections), Green (recoveries), Gray (deaths)
- Standard figure sizes and 300 DPI export settings
- Phase 1 and Phase 2 notebook templates with TODO structure
- Guidelines document with standards and best practices

**Integration:** Framework uses ETL outputs; ready for implementation

### Hudson's Test Suite Passing
**Status:** 36 tests passing in 0.32 seconds
- 14 data quality tests (schema, nulls, dates, geography)
- 16 statistics tests (rates, aggregations, time series)
- 6 ETL pipeline tests
- Comprehensive fixture library and configuration

**Integration:** Tests validate all ETL transformations and statistics

