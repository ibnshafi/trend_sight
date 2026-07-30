"""
engine/trend_analysis.py
========================
Computes linear trend slope, R², rate of change per month, and projected
months-until-threshold-crossing for each lab marker per patient.

Prototype for educational/hackathon purposes only. Not a diagnostic device.
Not medical advice. Always consult a licensed clinician.

Risk thresholds / rate constants are illustrative, not clinically validated.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrendResult:
    """Result of a trend analysis for a single patient-marker pair."""

    marker: str
    unit: str
    normal_low: float
    normal_high: float

    # Trend statistics
    slope: float            # change in lab value per day
    r_squared: float        # goodness of fit (0-1)
    n_visits: int

    # Derived
    rate_per_month: float   # slope * 30.44
    months_until_low: Optional[float]   # months until crossing low threshold
    months_until_high: Optional[float]  # months until crossing high threshold
    latest_value: float
    is_above_high: bool     # currently exceeds upper limit
    is_below_low: bool      # currently below lower limit

    # Raw data (for charting / explanations)
    dates: list = None
    values: list = None


def analyze_marker(
    dates: pd.DatetimeIndex,
    values: np.ndarray,
    marker_name: str,
    unit: str,
    normal_low: float,
    normal_high: float,
) -> TrendResult:
    """
    Perform linear regression of lab values over time.

    Parameters
    ----------
    dates : array-like of datetime
        Visit dates.
    values : array of float
        Lab values at each visit.
    marker_name, unit, normal_low, normal_high : metadata.

    Returns
    -------
    TrendResult with slope (per day), R², rate/month, threshold projections.
    """
    # Convert dates to numeric days since first visit
    days_since_first = (pd.to_datetime(dates) - pd.to_datetime(dates[0])).days.values.astype(float)

    # Use 1D arrays for simple closed-form linear regression
    x = days_since_first.flatten()
    y = np.asarray(values, dtype=float)

    n = len(y)
    if n < 2:
        # Not enough data points for a trend
        return TrendResult(
            marker=marker_name,
            unit=unit,
            normal_low=normal_low,
            normal_high=normal_high,
            slope=0.0,
            r_squared=0.0,
            n_visits=n,
            rate_per_month=0.0,
            months_until_low=None,
            months_until_high=None,
            latest_value=y[-1] if n > 0 else 0.0,
            is_above_high=(y[-1] > normal_high) if n > 0 else False,
            is_below_low=(y[-1] < normal_low) if n > 0 else False,
            dates=dates.tolist() if hasattr(dates, 'tolist') else list(dates),
            values=y.tolist(),
        )

    # Linear regression using simple closed-form (demonstrates technique transparently)
    # slope = cov(x, y) / var(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)

    # Slope (change in lab value per day)
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    slope = numerator / denominator if abs(denominator) > 1e-12 else 0.0

    # Intercept
    intercept = y_mean - slope * x_mean

    # R²
    y_pred = intercept + slope * x
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 0.0

    # Rate per month (30.44 days avg)
    rate_per_month = slope * 30.44

    latest_value = float(y[-1])
    is_above_high = latest_value > normal_high
    is_below_low = latest_value < normal_low

    # Projected months to threshold crossing
    # If slope is zero (or very tiny), projection is undefined
    months_until_low = None
    months_until_high = None

    if abs(slope) > 1e-10:
        days_per_month = 30.44

        if slope < 0:
            # Value is decreasing — when will it hit normal_low?
            if latest_value > normal_low and not is_below_low:
                days_to_low = (normal_low - latest_value) / slope  # negative / negative = positive
                months_until_low = days_to_low / days_per_month if days_to_low > 0 else None
            elif is_below_low:
                months_until_low = 0.0  # already below
        else:
            # Value is increasing — when will it hit normal_high?
            if latest_value < normal_high and not is_above_high:
                days_to_high = (normal_high - latest_value) / slope
                months_until_high = days_to_high / days_per_month if days_to_high > 0 else None
            elif is_above_high:
                months_until_high = 0.0  # already above

    # Clip to reasonable range (no projections beyond 10 years)
    if months_until_low is not None and months_until_low > 120:
        months_until_low = None
    if months_until_high is not None and months_until_high > 120:
        months_until_high = None

    return TrendResult(
        marker=marker_name,
        unit=unit,
        normal_low=normal_low,
        normal_high=normal_high,
        slope=slope,
        r_squared=r_squared,
        n_visits=n,
        rate_per_month=rate_per_month,
        months_until_low=months_until_low,
        months_until_high=months_until_high,
        latest_value=latest_value,
        is_above_high=is_above_high,
        is_below_low=is_below_low,
        dates=dates.tolist() if hasattr(dates, 'tolist') else list(dates),
        values=y.tolist(),
    )


def analyze_persona(persona_df: pd.DataFrame) -> dict:
    """
    Analyze all markers for a single persona.

    Parameters
    ----------
    persona_df : DataFrame from persona_to_dataframe (long format).

    Returns
    -------
    dict of {marker_name: TrendResult}
    """
    results = {}
    for marker_name, group in persona_df.groupby("marker"):
        group = group.sort_values("visit_date")
        dates = group["visit_date"].values
        values = group["value"].values
        unit = group["unit"].iloc[0]
        normal_low = group["normal_low"].iloc[0]
        normal_high = group["normal_high"].iloc[0]

        results[marker_name] = analyze_marker(
            dates=pd.DatetimeIndex(dates),
            values=values,
            marker_name=marker_name,
            unit=unit,
            normal_low=normal_low,
            normal_high=normal_high,
        )
    return results
