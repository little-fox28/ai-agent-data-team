# Squad Decisions

## Active Decisions

### 1. Project Structure Architecture (ripley-project-structure)
**Date:** 2026-04-01 | **Author:** Ripley (Lead) | **Status:** Approved

Implemented layered, modular architecture with:
- ETL pipeline (extract/transform/load modules)
- Layered data organization (raw → interim → processed)
- Phase-separated notebooks (exploratory → phase1 → phase2)
- Comprehensive documentation (README, DATA_DICTIONARY, ETL_GUIDE, SETUP_GUIDE)

**Key Principles:** Separation of concerns, data lineage, reproducibility, team memory
**Benefits:** Clear structure, modular code, easy maintenance, comprehensive docs
**Trade-offs:** More initial setup, requires discipline to maintain

### 2. Data Cleaning Strategy (newt-data-cleaning-strategy)
**Date:** 2024-04-01 | **Author:** Newt (Data Analyst) | **Status:** Approved

Conservative, corrective cleaning for COVID-19 dataset (306,429 records):
- Negative values → 0 (0.002% impact)
- Illogical records (Deaths + Recovered > Confirmed) → adjusted (0.88% impact)
- Missing Province/State → "Unknown" (25.5% impact)
- Inconsistent country names → standardized

**Rationale:** Preserves data completeness, maintains logical consistency, defensible corrections
**Impact:** Clean data ready for visualization; recommendations for future epidemiological use

### 3. Visualization Framework and Standards (hicks-visualization-framework)
**Date:** 2026-04-01 | **Author:** Hicks (Visualization Engineer) | **Status:** Approved

Implemented comprehensive visualization framework:
- **Utilities module** (visualization_utils.py) with reusable functions
- **Semantic colors:** Red (infections), Green (recoveries), Gray (deaths)
- **Standard sizes:** 5 presets (small, medium, large, wide, square) at 300 DPI
- **File naming:** {PHASE}_{REQUIREMENT}_{DESCRIPTION}.{EXT}
- **Tech split:** Matplotlib/Seaborn (PNG) + Plotly (HTML)

**Rationale:** Consistency across team, efficiency, quality, accessibility, reproducibility
**Files:** visualization_utils.py, notebook templates, VISUALIZATION_GUIDELINES.md

### 4. Test Suite Architecture (hudson-test-suite-architecture)
**Date:** 2026-04-01 | **Author:** Hudson (Tester) | **Status:** Implemented

Built comprehensive pytest suite (36 tests, 0.32 seconds):
- **Data Quality (14 tests):** Schema, nulls, duplicates, consistency, dates
- **Statistics (16 tests):** CFR, recovery rate, aggregations, time series
- **ETL (6 tests):** Extract, transform, load operations

**Patterns:** Fixtures (conftest.py), logical organization, descriptive names, edge cases
**Standards Enforced:** Non-negative counts, logical consistency, date validity, null handling
**Commands:** `pytest tests/ -v`, `pytest tests/ --cov=etl --cov-report=html`

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
