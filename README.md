# COVID-19 Data Visualization Project (DAT2061)

## Overview
This project analyzes and visualizes COVID-19 global data using Python, Pandas, Matplotlib, Seaborn, and Plotly. The assignment is divided into two phases: basic visualizations (Phase 1) and advanced visualizations (Phase 2).

**Student:** Tran Hung Thinh  
**Course:** DAT2061 - Data Visualization  
**Dataset:** COVID-19 Global Data (18.3 MB)

## Project Structure

```
ai-team/
├── src/                           # All source code and resources
│   ├── etl/                       # ETL Pipeline modules
│   │   ├── extract/               # Data extraction scripts
│   │   ├── transform/             # Data transformation scripts
│   │   └── load/                  # Data loading utilities
│   ├── config/                    # Configuration files
│   ├── notebooks/                 # Jupyter notebooks
│   │   ├── exploratory/           # Initial data exploration
│   │   ├── phase1/                # Phase 1 visualizations (Y1-01 to Y1-03)
│   │   └── phase2/                # Phase 2 visualizations (Y2-01 to Y2-02)
│   ├── data/                      # Data storage
│   │   ├── raw/                   # Original datasets (DO NOT MODIFY)
│   │   └── processed/             # Final cleaned datasets
│   ├── outputs/                   # Generated outputs
│   │   ├── visualizations/        # Saved charts and graphs
│   │   └── reports/               # Analysis reports and summaries
│   ├── docs/                      # Project documentation
│   ├── tests/                     # Unit tests for ETL pipeline
│   └── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r src/requirements.txt

# 2. Run ETL pipeline to process raw data
python src/etl/run_pipeline.py

# 3. Run tests to verify everything works
python -m pytest src/tests/ -v

# 4. Launch Jupyter for visualizations
python -m jupyter notebook src/notebooks/
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Jupyter Notebook or JupyterLab

### Installation

1. **Clone or download this repository**

2. **Enable Windows Long Paths (if on Windows):**
   ```powershell
   # Run PowerShell as Administrator
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

3. **Install required packages:**
   ```bash
   pip install -r src/requirements.txt
   ```

4. **Verify data files:**
   - Ensure `src/data/raw/covid_19_data.csv` exists (18.3 MB)
   - The raw data will be processed into `src/data/processed/` by ETL pipeline

5. **Launch Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```

## Assignment Structure

### Phase 1: Basic Visualizations (Y1-01 to Y1-03)

**Objective:** Understand data distribution and trends

**Deliverables:**
1. **Y1-01: Distribution Analysis**
   - Histogram of infection counts
   - Box plot for outlier detection
   - Density plot for probability distribution

2. **Y1-02: Time Series Analysis**
   - Line plots showing confirmed, deaths, recovered over time
   - Multi-country comparison charts

3. **Y1-03: Trend and Recovery Analysis**
   - Seasonality patterns in deaths
   - Recovery rate analysis by country/region
   - Trend decomposition

**Notebooks:** `src/notebooks/phase1/`

### Phase 2: Advanced Visualizations (Y2-01 to Y2-02)

**Objective:** Deep insights and interactive exploration

**Deliverables:**
1. **Y2-01: Advanced Statistical Plots**
   - Violin plots for distribution comparison
   - Heatmaps showing spread rates across regions
   - Radial plots for death rates by demographics

2. **Y2-02: Interactive and Geographic Visualizations**
   - Interactive Plotly charts with region selection
   - Choropleth maps showing global COVID impact
   - Animated time-based visualizations

**Notebooks:** `src/notebooks/phase2/`

## Dataset Information

**Source:** COVID-19 Global Dataset  
**Size:** 18.3 MB  
**Format:** CSV

**Columns:**
- `SNo`: Serial number
- `ObservationDate`: Date of observation (MM/DD/YYYY)
- `Province/State`: Province or state name (nullable)
- `Country/Region`: Country or region name
- `Last Update`: Timestamp of last update
- `Confirmed`: Cumulative confirmed cases
- `Deaths`: Cumulative deaths
- `Recovered`: Cumulative recoveries

**Time Range:** January 2020 onwards  
**Geographic Coverage:** Worldwide (200+ countries/regions)

See `docs/DATA_DICTIONARY.md` for detailed field descriptions.

## ETL Pipeline (OOP/SOLID)

The ETL pipeline uses **Object-Oriented Programming** with **SOLID principles**:

```
src/etl/
├── base/                    # Abstract interfaces
│   ├── extractor.py        # BaseExtractor (abstract)
│   ├── transformer.py      # BaseTransformer (abstract)
│   └── loader.py           # BaseLoader (abstract)
├── extractors/             # Concrete extractors
│   └── csv_extractor.py    # CSVExtractor
├── transformers/           # 6 single-responsibility transformers
│   ├── date_transformer.py
│   ├── missing_value_transformer.py
│   ├── anomaly_transformer.py
│   ├── geography_transformer.py
│   ├── metrics_transformer.py
│   └── outlier_transformer.py
├── loaders/                # Output loaders
│   └── csv_loader.py       # CSVLoader, LatestSnapshotLoader, CountryAggregateLoader
├── pipeline.py             # ETLPipeline orchestrator (Dependency Injection)
└── run_pipeline.py         # Entry point
```

**SOLID Compliance:**
| Principle | Implementation |
|-----------|----------------|
| **S**ingle Responsibility | Each transformer handles ONE transformation |
| **O**pen/Closed | Add new transformers without modifying pipeline |
| **L**iskov Substitution | All transformers interchangeable |
| **I**nterface Segregation | Small focused ABC interfaces |
| **D**ependency Inversion | Pipeline depends on abstractions |

### Run the ETL Pipeline

```bash
# Process raw data → cleaned data
python src/etl/run_pipeline.py
```

**Output files generated:**
- `src/data/processed/covid_cleaned.csv` - Full cleaned dataset
- `src/data/processed/covid_latest.csv` - Latest snapshot per location
- `src/data/processed/covid_by_country.csv` - Country-level aggregates

## 🧪 Testing

Run all tests:
```bash
pytest src/tests/ -v
```

Run specific test categories:
```bash
# Data quality tests
pytest src/tests/test_data_quality.py -v

