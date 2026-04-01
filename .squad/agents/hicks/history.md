# Hicks' Project Knowledge

## Initial Context (2026-04-01)

**Project:** COVID-19 Data Visualization Assignment (DAT2061)
**User:** Tran Hung Thinh
**Tech Stack:** Python, Pandas, Matplotlib, Seaborn, Plotly

**Visualization Requirements:**

**Phase 1 - Basic Plots:**
- Y1-01: Histogram (infection distribution), Box plot (deaths with outliers), Density plot (recoveries)
- Y1-02: Time series (daily/monthly infections), Trend plots (long-term patterns), Seasonality plots (deaths)
- Y1-03: Recovery rate distribution, Death rate by age groups, Geographic distribution maps, Regional trend comparisons

**Phase 2 - Advanced Plots:**
- Y2-01: Violin plots (infection distribution by country), Heatmap (spread rate over time), Radial plot (death rate by age)
- Y2-02: Interactive charts (region selection, hover details), Geographic map (world map with infection levels), Interactive violin plots (regional filtering)

**Key Principles:**
- Clear labeling and titles
- Appropriate color schemes
- Interactive elements for exploration
- Performance optimization for 18MB dataset

## Learnings

### 2026-04-01: Visualization Framework Setup

**Task Completed**: Set up comprehensive visualization framework for Phase 1 and Phase 2 work.

**What I Created**:

1. **Visualization Utils Module** (`etl/visualization_utils.py`):
   - Reusable helper functions for consistent plotting
   - Color palettes (semantic colors for infections/deaths/recoveries)
   - Standard figure sizes and font configurations
   - File management functions (save figures to correct locations)
   - Data aggregation helpers (time series, rolling averages, rate calculations)
   - Styling helpers (formatting, large numbers, axes)
   - Plotly template configurations
   - Validation and reporting utilities

2. **Phase 1 Notebook Template** (`notebooks/phase1_basic_visualizations.ipynb`):
   - Complete structure for all Y1-01, Y1-02, Y1-03 requirements
   - Histogram, box plot, density plot sections (Y1-01)
   - Time series, trend, seasonality sections (Y1-02)
   - Regional comparisons, rates, geographic maps sections (Y1-03)
   - Code stubs with TODO comments and examples
   - Markdown cells explaining each requirement
   - Summary and validation section

3. **Phase 2 Notebook Template** (`notebooks/phase2_advanced_visualizations.ipynb`):
   - Structure for Y2-01 and Y2-02 requirements
   - Violin plot, heatmap, radial plot sections (Y2-01)
   - Interactive time series, maps, violin plots, dashboard (Y2-02)
   - Advanced widgets section for custom interactivity
   - All using Plotly for interactive features

4. **Documentation**:
   - `outputs/README.md`: Explains output structure, naming conventions, usage
   - `docs/VISUALIZATION_GUIDELINES.md`: Comprehensive visualization standards
     - Color schemes, typography, figure dimensions
     - Chart-specific guidelines (histograms, box plots, time series, etc.)
     - Quality checklist, examples, best practices

**Key Decisions**:
- Used semantic colors: Red for infections, Green for recoveries, Dark gray for deaths
- Standardized figure sizes: small (8×6), medium (12×8), large (16×10), wide (16×6), square (10×10)
- 300 DPI for all exported images (publication quality)
- File naming convention: `{PHASE}_{REQUIREMENT}_{DESCRIPTION}.{EXT}`
- Plotly for all interactive visualizations (HTML exports)
- Matplotlib/Seaborn for static visualizations (PNG exports)

**File Paths to Remember**:
- Utility module: `etl/visualization_utils.py`
- Phase 1 notebook: `notebooks/phase1_basic_visualizations.ipynb`
- Phase 2 notebook: `notebooks/phase2_advanced_visualizations.ipynb`
- Guidelines: `docs/VISUALIZATION_GUIDELINES.md`
- Output location: `outputs/visualizations/phase1/` and `phase2/`

**Next Steps**:
- Wait for Newt to provide cleaned data
- Implement actual visualizations using the templates
- Test performance with the 18MB dataset
- Validate all plots meet guidelines and requirements

**Integration Points**:
- Templates import from `etl.visualization_utils`
- Expect cleaned data in `data/processed/covid_cleaned.csv`
- All outputs automatically saved to `outputs/visualizations/`

## Cross-Team Updates (2026-04-01)

### Ripley's Project Architecture Complete
**Status:** Modular, layered architecture with ETL pipeline and full documentation
- Directory structure: data (raw/interim/processed), etl, notebooks, tests, docs
- ETL pipeline: run_pipeline.py with extract/transform/load modules
- Notebooks: exploratory, phase1, phase2 templates
- Documentation: comprehensive README, DATA_DICTIONARY, ETL_GUIDE, SETUP_GUIDE
- Tests: 6 passing tests in test_etl.py

**Integration:** Framework location, output directories, test structure all ready

### Newt's Data Analysis Complete
**Status:** 306,429 records cleaned; data ready in `data/processed/covid_cleaned.csv`
- Data quality fixed: 6 negative values, 2,685 illogical records, 78,103 missing locations
- Derived metrics: Active cases, Death Rate, Recovery Rate, Active Rate
- Analysis: Right-skewed distribution, strong correlations, multiple pandemic waves
- Key findings: Death rates 1.17%-19.6%, top countries US/India/Brazil

**Integration:** Cleaned data matches expected location and schema

### Hudson's Test Suite Complete
**Status:** 36 passing tests validating data quality and ETL (0.32 seconds)
- Data quality tests: Schema, nulls, duplicates, consistency, date validation
- Statistics tests: Rates, aggregations, active cases, time series
- ETL tests: Extract, transform, load operations
- All standards enforced: Non-negative counts, logical consistency, null handling

**Integration:** Tests validate framework and data integrity

