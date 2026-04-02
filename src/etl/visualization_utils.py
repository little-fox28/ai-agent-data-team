"""
Visualization Utilities for COVID-19 Data Analysis
===================================================

This module provides reusable helper functions for creating consistent,
professional visualizations across all phases of the project.

Author: Hicks (Visualization Engineer)
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
from typing import Optional, Tuple, List, Dict, Any


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Color palettes for different visualization types
COLOR_PALETTES = {
    'primary': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
    'sequential': 'YlOrRd',  # For heatmaps, choropleth
    'diverging': 'RdYlGn',   # For rate comparisons
    'categorical': 'Set2',   # For categorical data
    'infection': '#e74c3c',  # Red for infections
    'death': '#34495e',      # Dark gray for deaths
    'recovery': '#27ae60',   # Green for recoveries
}

# Standard figure sizes (width, height in inches)
FIGURE_SIZES = {
    'small': (8, 6),
    'medium': (12, 8),
    'large': (16, 10),
    'wide': (16, 6),
    'square': (10, 10),
}

# Font sizes for different elements
FONT_SIZES = {
    'title': 16,
    'subtitle': 14,
    'label': 12,
    'tick': 10,
    'legend': 11,
}

# Plot style settings
PLOT_STYLE = 'seaborn-v0_8-darkgrid'
DPI = 300  # High resolution for saved figures


# ============================================================================
# SETUP & INITIALIZATION
# ============================================================================

def setup_plotting_environment():
    """
    Configure matplotlib and seaborn with project-wide settings.
    Call this at the beginning of each notebook.
    """
    plt.style.use(PLOT_STYLE)
    sns.set_palette(COLOR_PALETTES['primary'])
    
    # Set default figure parameters
    plt.rcParams['figure.figsize'] = FIGURE_SIZES['medium']
    plt.rcParams['figure.dpi'] = 100  # Display DPI
    plt.rcParams['savefig.dpi'] = DPI
    plt.rcParams['font.size'] = FONT_SIZES['tick']
    plt.rcParams['axes.labelsize'] = FONT_SIZES['label']
    plt.rcParams['axes.titlesize'] = FONT_SIZES['title']
    plt.rcParams['xtick.labelsize'] = FONT_SIZES['tick']
    plt.rcParams['ytick.labelsize'] = FONT_SIZES['tick']
    plt.rcParams['legend.fontsize'] = FONT_SIZES['legend']
    
    print("✓ Plotting environment configured")


# ============================================================================
# FILE MANAGEMENT
# ============================================================================

def get_output_path(phase: str, filename: str, create_dir: bool = True) -> Path:
    """
    Generate standardized output path for saving visualizations.
    
    Args:
        phase: 'phase1' or 'phase2'
        filename: Name of the output file (include extension)
        create_dir: Whether to create directory if it doesn't exist
    
    Returns:
        Path object for the output file
    """
    base_path = Path(__file__).parent.parent / 'outputs' / 'visualizations' / phase
    
    if create_dir:
        base_path.mkdir(parents=True, exist_ok=True)
    
    return base_path / filename


def save_figure(fig, phase: str, filename: str, formats: List[str] = ['png']):
    """
    Save a matplotlib/seaborn figure to the appropriate output directory.
    
    Args:
        fig: Matplotlib figure object
        phase: 'phase1' or 'phase2'
        filename: Base filename (without extension)
        formats: List of formats to save ['png', 'pdf', 'svg']
    """
    for fmt in formats:
        output_path = get_output_path(phase, f"{filename}.{fmt}")
        fig.savefig(output_path, dpi=DPI, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")


def save_plotly_figure(fig, phase: str, filename: str, 
                       save_html: bool = True, save_png: bool = False):
    """
    Save a Plotly figure as HTML and optionally as static PNG.
    
    Args:
        fig: Plotly figure object
        phase: 'phase1' or 'phase2'
        filename: Base filename (without extension)
        save_html: Save interactive HTML version
        save_png: Save static PNG version
    """
    if save_html:
        html_path = get_output_path(phase, f"{filename}.html")
        fig.write_html(html_path)
        print(f"✓ Saved interactive: {html_path}")
    
    if save_png:
        png_path = get_output_path(phase, f"{filename}.png")
        fig.write_image(png_path, width=1600, height=1000)
        print(f"✓ Saved static: {png_path}")


# ============================================================================
# DATA AGGREGATION HELPERS
# ============================================================================

def aggregate_by_time(df: pd.DataFrame, 
                      date_col: str,
                      value_col: str,
                      freq: str = 'D',
                      agg_func: str = 'sum') -> pd.DataFrame:
    """
    Aggregate data by time period.
    
    Args:
        df: Input dataframe
        date_col: Name of date column
        value_col: Name of value column to aggregate
        freq: Frequency ('D'=daily, 'W'=weekly, 'M'=monthly)
        agg_func: Aggregation function ('sum', 'mean', 'count', etc.)
    
    Returns:
        Aggregated dataframe with datetime index
    """
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    df_copy = df_copy.set_index(date_col)
    
    return df_copy[value_col].resample(freq).agg(agg_func).reset_index()


def calculate_rolling_average(df: pd.DataFrame,
                              value_col: str,
                              window: int = 7) -> pd.Series:
    """
    Calculate rolling average for smoothing time series data.
    
    Args:
        df: Input dataframe
        value_col: Column to calculate rolling average on
        window: Rolling window size (default: 7 days)
    
    Returns:
        Series with rolling average values
    """
    return df[value_col].rolling(window=window, center=True).mean()


def calculate_rates(df: pd.DataFrame,
                   numerator_col: str,
                   denominator_col: str,
                   rate_name: str = 'rate') -> pd.Series:
    """
    Calculate rates (e.g., death rate, recovery rate) as percentages.
    
    Args:
        df: Input dataframe
        numerator_col: Column for numerator
        denominator_col: Column for denominator
        rate_name: Name for the output series
    
    Returns:
        Series with calculated rates
    """
    rates = (df[numerator_col] / df[denominator_col] * 100).fillna(0)
    rates.name = rate_name
    return rates


# ============================================================================
# STYLING HELPERS
# ============================================================================

def apply_standard_styling(ax, title: str, xlabel: str = '', ylabel: str = '',
                          grid: bool = True, legend: bool = True):
    """
    Apply consistent styling to matplotlib axes.
    
    Args:
        ax: Matplotlib axes object
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        grid: Whether to show grid
        legend: Whether to show legend
    """
    ax.set_title(title, fontsize=FONT_SIZES['title'], fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=FONT_SIZES['label'])
    ax.set_ylabel(ylabel, fontsize=FONT_SIZES['label'])
    
    if grid:
        ax.grid(True, alpha=0.3, linestyle='--')
    
    if legend and ax.get_legend() is not None:
        ax.legend(fontsize=FONT_SIZES['legend'], frameon=True, shadow=True)
    
    # Improve tick label formatting
    ax.tick_params(axis='both', which='major', labelsize=FONT_SIZES['tick'])


def format_large_numbers(ax, axis: str = 'y'):
    """
    Format axis to display large numbers with K, M suffixes.
    
    Args:
        ax: Matplotlib axes object
        axis: Which axis to format ('x', 'y', or 'both')
    """
    from matplotlib.ticker import FuncFormatter
    
    def format_func(value, tick_number):
        if abs(value) >= 1e6:
            return f'{value/1e6:.1f}M'
        elif abs(value) >= 1e3:
            return f'{value/1e3:.1f}K'
        else:
            return f'{value:.0f}'
    
    formatter = FuncFormatter(format_func)
    
    if axis in ['y', 'both']:
        ax.yaxis.set_major_formatter(formatter)
    if axis in ['x', 'both']:
        ax.xaxis.set_major_formatter(formatter)


# ============================================================================
# PLOTLY HELPERS
# ============================================================================

def get_plotly_template() -> Dict[str, Any]:
    """
    Get standard Plotly template configuration for consistent styling.
    
    Returns:
        Dictionary with Plotly layout parameters
    """
    return {
        'template': 'plotly_white',
        'font': {'family': 'Arial, sans-serif', 'size': FONT_SIZES['tick']},
        'title': {'font': {'size': FONT_SIZES['title'], 'color': '#2c3e50'}},
        'xaxis': {'title_font': {'size': FONT_SIZES['label']}},
        'yaxis': {'title_font': {'size': FONT_SIZES['label']}},
        'hoverlabel': {'font': {'size': FONT_SIZES['tick']}},
    }


def create_plotly_figure(title: str, width: int = 1200, height: int = 600) -> go.Figure:
    """
    Create a Plotly figure with standard configuration.
    
    Args:
        title: Figure title
        width: Figure width in pixels
        height: Figure height in pixels
    
    Returns:
        Configured Plotly figure object
    """
    fig = go.Figure()
    layout_config = get_plotly_template()
    
    fig.update_layout(
        title=title,
        width=width,
        height=height,
        **layout_config
    )
    
    return fig


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_data_for_plotting(df: pd.DataFrame, 
                               required_columns: List[str]) -> bool:
    """
    Validate that dataframe has required columns and data for plotting.
    
    Args:
        df: Input dataframe
        required_columns: List of column names that must exist
    
    Returns:
        True if validation passes
    
    Raises:
        ValueError if validation fails
    """
    if df is None or df.empty:
        raise ValueError("Dataframe is None or empty")
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return True


# ============================================================================
# EXPORT & REPORTING
# ============================================================================

def create_visualization_summary(phase: str) -> pd.DataFrame:
    """
    Create a summary report of all visualizations in a phase.
    
    Args:
        phase: 'phase1' or 'phase2'
    
    Returns:
        Dataframe with visualization inventory
    """
    phase_path = Path(__file__).parent.parent / 'outputs' / 'visualizations' / phase
    
    if not phase_path.exists():
        return pd.DataFrame(columns=['filename', 'type', 'size_kb', 'created'])
    
    files = []
    for file in phase_path.glob('*'):
        if file.is_file():
            files.append({
                'filename': file.name,
                'type': file.suffix,
                'size_kb': file.stat().st_size / 1024,
                'created': pd.Timestamp.fromtimestamp(file.stat().st_mtime)
            })
    
    return pd.DataFrame(files).sort_values('filename')


if __name__ == '__main__':
    # Test the module
    print("Visualization Utilities Module")
    print("=" * 50)
    setup_plotting_environment()
    print(f"\nColor palettes available: {list(COLOR_PALETTES.keys())}")
    print(f"Figure sizes available: {list(FIGURE_SIZES.keys())}")
    print("\n✓ Module loaded successfully")
