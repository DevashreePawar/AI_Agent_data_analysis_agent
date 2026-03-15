# =============================================================
#  tools.py — The Agent's "Hands"
# =============================================================
#
#  This file contains every function (tool) that the AI agent
#  is allowed to call. Think of these as skills the agent
#  can choose to use when analysing a dataset.
#
#  KEY CONCEPT: Tool Use
#  In agentic AI, a "tool" is just a Python function that the
#  LLM can decide to call. The LLM doesn't run code itself —
#  it outputs the name + arguments, and WE run the function
#  and hand the result back. This is called "function calling".
# =============================================================

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # Non-interactive backend (no GUI window needed)
import matplotlib.pyplot as plt
import numpy as np

# ── Shared State ─────────────────────────────────────────────
# The agent operates on one DataFrame at a time.
# We store it here so every tool can access it without
# passing it around as an argument.
_df: pd.DataFrame = None
OUTPUT_DIR = "output"


# ── Helper ───────────────────────────────────────────────────
def _ensure_output_dir():
    """Create the output/ folder if it doesn't already exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _require_data():
    """Raise a friendly error if load_data() hasn't been called yet."""
    if _df is None:
        raise RuntimeError("No data loaded. Call load_data(filepath) first.")


# =============================================================
#  TOOL 1 — load_data
# =============================================================
def load_data(filepath: str) -> str:
    """
    Load a CSV file into memory.

    WHY THIS TOOL EXISTS:
    The agent needs data to work with. This is always the
    first tool the agent calls — it's step zero.

    Args:
        filepath: Path to the CSV file (e.g. "data/sample_sales.csv")

    Returns:
        A summary string the agent can read (rows, columns, column names).
    """
    global _df
    _df = pd.read_csv(filepath)
    cols = ", ".join(_df.columns.tolist())
    return (
        f"Data loaded successfully!\n"
        f"  Shape : {_df.shape[0]} rows × {_df.shape[1]} columns\n"
        f"  Columns: {cols}"
    )


# =============================================================
#  TOOL 2 — describe_data
# =============================================================
def describe_data() -> str:
    """
    Get a high-level overview of the loaded dataset.

    WHY THIS TOOL EXISTS:
    Before diving into specific columns, the agent surveys
    the whole dataset — are there missing values? What are
    the data types? This mirrors what a human analyst does.

    Returns:
        A text summary of dtypes and missing-value counts.
    """
    _require_data()

    dtypes = _df.dtypes.to_string()
    missing = _df.isnull().sum()
    missing_str = missing[missing > 0].to_string() if missing.any() else "None"
    numeric_cols = _df.select_dtypes(include="number").columns.tolist()
    cat_cols = _df.select_dtypes(include="object").columns.tolist()

    return (
        f"Dataset Overview\n"
        f"  Rows   : {_df.shape[0]}\n"
        f"  Columns: {_df.shape[1]}\n\n"
        f"Column Data Types:\n{dtypes}\n\n"
        f"Missing Values:\n  {missing_str}\n\n"
        f"Numeric columns : {numeric_cols}\n"
        f"Categorical cols: {cat_cols}"
    )


# =============================================================
#  TOOL 3 — compute_stats
# =============================================================
def compute_stats(column: str) -> str:
    """
    Compute descriptive statistics for a single numeric column.

    WHY THIS TOOL EXISTS:
    Once the agent knows which columns exist, it drills into
    each numeric column to understand its distribution.
    Mean/median/std are the bread-and-butter of data analysis.

    Args:
        column: The column name to analyse.

    Returns:
        Mean, median, std deviation, min, max, and skewness.
    """
    _require_data()

    if column not in _df.columns:
        return f"Error: Column '{column}' not found. Available: {_df.columns.tolist()}"

    s = _df[column].dropna()
    if not pd.api.types.is_numeric_dtype(s):
        return f"Column '{column}' is not numeric. Use value_counts() for categorical data."

    return (
        f"Statistics for '{column}':\n"
        f"  Count  : {s.count()}\n"
        f"  Mean   : {s.mean():.2f}\n"
        f"  Median : {s.median():.2f}\n"
        f"  Std Dev: {s.std():.2f}\n"
        f"  Min    : {s.min():.2f}\n"
        f"  Max    : {s.max():.2f}\n"
        f"  Skew   : {s.skew():.2f}  (>1 or <-1 suggests skewed distribution)"
    )


# =============================================================
#  TOOL 4 — find_correlations
# =============================================================
def find_correlations() -> str:
    """
    Find the top correlations between all numeric columns.

    WHY THIS TOOL EXISTS:
    Correlation reveals relationships between variables
    (e.g. "does discount affect revenue?"). This is one of
    the most valuable quick-win analyses in data exploration.

    Returns:
        Top 10 column pairs sorted by absolute correlation.
    """
    _require_data()

    numeric_df = _df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return "Not enough numeric columns to compute correlations."

    corr = numeric_df.corr().abs()

    # Extract upper triangle only (avoid duplicates like A-B AND B-A)
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    pairs = (
        upper.stack()
        .reset_index()
        .rename(columns={"level_0": "col_a", "level_1": "col_b", 0: "correlation"})
        .sort_values("correlation", ascending=False)
        .head(10)
    )

    lines = ["Top Correlations (absolute value):"]
    for _, row in pairs.iterrows():
        lines.append(f"  {row['col_a']} ↔ {row['col_b']}: {row['correlation']:.3f}")
    return "\n".join(lines)


