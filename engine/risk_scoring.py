"""
engine/risk_scoring.py
======================
Combines distance-to-threshold and slope steepness into a transparent
Trend Risk Score (Low / Watch / Elevated).

Risk thresholds are illustrative, not clinically validated.

How the score works (fully transparent — no black box):
  1. Determine the direction of concern:
     - If slope is positive and moving toward normal_high → "high-side risk"
     - If slope is negative and moving toward normal_low → "low-side risk"
     - If flat or moving away from thresholds → Low risk.

  2. Calculate two sub-scores:
     - PROXIMITY_SCORE (0-5): How close the latest value is to the concerning
       threshold. 0 = at midpoint of range, 5 = at or past threshold.
     - VELOCITY_SCORE  (0-5): How fast the value is moving toward the
       threshold. 0 = flat/stable, 5 = steep decline/increase.

  3. TREND RISK SCORE = PROXIMITY + VELOCITY → mapped to:
       - Low      (0-3)
       - Watch    (4-6)
       - Elevated (7-10)
"""

from dataclasses import dataclass
from typing import Optional
from engine.trend_analysis import TrendResult


@dataclass
class RiskScore:
    marker: str
    unit: str
    risk_category: str  # "Low" | "Watch" | "Elevated"
    raw_score: int      # 0-10
    proximity_score: float
    velocity_score: float
    direction_of_concern: Optional[str]  # None, "high-side", "low-side"
    explanation: str    # One-line plain explanation


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def score_marker(tr: TrendResult) -> RiskScore:
    """
    Compute Trend Risk Score for a single marker's trend result.

    Parameters
    ----------
    tr : TrendResult from engine.trend_analysis.

    Returns
    -------
    RiskScore with category, raw_score, and explanation.
    """
    # Determine direction of concern
    direction = None
    if tr.slope > 1e-6:  # increasing
        # Concerned about hitting normal_high
        if tr.latest_value < tr.normal_high:
            direction = "high-side"
        elif tr.latest_value >= tr.normal_high:
            direction = "high-side"  # already above, still concerned
    elif tr.slope < -1e-6:  # decreasing
        # Concerned about hitting normal_low
        if tr.latest_value > tr.normal_low:
            direction = "low-side"
        elif tr.latest_value <= tr.normal_low:
            direction = "low-side"  # already below

    # If no concerning direction, risk is Low
    if direction is None:
        return RiskScore(
            marker=tr.marker,
            unit=tr.unit,
            risk_category="Low",
            raw_score=0,
            proximity_score=0.0,
            velocity_score=0.0,
            direction_of_concern=None,
            explanation=f"{tr.marker} is stable — no concerning trend detected.",
        )

    # -- PROXIMITY SCORE (0-5) --
    # How far is the latest value from the midpoint of the normal range?
    range_width = tr.normal_high - tr.normal_low
    midpoint = (tr.normal_low + tr.normal_high) / 2.0

    if direction == "high-side":
        # Distance from midpoint toward high end
        # 0 when at midpoint, 1 when at normal_high, >1 when past it
        dist_ratio = (tr.latest_value - midpoint) / (range_width / 2.0) if range_width > 0 else 0
        proximity = _clamp(dist_ratio * 5.0, 0.0, 5.0)
    else:  # low-side
        dist_ratio = (midpoint - tr.latest_value) / (range_width / 2.0) if range_width > 0 else 0
        proximity = _clamp(dist_ratio * 5.0, 0.0, 5.0)

    # -- VELOCITY SCORE (0-5) --
    # How fast is the value changing per month relative to range width?
    # Interpret: if the rate_per_month covers >50% of range in a year → very fast
    monthly_range_fraction = abs(tr.rate_per_month) / range_width if range_width > 0 else 0
    # Normalize: 0 = flat, 5 = ≥10% of range per month (would cross entire range in ~10 months)
    velocity = _clamp((monthly_range_fraction / 0.10) * 5.0, 0.0, 5.0)

    # -- RAW SCORE (0-10) --
    raw_score = int(round(proximity + velocity))
    raw_score = _clamp(raw_score, 0, 10)

    # -- CATEGORY --
    if raw_score <= 3:
        category = "Low"
    elif raw_score <= 6:
        category = "Watch"
    else:
        category = "Elevated"

    # -- EXPLANATION --
    if category == "Low":
        explanation = f"{tr.marker} shows minimal change — no action needed at this time."
    elif category == "Watch":
        explanation = (
            f"{tr.marker} is trending {'downward' if direction == 'low-side' else 'upward'} "
            f"({abs(tr.rate_per_month):.2f} {tr.unit}/month). "
            f"Still within normal range but worth monitoring."
        )
    else:  # Elevated
        if tr.is_above_high or tr.is_below_low:
            explanation = (
                f"{tr.marker} ({tr.latest_value:.1f} {tr.unit}) has already crossed "
                f"the normal range and continues to trend {'downward' if direction == 'low-side' else 'upward'}."
            )
        else:
            explanation = (
                f"{tr.marker} is trending {'downward' if direction == 'low-side' else 'upward'} "
                f"rapidly ({abs(tr.rate_per_month):.2f} {tr.unit}/month) and may cross "
                f"the normal threshold soon."
            )

    return RiskScore(
        marker=tr.marker,
        unit=tr.unit,
        risk_category=category,
        raw_score=raw_score,
        proximity_score=proximity,
        velocity_score=velocity,
        direction_of_concern=direction,
        explanation=explanation,
    )


def score_all_markers(trend_results: dict) -> list:
    """
    Score all markers for a single patient.

    Parameters
    ----------
    trend_results : dict of {marker_name: TrendResult}

    Returns
    -------
    list of RiskScore, sorted by raw_score descending (most concerning first).
    """
    scores = [score_marker(tr) for tr in trend_results.values()]
    scores.sort(key=lambda s: s.raw_score, reverse=True)
    return scores
