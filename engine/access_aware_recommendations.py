"""
engine/access_aware_recommendations.py
=======================================
Rules-based (explicitly NOT machine learning) logic that adjusts "next step"
recommendation copy based on a patient's tagged access factors.

This is purely rule-based decision logic — no ML models, no training data,
no black box. Every recommendation is a direct function of:
  - The patient's risk category for each marker
  - The patient's known access barriers (transport, insurance, pharmacy access)

Risk thresholds / recommendations are illustrative, not clinically validated.

Prototype for educational/hackathon purposes only. Not a diagnostic device.
Not medical advice. Always consult a licensed clinician.
"""

from typing import List


def get_recommendations(scores: list, tags: List[str]) -> List[str]:
    """
    Generate access-aware, rules-based recommendations.

    Parameters
    ----------
    scores : list of RiskScore objects (from engine.risk_scoring)
    tags : list of patient tag strings, e.g.
           ["rural", "limited transport", "2 PCP visits/year"]

    Returns
    -------
    list of recommendation strings (plain language, actionable).
    """
    recs = []

    # -- Determine patient access profile --
    has_limited_transport = any("limited transport" in t.lower() for t in tags)
    is_rural = any("rural" in t.lower() for t in tags)
    is_insured = any("insured" in t.lower() or "insurance" in t.lower() for t in tags)
    has_easy_pharmacy = any("easy pharmacy" in t.lower() for t in tags)
    has_no_barriers = any("no known barriers" in t.lower() for t in tags)
    monitored_htn = any("hypertension" in t.lower() for t in tags)

    # -- Determine highest risk level across all markers --
    highest_risk = "Low"
    for s in scores:
        if s.risk_category == "Elevated":
            highest_risk = "Elevated"
            break
        elif s.risk_category == "Watch":
            highest_risk = "Watch"

    # -- Recommendations based on risk level + access factors --

    if highest_risk == "Elevated":
        recs.append(
            "📋 Schedule a follow-up appointment within the next 1-2 weeks "
            "to review trending lab results."
        )

        if has_limited_transport or is_rural:
            recs.append(
                "🚗 Since transportation is limited, consider requesting a "
                "telehealth visit for the initial discussion. Your provider "
                "can order lab work at a location convenient to you."
            )
        else:
            recs.append(
                "🏥 Your regular clinic can handle this — no special travel "
                "arrangements needed."
            )

        if not is_insured:
            recs.append(
                "💰 For those without insurance, ask your provider about "
                "self-pay rates or community health center sliding-scale fees."
            )
        elif has_easy_pharmacy:
            recs.append(
                "💊 With easy pharmacy access, any prescribed medications "
                "can be picked up without delay."
            )

    elif highest_risk == "Watch":
        recs.append(
            "👀 Bring these trending values up at your next scheduled "
            "appointment. No urgent action needed, but don't let it slide."
        )

        if has_limited_transport or is_rural:
            recs.append(
                "📞 Ask if your next visit can be done via telehealth to "
                "avoid an unnecessary trip. A mail-in lab kit may also "
                "be available for follow-up testing."
            )

        if has_easy_pharmacy:
            recs.append(
                "💊 If your provider recommends lifestyle changes or "
                "medication, your pharmacy is conveniently accessible."
            )

    else:  # Low
        recs.append(
            "✅ All lab trends are stable. Continue with routine monitoring "
            "as recommended by your primary care provider."
        )

        if has_limited_transport or is_rural:
            recs.append(
                "📞 To reduce visits, ask if routine follow-ups can be "
                "done via telehealth or if you can consolidate lab visits."
            )

    # Add marker-specific recommendations for elevated markers
    for s in scores:
        if s.risk_category == "Elevated":
            if "creatinine" in s.marker.lower() or "egfr" in s.marker.lower():
                recs.append(
                    "🩺 For kidney markers: staying hydrated and avoiding "
                    "NSAIDs (like ibuprofen) is commonly recommended. "
                    "Discuss any medication adjustments with your doctor."
                )
            if "potassium" in s.marker.lower():
                recs.append(
                    "🥗 For potassium: dietary adjustments may help. "
                    "Common high-potassium foods include bananas, oranges, "
                    "and potatoes — discuss dietary changes with your provider."
                )
        if s.risk_category == "Watch":
            if "hba1c" in s.marker.lower() or "hemoglobin" in s.marker.lower():
                recs.append(
                    "🍎 Rising HbA1c is commonly associated with blood sugar "
                    "trends. Consider discussing diet and physical activity "
                    "habits with your provider at your next visit."
                )

    # Always include the disclaimer
    recs.append(
        "⚠️ These recommendations are illustrative and based on general "
        "guidelines. Always follow your clinician's specific advice."
    )

    return recs