# =============================================================
#  TOOL 5 — plot_histogram
# =============================================================
def plot_histogram(column: str) -> str:
    """
    Save a histogram of a numeric column to output/.

    WHY THIS TOOL EXISTS:
    Visualisation is key to spotting patterns, skew, and
    outliers. The agent generates charts automatically so
    the human can review them after the run.

    Args:
        column: The column to plot.

    Returns:
        The file path where the chart was saved.
    """
    _require_data()
    _ensure_output_dir()

    if column not in _df.columns:
        return f"Error: Column '{column}' not found."

    s = _df[column].dropna()
    if not pd.api.types.is_numeric_dtype(s):
        return f"Column '{column}' is not numeric."

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(s, bins=20, color="#4F81BD", edgecolor="white", alpha=0.85)
    ax.set_title(f"Distribution of '{column}'", fontsize=14, fontweight="bold")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, f"hist_{column}.png")
    plt.savefig(out_path, dpi=150)
    plt.close(fig)

    return f"Histogram saved → {out_path}"


# =============================================================
#  TOOL 6 — detect_outliers
# =============================================================
def detect_outliers(column: str) -> str:
    """
    Detect outliers in a numeric column using the IQR method.

    WHY THIS TOOL EXISTS:
    Outliers can skew analysis and often represent data
    quality issues or genuinely interesting anomalies.
    IQR (Interquartile Range) is a robust, standard method.

    HOW IQR WORKS:
        Q1 = 25th percentile,  Q3 = 75th percentile
        IQR = Q3 - Q1
        Outliers = values below (Q1 - 1.5×IQR)
                   OR above (Q3 + 1.5×IQR)

    Args:
        column: The numeric column to check.

    Returns:
        Count of outliers, their values, and boundary thresholds.
    """
    _require_data()

    if column not in _df.columns:
        return f"Error: Column '{column}' not found."

    s = _df[column].dropna()
    if not pd.api.types.is_numeric_dtype(s):
        return f"Column '{column}' is not numeric."

    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

    outliers = s[(s < lower) | (s > upper)]

    if outliers.empty:
        return f"No outliers found in '{column}' (bounds: {lower:.2f} to {upper:.2f})."

    return (
        f"Outliers in '{column}':\n"
        f"  IQR bounds: [{lower:.2f}, {upper:.2f}]\n"
        f"  Count      : {len(outliers)}\n"
        f"  Values     : {outliers.values.tolist()}"
    )


# =============================================================
#  TOOL 7 — value_counts
# =============================================================
def value_counts(column: str) -> str:
    """
    Show frequency counts for a categorical (text) column.

    WHY THIS TOOL EXISTS:
    For columns like 'region' or 'product', we want to know
    how often each category appears. This helps spot dominant
    categories and imbalances.

    Args:
        column: The categorical column to analyse.

    Returns:
        Top 15 value counts with percentages.
    """
    _require_data()

    if column not in _df.columns:
        return f"Error: Column '{column}' not found."

    counts = _df[column].value_counts().head(15)
    total = len(_df)
    lines = [f"Value counts for '{column}':"]
    for val, cnt in counts.items():
        pct = 100 * cnt / total
        lines.append(f"  {val:<20} {cnt:>5}  ({pct:.1f}%)")
    return "\n".join(lines)


# =============================================================
#  TOOL REGISTRY
# =============================================================
#  This dictionary maps tool names (strings) to their actual
#  function objects. The agent uses this to look up and call
#  the right function at runtime.
#
#  WHY A REGISTRY:
#  The LLM outputs text like: Action: compute_stats("revenue")
#  We parse that text and look up "compute_stats" here.
# =============================================================
TOOLS = {
    "load_data": load_data,
    "describe_data": describe_data,
    "compute_stats": compute_stats,
    "find_correlations": find_correlations,
    "plot_histogram": plot_histogram,
    "detect_outliers": detect_outliers,
    "value_counts": value_counts,
}

# Human-readable tool descriptions sent to the LLM so it knows what each tool does
TOOL_DESCRIPTIONS = """
Available tools:
  load_data(filepath)      — Load a CSV file. Always call this first.
  describe_data()          — Get column names, dtypes, and missing value counts.
  compute_stats(column)    — Mean, median, std, min, max, skewness for a numeric column.
  find_correlations()      — Find the top correlations between numeric columns.
  plot_histogram(column)   — Save a histogram chart for a numeric column.
  detect_outliers(column)  — Find outliers in a numeric column using the IQR method.
  value_counts(column)     — Frequency table for a categorical (text) column.
  FINISH                   — Stop the loop and generate the final report.
"""