# ETL pipeline tests
pytest src/tests/test_etl.py -v

# Statistics tests
pytest src/tests/test_statistics.py -v
```

## 📊 Running Visualizations

### Option 1: Jupyter Notebook (Interactive)

```bash
# Launch Jupyter
jupyter notebook

# Then navigate to:
# - src/notebooks/exploratory/  → Data exploration
# - src/notebooks/phase1/       → Basic visualizations (Y1-01 to Y1-03)
# - src/notebooks/phase2/       → Advanced visualizations (Y2-01 to Y2-02)
```

### Option 2: Direct Notebook Execution

```bash
# Explore data
jupyter notebook src/notebooks/exploratory/01_data_exploration.ipynb

# Phase 1: Distribution, Time Series, Trends
jupyter notebook src/notebooks/phase1/

# Phase 2: Advanced Stats, Interactive Charts, Maps
jupyter notebook src/notebooks/phase2/
```

### Option 3: Command Line (nbconvert)

```bash
# Execute notebook and save output
jupyter nbconvert --execute --to html src/notebooks/phase1/01_distribution_analysis.ipynb
```

## 📁 Outputs

All visualizations are automatically saved to:
- `src/outputs/visualizations/phase1/` - Phase 1 charts
- `src/outputs/visualizations/phase2/` - Phase 2 charts
- `src/outputs/reports/` - Analysis reports, ETL logs, summaries

## 🔧 Development Workflow

```
1. Data Exploration     → src/notebooks/exploratory/
2. ETL Processing       → python src/etl/run_pipeline.py
3. Run Tests            → pytest src/tests/ -v
4. Phase 1 Viz          → src/notebooks/phase1/
5. Phase 2 Viz          → src/notebooks/phase2/
6. Export Outputs       → src/outputs/
```

## Team AI Memory

This project uses the `.squad/` system for AI team collaboration:
- **Agent History:** `.squad/agents/{agent-name}/history.md`
- **Team Decisions:** `.squad/decisions.md`
- **Project Knowledge:** Maintained by Ripley (Lead)

Agents should read history files before starting work to understand project context.

## 🛠️ Tools and Libraries

- **Data Processing:** Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn, Plotly
- **Notebooks:** Jupyter, IPython
- **Maps:** Plotly Express, Folium (optional)
- **Testing:** pytest (for ETL validation)

## Contributing

For team members working on this project:
1. Read `.squad/agents/ripley/history.md` for project context
2. Follow the established folder structure
3. Document all major changes in appropriate history files
4. Save visualizations to designated output folders

## License

This is an academic project for DAT2061 course assignment.

## Contact

**Student:** Tran Hung Thinh  
**Assignment:** DAT2061 COVID-19 Data Visualization
