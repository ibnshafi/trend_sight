"""
llm/prompt_templates.py
=======================
Prompt templates for generating patient-friendly explanations from trend data.

These templates convert structured trend analysis results into:
  (a) A plain-language explanation for the patient
  (b) 3 specific questions to ask their doctor
  (c) An urgency framing (routine / "bring this up soon" / discuss promptly)

All templates include the required disclaimer.

Prototype for educational/hackathon purposes only. Not a diagnostic device.
Not medical advice. Always consult a licensed clinician.
"""

from engine.trend_analysis import TrendResult
from engine.risk_scoring import RiskScore


def build_explanation_prompt(
    marker_name: str,
    trend_result: TrendResult,
    risk_score: RiskScore,
    patient_name: str,
    patient_tags: list,
) -> str:
    """Build a structured prompt for generating a patient-friendly explanation."""

    if trend_result is None:
        return f"""
Patient: {patient_name}
Tags: {', '.join(patient_tags)}
Situation: All lab markers are stable with no clinically meaningful trend detected.

Please generate:
1) A brief, reassuring plain-language explanation (2-3 sentences) that:
   - States the patient's labs are stable
   - Explains that this means their values are not changing significantly over time
   - Encourages continuing routine care

2) Questions to ask the doctor (if any) — if all is stable, suggest "Is there anything I should watch for?"

3) Urgency level: "routine"

Important: Always include this disclaimer at the end:
"⚠️ Prototype for educational/hackathon purposes only. Not a diagnostic device. Not medical advice. Always consult a licensed clinician."
"""

    # Determine direction wording
    if risk_score.direction_of_concern == "high-side":
        direction_word = "rising"
        threshold_word = "upper limit"
    elif risk_score.direction_of_concern == "low-side":
        direction_word = "declining"
        threshold_word = "lower limit"
    else:
        direction_word = "changing"
        threshold_word = "normal range boundary"

    # Determine if already out of range
    out_of_range = trend_result.is_above_high or trend_result.is_below_low

    return f"""
Patient: {patient_name} (age abstracted)
Tags: {', '.join(patient_tags)}
Marker: {marker_name}

Trend Analysis Results:
- Current value: {trend_result.latest_value:.1f} {trend_result.unit}
- Normal range: {trend_result.normal_low} – {trend_result.normal_high} {trend_result.unit}
- Trend direction: {direction_word}
- Rate of change: {abs(trend_result.rate_per_month):.2f} {trend_result.unit} per month
- R² (trend strength): {trend_result.r_squared:.2f}
- Currently out of normal range: {"Yes" if out_of_range else "No"}
- Risk category: {risk_score.risk_category}
- Time until threshold crossing: {trend_result.months_until_low or trend_result.months_until_high or "Not projected"}

Please generate:
1) A plain-language explanation (2-3 sentences) that:
   - Uses no jargon or explains it simply
   - States clearly whether this is trending toward or away from the normal range
   - Is honest about what "still in normal range but trending" means
   - Does NOT give specific medical advice

2) Three specific, actionable questions the patient could ask their doctor about this trend

3) Urgency level — choose ONE of:
   - "Routine" if Low risk
   - "Bring this up soon" if Watch risk
   - "Discuss promptly" if Elevated risk

Important: Always include this disclaimer at the end:
"⚠️ Prototype for educational/hackathon purposes only. Not a diagnostic device. Not medical advice. Always consult a licensed clinician."
"""


def build_urgency_label(risk_category: str) -> str:
    """Map risk category to urgency label."""
    mapping = {
        "Low": "Routine",
        "Watch": "Bring this up soon",
        "Elevated": "Discuss promptly",
    }
    return mapping.get(risk_category, "Routine")
