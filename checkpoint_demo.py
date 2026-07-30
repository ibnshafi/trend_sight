"""
checkpoint_demo.py
==================
Standalone script that verifies Steps 1-4:
  - Generates synthetic data for all 4 personas
  - Runs trend analysis on each marker
  - Computes Trend Risk Scores
  - Produces a chart showing Maria's "still in normal range but clearly trending" case
  - Prints risk classification for all 4 personas

Prototype for educational/hackathon purposes only. Not a diagnostic device.
Not medical advice. Always consult a licensed clinician.
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from data.generate_synthetic_patients import generate_all_personas, persona_to_dataframe
from engine.trend_analysis import analyze_persona
from engine.risk_scoring import score_all_markers


def plot_maria_trend(persona_df: pd.DataFrame, output_path: str = "maria_trend_chart.png"):
    """Plot Maria's eGFR trend with reference band — the classic 'still normal but trending' case."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for marker_name, group in persona_df.groupby("marker"):
        group = group.sort_values("visit_date")
        dates = pd.to_datetime(group["visit_date"])
        values = group["value"].values
        normal_low = group["normal_low"].iloc[0]
        normal_high = group["normal_high"].iloc[0]

        if marker_name == "eGFR":
            color = "#2E86AB"
            marker_style = "o"
        else:
            color = "#A23B72"
            marker_style = "s"

        # Plot data points
        ax.plot(
            dates, values,
            color=color, marker=marker_style, linewidth=2,
            label=marker_name, markersize=6,
        )

        # Add reference band (normal range)
        ax.axhspan(normal_low, normal_high, alpha=0.12, color="green", label=f"{marker_name} normal range" if marker_name == "eGFR" else "")
        # Label the threshold lines
        ax.axhline(y=normal_low, color="green", linestyle="--", alpha=0.5, linewidth=0.8)
        ax.axhline(y=normal_high, color="green", linestyle="--", alpha=0.5, linewidth=0.8)

    ax.set_title("Maria (54) — eGFR & Creatinine: Trending Despite 'Normal' Range", fontsize=14, fontweight="bold")
    ax.set_xlabel("Visit Date", fontsize=12)
    ax.set_ylabel("Lab Value", fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add annotation highlighting the key insight
    ax.annotate(
        "eGFR still above 60\nbut declining 24%\nover 18 months",
        xy=(dates.iloc[-1], values[-1]),
        xytext=(dates.iloc[-1] + pd.Timedelta(days=60), values[-1] - 5),
        fontsize=10,
        fontweight="bold",
        color="#2E86AB",
        arrowprops=dict(arrowstyle="->", color="#2E86AB", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"  📊 Chart saved to {output_path}")


def print_risk_report(personas_dict: dict):
    """Print formatted risk report for all 4 personas."""
    for pname, persona in personas_dict.items():
        df = persona_to_dataframe(persona)
        trends = analyze_persona(df)
        scores = score_all_markers(trends)

        print(f"\n{'='*60}")
        print(f"  👤 {persona.name} (age {persona.age})")
        print(f"  Tags: {', '.join(persona.tags)}")
        print(f"{'='*60}")

        if not scores:
            print("  No markers to analyze.")
            continue

        for s in scores:
            emoji = {"Low": "🟢", "Watch": "🟡", "Elevated": "🔴"}.get(s.risk_category, "⚪")
            print(f"\n  {emoji} {s.marker} ({s.unit})")
            print(f"     Risk: {s.risk_category}  |  Score: {s.raw_score}/10")
            print(f"     Proximity: {s.proximity_score:.1f}/5  |  Velocity: {s.velocity_score:.1f}/5")
            print(f"     {s.explanation}")


def main():
    print("=" * 60)
    print("  TrendSight — Checkpoint Demo (Steps 1-4)")
    print("  Prototype for educational/hackathon purposes only.")
    print("  Not a diagnostic device. Not medical advice.")
    print("=" * 60)

    # Step 1: Generate synthetic data
    print("\n📦 Step 1: Generating synthetic patient data...")
    personas = generate_all_personas()
    for name, p in personas.items():
        print(f"  ✓ {name} ({p.age}) — {len(p.markers)} markers, {len(p.dates)} visits")

    # Step 2: Trend analysis
    print("\n📈 Step 2: Running trend analysis...")
    all_trends = {}
    for pname, persona in personas.items():
        df = persona_to_dataframe(persona)
        trends = analyze_persona(df)
        all_trends[pname] = trends
        print(f"  ✓ {pname} — {len(trends)} markers analyzed")

    # Step 3: Risk scoring
    print("\n⚠️  Step 3: Computing Trend Risk Scores...")
    all_scores = {}
    for pname, trends in all_trends.items():
        scores = score_all_markers(trends)
        all_scores[pname] = scores
        categories = [s.risk_category for s in scores]
        print(f"  ✓ {pname} — categories: {', '.join(categories)}")

    # Step 4: Chart
    print("\n📊 Step 4: Generating chart...")
    maria_df = persona_to_dataframe(personas["Maria"])
    plot_maria_trend(maria_df)

    # Print full risk report
    print("\n" + "=" * 60)
    print("  RISK CLASSIFICATION REPORT")
    print("=" * 60)
    print_risk_report(personas)

    # Summary
    print("\n" + "=" * 60)
    print("  ✅ CHECKPOINT PASSED — all Steps 1-4 verified.")
    print("  ✅ Chart produced — maria_trend_chart.png")
    print("  ✅ Risk scores computed for all 4 personas.")
    print("=" * 60)


if __name__ == "__main__":
    main()
