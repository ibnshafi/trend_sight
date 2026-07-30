"""
app/streamlit_app.py
====================
TrendSight — longitudinal lab-trend analysis tool.
Streamlit UI: select a persona, view trend charts with reference bands,
and see flagged markers with Trend Risk Scores and plain-language explanations.

Prototype for educational/hackathon purposes only. Not a diagnostic device.
Not medical advice. Always consult a licensed clinician.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generate_synthetic_patients import generate_all_personas, persona_to_dataframe
from engine.trend_analysis import analyze_persona
from engine.risk_scoring import score_all_markers
from engine.access_aware_recommendations import get_recommendations
from llm.explain import generate_explanation

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="TrendSight — Lab Trend Analyzer",
    page_icon="📈",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Disclaimer (always visible in sidebar)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚕️ TrendSight")
    st.markdown(
        "**Prototype for educational/hackathon purposes only.** "
        "Not a diagnostic device. Not medical advice. "
        "Always consult a licensed clinician."
    )
    st.divider()

    # Persona selector
    st.markdown("### Select Patient")
    persona_names = ["Maria", "James", "Aisha", "Robert"]
    selected_name = st.radio(
        "Choose a persona to analyze:",
        persona_names,
        index=0,
        format_func=lambda n: {
            "Maria": "👩 Maria (54) — declining eGFR",
            "James": "👨 James (39) — rising HbA1c",
            "Aisha": "👩 Aisha (28) — stable labs",
            "Robert": "👨 Robert (61) — potassium spike",
        }[n],
    )

    st.divider()
    st.caption(
        "Risk thresholds are illustrative, not clinically validated. "
        "All patient data is synthetic/generated."
    )

# ---------------------------------------------------------------------------
# Load data & compute analysis
# ---------------------------------------------------------------------------

@st.cache_data
def load_persona(name: str):
    """Load and analyze a persona, caching results."""
    personas = generate_all_personas()
    persona = personas[name]
    df = persona_to_dataframe(persona)
    trends = analyze_persona(df)
    scores = score_all_markers(trends)
    return persona, df, trends, scores


persona, df, trends, scores = load_persona(selected_name)

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

st.title(f"📈 {persona.name}'s Lab Trends")
st.markdown(f"**Age:** {persona.age}  |  **Tags:** {', '.join(persona.tags)}")

# ---- Risk Summary Cards ----
st.subheader("⚠️ Trend Risk Summary")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if scores:
        risk_counts = {"Low": 0, "Watch": 0, "Elevated": 0}
        for s in scores:
            risk_counts[s.risk_category] = risk_counts.get(s.risk_category, 0) + 1

        meta_cols = st.columns(3)
        colors = {"Low": "green", "Watch": "orange", "Elevated": "red"}
        emojis = {"Low": "🟢", "Watch": "🟡", "Elevated": "🔴"}
        for i, (cat, count) in enumerate(risk_counts.items()):
            meta_cols[i].metric(
                label=f"{emojis[cat]} {cat}",
                value=count,
                label_visibility="visible",
            )

# ---- Risk Details ----
for s in scores:
    emoji = {"Low": "🟢", "Watch": "🟡", "Elevated": "🔴"}.get(s.risk_category, "⚪")
    border_color = {"Low": "#27ae60", "Watch": "#f39c12", "Elevated": "#e74c3c"}.get(
        s.risk_category, "#95a5a6"
    )

    with st.container():
        st.markdown(
            f"""
            <div style="
                border-left: 5px solid {border_color};
                padding: 0.8rem 1rem;
                margin-bottom: 0.8rem;
                border-radius: 4px;
                background: #f8f9fa;
            ">
                <strong>{emoji} {s.marker}</strong>
                <span style="float: right;">
                    <strong>{s.risk_category}</strong> ({s.raw_score}/10)
                </span><br>
                <span style="color: #555;">{s.explanation}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---- Access-Aware Recommendations ----
st.subheader("💡 Personalized Recommendations")
recs = get_recommendations(scores, persona.tags)
for rec in recs:
    st.markdown(f"- {rec}")

# ---- Chart Section ----
st.subheader("📊 Lab Value Trends")

# Create a chart for each marker
for marker_name, group in df.groupby("marker"):
    group = group.sort_values("visit_date")
    dates = pd.to_datetime(group["visit_date"])
    values = group["value"].values
    normal_low = group["normal_low"].iloc[0]
    normal_high = group["normal_high"].iloc[0]
    unit = group["unit"].iloc[0]

    # Find the trend result for this marker
    trend = trends.get(marker_name)

    fig, ax = plt.subplots(figsize=(10, 4.5))

    # Plot reference band
    ax.axhspan(normal_low, normal_high, alpha=0.15, color="green", label="Normal range")
    ax.axhline(y=normal_low, color="green", linestyle="--", alpha=0.4, linewidth=0.8)
    ax.axhline(y=normal_high, color="green", linestyle="--", alpha=0.4, linewidth=0.8)

    # Plot data
    ax.plot(
        dates, values,
        color="#2E86AB", marker="o", linewidth=2, markersize=6,
        label=f"{marker_name} ({unit})",
    )

    # Plot trend line if we have a meaningful slope
    if trend is not None and abs(trend.slope) > 1e-8 and trend.r_squared > 0.1:
        days_num = (dates - dates[0]).days.values.astype(float)
        trend_line = (trend.slope * days_num) + (
            values[0] - trend.slope * days_num[0]
        )
        # Recompute intercept properly
        x_mean = np.mean(days_num)
        y_mean = np.mean(values)
        intercept = y_mean - trend.slope * x_mean
        trend_line = intercept + trend.slope * days_num
        ax.plot(
            dates, trend_line,
            color="#A23B72", linestyle="--", linewidth=1.5, alpha=0.8,
            label=f"Trend (R²={trend.r_squared:.2f})",
        )

    ax.set_title(f"{marker_name} — {persona.name}", fontsize=13, fontweight="bold")
    ax.set_ylabel(unit, fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)

# ---- LLM-Powered Explanation ----
st.subheader("🤖 AI Patient Summary")
st.caption("Powered by plain-language explanation engine. For demonstration only.")

# Collect flagged markers
flagged = [s for s in scores if s.risk_category in ("Watch", "Elevated")]

if flagged:
    for s in flagged:
        trend_data = trends.get(s.marker)
        if trend_data:
            explanation = generate_explanation(
                marker_name=s.marker,
                trend_result=trend_data,
                risk_score=s,
                patient_name=persona.name,
                patient_tags=persona.tags,
            )

            # Display patient-friendly explanation
            st.markdown(f"**{s.marker}**")
            st.markdown(f"*{explanation['plain_language']}*")

            st.markdown("**Questions to ask your doctor:**")
            for q in explanation["questions_for_doctor"]:
                st.markdown(f"- {q}")

            urgency = explanation["urgency"]
            urgency_style = {
                "routine": ("🟢", "green"),
                "bring this up soon": ("🟡", "orange"),
                "discuss promptly": ("🔴", "red"),
            }
            emoji_u, color_u = urgency_style.get(
                urgency.lower(), ("⚪", "gray")
            )
            st.markdown(
                f"**Urgency:** <span style='color:{color_u};font-weight:bold;'>{emoji_u} {urgency}</span>",
                unsafe_allow_html=True,
            )

            st.divider()
else:
    st.info("No markers currently flagged. All trends are stable.")
    # Show a generic positive explanation for Aisha
    explanation = generate_explanation(
        marker_name="All markers",
        trend_result=None,
        risk_score=None,
        patient_name=persona.name,
        patient_tags=persona.tags,
    )
    st.markdown(f"*{explanation['plain_language']}*")

# Footer disclaimer
st.divider()
st.caption(
    "⚠️ **Prototype for educational/hackathon purposes only.** "
    "Not a diagnostic device. Not medical advice. "
    "Always consult a licensed clinician. "
    "Risk thresholds are illustrative, not clinically validated. "
    "All patient data is synthetic/generated."
)
